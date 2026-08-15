#!/usr/bin/env python3
"""Compile registry-keyed institution PIB and Classes-of-Records tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import pandas as pd

from build_cor_table_from_markdown import OUT_COLUMNS as COR_COLUMNS
from build_pib_table_from_markdown import OUT_COLUMNS as PIB_COLUMNS
from pib_types import get_pib_type


CONTENT_ROOT = Path("institutions_infosource_docs")
SITE_ROOT = Path("site/data")
RELATED_RECORD_RE = re.compile(
    r"\b[A-Z]{2,8}(?:\s+[A-Z]{2,8})?\s+(?:\d{3}|\d+(?:\.\d+)+)\b", re.I
)


def load_jobs(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_table(path: Path, expected: list[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected:
            raise RuntimeError(f"Unexpected columns in {path}: {reader.fieldnames}; expected {expected}")
        return list(reader)


def write_table(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in columns} for row in rows)


def normalized_identifier(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").upper()).strip()


def build_pib_cor_links(
    pib_rows: list[dict[str, object]], cor_rows: list[dict[str, object]]
) -> list[dict[str, object]]:
    cor_exact = {
        (str(row["institution_id"]), normalized_identifier(row["record_number"])): str(row["record_number"])
        for row in cor_rows
    }
    cor_by_number: dict[tuple[str, str], list[str]] = {}
    for row in cor_rows:
        numbers = re.findall(r"\d+(?:\.\d+)*", str(row["record_number"]))
        if numbers:
            cor_by_number.setdefault((str(row["institution_id"]), numbers[-1]), []).append(
                str(row["record_number"])
            )
    standard_path = Path("standard_classes_of_records_en_fr.csv")
    standard: dict[str, str] = {}
    if standard_path.exists():
        for row in pd.read_csv(standard_path).fillna("").to_dict("records"):
            canonical = str(row["record_number"])
            standard[normalized_identifier(row["record_number_en"])] = canonical
            standard[normalized_identifier(row["record_number_fr"])] = canonical

    links: list[dict[str, object]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for pib in pib_rows:
        institution_id = str(pib["institution_id"])
        for language in ("en", "fr"):
            value = str(pib.get(f"related_record_number_{language}", "") or "")
            for match in RELATED_RECORD_RE.finditer(value):
                related = normalized_identifier(match.group(0))
                tokens = related.split()
                standard_index = next(
                    (index for index, token in enumerate(tokens) if token in {"PRN", "NDP"}), None
                )
                if standard_index is not None:
                    lookup = " ".join(tokens[standard_index:standard_index + 2])
                    scope = "standard"
                    resolved_to = standard.get(lookup, "")
                else:
                    scope = "institution_specific"
                    resolved_to = cor_exact.get((institution_id, related), "")
                    if not resolved_to:
                        numbers = re.findall(r"\d+(?:\.\d+)*", related)
                        candidates = cor_by_number.get((institution_id, numbers[-1]), []) if numbers else []
                        if len(candidates) == 1:
                            resolved_to = candidates[0]
                key = (institution_id, str(pib["bank_number_key"]), language, related)
                if key in seen:
                    continue
                seen.add(key)
                links.append({
                    "institution_id": institution_id,
                    "bank_number_key": pib["bank_number_key"],
                    "language": language,
                    "related_record_number": related,
                    "relationship_scope": scope,
                    "resolved": "true" if resolved_to else "false",
                    "cor_record_number": resolved_to,
                })
    return links


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-file", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    jobs = [job for job in load_jobs(args.jobs_file) if job.get("collectable")]
    cor_rows: list[dict[str, object]] = []
    pib_rows: list[dict[str, object]] = []
    missing: list[str] = []
    for job in jobs:
        folder = Path(str(job["content_folder"]))
        manifest_path = folder / "source_manifest.json"
        cor_path = folder / "cor_table_en_fr.csv"
        pib_path = folder / "pib_table_en_fr.csv"
        if not all(path.exists() for path in (manifest_path, cor_path, pib_path)):
            missing.append(str(job["institution_id"]))
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for field in ("snapshot_date", "registry_sha256", "institution_id"):
            if str(manifest.get(field, "")) != str(job[field]):
                raise RuntimeError(f"Stale or mismatched {field} in {manifest_path}")
        if manifest.get("parser_versions") != {"pibs": 4, "classes_of_records": 1}:
            raise RuntimeError(f"Stale parser versions in {manifest_path}; rebuild extractions first")
        identity = {
            "institution_id": job["institution_id"],
            "gc_orgID": job["gc_orgID"],
            "institution_name_en": job["institution_name_en"],
            "institution_name_fr": job["institution_name_fr"],
        }
        cor_rows.extend({**identity, **row} for row in read_table(cor_path, COR_COLUMNS))
        for row in read_table(pib_path, PIB_COLUMNS):
            pib_rows.append({
                **identity,
                **row,
                "pib_type": get_pib_type(
                    row.get("bank_number_key"), row.get("bank_number_en"), row.get("bank_number_fr")
                ),
            })

    if missing and not args.allow_incomplete:
        raise RuntimeError(f"Missing current outputs for {len(missing)} jobs: {missing}")

    cor_identity = ["institution_id", "gc_orgID", "institution_name_en", "institution_name_fr"]
    pib_columns = cor_identity + [PIB_COLUMNS[0], "pib_type", *PIB_COLUMNS[1:]]
    cor_columns = cor_identity + COR_COLUMNS
    link_columns = [
        "institution_id", "bank_number_key", "language", "related_record_number",
        "relationship_scope", "resolved", "cor_record_number",
    ]

    cor_keys = [(str(row["institution_id"]), str(row["record_number"]).casefold()) for row in cor_rows]
    pib_keys = [(str(row["institution_id"]), str(row["bank_number_key"]).casefold()) for row in pib_rows]
    for label, keys in (("COR", cor_keys), ("PIB", pib_keys)):
        duplicates = pd.Series(keys).duplicated(keep=False)
        if duplicates.any():
            values = pd.Series(keys)[duplicates].drop_duplicates().tolist()
            raise RuntimeError(f"Duplicate {label} canonical keys: {values[:20]}")

    link_rows = build_pib_cor_links(pib_rows, cor_rows)
    outputs = (
        (CONTENT_ROOT / "cor_table_en_fr_all.csv", cor_columns, cor_rows),
        (SITE_ROOT / "cor_table_en_fr_all.csv", cor_columns, cor_rows),
        (CONTENT_ROOT / "pib_table_en_fr_all.csv", pib_columns, pib_rows),
        (SITE_ROOT / "pib_table_en_fr_all.csv", pib_columns, pib_rows),
        (CONTENT_ROOT / "pib_cor_links.csv", link_columns, link_rows),
        (SITE_ROOT / "pib_cor_links.csv", link_columns, link_rows),
    )
    for path, columns, rows in outputs:
        write_table(path, columns, rows)
    print(
        f"Compiled {len(cor_rows)} classes and {len(pib_rows)} PIBs from "
        f"{len(jobs) - len(missing)}/{len(jobs)} institutions; "
        f"PIB-COR links={len(link_rows)}; missing={len(missing)}"
    )


if __name__ == "__main__":
    main()
