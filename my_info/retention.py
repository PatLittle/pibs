"""Conservative retention/disposition feature derivation for My Info.

The source fields are prose, not executable schedules.  This module deliberately
keeps an ``unknown`` outcome whenever a citizen's approximate interaction year is
not enough to apply a rule (for example, a period that starts at file closure).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RetentionPeriod:
    """One duration explicitly observed in the source prose."""

    value: float
    unit: str
    years: float
    qualifier: str
    is_age: bool
    source_language: str
    context: str


@dataclass(frozen=True)
class RetentionFeatures:
    """Structured, source-faithful interpretation of a bilingual retention rule."""

    raw_text_en: str
    raw_text_fr: str
    rule_type: str
    reference_events: tuple[str, ...]
    periods: tuple[RetentionPeriod, ...]
    minimum_years: float | None
    maximum_years: float | None
    disposition: str
    has_indefinite_component: bool
    has_immediate_disposal: bool
    requires_institution_contact: bool
    requires_schedule_lookup: bool
    is_under_review: bool
    confidence: str
    language_agreement: str
    method: str
    provenance: tuple[str, ...]
    caveats: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready representation without dropping the raw prose."""

        return asdict(self)


@dataclass(frozen=True)
class HoldingEstimate:
    """A conservative citizen-facing estimate as of a particular year."""

    status: str
    confidence: str
    interaction_year: int
    as_of_year: int
    trigger_year: int | None
    elapsed_years: int | None
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_ONES = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen",
}
_TENS = {
    20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
    60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety",
}


