#!/usr/bin/env python3
import csv
import re
import sys
import unicodedata
from collections import defaultdict, deque
from pathlib import Path

ALIAS = {}


def add_alias(field, *labels):
    for label in labels:
        ALIAS[label] = field


add_alias("description", "description")
add_alias(
    "class_of_individuals",
    "class of individuals",
    "classes of individuals",
    "categorie de personnes",
    "categories de personnes",
    "catégorie de personnes",
    "catégories de personnes",
)
add_alias("note", "note", "notes", "nota", "remarque")
add_alias("social_insurance_number", "social insurance number", "numero d assurance sociale")
add_alias("purpose", "purpose", "but")
add_alias("consistent_uses", "consistent uses", "consistent use", "usages compatibles", "utilisations compatibles")
add_alias(
    "retention_and_disposal_standards",
    "retention and disposal standards",
    "retention and disposition standards",
    "normes de conservation et de destruction",
    "normes de conservation et de disposition",
)
add_alias(
    "rda_number",
    "rda number",
    "no add",
    "no. add",
    "numero d add",
    "numero add",
    "numero d autorisation de divulgation",
    "numero d autorisation de divulgation add",
)
add_alias(
    "related_record_number",
    "related class of record number",
    "related records number",
    "related record number",
    "related record numbers",
    "renvoi au document no",
    "renvoi au document numero",
    "numero de renvoi au document",
    "numero de connexe",
    "numero de categorie du document connexe",
)
add_alias("last_updated", "last updated", "derniere mise a jour")
add_alias(
    "tbs_registration",
    "tbs registration",
    "enregistrement sct",
    "enregistrement du sct",
    "enregistrement au sct",
    "enregistrement aupres du sct",
    "numero d enregistrement du sct",
    "enregistrement",
)
add_alias(
    "bank_number",
    "bank number",
    "pib bank number",
    "numero de fichier",
    "numero du fichier",
    "numero de frp",
    "numero du frp",
)

BAD_TITLES = {
    "description",
    "document types",
    "types de documents",
    "class of individuals",
    "classes of individuals",
    "categorie de personnes",
    "categories de personnes",
    "catégorie de personnes",
    "catégories de personnes",
    "note",
    "notes",
    "social insurance number",
    "numero d assurance sociale",
    "purpose",
    "but",
    "consistent uses",
    "usages compatibles",
    "utilisations compatibles",
    "retention and disposal standards",
    "normes de conservation et de destruction",
    "normes de conservation et de disposition",
    "rda number",
    "no add",
    "related record number",
    "related records number",
    "related class of record number",
    "renvoi au document no",
    "renvoi au document numero",
    "tbs registration",
    "enregistrement du sct",
    "bank number",
    "numero de fichier",
    "personal information",
    "renseignements personnels",
    "language preferences",
    "preferences linguistiques",
    "background and experience",
    "antécédents et expériences",
    "skills and competencies",
    "competences",
    "préférences et opinions",
    "preferences and opinions",
}

FIELDS = [
    "title",
    "bank_number",
    "description",
    "class_of_individuals",
    "note",
    "social_insurance_number",
    "purpose",
    "consistent_uses",
    "retention_and_disposal_standards",
    "rda_number",
    "related_record_number",
    "last_updated",
    "tbs_registration",
]

OUT_COLUMNS = [
    "bank_number_key",
    "title_en",
    "title_fr",
    "bank_number_en",
    "bank_number_fr",
    "description_en",
    "description_fr",
    "class_of_individuals_en",
    "class_of_individuals_fr",
    "note_en",
    "note_fr",
    "social_insurance_number_en",
    "social_insurance_number_fr",
    "purpose_en",
    "purpose_fr",
    "consistent_uses_en",
    "consistent_uses_fr",
    "retention_and_disposal_standards_en",
    "retention_and_disposal_standards_fr",
    "rda_number_en",
    "rda_number_fr",
    "related_record_number_en",
    "related_record_number_fr",
    "last_updated_en",
    "last_updated_fr",
    "tbs_registration_en",
    "tbs_registration_fr",
]

BANK_RE = re.compile(r"\b([A-Z]{2,6})\s*([A-Z]{3})\s*(\d{3})\b")


def normalize_spaces(value):
    return re.sub(r"\s+", " ", value.replace("\xa0", " ").strip())


def normalize_label(value):
    value = normalize_spaces(value.strip().strip("*"))
    value = value.replace("’", " ").replace("'", " ")
    value = value.strip(" :;.-*")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_value(value):
    value = value.replace("\xa0", " ")
    value = re.sub(r"^\*+\s*", "", value)
    value = re.sub(r"\s*\*+$", "", value)
    return re.sub(r"\s+", " ", value).strip()


