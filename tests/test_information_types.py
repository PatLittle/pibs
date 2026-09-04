import json
import unittest

from compile_institution_tables import add_specific_information_types
from extract_information_types import extract_specific_information_types


class SpecificInformationTypeTests(unittest.TestCase):
    def test_internal_audit_list_excludes_generic_catch_all(self):
        description = (
            "This bank describes personal information related to a government institution's "
            "internal audit program. Personal information may include name, contact information, "
            "signature, employee identification number, financial information, gender, and other "
            "personal information in relevant records held by the institution."
        )
        self.assertEqual(extract_specific_information_types(description, "en"), [
            "name",
            "contact information",
            "signature",
            "employee identification number",
            "financial information",
            "gender",
        ])

    def test_occupational_health_list_preserves_compound_dates(self):
        description = (
            "This bank contains information about safe workplaces. Personal information may "
            "include: name, contact information, biographical information, biometric information, "
            "citizenship status, criminal checks/history, date and place of birth, date and place "
            "of death, educational information, employee identification number, employment equity "
            "information, employee personnel information, medical information, other identification "
            "numbers, physical attributes, signature and autopsy reports."
        )
        self.assertEqual(extract_specific_information_types(description, "en"), [
            "name", "contact information", "biographical information", "biometric information",
            "citizenship status", "criminal checks/history", "date and place of birth",
            "date and place of death", "educational information", "employee identification number",
            "employment equity information", "employee personnel information", "medical information",
            "other identification numbers", "physical attributes", "signature", "autopsy reports",
        ])

    def test_french_semicolon_list_retains_source_language(self):
        description = (
            "Les renseignements personnels peuvent comprendre : le nom; les coordonnées; "
            "des renseignements biographiques et biométriques; la date et le lieu de naissance; "
            "la signature; des rapports d’autopsie."
        )
        self.assertEqual(extract_specific_information_types(description, "fr"), [
            "nom", "coordonnées", "renseignements biographiques", "biométriques",
            "date et lieu de naissance", "signature", "rapports d’autopsie",
        ])

    def test_generic_description_without_explicit_list_is_not_extracted(self):
        description = "The program collects and analyzes workplace information for compliance."
        self.assertEqual(extract_specific_information_types(description, "en"), [])

    def test_compiler_serializes_language_arrays_as_json(self):
        row = add_specific_information_types({
            "description_en": "Personal information may include name and contact information.",
            "description_fr": "Les renseignements personnels incluent le nom et les coordonnées.",
        })
        self.assertEqual(json.loads(row["specific_information_types_en"]), [
            "name", "contact information",
        ])
        self.assertEqual(json.loads(row["specific_information_types_fr"]), [
            "nom", "coordonnées",
        ])


if __name__ == "__main__":
    unittest.main()
