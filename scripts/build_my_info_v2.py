#!/usr/bin/env python3
"""Build the isolated V2 prototype and human-readable logic/coverage documents."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import csv
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from my_info.model import load_pib_records
from my_info_v2.catalog import ACTIVITIES, GROUPS
from my_info_v2.retention_rules import RULES

OUT = ROOT / "site/my_info_v2"
DATA = ROOT / "data/derived/my_info_v2"
DOCS = ROOT / "docs/my_info_v2"
QUICK = ["tax_return", "federal_vote", "passport", "border_crossing"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def source_context(institution_id, language):
    """Extract source context, never use it as a matching rule.

    Scan actual section headings, not menu occurrences. Keep the exact source
    excerpt and path for review; absence is an explicit gap.
    """
    folder = ROOT / "institutions_infosource_docs" / institution_id
    headings = (r"Responsibilities|Background|2\.1\.1 Benefits, Services, and Support" if language == "en"
                else r"Responsabilités|Contexte|Historique|2\.1\.1 Prestations, services et soutien")
    chunks = []
    for name in [f"classes_of_records_{language}.md", f"pibs_{language}.md", f"infosource_{language}.md"]:
        path = folder / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(rf"(?im)^#{{1,4}}\s+(?:{headings})\s*$", text):
            tail = text[match.end():]
            end = re.search(r"(?m)^#{1,4} ", tail)
            section = tail[:end.start()] if end else tail[:5000]
            paragraphs = [p.strip() for p in section.split("\n\n") if len(p.strip()) > 90 and not p.lstrip().startswith(("*", "+", "-", "[", "#"))]
            if paragraphs:
                excerpt = "\n\n".join(paragraphs[:3])
                chunks.append({"source_path": str(path.relative_to(ROOT)), "source_line": text[:match.start()].count("\n") + 1,
                               "heading": match.group(0).lstrip("# "), "excerpt": excerpt,
                               "sha256": sha256(path.read_bytes()).hexdigest()})
        if chunks:
            break
    return chunks[:2]


def build_runtime():
    registry = read_csv(ROOT / "institution_registry.csv")
    registry_by_id = {r["institution_id"]: r for r in registry}
    source = {r.record_id: r for r in load_pib_records(ROOT / "spib_en_fr.csv", ROOT / "institutions_infosource_docs/pib_table_en_fr_all.csv")}
    features = {r["record_id"]: r for r in read_csv(ROOT / "data/derived/my_info/my_info_pib_features.csv")}
    contract = json.loads((ROOT / "data/derived/my_info/my_info_questionnaire.json").read_text())
    categories = {c["category_id"]: c for c in contract["personal_information_categories"]}
    records = []
    for record_id, row in source.items():
        item = asdict(row)
        feature = features[record_id]
        for language in ["en", "fr"]:
            institution = registry_by_id.get(row.institution_id, {})
            item[f"source_url_{language}"] = (feature[f"source_url_{language}"]
                or institution.get(f"pibs_url_{language}")
                or institution.get(f"infosource_url_{language}", ""))
        item["categories"] = [categories[k] for k in feature["category_ids"].split("|") if k in categories]
        item["quality_flags"] = []
        if not row.class_of_individuals_en and not row.class_of_individuals_fr:
            item["quality_flags"].append("population_missing")
        if not row.purpose_en and not row.purpose_fr:
            item["quality_flags"].append("purpose_missing")
        if not row.title_en or row.title_en.lower().strip() in {"you are here", "you are here:"} or row.title_en.startswith(("Bank number", "– Bank Number")):
            item["quality_flags"].append("title_needs_review")
        records.append(item)

    institutions = []
    for row in registry:
        institution_id = row["institution_id"]
        institutions.append({"id": institution_id, "name_en": row["preferred_name"] or row["legal_name_en"],
                             "name_fr": row["nom_prefere"] or row["legal_name_fr"],
                             "source_url_en": row["infosource_url_en"], "source_url_fr": row["infosource_url_fr"],
                             "context_en": source_context(institution_id, "en"), "context_fr": source_context(institution_id, "fr")})
    known_institutions = {i["id"] for i in institutions}
    for record in records:
        if record["institution_id"] and record["institution_id"] not in known_institutions:
            institutions.append({"id": record["institution_id"], "name_en": record["institution_name_en"], "name_fr": record["institution_name_fr"], "context_en": [], "context_fr": [], "source_url_en": record["source_url_en"], "source_url_fr": record["source_url_fr"]})
            known_institutions.add(record["institution_id"])

    activities = []
    for definition in ACTIVITIES:
        item = dict(definition)
        item["source_evidence"] = []
        for record_id in item["record_ids"]:
            if record_id not in source:
                raise ValueError(f"Unknown exact selector: {record_id}")
            row = source[record_id]
            if item["scope"] == "choose_institution" and row.scope != "standard":
                raise ValueError("Generic institution routing cannot fan out to institutional records")
            for field in ["class_of_individuals_en", "purpose_en", "class_of_individuals_fr", "purpose_fr"]:
                value = getattr(row, field)
                if value:
                    item["source_evidence"].append({"record_id": record_id, "field": field, "quote": value})
            if not row.class_of_individuals_en and not row.class_of_individuals_fr:
                raise ValueError(f"Reviewed selector lacks population evidence: {record_id}")
        if item["scope"] == "inferred" and not item["institution_ids"]:
            raise ValueError(f"Named activity lacks an inferred institution: {item['id']}")
        activities.append(item)
    ids = [a["id"] for a in activities]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate activity IDs")
    for rule in RULES:
        if rule["source_quote"] not in getattr(source[rule["record_id"]], rule["source_field"]):
            raise ValueError(f"Retention source changed: {rule['record_id']}")
    guided = {r for activity in activities for r in activity["record_ids"]}
    coverage = {
        "inventory_rows": len(records), "distinct_bank_keys": len({r["bank_number_key"] for r in records}),
        "guided_record_count": len(guided), "guided_percent": round(100 * len(guided) / len(records), 1),
        "directory_record_count": len(records), "directory_only_count": len(records) - len(guided),
        "activities": len(activities), "groups": len(GROUPS), "scope_activities": sum(a["scope"] == "choose_institution" for a in activities),
        "source_gap_activities": [a["id"] for a in activities if a["coverage"] == "source_gap"],
        "needs_detail_activities": [a["id"] for a in activities if a["coverage"] == "needs_detail"],
        "reviewed_retention_rules": len(RULES), "institutions_with_context_en": sum(bool(i["context_en"]) for i in institutions),
        "institutions_with_context_fr": sum(bool(i["context_fr"]) for i in institutions),
        "source_quality_flags": dict(Counter(flag for r in records for flag in r["quality_flags"])),
    }
    return {"version": "2.0-prototype", "baseline_commit": "9aa3b07", "source_contract": contract["content_version"],
            "groups": [{"id": i, "label_en": en, "label_fr": fr} for i, en, fr in GROUPS],
            "activities": activities, "records": records, "institutions": sorted(institutions, key=lambda i: i["name_en"]),
            "retention_rules": RULES, "quick_activity_ids": QUICK, "coverage": coverage}


def documentation(runtime):
    by_id = {r["record_id"]: r for r in runtime["records"]}
    institutions = {i["id"]: i for i in runtime["institutions"]}
    stats = runtime["coverage"]
    lines = ["# My Info V2 — reviewable survey specification", "",
             "This is a separately deployed comparison prototype at /pibs/my_info_v2/. The original survey remains at /pibs/my_info/ with its existing logic.", "",
             "## Product promise and flow", "",
             "Find which federal organizations may have records about you, what those records describe, and where to ask. Start with activities you recognize; dates are optional.", "",
             "1. Choose recognized activities in eight expandable groups, use the optional common-four shortcut, or search by program/institution. Selecting a group only navigates; it never matches a PIB.",
             "2. A named program infers its source-supported organization. A generic request, contract or workplace interaction asks for the organization; 'not sure' is supported and never means all organizations.",
             "3. Show a short list of relevant published descriptions immediately. Distinguish selected activities, records personally reviewed in the directory, uncertain activities, and source gaps.",
             "4. Optionally refine retention using only reviewed source rules. Ask when the rule's event happened (release, launch, closure, last action), with 'not happened' and 'not sure'. Do not substitute an application date.",
             "5. Offer the full program directory and source links for specialist or indirect records. The person must review the eligible population before adding a directory record.", "",
             "## Coverage and burden", "",
             f"There are {stats['activities']} activity statements in {stats['groups']} expandable groups, not {stats['activities']} mandatory questions. Search/group navigation reduces the visible list; this still needs user testing for scanning effort.", "",
             f"The reviewed guided routes reach {stats['guided_record_count']} of {stats['inventory_rows']} inventory rows ({stats['guided_percent']}%). The directory exposes all {stats['directory_record_count']} rows; {stats['directory_only_count']} need program/role review there. **Directory access is not 100% automatic matching coverage.** V1's 597 direct-labelled rows include broad classifier/selector matches that have not had the same source review.", "",
             f"There are {stats['distinct_bank_keys']} distinct bank-number keys: publishing the same key under multiple institutions explains part of the {stats['inventory_rows']}-row total. V2 selectors use full institution-scoped record IDs.", "",
             f"Info Source mandate/program context was extracted for {stats['institutions_with_context_en']} institutions in English and {stats['institutions_with_context_fr']} in French. Missing context is explicit; extracted text assists navigation and never supplies a personal match.", "",
             f"Only {stats['reviewed_retention_rules']} source-checked single-event retention rules are executable in this prototype. Other published rules remain visible and uncertain. This intentionally exposes the remaining curation work.", "",
             "## Decision rules and edge cases", "",
             "- Every guided result requires an explicit activity/role selection and an exact reviewed record ID. Personal-information attributes such as passport number or health information cannot nominate a service.",
             "- Unknown veteran benefit identifies Veterans Affairs and asks for program detail in the result guidance; it cannot imply Agent Orange, education or income-replacement eligibility.",
             "- CAF application and Regular Force service are different activities. DND is inferred; a published transfer to Library and Archives Canada is explained as custody, never a redundant department question.",
             "- A common-four selection assigns a ten-year interval only to the selected activity occurrence. It never hides NEXUS, consular help, customs, consultations, or older events. Unchecked items are unreported, not lifetime negatives.",
             "- Voting is linked to ELECTIONS PPU 037 (registration/identification, not ballot choice). Tax filing still has no reviewed direct route in this collected inventory.",
             "- Generic complaints do not select every complaint bank. Ask the institution and then the complaint program. ERC 802 requires both RCMP membership and the specified referral under the former Act.",
             "- Standard PIBs describe reusable classes. Their potential owner is the institution the person selects; they never establish that every government organization has a copy.",
             "- Province-funded or federally funded services do not automatically imply a federal personal record. The program's actual population and collection purpose must support it.",
             "- Indirect records can be found through an explicit role (e.g. passport reference) or source review in the directory. Absence from guided results cannot establish absence from federal holdings.",
             "- No mandatory dates. Multi-branch/age/death/unspecified retention starts remain uncertain. Approximate years use a one-year margin; a boundary overlap stays uncertain. 'Period elapsed' is not evidence that destruction actually occurred.",
             "- A timing answer applies to the selected program and event only; it is not reused across unrelated episodes. Results concern the latest reported episode; older files can follow other timelines.",
             "- The bilingual prototype uses the same rule IDs. It requires fluent French review and public usability testing before a production release.", "",
             "## Reviewer checklist", "",
             "For every activity below, check vocabulary, eligible role, institution, exact PIB IDs, exclusions, source excerpt and retention event. The generated routing_ledger.csv and coverage.csv support spreadsheet review. Record proposed changes by activity ID or record ID.", "",
             "## Activity routing ledger", ""]
    panels = []
    ledger = []
    for a in runtime["activities"]:
        owner = "; ".join(institutions[i]["name_en"] for i in a["institution_ids"] if i in institutions) or "Ask which institution; unknown allowed"
        lines.extend([f"### {a['id']}", "", f"EN: {a['label_en']}", "", f"FR: {a['label_fr']}", "",
                      f"Institution: {owner}. Scope: {a['scope']}. Coverage: {a['coverage']}.", "", a["help_en"], ""])
        panel = [f"<details><summary>{escape(a['label_en'])}</summary><p lang='fr'>{escape(a['label_fr'])}</p><p><code>{escape(a['id'])}</code> · {escape(owner)} · {escape(a['coverage'])}</p><p>{escape(a['help_en'])}</p><p lang='fr'>{escape(a['help_fr'])}</p>"]
        for rid in a["record_ids"]:
            r = by_id[rid]
            lines.extend([f"- `{rid}` — {r['title_en']}", f"  - Population: {r['class_of_individuals_en']}", f"  - Purpose: {r['purpose_en']}", f"  - Source: {r['source_url_en']}", ""])
            panel.append(f"<h4>{escape(r['bank_number_key'])} · {escape(r['title_en'])}</h4><p><b>Population:</b> {escape(r['class_of_individuals_en'])}</p><p><b>Purpose:</b> {escape(r['purpose_en'])}</p><p lang='fr'><b>Population :</b> {escape(r['class_of_individuals_fr'])}</p><p lang='fr'><b>Fin :</b> {escape(r['purpose_fr'])}</p><p><a href='{escape(r['source_url_en'], quote=True)}'>English source</a> · <a href='{escape(r['source_url_fr'], quote=True)}'>Source française</a></p>")
            ledger.append({"activity_id": a["id"], "label_en": a["label_en"], "label_fr": a["label_fr"], "scope": a["scope"], "record_id": rid, "population_en": r["class_of_individuals_en"], "purpose_en": r["purpose_en"], "source_url_en": r["source_url_en"], "source_url_fr": r["source_url_fr"]})
        panel.append("</details>")
        panels.append("".join(panel))
    lines.extend(["## Retention rule ledger", "", "Only the following reviewed single-event rules are executable. Other source schedules remain readable, with no automatic date conclusion.", ""])
    for rule in runtime["retention_rules"]:
        lines.extend([f"### {rule['record_id']}", "", f"Event: {rule['event_label_en']} / {rule['event_label_fr']}", "",
                      f"Disposition model: {rule['mode']}; period: {rule['years']} years.", "", f"Source: {rule['source_quote']}", ""])
    lines.extend(["## Acceptance cases", "", "Use [ACCEPTANCE_CASES.md](ACCEPTANCE_CASES.md) for reviewer stories and the public-release checklist.", ""])
    lines.extend(["## Source context", "", "These are extracted local snapshot excerpts. They are navigation context, not personal-record matching evidence.", ""])
    for i in runtime["institutions"]:
        if not i["context_en"] and not i["context_fr"]:
            continue
        lines.extend([f"### {i['name_en']}", ""])
        for lang in ["en", "fr"]:
            for c in i[f"context_{lang}"]:
                lines.extend([f"{lang.upper()} — `{c['source_path']}:{c['source_line']}` — {c['heading']}", "", c["excerpt"], ""])
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "REVIEW.md").write_text("\n".join(line.rstrip() for line in lines), encoding="utf-8")
    (DOCS / "routing_ledger.csv").write_text("", encoding="utf-8")
    with (DOCS / "routing_ledger.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(ledger[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(ledger)
    document = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>My Info V2 logic review</title><style>body{{font:17px/1.55 system-ui;max-width:1100px;margin:auto;padding:32px;color:#172c3b}}h1,h2{{line-height:1.2}}details{{border:1px solid #b8c9ce;border-radius:8px;padding:18px;margin:12px 0}}summary{{font-weight:650;cursor:pointer}}code{{overflow-wrap:anywhere}}.metrics{{background:#eaf4f0;padding:20px}}@media print{{details>*{{display:block!important}}summary{{list-style:none}}button,input{{display:none}}}}</style><h1>My Info V2 · logic review</h1><p>Activity → eligible role and program → exact record and organization → optional retention event.</p><p>This is an isolated comparison prototype. The full rationale, source context and edge cases are in <a href="REVIEW.md">REVIEW.md</a>; use the <a href="routing_ledger.csv">routing spreadsheet</a> for detailed comments.</p><div class="metrics">{stats['activities']} activities in {stats['groups']} groups · {stats['guided_record_count']} reviewed guided records · {stats['directory_record_count']} browsable records · {stats['reviewed_retention_rules']} executable retention rules</div><p>Guided and browsable coverage are different. A known program infers its organization. Uncertain activities produce a clarification, not every possible PIB. Dates are optional and must describe the event in the source rule.</p><button onclick="document.querySelectorAll('details').forEach(e=>e.open=true)">Expand all for review</button> <button onclick="document.querySelectorAll('details').forEach(e=>e.open=true);window.print()">Print</button><p><label>Find an activity <input id="filter" type="search"></label></p>{''.join(panels)}<h2>Retention ledger</h2>{''.join(f'<p><code>{escape(r["record_id"])}</code> — {escape(r["event_label_en"])} — {r["mode"]}, {r["years"]} years.<br>{escape(r["source_quote"])}</p>' for r in runtime['retention_rules'])}<script>document.querySelector('#filter').addEventListener('input',e=>document.querySelectorAll('details').forEach(d=>d.hidden=!d.textContent.toLowerCase().includes(e.target.value.toLowerCase())));</script></html>"""
    (DOCS / "index.html").write_text(document, encoding="utf-8")
    mappings = {r["record_id"]: [] for r in runtime["records"]}
    for activity in runtime["activities"]:
        for rid in activity["record_ids"]:
            mappings[rid].append(activity["id"])
    with (DOCS / "coverage.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["record_id", "bank", "title_en", "guided_activities", "discovery", "quality_flags"], lineterminator="\n")
        writer.writeheader()
        for r in runtime["records"]:
            writer.writerow({"record_id": r["record_id"], "bank": r["bank_number_key"], "title_en": r["title_en"], "guided_activities": "|".join(mappings[r["record_id"]]), "discovery": "guided_and_directory" if mappings[r["record_id"]] else "directory_requires_review", "quality_flags": "|".join(r["quality_flags"])})


def main():
    runtime = build_runtime()
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (DATA / "coverage.json").write_text(json.dumps(runtime["coverage"], indent=2) + "\n")
    (DATA / "activities.json").write_text(json.dumps(runtime["activities"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA / "program_context.json").write_text(json.dumps(runtime["institutions"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "runtime.json").write_text(json.dumps(runtime, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copy2(ROOT / "my_info_v2/engine.mjs", OUT / "engine.mjs")
    for name in ["index.html", "app.mjs", "styles.css"]:
        shutil.copy2(ROOT / "my_info_v2/web" / name, OUT / name)
    documentation(runtime)
    for name in ["index.html", "REVIEW.md", "routing_ledger.csv", "coverage.csv", "ACCEPTANCE_CASES.md"]:
        destination = OUT / "review" / name
        destination.parent.mkdir(exist_ok=True)
        shutil.copy2(DOCS / name, destination)
    print(json.dumps(runtime["coverage"], indent=2))


if __name__ == "__main__":
    main()
