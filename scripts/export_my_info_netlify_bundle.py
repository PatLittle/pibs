#!/usr/bin/env python3
"""Export the portable My Info JavaScript MCP bundle for stateless hosts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/my-info-mcp"
DERIVED = ROOT / "data/derived/my_info"


def _git_value(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def export_bundle(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for source in (PACKAGE / "src").glob("*.mjs"):
        shutil.copy2(source, output / source.name)

    data_dir = output / "data"
    data_dir.mkdir()
    contract = json.loads(
        (DERIVED / "my_info_questionnaire.json").read_text(encoding="utf-8")
    )
    with (DERIVED / "my_info_pib_features.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        features = list(csv.DictReader(handle))
    evidence: dict[str, object] = {}
    with (DERIVED / "my_info_derivation_evidence.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                item = json.loads(line)
                evidence[item["record"]["record_id"]] = item

    (data_dir / "runtime.json").write_text(
        json.dumps({"contract": contract, "features": features}, ensure_ascii=False),
        encoding="utf-8",
    )
    (data_dir / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False), encoding="utf-8"
    )
    (output / ".upstream.json").write_text(
        json.dumps(
            {
                "repo": "https://github.com/PatLittle/pibs",
                "commit": _git_value("rev-parse", "HEAD"),
                "date": _git_value("show", "-s", "--format=%ci", "HEAD"),
                "tool_api_version": "0.2.0",
                "contract_version": contract["content_version"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=PACKAGE / "dist",
        help="Bundle output directory (replaced if it exists)",
    )
    args = parser.parse_args()
    export_bundle(args.output.resolve())
    print(f"Exported My Info Netlify bundle to {args.output.resolve()}")


if __name__ == "__main__":
    main()
