#!/usr/bin/env python3
"""Build static site data assets and a compact overview summary."""

from __future__ import annotations

import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


SITE_DATA = Path("site/data")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def percent(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 1) if denominator else 0.0


def main() -> None:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    copies = {
        Path("standard_classes_of_records_en_fr.csv"): SITE_DATA / "standard_classes_of_records_en_fr.csv",
        Path("pib_type_values.csv"): SITE_DATA / "pib_type_values.csv",
    }
    for source, target in copies.items():
        shutil.copyfile(source, target)
    shutil.copyfile(
        Path("data/collection_jobs/institution_collection_status_2026-08-15.csv"),
        SITE_DATA / "institution_collection_status.csv",
    )

    registry = read_rows(SITE_DATA / "institution_registry.csv")
    pibs = read_rows(SITE_DATA / "pib_table_en_fr_all.csv")
    classes = read_rows(SITE_DATA / "cor_table_en_fr_all.csv")
    links = read_rows(SITE_DATA / "pib_cor_links.csv")
    standard_pibs = read_rows(SITE_DATA / "spib_en_fr.csv")
    standard_classes = read_rows(SITE_DATA / "standard_classes_of_records_en_fr.csv")
    categories = read_rows(SITE_DATA / "pi_categories_en_fr.csv")
    pib_types = read_rows(SITE_DATA / "pib_type_values.csv")
    collection = json.loads(
        Path("data/collection_jobs/institution_collection_summary_2026-08-15.json").read_text(
            encoding="utf-8"
        )
    )

    institution_names = {
        row["institution_id"]: (row["legal_name_en"], row["legal_name_fr"])
        for row in registry
    }
    explorer_link_columns = [
        "institution_id", "institution_name_en", "institution_name_fr",
        "bank_number_key", "language", "language_label", "related_record_number",
        "relationship_scope", "relationship_scope_label", "resolved",
        "resolution_label", "cor_record_number", "cor_record_number_display",
    ]
    with (SITE_DATA / "pib_cor_links_explorer.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=explorer_link_columns, lineterminator="\n")
        writer.writeheader()
        for row in links:
            name_en, name_fr = institution_names.get(row["institution_id"], ("", ""))
            is_standard = row["relationship_scope"] == "standard"
            resolved = row["resolved"].casefold() == "true"
            display_key = row["cor_record_number"]
            if is_standard and display_key:
                display_key = f"PRN {display_key} / NDP {display_key}"
            writer.writerow({
                **row,
                "institution_name_en": name_en,
                "institution_name_fr": name_fr,
                "language_label": "English" if row["language"] == "en" else "French",
                "relationship_scope_label": (
                    "Standard class" if is_standard else "Institution-specific class"
                ),
                "resolution_label": "Resolved" if resolved else "Needs review",
                "cor_record_number_display": display_key,
            })

    counts: dict[str, dict[str, object]] = defaultdict(
        lambda: {"pibs": 0, "classes": 0, "name_en": "", "name_fr": ""}
    )
    for row in pibs:
        item = counts[row["institution_id"]]
        item["pibs"] = int(item["pibs"]) + 1
        item["name_en"] = row["institution_name_en"]
        item["name_fr"] = row["institution_name_fr"]
    for row in classes:
        item = counts[row["institution_id"]]
        item["classes"] = int(item["classes"]) + 1
        item["name_en"] = row["institution_name_en"]
        item["name_fr"] = row["institution_name_fr"]

    top_institutions = sorted(
        (
            {
                "institution_id": institution_id,
                **values,
                "total": int(values["pibs"]) + int(values["classes"]),
            }
            for institution_id, values in counts.items()
        ),
        key=lambda item: (-int(item["total"]), str(item["name_en"])),
    )[:8]

    pib_type_counts = Counter(row["pib_type"] or "Unclassified legacy code" for row in pibs)
    resolved = sum(row["resolved"].casefold() == "true" for row in links)
    bilingual_pibs = sum(bool(row["title_en"] and row["title_fr"]) for row in pibs)
    bilingual_classes = sum(bool(row["name_en"] and row["name_fr"]) for row in classes)
    snapshot_date = max((row["registry_as_of_date"] for row in registry), default=str(date.today()))

    summary = {
        "snapshot_date": snapshot_date,
        "headline": {
            "institutions": len(registry),
            "institution_pibs": len(pibs),
            "institution_classes": len(classes),
            "pib_cor_links": len(links),
        },
        "quality": {
            "pibs_bilingual": bilingual_pibs,
            "pibs_bilingual_percent": percent(bilingual_pibs, len(pibs)),
            "classes_bilingual": bilingual_classes,
            "classes_bilingual_percent": percent(bilingual_classes, len(classes)),
            "links_resolved": resolved,
            "links_resolved_percent": percent(resolved, len(links)),
        },
        "collection": {
            "collectable_institutions": collection["collectable_institutions"],
            "collection_completed": collection["collection_completed"],
            "all_four_sources": collection["institutions_with_all_four_sources_collected"],
            "any_source": collection["institutions_with_any_source_collected"],
            "no_source_urls": collection["not_collectable_no_source_urls"],
            "no_successful_source": collection["institutions_with_no_source_collected"],
            "unique_failing_urls": collection["unique_failing_requested_urls"],
        },
        "datasets": {
            "institutions": len(registry),
            "pibs": len(pibs),
            "classes": len(classes),
            "links": len(links),
            "standard_pibs": len(standard_pibs),
            "standard_classes": len(standard_classes),
            "categories": len(categories),
            "pib_types": len(pib_types),
        },
        "pib_types": [
            {"name": name, "count": count}
            for name, count in sorted(pib_type_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "top_institutions": top_institutions,
    }
    (SITE_DATA / "site_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "Built site assets: "
        f"institutions={len(registry)}, PIBs={len(pibs)}, classes={len(classes)}, links={len(links)}"
    )


if __name__ == "__main__":
    main()
