#!/usr/bin/env python3
"""Build the standalone My Info browser survey from the canonical MCP engine."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/my_info"
ENGINE = ROOT / "packages/my-info-mcp/src/engine.mjs"
WEB_SOURCE = ROOT / "my_info/web"
SITE_OUTPUT = ROOT / "site/my_info"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _browser_engine(source: str) -> str:
    """Remove only the Node data-loader adapter; retain the survey implementation."""

    start = source.index('import fs from "node:fs";')
    class_start = source.index("export const STATE_SCHEMA_VERSION")
    transformed = source[:start] + source[class_start:]
    transformed = transformed.replace(
        "  constructor(contract = runtime.contract, features = runtime.features) {",
        "  constructor(contract, features) {\n"
        "    if (!contract || !features) throw new Error(\"Browser survey data was not supplied\");",
        1,
    )
    transformed = transformed.replace(
        "    if (!evidenceCache) evidenceCache = JSON.parse(fs.readFileSync(path.join(DATA_DIR, \"evidence.json\"), \"utf8\"));",
        "    if (!evidenceCache) throw new Error(\"Detailed derivation evidence is available through the MCP service\");",
        1,
    )
    transformed = transformed.replace("\nexport const engine = new SurveyToolEngine();\n", "\n")
    if "node:" in transformed or "DATA_DIR" in transformed or "new SurveyToolEngine();" in transformed:
        raise ValueError("Node-only survey engine code remained in the browser build")
    return transformed


def build(output: Path = SITE_OUTPUT) -> dict[str, object]:
    contract_bytes = (DERIVED / "my_info_questionnaire.json").read_bytes()
    contract = json.loads(contract_bytes)
    with (DERIVED / "my_info_pib_features.csv").open(encoding="utf-8", newline="") as handle:
        features = list(csv.DictReader(handle))

    engine_source = ENGINE.read_text(encoding="utf-8")
    browser_engine = _browser_engine(engine_source)
    tool_api_version = re.search(
        r'export const TOOL_API_VERSION = "([^"]+)"', engine_source
    ).group(1)
    release_stage = re.search(
        r'export const RELEASE_STAGE = "([^"]+)"', engine_source
    ).group(1)
    runtime = json.dumps(
        {"contract": contract, "features": features},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    output.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "app.mjs", "styles.css"):
        shutil.copy2(WEB_SOURCE / name, output / name)
    (output / "engine.mjs").write_text(browser_engine, encoding="utf-8")
    (output / "runtime.json").write_bytes(runtime)

    manifest = {
        "product": "My Info survey",
        "release_stage": release_stage,
        "contract_version": contract["content_version"],
        "contract_schema_version": contract["schema_version"],
        "tool_api_version": tool_api_version,
        "question_count": len(contract["questions"]),
        "adaptive_route_count": len(contract.get("adaptive_routes", [])),
        "pib_count": len(features),
        "source_hashes": {
            "questionnaire_sha256": _sha256_bytes(contract_bytes),
            "feature_csv_sha256": _sha256_bytes(
                (DERIVED / "my_info_pib_features.csv").read_bytes()
            ),
            "canonical_engine_sha256": _sha256_bytes(engine_source.encode("utf-8")),
        },
        "built_hashes": {
            "runtime_sha256": _sha256_bytes(runtime),
            "browser_engine_sha256": _sha256_bytes(browser_engine.encode("utf-8")),
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=SITE_OUTPUT)
    args = parser.parse_args()
    manifest = build(args.output.resolve())
    print(
        f"Built My Info web Beta: {manifest['question_count']} questions, "
        f"{manifest['adaptive_route_count']} adaptive routes, {manifest['pib_count']} PIBs"
    )


if __name__ == "__main__":
    main()
