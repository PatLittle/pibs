from __future__ import annotations

import json
from pathlib import Path
import unittest

from mcp.client import Client

from my_info.agent_tools import SurveyToolEngine
from my_info.mcp_server import mcp


ROOT = Path(__file__).resolve().parents[1]

VOICE_SESSION_ANSWERS = [
    {"question_code": "q_government_work", "value": "yes", "timing": {"kind": "current"}},
    {"question_code": "q_money_programs", "value": "yes", "timing": {"kind": "unknown"}},
    {"question_code": "q_tax_customs", "value": "yes", "timing": {"kind": "within_1_year"}},
    {"question_code": "q_immigration", "value": "no"},
    {"question_code": "q_travel_border", "value": "yes", "timing": {"kind": "1_to_3_years"}},
    {"question_code": "q_health_disability", "value": "no"},
    {"question_code": "q_indigenous_services", "value": "no"},
    {"question_code": "q_military_veterans", "value": "yes", "timing": {"kind": "current"}},
    {"question_code": "q_education_training", "value": "no"},
    {"question_code": "q_justice_safety", "value": "yes", "timing": {"kind": "within_1_year"}},
    {"question_code": "q_complaint_appeal", "value": "no"},
    {"question_code": "q_access_privacy", "value": "yes", "timing": {"kind": "approximate_year", "year": 2023}},
    {"question_code": "q_business_supplier", "value": "no"},
    {"question_code": "q_housing_property", "value": "no"},
    {"question_code": "q_civic_contact", "value": "yes", "timing": {"kind": "within_1_year"}},
    {"question_code": "q_culture_volunteer", "value": "no"},
    {"question_code": "q_research_survey", "value": "yes", "timing": {"kind": "4_to_7_years"}},
    {"question_code": "q_emergency", "value": "no"},
    {"question_code": "q_family_vital", "value": "no"},
]


class AgentToolEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = SurveyToolEngine()

    def test_manifest_and_initial_question_are_versioned(self) -> None:
        manifest = self.engine.get_manifest()
        self.assertEqual(4, len(manifest["tools"]))
        self.assertEqual(19, manifest["question_count"])
        self.assertEqual(1028, manifest["pib_count"])
        start = self.engine.advance()
        self.assertFalse(start["complete"])
        self.assertEqual("q_government_work", start["next_step"]["question_code"])
        self.assertEqual("plain_language_candidate_for_testing", start["next_step"]["wording_status"])

    def test_yes_answer_requires_timing_before_next_question(self) -> None:
        start = self.engine.advance()
        result = self.engine.advance(
            start["state"],
            [{"question_code": "q_government_work", "value": "yes"}],
        )
        self.assertEqual("timing", result["next_step"]["step_type"])
        self.assertEqual("q_government_work", result["next_step"]["question_code"])
        result = self.engine.advance(
            result["state"],
            [{
                "question_code": "q_government_work",
                "value": "yes",
                "timing": {"kind": "current"},
            }],
        )
        self.assertEqual("q_money_programs", result["next_step"]["question_code"])

    def test_voice_session_fixture_completes_and_produces_explainable_results(self) -> None:
        completed = self.engine.advance(answers=VOICE_SESSION_ANSWERS)
        self.assertTrue(completed["complete"])
        evaluation = self.engine.evaluate(
            completed["state"], as_of_year=2026, include_possible=False, max_results=500
        )
        self.assertGreater(evaluation["summary"]["total_matches"], 0)
        self.assertFalse(evaluation["summary"]["truncated"])
        self.assertEqual(
            {"strong_match"},
            {result["match_band"] for result in evaluation["results"]},
        )
        access = next(
            result
            for result in evaluation["results"]
            if result["record_id"] == "standard:PSU 901"
        )
        self.assertIn("q_access_privacy", access["matched_question_codes"])
        explanation = self.engine.explain_result(
            completed["state"], access["record_id"], as_of_year=2026
        )
        self.assertEqual("candidate_only", explanation["holding_inference"])
        self.assertTrue(explanation["question_triggers"])
        self.assertTrue(explanation["supporting_features"])

    def test_uncertain_is_not_treated_as_no(self) -> None:
        state = self.engine.advance(
            answers=[{"question_code": "q_access_privacy", "value": "not_sure"}]
        )["state"]
        evaluation = self.engine.evaluate(
            state, as_of_year=2026, include_possible=True, max_results=500
        )
        self.assertTrue(any(
            result["match_band"] == "review_if_relevant"
            and "q_access_privacy" in result["matched_question_codes"]
            for result in evaluation["results"]
        ))

    def test_state_rejects_free_text_and_unknown_fields(self) -> None:
        state = self.engine.create_state()
        state["case_details"] = "should never be stored"
        with self.assertRaisesRegex(ValueError, "Unsupported state fields"):
            self.engine.validate_state(state)
        with self.assertRaisesRegex(ValueError, "Unsupported answer-update fields"):
            self.engine.advance(
                answers=[{
                    "question_code": "q_government_work",
                    "value": "yes",
                    "details": "private narrative",
                }]
            )

    def test_answer_correction_replaces_prior_value(self) -> None:
        first = self.engine.advance(
            answers=[{
                "question_code": "q_government_work",
                "value": "yes",
                "timing": {"kind": "current"},
            }]
        )
        corrected = self.engine.advance(
            first["state"],
            [{"question_code": "q_government_work", "value": "no"}],
        )
        self.assertEqual("no", corrected["state"]["answers"]["q_government_work"]["value"])
        self.assertNotIn("timing", corrected["state"]["answers"]["q_government_work"])


class MCPAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_tools_are_structured_and_read_only(self) -> None:
        async with Client(mcp) as client:
            tools = (await client.list_tools()).tools
        self.assertEqual(
            {
                "my_info_get_manifest",
                "my_info_advance",
                "my_info_evaluate",
                "my_info_explain_result",
            },
            {tool.name for tool in tools},
        )
        for tool in tools:
            self.assertTrue(tool.annotations.read_only_hint)
            self.assertFalse(tool.annotations.destructive_hint)
            self.assertFalse(tool.annotations.open_world_hint)
            self.assertIsNotNone(tool.output_schema)

    async def test_manifest_tool_returns_structured_content(self) -> None:
        async with Client(mcp) as client:
            result = await client.call_tool("my_info_get_manifest", {})
        self.assertFalse(result.is_error)
        self.assertEqual("0.1.0", result.structured_content["tool_api_version"])

    async def test_advance_tool_round_trips_client_owned_state(self) -> None:
        async with Client(mcp) as client:
            started = await client.call_tool("my_info_advance", {})
            continued = await client.call_tool(
                "my_info_advance",
                {
                    "state": started.structured_content["state"],
                    "answers": [{
                        "question_code": "q_government_work",
                        "value": "yes",
                    }],
                },
            )
        self.assertFalse(continued.is_error)
        self.assertEqual("timing", continued.structured_content["next_step"]["step_type"])
        self.assertEqual(
            "yes",
            continued.structured_content["state"]["answers"]["q_government_work"]["value"],
        )

    async def test_exported_schemas_match_runtime_tools(self) -> None:
        exported = json.loads(
            (ROOT / "data/derived/my_info/my_info_mcp_tools.json").read_text(
                encoding="utf-8"
            )
        )
        runtime = [
            tool.model_dump(by_alias=True, exclude_none=True)
            for tool in sorted(await mcp.list_tools(), key=lambda item: item.name)
        ]
        self.assertEqual(runtime, exported["tools"])


if __name__ == "__main__":
    unittest.main()
