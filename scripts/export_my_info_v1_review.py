#!/usr/bin/env python3
"""Export the checked-in V1 survey as a review document without changing runtime data."""

from __future__ import annotations

import csv
from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from my_info.agent_tools import SurveyToolEngine, TIMING_KINDS  # noqa: E402

OUT = ROOT / "docs/my_info_v1"


def pipe(value):
    return set(filter(None, value.split("|")))


def build_review(engine):
    named = {bank for route in engine.routes.values() for option in route["options"]
             for bank in option["selectors"]["bank_numbers"]}
    records = []
    for row in engine.features:
        strong = bool(row["question_codes"]) and row["bank_number_key"] not in engine.exclusive_banks
        possible = bool(row["candidate_question_codes"]) and row["bank_number_key"] not in engine.exclusive_banks
        band = "direct" if strong or row["bank_number_key"] in named else "possible_only" if possible else "not_discoverable"
        records.append({**row, "reachability": band})
    questions = []
    for code in engine.question_order:
        question = {"code": code, "source": engine.questions[code],
                    "en": engine._question_view(code, "en-CA"),
                    "fr": engine._question_view(code, "fr-CA"), "options": []}
        for option in engine.routes.get(code, {}).get("options", []):
            state = engine.create_state()
            state["answers"][code] = {"value": "yes"}
            state["refinements"][code] = {"selected_options": [option["code"]], "timings": {}}
            departments = engine._department_options(code, state)
            banks = set(option["selectors"]["bank_numbers"])
            matched = [r for r in records if r["bank_number_key"] in banks]
            question["options"].append({**option, "departments_if_selected_alone": departments,
                "department_followup_if_selected_alone": len(departments) > 1 or bool(departments and code == "q_complaint_appeal"),
                "matched_records": matched,
                "missing_selectors": sorted(banks - {r["bank_number_key"] for r in matched})})
        state = engine.create_state()
        state["answers"][code] = {"value": "yes"}
        question["broad_department_options"] = engine._department_options(code, state)
        question["route"] = engine.routes.get(code)
        question["primary_records"] = [r["record_id"] for r in records if code in pipe(r["question_codes"])]
        question["candidate_records"] = [r["record_id"] for r in records if code in pipe(r["candidate_question_codes"])]
        questions.append(question)
    fingerprint_paths = [engine.contract_path, engine.feature_path, ROOT / "my_info/agent_tools.py",
                         ROOT / "my_info/web/app.mjs", ROOT / "packages/my-info-mcp/src/engine.mjs"]
    return {"content_version": engine.contract["content_version"], "data_snapshot": engine.contract["data_snapshot"],
        "inputs": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in fingerprint_paths},
        "inventory_count": len(records), "coverage": dict(Counter(r["reachability"] for r in records)),
        "questions": questions, "records": records}


