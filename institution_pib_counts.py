"""Keep Info Source institution PIB counts synchronized with the combined PIB table."""

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence


PIB_COUNT_COLUMN = "pib_count"


def normalize_orgid(value: object) -> str:
    text = str(value or "").strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text if text.isdigit() else ""


def count_pibs_by_orgid(rows: Iterable[Mapping[str, object]]) -> Dict[str, int]:
    counts = Counter()
    for row in rows:
        orgid = normalize_orgid(row.get("orgid"))
        if orgid:
            counts[orgid] += 1
    return dict(counts)


def load_pib_counts(combined_csv_path: Path) -> Dict[str, int]:
    if not combined_csv_path.exists():
        return {}
    with combined_csv_path.open("r", encoding="utf-8", newline="") as handle:
        return count_pibs_by_orgid(csv.DictReader(handle))


def add_pib_counts(
    headers: Sequence[str],
    rows: Iterable[MutableMapping[str, object]],
    counts: Mapping[str, int],
) -> tuple[List[str], List[MutableMapping[str, object]]]:
    output_headers = [header for header in headers if header != PIB_COUNT_COLUMN]
    insert_at = output_headers.index("gc_orgID") + 1
    output_headers.insert(insert_at, PIB_COUNT_COLUMN)

    output_rows = list(rows)
    for row in output_rows:
        orgid = normalize_orgid(row.get("gc_orgID"))
        row[PIB_COUNT_COLUMN] = counts.get(orgid, 0) if orgid else ""
    return output_headers, output_rows


def write_csv(path: Path, headers: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def update_institution_csv_counts(
    source_path: Path,
    destination_paths: Sequence[Path],
    counts: Mapping[str, int],
) -> int:
    if not source_path.exists():
        return 0
    with source_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers, rows = add_pib_counts(reader.fieldnames or [], list(reader), counts)
    for destination_path in destination_paths:
        write_csv(destination_path, headers, rows)
    return len(rows)
