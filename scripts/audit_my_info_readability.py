#!/usr/bin/env python3
"""Generate the English readability audit for My Info survey questions."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from my_info.interactions import questionnaire_questions
from my_info.readability import PROPOSED_QUESTION_WORDING_EN, audit_questions


CSV_PATH = ROOT / "data" / "derived" / "my_info" / "my_info_question_readability.csv"
REPORT_PATH = ROOT / "docs" / "MY_INFO_READABILITY_AUDIT.md"


def build_audit() -> list[dict[str, object]]:
    return audit_questions(
        questionnaire_questions(), proposed_wording=PROPOSED_QUESTION_WORDING_EN
    )


def write_csv(rows: list[dict[str, object]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "code",
        "question_en",
        "score",
        "band",
        "is_outlier",
        "sentences",
        "words",
        "syllables",
        "proposed_question_en",
        "proposed_score",
        "proposed_band",
        "score_change",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict[str, object]]) -> None:
    outliers = [row for row in rows if row["is_outlier"]]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# My Info English question readability audit",
        "",
        "This audit screens every current English top-level question with the Flesch Reading Ease formula. It is a comparative plain-language screen, not a substitute for user testing or content-design review.",
        "",
        "## Method",
        "",
        "The score is `206.835 - 1.015 × words per sentence - 84.6 × syllables per word`. Words are English alphabetic tokens; hyphenated and apostrophized terms count as one word, with each component included in the syllable estimate. The syllable heuristic counts vowel groups, treats `y` as a vowel when it is not next to another vowel, removes a likely silent final `e` except consonant + `le`, and assigns at least one syllable to each non-empty word part.",
        "",
        "The conventional bands are: 90+ very easy; 80–89 easy; 70–79 fairly easy; 60–69 standard; 50–59 fairly difficult; 30–49 difficult; below 30 very difficult. This audit flags scores below 60 for review. The threshold is configurable in `my_info.readability.flesch_reading_ease`.",
        "",
        "Flesch Reading Ease is an English formula. **Do not use these scores to assess the French questions.** French copy needs a French-language measure and fluent plain-language review.",
        "",
        "## Results",
        "",
        f"{len(outliers)} of {len(rows)} current questions score below 60. The many flags reflect long grouped questions and unavoidable multisyllabic program terms as well as genuine wording complexity. The proposed wording moves detailed program types into examples or follow-ups.",
        "",
        "| Code | Current score | Band | Proposed score | Change |",
        "|---|---:|---|---:|---:|",
    ]
    for row in rows:
        proposed_score = row.get("proposed_score", "—")
        change = row.get("score_change", "—")
        lines.append(
            f"| `{row['code']}` | {row['score']} | {row['band']} | {proposed_score} | {change} |"
        )
    lines.extend([
        "",
        "## Questions flagged for rewording",
        "",
    ])
    for row in outliers:
        lines.extend([
            f"### `{row['code']}`",
            "",
            f"Current ({row['score']}, {row['band']}): {row['question_en']}",
            "",
            f"Candidate ({row['proposed_score']}, {row['proposed_band']}): {row['proposed_question_en']}",
            "",
        ])
    lines.extend([
        "## Design observations",
        "",
        "- `q_research_survey` is the only current question at or above the audit threshold (65.7). It can remain as written, subject to usability testing.",
        "- `q_justice_safety` remains below 60 even after a shorter rewrite. It combines sensitive, distinct interactions and should be split into short adaptive routing questions.",
        "- `q_business_supplier` crosses the numeric threshold after rewriting, but still combines unrelated contracting, licensing, and permit routes. Its readability score does not remove the need to split it.",
        "- `q_tax_customs`, `q_travel_border`, and `q_military_veterans` also combine activities owned by different institutions. Readability improves when the survey first asks about the familiar activity and infers the likely institution.",
        "- A score can improve by deleting essential meaning. Rewrites therefore need semantic review against the PIB routing rules; the highest score is not automatically the best question.",
        "- Keep examples outside the score-bearing question (for example, in expandable help or the conversational agent's optional explanation). This makes the main prompt short without hiding unfamiliar terms.",
        "",
        "Regenerate the CSV and this report with:",
        "",
        "```bash",
        ".venv/bin/python scripts/audit_my_info_readability.py",
        "```",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_audit()
    write_csv(rows)
    write_report(rows)


if __name__ == "__main__":
    main()
