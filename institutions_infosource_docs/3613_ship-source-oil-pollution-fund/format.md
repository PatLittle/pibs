# Format Guide: Ship Source Oil Pollution Fund

French name: Caisse d’indemnisation des dommages dus a la pollution par les hydrocarbures causée par les navires

Use the markdown files in this folder (`infosource_en.md`, `infosource_fr.md`) and parse each personal information bank block into a table with the exact columns below.

## Target table headings

- title
- Bank number
- Description
- Class of individuals
- . Note
- Social insurance number
- Purpose
- Consistent uses
- Retention and disposal standards
- RDA number
- Related record number
- Last updated

## Parsing notes

- `title`: the personal information bank title heading.
- Keep one row per bank entry.
- Map EN/FR labels to the target headings where labels vary by language.
- Preserve bank identifiers in `Bank number` exactly as shown in source text.
- Keep multiline values as plain text (single cell) when exporting.
- If a field is not present for an entry, leave it blank.

## Suggested extraction flow

1. Split markdown on bank-level headings.
2. Within each block, identify label-value lines for the target headings.
3. Normalize heading labels to the target schema.
4. Emit tabular output (CSV/JSON/DataFrame) with the headings above in order.
