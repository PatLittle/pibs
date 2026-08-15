import csv
import json
import unittest
from pathlib import Path

import pandas as pd

from build_institution_registry import parse_due_dates, parse_schedule_i


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/raw/institution-registry/2026-08-15"


class InstitutionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = pd.read_csv(ROOT / "institution_registry.csv")

    def test_schedule_i_is_complete_and_bilingual(self):
        schedule = parse_schedule_i((SNAPSHOT / "access_to_information_act.xml").read_bytes())
        self.assertEqual(len(schedule), 148)
        self.assertEqual(schedule["institution_id"].nunique(), 148)
        self.assertFalse(schedule[["legal_name_en", "legal_name_fr"]].isna().any().any())
        self.assertEqual(
            schedule["access_act_group"].value_counts().sort_index().to_dict(),
            {
                "Departments and Ministries of State": 22,
                "Other Government Institutions": 126,
            },
        )

    def test_bilingual_due_date_appendices_are_complete(self):
        expected_counts = {"03-31": 55, "06-30": 42, "09-30": 45, "12-31": 54}
        for lang in ("en", "fr"):
            due = parse_due_dates((SNAPSHOT / f"tbs_due_dates_{lang}.html").read_bytes(), lang)
            self.assertEqual(len(due), 196)
            self.assertEqual(due["annual_due_date"].value_counts().to_dict(), expected_counts)

    def test_registry_membership_and_due_dates(self):
        registry = self.registry
        self.assertEqual(len(registry), 148)
        self.assertEqual(registry["institution_id"].nunique(), 148)
        both = registry.dropna(subset=["due_en_annual_due_date", "due_fr_annual_due_date"])
        self.assertTrue((both["due_en_annual_due_date"] == both["due_fr_annual_due_date"]).all())
        self.assertEqual(registry["annual_due_date"].notna().sum(), 138)

    def test_known_name_collisions_do_not_cross_match(self):
        registry = self.registry.set_index("legal_name_en")
        for institution in ("Canada Water Agency", "Law Commission of Canada", "Saint John Port Authority"):
            row = registry.loc[institution]
            self.assertTrue(pd.isna(row["infosource_url_en"]))
            self.assertTrue(pd.isna(row["infosource_url_fr"]))

    def test_library_and_archives_uses_detailed_holdings_pages(self):
        row = self.registry.set_index("legal_name_en").loc["Library and Archives of Canada"]
        self.assertIn("institution-specific-personal-information-banks", row["pibs_url_en"])
        self.assertIn("categories-documents-renseignements-institution", row["pibs_url_fr"])
        self.assertEqual(row["pibs_url_en"], row["classes_of_records_url_en"])
        self.assertEqual(row["pibs_url_fr"], row["classes_of_records_url_fr"])

    def test_populated_publication_links_are_urls(self):
        for column in (
            "infosource_url_en", "infosource_url_fr", "pibs_url_en", "pibs_url_fr",
            "classes_of_records_url_en", "classes_of_records_url_fr",
        ):
            values = self.registry[column].dropna().astype(str)
            self.assertTrue(values.str.startswith(("http://", "https://")).all(), column)

    def test_deep_links_do_not_point_to_tbs_standard_catalogues(self):
        forbidden = (
            "standard-personal-information-banks",
            "fichiers-renseignements-personnels-ordinaires",
            "standard-classes-of-records",
            "standard-classes-records",
            "categories-documents-ordinaires",
        )
        for column in (
            "pibs_url_en", "pibs_url_fr",
            "classes_of_records_url_en", "classes_of_records_url_fr",
        ):
            values = self.registry[column].dropna().astype(str)
            self.assertFalse(values.str.contains("|".join(forbidden), regex=True).any(), column)

    def test_raw_manifest_has_all_sources(self):
        manifest = json.loads((SNAPSHOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), 8)
        self.assertEqual({item["filename"] for item in manifest}, {
            "access_to_information_act.xml",
            "tbs_due_dates_en.html", "tbs_due_dates_fr.html",
            "tbs_central_list_en.html", "tbs_central_list_fr.html",
            "open_canada_organization_list.json",
            "open_canada_org_info.json", "open_canada_org_names.json",
        })

    def test_override_file_has_exact_schema(self):
        path = ROOT / "data/institution_registry_overrides.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            self.assertIsNone(reader.restkey)
            self.assertTrue(all(None not in row for row in rows))
            self.assertTrue(all(set(row) == set(reader.fieldnames or []) for row in rows))


if __name__ == "__main__":
    unittest.main()
