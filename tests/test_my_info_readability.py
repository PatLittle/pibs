import unittest

from my_info.interactions import questionnaire_questions
from my_info.readability import (
    audit_questions,
    count_syllables,
    flesch_reading_ease,
    reading_band,
)


class ReadabilityTests(unittest.TestCase):
    def test_known_simple_sentence_uses_exact_formula_counts(self):
        result = flesch_reading_ease("The cat sat on the mat.")
        self.assertEqual(result.sentences, 1)
        self.assertEqual(result.words, 6)
        self.assertEqual(result.syllables, 6)
        self.assertEqual(result.score, 116.1)
        self.assertEqual(result.band, "very easy")
        self.assertFalse(result.is_outlier)

    def test_hyphenated_token_sums_its_parts(self):
        self.assertEqual(count_syllables("home-buying"), 3)
        self.assertEqual(count_syllables("access-to-information"), 7)

    def test_empty_text_is_rejected(self):
        with self.assertRaises(ValueError):
            flesch_reading_ease(" -- ")

    def test_band_boundaries_and_configurable_outlier_threshold(self):
        self.assertEqual(reading_band(60), "standard")
        self.assertEqual(reading_band(59.9), "fairly difficult")
        result = flesch_reading_ease(
            "Have you used this service?", outlier_below=100
        )
        self.assertTrue(result.is_outlier)

    def test_every_current_english_question_can_be_audited(self):
        questions = questionnaire_questions()
        audit = audit_questions(questions)
        self.assertEqual(len(audit), len(questions))
        self.assertEqual(
            {row["code"] for row in audit},
            {row["code"] for row in questions},
        )
        self.assertTrue(all(isinstance(row["score"], float) for row in audit))

    def test_rewrite_comparison_is_reported(self):
        audit = audit_questions(
            [{"code": "q_test", "question_en": "Have you used it?"}],
            proposed_wording={"q_test": "Did you use it?"},
        )
        self.assertEqual(audit[0]["proposed_question_en"], "Did you use it?")
        self.assertIn("score_change", audit[0])


if __name__ == "__main__":
    unittest.main()
