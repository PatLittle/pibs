import csv
import json
import tempfile
import unittest
from pathlib import Path

from build_cor_table_from_markdown import merge_records as merge_cor_records
from build_cor_table_from_markdown import parse_records as parse_cor_records
from build_cor_table_from_markdown import process_files as process_cor_files
from build_pib_table_from_markdown import parse_records as parse_pib_records
from build_pib_table_from_markdown import process_files as process_pib_files
from collect_institution_content import same_site_namespace
from compile_institution_tables import build_pib_cor_links


class ClassOfRecordsExtractorTests(unittest.TestCase):
    def test_bilingual_prose_records_pair_by_numeric_suffix(self):
        english = """
### Accessible Transportation
**Description:** Records about accessible transportation.
**Document Types:** Correspondence, policies and decisions.
**Record Number:** CTA DRB 001
"""
        french = """
### Transports accessibles
**Description :** Documents sur les transports accessibles.
**Types de documents :** Correspondance, politiques et décisions.
**Numéro de dossier :** OTC RDD 001
"""
        rows = merge_cor_records(parse_cor_records(english), parse_cor_records(french))
        self.assertEqual(rows, [{
            "record_number": "CTA DRB 001",
            "name_en": "Accessible Transportation",
            "name_fr": "Transports accessibles",
            "document_types_en": "Correspondence, policies and decisions.",
            "document_types_fr": "Correspondance, politiques et décisions.",
        }])

    def test_plain_pdf_text_and_wrapped_document_types(self):
        markdown = """
The quasi-judicial review of certain ministerial conclusions
Description: This class contains review records.
Document Types: Applications, Authorizations, Briefing Notes, Decisions and
Reasons, Determinations, Legal Opinions, Policies, Research.
Record Number: ICO 001
"""
        rows = parse_cor_records(markdown)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "The quasi-judicial review of certain ministerial conclusions")
        self.assertIn("Reasons, Determinations", rows[0]["document_types"])

    def test_header_only_cor_table_is_always_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            en = root / "en.md"
            fr = root / "fr.md"
            out = root / "cor_table_en_fr.csv"
            en.write_text("No institution-specific classes.", encoding="utf-8")
            fr.write_text("Aucune catégorie propre à l'institution.", encoding="utf-8")
            self.assertEqual(process_cor_files(en, fr, out), (0, 0, 0))
            with out.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(next(csv.reader(handle)), [
                    "record_number", "name_en", "name_fr",
                    "document_types_en", "document_types_fr",
                ])


class PibExtractorTests(unittest.TestCase):
    def test_plain_titles_and_duplicate_bank_numbers_collapse(self):
        markdown = """
Program context
**Description:** A class-of-record description.
Exposure Device Operator
**Description:** Personal information about certified operators.
**Class of Individuals:** Certified operators.
**Purpose:** Certification.
**Bank Number:** CNSC PPU 060

Another program context
**Description:** Another class description.
Exposure Device Operator
**Description:** Personal information about certified operators.
**Class of Individuals:** Certified operators.
**Purpose:** Certification.
**Bank Number:** CNSC PPU 060
"""
        rows = parse_pib_records(markdown)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Exposure Device Operator")
        self.assertEqual(rows[0]["bank_number"], "CNSC PPU 060")

    def test_translated_organization_acronyms_share_local_bank_identity(self):
        markdown = """
### English duplicate
**Description:** English content.
**Bank Number:** ESDC PPU 050

### French record
**Description:** Contenu français plus complet.
**Bank Number:** EDSC PPU 050
"""
        rows = parse_pib_records(markdown)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["bank_number"], "EDSC PPU 050")

    def test_class_file_numbers_are_not_personal_information_banks(self):
        markdown = """
### Commercial activities
**Description:** Records about tariffs.
**Document types:** Reports and correspondence.
**File number:** SAG COM 005
"""
        self.assertEqual(parse_pib_records(markdown), [])

    def test_duplicate_occurrences_fill_missing_title_from_short_entry(self):
        markdown = """
Accidents and Compensation
- Bank Number: MPA PPU 005

Description: Full description.
Purpose: Claims administration.
Bank Number: MPA PPU 005
"""
        rows = parse_pib_records(markdown)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Accidents and Compensation")
        self.assertEqual(rows[0]["description"], "Full description.")

    def test_header_only_pib_table_is_always_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            en = root / "en.md"
            fr = root / "fr.md"
            out = root / "pib_table_en_fr.csv"
            en.write_text("No institution-specific PIBs.", encoding="utf-8")
            fr.write_text("Aucun FRP propre à l'institution.", encoding="utf-8")
            status, en_count, fr_count, merged = process_pib_files(en, fr, out)
            self.assertEqual((status, en_count, fr_count, merged), ("processed", 0, 0, 0))
            self.assertTrue(out.exists())


class LinkageModelTests(unittest.TestCase):
    def test_institution_specific_related_record_resolves(self):
        pibs = [{
            "institution_id": "inst-1",
            "bank_number_key": "ABC PPU 001",
            "related_record_number_en": "See ABC OPS 100 and PRN 930.",
            "related_record_number_fr": "Voir ABC OPS 100 et NDP 930.",
        }]
        classes = [{"institution_id": "inst-1", "record_number": "ABC OPS 100"}]
        links = build_pib_cor_links(pibs, classes)
        institutional = [row for row in links if row["relationship_scope"] == "institution_specific"]
        self.assertEqual(len(institutional), 2)
        self.assertTrue(all(row["resolved"] == "true" for row in institutional))
        standard = [row for row in links if row["relationship_scope"] == "standard"]
        self.assertEqual({row["cor_record_number"] for row in standard}, {"930"})

    def test_canada_ca_discovery_stays_in_institution_language_namespace(self):
        initial = (
            "https://www.canada.ca/en/immigration-refugees-citizenship/"
            "corporate/transparency/info-source.html"
        )
        self.assertTrue(same_site_namespace(
            initial,
            "https://www.canada.ca/en/immigration-refugees-citizenship/"
            "corporate/transparency/pibs.html",
        ))
        self.assertFalse(same_site_namespace(
            initial,
            "https://www.canada.ca/en/employment-social-development/"
            "corporate/transparency/pibs.html",
        ))
        self.assertFalse(same_site_namespace(
            initial,
            "https://www.canada.ca/fr/immigration-refugies-citoyennete/"
            "organisation/transparence/frp.html",
        ))

    def test_collection_job_manifest_is_complete_and_stable(self):
        path = Path("data/collection_jobs/institution_collection_jobs_2026-08-15.jsonl")
        jobs = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(jobs), 148)
        self.assertEqual(sum(bool(job["collectable"]) for job in jobs), 131)
        self.assertEqual(len({job["institution_id"] for job in jobs}), 148)
        self.assertTrue(all(job["content_folder"].endswith(job["institution_id"]) for job in jobs))


if __name__ == "__main__":
    unittest.main()
