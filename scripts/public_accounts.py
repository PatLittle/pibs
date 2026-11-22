"""Model the 2025–2026 Chart of Accounts and join observed service program codes."""

import csv
import gzip
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

from scripts import infobase_program_keys
from scripts.service_graph import program_id, service_id, source_record, SERVICE_RESOURCE

FISCAL_YEAR = "2025-2026"
SOURCE = "data/public_accounts/cp-pc-2526-eng.csv.gz"
RESOURCE = (
    "https://open.canada.ca/data/en/dataset/3c371e57-d487-49fa-bb0d-352ae8dd6e4e"
    "/resource/467a253b-fd0e-4123-acb3-7641252d8ffe"
)
SUPPORT = "https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/soutien-support-eng.html"
INVENTORY = "data/service_inventory/"
EXPORTS = {
    "codes": "public-accounts-codes.csv",
    "departments": "public-accounts-departments.csv",
    "services": "public-accounts-service-links.csv",
    "catalogue": "public-accounts-catalogue-links.csv",
    "infobase": "public-accounts-infobase-links.csv",
}
SOURCE_FIELDS = {
    "Min-portfolio_Portefeuille-min_eng": "portfolio_en",
    "Other-than-budgetary-expenditures_Autres-que-depenses-budgetaires_eng": "expenditure_category_en",
    "Entity_Entite_eng": "accounts_entity",
    "Prog-core-resp-code_Code-prog-resp-essent": "core_code",
    "Prog-core-resp-name_Nom-prog-resp-essent_eng": "core_name_en",
    "Prog-core-resp-desc_Desc-prog-resp-essent_eng": "core_description_en",
    "Prog-inv-code_Code-rep-prog": "program_id",
    "Prog-inv-name_Nom-rep-prog_eng": "program_name_en",
    "Prog-inv-desc_Desc-rep-prog_eng": "program_description_en",
    "Notes_eng": "notes_en",
    "Dept-specific_Particulier-au-min_eng": "department_specific_en",
}
DEPARTMENT_ENTRY = re.compile(r"(?:-\s*)?(\d{3})\s+-\s+(.+)")


def csv_rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def registry_number(value):
    """Read a three-character RG number from a registry CSV numeric string."""
    match = re.fullmatch(r"(\d{1,3})(?:\.0+)?", value.strip())
    return match[1].zfill(3) if match else ""


def department_entries(value):
    """Expand every semicolon-delimited department number without losing zeros."""
    for entry in value.split(";") if value else ():
        match = DEPARTMENT_ENTRY.fullmatch(entry.strip())
        if not match:
            raise ValueError(f"Unrecognized department entry: {entry!r}")
        yield match[1], match[2]


def entity_name(value):
    """Normalize the publisher's front/back placement of 'Department of/for'."""
    value = " ".join(value.casefold().split())
    value = re.sub(r"^department (?:of|for) (?:the )?", "", value)
    return re.sub(r" \(department (?:of|for)(?: the)?\)$", "", value)


