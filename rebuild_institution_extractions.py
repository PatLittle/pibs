#!/usr/bin/env python3
"""Re-run current PIB and COR parsers over collected institution Markdown."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from build_cor_table_from_markdown import parse_records as parse_cor_records
from build_cor_table_from_markdown import process_folder as process_cor_folder
from build_pib_table_from_markdown import parse_records as parse_pib_records
from build_pib_table_from_markdown import process_folder as process_pib_folder
from collect_institution_content import (
    convert_to_markdown,
    load_jobs,
    same_site_namespace,
)


def rebuild_markdown_from_raw(folder: Path, manifest: dict[str, object]) -> None:
    """Replay current crawl boundaries from immutable raw snapshots."""
    parsers = {
        "pibs_en": parse_pib_records,
        "pibs_fr": parse_pib_records,
        "classes_of_records_en": parse_cor_records,
        "classes_of_records_fr": parse_cor_records,
    }
    for role, parser in parsers.items():
        source = manifest.get("sources", {}).get(role, {})
        markdown_path = folder / f"{role}.md"
        if source.get("status") != "collected":
            markdown_path.write_text("", encoding="utf-8")
            continue
        raw_path = Path(str(source["raw_path"]))
        if not raw_path.exists():
            raise RuntimeError(f"Missing immutable raw source: {raw_path}")
        primary = convert_to_markdown(
            raw_path,
            raw_path.read_bytes(),
            str(source.get("content_type", "")),
            str(source.get("fragment", "")),
            str(source.get("encoding", "")),
        )
        linked: list[str] = []
        initial_url = str(source.get("final_url", source.get("requested_url", "")))
        for discovered in source.get("discovered_pages", []):
            candidate_url = str(discovered.get("final_url", discovered.get("url", "")))
            include = (
                discovered.get("status") != "error"
                and same_site_namespace(initial_url, candidate_url)
                and bool(discovered.get("raw_path"))
                and Path(str(discovered.get("raw_path"))).exists()
            )
            discovered["included_in_extraction"] = include
            if include:
                linked_path = Path(str(discovered["raw_path"]))
                linked.append(
                    convert_to_markdown(
                        linked_path,
                        linked_path.read_bytes(),
                        "text/html",
                        "",
                        "",
                    )
                )
        combined = "\n\n".join([primary, *linked])
        markdown = combined if linked and len(parser(combined)) > len(parser(primary)) else primary
        markdown_path.write_text(markdown, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-file", type=Path, required=True)
    parser.add_argument(
        "--extractions-only",
        action="store_true",
        help="Reparse existing role Markdown without replaying immutable raw snapshots.",
    )
    args = parser.parse_args()
    jobs = [job for job in load_jobs(args.jobs_file) if job.get("collectable")]
    rebuilt = 0
    missing = []
    for job in jobs:
        folder = Path(str(job["content_folder"]))
        manifest_path = folder / "source_manifest.json"
        if not manifest_path.exists():
            missing.append(str(job["institution_id"]))
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not args.extractions_only:
            rebuild_markdown_from_raw(folder, manifest)
        _, pib_en, pib_fr, pib_merged = process_pib_folder(folder)
        cor_en, cor_fr, cor_merged = process_cor_folder(folder)
        manifest["extraction"] = {
            "pibs": {"english": pib_en, "french": pib_fr, "merged": pib_merged},
            "classes_of_records": {"english": cor_en, "french": cor_fr, "merged": cor_merged},
        }
        manifest["parser_versions"] = {"pibs": 4, "classes_of_records": 1}
        manifest["extraction_rebuild_version"] = 2
        manifest["extracted_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rebuilt += 1
    print(f"Rebuilt {rebuilt}/{len(jobs)} institution outputs; missing={len(missing)}")
    if missing:
        print("Missing institution IDs: " + ", ".join(missing))


if __name__ == "__main__":
    main()
