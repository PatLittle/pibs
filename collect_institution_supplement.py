#!/usr/bin/env python3
"""Collect a dated, provenance-preserving supplemental Info Source page."""

from __future__ import annotations

import argparse
import hashlib
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

from urllib3.exceptions import InsecureRequestWarning

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
    parser.add_argument("--url", required=True, help="Published source URL, also used for a provided file's provenance.")
    parser.add_argument(
        "--local-file",
        type=Path,
        help="Use a user-provided saved source instead of requesting the published URL.",
    )
    parser.add_argument(
        "--allow-unverified-tls",
        action="store_true",
        help="Allow a known official source with a locally untrusted certificate chain; recorded in provenance.",
    )
    parser.add_argument("--role", action="append", required=True, choices=ROLE_NAMES)
    parser.add_argument("--snapshot-date", required=True)
    parser.add_argument("--provenance", required=True)
    parser.add_argument(
        "--replaces-previous",
        action="store_true",
        help="Use this publication in place of earlier captures for the selected roles.",
    )
    args = parser.parse_args()

    folder = Path("institutions_infosource_docs") / args.institution_id
    manifest_path = folder / "source_manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing canonical source manifest: {manifest_path}")

    if args.local_file:
        if not args.local_file.is_file():
            raise SystemExit(f"Missing provided source: {args.local_file}")
        content = args.local_file.read_bytes()
        content_type = "text/html; charset=utf-8"
        final_url = args.url
        encoding = "utf-8"
        http_status = None
    else:
        if args.allow_unverified_tls:
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        response = session().get(
            args.url, allow_redirects=True, timeout=(15, 75),
            verify=not args.allow_unverified_tls,
        )
        response.raise_for_status()
        content = response.content
        content_type = response.headers.get("content-type", "")
        final_url = response.url
        encoding = response.encoding or ""
        http_status = response.status_code
    if rejected_response(content):
        raise SystemExit("Upstream returned a request-rejection page")

    extension = content_extension(content_type, final_url)
    output = folder / "snapshots" / args.snapshot_date / "supplemental" / args.source_id
    output.mkdir(parents=True, exist_ok=True)
    raw_path = output / f"source{extension}"
    raw_path.write_bytes(content)
    markdown_path = output / "source.md"
    markdown = convert_to_markdown(
        raw_path,
        content,
        content_type,
        "",
        encoding,
    )
    markdown_path.write_text(
        markdown.rstrip() + "\n" if markdown else "",
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
        "final_url": final_url,
        "http_status": http_status,
        "capture_method": "provided_local_file" if args.local_file else "http_get",
        "tls_verified": None if args.local_file else not args.allow_unverified_tls,
        "provided_file_name": args.local_file.name if args.local_file else None,
        "content_type": content_type,
        "encoding": encoding,
        "byte_count": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "raw_path": str(raw_path),
        "markdown_path": str(markdown_path),
        "provenance": args.provenance,
        "replaces_previous": args.replaces_previous,
    })
    manifest["supplemental_sources"] = supplemental
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Collected {args.source_id}: {len(content)} bytes -> {raw_path}")


if __name__ == "__main__":
    main()
