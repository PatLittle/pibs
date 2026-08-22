#!/usr/bin/env python3
"""Build auditable derived datasets for the My Info PIB finder."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from my_info.categories import classify_records, load_category_definitions
from my_info.adaptive import ADAPTIVE_ROUTE_VERSION, adaptive_routes
from my_info.interactions import (
    coverage_report,
    derive_interaction_features,
    questionnaire_questions,
)
from my_info.model import DEFAULT_PIB_PATH, DEFAULT_SPIB_PATH, PibRecord, load_pib_records
from my_info.retention import derive_retention


DEFAULT_OUTPUT_DIR = Path("data/derived/my_info")
GENERATOR_VERSION = "1.2"


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _codes(items: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> str:
    return "|".join(sorted({str(item["code"]) for item in items}))


def _max_confidence(items: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> str:
    if not items:
        return ""
    return f"{max(float(item['confidence']) for item in items):.2f}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def _basic_record(record: PibRecord) -> dict[str, str]:
    return {
        "record_id": record.record_id,
        "scope": record.scope,
        "institution_id": record.institution_id,
        "gc_orgID": record.gc_org_id,
        "institution_name_en": record.institution_name_en,
        "institution_name_fr": record.institution_name_fr,
        "bank_number_key": record.bank_number_key,
        "pib_type": record.pib_type,
        "title_en": record.title_en,
        "title_fr": record.title_fr,
        "source_url_en": record.source_url_en,
        "source_url_fr": record.source_url_fr,
    }


def derive_outputs(records: list[PibRecord]) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Derive compact rows, normalized category rows, and full evidence records."""

    category_results = classify_records(records)
    feature_rows: list[dict[str, Any]] = []
    category_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []

    for record, category_result in zip(records, category_results, strict=True):
        retention = derive_retention(record)
        interactions = derive_interaction_features(asdict(record), source_kind=record.scope)
        topics = list(interactions["interaction_topics"])
        roles = list(interactions["individual_roles"])
        actions = list(interactions["service_actions"])
        candidate_questions = list(interactions["question_triggers"])
        questions = list(interactions["primary_question_triggers"])
        unmapped = sorted({item.concept for item in category_result.unmapped_evidence})
        category_ids = list(category_result.category_ids)

        feature_rows.append({
            **_basic_record(record),
            "category_ids": "|".join(category_ids),
            "category_count": len(category_ids),
            "category_max_confidence": (
                f"{max(item.confidence for item in category_result.assignments):.2f}"
                if category_result.assignments else ""
            ),
            "category_ambiguous": str(category_result.ambiguous).lower(),
            "category_unclassified": str(category_result.unclassified).lower(),
            "unmapped_concepts": "|".join(unmapped),
            "interaction_topic_codes": _codes(topics),
            "interaction_topic_max_confidence": _max_confidence(topics),
            "individual_role_codes": _codes(roles),
            "service_action_codes": _codes(actions),
            "question_codes": _codes(questions),
            "question_count": len(questions),
            "candidate_question_codes": _codes(candidate_questions),
            "candidate_question_count": len(candidate_questions),
            "time_follow_up_required": str(bool(questions)).lower(),
            "privacy_caveat_codes": _codes(list(interactions["privacy_caveats"])),
            "retention_rule_type": retention.rule_type,
            "retention_reference_events": "|".join(retention.reference_events),
            "retention_minimum_years": "" if retention.minimum_years is None else retention.minimum_years,
            "retention_maximum_years": "" if retention.maximum_years is None else retention.maximum_years,
            "retention_disposition": retention.disposition,
            "retention_confidence": retention.confidence,
            "retention_language_agreement": retention.language_agreement,
            "retention_requires_institution_contact": str(retention.requires_institution_contact).lower(),
            "retention_requires_schedule_lookup": str(retention.requires_schedule_lookup).lower(),
            "retention_has_indefinite_component": str(retention.has_indefinite_component).lower(),
            "retention_has_immediate_disposal": str(retention.has_immediate_disposal).lower(),
            "retention_is_under_review": str(retention.is_under_review).lower(),
            "retention_text_en": retention.raw_text_en,
            "retention_text_fr": retention.raw_text_fr,
        })

        for assignment in category_result.assignments:
            category_rows.append({
                "record_id": record.record_id,
                "scope": record.scope,
                "institution_id": record.institution_id,
                "bank_number_key": record.bank_number_key,
                "PI_CAT_ID": assignment.category_id,
                "confidence": f"{assignment.confidence:.2f}",
                "evidence_count": len(assignment.evidence),
                "evidence_json": _json([asdict(item) for item in assignment.evidence]),
            })

        evidence_rows.append({
            "record": _basic_record(record),
            "categories": category_result.to_dict(),
            "interactions": interactions,
            "retention": retention.to_dict(),
        })
    return feature_rows, category_rows, evidence_rows


