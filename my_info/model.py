"""Normalize standard and institution-specific PIB rows into one source model."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_SPIB_PATH = Path("spib_en_fr.csv")
DEFAULT_PIB_PATH = Path("institutions_infosource_docs/pib_table_en_fr_all.csv")


@dataclass(frozen=True)
class PibRecord:
    """Source-faithful view of a PIB used by the feature derivation modules."""

    record_id: str
    scope: str
    institution_id: str
    gc_org_id: str
    institution_name_en: str
    institution_name_fr: str
    bank_number_key: str
    pib_type: str
    title_en: str
    title_fr: str
    description_en: str
    description_fr: str
    class_of_individuals_en: str
    class_of_individuals_fr: str
    note_en: str
    note_fr: str
    purpose_en: str
    purpose_fr: str
    consistent_uses_en: str
    consistent_uses_fr: str
    retention_en: str
    retention_fr: str
    source_url_en: str
    source_url_fr: str

    @property
    def text_en(self) -> str:
        return "\n".join(
            value
            for value in (
                self.title_en,
                self.description_en,
                self.class_of_individuals_en,
                self.note_en,
                self.purpose_en,
                self.consistent_uses_en,
            )
            if value
        )

    @property
    def text_fr(self) -> str:
        return "\n".join(
            value
            for value in (
                self.title_fr,
                self.description_fr,
                self.class_of_individuals_fr,
                self.note_fr,
                self.purpose_fr,
                self.consistent_uses_fr,
            )
            if value
        )


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _clean(value: str | None) -> str:
    return str(value or "").strip()


def _standard_record(row: dict[str, str]) -> PibRecord:
    key = _clean(row.get("bank_number_key"))
    return PibRecord(
        record_id=f"standard:{key}",
        scope="standard",
        institution_id="",
        gc_org_id="",
        institution_name_en="Government of Canada institutions",
        institution_name_fr="Institutions du gouvernement du Canada",
        bank_number_key=key,
        pib_type=_clean(row.get("pib_type")),
        title_en=_clean(row.get("entry_title_en")),
        title_fr=_clean(row.get("entry_title_fr")),
        description_en=_clean(row.get("description_en")),
        description_fr=_clean(row.get("description_fr")),
        class_of_individuals_en=_clean(row.get("class_of_individuals_en")),
        class_of_individuals_fr=_clean(row.get("class_of_individuals_fr")),
        note_en=_clean(row.get("note_en")),
        note_fr=_clean(row.get("note_fr")),
        purpose_en=_clean(row.get("purpose_en")),
        purpose_fr=_clean(row.get("purpose_fr")),
        consistent_uses_en=_clean(row.get("consistent_uses_en")),
        consistent_uses_fr=_clean(row.get("consistent_uses_fr")),
        retention_en=_clean(row.get("retention_disposal_en")),
        retention_fr=_clean(row.get("retention_disposal_fr")),
        source_url_en=_clean(row.get("url_en")),
        source_url_fr=_clean(row.get("url_fr")),
    )


def _institution_record(row: dict[str, str]) -> PibRecord:
    institution_id = _clean(row.get("institution_id"))
    key = _clean(row.get("bank_number_key"))
    return PibRecord(
        record_id=f"institution:{institution_id}:{key}",
        scope="institution",
        institution_id=institution_id,
        gc_org_id=_clean(row.get("gc_orgID")),
        institution_name_en=_clean(row.get("institution_name_en")),
        institution_name_fr=_clean(row.get("institution_name_fr")),
        bank_number_key=key,
        pib_type=_clean(row.get("pib_type")),
        title_en=_clean(row.get("title_en")),
        title_fr=_clean(row.get("title_fr")),
        description_en=_clean(row.get("description_en")),
        description_fr=_clean(row.get("description_fr")),
        class_of_individuals_en=_clean(row.get("class_of_individuals_en")),
        class_of_individuals_fr=_clean(row.get("class_of_individuals_fr")),
        note_en=_clean(row.get("note_en")),
        note_fr=_clean(row.get("note_fr")),
        purpose_en=_clean(row.get("purpose_en")),
        purpose_fr=_clean(row.get("purpose_fr")),
        consistent_uses_en=_clean(row.get("consistent_uses_en")),
        consistent_uses_fr=_clean(row.get("consistent_uses_fr")),
        retention_en=_clean(row.get("retention_and_disposal_standards_en")),
        retention_fr=_clean(row.get("retention_and_disposal_standards_fr")),
        source_url_en="",
        source_url_fr="",
    )


def load_pib_records(
    spib_path: Path = DEFAULT_SPIB_PATH,
    pib_path: Path = DEFAULT_PIB_PATH,
) -> list[PibRecord]:
    """Load every source row and fail if a normalized key would be ambiguous."""

    records = [_standard_record(row) for row in _read_rows(spib_path)]
    records.extend(_institution_record(row) for row in _read_rows(pib_path))
    missing_keys = [record.record_id for record in records if not record.bank_number_key]
    if missing_keys:
        raise ValueError(f"PIB rows with blank bank number keys: {missing_keys[:5]}")
    counts: dict[str, int] = {}
    for record in records:
        counts[record.record_id] = counts.get(record.record_id, 0) + 1
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate normalized PIB record IDs: {duplicates[:5]}")
    return records


def records_by_id(records: Iterable[PibRecord]) -> dict[str, PibRecord]:
    """Index already-normalized records by their stable source-scoped identifier."""

    materialized = list(records)
    result = {record.record_id: record for record in materialized}
    if len(result) != len(materialized):
        raise ValueError("Duplicate record IDs")
    return result
