"""Link the Chart to year-scoped key projections from three GC InfoBase resources."""

import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict

from scripts.service_graph import source_record

SOURCE = "data/public_accounts/infobase-2526-keys.json.gz"
DATASET = "https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f"
RESOURCE_LABELS = {
    "spending_fte": "Expenditures and FTE by program",
    "performance": "Performance by program and organization",
    "federal_programs": "Federal Programs",
}


def infobase_number(value):
    match = re.fullmatch(r"(\d+)(?:\.0+)?", value.strip())
    return str(int(match[1])) if match else ""


def link_program_keys(root, registry, targets, fiscal_yr):
    raw = (root / SOURCE).read_bytes()
    snapshot = json.loads(gzip.decompress(raw))
    if snapshot["fiscal_yr"] != fiscal_yr:
        raise ValueError("GC InfoBase keys are from a different fiscal year")

    by_infobase = defaultdict(list)
    for row in registry:
        number = infobase_number(row["infobaseID"])
        if number:
            by_infobase[number].append(row["institution_id"])
    links, audit = [], {}
    for resource in snapshot["resources"]:
        outcomes = Counter()
        kind = resource["kind"]
        if sum(row[4] for row in resource["keys"]) + resource["blank_rows"] != resource["source_rows"]:
            raise ValueError(f"GC InfoBase key counts do not match the source snapshot: {kind}")
        for org, code, activity_type, program_id, count in resource["keys"]:
            organizations = by_infobase[infobase_number(org)]
            if len(organizations) != 1:
                outcomes["unresolved_infobase_org"] += 1
                continue
            institution = organizations[0]
            possible = targets.get((institution, code), [])
            if len(possible) != 1:
                outcomes["ambiguous_chart_code" if possible else "no_chart_code_for_owner"] += 1
                continue
            chart, department = possible[0]
            if activity_type and chart["code_kind"] != activity_type:
                outcomes["activity_type_mismatch"] += 1
                continue
            filters = {
                resource["yearName"]: resource["yearValue"],
                resource["organization"]: int(org) if kind == "federal_programs" else org,
                resource["code"]: code,
            }
            if program_id:
                filters["id"] = int(program_id)
            if kind == "performance":
                filters["activity_level"] = activity_type.replace("_", " ").title()
            links.append(dict(
                fiscal_yr=fiscal_yr, resource_kind=kind, infobase_org_id=org, program_code=code,
                activity_type=activity_type, source_program_id=program_id, source_rows=count,
                accounts_entity=chart["accounts_entity"], institution_id=institution,
                department_number=department["department_number"], resource_id=resource["id"],
                source_code_field=resource["code"],
                source_url=source_record(resource["id"], filters),
            ))
            outcomes["linked"] += 1
        audit[kind] = dict(
            resource_id=resource["id"], source_year_field=resource["yearName"],
            source_year_value=resource["yearValue"], source_rows=resource["source_rows"],
            rows_without_key=resource["blank_rows"], distinct_keys=len(resource["keys"]),
            outcomes=dict(outcomes),
        )

    def key(row):
        return row["resource_kind"], row["infobase_org_id"], row["program_code"]

    counts = Counter(map(key, links))
    ambiguous = {k for k, count in counts.items() if count > 1}
    for candidate in ambiguous:
        outcomes = audit[candidate[0]]["outcomes"]
        outcomes["ambiguous_source_key"] = outcomes.get("ambiguous_source_key", 0) + counts[candidate]
    links = [r for r in links if key(r) not in ambiguous]
    for kind, resource_audit in audit.items():
        resource_audit["outcomes"]["linked"] = sum(r["resource_kind"] == kind for r in links)
    return links, dict(
        source_path=SOURCE, snapshot_sha256=hashlib.sha256(raw).hexdigest(),
        retrieved_on=snapshot["retrieved_on"], resources=audit,
    )
