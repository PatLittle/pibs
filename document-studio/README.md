# Document Studio · Atelier documentaire

A standalone, browser-local visual editor for **one bilingual Markdown document at
a time**. Open [Document Studio](https://patlittle.github.io/pibs/document-studio/)
from the PIBs website footer. This directory owns the editor, schemas, templates,
source inventory, build tools, example and documentation. It has no runtime
framework, CDN, server account or connection to a document storage service.

## Write a document / Rédiger un document

1. Choose **New document / Nouveau document**, then a template. The default is a
   complete Info Source publication. All templates can also be browsed under All.
2. Write directly on the document. English and French are paired on the same page;
   changing the interface language does not remove either language. Bold, italic,
   lists and links are available in editable text. Template headings and fixed
   official wording stay locked to the selected document schema.
3. Use the outline to enter a section. Add a program, then an activity where
   applicable, a class of records, and the related PIBs. Breadcrumbs and **Back to
   parent section** provide a way out of every nested page. Add, duplicate, reorder
   and remove repeatable components; Undo restores changes.
4. Choose applicable Internal Services groups and standard descriptions. These are
   starting material, **not assertions that every standard applies** to an
   institution. Review disclosures, PIB status, SIN collection, identifiers and
   all institution-specific statements.
5. Save a **draft .md** at any time. Browser autosave is local to this browser and
   origin; download files to keep or share them. Multiple documents appear in the
   saved-drafts selector. Failed browser storage is reported without disabling
   downloads; unrecognized saved data is preserved with a recovery download.
6. Use **items to complete / éléments à compléter** to jump to missing or
   inconsistent fields. A review-ready `.md` download requires complete paired
   content and all implemented structural and relationship checks to pass.
   Review-ready is not legal compliance certification, a signature, TBS approval,
   submission, or publication. Nothing is emailed or uploaded.

Les mêmes étapes sont offertes en français. Un fichier contient toujours les
champs anglais et français. Les brouillons restent dans le navigateur et peuvent
être téléchargés en `.md`. Les modèles et les liens hiérarchiques sont contrôlés;
les faits, l’applicabilité et les approbations doivent être examinés par les
responsables compétents. Aucun envoi ni publication automatique n’a lieu.

## Template inventory and official sources

The initial library has **110 templates and reusable components**:

- The full Info Source publication; program, activity, class of records,
  institution-specific/central PIB, disclosure summary, class of personal
  information, manual and annual-update notification components.
- All **11 Internal Services groups**, with their source-defined class/PIB
  nesting; all **33 standard classes** and **49 standard PIBs**, captured in both
  languages. Program descriptions are presented once, activities are optional,
  and PIBs follow their containing class. Manuals sort by title on export.
- All five supplied TBS Word template families in English and French:
  **PIB Submission Form (A–N)**, **PIA Web Summary**, **Privacy Checklist**,
  **Privacy Impact Assessment**, and **Privacy Protocol**.
- A reusable participating-institution component, organization chart, and
  position/program assignments. Organization-chart fields are project extensions,
  not claimed requirements of the official Info Source publication.

Primary references:

- [Info Source Online Publishing Requirements](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/access-informatio-policies-guidance/programs-holdings-online-publishing-requirements.html),
  effective July 1, 2023. The superseded 2019 instructions are not the template authority.
- [Internal Services template](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/internal-services.html).
- [Standard classes](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-classes-records.html)
  and [standard PIBs](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html).
- [TBS forms](https://www.canada.ca/en/treasury-board-secretariat/corporate/forms.html).
  The exact EN/FR Word URLs, source checksums and inspection time are recorded in
  [sources.json](templates/sources.json).

[requirements.json](templates/requirements.json) maps requirements 4.1–4.10 and
Word-source field/table locations to schema components. [forms.json](templates/forms.json)
retains every heading, paragraph and table from the four large Word template
families in both languages. The PIB A–N fields have their own explicit schema;
its Annex A categories and Annex B code explanations remain available in the
linked official forms. [library.json](templates/library.json) retains standard
content and the two official bilingual Info Source boilerplates. The Additional
Information text fills the institution, ATIP contact, fee payee, informal contact
and language-specific links from authored fields, omitting the optional open-data
sentence when no open-data links apply.

Some published Internal Services anchors are stale, mistyped or point to banks
that TBS has since consolidated. `sources.json.link_exceptions` retains the
original fragments/labels and resolution evidence. Current English template links
establish nesting; French descriptions are independently keyed to the current
French standard descriptions. Conflicting French links do not silently change
bank identity. The former PSE 917 and surveillance/visitor-log references resolve
to PSU 907 only through the current TBS note explicitly describing that consolidation.
A future new/removed standard identifier stops a source refresh for review.

The Word models retain fixed question rows and all source guidance. Repeated
sets include handling/data-flow records, process steps, systems, access
inventories, risk/action-plan rows, and participating institutions. Applicable
tables need rows; a table marked not applicable needs a bilingual explanation.
Action-plan rows also capture a responsible lead and target date. Fixed questions
stay fixed and cannot be deleted. Conditional not-applicable answers are an
explicit editor accommodation: where the original answer cell offers only Yes/No,
the schema marks `x-conditional-na-extension`, and requires a bilingual explanation.
It does not automatically determine whether an assessment or protocol is legally
required. Source guidance remains available alongside each section. Guidance and
blank source examples are omitted from review-ready Markdown; authored answers,
questions, tables and fixed publication wording remain.

Government source material is attributed to Canada.ca and its published
[terms](https://www.canada.ca/en/transparency/terms.html). Source descriptions and
instructions are parsed as template data, never executed as commands. The editor
preserves the source document's stated mandatory/non-mandatory context.

## People, positions and program assignments

The People section creates a **chain-of-command chart for DG-and-above positions**.
Each position entry has a stable `id` and captures:

| Field | Treatment |
|---|---|
| Name | Proper name; no invented translation |
| Position title | Required English and French |
| Role level | DG, ADM, associate DM, deputy head or equivalent senior role |
| Classification | Group and level together when applicable; leave both empty otherwise |
| Position number | Optional official position identifier |
| Organization/unit | Required bilingual labels |
| Reports to | Another position-entry ID in this document; may be empty for an unrecorded/top-level manager |
| Programs | **At least one per position** for review-ready output; repeat for multiple responsibilities |
| Dates and source | Optional effective interval and official source URL |

The component is called `person` in version 1 of the schema, but its ID represents
this **position entry and named occupant**, not a verified cross-government person
identity. Changing an occupant's name keeps the position entry ID. Reporting links
connect these entries, not name strings. Unknown managers, self-links and cycles
are flagged. A top-level blank means no manager is recorded; it does not prove an
institution has no superior organization. The chart never infers rank or command
from a title, classification or shared program.

Assign a local document program or choose an organization-scoped program code
from the collected Service Inventory. Manually authored assignments are also
supported. Local references use `document_program_id`; changing that program's
name/code updates its explicit assignments. External references retain
`owner_org + program_id`, matching the knowledge graph's program identity;
`program_id` is not assumed globally unique or equated to an InfoBase numeric ID.
The suggested inventory is a snapshot of observed codes, not evidence that a
particular official is responsible for them. Authors explicitly make assignments.
The chart shows names, bilingual positions, classifications, units and programs;
click a position to edit it. The `.md` also contains a Mermaid chart and the full
position records. No real official names or reporting lines are prefilled.

The [example JSON](examples/organization-chart.json) and
[example Markdown](examples/organization-chart.md) contain **fictional people,
organization and program**. Open either through the editor to try the chart.

## Markdown and schema contract

`templates/document.schema.json` is **JSON Schema Draft 2020-12**, version `1.0.0`.
It has a strict document envelope and typed component definitions; unknown fields
and unknown document kinds are rejected. Components have stable IDs. English and
French content use `{ "en": "...", "fr": "..." }`; dedicated identifier, date,
proper-name, email and URL fields remain neutral values. Proper names within a
bilingual narrative can be repeated unchanged; no translation of names is invented. Optional
formatted values explicitly permit the empty string in JSON Schema.

An exported `.md` contains JSON front matter (JSON is valid YAML) and the readable
bilingual Markdown body. The front matter carries the complete typed document,
including IDs, relations and the selected schema version. The body is generated
from that data. This keeps a single portable `.md` while allowing lossless reopen,
schema checks, repeating components and diagrams. Raw HTML is escaped and links
are limited to HTTP(S) in the editor/body renderer.

- **Draft:** types, keys, fixed text and identity structure are checked. Required
  content may still be blank, and reporting/format problems may be awaiting repair.
- **Review-ready:** full JSON Schema field constraints plus bilingual,
  disclosure/SIN/submission, conditional-answer, table applicability, program
  assignment, reporting-link and date-order checks must pass.
- **Import:** accepts this typed `.md` format or its structured `.json` envelope.
  Arbitrary Markdown and Word documents are not silently converted. A visible
  Markdown body edited outside the app must match its structured data; otherwise
  import stops and preserves the current draft. Edit through the studio or edit
  the JSON data and regenerate; no mismatched body text is discarded.
- Fixed source wording is enforced by JSON Schema constants. Schema/renderer
  contract changes need a version change and an explicit migration; version 1
  does not invent migrations or overwrite unrecognized saved data.
- Typed names in approval sections are text, not electronic signatures.

The browser/Node validator intentionally implements the schema keywords used here
and rejects unsupported validation keywords. Python's independent `jsonschema`
validator checks the formal schema and the complete example. The browser's extra
relationship/content rules are implemented in `model.mjs`, with checks in tests.

## Files to edit and extending templates

| File | Purpose |
|---|---|
| `index.html`, `studio.css`, `studio.mjs` | Visual editor and document navigation |
| `model.mjs` | Defaults, IDs, validation, program references and chart layout |
| `markdown.mjs`, `vocabulary.mjs` | Safe rendering, bilingual labels and file round-trip |
| `tools/build_templates.py` | Authored Info Source schema and template/library builder |
| `tools/forms.py` | Safe OpenXML extraction and Word-question/table schemas |
| `templates/*.json` | Generated owning schema, catalogue and captured-source metadata |
| `examples/*` | Fictional complete example, not institutional source data |
| `README.md` | User, schema, source and maintenance guide |

To add a document family, add a typed definition in the builder, expose it through
`public_kinds` and the catalogue, assign bilingual labels, document source authority,
and add source/round-trip/browser coverage. Use reusable definitions for repeated
sets; keep identifiers separate from translated labels. Adding a new constraint
keyword also requires explicit support and tests in the browser validator.

Build offline from the captured metadata:

```sh
.venv/bin/python site/document-studio/tools/build_templates.py
.venv/bin/python -m unittest tests.test_document_studio
node --test tests/document-studio.test.mjs
python3 -m http.server 8772 --directory site
```

Then open `http://localhost:8772/document-studio/`. Browser checks use
`tests/document-studio.browser.cjs` with Playwright and `GRAPH_TEST_BASE`.

For a deliberate source refresh, download the four bilingual Info Source HTML
pages as `requirements[-fr].html`, `internal[-fr].html`, `classes[-fr].html` and
`banks[-fr].html`; download the five bilingual Word forms using the filenames in
`sources.json` (`pib-form-en.docx`/`pib-form-fr.docx` for the submission form).
Keep the downloads outside the checkout, then run:

```sh
.venv/bin/python site/document-studio/tools/build_templates.py --source-dir /path/to/captures
```

Review source hashes, alignment checks, link exceptions, additions/removals and
the requirement map before publishing. The `Info Source` current-source parser
fails if a bilingual standard entry disappears or the source catalogue count
changes. Word heading/block/table alignment changes also stop a refresh for review.
The normal site workflow builds offline and never downloads fresh Word templates.
