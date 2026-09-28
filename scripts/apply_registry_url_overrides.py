#!/usr/bin/env python3
"""Apply selected curated Info Source URL overrides to an existing registry snapshot.

This keeps the dated source snapshot and unrelated registry enrichments intact.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


URL_FIELDS = {
    "infosource_url_en_override": "infosource_url_en",
    "infosource_url_fr_override": "infosource_url_fr",
    "pibs_url_en_override": "pibs_url_en",
    "pibs_url_fr_override": "pibs_url_fr",
    "classes_url_en_override": "classes_of_records_url_en",
    "classes_url_fr_override": "classes_of_records_url_fr",
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("institution_registry.csv"))
    parser.add_argument("--overrides", type=Path, default=Path("data/institution_registry_overrides.csv"))
    parser.add_argument("--institution-id", action="append", required=True)
    args = parser.parse_args()

    fields, rows = read_rows(args.registry)
    _, override_rows = read_rows(args.overrides)
    overrides = {row["legal_name_en"]: row for row in override_rows}
    selected = set(args.institution_id)
    found: set[str] = set()
    for row in rows:
        institution_id = row["institution_id"]
        if institution_id not in selected:
            continue
        found.add(institution_id)
        override = overrides.get(row["legal_name_en"])
        if not override:
            raise SystemExit(f"Missing curated override: {institution_id}")
        for source_field, effective_field in URL_FIELDS.items():
            value = override[source_field].strip()
            if value:
                row[source_field] = value
                row[effective_field] = value
        for lang in ("en", "fr"):
            evidence = override[f"url_evidence_{lang}_override"].strip()
            if evidence:
                row[f"infosource_url_evidence_{lang}"] = evidence
    if missing := selected - found:
        raise SystemExit("Unknown institution IDs: " + ", ".join(sorted(missing)))
    with args.registry.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Applied curated URL overrides to {len(found)} institution rows")


if __name__ == "__main__":
    main()
