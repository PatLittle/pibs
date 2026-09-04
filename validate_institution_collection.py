#!/usr/bin/env python3
"""Validate institution source manifests, raw checksums, and table schemas."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from build_cor_table_from_markdown import OUT_COLUMNS as COR_COLUMNS
from build_pib_table_from_markdown import OUT_COLUMNS as PIB_COLUMNS
from collect_institution_content import ROLE_NAMES, load_jobs
from institution_extraction_versions import PARSER_VERSIONS


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def table_header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-file", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    completed = 0
    raw_files = 0
    for job in load_jobs(args.jobs_file):
        if not job.get("collectable"):
            continue
        folder = Path(str(job["content_folder"]))
        manifest_path = folder / "source_manifest.json"
        if not manifest_path.exists():
            errors.append(f"{job['institution_id']}: missing source manifest")
            continue
        completed += 1
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for field in ("institution_id", "registry_sha256", "snapshot_date"):
            if str(manifest.get(field, "")) != str(job[field]):
                errors.append(f"{job['institution_id']}: manifest {field} mismatch")
        if manifest.get("parser_versions") != PARSER_VERSIONS:
            errors.append(f"{job['institution_id']}: stale parser versions")

        for role in ROLE_NAMES:
            source = manifest.get("sources", {}).get(role, {})
            status = source.get("status")
            if status not in {"collected", "error", "missing_url"}:
                errors.append(f"{job['institution_id']} {role}: invalid status {status!r}")
                continue
            if status != "collected":
                continue
            raw_path = Path(str(source.get("raw_path", "")))
            markdown_path = Path(str(source.get("markdown_path", "")))
            if not raw_path.is_file():
                errors.append(f"{job['institution_id']} {role}: missing raw source {raw_path}")
            elif checksum(raw_path) != source.get("sha256"):
                errors.append(f"{job['institution_id']} {role}: raw checksum mismatch")
            else:
                raw_files += 1
            if not markdown_path.is_file():
                errors.append(f"{job['institution_id']} {role}: missing role Markdown")
            for discovered in source.get("discovered_pages", []):
                if discovered.get("status") == "error" or not discovered.get("raw_path"):
                    continue
                linked_path = Path(str(discovered["raw_path"]))
                if not linked_path.is_file():
                    errors.append(f"{job['institution_id']} {role}: missing discovered raw source")
                elif checksum(linked_path) != discovered.get("sha256"):
                    errors.append(f"{job['institution_id']} {role}: discovered checksum mismatch")
                else:
                    raw_files += 1

        for supplemental in manifest.get("supplemental_sources", []):
            source_id = str(supplemental.get("source_id", "")).strip() or "unnamed"
            label = f"{job['institution_id']} supplemental {source_id}"
            roles = supplemental.get("roles")
            if (
                not isinstance(roles, list)
                or not roles
                or any(role not in ROLE_NAMES for role in roles)
                or len(roles) != len(set(roles))
            ):
                errors.append(f"{label}: invalid roles {roles!r}")
            raw_path = Path(str(supplemental.get("raw_path", "")))
            markdown_path = Path(str(supplemental.get("markdown_path", "")))
            if not raw_path.is_file():
                errors.append(f"{label}: missing raw source {raw_path}")
            else:
                if raw_path.stat().st_size != supplemental.get("byte_count"):
                    errors.append(f"{label}: raw byte count mismatch")
                if checksum(raw_path) != supplemental.get("sha256"):
                    errors.append(f"{label}: raw checksum mismatch")
                else:
                    raw_files += 1
            if not markdown_path.is_file():
                errors.append(f"{label}: missing supplemental Markdown {markdown_path}")

        for filename, expected in (
            ("cor_table_en_fr.csv", COR_COLUMNS),
            ("pib_table_en_fr.csv", PIB_COLUMNS),
        ):
            path = folder / filename
            if not path.is_file():
                errors.append(f"{job['institution_id']}: missing {filename}")
            elif table_header(path) != expected:
                errors.append(f"{job['institution_id']}: invalid {filename} columns")

    if errors:
        raise SystemExit("Collection validation failed:\n- " + "\n- ".join(errors))
    print(
        f"Validated institution collection: completed={completed}, "
        f"raw_files={raw_files}, checksum_errors=0"
    )


if __name__ == "__main__":
    main()