def split_multi_label_lines(text):
    out = []
    for line in text.splitlines():
        matches = list(re.finditer(r"\*\*[^*\n]+?\*\*\s*:", line))
        if len(matches) <= 1:
            out.append(line)
            continue
        starts = [match.start() for match in matches] + [len(line)]
        for idx in range(len(matches)):
            part = line[starts[idx] : starts[idx + 1]].strip()
            if part:
                out.append(part)
    return "\n".join(out)


def extract_label_value(line):
    value = line.strip().replace("\xa0", " ")

    match = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", value)
    if match:
        inside = match.group(1).strip()
        tail = match.group(2).strip()
        normalized_inside = normalize_label(inside)

        if ":" in inside:
            prefix, rest = inside.split(":", 1)
            field = ALIAS.get(normalize_label(prefix))
            if field:
                return field, clean_value((rest.strip() + " " + tail).strip())
        elif tail.startswith(":"):
            field = ALIAS.get(normalized_inside)
            if field:
                return field, clean_value(tail[1:].strip())
        else:
            field = ALIAS.get(normalized_inside)
            if field:
                return field, clean_value(tail) if tail else ""

    if ":" in value:
        prefix, rest = value.split(":", 1)
        field = ALIAS.get(normalize_label(prefix))
        if field:
            return field, clean_value(rest)

    return None, None


def heading_title(line):
    match = re.match(r"^#{4,6}\s+(.+)$", line.strip())
    if not match:
        return None
    title = clean_value(match.group(1)).strip("* ").strip()
    if title and normalize_label(title) not in BAD_TITLES:
        return title
    return None


def inline_title(line):
    stripped = line.strip()

    match = re.match(r"^\*\*(.+?)\*\*$", stripped)
    if match:
        title = clean_value(match.group(1))
        if ":" not in title and normalize_label(title) not in BAD_TITLES:
            return title

    if stripped.startswith("**") and ":" not in stripped:
        title = clean_value(stripped[2:])
        if title and normalize_label(title) not in BAD_TITLES:
            return title

    return None


def parse_bank_number(value):
    match = BANK_RE.search(normalize_spaces(value).upper())
    if not match:
        return ""
    return f"{match.group(1)} {match.group(2)} {match.group(3)}"


