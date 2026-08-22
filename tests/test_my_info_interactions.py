import csv
from pathlib import Path
import unittest

from my_info.interactions import (
    coverage_report,
    derive_interaction_features,
    derive_many,
    questionnaire_questions,
)


ROOT = Path(__file__).resolve().parents[1]


def _codes(result, field):
    return {item["code"] for item in result[field]}


def _csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class InteractionFeatureTests(unittest.TestCase):
    def test_standard_access_request_maps_to_grouped_question_with_evidence(self):
        row = next(
            row for row in _csv_rows(ROOT / "spib_en_fr.csv")
            if row["bank_number_key"] == "PSU 901"
        )
        result = derive_interaction_features(row)
        self.assertEqual(result["source_kind"], "standard_pib")
        self.assertIn("access_privacy", _codes(result, "interaction_topics"))
        self.assertIn("requested_information_privacy", _codes(result, "service_actions"))
        self.assertIn("q_access_privacy", _codes(result, "question_triggers"))
        match = next(item for item in result["interaction_topics"] if item["code"] == "access_privacy")
        self.assertGreaterEqual(match["confidence"], 0.9)
        self.assertTrue(any(item["field"] == "title_en" for item in match["evidence"]))
        self.assertTrue(all(item["excerpt"] for item in match["evidence"]))

    def test_employee_and_third_party_roles_create_caveat(self):
        row = {
            "bank_number_key": "TEST PPU 001",
            "title_en": "Employee emergency contacts",
            "class_of_individuals_en": "Current and former federal employees, their spouses, dependants, and emergency contacts.",
            "purpose_en": "Used for workplace emergency and business continuity planning.",
        }
        result = derive_interaction_features(row)
        self.assertLessEqual(
            {"government_employee", "family_dependent"},
            _codes(result, "individual_roles"),
        )
        self.assertIn("q_government_work", _codes(result, "question_triggers"))
        self.assertEqual(result["derivation"]["holding_inference"], "candidate_only")
        self.assertIn("possible_third_party_information", _codes(result, "privacy_caveats"))

    def test_one_answer_can_trigger_multiple_related_pibs(self):
        rows = [
            {"bank_number_key": "A PPU 1", "title_en": "Student financial assistance applications", "class_of_individuals_en": "Students and program applicants."},
            {"bank_number_key": "B PPU 2", "title_en": "Student loan payments", "description_en": "Financial assistance and benefit payments to students."},
        ]
        results = derive_many(rows)
        for result in results:
            self.assertIn("q_money_programs", _codes(result, "question_triggers"))
        self.assertNotEqual(results[0]["record_key"], results[1]["record_key"])
        self.assertLess(len(questionnaire_questions()), 25)

    def test_personal_information_contents_do_not_create_primary_questions(self):
        row = {
            "bank_number_key": "TEST PSE 001",
            "title_en": "Employee personnel record",
            "class_of_individuals_en": "Employees, their spouses and emergency contacts.",
            "description_en": "May include passport, medical, citizenship and tax information.",
            "purpose_en": "Used to administer employment.",
        }
        result = derive_interaction_features(row)
        self.assertIn("q_government_work", _codes(result, "primary_question_triggers"))
        self.assertNotIn("q_travel_border", _codes(result, "primary_question_triggers"))
        self.assertNotIn("q_health_disability", _codes(result, "primary_question_triggers"))
        self.assertNotIn("q_family_vital", _codes(result, "primary_question_triggers"))

    def test_institution_schema_and_french_text_are_supported(self):
        row = {
            "institution_id": "example",
            "bank_number_key": "EX PPU 9",
            "title_fr": "Demandes de citoyenneté",
            "class_of_individuals_fr": "Réfugiés et résidents permanents.",
            "purpose_fr": "Traiter les demandes de citoyenneté.",
        }
        result = derive_interaction_features(row)
        self.assertEqual(result["source_kind"], "institution_pib")
        self.assertIn("immigration_citizenship", _codes(result, "interaction_topics"))
        self.assertIn("immigrant_refugee_newcomer", _codes(result, "individual_roles"))
        self.assertIn("q_immigration", _codes(result, "question_triggers"))
        immigration = next(item for item in result["interaction_topics"] if item["code"] == "immigration_citizenship")
        self.assertTrue(any(item["field"].endswith("_fr") for item in immigration["evidence"]))

    def test_sensitive_and_broad_population_are_explicit_caveats(self):
        row = {
            "bank_number_key": "EX PPU 10",
            "title_en": "Medical services",
            "class_of_individuals_en": "Members of the general public and patients.",
            "description_en": "May include a medical diagnosis and Social Insurance Number.",
        }
        result = derive_interaction_features(row)
        self.assertLessEqual(
            {"broad_population", "sensitive_context"},
            _codes(result, "privacy_caveats"),
        )

    def test_coverage_report_accounts_for_every_source_row(self):
        standard = _csv_rows(ROOT / "spib_en_fr.csv")
        institution = _csv_rows(ROOT / "site" / "data" / "pib_table_en_fr_all.csv")
        features = derive_many(standard, source_kind="standard_pib") + derive_many(
            institution, source_kind="institution_pib"
        )
        report = coverage_report(features)
        self.assertEqual(report["record_count"], len(standard) + len(institution))
        self.assertEqual(
            report["matched_question_count"] + len(report["unmatched_record_keys"]),
            report["record_count"],
        )
        self.assertGreaterEqual(report["matched_question_rate"], 0.75)


if __name__ == "__main__":
    unittest.main()