def build(root, registry, read):
    raw = gzip.decompress((root / SOURCE).read_bytes())
    source_sha = hashlib.sha256(raw).hexdigest()
    source = csv_rows(raw)
    if not source or set(source[0]) != SOURCE_FIELDS.keys():
        raise ValueError("Unexpected Chart of Accounts CSV header")

    by_number = defaultdict(list)
    for row in registry:
        number = registry_number(row["rg"])
        if number:
            by_number[number].append(row)

    codes, departments = {}, {}
    for ordinal, original in enumerate(source, 1):
        row = {name: original[field] for field, name in SOURCE_FIELDS.items()}
        entity = row["accounts_entity"]
        if not entity or not row["core_code"]:
            raise ValueError(f"Missing entity or core code in source record {ordinal}")

        def add_code(prefix, record_kind, parent=""):
            code = row["program_id"] if prefix == "program" else row["core_code"]
            record = dict(
                fiscal_yr=FISCAL_YEAR, accounts_entity=entity, account_code=code,
                code_kind=record_kind, parent_code=parent, name_en=row[prefix + "_name_en"],
                description_en=row[prefix + "_description_en"], portfolio_en=row["portfolio_en"],
                expenditure_category_en=row["expenditure_category_en"],
                department_specific_en=row["department_specific_en"],
            )
            current = codes.setdefault((entity, code), (record, [], set()))
            if current[0] != record or (prefix == "program" and current[1]):
                raise ValueError(f"Conflicting Chart of Accounts code record: {entity}, {code}")
            current[1].append(ordinal)
            if row["notes_en"]:
                current[2].add(row["notes_en"])

        add_code("core", "non_budgetary" if row["expenditure_category_en"] else "core_responsibility")
        if row["program_id"]:
            add_code("program", "program", row["core_code"])

        for number, label in department_entries(row["department_specific_en"]):
            candidates = by_number[number]
            target = candidates[0] if len(candidates) == 1 else None
            labels = [label]
            if target:
                labels.extend(target[k] for k in (
                    "legal_name_en", "harmonized_name", "preferred_name", "open_canada_title_en",
                ) if target.get(k))
            record = dict(
                fiscal_yr=FISCAL_YEAR, accounts_entity=entity, department_number=number,
                department_label_en=label, institution_id=target["institution_id"] if target else "",
                resolution="resolved" if target else "ambiguous" if candidates else "unmatched",
                entity_matches_department="true" if entity_name(entity) in map(entity_name, labels) else "false",
                candidate_institutions=sorted(r["institution_id"] for r in candidates),
            )
            current = departments.setdefault((entity, number), (record, []))
            if current[0] != record:
                raise ValueError(f"Conflicting department labels for {entity}, {number}")
            current[1].append(ordinal)

    code_rows = [
        dict(record, source_records=ordinals, notes_en=sorted(notes))
        for record, ordinals, notes in codes.values()
    ]
    department_rows = [dict(record, source_records=ordinals) for record, ordinals in departments.values()]
    entity_codes = defaultdict(list)
    for row in code_rows:
        if row["code_kind"] != "non_budgetary":
            entity_codes[row["accounts_entity"]].append(row)
    targets = defaultdict(list)
    for link in department_rows:
        if link["institution_id"] and link["entity_matches_department"] == "true":
            for code in entity_codes[link["accounts_entity"]]:
                targets[link["institution_id"], code["account_code"]].append((code, link))

    owners = {r["owner_org"]: r["institution_id"] for r in read(INVENTORY + "organizations.csv", True)}
    service_links, unresolved = [], []
    same_year = [
        row for row in read(INVENTORY + "program_references.csv", True)
        if row["fiscal_yr"] == FISCAL_YEAR
    ]
    for row in same_year:
        owner, service, program = (row[k] for k in ("owner_org", "service_id", "program_id"))
        institution = owners.get(owner, "")
        lookup = targets[institution, program]
        if len(lookup) == 1:
            code, department = lookup[0]
            service_links.append(dict(
                fiscal_yr=FISCAL_YEAR, owner_org=owner, service_id=service, program_id=program,
                accounts_entity=code["accounts_entity"], institution_id=institution,
                department_number=department["department_number"],
            ))
        else:
            unresolved.append(dict(row, institution_id=institution, chart_status=(
                "unmapped_service_owner" if not institution else
                "ambiguous_chart_code" if lookup else "no_matching_chart_code_for_owner"
            )))

    distinct_year_matches = {(row["owner_org"], row["program_id"]) for row in service_links}
    catalogue_links = []
    for row in read(INVENTORY + "programs.csv", True):
        owner, program = row["owner_org"], row["program_id"]
        institution = owners.get(owner, "")
        lookup = targets[institution, program]
        if len(lookup) == 1:
            code, department = lookup[0]
            catalogue_links.append(dict(
                fiscal_yr=FISCAL_YEAR, owner_org=owner, program_id=program,
                accounts_entity=code["accounts_entity"], institution_id=institution,
                department_number=department["department_number"],
            ))
    infobase_links, infobase_audit = infobase_program_keys.link_program_keys(root, registry, targets, FISCAL_YEAR)
    audit = dict(
        fiscal_yr=FISCAL_YEAR, source_url=RESOURCE, documentation_url=SUPPORT,
        source_sha256=source_sha, source_rows=len(source), source_fields=list(SOURCE_FIELDS),
        codes_by_kind=dict(Counter(row["code_kind"] for row in code_rows)),
        department_numbers=len({row["department_number"] for row in department_rows}),
        department_links=dict(Counter(row["resolution"] for row in department_rows)),
        resolved_institutions=len({row["institution_id"] for row in department_rows} - {""}),
        same_year_service_references=len(same_year), resolved_service_references=len(service_links),
        services_with_chart_codes=len({(row["owner_org"], row["service_id"]) for row in service_links}),
        owner_program_pairs_with_same_year_evidence=len(distinct_year_matches),
        shared_service_catalogue_codes=len(catalogue_links),
        unresolved_service_references=unresolved,
        infobase=infobase_audit,
    )
    return dict(
        codes=code_rows, departments=department_rows, services=service_links,
        catalogue=catalogue_links, infobase=infobase_links, audit=audit,
    )


