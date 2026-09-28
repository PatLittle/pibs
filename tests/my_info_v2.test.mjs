import assert from "node:assert/strict";
import test from "node:test";
import fs from "node:fs";
import { SurveyV2 } from "../my_info_v2/engine.mjs";

const runtime = JSON.parse(fs.readFileSync(new URL("../site/my_info_v2/runtime.json", import.meta.url), "utf8"));
const engine = new SurveyV2(runtime);
const choose = (activities, other = {}) => engine.select(engine.createState(), {activities, ...other});
const banks = (state) => engine.evaluate(state, 2026).results.map(r => r.bank_number_key);
const dnd = "ati-schedule-i-department-of-national-defence";
const cbsa = "ati-schedule-i-canada-border-services-agency";

test("all guided selectors resolve exactly and carry source population evidence", () => {
  for (const a of runtime.activities) {
    for (const id of a.record_ids) {
      assert.ok(engine.records.has(id), id);
      assert.match(engine.records.get(id).source_url_en, /^https?:\/\//, id);
      assert.match(engine.records.get(id).source_url_fr, /^https?:\/\//, id);
      assert.ok(a.source_evidence.some(e => e.record_id === id && e.field.startsWith("class_of_individuals")), id);
    }
  }
  assert.equal(runtime.records.length, 1040);
  assert.equal(new Set(runtime.records.map(r=>r.record_id)).size, 1040);
});

test("veterans programs infer VAC and never infer Agent Orange from another benefit", () => {
  const state = choose(["veterans_education"]);
  assert.equal(engine.nextStep(state).type, "results");
  assert.deepEqual(banks(state), ["VAC PPU 710"]);
  assert.ok(!banks(state).includes("VAC PPU 200"));
  const unknown = choose(["veterans_unknown"]);
  assert.equal(engine.nextStep(unknown).type, "results");
  assert.equal(engine.evaluate(unknown).gaps[0].institution_ids[0], "ati-schedule-i-department-of-veterans-affairs");
  assert.deepEqual(banks(unknown), []);
});

test("CAF applicants and Regular Force members have distinct records without department questions", () => {
  const application = choose(["caf_application"]);
  assert.deepEqual(banks(application), ["DND PPU 025"]);
  const served = choose(["caf_regular_service"]);
  assert.equal(engine.nextStep(served).type, "results");
  assert.deepEqual(banks(served), ["DND PPE 818"]);
  assert.deepEqual(engine.evaluate(served).results[0].owner_ids, [dnd]);
});

test("old CAF service shows possible archive custody using release date", () => {
  let state = choose(["caf_regular_service"]);
  const question = engine.timingQuestions(state)[0];
  assert.equal(question.event, "service_ended");
  state = engine.setDate(state, question.key, {kind:"year", year:2000});
  assert.equal(engine.evaluate(state,2026).results[0].retention.status, "archive_possible");
});

test("the quick four leave NEXUS, other travel and civic activities available", () => {
  const state = choose([...runtime.quick_activity_ids, "nexus", "health_consultation"], {quick_activities:runtime.quick_activity_ids});
  assert.ok(banks(state).includes("CBSA PPU 031"));
  assert.ok(banks(state).includes("HC PPU 051"));
  assert.ok(banks(state).includes("ELECTIONS PPU 037"));
  assert.ok(!banks(state).includes("CBSA PPU 014"));
  assert.ok(!banks(state).includes("CBSA PPU 010"));
  const crossing = engine.evaluate(state,2026).results.find(r=>r.bank_number_key==="CBSA PPU 018");
  assert.equal(crossing.retention.status,"may_remain");
});

test("election registration is available while tax filing stays an honest source gap", () => {
  assert.deepEqual(banks(choose(["federal_vote"])), ["ELECTIONS PPU 037"]);
  const tax = engine.evaluate(choose(["tax_return"]));
  assert.equal(tax.results.length,0);
  assert.equal(tax.gaps[0].id,"tax_return");
});

test("exact publisher IDs prevent duplicated ESDC institutions", () => {
  const result=engine.evaluate(choose(["cpp","oas"]));
  assert.equal(result.results.length,2);
  assert.ok(result.results.every(r=>r.institution_id==="ati-schedule-i-department-of-employment-and-social-development"));
  assert.ok(result.results.some(r=>r.bank_number_key==="ESDC PPU 116"));
});

test("generic complaints never fan out and unknown recipients remain unknown", () => {
  let state=choose(["other_complaint"]);
  assert.equal(engine.nextStep(state).type,"institution");
  state=engine.setScope(state,"other_complaint",[cbsa]);
  assert.deepEqual(banks(state),[]);
  assert.equal(engine.evaluate(state).gaps.length,1);
  assert.deepEqual(banks(choose(["cbsa_complaint"])),["CBSA PPU 003"]);
  state=engine.setScope(state,"other_complaint",["unknown"]);
  assert.equal(engine.nextStep(state).type,"results");
  assert.deepEqual(banks(state),[]);
});

test("standard banks bind to a reported organization rather than every institution", () => {
  let state=choose(["access_request"]);
  state=engine.setScope(state,"access_request",[cbsa]);
  const result=engine.evaluate(state).results[0];
  assert.equal(result.scope,"standard");
  assert.deepEqual(result.owner_ids,[cbsa]);
  assert.throws(()=>engine.setScope(state,"access_request",[cbsa,"unknown"]),/Unknown cannot/);
});

test("ERC requires the explicit member/referral activity and CSA requires launch attendance", () => {
  assert.deepEqual(banks(choose(["erc_grievance"])),["ERC PPU 802"]);
  assert.ok(!banks(choose(["cbsa_complaint","professional_contract"])).some(b=>b.startsWith("ERC")));
  assert.ok(!banks(choose(["professional_contract"])).includes("CSA PPU 020"));
  const launch=choose(["space_launch"]);
  assert.deepEqual(banks(launch),["CSA PPU 020"]);
  assert.equal(engine.timingQuestions(launch)[0].event_label_en,"the mission launch took place");
});

test("dates are optional and complex passport/voting rules do not ask meaningless dates", () => {
  const state=choose(["passport","federal_vote","oas","veterans_education"]);
  assert.equal(engine.nextStep(state).type,"results");
  assert.deepEqual(engine.timingQuestions(state),[]);
  assert.ok(engine.evaluate(state).results.every(r=>r.retention.status==="unknown"));
});

test("retention boundaries stay uncertain and no closure means no elapsed-from-complaint claim", () => {
  let state=choose(["space_launch"]);
  state=engine.setDate(state,engine.timingQuestions(state)[0].key,{kind:"year",year:2024});
  assert.equal(engine.evaluate(state,2026).results[0].retention.status,"may_remain");
  state=choose(["cbsa_complaint"]);
  state=engine.setDate(state,engine.timingQuestions(state)[0].key,{kind:"not_yet"});
  assert.equal(engine.evaluate(state,2026).results[0].retention.status,"event_not_reached");
});

test("search alone produces no personal matches; all inventory rows can be explicitly reviewed", () => {
  assert.equal(engine.searchRecords().length,1040);
  assert.ok(engine.searchRecords("automated document").some(r=>r.bank_number_key==="PSU 904"));
  assert.deepEqual(engine.evaluate(engine.createState()).results,[]);
  const chosen=choose([],{reviewed_records:["standard:PSU 904"]});
  assert.deepEqual(banks(chosen),["PSU 904"]);
  assert.equal(engine.evaluate(chosen).results[0].bases[0].kind,"source_reviewed");
});

test("uncertainty, changed selections and invalid state cannot silently create positive matches", () => {
  const uncertain=choose([],{unsure:["veterans_education"]});
  assert.equal(engine.evaluate(uncertain).results.length,0);
  assert.equal(engine.evaluate(uncertain).unresolved.length,1);
  let state=choose(["space_launch"]);
  state=engine.setDate(state,engine.timingQuestions(state)[0].key,{kind:"year",year:2020});
  state=engine.select(state,{activities:["passport"]});
  assert.deepEqual(state.dates,{});
  assert.throws(()=>choose(["made_up_activity"]),/Unknown activities/);
  assert.throws(()=>engine.validate({...engine.createState(),case_details:"text"}),/Unexpected state field/);
});
