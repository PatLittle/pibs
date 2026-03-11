#!/usr/bin/env python3
import csv
import re
from pathlib import Path

INPUT_GLOB = "institutions_infosource_docs/*/pib_table_en_fr.csv"
OUTPUT_PATH = Path("institutions_infosource_docs/pib_table_en_fr_all.csv")
SITE_OUTPUT_PATH = Path("site/data/pib_table_en_fr_all.csv")
INSTITUTIONS_PATH = Path("infosource_institutions_en_fr.csv")
ORGID_FROM_FOLDER_RE = re.compile(r"^(\d+)_")


def read_csv_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        rows = [dict(row) for row in reader]
    return headers, rows


def load_institutions_map(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        institutions = {}
        for row in reader:
            orgid = str(row.get("gc_orgID", "")).strip()
            if not orgid:
                continue
            institutions[orgid] = {
                "institution_name_en": str(row.get("institution_name_en", "")).strip(),
                "institution_name_fr": str(row.get("institution_name_fr", "")).strip(),
            }
    return institutions


def write_combined_csv(path: Path, headers, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow({header: record.get(header, "") for header in headers})


def main():
    if not INSTITUTIONS_PATH.exists():
        raise SystemExit(f"Missing institutions lookup file: {INSTITUTIONS_PATH}")

    csv_paths = sorted(Path(".").glob(INPUT_GLOB))
    if not csv_paths:
        raise SystemExit(f"No files found for glob: {INPUT_GLOB}")

    institutions_by_orgid = load_institutions_map(INSTITUTIONS_PATH)
    header_order = []
    records = []
    missing_orgid_map = 0

    for csv_path in csv_paths:
        folder_name = csv_path.parent.name
        orgid_match = ORGID_FROM_FOLDER_RE.match(folder_name)
        orgid = orgid_match.group(1) if orgid_match else ""
        institution = institutions_by_orgid.get(
            orgid, {"institution_name_en": "", "institution_name_fr": ""}
        )
        if orgid and not institution["institution_name_en"] and not institution["institution_name_fr"]:
            missing_orgid_map += 1

        headers, rows = read_csv_rows(csv_path)
        for header in headers:
            if header not in header_order:
                header_order.append(header)
        for row in rows:
            records.append(
                {
                    "orgid": orgid,
                    "institution_name_en": institution["institution_name_en"],
                    "institution_name_fr": institution["institution_name_fr"],
                    **row,
                }
            )

    fixed_headers = ["orgid", "institution_name_en", "institution_name_fr"]
    header_order = [header for header in header_order if header not in fixed_headers]
    output_headers = fixed_headers + header_order
    write_combined_csv(OUTPUT_PATH, output_headers, records)
    write_combined_csv(SITE_OUTPUT_PATH, output_headers, records)

    print(
        f"Wrote {len(records)} rows from {len(csv_paths)} files to "
        f"{OUTPUT_PATH} and {SITE_OUTPUT_PATH}. "
        f"Institution-name misses: {missing_orgid_map}"
    )


if __name__ == "__main__":
    main()
