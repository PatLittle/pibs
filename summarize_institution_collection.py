#!/usr/bin/env python3
"""Summarize registry-driven institution collection and extraction coverage."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROLES = ("pibs_en", "pibs_fr", "classes_of_records_en", "classes_of_records_fr")


def load_jobs(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def table_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def error_class(message: str) -> str:
    text = message.casefold()
    if "404 client error" in text:
        return "http_404"
    if "403 client error" in text:
        return "http_403"
    if "400 client error" in text:
        return "http_400"
    if "certificate verify failed" in text or "sslerror" in text:
        return "tls_certificate"
    if "name or service not known" in text or "nameresolutionerror" in text:
        return "dns"
    if "timeout" in text or "timed out" in text:
        return "timeout"
    if "connection" in text:
        return "connection"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-file", type=Path, required=True)
    parser.add_argument("--status-csv", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    role_status = Counter()
    errors = Counter()
    failing_urls: set[str] = set()
    for job in load_jobs(args.jobs_file):
        folder = Path(str(job["content_folder"]))
        manifest_path = folder / "source_manifest.json"
        manifest = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.exists()
            else {}
        )
        sources = manifest.get("sources", {})
        statuses: dict[str, str] = {}
        for role in ROLES:
            source = sources.get(role, {})
            status = str(
                source.get(
                    "status", "not_run" if job.get("collectable") else "not_applicable"
                )
            )
            statuses[role] = status
            role_status[status] += 1
            if status == "error":
                errors[error_class(str(source.get("error", "")))] += 1
                if source.get("requested_url"):
                    failing_urls.add(str(source["requested_url"]))

        pibs = table_count(folder / "pib_table_en_fr.csv")
        classes = table_count(folder / "cor_table_en_fr.csv")
        extraction = manifest.get("extraction", {})
        pib_counts = extraction.get("pibs", {})
        cor_counts = extraction.get("classes_of_records", {})
        rows.append({
            "institution_id": job["institution_id"],
            "gc_orgID": job["gc_orgID"],
            "institution_name_en": job["institution_name_en"],
            "institution_name_fr": job["institution_name_fr"],
            "collectable": str(bool(job.get("collectable"))).lower(),
            "collection_completed": str(bool(manifest)).lower(),
            **{f"{role}_status": statuses[role] for role in ROLES},
            "source_error_count": sum(status == "error" for status in statuses.values()),
            "pibs_english": pib_counts.get("english", ""),
            "pibs_french": pib_counts.get("french", ""),
            "pibs_merged": pibs,
            "classes_of_records_english": cor_counts.get("english", ""),
            "classes_of_records_french": cor_counts.get("french", ""),
            "classes_of_records_merged": classes,
        })

    args.status_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.status_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    collectable_rows = [row for row in rows if row["collectable"] == "true"]
    completed_rows = [row for row in collectable_rows if row["collection_completed"] == "true"]
    summary = {
        "jobs_file": str(args.jobs_file),
        "registry_institutions": len(rows),
        "collectable_institutions": len(collectable_rows),
        "not_collectable_no_source_urls": len(rows) - len(collectable_rows),
        "collection_completed": len(completed_rows),
        "institutions_with_all_four_sources_collected": sum(
            all(row[f"{role}_status"] == "collected" for role in ROLES)
            for row in completed_rows
        ),
        "institutions_with_any_source_collected": sum(
            any(row[f"{role}_status"] == "collected" for role in ROLES)
            for row in completed_rows
        ),
        "institutions_with_no_source_collected": sum(
            not any(row[f"{role}_status"] == "collected" for role in ROLES)
            for row in completed_rows
        ),
        "role_status_counts": dict(sorted(role_status.items())),
        "source_error_classes": dict(sorted(errors.items())),
        "unique_failing_requested_urls": len(failing_urls),
        "institutions_with_pibs": sum(int(row["pibs_merged"]) > 0 for row in completed_rows),
        "institutions_with_classes_of_records": sum(
            int(row["classes_of_records_merged"]) > 0 for row in completed_rows
        ),
        "pib_rows": sum(int(row["pibs_merged"]) for row in completed_rows),
        "classes_of_records_rows": sum(
            int(row["classes_of_records_merged"]) for row in completed_rows
        ),
        "status_csv": str(args.status_csv),
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
