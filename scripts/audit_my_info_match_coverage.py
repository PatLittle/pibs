#!/usr/bin/env python3
"""Audit theoretical PIB reachability in the My Info survey.

This is a static upper bound, not a precision, recall, or user-frequency score.
It mirrors the engine's primary/candidate and explicit-bank route gates, including
the exclusive route guard, but does not assume that any particular person used a
program or selected the corresponding institution and timing.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from my_info.adaptive import adaptive_routes

SOURCE = ROOT / "data/derived/my_info/my_info_pib_features.csv"
DETAIL = ROOT / "data/audits/my_info_match_coverage.csv"
REPORT = ROOT / "docs/MY_INFO_MATCH_COVERAGE_AUDIT.md"


def audit_rows() -> list[dict[str, str]]:
    routes = adaptive_routes()
    named = {
        bank for route in routes for option in route["options"]
        for bank in option["selectors"]["bank_numbers"]
    }
    exclusive = {
        bank for route in routes for option in route["options"]
        if option["exclusive"] for bank in option["selectors"]["bank_numbers"]
    }
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    result = []
    for row in source_rows:
        bank = row["bank_number_key"]
        primary = bool(row["question_codes"]) and bank not in exclusive
        explicit = bank in named
        candidate = bool(row["candidate_question_codes"]) and bank not in exclusive
        band = "direct" if primary or explicit else "possible_only" if candidate else "not_discoverable"
        result.append({
            "record_id": row["record_id"],
            "scope": row["scope"],
            "institution_id": row["institution_id"],
            "institution_name_en": row["institution_name_en"],
            "bank_number_key": bank,
            "title_en": row["title_en"],
            "reachability": band,
            "primary_question_codes": row["question_codes"] if primary else "",
            "candidate_question_codes": row["candidate_question_codes"] if candidate else "",
            "named_route": str(explicit).lower(),
            "exclusive_route_required": str(bank in exclusive).lower(),
        })
    return result


def write_audit(rows: list[dict[str, str]]) -> None:
    DETAIL.parent.mkdir(parents=True, exist_ok=True)
    with DETAIL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["reachability"] for row in rows)
    total = len(rows)
    pct = lambda count: f"{100 * count / total:.1f}%"
    possible = [row for row in rows if row["reachability"] == "possible_only"]
    absent = [row for row in rows if row["reachability"] == "not_discoverable"]
    possible_codes = Counter(
        code for row in possible for code in row["candidate_question_codes"].split("|") if code
    )
    weak_institutions = Counter(row["institution_name_en"] for row in possible)
    title_registration = [
        row for row in rows
        if "registration" in row["title_en"].casefold()
        and row["reachability"] != "direct"
    ]
    lines = [
        "# My Info PIB-to-question matching audit",
        "",
        "Generated from the current bilingual PIB feature inventory and adaptive-route selectors. "
        "Every record is classified in [`my_info_match_coverage.csv`](../data/audits/my_info_match_coverage.csv).",
        "",
        "## What the percentages mean",
        "",
        f"| Reachability | PIBs | Share of {total:,} | Normal web results |",
        "|---|---:|---:|---|",
        f"| Direct question or named activity route | {counts['direct']:,} | {pct(counts['direct'])} | Potentially shown after matching answers/refinements |",
        f"| Broad candidate match only | {counts['possible_only']:,} | {pct(counts['possible_only'])} | Hidden; the web uses `includePossible: false` |",
        f"| No matching question or route | {counts['not_discoverable']:,} | {pct(counts['not_discoverable'])} | Cannot be found by current questions |",
        "",
        f"The theoretical direct ceiling is **{pct(counts['direct'])}**. With optional possible matches enabled, "
        f"the keyword-based ceiling is **{pct(counts['direct'] + counts['possible_only'])}**, "
        "but these broad signals can be false positives and should not be presented as confirmed holdings. "
        "The percentages are inventory coverage, not recall against real people's records. A single person will "
        "normally see far fewer PIBs because activities, department selection, and retention timing differ.",
        "The faster ten-year path also skips the broader tax/customs, travel, and civic questions after "
        "its four selected common activities. Its personal reachability is therefore narrower than the "
        "full-survey ceiling; the UI discloses that older and other interactions are not ruled out.",
        "",
        "## Largest candidate-only clusters",
        "",
        "These overlapping counts identify where the question recognizes words in PIB text but lacks "
        "strong enough evidence or a named route to show the record in the normal web results.",
        "",
        "| Question | Candidate-only PIBs |",
        "|---|---:|",
    ]
    for code, count in possible_codes.most_common():
        lines.append(f"| `{code}` | {count:,} |")
    lines.extend([
        "",
        "The institutions with the most candidate-only PIBs are:",
        "",
        "| Institution | Candidate-only PIBs |",
        "|---|---:|",
    ])
    for institution, count in weak_institutions.most_common(15):
        lines.append(f"| {institution.replace('|', '/')} | {count:,} |")
    lines.extend([
        "",
        "## Concrete false-positive and source gaps",
        "",
        "- `CSA PPU 020` describes registering to **attend a space mission launch**. Bare “registration” "
        "previously made this a direct business match. Registration alone is no longer a business signal; "
        "the PIB now requires the named public-event route, and unrelated candidate keywords such as "
        "passport or citizenship details cannot surface it.",
        "- `HC PPU 035` is a pesticide-exposure **pilot study**, not an aviation-pilot licensing "
        "service. `IRCC PPU 080` involves identity and refugee travel **certificates**, not a "
        "business permit. Generic 'pilot' and 'certificate' signals no longer make these direct "
        "business matches.",
        "- `ERC PPU 801–805` require the RCMP-member review route. A generic complaint cannot surface them; "
        "the department prompt asks who actually handled the complaint or appeal.",
        "- Federal income-tax filing and federal voting remain explicit **source-inventory gaps**: the "
        "questionnaire asks about them, but this PIB inventory does not provide defensible named "
        "matches for those activity routes. A ten-year shortcut therefore must not invent results for them.",
        f"- {len(title_registration)} records with “registration” in the English title are not direct matches; "
        "they need a specific activity route or stronger context, not a generic business inference.",
        "",
        "## Records the questions cannot discover",
        "",
        "These are the current zero-signal cases, not necessarily PIBs that should all be shown to "
        "the general public. Several describe internal, technical, professional or institutional workflows; "
        "others have poorly parsed titles, so source quality and question design both need review.",
        "",
        "| PIB | Institution | Title |",
        "|---|---|---|",
    ])
    for row in absent:
        lines.append(
            f"| `{row['bank_number_key']}` | {row['institution_name_en'].replace('|', '/')} "
            f"| {row['title_en'].replace('|', '/')} |"
        )
    lines.extend([
        "",
        "## Interpretation and next review priorities",
        "",
        "1. Manually review the high-volume candidate-only business, employment, justice, money, and health "
        "clusters against the actual class of individuals and purpose text. A matching word may be a "
        "piece of information held, not an activity the person performed.",
        "2. Add named, source-backed routes for common activities only when the PIB's purpose and eligible "
        "population align. A route should not be added merely to increase the coverage percentage.",
        "3. Repair malformed or generic source titles among the zero-signal cases, then reassess whether "
        "a user-facing question is warranted for each service.",
        "4. Keep separate tests for false-positive cases, especially records whose titles use broad words "
        "such as registration, service, application, health, or contact.",
        "",
        "Rebuild the audit with `.venv/bin/python scripts/audit_my_info_match_coverage.py`. "
        "Run `build_my_info_features.py` first after changing classification rules or routes.",
        "",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = audit_rows()
    write_audit(rows)
    counts = Counter(row["reachability"] for row in rows)
    print(f"{len(rows)} PIBs: {counts['direct']} direct, {counts['possible_only']} possible-only, {counts['not_discoverable']} undiscoverable")


if __name__ == "__main__":
    main()
