#!/usr/bin/env python3
"""Validate static site assets, summary counts, and local navigation targets."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


SITE = Path("site")
DATASETS = {
    "institutions": "institution_registry.csv",
    "pibs": "pib_table_en_fr_all.csv",
    "classes": "cor_table_en_fr_all.csv",
    "links": "pib_cor_links.csv",
    "standard_pibs": "spib_en_fr.csv",
    "standard_classes": "standard_classes_of_records_en_fr.csv",
    "categories": "pi_categories_en_fr.csv",
    "pib_types": "pib_type_values.csv",
}
REQUIRED_FIELDS = {
    "institutions": {"institution_id", "legal_name_en", "legal_name_fr"},
    "pibs": {"institution_id", "bank_number_key", "title_en", "title_fr"},
    "classes": {"institution_id", "record_number", "name_en", "name_fr"},
    "links": {"institution_id", "bank_number_key", "cor_record_number"},
}


def row_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    errors: list[str] = []
    summary_path = SITE / "data/site_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    for key, filename in DATASETS.items():
        path = SITE / "data" / filename
        if not path.exists():
            errors.append(f"missing dataset asset: {path}")
            continue
        actual = row_count(path)
        if actual != summary["datasets"][key]:
            errors.append(
                f"summary count mismatch for {key}: {summary['datasets'][key]} != {actual}"
            )
        if key in REQUIRED_FIELDS:
            with path.open(encoding="utf-8", newline="") as handle:
                fields = set(csv.DictReader(handle).fieldnames or [])
            missing = sorted(REQUIRED_FIELDS[key] - fields)
            if missing:
                errors.append(f"{key} dataset missing relational fields: {missing}")

    generated_assets = {
        "pib_cor_links_explorer.csv": summary["datasets"]["links"],
        "institution_collection_status.csv": summary["collection"]["collectable_institutions"],
    }
    for filename, minimum in generated_assets.items():
        path = SITE / "data" / filename
        if not path.exists():
            errors.append(f"missing generated explorer asset: {path}")
        elif row_count(path) < minimum:
            errors.append(f"generated explorer asset is unexpectedly short: {path}")

    for html_path in SITE.rglob("*.html"):
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        if not soup.title or not soup.title.get_text(strip=True):
            errors.append(f"missing title: {html_path}")
        for element in soup.find_all(href=True):
            href = str(element["href"])
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("#"):
                continue
            target = (html_path.parent / parsed.path).resolve()
            if not target.exists():
                errors.append(f"broken local link in {html_path}: {href}")

    my_info = SITE / "my-info"
    my_info_files = ("index.html", "app.mjs", "engine.mjs", "runtime.json", "manifest.json", "styles.css")
    missing_my_info = [filename for filename in my_info_files if not (my_info / filename).exists()]
    for filename in missing_my_info:
        errors.append(f"missing My Info web asset: {my_info / filename}")
    if not missing_my_info:
        my_info_manifest = json.loads((my_info / "manifest.json").read_text(encoding="utf-8"))
        my_info_runtime = json.loads((my_info / "runtime.json").read_text(encoding="utf-8"))
        canonical_engine = Path("packages/my-info-mcp/src/engine.mjs").read_bytes()
        if my_info_manifest.get("release_stage") != "beta":
            errors.append("My Info web manifest is not marked beta")
        if my_info_manifest.get("contract_version") != my_info_runtime["contract"].get("content_version"):
            errors.append("My Info web contract version mismatch")
        if my_info_manifest.get("question_count") != len(my_info_runtime["contract"].get("questions", [])):
            errors.append("My Info web question count mismatch")
        if my_info_manifest.get("pib_count") != len(my_info_runtime.get("features", [])):
            errors.append("My Info web PIB count mismatch")
        if my_info_manifest.get("source_hashes", {}).get("canonical_engine_sha256") != hashlib.sha256(canonical_engine).hexdigest():
            errors.append("My Info web engine is stale relative to the MCP engine")
        browser_engine = (my_info / "engine.mjs").read_text(encoding="utf-8")
        if "node:" in browser_engine or "DATA_DIR" in browser_engine:
            errors.append("My Info browser engine includes Node-only code")

    index = BeautifulSoup((SITE / "index.html").read_text(encoding="utf-8"), "html.parser")
    expected_ids = {
        "stat-institutions", "stat-pibs", "stat-classes", "stat-links",
        "pib-type-bars", "institution-bars", "quality-links", "datasets",
    }
    missing_ids = sorted(identifier for identifier in expected_ids if not index.find(id=identifier))
    if missing_ids:
        errors.append(f"landing page missing required components: {missing_ids}")

    table = BeautifulSoup((SITE / "table.html").read_text(encoding="utf-8"), "html.parser")
    for identifier in ("dataset-table-container", "table-search", "record-dialog", "dataset-facets", "dataset-nav"):
        if not table.find(id=identifier):
            errors.append(f"table explorer missing component: {identifier}")

    if errors:
        raise SystemExit("Site validation failed:\n- " + "\n- ".join(errors))
    print(
        "Validated static site: "
        f"datasets={len(DATASETS)}, records={sum(summary['datasets'].values())}, "
        f"html_pages={len(list(SITE.rglob('*.html')))}, broken_links=0"
    )


if __name__ == "__main__":
    main()
