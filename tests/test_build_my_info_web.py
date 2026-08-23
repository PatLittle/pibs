from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from my_info.agent_tools import SurveyToolEngine
from scripts.build_my_info_web import ENGINE, build


ROOT = Path(__file__).resolve().parents[1]


class MyInfoWebBuildTests(unittest.TestCase):
    def test_browser_build_is_pinned_to_the_canonical_contract_and_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest = build(output)
            runtime = json.loads((output / "runtime.json").read_text(encoding="utf-8"))

            self.assertEqual("beta", manifest["release_stage"])
            self.assertEqual(runtime["contract"]["content_version"], manifest["contract_version"])
            self.assertEqual(len(runtime["contract"]["questions"]), manifest["question_count"])
            self.assertEqual(len(runtime["features"]), manifest["pib_count"])
            self.assertEqual(
                hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
                manifest["source_hashes"]["canonical_engine_sha256"],
            )
            browser_engine = (output / "engine.mjs").read_text(encoding="utf-8")
            self.assertNotIn("node:", browser_engine)
            self.assertNotIn("DATA_DIR", browser_engine)

    def test_browser_and_python_engines_return_the_same_direct_match(self) -> None:
        answers = [{"question_code": "q_boating", "value": "yes"}]
        refinements = [{
            "question_code": "q_boating",
            "selected_options": ["pleasure_craft_operator_card"],
            "timings": {"pleasure_craft_operator_card": {"kind": "within_1_year"}},
        }]
        python_engine = SurveyToolEngine()
        python_state = python_engine.advance(
            answers=answers, refinements=refinements
        )["state"]
        python_ids = [
            result["record_id"]
            for result in python_engine.evaluate(
                python_state, as_of_year=2026, max_results=500
            )["results"]
        ]

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build(output)
            script = """
import fs from 'node:fs';
import { SurveyToolEngine } from './engine.mjs';
const runtime = JSON.parse(fs.readFileSync('./runtime.json', 'utf8'));
const engine = new SurveyToolEngine(runtime.contract, runtime.features);
const state = engine.advance(null,
  [{question_code:'q_boating', value:'yes'}],
  [{question_code:'q_boating', selected_options:['pleasure_craft_operator_card'], timings:{pleasure_craft_operator_card:{kind:'within_1_year'}}}]
).state;
process.stdout.write(JSON.stringify({manifest:engine.getManifest(), ids:engine.evaluate(state, {asOfYear:2026, maxResults:500}).results.map((item) => item.record_id)}));
"""
            completed = subprocess.run(
                ["node", "--input-type=module", "--eval", script],
                cwd=output,
                check=True,
                capture_output=True,
                text=True,
            )
            browser = json.loads(completed.stdout)

        self.assertEqual(python_ids, browser["ids"])
        self.assertEqual(python_engine.get_manifest(), browser["manifest"])


if __name__ == "__main__":
    unittest.main()
