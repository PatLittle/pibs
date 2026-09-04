#!/usr/bin/env python3
"""Extract explicitly enumerated personal-information types from PIB descriptions.

The extractor is intentionally conservative: it only reads clauses introduced by
an explicit English or French personal-information list phrase.  Values retain
the language and wording of the source description and are serialized as JSON by
the institution table compiler.
"""

from __future__ import annotations

import re


_LIST_INTRODUCERS = {
    "en": re.compile(
        r"\bpersonal information\b[^.!?]{0,240}?\b"
        r"(?:may include|may comprise|includes|consists of)\s*:?[\s*]*",
        re.IGNORECASE,
    ),
    "fr": re.compile(
        r"\b(?:les |des )?renseignements personnels\b[^.!?]{0,240}?\b"
        r"(?:peuvent (?:comprendre|inclure)|comprennent|incluent|consistent en)\s*:?[\s*]*",
        re.IGNORECASE,
    ),
}

_SENTENCE_END = re.compile(r"[.!?](?=\s+(?:[*#]+\s*)?[A-ZÀ-ÖØ-Þ]|$)")
_MARKDOWN_LINK = re.compile(r"\[([^]]+)]\([^)]+\)")
_LEADING_DETERMINER = {
    "en": re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE),
    "fr": re.compile(
        r"^(?:de l[’']|de la|les|des|une|un|du|le|la|l[’'])\s*",
        re.IGNORECASE,
    ),
}
_GENERIC_CATCH_ALL = {
    "en": re.compile(
        r"^(?:any |all |other )?(?:relevant )?personal information\b|"
        r"^information (?:contained|found|held) in\b",
        re.IGNORECASE,
    ),
    "fr": re.compile(
        r"^(?:(?:tout |tous |toute |toutes |autres? )(?:les? )?|d[’']autres )"
        r"renseignements? personnels?\b|"
        r"^renseignements? (?:contenus?|figurant|détenus?)\b",
        re.IGNORECASE,
    ),
}

# These are single, conventional information types despite containing a list
# conjunction. Placeholders prevent the conjunction pass from splitting them.
_COMPOUND_TYPES = {
    "en": (
        "date and place of birth",
        "date and place of death",
        "views and opinions",
        "opinions and views",
    ),
    "fr": (
        "date et (?:le )?lieu de naissance",
        "date et (?:le )?lieu de décès",
        "points de vue et opinions",
        "opinions et points de vue",
    ),
}


def _enumerated_clause(description: str, match: re.Match[str]) -> str:
    """Return the remainder of the introducer sentence, tolerating abbreviations."""
    tail = description[match.end():]
    end = _SENTENCE_END.search(tail)
    return tail[: end.start()] if end else tail


def _split_outside_parentheses(value: str) -> list[str]:
    """Split comma/semicolon delimiters without breaking examples in parentheses."""
    parts: list[str] = []
    start = 0
    depth = 0
    for index, character in enumerate(value):
        if character in "([":
            depth += 1
        elif character in ")]" and depth:
            depth -= 1
        elif character in ",;" and depth == 0:
            parts.append(value[start:index])
            start = index + 1
        elif (
            character in "*•"
            and depth == 0
            and (index == 0 or value[index - 1].isspace())
            and (index + 1 == len(value) or value[index + 1].isspace())
        ):
            parts.append(value[start:index])
            start = index + 1
    parts.append(value[start:])
    return parts


def _split_conjunctions(value: str, language: str) -> list[str]:
    protected = value
    replacements: dict[str, str] = {}
    for index, compound in enumerate(_COMPOUND_TYPES[language]):
        token = f"__compound_{index}__"
        pattern = compound if language == "fr" else re.escape(compound)
        protected = re.sub(pattern, token, protected, flags=re.IGNORECASE)
        replacements[token] = re.sub(r"\(\?:le \)\?", "", compound)
    conjunction = r"\s+(?:and|as well as)\s+" if language == "en" else r"\s+(?:et|ainsi que)\s+"
    parts = re.split(conjunction, protected, flags=re.IGNORECASE)
    for index, part in enumerate(parts):
        for token, compound in replacements.items():
            part = part.replace(token, compound)
        parts[index] = part
    return parts


def _clean_item(value: str, language: str) -> str:
    value = _MARKDOWN_LINK.sub(r"\1", value)
    value = re.sub(r"^[\s:–—*•-]+|[\s:–—*•-]+$", "", value)
    value = re.sub(r"^(?:including|such as)\s+", "", value, flags=re.IGNORECASE)
    if language == "fr":
        value = re.sub(r"^(?:notamment|comme)\s+", "", value, flags=re.IGNORECASE)
    value = _LEADING_DETERMINER[language].sub("", value)
    return re.sub(r"\s+", " ", value).strip(" ,;:")


def extract_specific_information_types(description: object, language: str) -> list[str]:
    """Extract source-language types from explicit enumerations, in source order.

    Generic catch-all tails (for example, ``other personal information in
    relevant records``) are excluded because they are not specific types.
    Duplicate items are collapsed case-insensitively without reordering.
    """
    if language not in _LIST_INTRODUCERS:
        raise ValueError(f"Unsupported language: {language}")
    text = re.sub(r"\s+", " ", str(description or "")).strip()
    values: list[str] = []
    seen: set[str] = set()
    for match in _LIST_INTRODUCERS[language].finditer(text):
        clause = _enumerated_clause(text, match)
        for comma_part in _split_outside_parentheses(clause):
            for candidate in _split_conjunctions(comma_part, language):
                item = _clean_item(candidate, language)
                if not item or _GENERIC_CATCH_ALL[language].search(item):
                    continue
                key = item.casefold()
                if key not in seen:
                    seen.add(key)
                    values.append(item)
    return values
