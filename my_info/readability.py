"""Reproducible English readability measures for My Info survey copy.

The Flesch Reading Ease formula is defined for English prose.  Scores from
this module must not be used to judge the French questionnaire; French copy
needs a French-language measure and review by a fluent plain-language editor.

The implementation intentionally has no third-party dependency.  Its syllable
counter is a documented heuristic, so scores are suitable for comparative
screening rather than a linguistic certification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable, Mapping


WORD_RE = re.compile(r"[A-Za-z]+(?:[\-'’][A-Za-z]+)*")
SENTENCE_RE = re.compile(r"[.!?]+")
# Treat ``y`` as a vowel only when it is not beside a conventional vowel.
# This keeps ``happy`` at two groups while avoiding one merged group for
# words such as ``buying``.
VOWEL_GROUP_RE = re.compile(r"[aeiou]+|(?<![aeiou])y+(?![aeiou])")


# Candidate copy for content-design and usability review.  These strings are
# deliberately exported with the audit and questionnaire contract without
# silently replacing the bilingual production prompts.  Compound questions
# still need the adaptive splits described in QUESTION_HELP.
PROPOSED_QUESTION_WORDING_EN = {
    "q_government_work": "Have you applied for a federal job or worked for one?",
    "q_money_programs": "Did a federal program give you money or other help?",
    "q_tax_customs": "Did you ever file federal taxes or declare goods at the border?",
    "q_immigration": "Have you applied to move to Canada, stay here or become a citizen?",
    "q_travel_border": "Have you applied for a passport, crossed the border or used NEXUS?",
    "q_health_disability": "Did a federal health program give you care or support?",
    "q_indigenous_services": "Have you used a federal service for First Nations, Inuit or Métis people?",
    "q_military_veterans": "Have you served in the Armed Forces or received help as a veteran?",
    "q_education_training": "Has the Government of Canada helped pay for your school or job training?",
    "q_justice_safety": "Did you have a security check or deal with a federal law officer, prison or parole?",
    "q_complaint_appeal": "Did you file a complaint or ask a federal office to review a choice it made?",
    "q_access_privacy": "Have you asked a federal office for records about you or to fix your records?",
    "q_business_supplier": "Did you run a business, get a federal permit or sell goods or services to the government?",
    "q_firearms": "Have you had a firearms licence or registered a gun?",
    "q_boating": "Have you had a boating card or registered a boat with Transport Canada?",
    "q_housing_property": "Have you used a federal program to rent or buy a home?",
    "q_civic_contact": "Did you contact a federal office, share your views, sign a petition or vote?",
    "q_culture_volunteer": "Have you joined or helped with a federal arts, sports, heritage or parks event?",
    "q_emergency": "Did you ask for federal help in a crisis or after a disaster?",
    "q_family_vital": "Did you use a federal service for a birth, wedding, divorce, adoption or death?",
}


@dataclass(frozen=True)
class ReadabilityResult:
    """The counts and Flesch result for one English text string."""

    score: float
    band: str
    is_outlier: bool
    sentences: int
    words: int
    syllables: int


def _syllables_in_part(part: str) -> int:
    """Estimate syllables in one alphabetic word part.

    The heuristic counts contiguous vowel groups, removes a likely silent
    terminal ``e`` (except consonant + ``le``), and always returns at least one
    syllable for a non-empty alphabetic part.  The caller splits hyphenated and
    apostrophized tokens and sums the parts.
    """

    word = re.sub(r"[^a-z]", "", part.casefold())
    if not word:
        return 0
    count = len(VOWEL_GROUP_RE.findall(word))
    if word.endswith("e") and not (
        word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy"
    ):
        count -= 1
    return max(1, count)


def count_syllables(token: str) -> int:
    """Estimate syllables in a token, including all hyphenated parts."""

    parts = re.findall(r"[A-Za-z]+", token)
    return sum(_syllables_in_part(part) for part in parts)


def reading_band(score: float) -> str:
    """Return the conventional Flesch Reading Ease interpretation band."""

    if score >= 90:
        return "very easy"
    if score >= 80:
        return "easy"
    if score >= 70:
        return "fairly easy"
    if score >= 60:
        return "standard"
    if score >= 50:
        return "fairly difficult"
    if score >= 30:
        return "difficult"
    return "very difficult"


def flesch_reading_ease(text: str, *, outlier_below: float = 60.0) -> ReadabilityResult:
    """Calculate an English Flesch Reading Ease score.

    Formula: ``206.835 - 1.015(words / sentences) -
    84.6(syllables / words)``.  A question below ``outlier_below`` is marked as
    an outlier for plain-language review.  Sentence count is the number of
    punctuation runs ending in ``.``, ``!`` or ``?``; non-empty text without
    one is treated as one sentence.
    """

    words = WORD_RE.findall(text)
    if not words:
        raise ValueError("text must contain at least one English word")
    sentence_count = len(SENTENCE_RE.findall(text)) or 1
    syllable_count = sum(count_syllables(word) for word in words)
    score = 206.835 - 1.015 * (len(words) / sentence_count) - 84.6 * (
        syllable_count / len(words)
    )
    rounded = round(score, 1)
    return ReadabilityResult(
        score=rounded,
        band=reading_band(rounded),
        is_outlier=rounded < outlier_below,
        sentences=sentence_count,
        words=len(words),
        syllables=syllable_count,
    )


def audit_questions(
    questions: Iterable[Mapping[str, str]],
    *,
    proposed_wording: Mapping[str, str] | None = None,
    outlier_below: float = 60.0,
) -> list[dict[str, object]]:
    """Score question mappings and, when supplied, their proposed rewrites."""

    rewrites = proposed_wording or {}
    results: list[dict[str, object]] = []
    for question in questions:
        code = question["code"]
        original = question["question_en"]
        original_result = flesch_reading_ease(original, outlier_below=outlier_below)
        row: dict[str, object] = {
            "code": code,
            "question_en": original,
            **asdict(original_result),
        }
        rewrite = rewrites.get(code)
        if rewrite:
            rewrite_result = flesch_reading_ease(rewrite, outlier_below=outlier_below)
            row.update({
                "proposed_question_en": rewrite,
                "proposed_score": rewrite_result.score,
                "proposed_band": rewrite_result.band,
                "score_change": round(rewrite_result.score - original_result.score, 1),
            })
        results.append(row)
    return results
