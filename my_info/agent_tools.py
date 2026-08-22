"""Framework-neutral, privacy-minimizing tools for AI survey clients.

The functions in this module are the authority for survey state transitions and
result calculation.  MCP, command-line, web, and test adapters should delegate
to this layer instead of reproducing the rules in prompts or transport code.

Survey state is deliberately client-owned and contains controlled values only.
Names, account numbers, case details, travel details, and narrative free text
are neither accepted nor retained.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import csv
from datetime import date
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT / "data/derived/my_info/my_info_questionnaire.json"
DEFAULT_FEATURE_PATH = ROOT / "data/derived/my_info/my_info_pib_features.csv"
DEFAULT_EVIDENCE_PATH = ROOT / "data/derived/my_info/my_info_derivation_evidence.jsonl"

STATE_SCHEMA_VERSION = "1.1"
TOOL_API_VERSION = "0.2.0"
ANSWER_VALUES = ("yes", "no", "not_sure", "prefer_not_to_answer")
TIMING_KINDS = (
    "current",
    "within_1_year",
    "1_to_3_years",
    "4_to_7_years",
    "8_to_15_years",
    "more_than_15_years",
    "approximate_year",
    "unknown",
)

_STATE_FIELDS = {"schema_version", "contract_version", "locale", "answers", "refinements"}
_ANSWER_FIELDS = {"value", "timing"}
_TIMING_FIELDS = {"kind", "year"}
_REFINEMENT_FIELDS = {"selected_options", "timings"}


def _pipe_set(value: object) -> set[str]:
    return {item for item in str(value or "").split("|") if item}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _bool(value: object) -> bool:
    return str(value).casefold() == "true"


class SurveyToolEngine:
    """Load one immutable generated snapshot and expose deterministic operations."""

    def __init__(
        self,
        contract_path: Path = DEFAULT_CONTRACT_PATH,
        feature_path: Path = DEFAULT_FEATURE_PATH,
        evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    ) -> None:
        self.contract_path = contract_path
        self.feature_path = feature_path
        self.evidence_path = evidence_path
        self.contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.features = _read_csv(feature_path)
        self.questions = {
            question["code"]: question for question in self.contract["questions"]
        }
        self.question_order = [question["code"] for question in self.contract["questions"]]
        self.routes = {
            route["parent_question_code"]: route
            for route in self.contract.get("adaptive_routes", [])
        }
        self.route_options = {
            parent: {option["code"]: option for option in route["options"]}
            for parent, route in self.routes.items()
        }
        self.categories = {
            item["category_id"]: item
            for item in self.contract["personal_information_categories"]
        }
        self.evidence: dict[str, dict[str, Any]] = {}
        with evidence_path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    item = json.loads(line)
                    self.evidence[item["record"]["record_id"]] = item
        feature_ids = {row["record_id"] for row in self.features}
        if feature_ids != set(self.evidence):
            raise ValueError("Feature and derivation-evidence record IDs do not match")

    def create_state(self, locale: str = "en-CA") -> dict[str, Any]:
        self._validate_locale(locale)
        return {
            "schema_version": STATE_SCHEMA_VERSION,
            "contract_version": self.contract["content_version"],
            "locale": locale,
            "answers": {},
            "refinements": {},
        }

    def get_manifest(self) -> dict[str, Any]:
        """Return public versions, capabilities, and privacy constraints."""

        return {
            "tool_api_version": TOOL_API_VERSION,
            "state_schema_version": STATE_SCHEMA_VERSION,
            "contract_schema_version": self.contract["schema_version"],
            "contract_version": self.contract["content_version"],
            "generator_version": self.contract["generator_version"],
            "data_snapshot": self.contract["data_snapshot"],
            "supported_locales": self.contract["supported_locales"],
            "question_count": len(self.question_order),
            "adaptive_route_count": len(self.routes),
            "adaptive_route_version": self.contract.get("adaptive_route_version", ""),
            "pib_count": len(self.features),
            "answer_values": list(ANSWER_VALUES),
            "timing_kinds": list(TIMING_KINDS),
            "tools": [
                "my_info_get_manifest",
                "my_info_advance",
                "my_info_evaluate",
                "my_info_explain_result",
            ],
            "privacy": self.contract["privacy"],
            "limitations": [
                "Results are estimates, not confirmation that a record exists.",
                "Fallback route choices can still overmatch when a named program or institution is not known.",
                "The current local CRA extract has no defensible direct tax-return PIB record.",
                "A published retention rule may not reflect current operational holdings.",
            ],
        }

    def advance(
        self,
        state: Mapping[str, Any] | None = None,
        answers: Sequence[Mapping[str, Any]] | None = None,
        refinements: Sequence[Mapping[str, Any]] | None = None,
        *,
        locale: str = "en-CA",
    ) -> dict[str, Any]:
        """Apply controlled answers and return the next question or timing step."""

        working = self.create_state(locale) if state is None else deepcopy(dict(state))
        self.validate_state(working)
        for update in answers or ():
            self._apply_answer(working, update)
        for update in refinements or ():
            self._apply_refinement(working, update)
        self.validate_state(working)

        next_step: dict[str, Any] | None = None
        for code in self.question_order:
            answer = working["answers"].get(code)
            if answer is None:
                next_step = self._question_view(code, working["locale"])
                break
            if answer["value"] == "yes":
                if code in self.routes:
                    refinement = working["refinements"].get(code)
                    if refinement is None:
                        next_step = self._refinement_view(code, working["locale"])
                        break
                    untimed = next(
                        (
                            option_code
                            for option_code in refinement["selected_options"]
                            if self.route_options[code][option_code].get("ask_timing", True)
                            and option_code not in refinement.get("timings", {})
                        ),
                        None,
                    )
                    if untimed:
                        next_step = self._timing_view(
                            code, working["locale"], route_option_code=untimed
                        )
                        break
                elif "timing" not in answer:
                    next_step = self._timing_view(code, working["locale"])
                    break

        answered = len(working["answers"])
        timed_yes = sum(
            answer["value"] == "yes"
            and (
                (code not in self.routes and "timing" in answer)
                or (
                    code in working["refinements"]
                    and all(
                        option_code in working["refinements"][code].get("timings", {})
                        for option_code in working["refinements"][code]["selected_options"]
                        if self.route_options[code][option_code].get("ask_timing", True)
                    )
                )
            )
            for code, answer in working["answers"].items()
        )
        return {
            "state": working,
            "complete": next_step is None,
            "next_step": next_step,
            "progress": {
                "answered_questions": answered,
                "total_questions": len(self.question_order),
                "yes_answers_with_timing": timed_yes,
            },
        }

    def validate_state(self, state: Mapping[str, Any]) -> dict[str, Any]:
        """Validate a client-owned state object and reject unstructured fields."""

        unknown = set(state) - _STATE_FIELDS
        if unknown:
            raise ValueError(f"Unsupported state fields: {sorted(unknown)}")
        if state.get("schema_version") != STATE_SCHEMA_VERSION:
            raise ValueError("Unsupported survey state schema_version")
        if state.get("contract_version") != self.contract["content_version"]:
            raise ValueError("Survey state contract_version does not match this data snapshot")
        locale = str(state.get("locale") or "")
        self._validate_locale(locale)
        answers = state.get("answers")
        if not isinstance(answers, Mapping):
            raise ValueError("state.answers must be an object")
        for code, answer in answers.items():
            self._validate_answer(str(code), answer)
        refinements = state.get("refinements")
        if not isinstance(refinements, Mapping):
            raise ValueError("state.refinements must be an object")
        for code, refinement in refinements.items():
            self._validate_refinement(str(code), refinement, answers)
        return deepcopy(dict(state))

    def evaluate(
        self,
        state: Mapping[str, Any],
        *,
        as_of_year: int | None = None,
        include_possible: bool = False,
        max_results: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Return ranked PIB candidates and conservative holding estimates."""

        normalized = self.validate_state(state)
        assessment_year = as_of_year or date.today().year
        if assessment_year < 1900 or assessment_year > 2200:
            raise ValueError("as_of_year must be between 1900 and 2200")
        if max_results < 1 or max_results > 500:
            raise ValueError("max_results must be between 1 and 500")
        if offset < 0:
            raise ValueError("offset cannot be negative")

        results = self._results(normalized, assessment_year, include_possible)
        status_counts = Counter(result["holding_status"] for result in results)
        band_counts = Counter(result["match_band"] for result in results)
        institution_counts = Counter(result["institution_name"] for result in results)
        unanswered = [code for code in self.question_order if code not in normalized["answers"]]
        uncertain = [
            code
            for code, answer in normalized["answers"].items()
            if answer["value"] in {"not_sure", "prefer_not_to_answer"}
        ]
        incomplete_refinements = [
            code
            for code, answer in normalized["answers"].items()
            if answer["value"] == "yes"
            and code in self.routes
            and not self._refinement_complete(code, normalized["refinements"].get(code))
        ]
        inventory_gaps = [
            {
                "question_code": code,
                "route_option_code": option_code,
                "message": (
                    "The current PIB inventory does not contain a defensible direct record for this interaction."
                ),
            }
            for code, refinement in normalized["refinements"].items()
            for option_code in refinement["selected_options"]
            if self.route_options[code][option_code]["coverage"] == "inventory_gap"
        ]
        refinement_needed = sorted({
            code
            for result in results
            for code in result["matched_question_codes"]
            if self.questions[code]["help"]["split_recommendation_en"]
            and code not in normalized["refinements"]
        })
        returned = results[offset:offset + max_results]
        next_offset = offset + len(returned)
        return {
            "assessment": {
                "as_of_year": assessment_year,
                "complete_survey": not unanswered and not incomplete_refinements,
                "unanswered_question_codes": unanswered,
                "uncertain_question_codes": uncertain,
                "incomplete_refinement_question_codes": incomplete_refinements,
                "inventory_gaps": inventory_gaps,
                "refinement_needed_question_codes": refinement_needed,
                "caveat": "These are candidate PIBs, not confirmation that an institution holds information about this person.",
            },
            "summary": {
                "total_matches": len(results),
                "returned_matches": len(returned),
                "truncated": len(returned) < len(results),
                "offset": offset,
                "next_offset": next_offset if next_offset < len(results) else None,
                "holding_status_counts": dict(sorted(status_counts.items())),
                "match_band_counts": dict(sorted(band_counts.items())),
                "top_institutions": [
                    {"institution_name": name, "count": count}
                    for name, count in institution_counts.most_common(10)
                ],
            },
            "results": returned,
            "versions": {
                "tool_api_version": TOOL_API_VERSION,
                "state_schema_version": STATE_SCHEMA_VERSION,
                "contract_version": self.contract["content_version"],
                "data_snapshot": self.contract["data_snapshot"],
            },
        }

    def explain_result(
        self,
        state: Mapping[str, Any],
        record_id: str,
        *,
        as_of_year: int | None = None,
    ) -> dict[str, Any]:
        """Explain one candidate using the precise derivation evidence."""

        normalized = self.validate_state(state)
        assessment_year = as_of_year or date.today().year
        result = next(
            (
                item
                for item in self._results(normalized, assessment_year, True)
                if item["record_id"] == record_id
            ),
            None,
        )
        if result is None:
            raise ValueError("record_id is not a candidate for the supplied survey state")

        derivation = self.evidence[record_id]
        matched_codes = set(result["matched_question_codes"])
        triggers = [
            trigger
            for field in ("primary_question_triggers", "question_triggers")
            for trigger in derivation["interactions"].get(field, [])
            if trigger["code"] in matched_codes
        ]
        feature_codes = {
            basis["feature_code"]
            for trigger in triggers
            for basis in trigger.get("trigger_basis", [])
        }
        supporting_features = [
            feature
            for field in ("interaction_topics", "individual_roles", "service_actions")
            for feature in derivation["interactions"].get(field, [])
            if feature["code"] in feature_codes
        ]
        adaptive_triggers = [
            {
                "question_code": item["question_code"],
                "route_option_code": item["route_option_code"],
                "label_en": self.route_options[item["question_code"]][item["route_option_code"]]["label_en"],
                "label_fr": self.route_options[item["question_code"]][item["route_option_code"]]["label_fr"],
                "institution_en": self.route_options[item["question_code"]][item["route_option_code"]]["institution_en"],
                "institution_fr": self.route_options[item["question_code"]][item["route_option_code"]]["institution_fr"],
                "coverage": self.route_options[item["question_code"]][item["route_option_code"]]["coverage"],
            }
            for item in result["matched_route_options"]
        ]
        return {
            "result": result,
            "question_triggers": triggers,
            "adaptive_route_triggers": adaptive_triggers,
            "supporting_features": supporting_features,
            "retention_derivation": derivation["retention"],
            "category_derivation": derivation["categories"],
            "holding_inference": "candidate_only",
        }

    def _validate_locale(self, locale: str) -> None:
        if locale not in self.contract["supported_locales"]:
            raise ValueError(f"Unsupported locale: {locale}")

    def _validate_answer(self, code: str, answer: object) -> None:
        if code not in self.questions:
            raise ValueError(f"Unknown question_code: {code}")
        if not isinstance(answer, Mapping):
            raise ValueError(f"{code}: answer must be an object")
        unknown = set(answer) - _ANSWER_FIELDS
        if unknown:
            raise ValueError(f"{code}: unsupported answer fields: {sorted(unknown)}")
        value = answer.get("value")
        if value not in ANSWER_VALUES:
            raise ValueError(f"{code}: unsupported answer value")
        timing = answer.get("timing")
        if timing is not None:
            if value != "yes":
                raise ValueError(f"{code}: timing is accepted only for a yes answer")
            if code in self.routes:
                raise ValueError(f"{code}: timing belongs to each selected adaptive route")
            self._validate_timing(code, timing)

    def _validate_refinement(
        self,
        code: str,
        refinement: object,
        answers: Mapping[str, Any],
    ) -> None:
        if code not in self.routes:
            raise ValueError(f"{code}: no adaptive route exists")
        if answers.get(code, {}).get("value") != "yes":
            raise ValueError(f"{code}: a refinement requires a yes parent answer")
        if not isinstance(refinement, Mapping):
            raise ValueError(f"{code}: refinement must be an object")
        unknown = set(refinement) - _REFINEMENT_FIELDS
        if unknown:
            raise ValueError(f"{code}: unsupported refinement fields: {sorted(unknown)}")
        selected = refinement.get("selected_options")
        if not isinstance(selected, list) or not selected:
            raise ValueError(f"{code}: selected_options must be a non-empty array")
        if len(selected) != len(set(selected)):
            raise ValueError(f"{code}: selected_options cannot contain duplicates")
        valid_options = self.route_options[code]
        invalid = [item for item in selected if item not in valid_options]
        if invalid:
            raise ValueError(f"{code}: unsupported route options: {invalid}")
        timings = refinement.get("timings", {})
        if not isinstance(timings, Mapping):
            raise ValueError(f"{code}: timings must be an object")
        unselected = set(timings) - set(selected)
        if unselected:
            raise ValueError(f"{code}: timing supplied for unselected options: {sorted(unselected)}")
        for option_code, timing in timings.items():
            self._validate_timing(f"{code}.{option_code}", timing)

    def _refinement_complete(self, code: str, refinement: object) -> bool:
        if not isinstance(refinement, Mapping):
            return False
        try:
            self._validate_refinement(
                code,
                refinement,
                {code: {"value": "yes"}},
            )
        except ValueError:
            return False
        timings = refinement.get("timings", {})
        return all(
            not self.route_options[code][option_code].get("ask_timing", True)
            or option_code in timings
            for option_code in refinement["selected_options"]
        )

    def _validate_timing(self, code: str, timing: object) -> None:
        if not isinstance(timing, Mapping):
            raise ValueError(f"{code}: timing must be an object")
        unknown = set(timing) - _TIMING_FIELDS
        if unknown:
            raise ValueError(f"{code}: unsupported timing fields: {sorted(unknown)}")
        kind = timing.get("kind")
        if kind not in TIMING_KINDS:
            raise ValueError(f"{code}: unsupported timing kind")
        year = timing.get("year")
        if kind == "approximate_year":
            if not isinstance(year, int) or year < 1800 or year > 2200:
                raise ValueError(f"{code}: approximate_year requires a valid integer year")
        elif year is not None:
            raise ValueError(f"{code}: year is allowed only with approximate_year")

    def _apply_answer(self, state: dict[str, Any], update: Mapping[str, Any]) -> None:
        if not isinstance(update, Mapping):
            raise ValueError("Each answer update must be an object")
        unknown = set(update) - {"question_code", "value", "timing"}
        if unknown:
            raise ValueError(f"Unsupported answer-update fields: {sorted(unknown)}")
        code = str(update.get("question_code") or "")
        answer = {key: deepcopy(update[key]) for key in ("value", "timing") if key in update}
        self._validate_answer(code, answer)
        state["answers"][code] = answer
        if answer["value"] != "yes":
            state["refinements"].pop(code, None)

    def _apply_refinement(self, state: dict[str, Any], update: Mapping[str, Any]) -> None:
        if not isinstance(update, Mapping):
            raise ValueError("Each refinement update must be an object")
        unknown = set(update) - {"question_code", *_REFINEMENT_FIELDS}
        if unknown:
            raise ValueError(f"Unsupported refinement-update fields: {sorted(unknown)}")
        code = str(update.get("question_code") or "")
        refinement = {
            key: deepcopy(update[key])
            for key in _REFINEMENT_FIELDS
            if key in update
        }
        self._validate_refinement(code, refinement, state["answers"])
        state["refinements"][code] = refinement

    def _question_view(self, code: str, locale: str) -> dict[str, Any]:
        question = self.questions[code]
        french = locale == "fr-CA"
        prompt = question["question_fr"] if french else question["readability_en"]["candidate_question_en"]
        source_prompt = question["question_fr"] if french else question["question_en"]
        examples = [
            {
                "institution": item["institution_fr"] if french else item["institution_en"],
                "activity": item["activity_fr"] if french else item["activity_en"],
                "source_pib_keys": item["source_pib_keys"],
                "evidence_note": item["evidence_note_fr"] if french else item["evidence_note_en"],
            }
            for item in question["help"]["examples"]
        ]
        return {
            "step_type": "question",
            "question_code": code,
            "prompt": prompt,
            "source_prompt": source_prompt,
            "wording_status": "current" if french else "plain_language_candidate_for_testing",
            "answer_values": list(ANSWER_VALUES),
            "help": {
                "familiarity": question["help"]["familiarity"],
                "agent_offer": question["help"]["agent_offer"],
                "examples": examples,
                "split_recommendation": (
                    question["help"]["split_recommendation_fr"]
                    if french
                    else question["help"]["split_recommendation_en"]
                ),
            },
        }

    def _refinement_view(self, code: str, locale: str) -> dict[str, Any]:
        route = self.routes[code]
        french = locale == "fr-CA"
        return {
            "step_type": "refinement",
            "question_code": code,
            "prompt": route["prompt_fr"] if french else route["prompt_en"],
            "selection_type": "multi_select",
            "options": [
                {
                    "code": option["code"],
                    "label": option["label_fr"] if french else option["label_en"],
                    "institution": (
                        option["institution_fr"] if french else option["institution_en"]
                    ),
                    "coverage": option["coverage"],
                }
                for option in route["options"]
            ],
            "privacy_note": (
                "Choisissez seulement les types d'interaction; ne fournissez aucun numéro ni détail de dossier."
                if french
                else "Choose interaction types only; do not provide identifiers or case details."
            ),
        }

    def _timing_view(
        self,
        code: str,
        locale: str,
        *,
        route_option_code: str | None = None,
    ) -> dict[str, Any]:
        question = self.questions[code]
        french = locale == "fr-CA"
        if route_option_code:
            option = self.route_options[code][route_option_code]
            label = option["label_fr"] if french else option["label_en"]
            prompt = (
                f"Vers quand cela s'est-il produit pour la dernière fois : {label}?"
                if french
                else f"About when did this last happen: {label}?"
            )
        else:
            prompt = question["timing"]["prompt_fr"] if french else question["timing"]["prompt_en"]
        return {
            "step_type": "timing",
            "question_code": code,
            "route_option_code": route_option_code,
            "prompt": prompt,
            "timing_kinds": list(TIMING_KINDS),
            "year_required_for": "approximate_year",
            "privacy_note": (
                "Une période approximative suffit; ne fournissez aucun détail de dossier."
                if french
                else "An approximate period is enough; do not provide case details."
            ),
        }

    def _results(
        self,
        state: Mapping[str, Any],
        as_of_year: int,
        include_possible: bool,
    ) -> list[dict[str, Any]]:
        answers = state["answers"]
        yes_codes = {code for code, answer in answers.items() if answer["value"] == "yes"}
        broad_yes_codes = set(yes_codes)
        route_matches: dict[str, list[tuple[str, str]]] = {}
        for parent_code, refinement in state["refinements"].items():
            selected = refinement["selected_options"]
            if not any(
                self.route_options[parent_code][option_code].get("fallback_to_parent", False)
                for option_code in selected
            ):
                broad_yes_codes.discard(parent_code)
            for option_code in selected:
                option = self.route_options[parent_code][option_code]
                for bank_number in option.get("selectors", {}).get("bank_numbers", []):
                    route_matches.setdefault(bank_number, []).append((parent_code, option_code))
        uncertain_codes = {
            code
            for code, answer in answers.items()
            if answer["value"] in {"not_sure", "prefer_not_to_answer"}
        }
        results: list[dict[str, Any]] = []
        for row in self.features:
            primary = _pipe_set(row["question_codes"])
            candidates = _pipe_set(row["candidate_question_codes"])
            direct_routes = route_matches.get(row["bank_number_key"], [])
            direct_codes = {parent for parent, _ in direct_routes}
            strong_codes = sorted((primary & broad_yes_codes) | direct_codes)
            possible_codes = sorted((candidates & broad_yes_codes) - set(strong_codes))
            review_codes = sorted(candidates & uncertain_codes)
            if strong_codes:
                band, matched = "strong_match", strong_codes
            elif possible_codes and include_possible:
                band, matched = "possible_match", possible_codes
            elif review_codes and include_possible:
                band, matched = "review_if_relevant", review_codes
            else:
                continue
            results.append(
                self._result_view(
                    row,
                    band,
                    matched,
                    state,
                    as_of_year,
                    matched_route_options=[
                        {"question_code": parent, "route_option_code": option}
                        for parent, option in direct_routes
                    ],
                )
            )
        status_order = {
            "likely_held": 0,
            "may_still_be_held": 1,
            "retention_unknown": 2,
            "likely_disposed": 3,
        }
        band_order = {"strong_match": 0, "possible_match": 1, "review_if_relevant": 2}
        results.sort(key=lambda item: (
            status_order[item["holding_status"]],
            band_order[item["match_band"]],
            item["institution_name"].casefold(),
            item["title"].casefold(),
            item["record_id"],
        ))
        return results

    def _result_view(
        self,
        row: Mapping[str, str],
        band: str,
        matched_codes: list[str],
        state: Mapping[str, Any],
        as_of_year: int,
        *,
        matched_route_options: list[dict[str, str]],
    ) -> dict[str, Any]:
        french = state["locale"] == "fr-CA"
        route_parents = {item["question_code"] for item in matched_route_options}
        statuses = [
            self._holding_status(
                row,
                state["refinements"][item["question_code"]]
                .get("timings", {})
                .get(item["route_option_code"]),
                as_of_year,
            )
            for item in matched_route_options
        ]
        for code in matched_codes:
            if state["answers"][code]["value"] != "yes":
                continue
            if code in route_parents:
                continue
            if code in self.routes and code in state["refinements"]:
                fallback_codes = [
                    option_code
                    for option_code in state["refinements"][code]["selected_options"]
                    if self.route_options[code][option_code].get("fallback_to_parent", False)
                ]
                timing = next(
                    (
                        state["refinements"][code].get("timings", {}).get(option_code)
                        for option_code in fallback_codes
                    ),
                    None,
                )
            else:
                timing = state["answers"][code].get("timing")
            statuses.append(self._holding_status(row, timing, as_of_year))
        if statuses:
            precedence = {
                "likely_held": 0,
                "may_still_be_held": 1,
                "retention_unknown": 2,
                "likely_disposed": 3,
            }
            retention = min(statuses, key=lambda item: precedence[item["status"]])
        else:
            retention = {
                "status": "retention_unknown",
                "confidence": "low",
                "rationale": "The interaction answer was uncertain, so no holding estimate was made.",
                "timing": None,
            }
        categories = [
            {
                "category_id": code,
                "name": self.categories[code]["name_fr" if french else "name_en"],
            }
            for code in sorted(_pipe_set(row["category_ids"]))
            if code in self.categories
        ]
        return {
            "record_id": row["record_id"],
            "bank_number": row["bank_number_key"],
            "scope": "institution_specific" if row["scope"] == "institution" else "standard",
            "institution_id": row["institution_id"],
            "institution_name": row["institution_name_fr" if french else "institution_name_en"],
            "title": row["title_fr" if french else "title_en"],
            "source_url": row["source_url_fr" if french else "source_url_en"],
            "match_band": band,
            "matched_question_codes": matched_codes,
            "matched_route_options": matched_route_options,
            "holding_status": retention["status"],
            "retention": {
                **retention,
                "rule_type": row["retention_rule_type"],
                "reference_events": sorted(_pipe_set(row["retention_reference_events"])),
                "published_text_excerpt": (
                    row["retention_text_fr" if french else "retention_text_en"][:280]
                ),
                "published_text_truncated": len(
                    row["retention_text_fr" if french else "retention_text_en"]
                ) > 280,
            },
            "categories_of_personal_information": categories,
            "privacy_caveat_codes": sorted(_pipe_set(row["privacy_caveat_codes"])),
        }

    def _holding_status(
        self,
        row: Mapping[str, str],
        timing: object,
        as_of_year: int,
    ) -> dict[str, Any]:
        if not isinstance(timing, Mapping) or timing.get("kind") == "unknown":
            return self._retention_unknown("No usable approximate interaction date was supplied.", timing)
        rule_type = row["retention_rule_type"]
        if rule_type == "indefinite" and not _bool(row["retention_has_immediate_disposal"]):
            return {
                "status": "likely_held",
                "confidence": row["retention_confidence"],
                "rationale": "The published rule says the records are retained indefinitely.",
                "timing": dict(timing),
            }
        if rule_type in {"unknown", "policy_pending", "institution_defined", "schedule_defined", "trigger_based"}:
            return self._retention_unknown(
                "The published rule does not provide a duration that can be applied to this answer.", timing
            )
        if _bool(row["retention_has_immediate_disposal"]) or _bool(row["retention_has_indefinite_component"]):
            return self._retention_unknown(
                "Different published branches permit immediate disposal or indefinite retention.", timing
            )
        reference_events = _pipe_set(row["retention_reference_events"])
        if any(
            event not in {"unspecified_start", "record_creation_or_receipt", "date_of_issue"}
            for event in reference_events
        ):
            return self._retention_unknown(
                "The retention clock starts at another event, such as file closure or departure.", timing
            )

        elapsed_min, elapsed_max = self._elapsed_interval(timing, as_of_year)
        if elapsed_min is None:
            return self._retention_unknown("The supplied timing could not be applied.", timing)
        minimum = float(row["retention_minimum_years"]) if row["retention_minimum_years"] else None
        maximum = float(row["retention_maximum_years"]) if row["retention_maximum_years"] else None
        disposition = row["retention_disposition"]
        if maximum is not None and elapsed_min > maximum:
            if disposition == "destroy":
                return {
                    "status": "likely_disposed",
                    "confidence": row["retention_confidence"],
                    "rationale": "Even the most recent date in the supplied period is beyond the published maximum followed by destruction.",
                    "timing": dict(timing),
                }
            if disposition == "transfer_to_archives":
                return {
                    "status": "likely_held",
                    "confidence": row["retention_confidence"],
                    "rationale": "The published rule says records transfer to Library and Archives Canada after the institutional period.",
                    "timing": dict(timing),
                }
        if minimum is not None and elapsed_max is not None and elapsed_max < minimum:
            return {
                "status": "likely_held",
                "confidence": row["retention_confidence"],
                "rationale": "The entire supplied period is within the published minimum or fixed retention period.",
                "timing": dict(timing),
            }
        if minimum is not None or maximum is not None:
            return {
                "status": "may_still_be_held",
                "confidence": row["retention_confidence"],
                "rationale": "The approximate period overlaps a boundary, or the published rule gives only a minimum, range, or conditional disposition.",
                "timing": dict(timing),
            }
        return self._retention_unknown("The published text has no applicable numeric period.", timing)

    @staticmethod
    def _retention_unknown(rationale: str, timing: object) -> dict[str, Any]:
        return {
            "status": "retention_unknown",
            "confidence": "low",
            "rationale": rationale,
            "timing": dict(timing) if isinstance(timing, Mapping) else None,
        }

    @staticmethod
    def _elapsed_interval(timing: Mapping[str, Any], as_of_year: int) -> tuple[int | None, int | None]:
        kind = timing["kind"]
        intervals = {
            "current": (0, 0),
            "within_1_year": (0, 1),
            "1_to_3_years": (1, 3),
            "4_to_7_years": (4, 7),
            "8_to_15_years": (8, 15),
            "more_than_15_years": (16, None),
        }
        if kind == "approximate_year":
            elapsed = as_of_year - int(timing["year"])
            if elapsed < 0:
                raise ValueError("An approximate interaction year cannot be after as_of_year")
            return elapsed, elapsed
        return intervals.get(str(kind), (None, None))


_DEFAULT_ENGINE: SurveyToolEngine | None = None


def default_engine() -> SurveyToolEngine:
    global _DEFAULT_ENGINE
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = SurveyToolEngine()
    return _DEFAULT_ENGINE


def get_manifest() -> dict[str, Any]:
    return default_engine().get_manifest()


def advance(
    state: Mapping[str, Any] | None = None,
    answers: Sequence[Mapping[str, Any]] | None = None,
    refinements: Sequence[Mapping[str, Any]] | None = None,
    *,
    locale: str = "en-CA",
) -> dict[str, Any]:
    return default_engine().advance(state, answers, refinements, locale=locale)


def evaluate(
    state: Mapping[str, Any],
    *,
    as_of_year: int | None = None,
    include_possible: bool = False,
    max_results: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    return default_engine().evaluate(
        state,
        as_of_year=as_of_year,
        include_possible=include_possible,
        max_results=max_results,
        offset=offset,
    )


def explain_result(
    state: Mapping[str, Any],
    record_id: str,
    *,
    as_of_year: int | None = None,
) -> dict[str, Any]:
    return default_engine().explain_result(state, record_id, as_of_year=as_of_year)
