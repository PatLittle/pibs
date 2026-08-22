import assert from "node:assert/strict";
import test from "node:test";

import { SurveyToolEngine } from "../dist/engine.mjs";

const engine = new SurveyToolEngine();

test("manifest and adaptive advance are versioned", () => {
  const manifest = engine.getManifest();
  assert.equal(manifest.tool_api_version, "0.2.0");
  assert.equal(manifest.question_count, 21);
  assert.equal(manifest.adaptive_route_count, 9);
  let step = engine.advance();
  step = engine.advance(step.state, [{ question_code: "q_government_work", value: "yes" }]);
  assert.equal(step.next_step.step_type, "refinement");
});

test("candidate-only boating record becomes a strong direct route", () => {
  const state = engine.advance(null,
    [{ question_code: "q_boating", value: "yes" }],
    [{
      question_code: "q_boating",
      selected_options: ["pleasure_craft_operator_card"],
      timings: { pleasure_craft_operator_card: { kind: "within_1_year" } }
    }]
  ).state;
  const result = engine.evaluate(state, { asOfYear: 2026 }).results.find((item) => item.bank_number === "TC PPU 023");
  assert.equal(result.match_band, "strong_match");
  assert.equal(result.matched_route_options[0].route_option_code, "pleasure_craft_operator_card");
});

test("tax filing exposes the current source inventory gap", () => {
  const state = engine.advance(null,
    [{ question_code: "q_tax_customs", value: "yes" }],
    [{
      question_code: "q_tax_customs",
      selected_options: ["federal_tax_return"],
      timings: { federal_tax_return: { kind: "within_1_year" } }
    }]
  ).state;
  const result = engine.evaluate(state, { asOfYear: 2026 });
  assert.equal(result.results.length, 0);
  assert.equal(result.assessment.inventory_gaps[0].route_option_code, "federal_tax_return");
});
