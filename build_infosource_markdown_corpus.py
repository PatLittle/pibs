#!/usr/bin/env python3
"""Create per-institution EN/FR HTML + Markdown copies for matched Info Source entries."""

import csv
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from markitdown import MarkItDown
from unidecode import unidecode

INPUT_CSV = Path("infosource_institutions_en_fr.csv")
REGISTRY_CSV = Path("institution_registry.csv")
OUTPUT_ROOT = Path("institutions_infosource_docs")

# Historical input rows sometimes lack both gc_orgID and Open Government slug,
# or contain only one language/name from an older institution listing.  Keep
# those rows in the same corpus folder as their known canonical institution.
LEGACY_FOLDER_ALIASES = {
    "na_british-columbia-treaty-commission": "ati-schedule-i-british-columbia-treaty-commission",
    "na_women-and-gender-equality": "ati-schedule-i-department-for-women-and-gender-equality",
    "na_infrastructure-canada": "ati-schedule-i-department-of-housing-infrastructure-and-communities",
    "na_federal-public-service-health-care-plan-administration-authority": (
        "ati-schedule-i-federal-public-service-health-care-plan-administration-authority"
    ),
    "na_gwich-in-land-and-water-board": "ati-schedule-i-gwich-in-land-and-water-board",
    "na_office-gwich-in-d-amenagement-territorial": (
        "ati-schedule-i-gwich-in-land-use-planning-board"
    ),
    "na_nunavut-water-board": "ati-schedule-i-nunavut-water-board",
    "na_comite-externe-d-examen-de-la-gendarmerie-royale-du-canada": (
        "ati-schedule-i-royal-canadian-mounted-police-external-review-committee"
    ),
    "na_canada-post": "3651_canada-post",
    "na_societe-du-pont-de-la-riviere-ste-marie": "na_st-mary-s-river-bridge-company",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoSource-Markdown-Corpus/1.0; +https://example.local)"
}

TABLE_HEADINGS = [
    "title",
    "Bank number",
    "Description",
    "Class of individuals",
    ". Note",
    "Social insurance number",
    "Purpose",
    "Consistent uses",
    "Retention and disposal standards",
    "RDA number",
    "Related record number",
    "Last updated",
]


def slugify(text: str, max_len: int = 80) -> str:
    s = unidecode((text or "").strip().lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if not s:
        s = "institution"
    return s[:max_len].rstrip("-")


def normalize_orgid(value: object) -> str:
    text = "" if pd.isna(value) else str(value or "").strip()
    return text[:-2] if re.fullmatch(r"\d+\.0", text) else text


def load_registry_folder_lookup(path: Path = REGISTRY_CSV) -> dict[str, str]:
    """Map legacy operational identifiers to canonical Schedule I folder IDs."""
    if not path.exists():
        return {}
    lookup: dict[str, str] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            institution_id = str(row.get("institution_id") or "").strip()
            orgid = normalize_orgid(row.get("gc_orgID"))
            open_canada_slug = str(row.get("open_canada_org_slug") or "").strip()
            if institution_id and orgid:
                lookup[f"gc:{orgid}"] = institution_id
            if institution_id and open_canada_slug:
                lookup[f"slug:{open_canada_slug}"] = institution_id
    return lookup


def corpus_folder_for(
    row: object,
    registry_lookup: dict[str, str],
    root: Path = OUTPUT_ROOT,
) -> Path:
    """Use the canonical Schedule I folder, falling back for non-registry entities."""
    getter = row.get  # pandas Series and dictionaries both provide get().
    orgid = normalize_orgid(getter("gc_orgID"))
    raw_slug = getter("open_gov_ouvert")
    open_canada_slug = "" if pd.isna(raw_slug) else str(raw_slug or "").strip()
    institution_id = registry_lookup.get(f"gc:{orgid}")
    if not institution_id and open_canada_slug:
        institution_id = registry_lookup.get(f"slug:{open_canada_slug}")
    if institution_id:
        return root / institution_id
    raw_name = getter("institution_name_en")
    if pd.isna(raw_name) or not str(raw_name).strip():
        raw_name = getter("institution_name_fr")
    name = "" if pd.isna(raw_name) else str(raw_name or "").strip()
    fallback_name = f"{orgid or 'na'}_{slugify(name)}"
    return root / LEGACY_FOLDER_ALIASES.get(fallback_name, fallback_name)


def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=40)
    r.raise_for_status()
    return r.text