def write_outputs(
    output_dir: Path,
    feature_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    *,
    spib_path: Path,
    pib_path: Path,
    generated_date: str,
) -> dict[str, Any]:
    """Write deterministic datasets and a compact quality summary."""

    output_dir.mkdir(parents=True, exist_ok=True)
    feature_fields = list(feature_rows[0]) if feature_rows else []
    category_fields = list(category_rows[0]) if category_rows else [
        "record_id", "scope", "institution_id", "bank_number_key", "PI_CAT_ID",
        "confidence", "evidence_count", "evidence_json",
    ]
    _write_csv(output_dir / "my_info_pib_features.csv", feature_rows, feature_fields)
    _write_csv(output_dir / "my_info_pib_category_assignments.csv", category_rows, category_fields)

    with (output_dir / "my_info_derivation_evidence.jsonl").open("w", encoding="utf-8", newline="") as handle:
        for row in evidence_rows:
            handle.write(_json(row) + "\n")

    definitions = load_category_definitions()
    source_snapshot = {
        str(spib_path): {"sha256": _sha256(spib_path)},
        str(pib_path): {"sha256": _sha256(pib_path)},
    }
    questionnaire = {
        "schema_version": "1.2",
        "content_version": f"{generated_date}.2",
        "generator_version": GENERATOR_VERSION,
        "data_snapshot": {
            "generated_date": generated_date,
            "source_files": source_snapshot,
        },
        "supported_locales": ["en-CA", "fr-CA"],
        "privacy": {
            "state_owner": "client",
            "free_text_required": False,
            "notice_en": "Do not provide account numbers, case details, health details, or other sensitive free text.",
            "notice_fr": "Ne fournissez pas de numéros de compte, de détails de dossier, de renseignements sur la santé ou d'autres textes libres sensibles.",
        },
        "questions": questionnaire_questions(),
        "adaptive_route_version": ADAPTIVE_ROUTE_VERSION,
        "adaptive_routes": adaptive_routes(),
        "personal_information_categories": [
            asdict(definitions[key])
            for key in sorted(definitions, key=lambda value: int(value.split("-")[1]))
        ],
        "retention_statuses": ["likely_held", "likely_disposed", "uncertain"],
    }
    (output_dir / "my_info_questionnaire.json").write_text(
        json.dumps(questionnaire, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    primary_interaction_coverage = coverage_report(
        (row["interactions"] for row in evidence_rows),
        question_field="primary_question_triggers",
    )
    candidate_interaction_coverage = coverage_report(
        (row["interactions"] for row in evidence_rows),
        question_field="question_triggers",
    )
    summary = {
        "generator_version": GENERATOR_VERSION,
        "generated_date": generated_date,
        "source_files": source_snapshot,
        "record_count": len(feature_rows),
        "scope_counts": dict(sorted(Counter(row["scope"] for row in feature_rows).items())),
        "category_assignment_count": len(category_rows),
        "categorized_record_count": sum(bool(row["category_ids"]) for row in feature_rows),
        "category_unclassified_record_count": sum(row["category_unclassified"] == "true" for row in feature_rows),
        "category_ambiguous_record_count": sum(row["category_ambiguous"] == "true" for row in feature_rows),
        "retention_rule_counts": dict(sorted(Counter(row["retention_rule_type"] for row in feature_rows).items())),
        "questionnaire": {
            "primary": primary_interaction_coverage,
            "candidate": candidate_interaction_coverage,
        },
    }
    (output_dir / "my_info_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spib", type=Path, default=DEFAULT_SPIB_PATH)
    parser.add_argument("--pib", type=Path, default=DEFAULT_PIB_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generated-date", default=date.today().isoformat())
    args = parser.parse_args()

    records = load_pib_records(args.spib, args.pib)
    outputs = derive_outputs(records)
    summary = write_outputs(
        args.output_dir,
        *outputs,
        spib_path=args.spib,
        pib_path=args.pib,
        generated_date=args.generated_date,
    )
    print(
        f"Wrote My Info features for {summary['record_count']} PIB rows to {args.output_dir}; "
        f"category assignments={summary['category_assignment_count']}, "
        f"primary question matches={summary['questionnaire']['primary']['matched_question_count']}, "
        f"candidate question matches={summary['questionnaire']['candidate']['matched_question_count']}."
    )


if __name__ == "__main__":
    main()
