# My Info persona test method

Persona testing separates human-readable life stories from the controlled
questionnaire state. A resume or narrative can contain rich context, but the
evaluator passes only answer values, adaptive route selections, and approximate
timing values to the canonical My Info engine.

## Fixture shape

`data/test_personas/personas.json` may use canonical state maps or MCP-style
update arrays. The minimal map form is:

```json
{
  "schema_version": "1.0",
  "contract_version": "2026-08-22.3",
  "assessment_year": 2026,
  "include_possible": false,
  "personas": [
    {
      "persona_id": "example-person",
      "name": "Example Person",
      "survey": {
        "locale": "en-CA",
        "answers": {
          "q_boating": {"value": "yes"}
        },
        "refinements": {
          "q_boating": {
            "selected_options": ["pleasure_craft_operator_card"],
            "timings": {
              "pleasure_craft_operator_card": {"kind": "within_1_year"}
            }
          }
        }
      },
      "expectations": {
        "expected_bank_numbers": ["TC PPU 023"],
        "expected_inventory_gaps": []
      }
    }
  ]
}
```

Optional expectation fields are `expected_record_ids`,
`expected_bank_numbers`, `known_expected_banks`,
`likely_false_positive_record_ids`, `likely_false_positive_bank_numbers`,
`unexpected_record_ids`, `unexpected_bank_numbers`, `allowed_record_ids`,
`allowed_bank_numbers`, and `expected_inventory_gaps`. Qualitative
`expected_ambiguities`, `known_false_positive_risks`, and
`known_false_negative_risks` are carried into the analysis but are not counted
as pass/fail assertions. An explicit allowlist is
required before an unlisted result is classified as an allowlist exception.

## Run

```bash
.venv/bin/python scripts/evaluate_my_info_personas.py
```

If the unversioned default is absent, the command uses
`data/test_personas/personas.v1.json`. Supplying `--input` always takes
precedence.

Use `--input`, `--output-dir`, and `--as-of-year` to override the defaults.
`--include-possible` audits broader candidate matching; `--strong-only` limits
the run to strong matches. Output is deterministic JSON plus a concise Markdown
analysis under `data/test_personas/generated/` by default.

## Metrics and interpretation

The report counts match bands, holding statuses, scope, institutions, adaptive
route coverage (`direct`, `fallback`, `partial`, and `inventory_gap`),
unanswered or incomplete state, retention unknowns, category coverage, and
fixture expectation outcomes. Automatic flags identify review targets, not
proof of an error. In particular, a high result count or unknown retention rule
requires investigation against the source PIB; neither is automatically a
false positive.

The ranked findings also distinguish results tied to an explicit route selector
from results associated only with a broad fallback parent. A bank-number match
under a different canonical `record_id` is reported as a fixture format issue,
not as a business-logic coverage failure.
