import base64
import json
import tempfile
import unittest
from pathlib import Path

from scripts.render_my_info_personas import (
    RenderError,
    find_browser,
    render_all,
    render_results_html,
)


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUB"
    "AScY42YAAAAASUVORK5CYII="
)


def fixture_payloads(root: Path) -> tuple[Path, Path, Path, Path]:
    personas = {
        "schema_version": "1.0",
        "contract_version": "test",
        "assessment_year": 2026,
        "personas": [{
            "persona_id": "alex-example",
            "display_name": "Alex <Example>",
            "subtitle": "Synthetic program tester",
            "summary": "A fictional person used to test deterministic rendering.",
            "contact_line": "Ottawa, Ontario",
            "cv": {
                "experience": [{
                    "role": "Program analyst",
                    "organization": "Example organization",
                    "period": "2020–present",
                    "highlights": ["Participated in a federal consultation"],
                }],
                "education": [{"degree": "Master of Testing", "institution": "Example University"}],
                "memberships": ["Community association"],
            },
            "answers": [],
            "refinements": [],
            "episodes": [],
        }],
    }
    evaluations = {
        "personas": [{
            "persona_id": "alex-example",
            "evaluation": {
                "assessment": {
                    "as_of_year": 2026,
                    "caveat": "Candidate records only.",
                    "inventory_gaps": [{"message": "An example inventory gap."}],
                },
                "summary": {
                    "total_matches": 1,
                    "holding_status_counts": {"likely_held": 1},
                },
                "results": [{
                    "record_id": "institution:EX PPU 001",
                    "bank_number": "EX PPU 001",
                    "scope": "institution_specific",
                    "institution_name": "Example Agency",
                    "title": "Example records",
                    "source_url": "https://example.test/pib",
                    "match_band": "strong_match",
                    "holding_status": "likely_held",
                    "retention": {"rationale": "The interaction is current."},
                    "categories_of_personal_information": [
                        {"category_id": "PI_CAT_001", "name": "Identifying information"}
                    ],
                }],
            },
            "analysis": {"observations": ["Expected match was returned."]},
        }],
    }
    personas_path = root / "personas.json"
    evaluations_path = root / "evaluation.json"
    portrait_dir = root / "portraits"
    output_dir = root / "generated"
    portrait_dir.mkdir()
    personas_path.write_text(json.dumps(personas), encoding="utf-8")
    evaluations_path.write_text(json.dumps(evaluations), encoding="utf-8")
    (portrait_dir / "alex-example.png").write_bytes(PNG_1X1)
    return personas_path, evaluations_path, portrait_dir, output_dir


class PersonaRendererTests(unittest.TestCase):
    def test_html_only_outputs_are_deterministic_and_escape_persona_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture_payloads(Path(directory))
            outputs = render_all(*paths, html_only=True)
            first = {path.name: path.read_bytes() for path in outputs}
            outputs_again = render_all(*paths, html_only=True)
            second = {path.name: path.read_bytes() for path in outputs_again}

            self.assertEqual(first, second)
            self.assertEqual(2, len(outputs))
            cv = next(path for path in outputs if path.name.endswith("-cv.html")).read_text()
            results = next(path for path in outputs if path.name.endswith("-survey-results.html")).read_text()
            self.assertIn("SYNTHETIC TEST PERSONA", cv)
            self.assertIn("Alex &lt;Example&gt;", cv)
            self.assertIn("data:image/png;base64,", cv)
            self.assertIn("Likely still held", results)
            self.assertIn("Example Agency", results)
            self.assertIn("Known inventory gaps", results)

    def test_missing_portrait_has_actionable_error_and_no_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture_payloads(Path(directory))
            (paths[2] / "alex-example.png").unlink()
            with self.assertRaisesRegex(RenderError, "never creates placeholders"):
                render_all(*paths, html_only=True)

    def test_unknown_persona_filter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture_payloads(Path(directory))
            with self.assertRaisesRegex(RenderError, "Unknown persona_id"):
                render_all(*paths, html_only=True, persona_ids={"missing-persona"})

    def test_unsafe_source_link_is_not_rendered(self) -> None:
        persona = {"persona_id": "safe", "display_name": "Safe Example"}
        evaluation = {
            "persona_id": "safe",
            "evaluation": {
                "summary": {"total_matches": 1},
                "assessment": {},
                "results": [{
                    "institution_name": "Agency",
                    "title": "Record",
                    "source_url": "javascript:alert(1)",
                    "holding_status": "retention_unknown",
                }],
            },
        }
        rendered = render_results_html(persona, evaluation, 2026)
        self.assertNotIn("javascript:", rendered)

    @unittest.skipUnless(find_browser(), "Chromium-family browser is unavailable")
    def test_chromium_can_render_both_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = fixture_payloads(Path(directory))
            outputs = render_all(*paths, browser_name=find_browser())
            pdfs = [path for path in outputs if path.suffix == ".pdf"]
            self.assertEqual(2, len(pdfs))
            for pdf in pdfs:
                self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                self.assertGreater(pdf.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
