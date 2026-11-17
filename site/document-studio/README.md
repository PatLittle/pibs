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
   choose **EN**, **FR**, or **BIL** above the paper to display one or both languages.
   The separate interface-language button changes navigation labels. Neither
   control removes translated content from the saved document. Bold, italic,
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
6. Choose **PDF details / Métadonnées** to supply authorship, rights, keywords and
   contact information. **Export PDF** downloads the current EN, FR or BIL view
   with embedded XMP/IPTC metadata and the organization chart where present.
   Incomplete documents receive a DRAFT / BROUILLON label. The `.md` remains the
   editable, bilingual source; PDF is a presentation copy.
7. Use **items to complete / éléments à compléter** to jump to missing or
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

The library has **118 templates and reusable components**:

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
- The remaining eight TBS ATIP form families: **material privacy breach report**,
  **access request**, **personal information request**, **consent**,
  **authorization**, **record correction**, and the **Access Act / Privacy Act
  statistical reports**. Together with the five Word families, these cover all
  **13 ATIP families** in the captured TBS register, before the unrelated Phoenix
  pay-system section. Browse **Privacy & PIA** or **Access forms**, or search by
  form number.
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

## ATIP preparation and official completion formats

[atip.json](templates/atip.json) records the 13 bilingual form entries, official
URLs, SHA-256 source checksums, HTML instructions, statistical input labels and
coordinates, and static breach-PDF field labels/instructions. Each form displays
its number and official EN/FR links. Source documents are reference material;
source instructions are never executed or treated as instructions to this app.

| TBS/SCT form | Studio option | Official completion consideration |
|---|---|---|
| 350-57 | Access request | Official request/signature/payment process |
| 350-58 | Personal information request | Official request/attestation process |
| 350-60E/F | Consent | Official signatures remain separate |
| 350-55E/F | Authorization | Official signatures remain separate |
| 350-11 | Record correction | Official correction/attestation process |
| 350-62 | Access Act statistics | Submit the official XML/XLS; Studio is a worksheet |
| 350-63 | Privacy Act statistics | Submit the official XML/XLS; Studio is a worksheet |
| 350-64E/F | Material privacy breach | Complete the official dynamic PDF in suitable desktop PDF software |
| 350-65E/F | Privacy checklist | Prescribed Word template |
| 350-66E/F | PIA | Prescribed Word template and approval process |
| 350-67E/F | PIB submission | Prescribed Word form |
| 350-68E/F | PIA web summary | Prescribed template and publication after approval |
| 350-69E/F | Privacy protocol | The template is non-mandatory and adaptable |

The breach model maps **all 175 source field identifiers** in each language.
Exclusive choices are grouped; independent checkboxes remain separate. The hidden
form-identification field is retained as locked administrative metadata. Original
reports have source-specific conditional completion checks; amendments require an
existing OPC file number and bilingual amendment summary and can leave other
sections blank. These checks do not reproduce Adobe JavaScript, signatures,
automated sending, or the original form’s dynamic behavior. Do not enter affected
individuals’ names/identifiers or sensitive system-security details; follow the
linked source instructions. Studio PDF is a preparation copy, not an official
filled submission form.

The statistical models retain **691 English / 692 French access-report inputs**
and **592 inputs per language for the privacy report**. Values are nonnegative
numeric strings, except institution name and reporting dates. Empty numeric cells
can explicitly be set to zero for one table. No official spreadsheet formulas or
cross-table reconciliation is claimed. The sources contain duplicate or differing
IDs and one French-only access cell with an empty source ID. Alignment uses exact
IDs with table/row/cell disambiguation, or verified coordinates; every exception is
recorded in `atip.json`. The French-only cell is retained with its French source
label in the English column as well, rather than inventing a translation.
`requirements.json.atip_fields` maps every statistical and breach field to its
source ID(s). Existing Word coverage stays under `form_fields`.

## PDF and embedded metadata

PDFs are generated locally using bundled **pdf-lib 1.17.1**, **@pdf-lib/fontkit
1.1.1**, and embedded Noto Sans regular/bold fonts. No external PDF service receives
the document. Assets load only on PDF export. French accents are retained as real
text; unsupported characters produce an explicit error instead of disappearing.
The PDF body follows EN/FR/BIL; the canonical `.md` always retains both languages.
Bilingual text uses two columns. Position records appear in full, with a vector
chain-of-command diagram on a separate page. Long content paginates.

Each PDF includes the PDF Info dictionary and a catalog-linked `/Metadata` XML
stream containing RDF XMP. IPTC Core and IPTC Extension properties are embedded
**inside that XMP packet**, the appropriate mapping for PDF; legacy JPEG IPTC-IIM
blocks are not added. Automatic metadata includes document/schema identity,
selected language(s), draft/review status, creation/modification times, creator
software, a stable DocumentID, a fresh InstanceID, and official form number/source
URLs when applicable. Author-supplied metadata includes bilingual title,
description, copyright and usage terms; creators, keywords, credit, source,
headline, writer, instructions, creation date, rights link, subject/scene codes,
country code, digital-source type and structured creator contact information.

**All supplied applicable metadata is embedded; unspecified fields remain absent.**
Studio does not fabricate ownership, creators, contact details, or irrelevant
photo/camera/location data. Advanced additional properties support any valid,
non-reserved namespace and text, Bag, Seq, language-alternative and structured
RDF values. Populated standard fields cannot be overridden by an additional
property. Example additional property (the `value` is a JSON string):

```json
[{"namespace":"http://iptc.org/std/Iptc4xmpExt/2008-02-29/","prefix":"Iptc4xmpExt","property":"OrganisationInImageName","type":"bag","value":"[\"Example institution\"]"}]
```

Metadata is retained in the document’s optional `metadata` object for later edits
and `.md` reopen. EN/FR PDF bodies contain the chosen language; metadata may still
contain bilingual title/rights alternatives. Exported files are not PDF/A,
electronically signed, encrypted, or tagged accessible PDFs. Official submission
and accessible publication requirements need their own review.

References: [pdf-lib API](https://pdf-lib.js.org/docs/api/classes/pdfdocument),
[IPTC Photo Metadata standard](https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2025.1.html).
Bundled asset origins/checksums are in [vendor/manifest.json](vendor/manifest.json),
with upstream MIT notices and the font SIL Open Font License alongside the assets.

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
| `pdf.mjs`, `metadata.mjs`, `fonts/`, `vendor/` | Local PDF rendering, embedded XMP/IPTC and licensed dependencies |
| `tools/atip.py`, `atip-validation.mjs` | ATIP register, captured HTML/PDF field models and conditional breach checks |
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
node --test tests/document-studio.test.mjs tests/document-studio-pdf.test.mjs
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

To refresh the additional ATIP captures, keep the seven bilingual HTML pairs named
`350-57-en.html`, `350-57-fr.html`, etc., and the breach PDFs named
`350-64e-eng.pdf` / `350-64-fr.pdf` outside the checkout. Run the builder with
`--atip-source-dir /path/to/captures`. This capture-only path additionally needs
`pdfminer.six` and `pdfplumber`; it extracts static fields/text without running PDF
JavaScript. Inspect alignment exceptions and source-field coverage before committing.
PDF tests use `pdfplumber` to independently inspect the actual PDF text, XMP,
IPTC Core/Extension and PDF Info, rather than only checking exporter internals.
Schema additions are backward-compatible within version 1.0.0: earlier documents
without the optional metadata object and existing template bodies still reopen.
