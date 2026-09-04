#!/usr/bin/env python3
"""Replay structured test personas through My Info and report logic diagnostics.

The evaluator intentionally ignores persona narrative fields. Only controlled
survey answers, adaptive-route choices, and timing values are sent to the
canonical Python engine.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from my_info.agent_tools import SurveyToolEngine  # noqa: E402


DEFAULT_INPUT = ROOT / "data/test_personas/personas.json"
VERSIONED_INPUT_FALLBACK = ROOT / "data/test_personas/personas.v1.json"
DEFAULT_OUTPUT_DIR = ROOT / "data/test_personas/generated"
JSON_OUTPUT_NAME = "evaluation.json"
MARKDOWN_OUTPUT_NAME = "persona_analysis.md"
REPORT_SCHEMA_VERSION = "1.0"


def _sorted_counts(values: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _as_string_list(value: object, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be an array of strings")
    return sorted(set(value))


def _updates(value: object, *, code_field: str, field: str) -> list[dict[str, Any]]:
    """Accept canonical maps or MCP-style update arrays."""

    if value is None:
        return []
    if isinstance(value, Mapping):
        updates: list[dict[str, Any]] = []
        for code, item in value.items():
            if not isinstance(item, Mapping):
                raise ValueError(f"{field}.{code} must be an object")
            updates.append({code_field: str(code), **deepcopy(dict(item))})
        return updates
    if isinstance(value, list) and all(isinstance(item, Mapping) for item in value):
        return [deepcopy(dict(item)) for item in value]
    raise ValueError(f"{field} must be an object or an array of objects")


def _survey_block(persona: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("survey", "questionnaire"):
        value = persona.get(key)
        if isinstance(value, Mapping):
            return value
    return persona


def build_state(engine: SurveyToolEngine, persona: Mapping[str, Any]) -> dict[str, Any]:
    """Build and validate one client-owned state using controlled fixture values."""

    survey = _survey_block(persona)
    supplied_state = survey.get("state", persona.get("survey_state"))
    if supplied_state is not None:
        if not isinstance(supplied_state, Mapping):
            raise ValueError("survey.state must be an object")
        return engine.validate_state(supplied_state)

    locale = str(survey.get("locale", persona.get("locale", "en-CA")))
    answers = _updates(
        survey.get("answers", persona.get("answers")),
        code_field="question_code",
        field="survey.answers",
    )
    refinements = _updates(
        survey.get("refinements", persona.get("refinements")),
        code_field="question_code",
        field="survey.refinements",
    )
    response = engine.advance(
        answers=answers,
        refinements=refinements,
        locale=locale,
    )
    while not response["complete"] and response["next_step"]["step_type"] == "department":
        step = response["next_step"]
        response = engine.advance(
            response["state"],
            departments=[{
                "question_code": step["question_code"],
                "institution_ids": [item["institution_id"] for item in step["options"]],
            }],
        )
    state = response["state"]
    return engine.validate_state(state)


def evaluate_all_results(
    engine: SurveyToolEngine,
    state: Mapping[str, Any],
    *,
    as_of_year: int,
    include_possible: bool,
    page_size: int = 500,
) -> dict[str, Any]:
    """Collect every result while retaining the engine's first-page assessment."""

    if page_size < 1 or page_size > 500:
        raise ValueError("page_size must be between 1 and 500")
    offset = 0
    results: list[dict[str, Any]] = []
    first: dict[str, Any] | None = None
    while True:
        page = engine.evaluate(
            state,
            as_of_year=as_of_year,
            include_possible=include_possible,
            max_results=page_size,
            offset=offset,
        )
        if first is None:
            first = page
        results.extend(page["results"])
        next_offset = page["summary"]["next_offset"]
        if next_offset is None:
            break
        if next_offset <= offset:
            raise RuntimeError("Survey result pagination did not advance")
        offset = next_offset

    assert first is not None
    expected_total = first["summary"]["total_matches"]
    if len(results) != expected_total:
        raise RuntimeError(
            f"Collected {len(results)} results but the engine reported {expected_total}"
        )
    if len({item["record_id"] for item in results}) != len(results):
        raise RuntimeError("Survey pagination returned duplicate record IDs")
    output = deepcopy(first)
    output["results"] = results
    output["summary"].update({
        "returned_matches": len(results),
        "truncated": False,
        "offset": 0,
        "next_offset": None,
    })
    return output


