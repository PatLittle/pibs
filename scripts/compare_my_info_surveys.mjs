import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SurveyToolEngine } from "../site/my_info/engine.mjs";
import { SurveyV2 } from "../my_info_v2/engine.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
const baseline = read("site/my_info/runtime.json");
const candidate = read("site/my_info_v2/runtime.json");
const v1 = new SurveyToolEngine(baseline.contract,baseline.features);
const v2 = new SurveyV2(candidate);
const vac = "ati-schedule-i-department-of-veterans-affairs";
const dnd = "ati-schedule-i-department-of-national-defence";
const cbsa = "ati-schedule-i-canada-border-services-agency";
const scenarios = [
  {name:"No reported activity", v1:{}, v2:[]},
  {name:"Veterans education benefit", v1:{q_military_veterans:["veterans_program"]}, v2:["veterans_education"], departments:[vac]},
  {name:"Regular Force service", v1:{q_military_veterans:["caf_service"]}, v2:["caf_regular_service"], departments:[dnd]},
  {name:"NEXUS application", v1:{q_travel_border:["trusted_traveller"]}, v2:["nexus"]},
  {name:"Federal voting", v1:{q_civic_contact:["federal_election"]}, v2:["federal_vote"]},
  {name:"Space launch attendance", v1:{q_culture_volunteer:["space_launch_attendance"]}, v2:["space_launch"]},
  {name:"CBSA service complaint", v1:{q_complaint_appeal:["cbsa_complaint_review"]}, v2:["cbsa_complaint"], departments:[cbsa]},
  {name:"Common four plus NEXUS", v1:{q_common_start:["federal_tax_return","federal_election","passport_application","border_crossing"],q_travel_border:["trusted_traveller"]}, v2:[...candidate.quick_activity_ids,"nexus"], quick:true},
];

function replayV1(scenario) {
  let response=v1.advance();
  const counts={question:0,refinement:0,timing:0,department:0};
  for(let guard=0;!response.complete&&guard<200;guard++){
    const s=response.next_step;
    counts[s.step_type]++;
    if(s.step_type==="question") response=v1.advance(response.state,[{question_code:s.question_code,value:scenario.v1[s.question_code]?"yes":"no"}]);
    else if(s.step_type==="refinement") response=v1.advance(response.state,[],[{question_code:s.question_code,selected_options:scenario.v1[s.question_code],timings:{}}]);
    else if(s.step_type==="timing") {
      const refinement=structuredClone(response.state.refinements[s.question_code]);
      refinement.timings[s.route_option_code]={kind:"unknown"};
      response=v1.advance(response.state,[],[{question_code:s.question_code,...refinement}]);
    }else if(s.step_type==="department") {
      const options=s.options.map(o=>o.institution_id);
      const selected=scenario.departments?scenario.departments.filter(id=>options.includes(id)):options;
      if(!selected.length)throw Error(`No department selection for ${scenario.name}`);
      response=v1.advance(response.state,[],[],[{question_code:s.question_code,institution_ids:selected}]);
    }
  }
  if(!response.complete)throw Error(`V1 did not complete: ${scenario.name}`);
  const results=v1.evaluate(response.state,{asOfYear:2026,maxResults:500}).results;
  return {screens:Object.values(counts).reduce((a,b)=>a+b,0),...counts,banks:results.map(r=>r.bank_number).sort()};
}

function replayV2(scenario) {
  let state=v2.select(v2.createState(),{activities:scenario.v2,quick_activities:scenario.quick?candidate.quick_activity_ids:[]});
  let count=0;
  for(let guard=0;guard<20;guard++){
    const step=v2.nextStep(state);
    if(step.type==="results")break;
    count++;
    state=v2.setScope(state,step.activity_id,scenario.departments||["unknown"]);
  }
  return {selection_submissions:1,required_scope_questions:count,optional_date_questions:v2.timingQuestions(state).length,
          banks:v2.evaluate(state,2026).results.map(r=>r.bank_number_key).sort()};
}

