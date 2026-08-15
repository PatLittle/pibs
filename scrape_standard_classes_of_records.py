#!/usr/bin/env python3
"""Download and normalize Canada's bilingual standard classes of records."""

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List

import requests
from bs4 import BeautifulSoup, Tag


URL_EN = (
    "https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/"
    "access-information/info-source/standard-classes-records.html"
)
URL_FR = (
    "https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-"
    "protection-renseignements-personnels/acces-information/info-source/"
    "categories-documents-ordinaires.html"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "standard_classes_of_records_en_fr.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PIBS-Standard-Classes-Scraper/1.0; "
        "+https://github.com/PatLittle/pibs)"
    )
}
CSV_COLUMNS = [
    "record_number",
    "record_number_en",
    "record_number_fr",
    "title_en",
    "title_fr",
    "description_en",
    "description_fr",
    "document_types_en",
    "document_types_fr",
    "url_en",
    "url_fr",
]


def clean_text(value: str) -> str:
    """Collapse HTML and non-breaking whitespace into normal spaces."""
    return re.sub(r"\s+", " ", (value or "").replace("\xa0", " ")).strip()


def fetch_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def paragraph_value(paragraph: Tag) -> tuple[str, str]:
    """Return the normalized strong-label and value from a source paragraph."""
    label_element = paragraph.find("strong")
    if label_element is None:
        return "", clean_text(paragraph.get_text(" ", strip=True))

    label = clean_text(label_element.get_text(" ", strip=True)).rstrip(":").strip().casefold()
    label_element.extract()
    return label, clean_text(paragraph.get_text(" ", strip=True))


def entry_paragraphs(heading: Tag) -> Iterable[Tag]:
    sibling = heading.find_next_sibling()
    while sibling is not None and sibling.name not in {"h2", "h3"}:
        if sibling.name == "p":
            yield sibling
        sibling = sibling.find_next_sibling()


def parse_page(url: str, language: str) -> List[Dict[str, str]]:
    prefix = "PRN" if language == "en" else "NDP"
    heading_pattern = re.compile(rf"^{prefix.lower()}(\d+)$")
    labels = {
        "description": "description",
        "document types": "document_types",
        "record number": "record_number_text",
    }
    if language == "fr":
        labels = {
            "description": "description",
            "types de documents": "document_types",
            "numéro du document": "record_number_text",
        }

    soup = fetch_soup(url)
    main = soup.find("main")
    if main is None:
        raise RuntimeError(f"Could not find the main content in {url}")

    records: List[Dict[str, str]] = []
    seen_codes = set()
    for heading in main.find_all(["h2", "h3"]):
        heading_id = clean_text(heading.get("id", "")).lower()
        match = heading_pattern.fullmatch(heading_id)
        if match is None:
            continue

        code = match.group(1)
        if code in seen_codes:
            raise RuntimeError(f"Duplicate {prefix} code {code} in {url}")
        seen_codes.add(code)

        fields = {"description": "", "document_types": "", "record_number_text": ""}
        for paragraph in entry_paragraphs(heading):
            label, value = paragraph_value(paragraph)
            field_name = labels.get(label)
            if field_name:
                fields[field_name] = value

        expected_number = f"{prefix} {code}"
        if fields["record_number_text"].upper() != expected_number:
            raise RuntimeError(
                f"Heading {heading_id} has unexpected record number "
                f"{fields['record_number_text']!r}; expected {expected_number!r}"
            )
        if not fields["description"] or not fields["document_types"]:
            raise RuntimeError(f"Missing normalized content for {expected_number}")

        records.append(
            {
                "record_number": code,
                "record_number_text": expected_number,
                "title": clean_text(heading.get_text(" ", strip=True)),
                "description": fields["description"],
                "document_types": fields["document_types"],
                "url": f"{url}#{heading_id}",
            }
        )

    if not records:
        raise RuntimeError(f"No {prefix} records found in {url}")
    return records


def merge_bilingual_records(
    english_records: List[Dict[str, str]], french_records: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    french_by_code = {record["record_number"]: record for record in french_records}
    english_codes = {record["record_number"] for record in english_records}
    french_codes = set(french_by_code)
    if english_codes != french_codes:
        raise RuntimeError(
            "The English PRN and French NDP codes do not match: "
            f"English only={sorted(english_codes - french_codes)}, "
            f"French only={sorted(french_codes - english_codes)}"
        )

    rows: List[Dict[str, str]] = []
    for english in english_records:
        french = french_by_code[english["record_number"]]
        rows.append(
            {
                "record_number": english["record_number"],
                "record_number_en": english["record_number_text"],
                "record_number_fr": french["record_number_text"],
                "title_en": english["title"],
                "title_fr": french["title"],
                "description_en": english["description"],
                "description_fr": french["description"],
                "document_types_en": english["document_types"],
                "document_types_fr": french["document_types"],
                "url_en": english["url"],
                "url_fr": french["url"],
            }
        )
    return rows


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT.name})",
    )
    args = parser.parse_args()

    english_records = parse_page(URL_EN, "en")
    french_records = parse_page(URL_FR, "fr")
    rows = merge_bilingual_records(english_records, french_records)
    write_csv(args.output.resolve(), rows)
    print(f"Wrote {len(rows)} bilingual standard classes of records to {args.output.resolve()}")


if __name__ == "__main__":
    main()
