import unittest

from my_info.retention import derive_retention, estimate_holding, parse_retention


class RetentionParsingTests(unittest.TestCase):
    def test_raw_text_is_preserved_and_contact_only_rule_has_no_bounds(self):
        raw = "For information about retention, please contact the institution's Access to Information and Privacy Coordinator."
        result = parse_retention(raw, "Veuillez communiquer avec le coordonnateur.")
        self.assertEqual(result.raw_text_en, raw)
        self.assertEqual(result.rule_type, "institution_defined")
        self.assertTrue(result.requires_institution_contact)
        self.assertIsNone(result.minimum_years)
        self.assertIsNone(result.maximum_years)

    def test_fixed_period_and_disposal_estimate(self):
        result = parse_retention(
            "Records are retained for 7 years from the date of receipt and then destroyed."
        )
        self.assertEqual(result.rule_type, "fixed_period")
        self.assertEqual((result.minimum_years, result.maximum_years), (7, 7))
        self.assertEqual(result.disposition, "destroy")
        estimate = estimate_holding(result, interaction_year=2016, as_of_year=2026)
        self.assertEqual(estimate.status, "likely_disposed")

    def test_last_administrative_action_requires_its_own_year(self):
        result = parse_retention(
            "Personal information is retained for a minimum of two (2) years after the last administrative action."
        )
        self.assertEqual(result.rule_type, "minimum_period")
        self.assertEqual(result.minimum_years, 2)
        self.assertIsNone(result.maximum_years)
        self.assertEqual(estimate_holding(result, 2018, 2026).status, "uncertain")
        self.assertEqual(estimate_holding(result, 2018, 2026, trigger_year=2025).status, "likely_held")

    def test_explicit_range_is_structured(self):
        result = parse_retention("Information is retained from 2 to 25 years and then destroyed.")
        self.assertEqual(result.rule_type, "bounded_range")
        self.assertEqual((result.minimum_years, result.maximum_years), (2, 25))
        self.assertEqual([period.qualifier for period in result.periods], ["minimum", "maximum"])

    def test_indefinite_branch_defeats_numeric_maximum(self):
        result = parse_retention(
            "Records are retained for up to 10 years, except cases of special interest which are retained indefinitely."
        )
        self.assertEqual(result.rule_type, "conditional_periods")
        self.assertTrue(result.has_indefinite_component)
        self.assertIsNone(result.maximum_years)
        self.assertEqual(estimate_holding(result, 2000, 2026).status, "uncertain")

    def test_age_is_a_trigger_not_a_retention_duration(self):
        result = parse_retention(
            "Records are retained until the former employee reaches 80 years of age and are then destroyed."
        )
        self.assertEqual(result.rule_type, "trigger_based")
        self.assertEqual(result.reference_events, ("individual_age",))
        self.assertTrue(result.periods[0].is_age)
        self.assertIsNone(result.maximum_years)

    def test_archival_transfer_counts_as_likely_held(self):
        result = parse_retention(
            "Records are retained for 30 years from the date of issuance and then transferred to Library and Archives Canada."
        )
        estimate = estimate_holding(result, 1980, 2026)
        self.assertEqual(estimate.status, "likely_held")
        self.assertIn("Library and Archives Canada", estimate.rationale)

    def test_french_fallback_parses_duration_and_disposition(self):
        result = parse_retention("", "Les dossiers sont conservés pendant cinq ans et ensuite détruits.")
        self.assertEqual(result.provenance, ("retention_fr:fallback",))
        self.assertEqual((result.minimum_years, result.maximum_years), (5, 5))
        self.assertEqual(result.disposition, "destroy")

    def test_bilingual_numeric_disagreement_lowers_confidence(self):
        result = parse_retention(
            "Records are retained for 5 years and then destroyed.",
            "Les dossiers sont conservés pendant six ans et ensuite détruits.",
        )
        self.assertEqual(result.language_agreement, "mismatch")
        self.assertEqual(result.confidence, "low")

    def test_blank_text_remains_unknown(self):
        result = parse_retention("", "")
        self.assertEqual(result.rule_type, "unknown")
        self.assertEqual(result.periods, ())
        self.assertEqual(estimate_holding(result, 2020, 2026).status, "uncertain")

    def test_derives_from_normalized_record_shape(self):
        class Record:
            retention_en = "Records are kept for two years and then destroyed."
            retention_fr = "Les dossiers sont conservés pendant deux ans et ensuite détruits."

        self.assertEqual(derive_retention(Record()).maximum_years, 2)


if __name__ == "__main__":
    unittest.main()
