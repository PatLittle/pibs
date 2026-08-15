#!/usr/bin/env python3
"""Create deterministic, registry-driven per-institution collection jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd


REGISTRY = Path("institution_registry.csv")
OUTPUT_ROOT = Path("data/collection_jobs")
CONTENT_ROOT = Path("institutions_infosource_docs")


def clean(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_orgid(value: object) -> str:
    text = clean(value)
    return text[:-2] if re.fullmatch(r"\d+\.0", text) else text


def make_job(row: pd.Series, snapshot_date: str, registry_sha256: str) -> dict[str, object]:
    institution_id = clean(row["institution_id"])
    urls = {
        "pibs_en": clean(row.get("pibs_url_en")),
        "pibs_fr": clean(row.get("pibs_url_fr")),
        "classes_of_records_en": clean(row.get("classes_of_records_url_en")),
        "classes_of_records_fr": clean(row.get("classes_of_records_url_fr")),
    }
    return {
        "snapshot_date": snapshot_date,
        "registry_sha256": registry_sha256,
        "institution_id": institution_id,
        "gc_orgID": clean_orgid(row.get("gc_orgID")),
        "institution_name_en": clean(row.get("legal_name_en")),
        "institution_name_fr": clean(row.get("legal_name_fr")),
        "access_act_order": int(row["access_act_order"]),
        "content_folder": str(CONTENT_ROOT / institution_id),
        "collectable": any(urls.values()),
        "urls": urls,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--snapshot-date", default=date.today().isoformat())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    registry_bytes = args.registry.read_bytes()
    registry_sha256 = hashlib.sha256(registry_bytes).hexdigest()
    registry = pd.read_csv(args.registry).sort_values("access_act_order")
    jobs = [make_job(row, args.snapshot_date, registry_sha256) for _, row in registry.iterrows()]

    output = args.output or OUTPUT_ROOT / f"institution_collection_jobs_{args.snapshot_date}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(job, ensure_ascii=False, sort_keys=True) + "\n" for job in jobs),
        encoding="utf-8",
    )
    collectable = sum(bool(job["collectable"]) for job in jobs)
    print(f"Wrote {len(jobs)} jobs ({collectable} collectable) to {output}")


if __name__ == "__main__":
    main()