def _expectation_metrics(
    expectations: object,
    results: Sequence[Mapping[str, Any]],
    inventory_gaps: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if expectations is None:
        expectations = {}
    if not isinstance(expectations, Mapping):
        raise ValueError("persona.expectations must be an object")

    result_ids = {str(item["record_id"]) for item in results}
    bank_numbers = {str(item["bank_number"]) for item in results}
    gap_options = {str(item["route_option_code"]) for item in inventory_gaps}

    expected_ids = _as_string_list(
        expectations.get("expected_record_ids"), "expected_record_ids"
    )
    expected_banks = _as_string_list(
        expectations.get("expected_bank_numbers", expectations.get("known_expected_banks")),
        "expected_bank_numbers",
    )
    false_positive_ids = _as_string_list(
        expectations.get(
            "likely_false_positive_record_ids", expectations.get("unexpected_record_ids")
        ),
        "likely_false_positive_record_ids",
    )
    false_positive_banks = _as_string_list(
        expectations.get(
            "likely_false_positive_bank_numbers", expectations.get("unexpected_bank_numbers")
        ),
        "likely_false_positive_bank_numbers",
    )
    allowed_ids = _as_string_list(expectations.get("allowed_record_ids"), "allowed_record_ids")
    allowed_banks = _as_string_list(
        expectations.get("allowed_bank_numbers"), "allowed_bank_numbers"
    )
    expected_gaps = _as_string_list(
        expectations.get("expected_inventory_gaps"), "expected_inventory_gaps"
    )
    qualitative = {
        "expected_ambiguities": _as_string_list(
            expectations.get("expected_ambiguities"), "expected_ambiguities"
        ),
        "known_false_positive_risks": _as_string_list(
            expectations.get("known_false_positive_risks"),
            "known_false_positive_risks",
        ),
        "known_false_negative_risks": _as_string_list(
            expectations.get("known_false_negative_risks"),
            "known_false_negative_risks",
        ),
    }

    unmatched_expected_ids = set(expected_ids) - result_ids
    format_mismatches: list[dict[str, Any]] = []
    for expected_id in sorted(unmatched_expected_ids):
        expected_bank = expected_id.rsplit(":", 1)[-1]
        actual_ids = sorted(
            str(item["record_id"])
            for item in results
            if str(item["bank_number"]) == expected_bank
        )
        if actual_ids:
            format_mismatches.append({
                "expected_record_id": expected_id,
                "bank_number": expected_bank,
                "actual_record_ids": actual_ids,
            })
    format_mismatch_ids = {item["expected_record_id"] for item in format_mismatches}
    genuine_missing_ids = sorted(unmatched_expected_ids - format_mismatch_ids)

    metrics = {
        "expected_record_ids": {
            "found": sorted(result_ids & set(expected_ids)),
            "missing": genuine_missing_ids,
            "format_mismatches": format_mismatches,
        },
        "expected_bank_numbers": {
            "found": sorted(bank_numbers & set(expected_banks)),
            "missing": sorted(set(expected_banks) - bank_numbers),
        },
        "known_likely_false_positives": {
            "record_ids_found": sorted(result_ids & set(false_positive_ids)),
            "bank_numbers_found": sorted(bank_numbers & set(false_positive_banks)),
        },
        "expected_inventory_gaps": {
            "found": sorted(gap_options & set(expected_gaps)),
            "missing": sorted(set(expected_gaps) - gap_options),
        },
        "allowlist_exceptions": {
            "record_ids": sorted(result_ids - set(allowed_ids)) if allowed_ids else [],
            "bank_numbers": sorted(bank_numbers - set(allowed_banks)) if allowed_banks else [],
        },
        "qualitative_risks": qualitative,
        "expectations_supplied": bool(expectations),
    }
    metrics["failed_assertion_count"] = sum(
        len(items)
        for items in (
            metrics["expected_record_ids"]["missing"],
            metrics["expected_bank_numbers"]["missing"],
            metrics["known_likely_false_positives"]["record_ids_found"],
            metrics["known_likely_false_positives"]["bank_numbers_found"],
            metrics["expected_inventory_gaps"]["missing"],
            metrics["allowlist_exceptions"]["record_ids"],
            metrics["allowlist_exceptions"]["bank_numbers"],
        )
    )
    metrics["fixture_format_issue_count"] = len(format_mismatches)
    return metrics


def _route_metrics(
    engine: SurveyToolEngine,
    state: Mapping[str, Any],
    results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    selected: list[dict[str, Any]] = []
    for question_code in engine.question_order:
        refinement = state["refinements"].get(question_code)
        if not refinement:
            continue
        for option_code in refinement["selected_options"]:
            option = engine.route_options[question_code][option_code]
            selected.append({
                "question_code": question_code,
                "route_option_code": option_code,
                "coverage": option["coverage"],
                "fallback_to_parent": bool(option.get("fallback_to_parent", False)),
                "selector_bank_number_count": len(
                    option.get("selectors", {}).get("bank_numbers", [])
                ),
            })
    selected_lookup = {
        (item["question_code"], item["route_option_code"]): item
        for item in selected
    }
    explicit_by_coverage: dict[str, set[str]] = {}
    fallback_parent_codes = {
        item["question_code"] for item in selected if item["fallback_to_parent"]
    }
    explicit_result_ids: set[str] = set()
    fallback_associated_ids: set[str] = set()
    for result in results:
        record_id = str(result["record_id"])
        if fallback_parent_codes & set(result["matched_question_codes"]):
            fallback_associated_ids.add(record_id)
        for matched in result["matched_route_options"]:
            option = selected_lookup.get(
                (matched["question_code"], matched["route_option_code"])
            )
            if option:
                explicit_result_ids.add(record_id)
                explicit_by_coverage.setdefault(option["coverage"], set()).add(record_id)
    return {
        "selected_count": len(selected),
        "coverage_counts": _sorted_counts([item["coverage"] for item in selected]),
        "selected": selected,
        "result_attribution": {
            "explicit_route_result_count": len(explicit_result_ids),
            "explicit_route_result_counts_by_coverage": {
                key: len(value) for key, value in sorted(explicit_by_coverage.items())
            },
            "fallback_parent_associated_result_count": len(fallback_associated_ids),
            "fallback_only_result_count": len(fallback_associated_ids - explicit_result_ids),
            "fallback_and_explicit_overlap_count": len(
                fallback_associated_ids & explicit_result_ids
            ),
        },
    }


def _diagnostic_flags(metrics: Mapping[str, Any]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    total = metrics["result_count"]
    retention_unknown = metrics["holding_status_counts"].get("retention_unknown", 0)
    fallback = metrics["selected_routes"]["coverage_counts"].get("fallback", 0)
    partial = metrics["selected_routes"]["coverage_counts"].get("partial", 0)
    if fallback:
        flags.append({
            "code": "fallback_route_selected",
            "message": f"{fallback} selected route(s) fall back to broad parent matching.",
        })
    if partial:
        flags.append({
            "code": "partial_route_selected",
            "message": f"{partial} selected route(s) have only partial inventory coverage.",
        })
    if metrics["inventory_gap_count"]:
        flags.append({
            "code": "inventory_gap",
            "message": f"{metrics['inventory_gap_count']} selected interaction(s) have no defensible direct PIB.",
        })
    if total and retention_unknown / total >= 0.5:
        flags.append({
            "code": "retention_unknown_majority",
            "message": f"Retention is unknown for {retention_unknown} of {total} results.",
        })
    if metrics["uncategorized_result_count"]:
        flags.append({
            "code": "uncategorized_results",
            "message": f"{metrics['uncategorized_result_count']} result(s) have no derived personal-information category.",
        })
    failures = metrics["expectations"]["failed_assertion_count"]
    if failures:
        flags.append({
            "code": "expectation_failure",
            "message": f"{failures} fixture expectation assertion(s) failed.",
        })
    if not metrics["complete_survey"]:
        flags.append({
            "code": "incomplete_survey",
            "message": "The structured survey state is incomplete; results are provisional.",
        })
    return flags


def evaluate_persona(
    engine: SurveyToolEngine,
    persona: Mapping[str, Any],
    *,
    as_of_year: int,
    include_possible: bool,
    page_size: int = 500,
) -> dict[str, Any]:
    persona_id = persona.get("persona_id", persona.get("id", persona.get("slug")))
    if not isinstance(persona_id, str) or not persona_id.strip():
        raise ValueError("Each persona requires a non-empty persona_id, id, or slug")
    name = persona.get("name", persona.get("display_name", persona_id))
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{persona_id}: name must be a non-empty string")

    state = build_state(engine, persona)
    evaluation = evaluate_all_results(
        engine,
        state,
        as_of_year=as_of_year,
        include_possible=include_possible,
        page_size=page_size,
    )
    results = evaluation["results"]
    assessment = evaluation["assessment"]
    category_ids = [
        item["category_id"]
        for result in results
        for item in result["categories_of_personal_information"]
    ]
    category_counts = _sorted_counts(category_ids)
    route_metrics = _route_metrics(engine, state, results)
    expectation_metrics = _expectation_metrics(
        persona.get("expectations"), results, assessment["inventory_gaps"]
    )
    metrics: dict[str, Any] = {
        "result_count": len(results),
        "match_band_counts": _sorted_counts([item["match_band"] for item in results]),
        "holding_status_counts": _sorted_counts(
            [item["holding_status"] for item in results]
        ),
        "scope_counts": _sorted_counts([item["scope"] for item in results]),
        "institution_counts": _sorted_counts(
            [item["institution_name"] for item in results]
        ),
        "selected_routes": route_metrics,
        "complete_survey": assessment["complete_survey"],
        "unanswered_question_count": len(assessment["unanswered_question_codes"]),
        "unanswered_question_codes": assessment["unanswered_question_codes"],
        "uncertain_question_count": len(assessment["uncertain_question_codes"]),
        "uncertain_question_codes": assessment["uncertain_question_codes"],
        "incomplete_refinement_count": len(
            assessment["incomplete_refinement_question_codes"]
        ),
        "incomplete_refinement_question_codes": assessment[
            "incomplete_refinement_question_codes"
        ],
        "inventory_gap_count": len(assessment["inventory_gaps"]),
        "inventory_gaps": assessment["inventory_gaps"],
        "retention_unknown_count": sum(
            item["holding_status"] == "retention_unknown" for item in results
        ),
        "category_coverage": {
            "distinct_category_count": len(category_counts),
            "canonical_category_count": len(engine.categories),
            "coverage_ratio": round(len(category_counts) / len(engine.categories), 4)
            if engine.categories
            else 0.0,
            "category_result_counts": category_counts,
        },
        "uncategorized_result_count": sum(
            not item["categories_of_personal_information"] for item in results
        ),
        "expectations": expectation_metrics,
    }
    metrics["business_logic_flags"] = _diagnostic_flags(metrics)
    return {
        "persona_id": persona_id,
        "name": name,
        "state": state,
        "assessment": assessment,
        "summary": evaluation["summary"],
        "metrics": metrics,
        "analysis": {
            "business_logic_flags": [
                item["message"] for item in metrics["business_logic_flags"]
            ],
            "expectation_failure_count": expectation_metrics["failed_assertion_count"],
        },
        "results": results,
    }


def _aggregate(personas: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    results = [result for persona in personas for result in persona["results"]]
    return {
        "persona_count": len(personas),
        "result_count": len(results),
        "unique_record_count": len({item["record_id"] for item in results}),
        "match_band_counts": _sorted_counts([item["match_band"] for item in results]),
        "holding_status_counts": _sorted_counts(
            [item["holding_status"] for item in results]
        ),
        "scope_counts": _sorted_counts([item["scope"] for item in results]),
        "selected_route_coverage_counts": _sorted_counts([
            route["coverage"]
            for persona in personas
            for route in persona["metrics"]["selected_routes"]["selected"]
        ]),
        "inventory_gap_count": sum(
            persona["metrics"]["inventory_gap_count"] for persona in personas
        ),
        "retention_unknown_count": sum(
            persona["metrics"]["retention_unknown_count"] for persona in personas
        ),
        "expectation_failure_count": sum(
            persona["metrics"]["expectations"]["failed_assertion_count"]
            for persona in personas
        ),
        "fixture_format_issue_count": sum(
            persona["metrics"]["expectations"]["fixture_format_issue_count"]
            for persona in personas
        ),
        "fallback_only_result_count": sum(
            persona["metrics"]["selected_routes"]["result_attribution"][
                "fallback_only_result_count"
            ]
            for persona in personas
        ),
        "explicit_route_result_count": sum(
            persona["metrics"]["selected_routes"]["result_attribution"][
                "explicit_route_result_count"
            ]
            for persona in personas
        ),
        "uncategorized_result_count": sum(
            persona["metrics"]["uncategorized_result_count"] for persona in personas
        ),
    }


def _ranked_findings(
    aggregate: Mapping[str, Any],
    personas: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    total = int(aggregate["result_count"])
    fallback_count = aggregate["selected_route_coverage_counts"].get("fallback", 0)
    strong = aggregate["match_band_counts"].get("strong_match", 0)
    findings: list[dict[str, Any]] = []
    if fallback_count and aggregate["fallback_only_result_count"]:
        findings.append({
            "rank": 1,
            "severity": "high",
            "code": "fallbacks_flatten_to_strong",
            "finding": (
                f"{fallback_count} fallback selections are associated with "
                f"{aggregate['fallback_only_result_count']} fallback-only results, while "
                f"{strong} of {total} results are labelled strong. The engine retains the "
                "broad parent yes for fallback routes instead of lowering match confidence."
            ),
            "recommendation": (
                "Add a fallback-derived match band, or carry route coverage into result "
                "confidence and reserve strong_match for explicit selectors."
            ),
        })
    if total:
        inventory_share = aggregate["unique_record_count"] / int(manifest["pib_count"])
        findings.append({
            "rank": len(findings) + 1,
            "severity": "high" if inventory_share >= 0.25 else "medium",
            "code": "candidate_volume",
            "finding": (
                f"The four personas return {total} results covering "
                f"{aggregate['unique_record_count']} unique PIBs "
                f"({inventory_share:.1%} of the {manifest['pib_count']}-PIB snapshot)."
            ),
            "recommendation": (
                "Prioritize named institution/program routes for the fallback interactions "
                "that contribute the largest candidate sets."
            ),
        })
    if total and aggregate["retention_unknown_count"]:
        unknown_share = aggregate["retention_unknown_count"] / total
        findings.append({
            "rank": len(findings) + 1,
            "severity": "high" if unknown_share >= 0.5 else "medium",
            "code": "retention_unknown",
            "finding": (
                f"Retention is unknown for {aggregate['retention_unknown_count']} of "
                f"{total} results ({unknown_share:.1%})."
            ),
            "recommendation": (
                "Capture the actual retention trigger (for example file closure, departure, "
                "licence expiry, or last administrative action) only where it can materially "
                "change the estimate."
            ),
        })
    if aggregate["uncategorized_result_count"]:
        findings.append({
            "rank": len(findings) + 1,
            "severity": "medium",
            "code": "uncategorized_results",
            "finding": (
                f"{aggregate['uncategorized_result_count']} persona-results have no derived "
                "personal-information category."
            ),
            "recommendation": "Review category extraction evidence for these PIB records.",
        })
    if aggregate["inventory_gap_count"]:
        findings.append({
            "rank": len(findings) + 1,
            "severity": "medium",
            "code": "known_inventory_gaps",
            "finding": (
                f"The fixtures encounter {aggregate['inventory_gap_count']} selected "
                "interactions explicitly marked as inventory gaps."
            ),
            "recommendation": (
                "Keep these visible as coverage limitations; do not substitute broad unrelated "
                "PIBs merely to return a result."
            ),
        })
    if aggregate["fixture_format_issue_count"]:
        findings.append({
            "rank": len(findings) + 1,
            "severity": "test_data",
            "code": "fixture_record_id_format",
            "finding": (
                f"{aggregate['fixture_format_issue_count']} expected record IDs name a bank "
                "that was returned under a different canonical record ID."
            ),
            "recommendation": (
                "Correct fixture record IDs; do not count these as business-logic coverage gaps."
            ),
        })
    if aggregate["expectation_failure_count"]:
        findings.append({
            "rank": len(findings) + 1,
            "severity": "high",
            "code": "genuine_expectation_failures",
            "finding": (
                f"{aggregate['expectation_failure_count']} expectation assertions remain after "
                "record-ID format mismatches are excluded."
            ),
            "recommendation": "Review these as genuine coverage or fixture assertion failures.",
        })
    return findings


def evaluate_fixture(
    fixture: object,
    *,
    engine: SurveyToolEngine | None = None,
    as_of_year: int | None = None,
    include_possible: bool | None = None,
    page_size: int = 500,
) -> dict[str, Any]:
    engine = engine or SurveyToolEngine()
    if isinstance(fixture, list):
        personas = fixture
        defaults: Mapping[str, Any] = {}
    elif isinstance(fixture, Mapping):
        personas = fixture.get("personas")
        defaults = fixture
    else:
        raise ValueError("Persona fixture must be an array or an object with personas")
    if not isinstance(personas, list) or not personas:
        raise ValueError("Persona fixture must contain a non-empty personas array")
    if any(not isinstance(persona, Mapping) for persona in personas):
        raise ValueError("Every personas entry must be an object")

    contract_version = defaults.get("contract_version")
    if contract_version is not None and contract_version != engine.contract["content_version"]:
        raise ValueError(
            "Persona fixture contract_version does not match the canonical engine: "
            f"{contract_version!r} != {engine.contract['content_version']!r}"
        )
    year = (
        as_of_year
        if as_of_year is not None
        else defaults.get("assessment_year", defaults.get("as_of_year"))
    )
    if not isinstance(year, int):
        raise ValueError("Supply an integer as_of_year in the fixture or command line")
    possible = (
        include_possible
        if include_possible is not None
        else bool(defaults.get("include_possible", False))
    )
    reports = [
        evaluate_persona(
            engine,
            persona,
            as_of_year=year,
            include_possible=possible,
            page_size=page_size,
        )
        for persona in personas
    ]
    ids = [item["persona_id"] for item in reports]
    if len(ids) != len(set(ids)):
        raise ValueError("persona_id values must be unique")
    aggregate = _aggregate(reports)
    manifest = engine.get_manifest()
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "configuration": {
            "as_of_year": year,
            "include_possible": possible,
            "page_size": page_size,
        },
        "engine_manifest": manifest,
        "aggregate": aggregate,
        "ranked_findings": _ranked_findings(aggregate, reports, manifest),
        "personas": reports,
    }


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: Mapping[str, Any]) -> str:
    config = report["configuration"]
    manifest = report["engine_manifest"]
    aggregate = report["aggregate"]
    lines = [
        "# My Info persona evaluation",
        "",
        (
            f"Canonical Beta contract `{manifest['contract_version']}` was evaluated as of "
            f"{config['as_of_year']}. Possible matches were "
            f"{'included' if config['include_possible'] else 'excluded'}."
        ),
        "",
        "These are candidate PIBs, not confirmation that an institution holds a record.",
        "",
        "## Cross-persona summary",
        "",
        "| Personas | Results | Unique PIBs | Inventory gaps | Retention unknown | Expectation failures |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {aggregate['persona_count']} | {aggregate['result_count']} | "
            f"{aggregate['unique_record_count']} | {aggregate['inventory_gap_count']} | "
            f"{aggregate['retention_unknown_count']} | "
            f"{aggregate['expectation_failure_count']} |"
        ),
        "",
        "## Ranked business-logic findings",
        "",
    ]
    for finding in report["ranked_findings"]:
        lines.extend([
            f"### {finding['rank']}. {finding['code'].replace('_', ' ').title()} ({finding['severity']})",
            "",
            finding["finding"],
            "",
            f"Recommendation: {finding['recommendation']}",
            "",
        ])
    lines.extend([
        "## Persona summaries",
        "",
        "| Persona | Results | Strong | Possible/review | Unknown retention | Route coverage |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ])
    for persona in report["personas"]:
        metrics = persona["metrics"]
        bands = metrics["match_band_counts"]
        possible = bands.get("possible_match", 0) + bands.get("review_if_relevant", 0)
        routes = ", ".join(
            f"{key}: {value}"
            for key, value in metrics["selected_routes"]["coverage_counts"].items()
        ) or "none"
        lines.append(
            f"| {_cell(persona['name'])} | {metrics['result_count']} | "
            f"{bands.get('strong_match', 0)} | {possible} | "
            f"{metrics['retention_unknown_count']} | {_cell(routes)} |"
        )

    for persona in report["personas"]:
        metrics = persona["metrics"]
        lines.extend(["", f"## {_cell(persona['name'])}", ""])
        lines.append(
            f"The survey produced **{metrics['result_count']}** candidates across "
            f"**{len(metrics['institution_counts'])}** institutions. "
            f"The state is **{'complete' if metrics['complete_survey'] else 'incomplete'}**."
        )
        lines.extend(["", "### Result profile", ""])
        lines.append(
            "- Match bands: "
            + (", ".join(
                f"{key} {value}" for key, value in metrics["match_band_counts"].items()
            ) or "none")
        )
        lines.append(
            "- Holding status: "
            + (", ".join(
                f"{key} {value}" for key, value in metrics["holding_status_counts"].items()
            ) or "none")
        )
        lines.append(
            "- Scope: "
            + (", ".join(
                f"{key} {value}" for key, value in metrics["scope_counts"].items()
            ) or "none")
        )
        top = sorted(
            metrics["institution_counts"].items(), key=lambda item: (-item[1], item[0])
        )[:5]
        lines.append(
            "- Top institutions: "
            + (", ".join(f"{name} ({count})" for name, count in top) or "none")
        )
        coverage = metrics["category_coverage"]
        lines.append(
            f"- Category coverage: {coverage['distinct_category_count']} of "
            f"{coverage['canonical_category_count']} controlled categories; "
            f"{metrics['uncategorized_result_count']} result(s) uncategorized."
        )
        if metrics["inventory_gaps"]:
            gaps = ", ".join(
                item["route_option_code"] for item in metrics["inventory_gaps"]
            )
            lines.append(f"- Inventory gaps: {gaps}.")
        if metrics["unanswered_question_codes"]:
            lines.append(
                f"- Unanswered questions ({metrics['unanswered_question_count']}): "
                + ", ".join(metrics["unanswered_question_codes"])
                + "."
            )

        expectations = metrics["expectations"]
        if expectations["expectations_supplied"]:
            lines.extend(["", "### Fixture expectations", ""])
            lines.append(
                f"Expectation assertions failed: **{expectations['failed_assertion_count']}**."
            )
            for label, values in (
                ("Missing expected record IDs", expectations["expected_record_ids"]["missing"]),
                ("Missing expected bank numbers", expectations["expected_bank_numbers"]["missing"]),
                (
                    "Known likely false-positive record IDs returned",
                    expectations["known_likely_false_positives"]["record_ids_found"],
                ),
                (
                    "Known likely false-positive bank numbers returned",
                    expectations["known_likely_false_positives"]["bank_numbers_found"],
                ),
                ("Allowlist record exceptions", expectations["allowlist_exceptions"]["record_ids"]),
                ("Allowlist bank exceptions", expectations["allowlist_exceptions"]["bank_numbers"]),
            ):
                if values:
                    lines.append(f"- {label}: {', '.join(values)}")
            format_mismatches = expectations["expected_record_ids"]["format_mismatches"]
            if format_mismatches:
                lines.append("- Fixture record-ID format mismatches:")
                lines.extend(
                    f"  - {item['expected_record_id']} -> {', '.join(item['actual_record_ids'])}"
                    for item in format_mismatches
                )
            risks = expectations["qualitative_risks"]
            for label, values in (
                ("Expected ambiguities", risks["expected_ambiguities"]),
                ("Known false-positive risks", risks["known_false_positive_risks"]),
                ("Known false-negative risks", risks["known_false_negative_risks"]),
            ):
                if values:
                    lines.append(f"- {label}:")
                    lines.extend(f"  - {value}" for value in values)

        lines.extend(["", "### Business-logic flags", ""])
        flags = metrics["business_logic_flags"]
        if flags:
            lines.extend(f"- `{item['code']}`: {item['message']}" for item in flags)
        else:
            lines.append("- No automatic diagnostic flags.")

    lines.extend([
        "",
        "## Interpretation guardrails",
        "",
        "- An expected PIB is a test assertion, not proof that a real record exists.",
        "- A likely false positive is reported only when the fixture names it, or when an explicit allowlist is supplied.",
        "- High result counts and unknown retention are diagnostics for review, not automatic failures.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: Mapping[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / JSON_OUTPUT_NAME
    markdown_path = output_dir / MARKDOWN_OUTPUT_NAME
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--as-of-year", type=int)
    possible = parser.add_mutually_exclusive_group()
    possible.add_argument("--include-possible", action="store_true", default=None)
    possible.add_argument("--strong-only", action="store_false", dest="include_possible")
    args = parser.parse_args()

    input_path = args.input
    if input_path == DEFAULT_INPUT and not input_path.exists() and VERSIONED_INPUT_FALLBACK.exists():
        input_path = VERSIONED_INPUT_FALLBACK
    fixture = json.loads(input_path.read_text(encoding="utf-8"))
    report = evaluate_fixture(
        fixture,
        as_of_year=args.as_of_year,
        include_possible=args.include_possible,
    )
    json_path, markdown_path = write_report(report, args.output_dir)
    print(
        f"Evaluated {report['aggregate']['persona_count']} persona(s): "
        f"{report['aggregate']['result_count']} candidate results"
    )
    print(json_path)
    print(markdown_path)


if __name__ == "__main__":
    main()
