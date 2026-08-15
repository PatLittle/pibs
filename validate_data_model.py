#!/usr/bin/env python3
"""Validate declared primary keys, foreign keys, and controlled values."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


MODEL_PATH = Path("data_model.json")


def main() -> None:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    frames: dict[str, pd.DataFrame] = {}
    errors: list[str] = []
    for name, table in model["tables"].items():
        path = Path(table["path"])
        if not path.exists():
            errors.append(f"{name}: missing {path}")
            continue
        frame = pd.read_csv(path, dtype=str).fillna("")
        frames[name] = frame
        key = table.get("primary_key", [])
        missing_columns = [column for column in key if column not in frame.columns]
        if missing_columns:
            errors.append(f"{name}: missing key columns {missing_columns}")
            continue
        if key and frame[key].eq("").any(axis=1).any():
            errors.append(f"{name}: blank primary-key values")
        if key and frame.duplicated(key).any():
            errors.append(f"{name}: duplicate primary keys")

    for name, table in model["tables"].items():
        if name not in frames:
            continue
        for foreign in table.get("foreign_keys", []):
            target_name = foreign["references"]
            if target_name not in frames:
                continue
            fields = foreign["fields"]
            target_fields = foreign["reference_fields"]
            source = frames[name][fields].astype(str)
            target = frames[target_name][target_fields].astype(str)
            target_keys = set(map(tuple, target.itertuples(index=False, name=None)))
            missing = {
                key for key in map(tuple, source.itertuples(index=False, name=None))
                if any(key) and key not in target_keys
            }
            if missing:
                errors.append(f"{name}: {len(missing)} missing keys for {target_name}: {sorted(missing)[:10]}")

    links = frames.get("pib_cor_links")
    classes = frames.get("institution_classes_of_records")
    standard = frames.get("standard_classes_of_records")
    if links is not None and classes is not None and standard is not None:
        institution_targets = set(
            map(
                tuple,
                classes[["institution_id", "record_number"]].itertuples(index=False, name=None),
            )
        )
        standard_targets = set(standard["record_number"])
        resolved_links = links[links["resolved"].str.casefold().eq("true")]
        for row in resolved_links.to_dict("records"):
            scope = row["relationship_scope"]
            target = row["cor_record_number"]
            if scope == "institution_specific":
                if (row["institution_id"], target) not in institution_targets:
                    errors.append(
                        "pib_cor_links: resolved institution-specific target is missing: "
                        f"{row['institution_id']} / {target}"
                    )
            elif scope == "standard":
                if target not in standard_targets:
                    errors.append(
                        f"pib_cor_links: resolved standard target is missing: {target}"
                    )
            else:
                errors.append(f"pib_cor_links: unknown relationship scope: {scope}")

    if errors:
        raise SystemExit("Data-model validation failed:\n- " + "\n- ".join(errors))
    print(
        "Validated data model: "
        + ", ".join(f"{name}={len(frame)}" for name, frame in frames.items())
    )


if __name__ == "__main__":
    main()