const results=scenarios.map(s=>({name:s.name,v1:replayV1(s),v2:replayV2(s)}));
const coverage=candidate.coverage;
const report={baseline_commit:"9aa3b07",v1_branch:"codex/my-info-v1-review",v2_branch:"codex/my-info-v2",coverage,scenarios:results};
fs.writeFileSync(path.join(root,"docs/my_info_v2/comparison.json"),JSON.stringify(report,null,2)+"\n");
const rows=results.map(r=>`| ${r.name} | ${r.v1.screens} | ${r.v1.department} | ${r.v1.timing} | ${r.v2.selection_submissions+r.v2.required_scope_questions} | ${r.v2.optional_date_questions} |`);
const md=["# My Info — V1 and V2 comparison","",
  "Both versions are available side by side on GitHub Pages and preserved on feature branches. The original remains at `/pibs/my_info/`; the new review prototype is at `/pibs/my_info_v2/`. Publication is controlled through `main` with separate deployment folders.","",
  "- V1: `codex/my-info-v1-review` — existing survey plus a generated, printable logic document.",
  "- V2: `codex/my-info-v2` — additive prototype at `site/my_info_v2/`; the V1 application, classifier, data and MCP endpoint are unchanged.","",
  "## Open and review","",
  "Published comparison: https://patlittle.github.io/pibs/my_info_compare/ — includes both surveys, printable logic documents and routing spreadsheets.","",
  "From a checkout of the V2 branch, run `python3 -m http.server 8766 --directory site`, then open `http://localhost:8766/my_info_compare/`.","",
  "The comparison page links to both runnable versions and their printable review documents. For spreadsheet review, use `docs/my_info_v1/pib_mapping.csv`, `docs/my_info_v2/routing_ledger.csv`, and `docs/my_info_v2/coverage.csv`.","",
  "V1's document is generated from its actual 22 gates, 76 options, source selectors, timing and department rules. V2's document states the proposed flow, exact selectors, source population/purpose excerpts, retention rules, edge cases and remaining work.","",
  "## What changed and why","",
  "| Decision | V1 | V2 |","|---|---|---|",
  "| Entry | Up to 22 broad yes/no gates and child questions | Recognizable activities in eight expandable groups, with program search |",
  "| Known department | Sometimes asks people to distinguish delivery or archive institutions | Infers the institution from the program; explains custody separately |",
  "| Record selection | Broad keyword classifier plus bank-number selectors | Exact institution-scoped selectors, supported by purpose and population |",
  "| Less-common programs | Only classifier-reachable PIBs appear | Full source directory; explicit population review required to add a record |",
  "| Dates | Asked for each selected activity even if unusable | Results first; optional dates only for a reviewed event-based rule |",
  "| Common four | Skips full tax/travel/civic gates | Resolves only selected activities and leaves all others available |",
  "| Uncertainty | Often absent from normal results | Separate unsure, source-gap and unresolved-program guidance |",
  "| Standard PIB | Generic government-wide description | Tied to the organization the person identifies, or explicitly unknown |","",
  "## Source findings that changed the design","",
  "The Info Source introductions distinguish organizational responsibilities and service delivery; the PIB population and purpose establish personal applicability. For example IRCC's introduction names Service Canada passport delivery, DND describes CAF administration, Health Canada describes the transfer of First Nations service responsibilities to ISC, and VAC's program section distinguishes its benefits.","",
  "- Voting was labelled a gap even though ELECTIONS PPU 037 is already collected. V2 uses its registration/identification description.",
  "- Generic veteran routes included VAC PPU 200, the narrowly historical Agent Orange payment. V2 requires that named activity.",
  "- CAF applicant and Regular Force personnel files describe different populations. V2 distinguishes the roles and does not ask the person to choose an archive.",
  "- General border crossing did not establish commercial passenger, duties-payment or regional immigration-interview records. V2 has distinct activities.",
  "- CPP/OAS routing omitted the actual OAS bank, ESDC PPU 116. V2 selects CPP 146 and OAS 116 separately.",
  "- Bank keys are repeated across institutional publishers. V2 uses the full publisher-and-bank record ID.",
  "- V1's derived retention start is unspecified for 630 records. V2 cannot borrow an activity date for an unspecified start. CSA020 starts at launch; DND818 starts at release and transfers to LAC.","",
  "## Measured interaction paths","",
  "These are executable scenario replays, not usability timing measurements. V2's one activity-selection submission still involves reading/selecting activities. The table must not be read as proof that a large checklist takes one decision. Optional program search and directory review add effort, and optional timing is shown separately.","",
  "| Scenario | V1 mandatory screens | V1 department prompts | V1 date prompts | V2 selection + required prompts | V2 optional date prompts |",
  "|---|---:|---:|---:|---:|---:|",...rows,"",
  "V1 dates are answered 'unknown' to expose its mandatory path. V2 dates are deferred. Record-bank outputs for every replay are in `docs/my_info_v2/comparison.json`; more records is not automatically a better result.","",
  "## Coverage, quality and release boundary","",
  `V2 currently has ${coverage.activities} reviewed activity statements reaching ${coverage.guided_record_count}/${coverage.inventory_rows} inventory rows (${coverage.guided_percent}%). All ${coverage.directory_record_count} records can be discovered through the directory, with ${coverage.directory_only_count} requiring that additional program/population review. V1's 597 direct-labelled rows are a broader theoretical ceiling; these two measures use different evidentiary thresholds.`,"",
  `Institutional context is available from local captures for ${coverage.institutions_with_context_en} English and ${coverage.institutions_with_context_fr} French institutions. There are ${coverage.source_quality_flags.title_needs_review} flagged titles, ${coverage.source_quality_flags.population_missing} missing populations and ${coverage.source_quality_flags.purpose_missing} missing purposes in the source inventory. These are exposed, not silently repaired.`,"",
  `Only ${coverage.reviewed_retention_rules} unambiguous rules are executable in V2. Other schedules remain available to read. Expand that ledger and the guided catalogue with source review before claiming production-level coverage.`,"",
  "This branch is a reviewable design prototype. Public release still needs broader program curation, more retention review, fluent French review, accessibility/user testing, and tests with realistic stories including indirect records. The structured V2 engine supports the same next-step/evaluation contract a future voice adapter can use; the existing public MCP service has not been replaced.","",
  "## Rebuild and verify","",
  "```bash","python3 scripts/build_my_info_v2.py","node --test tests/my_info_v2.test.mjs","node scripts/compare_my_info_surveys.mjs","```","",
];
fs.writeFileSync(path.join(root,"docs/MY_INFO_SURVEY_COMPARISON.md"),md.join("\n"));
const out=path.join(root,"site/my_info_compare");fs.mkdirSync(out,{recursive:true});
fs.copyFileSync(path.join(root,"docs/my_info_v1/index.html"),path.join(out,"v1-review.html"));
fs.copyFileSync(path.join(root,"docs/my_info_v1/pib_mapping.csv"),path.join(out,"v1-pib-mapping.csv"));
fs.copyFileSync(path.join(root,"docs/MY_INFO_SURVEY_COMPARISON.md"),path.join(out,"comparison.md"));
fs.writeFileSync(path.join(out,"comparison.json"),JSON.stringify(report,null,2)+"\n");
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compare My Info surveys</title><link rel="stylesheet" href="https://cdn.design-system.alpha.canada.ca/@cdssnc/gcds-components@0.40.0/dist/gcds/gcds.css"><script type="module" src="https://cdn.design-system.alpha.canada.ca/@cdssnc/gcds-components@0.40.0/dist/gcds/gcds.esm.js"></script><link rel="stylesheet" href="../prototype-label.css"><style>body{font:18px/1.55 system-ui;max-width:1000px;margin:0 auto;padding:0 24px 24px;color:#18323d;background:#f4f7f6}h1{line-height:1.15}.versions{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}article{background:white;border:1px solid #b8cccc;border-radius:10px;padding:25px}a{color:#075b8b}.launch{display:inline-block;background:#166450;color:white;padding:12px 20px;border-radius:5px;text-decoration:none}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border-bottom:1px solid #baccca;text-align:left;padding:12px}.scroll{overflow:auto}.note{background:#e3eee9;padding:18px}code{overflow-wrap:anywhere}</style><gcds-header lang-href="#" skip-to-href="#compare-main"><div class="prototype-signature" slot="signature"><span class="prototype-label-text" style="display:none">Prototype - For Discussion</span><gcds-signature></gcds-signature></div><a href="../index.html" slot="toggle">PIBS data explorer</a><gcds-breadcrumbs slot="breadcrumb"><gcds-breadcrumbs-item href="../index.html">PIBS</gcds-breadcrumbs-item></gcds-breadcrumbs></gcds-header><main id="compare-main"><p>My Info · comparison branches</p><h1>Two approaches to finding your federal records</h1><p>Try the original topic questionnaire and the activity-based prototype side by side.</p><div class="versions"><article><h2>Version 1</h2><p>22 topic gates, named refinements, dates and department prompts.</p><p><a class="launch" href="../my_info/">Try V1</a></p><p><a href="v1-review.html">Review V1 logic</a> · <a href="v1-pib-mapping.csv">PIB spreadsheet</a></p><code>codex/my-info-v1-review</code></article><article><h2>Version 2</h2><p>Recognizable activities, inferred organizations, optional dates and a full program directory.</p><p><a class="launch" href="../my_info_v2/">Try V2</a></p><p><a href="../my_info_v2/review/index.html">Review V2 logic</a> · <a href="../my_info_v2/review/routing_ledger.csv">Routing spreadsheet</a></p><code>codex/my-info-v2</code></article></div><h2>What to compare</h2><p>Can you recognize the activity? Is each follow-up useful? Are the right institutions and roles inferred? Can you explain every record in the result? Where does uncertainty need another question?</p><p class="note">V2 is a design prototype: ${coverage.guided_record_count} source-checked guided records, ${coverage.directory_record_count} browsable records requiring personal review, and ${coverage.reviewed_retention_rules} executable retention rules. Directory access is not automatic survey coverage.</p><h2>Scenario replay</h2><p>Counts exclude results. Selecting activities and browsing programs take effort; one selection screen does not mean one cognitive decision.</p><div class="scroll"><table><thead><tr><th>Scenario</th><th>V1 mandatory screens</th><th>V2 selection + required prompts</th><th>V2 optional dates</th></tr></thead><tbody>${results.map(r=>`<tr><td>${r.name}</td><td>${r.v1.screens}</td><td>${1+r.v2.required_scope_questions}</td><td>${r.v2.optional_date_questions}</td></tr>`).join("")}</tbody></table></div><p><a href="comparison.md">Full comparison and limitations</a> · <a href="comparison.json">Replay data</a></p></main></html>`;
fs.writeFileSync(path.join(out,"index.html"),html);
console.log(JSON.stringify(results,null,2));
