# Synthetic persona PDF pipeline

`scripts/render_my_info_personas.py` turns the versioned persona fixtures and
their completed My Info evaluations into two documents per persona:

- a polished synthetic CV/resume; and
- a survey-results report grouped by retention status and institution.

Every page is visibly marked **SYNTHETIC TEST PERSONA — NOT A REAL PERSON**.
The documents are test evidence, not a claim that any institution has records
about a real individual.

## Inputs

The default input paths are:

```text
data/test_personas/personas.json
data/test_personas/generated/evaluation.json
data/test_personas/portraits/<persona_id>.png
```

`personas.json` uses this envelope:

```json
{
  "schema_version": "1.0",
  "contract_version": "2026-08-22.3",
  "assessment_year": 2026,
  "personas": [
    {
      "id": "example_person",
      "display_name": "Example Person",
      "subtitle": "Short professional headline",
      "summary": "Short life-story summary.",
      "contact_line": "Optional fictional location",
      "cv": {
        "experience": [
          {
            "role": "Role",
            "organization": "Organization",
            "period": "2020–present",
            "description": "Context",
            "highlights": ["One concise point"]
          }
        ],
        "education": [],
        "memberships": [],
        "community_participation": [],
        "federal_interactions": [],
        "life_events": []
      },
      "survey": {
        "answers": [],
        "refinements": []
      },
      "episodes": []
    }
  ]
}
```

The canonical evaluation envelope is:

```json
{
  "personas": [
    {
      "persona_id": "example_person",
      "assessment": {},
      "summary": {},
      "results": [],
      "analysis": {}
    }
  ]
}
```

The renderer also accepts an `evaluation` or `survey_results` wrapper for
compatibility. It groups each result using `holding_status`, then
`institution_name`, mirroring the hierarchy and status palette used by the web
survey.

Portraits are required and must be PNG files named exactly for `persona_id`.
The renderer embeds the supplied portrait in the HTML; it deliberately does not
generate a placeholder when an image is absent.

## Generate artifacts

From the repository root:

```bash
.venv/bin/python scripts/render_my_info_personas.py
```

Output is retained under:

```text
data/test_personas/generated/<persona_id>/<persona_id>-cv.html
data/test_personas/generated/<persona_id>/<persona_id>-cv.pdf
data/test_personas/generated/<persona_id>/<persona_id>-survey-results.html
data/test_personas/generated/<persona_id>/<persona_id>-survey-results.pdf
```

To render one persona:

```bash
.venv/bin/python scripts/render_my_info_personas.py --persona-id example-person
```

To generate deterministic HTML intermediates without a browser:

```bash
.venv/bin/python scripts/render_my_info_personas.py --html-only
```

The renderer looks for Chromium, Chromium Browser, or Google Chrome. An exact
executable can be selected when auto-detection is unsuitable:

```bash
.venv/bin/python scripts/render_my_info_personas.py --browser /path/to/chromium
```

If the browser cannot be found or rendering fails, the command exits with an
actionable diagnostic. HTML generation remains available with `--html-only`.

## Reproducibility and review

The HTML is the deterministic source artifact: it contains no current date,
random identifiers, remote fonts, remote scripts, or network-loaded images.
Persona text is HTML-escaped and source links are restricted to HTTP(S). The
same fixtures produce byte-identical HTML.

Chromium writes its own PDF metadata, which may vary by browser version. For
visual regression work, record the Chromium version alongside the generated
PDFs and compare renders made with the same major version.

Run the focused test suite with:

```bash
.venv/bin/python -m unittest tests.test_render_my_info_personas
```

The PDF smoke test skips automatically if no Chromium-family browser is
available. The HTML determinism, escaping, source-link, and required-portrait
tests do not need a browser.