def write_format_md(folder: Path, institution_en: str, institution_fr: str):
    lines = [
        f"# Format Guide: {institution_en}",
        "",
        f"French name: {institution_fr}",
        "",
        "Use the markdown files in this folder (`infosource_en.md`, `infosource_fr.md`) and parse each personal information bank block into a table with the exact columns below.",
        "",
        "## Target table headings",
        "",
    ]
    lines.extend([f"- {heading}" for heading in TABLE_HEADINGS])
    lines.extend(
        [
            "",
            "## Parsing notes",
            "",
            "- `title`: the personal information bank title heading.",
            "- Keep one row per bank entry.",
            "- Map EN/FR labels to the target headings where labels vary by language.",
            "- Preserve bank identifiers in `Bank number` exactly as shown in source text.",
            "- Keep multiline values as plain text (single cell) when exporting.",
            "- If a field is not present for an entry, leave it blank.",
            "",
            "## Suggested extraction flow",
            "",
            "1. Split markdown on bank-level headings.",
            "2. Within each block, identify label-value lines for the target headings.",
            "3. Normalize heading labels to the target schema.",
            "4. Emit tabular output (CSV/JSON/DataFrame) with the headings above in order.",
        ]
    )
    (folder / "format.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    required = [
        "institution_name_en",
        "institution_name_fr",
        "infosource_url_en",
        "infosource_url_fr",
        "infosource_status_en",
        "infosource_status_fr",
        "gc_orgID",
    ]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    matched = df[
        df["institution_name_en"].notna()
        & df["institution_name_fr"].notna()
        & df["infosource_url_en"].notna()
        & df["infosource_url_fr"].notna()
        & (df["infosource_status_en"] == 200)
        & (df["infosource_status_fr"] == 200)
    ].copy()

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    registry_lookup = load_registry_folder_lookup()
    md = MarkItDown()

    print(f"Institutions to process (matched + EN/FR status 200): {len(matched)}")
    processed = 0
    failed = 0

    for idx, row in matched.reset_index(drop=True).iterrows():
        gco = row.get("gc_orgID")
        gco_str = str(int(gco)) if pd.notna(gco) else "na"
        name_en = str(row["institution_name_en"]).strip()
        name_fr = str(row["institution_name_fr"]).strip()
        folder = corpus_folder_for(row, registry_lookup)
        folder.mkdir(parents=True, exist_ok=True)

        print(f"[{idx + 1}/{len(matched)}] {name_en}")
        try:
            for lang in ("en", "fr"):
                url = str(row[f"infosource_url_{lang}"]).strip()
                html = fetch_html(url)
                html_path = folder / f"infosource_{lang}.html"
                md_path = folder / f"infosource_{lang}.md"
                html_path.write_text(html, encoding="utf-8")

                result = md.convert(str(html_path))
                md_path.write_text(result.markdown or "", encoding="utf-8")

            write_format_md(folder, name_en, name_fr)

            meta_lines = [
                f"institution_name_en: {name_en}",
                f"institution_name_fr: {name_fr}",
                f"gc_orgID: {gco_str}",
                f"infosource_url_en: {row['infosource_url_en']}",
                f"infosource_url_fr: {row['infosource_url_fr']}",
            ]
            (folder / "metadata.txt").write_text("\n".join(meta_lines) + "\n", encoding="utf-8")
            processed += 1
        except Exception as exc:
            failed += 1
            (folder / "error.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")

    print(f"Completed. Success: {processed}, Failed: {failed}")


if __name__ == "__main__":
    main()
