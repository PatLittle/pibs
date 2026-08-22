import unittest

from my_info.categories import classify_record, classify_records, load_category_definitions
from my_info.model import load_pib_records


class CategoryDefinitionTests(unittest.TestCase):
    def test_loads_exact_official_id_set(self):
        definitions = load_category_definitions()
        self.assertEqual(25, len(definitions))
        self.assertEqual("Biographical information", definitions["PI_CAT-1"].name_en)
        self.assertEqual("Numéro d’assurance sociale (NAS)", definitions["PI_CAT-25"].name_fr)


class CategoryClassifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {record.record_id: record for record in load_pib_records()}

    def test_assigns_multiple_categories_with_source_evidence(self):
        result = classify_record(self.records["standard:PSU 931"])
        self.assertTrue({"PI_CAT-3", "PI_CAT-10", "PI_CAT-13", "PI_CAT-17", "PI_CAT-24", "PI_CAT-25"}.issubset(result.category_ids))
        financial = next(item for item in result.assignments if item.category_id == "PI_CAT-13")
        self.assertEqual(1.0, financial.confidence)
        self.assertTrue(any(item.field == "description_en" for item in financial.evidence))
        self.assertTrue(any("financial information" in item.matched_text.lower() for item in financial.evidence))

    def test_uses_french_evidence_when_english_is_absent(self):
        result = classify_record(
            {
                "record_id": "test:french",
                "description_fr": "Les renseignements personnels peuvent inclure le nom, les coordonnées, la date de naissance et la signature.",
            }
        )
        self.assertEqual(("PI_CAT-3", "PI_CAT-8", "PI_CAT-17", "PI_CAT-24"), result.category_ids)
        self.assertTrue(all(any(e.language == "fr" for e in assignment.evidence) for assignment in result.assignments))

    def test_does_not_infer_name_from_program_or_institution_metadata(self):
        result = classify_record(
            {
                "record_id": "test:no-name-category",
                "institution_name_en": "Department with Name in its title",
                "title_en": "Program name register",
                "description_en": "This bank supports operation of the program.",
            }
        )
        self.assertNotIn("PI_CAT-17", result.category_ids)
        self.assertTrue(result.unclassified)

    def test_flags_education_as_unmapped_instead_of_guessing(self):
        result = classify_record(
            {
                "record_id": "test:education",
                "description_en": "Personal information may include educational information and education records.",
            }
        )
        self.assertTrue(result.ambiguous)
        self.assertTrue(result.unclassified)
        self.assertEqual({"education"}, {item.concept for item in result.unmapped_evidence})
        self.assertNotIn("PI_CAT-1", result.category_ids)

    def test_credit_information_is_retained_but_flagged_as_overloaded(self):
        result = classify_record(
            {
                "record_id": "test:credit",
                "description_en": "Personal information may include credit information.",
            }
        )
        self.assertEqual(("PI_CAT-6",), result.category_ids)
        self.assertEqual(0.79, result.assignments[0].confidence)
        self.assertTrue(result.ambiguous)

    def test_classifies_entire_current_corpus_without_duplicate_results(self):
        records = list(self.records.values())
        results = classify_records(records)
        self.assertEqual(1028, len(results))
        self.assertEqual(1028, len({result.record_id for result in results}))
        self.assertTrue(all(len(result.category_ids) == len(set(result.category_ids)) for result in results))


if __name__ == "__main__":
    unittest.main()
