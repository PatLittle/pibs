import tempfile
import unittest
import json
from pathlib import Path

from build_my_info_features import derive_outputs, write_outputs
from my_info.model import PibRecord


def sample_record() -> PibRecord:
    return PibRecord(
        record_id="institution:test:ABC PPU 001",
        scope="institution",
        institution_id="test",
        gc_org_id="1",
        institution_name_en="Test Department",
        institution_name_fr="Ministère test",
        bank_number_key="ABC PPU 001",
        pib_type="Public Bank",
        title_en="Benefit applications",
        title_fr="Demandes de prestations",
        description_en="Personal information may include name, contact information and Social Insurance Number.",
        description_fr="Les renseignements personnels peuvent comprendre le nom, les coordonnées et le numéro d’assurance sociale.",
        class_of_individuals_en="Benefit applicants.",
        class_of_individuals_fr="Demandeurs de prestations.",
        note_en="",
        note_fr="",
        purpose_en="Used to process benefit applications and payments.",
        purpose_fr="Utilisés pour traiter les demandes de prestations et les paiements.",
        consistent_uses_en="",
        consistent_uses_fr="",
        retention_en="Records are retained for two years after the last administrative action and then destroyed.",
        retention_fr="Les dossiers sont conservés pendant deux ans après la dernière mesure administrative, puis détruits.",
        source_url_en="",
        source_url_fr="",
    )


class MyInfoBuilderTests(unittest.TestCase):
    def test_derives_joinable_compact_and_evidence_rows(self):
        features, categories, evidence = derive_outputs([sample_record()])
        self.assertEqual("institution:test:ABC PPU 001", features[0]["record_id"])
        self.assertIn("PI_CAT-17", features[0]["category_ids"])
        self.assertEqual("fixed_period", features[0]["retention_rule_type"])
        self.assertTrue(features[0]["question_codes"])
        self.assertEqual(features[0]["record_id"], categories[0]["record_id"])
        self.assertEqual(features[0]["record_id"], evidence[0]["record"]["record_id"])

    def test_writes_all_artifact_types(self):
        features, categories, evidence = derive_outputs([sample_record()])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spib = root / "spib.csv"
            pib = root / "pib.csv"
            spib.write_text("x\n", encoding="utf-8")
            pib.write_text("x\n", encoding="utf-8")
            summary = write_outputs(
                root / "out", features, categories, evidence,
                spib_path=spib, pib_path=pib, generated_date="2026-08-22",
            )
            self.assertEqual(1, summary["record_count"])
            self.assertTrue((root / "out/my_info_pib_features.csv").exists())
            self.assertTrue((root / "out/my_info_pib_category_assignments.csv").exists())
            self.assertTrue((root / "out/my_info_derivation_evidence.jsonl").exists())
            self.assertTrue((root / "out/my_info_questionnaire.json").exists())
            self.assertTrue((root / "out/my_info_summary.json").exists())
            questionnaire = json.loads(
                (root / "out/my_info_questionnaire.json").read_text(encoding="utf-8")
            )
            first = questionnaire["questions"][0]
            self.assertIn("readability_en", first)
            self.assertTrue(first["help"]["examples"])


if __name__ == "__main__":
    unittest.main()