def _english_number(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return _TENS[tens * 10] + (f"-{_ONES[ones]}" if ones else "")
    hundreds, remainder = divmod(n, 100)
    result = f"{_ONES[hundreds]} hundred"
    return result + (f" and {_english_number(remainder)}" if remainder else "")


_FRENCH_NUMBERS = {
    "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4,
    "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10,
    "onze": 11, "douze": 12, "treize": 13, "quatorze": 14,
    "quinze": 15, "seize": 16, "vingt": 20, "vingt-cinq": 25,
    "trente": 30, "trente-cinq": 35, "quarante": 40, "cinquante": 50,
    "soixante": 60, "soixante-cinq": 65, "soixante-dix": 70,
    "soixante-quinze": 75, "quatre-vingts": 80, "quatre-vingt-dix": 90,
    "quatre-vingt-dix-neuf": 99, "cent": 100, "cent cinquante": 150,
}
_NUMBER_WORDS = {_english_number(n): n for n in range(1, 201)} | _FRENCH_NUMBERS
_WORD_NUMBER_PATTERN = "|".join(
    re.escape(word) for word in sorted(_NUMBER_WORDS, key=len, reverse=True)
)
_NUMBER_PATTERN = rf"(?:\d+(?:\.\d+)?|{_WORD_NUMBER_PATTERN})"
_UNIT_PATTERN = r"(?:(?:calendar|fiscal|full)\s+)?(?:years?|months?|days?)|ans?|ann(?:e|é)es?|mois|jours?"
_PERIOD_RE = re.compile(
    rf"(?P<number>{_NUMBER_PATTERN})(?:\s*\(\s*\d+(?:\.\d+)?\s*\))?"
    rf"\s+(?P<unit>{_UNIT_PATTERN})\b",
    re.IGNORECASE,
)
_RANGE_RE = re.compile(
    rf"(?:between\s+|from\s+|de\s+|entre\s+)?(?P<low>{_NUMBER_PATTERN})"
    rf"\s+(?:to|and|à|a|et)\s+(?P<high>{_NUMBER_PATTERN})\s+"
    rf"(?P<unit>{_UNIT_PATTERN})\b",
    re.IGNORECASE,
)


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().lower()


def _number(value: str) -> float:
    folded = _fold(value)
    if re.fullmatch(r"\d+(?:\.\d+)?", folded):
        return float(folded)
    return float(_NUMBER_WORDS[folded])


def _years(value: float, unit: str) -> float:
    folded = _fold(unit)
    if "month" in folded or folded.startswith("mois"):
        result = value / 12
    elif "day" in folded or folded.startswith("jour"):
        result = value / 365.25
    else:
        result = value
    return round(result, 4)


def _qualifier(prefix: str) -> str:
    if re.search(r"(?:minimum(?: retention)?(?: period)?(?: of)?|at least|not less than|au moins|minim(?:um|ale))\s*$", prefix):
        return "minimum"
    if re.search(r"(?:up to|maximum(?: of)?|no more than|jusqu(?:'|’)a|au plus|maxim(?:um|ale))\s*$", prefix):
        return "maximum"
    return "exact"


def _extract_periods(text: str, language: str) -> tuple[RetentionPeriod, ...]:
    folded = _fold(text)
    ranges: list[tuple[int, int]] = []
    periods: list[RetentionPeriod] = []

    for match in _RANGE_RE.finditer(folded):
        low, high = _number(match["low"]), _number(match["high"])
        unit = match["unit"]
        context = folded[max(0, match.start() - 45):min(len(folded), match.end() + 60)]
        is_age = bool(re.search(r"(?:of age|d'age|d age)", folded[match.end():match.end() + 18]))
        periods.extend((
            RetentionPeriod(low, unit, _years(low, unit), "minimum", is_age, language, context),
            RetentionPeriod(high, unit, _years(high, unit), "maximum", is_age, language, context),
        ))
        ranges.append(match.span())

    for match in _PERIOD_RE.finditer(folded):
        if any(start <= match.start() and match.end() <= end for start, end in ranges):
            continue
        value, unit = _number(match["number"]), match["unit"]
        prefix = folded[max(0, match.start() - 45):match.start()]
        suffix = folded[match.end():match.end() + 22]
        is_age = bool(re.search(r"^\s*(?:of age|d'age|d age)", suffix))
        context = folded[max(0, match.start() - 45):min(len(folded), match.end() + 60)]
        periods.append(RetentionPeriod(
            value=value,
            unit=unit,
            years=_years(value, unit),
            qualifier=_qualifier(prefix),
            is_age=is_age,
            source_language=language,
            context=context,
        ))
    return tuple(periods)


_PENDING_RE = re.compile(
    r"under (?:development|review)|to be (?:determined|established|decided)|"
    r"not yet (?:determined|established)|undetermined period|\bindeterminate\b|periode indeterminee|forthcoming rda|"
    r"has not issued a records disposition authority|en cours (?:d'elaboration|d'examen|de revision)|"
    r"a (?:determiner|etablir)|sera determine",
)
_CONTACT_RE = re.compile(
    r"(?:please )?contact|access to information and privacy coordinator|"
    r"communiqu(?:er|ez)|coordonnateur.*(?:acces|protection)",
)
_INDEFINITE_RE = re.compile(
    r"indefinite(?:ly| period)?|indeterminately|kept forever|never destroyed|"
    r"(?:retained|kept|maintained|stored|preserved).{0,30}permanent(?:ly)?|permanent retention|"
    r"permanently (?:retain|maintain|keep|preserve)|"
    r"conserve(?:s|es|e)? indefiniment|conservation permanente|jamais detruit",
)
_NO_DISPOSAL_RE = re.compile(
    r"no records? can be disposed|must be retained in (?:their|its) entirety|"
    r"aucun dossier ne peut etre (?:detruit|elimine)",
)
_IMMEDIATE_RE = re.compile(
    r"destroyed immediately|immediate disposal|destroyed after (?:scanning|imaging|microfilming)|"
    r"immediatement (?:detruit|eliminee?|supprime)",
)
_DESTROY_RE = re.compile(
    r"destroy(?:ed|uction)?|delet(?:ed|ion)|disposed of|purged|shredded|"
    r"detruit|destruction|eliminee?|elimination|supprime|dechiquete",
)
_ARCHIVE_RE = re.compile(
    r"(?:transfer(?:red)?|forwarded) (?:to|into).*?(?:library and archives|archives canada)|"
    r"archival (?:value|purposes?|records?)|historical (?:value|purposes?|records?)|"
    r"transfere.*?(?:bibliotheque et archives|archives canada)|valeur archivistique",
)
_SCHEDULE_RE = re.compile(
    r"(?:governed by|in accordance with|subject to|applicable) (?:the )?.{0,50}"
    r"(?:retention and disposal schedule|records disposition authority|rda)|"
    r"retention and disposal schedules? (?:approved|applicable)|"
    r"calendrier.*conservation|autorisation de disposition",
)


def _signals(text: str) -> dict[str, bool]:
    return {
        "pending": bool(_PENDING_RE.search(text)),
        "contact": bool(_CONTACT_RE.search(text)),
        "schedule": bool(_SCHEDULE_RE.search(text)),
        "indefinite": bool(_INDEFINITE_RE.search(text) or _NO_DISPOSAL_RE.search(text)),
        "no_disposal": bool(_NO_DISPOSAL_RE.search(text)),
        "immediate": bool(_IMMEDIATE_RE.search(text)),
        "destroy": bool(_DESTROY_RE.search(text)),
        "archive": bool(_ARCHIVE_RE.search(text)),
    }


def _reference_events(text: str) -> tuple[str, ...]:
    patterns = (
        ("last_administrative_action", r"last administrative (?:action|use)|derniere (?:mesure|utilisation) administrative"),
        ("file_or_case_closure", r"(?:file|case) (?:is )?closed|closure of (?:the )?(?:file|case)|fermeture du dossier"),
        ("employment_or_service_end", r"departure|termination|end of employment|duration of employment|end of service|fin d'emploi|depart"),
        ("program_or_relationship_end", r"end of (?:the )?(?:agreement|training|benefits?|sponsorship)|subscription is active|business relationship|programme prend fin"),
        ("record_creation_or_receipt", r"date of (?:receipt|collection|creation)|(?:record|request) (?:was )?(?:received|created|logged)|transaction took place|date de (?:reception|creation)"),
        ("date_of_issue", r"date of issu(?:e|ance)|date de delivrance"),
        ("individual_age", r"years? of age|reaches?.{0,30}\bage|birthday|ans d'age|atteint l'age"),
        ("death", r"death|deceased|deces"),
        ("superseded_or_obsolete", r"supersed|replaced|obsolete|remplace|desuet"),
        ("operational_or_business_need_end", r"operational needs? (?:have )?expired|no longer (?:required|has business value)|as long as .*? required|besoins operationnels"),
        ("condition_or_status_end", r"until (?:such time as )?.{0,45}(?:closes|is released|warrant)|execution of warrant|if .*?not updated annually"),
    )
    events = tuple(name for name, pattern in patterns if re.search(pattern, text))
    return events or ("unspecified_start",)


def _bounds(periods: tuple[RetentionPeriod, ...], signals: dict[str, bool]) -> tuple[float | None, float | None]:
    durations = [period for period in periods if not period.is_age]
    if not durations:
        return None, None
    minimums = [period.years for period in durations if period.qualifier == "minimum"]
    maximums = [period.years for period in durations if period.qualifier == "maximum"]
    exacts = [period.years for period in durations if period.qualifier == "exact"]

    minimum = min(minimums) if minimums else None
    maximum = max(maximums) if maximums else None
    if len(durations) == 1 and exacts:
        minimum = maximum = exacts[0]
    elif len(set(period.years for period in durations)) == 1 and exacts:
        minimum = maximum = exacts[0]

    # An indefinite branch defeats any global maximum; an immediate-disposal
    # branch defeats any global minimum.  The observed periods remain available.
    if signals["indefinite"]:
        maximum = None
    if signals["immediate"]:
        minimum = None
    return minimum, maximum


def _disposition(signals: dict[str, bool]) -> str:
    if signals["no_disposal"]:
        return "retention_required"
    if signals["destroy"] and signals["archive"]:
        return "destroy_or_transfer"
    if signals["destroy"]:
        return "destroy"
    if signals["archive"]:
        return "transfer_to_archives"
    if signals["indefinite"]:
        return "retain"
    return "unknown"


def _agreement(en_periods: tuple[RetentionPeriod, ...], fr_periods: tuple[RetentionPeriod, ...], raw_en: str, raw_fr: str) -> str:
    if not raw_en or not raw_fr:
        return "not_comparable"
    en_values = {(p.years, p.is_age) for p in en_periods}
    fr_values = {(p.years, p.is_age) for p in fr_periods}
    if not en_values and not fr_values:
        return "no_numeric_periods"
    return "consistent" if en_values == fr_values else "mismatch"


def parse_retention(raw_text_en: str | None, raw_text_fr: str | None = None) -> RetentionFeatures:
    """Parse bilingual source prose into conservative structured features.

    English is the primary source when present. French is a fallback and a
    cross-check; disagreement is surfaced instead of silently reconciling it.
    """

    raw_en, raw_fr = str(raw_text_en or "").strip(), str(raw_text_fr or "").strip()
    folded_en, folded_fr = _fold(raw_en), _fold(raw_fr)
    en_periods = _extract_periods(raw_en, "en") if raw_en else ()
    fr_periods = _extract_periods(raw_fr, "fr") if raw_fr else ()
    primary_text = folded_en or folded_fr
    primary_periods = en_periods if folded_en else fr_periods
    signals = _signals(primary_text)
    minimum, maximum = _bounds(primary_periods, signals)
    duration_periods = tuple(period for period in primary_periods if not period.is_age)
    age_periods = tuple(period for period in primary_periods if period.is_age)

    if not primary_text:
        rule_type = "unknown"
    elif signals["indefinite"] and not duration_periods and not signals["destroy"]:
        rule_type = "indefinite"
    elif signals["pending"] and not duration_periods:
        rule_type = "policy_pending"
    elif signals["contact"] and not duration_periods:
        rule_type = "institution_defined"
    elif signals["schedule"] and not duration_periods:
        rule_type = "schedule_defined"
    elif age_periods and not duration_periods:
        rule_type = "trigger_based"
    elif signals["indefinite"] and signals["destroy"] and not duration_periods:
        rule_type = "conditional_periods"
    elif not duration_periods:
        rule_type = "trigger_based" if _reference_events(primary_text) != ("unspecified_start",) else "unknown"
    elif signals["pending"] or signals["indefinite"] or signals["immediate"] or len(duration_periods) > 2:
        rule_type = "conditional_periods"
    elif minimum is not None and maximum is not None and minimum != maximum:
        rule_type = "bounded_range"
    elif minimum is not None and maximum is None:
        rule_type = "minimum_period"
    elif minimum is None and maximum is not None:
        rule_type = "maximum_period"
    elif minimum is not None:
        rule_type = "fixed_period"
    else:
        rule_type = "conditional_periods"

    agreement = _agreement(en_periods, fr_periods, raw_en, raw_fr)
    if rule_type in {"unknown", "policy_pending", "institution_defined", "schedule_defined", "conditional_periods"}:
        confidence = "low"
    elif rule_type == "fixed_period" and _disposition(signals) != "unknown":
        confidence = "high" if _reference_events(primary_text) != ("unspecified_start",) else "medium"
    else:
        confidence = "medium"
    if agreement == "mismatch":
        confidence = "low"

    caveats: list[str] = []
    if rule_type in {"unknown", "policy_pending", "institution_defined", "schedule_defined"}:
        caveats.append("No defensible calendar disposal date can be derived from this text.")
    if len(duration_periods) > 1:
        caveats.append("The text contains multiple periods that may apply to different record types or circumstances.")
    if age_periods:
        caveats.append("A stated age is a trigger, not a duration from the citizen's interaction year.")
    if signals["indefinite"] and duration_periods:
        caveats.append("At least one branch is indefinite, so no overall maximum retention period is inferred.")
    if signals["immediate"]:
        caveats.append("At least one branch allows immediate disposal, so no overall minimum retention period is inferred.")
    if agreement == "mismatch":
        caveats.append("English and French numeric periods differ; the English text remains primary.")
    if _reference_events(primary_text) == ("unspecified_start",) and duration_periods:
        caveats.append("The event that starts the retention clock is not explicit.")

    provenance = (("retention_en:primary", "retention_fr:cross_check") if raw_en and raw_fr
                  else (("retention_en:primary",) if raw_en else (("retention_fr:fallback",) if raw_fr else ())))
    return RetentionFeatures(
        raw_text_en=raw_en,
        raw_text_fr=raw_fr,
        rule_type=rule_type,
        reference_events=_reference_events(primary_text) if primary_text else (),
        periods=primary_periods,
        minimum_years=minimum,
        maximum_years=maximum,
        disposition=_disposition(signals),
        has_indefinite_component=signals["indefinite"],
        has_immediate_disposal=signals["immediate"],
        requires_institution_contact=signals["contact"],
        requires_schedule_lookup=signals["schedule"],
        is_under_review=signals["pending"],
        confidence=confidence,
        language_agreement=agreement,
        method="deterministic_regex_v1",
        provenance=provenance,
        caveats=tuple(caveats),
    )


def derive_retention(record: Any) -> RetentionFeatures:
    """Derive features from a normalized ``PibRecord``-like object."""

    return parse_retention(record.retention_en, record.retention_fr)


def estimate_holding(
    features: RetentionFeatures,
    interaction_year: int,
    as_of_year: int,
    *,
    trigger_year: int | None = None,
) -> HoldingEstimate:
    """Estimate likely holding without treating an interaction year as every trigger.

    ``trigger_year`` should be supplied when the prose starts its clock at file
    closure, last administrative action, departure, or another later event.
    """

    if interaction_year > as_of_year:
        raise ValueError("interaction_year cannot be after as_of_year")
    if trigger_year is not None and trigger_year > as_of_year:
        raise ValueError("trigger_year cannot be after as_of_year")

    if features.rule_type == "indefinite":
        return HoldingEstimate(
            "likely_held", features.confidence, interaction_year, as_of_year,
            trigger_year, None, "The published rule says the records are retained indefinitely.",
        )
    if features.rule_type in {"unknown", "policy_pending", "institution_defined", "schedule_defined", "trigger_based"}:
        return HoldingEstimate(
            "uncertain", "low", interaction_year, as_of_year, trigger_year, None,
            "The published rule does not provide a duration that can be applied to the supplied year.",
        )
    if features.has_immediate_disposal or features.has_indefinite_component:
        return HoldingEstimate(
            "uncertain", "low", interaction_year, as_of_year, trigger_year, None,
            "Different branches permit immediate disposal or indefinite retention.",
        )

    needs_distinct_trigger = any(event not in {"unspecified_start", "record_creation_or_receipt", "date_of_issue"}
                                 for event in features.reference_events)
    if needs_distinct_trigger and trigger_year is None:
        return HoldingEstimate(
            "uncertain", "low", interaction_year, as_of_year, None, None,
            "The retention clock starts at a later event; ask for that event's approximate year.",
        )
    effective_year = trigger_year if trigger_year is not None else interaction_year
    elapsed = as_of_year - effective_year
    minimum, maximum = features.minimum_years, features.maximum_years

    if minimum is not None and elapsed < minimum:
        return HoldingEstimate(
            "likely_held", features.confidence, interaction_year, as_of_year,
            trigger_year, elapsed, "The elapsed time is shorter than the published minimum/fixed retention period.",
        )
    if maximum is not None and elapsed > maximum:
        if features.disposition == "destroy":
            status, rationale = "likely_disposed", "The elapsed time exceeds the published maximum/fixed period, followed by destruction."
        elif features.disposition == "transfer_to_archives":
            status, rationale = "likely_held", "The elapsed time exceeds the institutional period, but the rule says records transfer to Library and Archives Canada."
        else:
            status, rationale = "uncertain", "The elapsed time exceeds the stated period, but the final disposition is conditional or unspecified."
        return HoldingEstimate(status, features.confidence, interaction_year, as_of_year,
                               trigger_year, elapsed, rationale)
    if minimum is not None and maximum == minimum and elapsed == maximum:
        return HoldingEstimate(
            "uncertain", "low", interaction_year, as_of_year, trigger_year, elapsed,
            "The approximate year falls on the disposal boundary.",
        )
    return HoldingEstimate(
        "uncertain", features.confidence, interaction_year, as_of_year, trigger_year, elapsed,
        "The source provides only a minimum, maximum, range, or conditional period at this elapsed time.",
    )