def parse_records(markdown):
    lines = split_multi_label_lines(markdown).splitlines()

    bank_points = []
    for idx, line in enumerate(lines):
        field, value = extract_label_value(line)
        if field != "bank_number":
            continue

        bank_value = value
        if not bank_value:
            pointer = idx + 1
            while pointer < len(lines):
                nxt = lines[pointer].strip()
                if not nxt:
                    pointer += 1
                    continue
                bank_value = nxt[1:].strip() if nxt.startswith(":") else nxt
                break

        bank = parse_bank_number(bank_value)
        if bank:
            bank_points.append((idx, bank))

    records = []
    for idx, (bank_idx, bank_number) in enumerate(bank_points):
        prev_bank_idx = bank_points[idx - 1][0] if idx else -1

        title_index = None
        title = ""
        for scan in range(bank_idx - 1, prev_bank_idx, -1):
            candidate = heading_title(lines[scan])
            if candidate:
                title_index = scan
                title = candidate
                break

        if title_index is None:
            for scan in range(bank_idx - 1, prev_bank_idx, -1):
                candidate = inline_title(lines[scan])
                if candidate:
                    title_index = scan
                    title = candidate
                    break

        if title_index is None:
            title_index = max(prev_bank_idx + 1, 0)
            title = clean_value(lines[title_index].lstrip("#").strip("* "))

        block = lines[title_index : bank_idx + 1]
        record = {field: "" for field in FIELDS}
        record["title"] = title
        record["bank_number"] = bank_number

        block_idx = 0
        while block_idx < len(block):
            field, immediate = extract_label_value(block[block_idx])
            if not field:
                block_idx += 1
                continue

            values = []
            if immediate:
                values.append(immediate)

            scan = block_idx + 1
            while scan < len(block):
                nxt = block[scan].strip()
                if not nxt:
                    scan += 1
                    continue

                next_field, _ = extract_label_value(block[scan])
                if next_field or re.match(r"^#{1,6}\s+", nxt):
                    break

                values.append(nxt[1:].strip() if nxt.startswith(":") else nxt)
                scan += 1

            value = clean_value(" ".join(values))
            if value:
                record[field] = value
            block_idx = scan

        if not record["last_updated"]:
            match = re.search(
                r"(?:Last updated|Derni[eè]re mise [aà] jour)\s*:?\s*([0-9]{4}(?:-[0-9]{2}(?:-[0-9]{2})?)?)",
                lines[bank_idx],
                re.I,
            )
            if match:
                record["last_updated"] = match.group(1)

        records.append(record)

    deduped = []
    seen = set()
    for record in records:
        key = (record["bank_number"], record["title"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def normalize_series(series):
    return "PCU" if series.upper() == "POU" else series.upper()


def key_parts(bank_number):
    match = BANK_RE.search(normalize_spaces(bank_number).upper())
    if not match:
        return "", "", ""
    org = match.group(1).upper()
    series = normalize_series(match.group(2))
    number = match.group(3)
    if org == "SCT":
        org = "TBS"
    return org, series, number


def full_key(bank_number):
    org, series, number = key_parts(bank_number)
    return f"{org} {series} {number}".strip()


def short_key(bank_number):
    _, series, number = key_parts(bank_number)
    return f"{series} {number}".strip()


def merge_records(en_records, fr_records):
    en_map = defaultdict(deque)
    fr_map = defaultdict(deque)
    order = []
    seen = set()

    for record in en_records:
        key = short_key(record["bank_number"])
        en_map[key].append(record)
        if key not in seen:
            seen.add(key)
            order.append(key)

    for record in fr_records:
        key = short_key(record["bank_number"])
        fr_map[key].append(record)
        if key not in seen:
            seen.add(key)
            order.append(key)

    rows = []
    for key in order:
        total = max(len(en_map[key]), len(fr_map[key]))
        for _ in range(total):
            en = en_map[key].popleft() if en_map[key] else {field: "" for field in FIELDS}
            fr = fr_map[key].popleft() if fr_map[key] else {field: "" for field in FIELDS}
            rows.append(
                {
                    "bank_number_key": full_key(en["bank_number"]) or full_key(fr["bank_number"]) or key,
                    "title_en": clean_value(en["title"]),
                    "title_fr": clean_value(fr["title"]),
                    "bank_number_en": en["bank_number"],
                    "bank_number_fr": fr["bank_number"],
                    "description_en": en["description"],
                    "description_fr": fr["description"],
                    "class_of_individuals_en": en["class_of_individuals"],
                    "class_of_individuals_fr": fr["class_of_individuals"],
                    "note_en": en["note"],
                    "note_fr": fr["note"],
                    "social_insurance_number_en": en["social_insurance_number"],
                    "social_insurance_number_fr": fr["social_insurance_number"],
                    "purpose_en": en["purpose"],
                    "purpose_fr": fr["purpose"],
                    "consistent_uses_en": en["consistent_uses"],
                    "consistent_uses_fr": fr["consistent_uses"],
                    "retention_and_disposal_standards_en": en["retention_and_disposal_standards"],
                    "retention_and_disposal_standards_fr": fr["retention_and_disposal_standards"],
                    "rda_number_en": en["rda_number"],
                    "rda_number_fr": fr["rda_number"],
                    "related_record_number_en": en["related_record_number"],
                    "related_record_number_fr": fr["related_record_number"],
                    "last_updated_en": en["last_updated"],
                    "last_updated_fr": fr["last_updated"],
                    "tbs_registration_en": en["tbs_registration"],
                    "tbs_registration_fr": fr["tbs_registration"],
                }
            )
    return rows


def process_folder(folder: Path):
    en_path = folder / "infosource_en.md"
    fr_path = folder / "infosource_fr.md"
    if not en_path.exists() or not fr_path.exists():
        return "skip", 0, 0, 0

    en_records = parse_records(en_path.read_text(encoding="utf-8", errors="replace"))
    fr_records = parse_records(fr_path.read_text(encoding="utf-8", errors="replace"))
    if not en_records and not fr_records:
        return "skip", 0, 0, 0

    rows = merge_records(en_records, fr_records)
    out_path = folder / "pib_table_en_fr.csv"
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return "processed", len(en_records), len(fr_records), len(rows)


def main():
    if len(sys.argv) != 2:
        print("Usage: build_pib_table_from_markdown.py <institution_folder>", file=sys.stderr)
        return 1

    folder = Path(sys.argv[1]).resolve()
    if not folder.exists() or not folder.is_dir():
        print(f"Invalid folder: {folder}", file=sys.stderr)
        return 1

    status, en_count, fr_count, merged_count = process_folder(folder)
    if status == "skip":
        print(f"SKIP {folder.name} (no PIB content in markdown)")
        return 2

    print(f"OK {folder.name}: en={en_count} fr={fr_count} merged={merged_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
