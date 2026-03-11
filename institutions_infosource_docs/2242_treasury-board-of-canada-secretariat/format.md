# Format Guide: Treasury Board of Canada Secretariat

French name: Secrétariat du Conseil du Trésor du Canada

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

And the value resolves to a bank id like `TBS PCE 802` (`<ORG> <SERIES> <3 digits>`).

## Field extraction rules

- `title`: nearest preceding PIB title line.
  - First preference: markdown headings (`##### ...` / `###### ...`).
  - Fallback: standalone bold title lines (`**...**`) and malformed title lines starting with `**`.
- Handle both markdown styles:
  - Definition list style:
    - `Description:`
    - `: value`
  - Inline bold style:
    - `**Description:** value`
    - `**Description :** value`
- Support bold field headings with no inline value (for example `**Class of individuals**` on one line and value below).
- Preserve full field text in one cell; collapse internal newlines to spaces.
- Leave missing fields blank.

## Label crosswalk

- `description`: `Description`
- `class_of_individuals`: `Class of Individuals` | `Classes of Individuals` | `Catégorie(s) de personnes`
- `note`: `Note` | `Nota` | `Remarque`
- `social_insurance_number`: `Social insurance number` | `Numéro d'assurance sociale`
- `purpose`: `Purpose` | `But`
- `consistent_uses`: `Consistent Uses` | `Usages compatibles` | `Utilisations compatibles`
- `retention_and_disposal_standards`: `Retention and Disposal Standards` | `Normes de conservation et de destruction`
- `rda_number`: `RDA Number` | `No. ADD` | `Numéro d'ADD` | `Numéro ADD`
- `related_record_number`: `Related Class/Record Number` | `Renvoi au document no/numéro`
- `last_updated`: `Last updated` | `Dernière mise à jour`
- `tbs_registration`: `TBS Registration` | `Enregistrement (SCT)` | `Enregistrement du SCT` | `Enregistrement auprès du SCT`
- `bank_number`: `Bank Number` | `PIB Bank Number` | `Numéro de fichier` | `Numéro du FRP`

## EN/FR merge logic

1. Normalize join key to bank series + number (for example `PCE 802`) and use this to pair EN/FR rows.
2. Normalize known language variants for keying:
  - `SCT` org code corresponds to `TBS`
  - `POU` series corresponds to `PCU`
3. Set `bank_number_key` from normalized full key (`TBS PCE 802` style).
4. If duplicates exist for one key, pair by source order.
5. Keep unmatched side blank (should be rare; report if found).

## Validation checklist

- EN and FR PIB counts should be close and explainable.
- `bank_number_en` / `bank_number_fr` should map to the same `bank_number_key`.
- No label leakage between fields (for example `**Class of individuals**` text inside another field) after extraction.
