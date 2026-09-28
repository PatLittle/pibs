import assert from "node:assert/strict";
import test from "node:test";

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { findDataDir, SurveyToolEngine } from "../dist/engine.mjs";

const engine = new SurveyToolEngine();

test("runtime data resolves after a Netlify function bundle relocates the module", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "my-info-netlify-layout-"));
  const moduleDir = path.join(root, "netlify", "functions");
  const dataDir = path.join(root, "vendor", "pibs-my-info", "data");
  fs.mkdirSync(moduleDir, { recursive: true });
  fs.mkdirSync(dataDir, { recursive: true });
  fs.writeFileSync(path.join(dataDir, "runtime.json"), "{}", "utf8");
  try {
    assert.equal(findDataDir(moduleDir, root), dataDir);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("manifest and adaptive advance are versioned", () => {
  const manifest = engine.getManifest();
  assert.equal(manifest.tool_api_version, "0.4.0");
  assert.equal(manifest.question_count, 22);
  assert.equal(manifest.adaptive_route_count, 22);
  let step = engine.advance();
  assert.equal(step.next_step.question_code, "q_common_start");
  step = engine.advance(step.state, [{ question_code: "q_common_start", value: "no" }, { question_code: "q_government_work", value: "yes" }]);
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

test("department follow-up narrows broad complaint matches", () => {
  const answers = engine.questionOrder.filter((code) => code !== "q_complaint_appeal").map((question_code) => ({ question_code, value: "no" }));
  answers.push({ question_code: "q_complaint_appeal", value: "yes" });
  let response = engine.advance(null, answers, [{
    question_code: "q_complaint_appeal",
    selected_options: ["other_complaint_appeal"],
    timings: { other_complaint_appeal: { kind: "within_1_year" } }
  }]);
  assert.equal(response.next_step.step_type, "department");
  const selected = response.next_step.options[0].institution_id;
  response = engine.advance(response.state, [], [], [{
    question_code: "q_complaint_appeal",
    institution_ids: [selected]
  }]);
  assert.equal(response.complete, true);
  const results = engine.evaluate(response.state, { asOfYear: 2026, maxResults: 500 }).results;
  assert.ok(results.length > 0);
  assert.ok(results.every((item) => !item.institution_id || item.institution_id === selected));
});

test("common shortcut selects four recent activities without individual timing prompts", () => {
  const response = engine.advance(null,
    [{ question_code: "q_common_start", value: "yes" }],
    [{ question_code: "q_common_start", selected_options: ["federal_tax_return", "federal_election", "passport_application", "border_crossing"], timings: {} }]
  );
  assert.equal(response.next_step.question_code, "q_government_work");
  assert.equal(response.progress.total_questions, 19);
  const evaluation = engine.evaluate(response.state, { asOfYear: 2026, maxResults: 500 });
  assert.ok(evaluation.assessment.inventory_gaps.some((gap) => gap.route_option_code === "federal_tax_return"));
  assert.ok(evaluation.assessment.inventory_gaps.some((gap) => gap.route_option_code === "federal_election"));
  assert.ok(!evaluation.assessment.unanswered_question_codes.includes("q_travel_border"));
  assert.equal(evaluation.results.find((item) => item.bank_number === "IRCC PPU 081").retention.timing.kind, "within_10_years");
  const none = engine.advance(null,
    [{ question_code: "q_common_start", value: "yes" }],
    [{ question_code: "q_common_start", selected_options: ["none_recent"], timings: {} }]
  );
  assert.equal(engine.evaluate(none.state, { asOfYear: 2026 }).results.length, 0);
  assert.throws(() => engine.advance(null,
    [{ question_code: "q_common_start", value: "yes" }],
    [{ question_code: "q_common_start", selected_options: ["none_recent", "border_crossing"], timings: {} }]
  ), /none_recent cannot be combined/);
});

test("RCMP External Review Committee records require the RCMP-member route", () => {
  const erc = "ati-schedule-i-royal-canadian-mounted-police-external-review-committee";
  const answers = engine.questionOrder.map((question_code) => ({ question_code, value: question_code === "q_complaint_appeal" ? "yes" : "no" }));
  const generic = engine.advance(null, answers, [{ question_code: "q_complaint_appeal", selected_options: ["other_complaint_appeal"], timings: { other_complaint_appeal: { kind: "within_1_year" } } }]);
  assert.ok(!generic.next_step.options.some((item) => item.institution_id === erc));
  assert.throws(() => engine.advance(generic.state, [], [], [{ question_code: "q_complaint_appeal", institution_ids: [erc] }]), /unsupported department IDs/);
  assert.ok(!engine.evaluate(generic.state, { asOfYear: 2026, maxResults: 500 }).results.some((item) => item.bank_number.startsWith("ERC PPU")));
  const specific = engine.advance(null, answers, [{ question_code: "q_complaint_appeal", selected_options: ["rcmp_member_review"], timings: { rcmp_member_review: { kind: "within_1_year" } } }]);
  assert.equal(specific.next_step.step_type, "department");
  const selected = engine.advance(specific.state, [], [], [{ question_code: "q_complaint_appeal", institution_ids: [erc] }]);
  assert.ok(engine.evaluate(selected.state, { asOfYear: 2026, maxResults: 500 }).results.some((item) => item.bank_number === "ERC PPU 802"));
});

test("space launch registration requires the named public event route", () => {
  const business = engine.advance(null,
    [{ question_code: "q_business_supplier", value: "yes" }],
    [{ question_code: "q_business_supplier", selected_options: ["other_business_regulatory"], timings: { other_business_regulatory: { kind: "within_1_year" } } }]
  );
  assert.ok(!engine.evaluate(business.state, { asOfYear: 2026, includePossible: true, maxResults: 500 }).results.some((item) => item.bank_number === "CSA PPU 020"));
  const attended = engine.advance(null,
    [{ question_code: "q_culture_volunteer", value: "yes" }],
    [{ question_code: "q_culture_volunteer", selected_options: ["space_launch_attendance"], timings: { space_launch_attendance: { kind: "within_1_year" } } }]
  );
  assert.equal(engine.evaluate(attended.state, { asOfYear: 2026, maxResults: 500 }).results.find((item) => item.bank_number === "CSA PPU 020").match_band, "strong_match");
});
