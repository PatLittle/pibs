# Format Guide: Canadian Heritage

French name: Patrimoine canadien

Use `infosource_en.md` and `infosource_fr.md` to build a bilingual PIB table.

## Output file

- `pib_table_en_fr.csv`

## Output columns (exact order)

- `bank_number_key`
- `title_en`, `title_fr`
- `bank_number_en`, `bank_number_fr`
- `description_en`, `description_fr`
- `class_of_individuals_en`, `class_of_individuals_fr`
- `note_en`, `note_fr`
- `social_insurance_number_en`, `social_insurance_number_fr`
- `purpose_en`, `purpose_fr`
- `consistent_uses_en`, `consistent_uses_fr`
- `retention_and_disposal_standards_en`, `retention_and_disposal_standards_fr`
- `rda_number_en`, `rda_number_fr`
- `related_record_number_en`, `related_record_number_fr`
- `last_updated_en`, `last_updated_fr`
- `tbs_registration_en`, `tbs_registration_fr`

All headers must be lowercase snake_case.

## Scope filter (important)

Only include Personal Information Bank entries, not general record classes.

A block is in scope only if it contains a PIB bank/file label such as:

- EN: `Bank Number`, `PIB Bank Number`
- FR: `Numéro de fichier`, `Numéro du FRP`, `Numéro de FRP`

And the value resolves to a bank id like `PCH PPU 078` (`<ORG> <SERIES> <3 digits>`).

## Field extraction rules

- `title`: nearest preceding PIB title line (prefer `##### ...`; fallback to standalone `**...**` line).
- Handle both markdown styles:
  - Definition list style:
    - `Description:`
    - `: value`
  - Inline bold style:
    - `**Description:** value`
    - `**Description :** value`
- Preserve full field text in one cell; collapse internal newlines to spaces.
- Leave missing fields blank.

## Label crosswalk

- `description`: `Description`
- `class_of_individuals`: `Class of Individuals` | `Catégorie de personnes`
- `note`: `Note` | `Nota` | `Remarque`
- `social_insurance_number`: `Social insurance number` | `Numéro d'assurance sociale`
- `purpose`: `Purpose` | `But`
- `consistent_uses`: `Consistent Uses` | `Usages compatibles`
- `retention_and_disposal_standards`: `Retention and Disposal Standards` | `Normes de conservation et de destruction`
- `rda_number`: `RDA Number` | `No. ADD` | `Numéro d'ADD` | `Numéro ADD`
- `related_record_number`: `Related Class of Record Number` | `Related Record Number` | `Renvoi au document no/numéro`
- `last_updated`: `Last updated` | `Dernière mise à jour`
- `tbs_registration`: `TBS Registration` | `Enregistrement (SCT)` | `Enregistrement du SCT` | `Enregistrement auprès du SCT`
- `bank_number`: `Bank Number` | `PIB Bank Number` | `Numéro de fichier` | `Numéro du FRP`

## EN/FR merge logic

1. Normalize bank numbers to a join key (`bank_number_key`): uppercase, single spaces.
2. Join EN and FR records on this key.
3. If duplicates exist for one key, pair by source order.
4. Keep unmatched side blank (should be rare; report if found).

## Validation checklist

- EN and FR PIB counts should be close and explainable.
- `bank_number_en` / `bank_number_fr` should match the same `bank_number_key`.
- No markdown label artifacts (`**`) should remain in values.
