#!/usr/bin/env python3
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INSTITUTIONS_DIR = ROOT / "institutions_infosource_docs"
README_PATH = ROOT / "README.md"

BANK_INLINE_RE = re.compile(
    r"(?:Bank Number|PIB Bank Number|Num[ée]ro(?:\s+du)?\s+fichier|Num[ée]ro(?:\s+du)?\s+FRP)[^\\n]{0,80}[A-Z]{2,6}\\s*[A-Z]{3}\\s*\\d{3}",
    re.I,
)


def has_inline_pib_content(folder: Path) -> bool:
    for name in ("infosource_en.md", "infosource_fr.md"):
        path = folder / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if BANK_INLINE_RE.search(text):
            return True
    return False


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        # minus header
        return max(sum(1 for _ in reader) - 1, 0)


def build_rows():
    rows = []
    for folder in sorted(p for p in INSTITUTIONS_DIR.iterdir() if p.is_dir()):
        csv_path = folder / "pib_table_en_fr.csv"
        processed = csv_path.exists()
        inline_pib = has_inline_pib_content(folder)
        row_count = csv_row_count(csv_path) if processed else 0

        if processed:
            status = "processed"
            notes = ""
        elif not inline_pib:
            status = "skipped"
            notes = "No PIB bank content in markdown (links out to other pages)."
        else:
            status = "pending"
            notes = ""

        rows.append(
            {
                "folder": folder.name,
                "status": status,
                "rows": row_count,
                "notes": notes,
            }
        )
    return rows


def main():
    rows = build_rows()
    total = len(rows)
    processed = sum(1 for row in rows if row["status"] == "processed")
    skipped = sum(1 for row in rows if row["status"] == "skipped")
    pending = sum(1 for row in rows if row["status"] == "pending")

    lines = [
        "# pibs",
        "",
        "## Processing Status",
        "",
        f"- Total departments: {total}",
        f"- Processed: {processed}",
        f"- Skipped: {skipped}",
        f"- Pending: {pending}",
        "",
        "| Department folder | Status | PIB rows | Notes |",
        "| --- | --- | ---: | --- |",
    ]

    for row in rows:
        notes = row["notes"].replace("|", "\\|")
        lines.append(f"| `{row['folder']}` | {row['status']} | {row['rows']} | {notes} |")

    README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"README updated: processed={processed} skipped={skipped} pending={pending}")


if __name__ == "__main__":
    main()
