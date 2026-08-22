#!/usr/bin/env python3
"""Validate generated My Info feature datasets against their source records."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from my_info.categories import load_category_definitions
from my_info.interactions import questionnaire_questions
from my_info.model import load_pib_records


DEFAULT_DIR = Path("data/derived/my_info")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(output_dir: Path) -> dict[str, int]:
    records = load_pib_records()
    source_ids = {record.record_id for record in records}
    features = _rows(output_dir / "my_info_pib_features.csv")
    assignments = _rows(output_dir / "my_info_pib_category_assignments.csv")
    questionnaire = json.loads((output_dir / "my_info_questionnaire.json").read_text(encoding="utf-8"))
    summary = json.loads((output_dir / "my_info_summary.json").read_text(encoding="utf-8"))
    evidence = [
        json.loads(line)
        for line in (output_dir / "my_info_derivation_evidence.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]

    errors: list[str] = []
    if questionnaire.get("schema_version") != "1.2":
        errors.append("questionnaire JSON has an unexpected schema_version")
    if questionnaire.get("supported_locales") != ["en-CA", "fr-CA"]:
        errors.append("questionnaire JSON must declare equivalent English and French locales")
    if questionnaire.get("privacy", {}).get("state_owner") != "client":
        errors.append("questionnaire JSON must keep survey state client-owned")
    if questionnaire.get("data_snapshot", {}).get("source_files") != summary.get("source_files"):
        errors.append("questionnaire JSON source snapshot must match the build summary")
    feature_ids = [row["record_id"] for row in features]
    if len(feature_ids) != len(set(feature_ids)):
        errors.append("feature CSV has duplicate record_id values")
    if set(feature_ids) != source_ids:
        errors.append("feature CSV record IDs do not exactly match the source corpus")

    assignment_keys = [(row["record_id"], row["PI_CAT_ID"]) for row in assignments]
    if len(assignment_keys) != len(set(assignment_keys)):
        errors.append("category assignment CSV has duplicate record/category pairs")
    category_ids = set(load_category_definitions())
    unknown_categories = {row["PI_CAT_ID"] for row in assignments} - category_ids
    if unknown_categories:
        errors.append(f"unknown personal-information categories: {sorted(unknown_categories)}")
    unknown_assignment_records = {row["record_id"] for row in assignments} - source_ids
    if unknown_assignment_records:
        errors.append("category assignments reference unknown PIB records")

    declared_questions = {row["code"] for row in questionnaire["questions"]}
    expected_questions = {row["code"] for row in questionnaire_questions()}
    if declared_questions != expected_questions:
        errors.append("questionnaire JSON does not match the implemented question taxonomy")
    routes = questionnaire.get("adaptive_routes", [])
    routed_questions = [route.get("parent_question_code") for route in routes]
    if len(routed_questions) != len(set(routed_questions)):
        errors.append("adaptive routes contain duplicate parent questions")
    if set(routed_questions) - declared_questions:
        errors.append("adaptive routes reference undeclared parent questions")
    known_bank_numbers = {row["bank_number_key"] for row in features}
    for route in routes:
        option_codes = [option.get("code") for option in route.get("options", [])]
        if not option_codes or len(option_codes) != len(set(option_codes)):
            errors.append(f"{route.get('parent_question_code')}: invalid adaptive options")
        for option in route.get("options", []):
            missing = set(option.get("selectors", {}).get("bank_numbers", [])) - known_bank_numbers
            if missing:
                errors.append(
                    f"{route.get('parent_question_code')}.{option.get('code')}: "
                    f"unknown bank numbers {sorted(missing)}"
                )
    for question in questionnaire["questions"]:
        if question.get("readability_en", {}).get("method") != "flesch_reading_ease":
            errors.append(f"{question.get('code')}: missing English readability result")
        examples = question.get("help", {}).get("examples", [])
        if not examples:
            errors.append(f"{question.get('code')}: missing real-world examples")
        for example in examples:
            if not all(
                example.get(field)
                for field in ("institution_en", "institution_fr", "activity_en", "activity_fr")
            ):
                errors.append(f"{question.get('code')}: incomplete bilingual named example")
    used_questions = {
        code
        for row in features
        for code in row["question_codes"].split("|")
        if code
    }
    if used_questions - declared_questions:
        errors.append(f"feature rows use undeclared questions: {sorted(used_questions - declared_questions)}")

    evidence_ids = [row.get("record", {}).get("record_id") for row in evidence]
    if len(evidence_ids) != len(set(evidence_ids)) or set(evidence_ids) != source_ids:
        errors.append("evidence JSONL must contain exactly one object for every source record")
    if summary.get("record_count") != len(records):
        errors.append("summary record_count does not match source corpus")
    if summary.get("category_assignment_count") != len(assignments):
        errors.append("summary category_assignment_count does not match assignment CSV")

    for row in features:
        for field in ("category_ambiguous", "category_unclassified", "time_follow_up_required"):
            if row[field] not in {"true", "false"}:
                errors.append(f"{row['record_id']}: invalid boolean in {field}")
        for field in ("retention_minimum_years", "retention_maximum_years"):
            if row[field] and float(row[field]) < 0:
                errors.append(f"{row['record_id']}: negative value in {field}")

    if errors:
        raise ValueError("My Info validation failed:\n- " + "\n- ".join(errors))
    return {
        "records": len(features),
        "category_assignments": len(assignments),
        "evidence_records": len(evidence),
        "questions": len(declared_questions),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    counts = validate(args.output_dir)
    print(
        "Validated My Info datasets: "
        + ", ".join(f"{name}={count}" for name, count in counts.items())
    )


if __name__ == "__main__":
    main()
