#!/usr/bin/env python3
"""Build a bilingual institution-specific Classes of Records table from Markdown."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


OUT_COLUMNS = [
    "record_number",
    "name_en",
    "name_fr",
    "document_types_en",
    "document_types_fr",
]

LABELS = {
    "document types": "document_types",
    "types of documents": "document_types",
    "types de documents": "document_types",
    "record number": "record_number",
    "records number": "record_number",
    "numero de dossier": "record_number",
    "numero du dossier": "record_number",
    "numero de document": "record_number",
    "numero du document": "record_number",
    "numero de la categorie de documents": "record_number",
}

BAD_TITLES = {
    "description",
    "document types",
    "types of documents",
    "types de documents",
    "format",
    "record number",
    "numero de dossier",
    "numero du dossier",
    "numero de document",
    "numero du document",
    "disclosure summaries",
    "sommaire des divulgations",
}


def clean_value(value: str) -> str:
    value = value.replace("\xa0", " ").strip()
    value = re.sub(r"^[:*+\-\s]+", "", value)
    value = re.sub(r"\s*[*]+$", "", value)
    return re.sub(r"\s+", " ", value).strip().strip("|").strip()


def normalize_label(value: str) -> str:
    value = clean_value(value).replace("’", "'")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).casefold()
    return re.sub(r"\s+", " ", value).strip()


def extract_label_value(line: str) -> tuple[str | None, str]:
    value = line.strip().replace("\xa0", " ")
    patterns = (
        r"^(?:[*+\-]\s*)?\*\*(.+?)\*\*\s*:?[ \t]*(.*)$",
        r"^(?:[*+\-]\s*)?([^:]{2,80})\s*:\s*(.*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, value)
        if not match:
            continue
        label = normalize_label(match.group(1).rstrip(":"))
        field = LABELS.get(label)
        if field:
            return field, clean_value(match.group(2))
    return None, ""


def heading_title(line: str) -> str:
    match = re.match(r"^#{3,6}\s+(.+)$", line.strip())
    if not match:
        return ""
    title = clean_value(match.group(1).strip("* "))
    return "" if normalize_label(title) in BAD_TITLES else title


def inline_title(line: str) -> str:
    match = re.match(r"^\s*\*\*(.+?)\*\*\s*$", line)
    if not match:
        return ""
    title = clean_value(match.group(1))
    return "" if ":" in title or normalize_label(title) in BAD_TITLES else title


def collect_value(lines: list[str], start: int, immediate: str) -> str:
    values: list[str] = [clean_value(immediate)] if immediate else []
    pointer = start + 1
    while pointer < len(lines):
        stripped = lines[pointer].strip()
        if not stripped:
            pointer += 1
            continue
        next_field, _ = extract_label_value(lines[pointer])
        any_bold_label = re.match(r"^(?:[*+\-]\s*)?\*\*[^*]+?\*\*\s*:?", stripped)
        if next_field or any_bold_label or re.match(r"^#{1,6}\s+", stripped):
            break
        values.append(clean_value(stripped))
        pointer += 1
    return clean_value(" ".join(item for item in values if item))


def parse_records(markdown: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    points: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        field, immediate = extract_label_value(line)
        if field != "record_number":
            continue
        number = clean_value(immediate) if immediate else collect_value(lines, index, "")
        if number:
            points.append((index, number))

    records: list[dict[str, str]] = []
    previous_point = -1
    for point_index, record_number in points:
        title_index = -1
        title = ""
        for scan in range(point_index - 1, previous_point, -1):
            title = heading_title(lines[scan]) or inline_title(lines[scan])
            if title:
                title_index = scan
                break
        if title_index < 0:
            for scan in range(point_index - 1, previous_point, -1):
                if not re.match(r"^\s*(?:description)\s*:\s*", lines[scan], re.I):
                    continue
                candidate_index = scan - 1
                while candidate_index > previous_point and not clean_value(lines[candidate_index]):
                    candidate_index -= 1
                candidate = clean_value(lines[candidate_index])
                if candidate and normalize_label(candidate) not in BAD_TITLES:
                    title_index = candidate_index
                    title = candidate
                    break
        if title_index < 0:
            previous_point = point_index
            continue

        document_types = ""
        for scan in range(title_index + 1, point_index):
            field, immediate = extract_label_value(lines[scan])
            if field == "document_types":
                document_types = collect_value(lines, scan, immediate)
                break

        canonical_number = canonical_record_number(record_number)
        if not canonical_number:
            previous_point = point_index
            continue
        records.append(
            {
                "record_number": canonical_number,
                "name": clean_value(title),
                "document_types": document_types,
            }
        )
        previous_point = point_index

    best_by_number: dict[str, tuple[tuple[int, int, str], dict[str, str]]] = {}
    order: list[str] = []
    for record in records:
        key = normalize_label(record["record_number"])
        quality = (
            sum(bool(record[field]) for field in ("name", "document_types")),
            len(record["name"]) + len(record["document_types"]),
            record["name"],
        )
        if key not in best_by_number:
            order.append(key)
            best_by_number[key] = (quality, record)
        elif quality > best_by_number[key][0]:
            best_by_number[key] = (quality, record)
    return [best_by_number[key][1] for key in order]


def number_tokens(value: str) -> list[str]:
    return re.findall(r"[a-z]+|\d+", normalize_label(value))


def suffix_key(value: str) -> str:
    tokens = number_tokens(value)
    if not tokens:
        return ""
    if len(tokens) >= 3:
        return " ".join(tokens[-2:])
    return tokens[-1]


def numeric_key(value: str) -> str:
    numbers = re.findall(r"\d+", normalize_label(value))
    return numbers[-1].lstrip("0") or "0" if numbers else ""


def canonical_record_number(value: str) -> str:
    cleaned = clean_value(value)
    match = re.search(
        r"\b[A-ZÀ-ÖØ-Þ]{2,8}(?:\s+[A-ZÀ-ÖØ-Þ]{2,8})?\s+(?:\d{3,4}|\d+(?:\.\d+)+)\b",
        cleaned,
        re.I,
    )
    return clean_value(match.group(0)) if match else ""


def merge_records(
    english: list[dict[str, str]], french: list[dict[str, str]]
) -> list[dict[str, str]]:
    en_suffix = Counter(suffix_key(row["record_number"]) for row in english)
    fr_suffix = Counter(suffix_key(row["record_number"]) for row in french)
    en_numeric = Counter(numeric_key(row["record_number"]) for row in english)
    fr_numeric = Counter(numeric_key(row["record_number"]) for row in french)

    matched: dict[int, int] = {}
    used_fr: set[int] = set()
    fr_by_suffix = {suffix_key(row["record_number"]): index for index, row in enumerate(french)}
    for en_index, row in enumerate(english):
        suffix = suffix_key(row["record_number"])
        if suffix and en_suffix[suffix] == fr_suffix[suffix] == 1:
            fr_index = fr_by_suffix[suffix]
            matched[en_index] = fr_index
            used_fr.add(fr_index)

    # Bilingual institutional acronyms and series often differ (for example,
    # CTA DRB 001 / OTC RDD 001). Within each numeric code, source order is a
    # stable tie-breaker; unequal groups are deliberately left unpaired.
    en_by_number: dict[str, list[int]] = defaultdict(list)
    fr_by_number: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(english):
        if index not in matched:
            en_by_number[numeric_key(row["record_number"])].append(index)
    for index, row in enumerate(french):
        if index not in used_fr:
            fr_by_number[numeric_key(row["record_number"])].append(index)
    for number, en_indexes in en_by_number.items():
        fr_indexes = fr_by_number.get(number, [])
        if number and len(en_indexes) == len(fr_indexes):
            for en_index, fr_index in zip(en_indexes, fr_indexes):
                matched[en_index] = fr_index
                used_fr.add(fr_index)

    rows: list[dict[str, str]] = []
    for en_index, en in enumerate(english):
        fr = french[matched[en_index]] if en_index in matched else {}
        rows.append(
            {
                "record_number": en["record_number"],
                "name_en": en["name"],
                "name_fr": fr.get("name", ""),
                "document_types_en": en["document_types"],
                "document_types_fr": fr.get("document_types", ""),
            }
        )
    for fr_index, fr in enumerate(french):
        if fr_index not in used_fr:
            rows.append(
                {
                    "record_number": fr["record_number"],
                    "name_en": "",
                    "name_fr": fr["name"],
                    "document_types_en": "",
                    "document_types_fr": fr["document_types"],
                }
            )
    return rows


def process_files(en_path: Path, fr_path: Path, output_path: Path) -> tuple[int, int, int]:
    en_records = parse_records(en_path.read_text(encoding="utf-8", errors="replace")) if en_path.exists() else []
    fr_records = parse_records(fr_path.read_text(encoding="utf-8", errors="replace")) if fr_path.exists() else []
    rows = merge_records(en_records, fr_records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(en_records), len(fr_records), len(rows)


def process_folder(folder: Path) -> tuple[int, int, int]:
    en_path = folder / "classes_of_records_en.md"
    fr_path = folder / "classes_of_records_fr.md"
    if not en_path.exists():
        en_path = folder / "infosource_en.md"
    if not fr_path.exists():
        fr_path = folder / "infosource_fr.md"
    return process_files(en_path, fr_path, folder / "cor_table_en_fr.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    en_count, fr_count, merged_count = process_folder(args.folder.resolve())
    print(f"OK {args.folder.name}: en={en_count} fr={fr_count} merged={merged_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
