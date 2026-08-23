#!/usr/bin/env python3
"""Validate the independently deployed My Info browser survey."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "site/my_info"
DERIVED = ROOT / "data/derived/my_info"
ENGINE = ROOT / "packages/my-info-mcp/src/engine.mjs"
REQUIRED_FILES = (
    "index.html",
    "app.mjs",
    "engine.mjs",
    "runtime.json",
    "manifest.json",
    "styles.css",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    errors: list[str] = []
    missing = [name for name in REQUIRED_FILES if not (OUTPUT / name).is_file()]
    errors.extend(f"missing My Info web asset: {OUTPUT / name}" for name in missing)

    if not missing:
        manifest = json.loads((OUTPUT / "manifest.json").read_text(encoding="utf-8"))
        runtime = json.loads((OUTPUT / "runtime.json").read_text(encoding="utf-8"))
        browser_engine = (OUTPUT / "engine.mjs").read_text(encoding="utf-8")
        index = (OUTPUT / "index.html").read_text(encoding="utf-8")

        if manifest.get("release_stage") != "beta":
            errors.append("My Info web manifest is not marked beta")
        if manifest.get("contract_version") != runtime["contract"].get("content_version"):
            errors.append("My Info web contract version mismatch")
        if manifest.get("question_count") != len(runtime["contract"].get("questions", [])):
            errors.append("My Info web question count mismatch")
        if manifest.get("adaptive_route_count") != len(runtime["contract"].get("adaptive_routes", [])):
            errors.append("My Info web adaptive-route count mismatch")
        if manifest.get("pib_count") != len(runtime.get("features", [])):
            errors.append("My Info web PIB count mismatch")

        source_hashes = manifest.get("source_hashes", {})
        if source_hashes.get("canonical_engine_sha256") != _sha256(ENGINE):
            errors.append("My Info web engine is stale relative to the MCP engine")
        if source_hashes.get("questionnaire_sha256") != _sha256(
            DERIVED / "my_info_questionnaire.json"
        ):
            errors.append("My Info web contract is stale relative to the derived questionnaire")
        if source_hashes.get("feature_csv_sha256") != _sha256(
            DERIVED / "my_info_pib_features.csv"
        ):
            errors.append("My Info web data is stale relative to the derived feature CSV")
        if manifest.get("built_hashes", {}).get("runtime_sha256") != _sha256(
            OUTPUT / "runtime.json"
        ):
            errors.append("My Info runtime hash mismatch")
        if manifest.get("built_hashes", {}).get("browser_engine_sha256") != _sha256(
            OUTPUT / "engine.mjs"
        ):
            errors.append("My Info browser-engine hash mismatch")
        if "node:" in browser_engine or "DATA_DIR" in browser_engine:
            errors.append("My Info browser engine includes Node-only code")
        for reference in ('href="styles.css"', 'src="app.mjs"'):
            if reference not in index:
                errors.append(f"My Info page is missing {reference}")

    if errors:
        raise SystemExit("My Info web validation failed:\n- " + "\n- ".join(errors))
    print(
        "Validated My Info web Beta: "
        f"questions={manifest['question_count']}, routes={manifest['adaptive_route_count']}, "
        f"pibs={manifest['pib_count']}, path=/my_info/"
    )


if __name__ == "__main__":
    main()
