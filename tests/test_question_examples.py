from __future__ import annotations

import csv
from pathlib import Path
import unittest

from my_info.interactions import QUESTION_GROUPS
from my_info.question_examples import QUESTION_HELP, help_for_question


ROOT = Path(__file__).resolve().parents[1]


def _source_keys() -> set[str]:
    values: set[str] = set()
    for path in (ROOT / "spib_en_fr.csv", ROOT / "site/data/pib_table_en_fr_all.csv"):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            values.update(row["bank_number_key"] for row in csv.DictReader(handle))
    return values


class QuestionExamplesTests(unittest.TestCase):
    def test_every_question_has_bilingual_named_examples(self) -> None:
        question_codes = {question.code for question in QUESTION_GROUPS}
        self.assertEqual(set(QUESTION_HELP), question_codes)
        for question_code, help_text in QUESTION_HELP.items():
            self.assertIs(help_for_question(question_code), help_text)
            self.assertIn(help_text.familiarity, {"common", "mixed", "unfamiliar"})
            self.assertTrue(help_text.examples)
            for example in help_text.examples:
                self.assertTrue(example.institution_en.strip())
                self.assertTrue(example.institution_fr.strip())
                self.assertTrue(example.activity_en.strip())
                self.assertTrue(example.activity_fr.strip())

    def test_all_cited_pib_keys_exist_in_the_local_sources(self) -> None:
        source_keys = _source_keys()
        cited_keys = {
            key
            for help_text in QUESTION_HELP.values()
            for example in help_text.examples
            for key in example.pib_keys
        }
        self.assertTrue(cited_keys)
        self.assertLessEqual(cited_keys, source_keys)

    def test_uncited_examples_explain_the_source_gap(self) -> None:
        uncited = [
            example
            for help_text in QUESTION_HELP.values()
            for example in help_text.examples
            if not example.pib_keys
        ]
        self.assertTrue(uncited)
        for example in uncited:
            self.assertTrue(example.evidence_note_en.strip())
            self.assertTrue(example.evidence_note_fr.strip())

    def test_split_recommendations_are_bilingual(self) -> None:
        for help_text in QUESTION_HELP.values():
            self.assertEqual(
                bool(help_text.split_recommendation_en),
                bool(help_text.split_recommendation_fr),
            )


if __name__ == "__main__":
    unittest.main()