class Document:
    def __init__(self):
        self.md = []
        self.html = []

    def heading(self, text, level=2, anchor=None):
        self.md.extend(["#" * level + " " + text, ""])
        self.html.append(f'<h{level}' + (f' id="{escape(anchor)}"' if anchor else '') + f'>{escape(text)}</h{level}>')

    def paragraph(self, text):
        self.md.extend([text, ""])
        self.html.append(f"<p>{escape(text)}</p>")

    def table(self, headers, rows, links=False):
        def mdcell(value):
            if isinstance(value, tuple):
                return " / ".join(f"[{label}]({url})" for label, url in value) or "—"
            return str(value).replace("|", " / ").replace("\n", " ")
        def htmlcell(value):
            if isinstance(value, tuple):
                return " / ".join(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>' for label, url in value) or "—"
            return escape(str(value))
        self.md.extend(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"])
        self.md.extend("| " + " | ".join(mdcell(v) for v in row) + " |" for row in rows)
        self.md.append("")
        self.html.append('<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th>{escape(h)}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{htmlcell(v)}</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table></div>')


RULES = [
    ("Survey flow", "Start → quick check or individual path → next unanswered topic → if yes, select a named activity when offered → timing for each selected activity → department selection when required → repeat → candidate results. No, not sure and prefer not to answer advance without follow-ups. The normal web hides uncertain/possible-only results."),
    ("Quick path", "The opening yes means use the shortcut, not yes to every activity. The web preselects tax filing, voting, passport and border crossing; unchecked activities are omitted. Empty selection becomes none_recent, which cannot coexist with another option. Every selected activity uses 0–10 years. Once the shortcut has a refinement, the engine skips q_tax_customs, q_travel_border and q_civic_contact, even when none_recent is selected. This also skips other customs, trusted-traveller and civic activities; absence of results cannot rule these out. The detailed path has 22 gates; the quick path has 19. These counts exclude refinement, date and department screens."),
    ("Department rule", "After timing, ask for departments only if the available list has more than one institution; complaints ask even for a singleton. Department options are built from primary-classified rows for that gate, filtered by named selectors unless an Other fallback is chosen. They are not built from all selector records. Several selected activities share one combined department follow-up. Displayed institution hints do not themselves set a department answer. Rows with an empty institution ID pass any department filter."),
    ("Why some follow-ups feel redundant", "Veterans-payment selected alone currently yields only Veterans Affairs and skips the department step. Selecting another payment option can create a combined follow-up. CAF-service selected alone yields National Defence and Library and Archives of Canada because the inventory includes archived military records. Asking the person to choose the archive implies knowledge they may not have. A future design should distinguish an activity's responsible institution from later custodians, while retaining source-backed cross-institution cases such as Service Canada delivery."),
    ("Named versus broad matching", "A named activity selects every inventory row with one of its exact bank-number keys, subject to department filtering. It does not independently check eligibility or the purpose/class-of-individuals text. Selecting only named activities suppresses the broad parent-question match. Selecting an Other fallback re-enables all primary matches for that topic and, when requested, candidate matches. Exclusive banks (including CSA launch attendance and ERC member reviews) require their named selector route."),
    ("Match confidence", "A primary topic or exact named route yields strong_match. Candidate-only topic signals yield possible_match only when include_possible is true. Not sure/prefer not to answer can yield review_if_relevant only when that option is enabled. The ordinary web passes includePossible: false. Strong is the engine's label, not independently validated precision. Personal-information fields such as citizenship or passport numbers can produce misleading topical signals without proving that the person used an immigration or passport service."),
    ("Standard banks and ownership", "A standard PIB describes a reusable government-wide record class. It is not evidence that every institution holds that person's information. Standard records often have no institution ID and therefore survive department selection. Work, correspondence, access requests and complaints require an actual institution/activity context; the current model does not bind every standard bank to that context."),
    ("Partial sources and absent results", "The denominator is the collected PIB inventory, not all federal holdings. Missing or rejected source pages, incomplete bilingual captures, aliases and poorly parsed titles can hide programs. Federal tax filing and federal voting currently have explicit inventory_gap options with no bank selectors. Asking these questions creates no direct tax/voting result. Institution responsibilities and a program's existence do not alone prove an applicable PIB or retention rule."),
    ("Timing vocabulary", "The engine accepts current, within_1_year, 1_to_3_years, 4_to_7_years, 8_to_15_years, more_than_15_years, approximate_year and unknown. Numeric intervals are respectively 0; 0–1; 1–3; 4–7; 8–15; 16+ years. Approximate year subtracts the year from the evaluation year. The shortcut's internal within_10_years means 0–10. Dates describe the latest interaction, which may differ from a file's retention trigger."),
    ("Retention decision order", "Missing/unknown timing gives retention_unknown, even for an indefinite rule. Otherwise indefinite retention gives likely_held unless immediate disposal is possible. Unknown, pending, institution-defined, schedule-defined or trigger-based rules give retention_unknown. Mixed immediate/indefinite branches also give unknown. Any reference event other than unspecified start, record creation/receipt or issue date gives unknown because the interaction date cannot establish closure, departure or another trigger."),
    ("Numeric retention decisions", "When the entire elapsed interval is beyond the published maximum: destruction yields likely_disposed, while transfer to archives yields likely_held. When the entire interval is strictly below the published minimum/fixed period, it yields likely_held. Boundary overlap and other numeric cases yield may_still_be_held. If several matched activities yield estimates, the engine chooses the most retention-preserving status: likely_held, then may_still_be_held, then unknown, then likely_disposed. These estimates are not confirmation of current holdings or completed destruction."),
    ("Review priorities", "Check each named selector against eligible population and actual activity; clarify multi-institution service delivery and archives; split broad Other branches where they overmatch; preserve specialist discoveries without asking everyone specialist questions; remove hidden quick-path coverage losses; repair source gaps before promising comprehensive coverage; and test plain-language English and French with people unfamiliar with government terminology."),
]


def render(review):
    doc = Document()
    doc.heading("My Info V1 — survey logic review", 1)
    doc.paragraph(f"Generated from checked-in contract {review['content_version']}. This is a review of existing behaviour, not a proposed redesign. The accompanying logic.json contains the complete contract views, selectors, source-linked inventory rows and input fingerprints; pib_mapping.csv supports spreadsheet review.")
    doc.heading("Coverage and reading guide")
    total = review["inventory_count"]
    doc.table(["Reachability (theoretical)", "PIBs", "Share"], [
        (name, review["coverage"].get(key, 0), f"{100 * review['coverage'].get(key, 0) / total:.1f}%")
        for key, name in [("direct", "Primary question or named route"), ("possible_only", "Candidate only; hidden in normal web"), ("not_discoverable", "No current route or question")]])
    doc.paragraph(f"Denominator: {total:,} collected inventory rows. This is a static upper bound before a person's answers and department restrictions. It does not measure accuracy, population prevalence or real-world recall. Question counts below overlap. Follow-up department lists are calculated from the Python engine for each option selected alone; multi-option selections can produce different lists.")
    for heading, paragraph in RULES:
        doc.heading(heading, 3)
        doc.paragraph(paragraph)
    doc.heading("Gate index")
    doc.table(["Order", "Gate", "Displayed English prompt", "Options", "Primary / candidate rows"], [
        (i, q["code"], q["en"]["prompt"], len(q["options"]), f"{len(q['primary_records'])} / {len(q['candidate_records'])}")
        for i, q in enumerate(review["questions"], 1)])
    for i, q in enumerate(review["questions"], 1):
        doc.html.append(f'<details class="gate"><summary>{i}. {escape(q["code"])} — {escape(q["en"]["prompt"])}</summary>')
        doc.heading(f"{i}. {q['code']}", 2, q["code"])
        doc.table(["Field", "Exact text / values"], [
            ("Displayed EN", q["en"]["prompt"]), ("Displayed FR", q["fr"]["prompt"]),
            ("Source EN before readability rewrite", q["source"]["question_en"]),
            ("Answers", ", ".join(q["en"]["answer_values"])),
            ("EN timing (non-route)", q["source"]["timing"]["prompt_en"]),
            ("FR timing (non-route)", q["source"]["timing"]["prompt_fr"]),
            ("EN help note", q["en"]["help"]["split_recommendation"]),
            ("FR help note", q["fr"]["help"]["split_recommendation"])])
        if q["route"]:
            doc.paragraph("Refinement EN: " + q["route"]["prompt_en"])
            doc.paragraph("Refinement FR: " + q["route"]["prompt_fr"])
            doc.paragraph("Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?")
        else:
            doc.paragraph("No named refinement: yes asks one timing question, then the department rule applies to the full primary-topic institution list below.")
        for o in q["options"]:
            doc.heading(o["code"], 3)
            departments = o["departments_if_selected_alone"]
            doc.table(["Field", "Value"], [
                ("EN answer", o["label_en"]), ("FR answer", o["label_fr"]),
                ("Implied institution EN", o["institution_en"]), ("Implied institution FR", o["institution_fr"]),
                ("Coverage label", o["coverage"]), ("Ask timing", str(o["ask_timing"])),
                ("Re-enable broad parent matches", str(o["fallback_to_parent"])),
                ("Exclusive selector required", str(o["exclusive"])),
                ("Exact selectors", ", ".join(o["selectors"]["bank_numbers"]) or "None"),
                ("Missing selector bank keys", ", ".join(o["missing_selectors"]) or "None"),
                ("Ask department if selected alone", str(o["department_followup_if_selected_alone"])),
                ("Department options EN / FR", "; ".join(f"{d['name_en']} / {d['name_fr']} [{d['institution_id']}]" for d in departments) or "None")])
            if o["matched_records"]:
                doc.table(["PIB selector", "Inventory holder", "PIB title EN / FR", "Source"], [
                    (r["bank_number_key"], r["institution_name_en"], r["title_en"] + " / " + r["title_fr"],
                     tuple((lang.upper(), r[f"source_url_{lang}"]) for lang in ("en", "fr") if r[f"source_url_{lang}"]))
                    for r in o["matched_records"]])
            else:
                doc.paragraph("No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.")
        doc.heading("Broad / Other department list", 3)
        ds = q["broad_department_options"]
        doc.table(["Institution ID", "EN", "FR"], [(d["institution_id"], d["name_en"], d["name_fr"]) for d in ds]) if ds else doc.paragraph("No primary-topic institution options.")
        doc.paragraph("All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.")
        doc.html.append("</details>")
    doc.heading("Provenance and regeneration")
    doc.paragraph("Run .venv/bin/python scripts/export_my_info_v1_review.py from the repository root. Review source evidence before treating any selector or keyword match as validated. Exact input hashes follow so this document's snapshot can be compared with future runtime changes.")
    doc.table(["Input", "SHA-256"], review["inputs"].items())
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>My Info V1 — survey logic review</title>
<style>body{font:17px/1.55 system-ui,sans-serif;color:#172b3a;max-width:1200px;margin:2rem auto;padding:0 1.2rem}h1,h2,h3{line-height:1.2}h2{margin-top:2rem}table{border-collapse:collapse;width:100%;font-size:.86rem}th,td{border:1px solid #bac6cd;padding:.55rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#edf3f6}.table-wrap{overflow-x:auto;margin:1rem 0}details{border:1px solid #8eacbb;padding:1rem;margin:1rem 0}summary{cursor:pointer;font-weight:650}a{color:#005ea8}button{padding:.65rem;margin:0 .5rem .5rem 0;font:inherit}nav{position:sticky;top:0;background:white;padding:.5rem 0;border-bottom:1px solid #ddd}@media print{body{font-size:10pt;max-width:none;margin:0}nav{display:none}details{border:0;padding:0;break-before:page}summary{display:none}table{font-size:8pt}tr{break-inside:avoid}.table-wrap{overflow:visible}a{color:inherit}h2,h3{break-after:avoid}}</style>
<nav aria-label="Document controls"><button type="button" onclick="document.querySelectorAll('details').forEach(x=>x.open=true)">Expand all questions</button><button type="button" onclick="document.querySelectorAll('details').forEach(x=>x.open=false)">Collapse all questions</button><button type="button" onclick="window.print()">Print / save PDF</button></nav><main>''' + "\n".join(doc.html) + '''</main><script>let saved=[];addEventListener('beforeprint',()=>{saved=[...document.querySelectorAll('details')].map(x=>x.open);document.querySelectorAll('details').forEach(x=>x.open=true)});addEventListener('afterprint',()=>document.querySelectorAll('details').forEach((x,i)=>x.open=saved[i]));</script></html>'''
    return "\n".join(doc.md), html


def main():
    engine = SurveyToolEngine()
    review = build_review(engine)
    markdown, html = render(review)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "README.md").write_text(markdown, encoding="utf-8")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / "logic.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    columns = ["record_id", "scope", "bank_number_key", "institution_name_en", "title_en", "title_fr", "reachability", "question_codes", "candidate_question_codes", "source_url_en", "source_url_fr"]
    with (OUT / "pib_mapping.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(review["records"])
    print(f"Exported {len(review['questions'])} gates, {sum(len(q['options']) for q in review['questions'])} options and {review['inventory_count']} PIB records to {OUT}")


if __name__ == "__main__":
    main()
