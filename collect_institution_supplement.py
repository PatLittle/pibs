#!/usr/bin/env python3
"""Collect a dated, provenance-preserving supplemental Info Source page."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from collect_institution_content import (
    ROLE_NAMES,
    content_extension,
    convert_to_markdown,
    rejected_response,
    session,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--institution-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--role", action="append", required=True, choices=ROLE_NAMES)
    parser.add_argument("--snapshot-date", required=True)
    parser.add_argument("--provenance", required=True)
    args = parser.parse_args()

    folder = Path("institutions_infosource_docs") / args.institution_id
    manifest_path = folder / "source_manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing canonical source manifest: {manifest_path}")

    response = session().get(args.url, allow_redirects=True, timeout=(15, 75))
    response.raise_for_status()
    if rejected_response(response.content):
        raise SystemExit("Upstream returned a request-rejection page")

    content_type = response.headers.get("content-type", "")
    extension = content_extension(content_type, response.url)
    output = folder / "snapshots" / args.snapshot_date / "supplemental" / args.source_id
    output.mkdir(parents=True, exist_ok=True)
    raw_path = output / f"source{extension}"
    raw_path.write_bytes(response.content)
    markdown_path = output / "source.md"
    markdown_path.write_text(
        convert_to_markdown(
            raw_path,
            response.content,
            content_type,
            "",
            response.encoding or "",
        ),
        encoding="utf-8",
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    supplemental = [
        item
        for item in manifest.get("supplemental_sources", [])
        if item.get("source_id") != args.source_id
    ]
    supplemental.append({
        "source_id": args.source_id,
        "snapshot_date": args.snapshot_date,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "language": args.role[0].rsplit("_", 1)[-1],
        "roles": args.role,
        "requested_url": args.url,
        "final_url": response.url,
        "http_status": response.status_code,
        "content_type": content_type,
        "encoding": response.encoding or "",
        "byte_count": len(response.content),
        "sha256": hashlib.sha256(response.content).hexdigest(),
        "raw_path": str(raw_path),
        "markdown_path": str(markdown_path),
        "provenance": args.provenance,
    })
    manifest["supplemental_sources"] = supplemental
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Collected {args.source_id}: {len(response.content)} bytes -> {raw_path}")


if __name__ == "__main__":
    main()
