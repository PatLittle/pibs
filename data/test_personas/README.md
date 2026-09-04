# My Info synthetic personas

These fixtures are entirely fictional. They are designed to test the My Info
Beta questionnaire and must not be read as claims about any real person.

`personas.json` has two intentionally separate layers and declares its fixture
schema version in the top-level `schema_version` field:

- `display_name`, `summary`, `cv`, and `episodes` contain synthetic source
  material for persona cards and PDFs.
- `survey.answers` and `survey.refinements` contain only the controlled values
  accepted by the My Info engine. Narrative details, names, case numbers, exact
  travel details, and other free text must never be sent to the MCP service.

Each persona answers all 21 top-level questions. Every `yes` answer includes an
adaptive selection and an approximate timing for each selected option. The
`expectations` object records durable assertions and known gaps; it is not proof
that the fictional person would actually have a record in a named PIB.

The fixtures target contract `2026-09-04.4`, adaptive route version `2.0`, and
an assessment year of 2026. Update the fixture version and re-review every
expectation when the generated questionnaire contract changes.

The four PNGs in `portraits/` are generated editorial-cartoon portraits. They
depict fictional people and are embedded in the CV artifacts.

From the repository root, reproduce the evaluation and PDFs with:

```bash
.venv/bin/python scripts/evaluate_my_info_personas.py
.venv/bin/python scripts/render_my_info_personas.py --browser /snap/bin/chromium
```

Generated artifacts and a linked index are written to `generated/`.