def write(root):
    root = Path(root)

    def read(path, table=False):
        raw = (root / path).read_bytes()
        return csv_rows(raw) if table else json.loads(raw)

    data = build(root, read("institution_registry.csv", True), read)
    output = root / "site/data"
    output.mkdir(parents=True, exist_ok=True)
    for group, path in EXPORTS.items():
        rows = data[group]
        with (output / path).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows({
                key: json.dumps([str(v) for v in item], ensure_ascii=False) if isinstance(item, list) else item
                for key, item in row.items()
            } for row in rows)
    (output / "public-accounts-join-audit.json").write_text(
        json.dumps(data["audit"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )


def account_id(entity, code):
    return "account-code:" + FISCAL_YEAR + ":" + quote(entity, safe="") + ":" + quote(code, safe="")


def add_to_graph(data, add_node, add_edge):
    departments = defaultdict(list)
    for row in data["departments"]:
        departments[row["accounts_entity"]].append(row)
    codes = {(row["accounts_entity"], row["account_code"]): row for row in data["codes"]}
    audit = data["audit"]

    def evidence(row, field, mention, method):
        return dict(
            source_path=SOURCE, source_url=RESOURCE, source_sha256=audit["source_sha256"],
            fiscal_yr=FISCAL_YEAR, accounts_entity=row["accounts_entity"],
            source_records=row["source_records"], field=field, mention=mention, method=method,
        )

    for (entity, code), row in codes.items():
        links = departments[entity]
        institution_ids = {
            link["institution_id"] for link in links
            if link["institution_id"] and link["entity_matches_department"] == "true"
        }
        add_node(dict(
            id=account_id(entity, code), type="account_code", identifier=code,
            institution_id=next(iter(institution_ids)) if len(institution_ids) == 1 else None,
            label_en=row["name_en"], label_fr="", description_en=row["description_en"],
            aliases=[entity, FISCAL_YEAR, *(link["department_number"] for link in links)],
            sources={"chart_of_accounts": RESOURCE}, record_url=RESOURCE, source_path=SOURCE,
            attributes=dict(row, department_links=links, source_language="en"),
        ))

    for (entity, code), row in codes.items():
        ident = account_id(entity, code)
        if row["parent_code"]:
            add_edge(ident, account_id(entity, row["parent_code"]), "account_core_responsibility", [
                evidence(row, "Prog-core-resp-code_Code-prog-resp-essent", row["parent_code"], "same_chart_source_row"),
            ])
        for link in departments[entity]:
            if link["institution_id"]:
                add_edge(ident, "institution:" + link["institution_id"], "accounted_by", [
                    dict(evidence(row, "Dept-specific_Particulier-au-min_eng",
                                  link["department_number"], "unique_registry_receiver_general_number"),
                         registry_field="rg", registry_source_path="institution_registry.csv",
                         department_label_en=link["department_label_en"],
                         entity_matches_department=link["entity_matches_department"] == "true"),
                ])

    for group in ("services", "catalogue"):
        for link in data[group]:
            owner, code = link["owner_org"], link["program_id"]
            chart = codes[link["accounts_entity"], code]
            inventory_path = INVENTORY + ("program_references.csv" if group == "services" else "programs.csv")
            item = dict(
                evidence(chart, "program_id", code, "chart_code_and_scoped_receiver_general_number"),
                owner_org=owner, department_number=link["department_number"],
                institution_id=link["institution_id"], inventory_source_path=inventory_path,
            )
            if group == "services":
                service = link["service_id"]
                item["service_id"] = service
                item["inventory_source_url"] = source_record(
                    SERVICE_RESOURCE, dict(owner_org=owner, fiscal_yr=FISCAL_YEAR, service_id=service),
                )
                add_edge(service_id(owner, service), account_id(link["accounts_entity"], code),
                         "reports_account_code", [item])
            else:
                item["comparison"] = "catalogue_code_only"
                add_edge(program_id(owner, code), account_id(link["accounts_entity"], code),
                         "shares_account_code", [item])

    infobase_by_program = defaultdict(list)
    for row in data["infobase"]:
        infobase_by_program[row["infobase_org_id"], row["program_code"]].append(row)
    for (org, code), rows in infobase_by_program.items():
        first = rows[0]
        chart = codes[first["accounts_entity"], code]
        ident = f"infobase-program:{FISCAL_YEAR}:{quote(org, safe='')}:{quote(code, safe='')}"
        sources = {infobase_program_keys.RESOURCE_LABELS[row["resource_kind"]]: row["source_url"] for row in rows}
        add_node(dict(
            id=ident, type="infobase_program", identifier=code, institution_id=first["institution_id"],
            label_en=chart["name_en"], label_fr="", aliases=[chart["accounts_entity"], FISCAL_YEAR, org],
            sources=sources, source_path=infobase_program_keys.SOURCE,
            record_url=sources.get("Federal Programs", next(iter(sources.values()))),
            attributes=dict(
                fiscal_yr=FISCAL_YEAR, infobase_org_id=org, program_code=code, label_source=RESOURCE,
                infobase_resources=[dict(row, label_en=infobase_program_keys.RESOURCE_LABELS[row["resource_kind"]]) for row in rows],
            ),
        ))
        add_edge(account_id(chart["accounts_entity"], code), ident, "matches_infobase_program", [
            dict(
                source_path=infobase_program_keys.SOURCE, source_url=row["source_url"],
                source_sha256=audit["infobase"]["snapshot_sha256"], field=row["source_code_field"], mention=code,
                method="same_year_code_and_dual_registry_identifiers", chart_source_url=RESOURCE,
                fiscal_yr=FISCAL_YEAR, infobase_org_id=org, department_number=row["department_number"],
                resource_id=row["resource_id"], institution_id=row["institution_id"],
            )
            for row in rows
        ])


if __name__ == "__main__":
    write(Path(__file__).resolve().parents[1])
