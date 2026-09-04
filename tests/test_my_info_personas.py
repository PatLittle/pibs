from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from my_info.agent_tools import SurveyToolEngine
from scripts.evaluate_my_info_personas import (
    evaluate_fixture,
    render_markdown,
    write_report,
)


class MyInfoPersonaEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = SurveyToolEngine()

    @staticmethod
    def fixture() -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "contract_version": "2026-09-04.4",
            "assessment_year": 2026,
            "include_possible": False,
            "personas": [{
                "persona_id": "minimal-boater",
                "name": "Minimal Boater",
                "narrative": "This prose is display metadata and is not sent to the engine.",
                "survey": {
                    "locale": "en-CA",
                    "answers": {
                        "q_boating": {"value": "yes"},
                        "q_tax_customs": {"value": "yes"},
                    },
                    "refinements": {
                        "q_boating": {
                            "selected_options": ["pleasure_craft_operator_card"],
                            "timings": {
                                "pleasure_craft_operator_card": {"kind": "within_1_year"}
                            },
                        },
                        "q_tax_customs": {
                            "selected_options": ["federal_tax_return"],
                            "timings": {
                                "federal_tax_return": {"kind": "within_1_year"}
                            },
                        },
                    },
                },
                "expectations": {
                    "expected_bank_numbers": ["TC PPU 023"],
                    "expected_inventory_gaps": ["federal_tax_return"],
                },
            }],
        }

    def test_evaluates_controlled_state_and_collects_paginated_results(self) -> None:
        report = evaluate_fixture(self.fixture(), engine=self.engine, page_size=1)
        persona = report["personas"][0]
        metrics = persona["metrics"]

        self.assertEqual(metrics["result_count"], len(persona["results"]))
        self.assertGreater(metrics["result_count"], 0)
        self.assertFalse(persona["summary"]["truncated"])
        self.assertEqual(
            {"direct": 1, "inventory_gap": 1},
            metrics["selected_routes"]["coverage_counts"],
        )
        self.assertEqual(1, metrics["inventory_gap_count"])
        self.assertEqual(
            ["TC PPU 023"],
            metrics["expectations"]["expected_bank_numbers"]["found"],
        )
        self.assertEqual(0, metrics["expectations"]["failed_assertion_count"])
        self.assertEqual(19, metrics["unanswered_question_count"])

    def test_output_is_deterministic_and_markdown_is_concise(self) -> None:
        first = evaluate_fixture(self.fixture(), engine=self.engine, page_size=2)
        second = evaluate_fixture(self.fixture(), engine=self.engine, page_size=2)
        self.assertEqual(first, second)
        markdown = render_markdown(first)
        self.assertIn("# My Info persona evaluation", markdown)
        self.assertIn("Minimal Boater", markdown)
        self.assertIn("`inventory_gap`", markdown)

        with tempfile.TemporaryDirectory() as temporary:
            json_path, markdown_path = write_report(first, Path(temporary))
            self.assertEqual(first, json.loads(json_path.read_text(encoding="utf-8")))
            self.assertEqual(markdown, markdown_path.read_text(encoding="utf-8"))

    def test_free_text_in_controlled_answer_is_rejected(self) -> None:
        fixture = self.fixture()
        fixture["personas"][0]["survey"]["answers"] = [{
            "question_code": "q_boating",
            "value": "yes",
            "details": "a narrative accident description",
        }]
        fixture["personas"][0]["survey"]["refinements"] = []
        with self.assertRaisesRegex(ValueError, "Unsupported answer-update fields"):
            evaluate_fixture(fixture, engine=self.engine)

    def test_expectations_do_not_treat_all_unlisted_results_as_false_positives(self) -> None:
        report = evaluate_fixture(self.fixture(), engine=self.engine)
        expectations = report["personas"][0]["metrics"]["expectations"]
        self.assertEqual([], expectations["allowlist_exceptions"]["record_ids"])
        self.assertEqual([], expectations["allowlist_exceptions"]["bank_numbers"])

    def test_record_id_format_issue_is_not_counted_as_a_coverage_gap(self) -> None:
        fixture = self.fixture()
        fixture["personas"][0]["expectations"]["expected_record_ids"] = [
            "standard:TC PPU 023"
        ]
        report = evaluate_fixture(fixture, engine=self.engine)
        expectations = report["personas"][0]["metrics"]["expectations"]
        self.assertEqual([], expectations["expected_record_ids"]["missing"])
        self.assertEqual(1, expectations["fixture_format_issue_count"])
        self.assertEqual(0, expectations["failed_assertion_count"])
        mismatch = expectations["expected_record_ids"]["format_mismatches"][0]
        self.assertEqual("TC PPU 023", mismatch["bank_number"])
        self.assertTrue(mismatch["actual_record_ids"][0].startswith("institution:"))

    def test_fallback_parent_results_are_identified_despite_strong_band(self) -> None:
        fixture = {
            "contract_version": self.engine.contract["content_version"],
            "assessment_year": 2026,
            "personas": [{
                "id": "fallback-housing",
                "display_name": "Fallback Housing",
                "survey": {
                    "answers": [{"question_code": "q_housing_property", "value": "yes"}],
                    "refinements": [{
                        "question_code": "q_housing_property",
                        "selected_options": ["other_federal_housing"],
                        "timings": {"other_federal_housing": {"kind": "within_1_year"}},
                    }],
                },
            }],
        }
        report = evaluate_fixture(fixture, engine=self.engine)
        persona = report["personas"][0]
        attribution = persona["metrics"]["selected_routes"]["result_attribution"]
        self.assertGreater(attribution["fallback_only_result_count"], 0)
        self.assertEqual(
            {"strong_match"},
            {item["match_band"] for item in persona["results"]},
        )
        self.assertEqual("fallbacks_flatten_to_strong", report["ranked_findings"][0]["code"])

    def test_stale_fixture_contract_is_rejected(self) -> None:
        fixture = self.fixture()
        fixture["contract_version"] = "stale-contract"
        with self.assertRaisesRegex(ValueError, "contract_version does not match"):
            evaluate_fixture(fixture, engine=self.engine)


if __name__ == "__main__":
    unittest.main()
