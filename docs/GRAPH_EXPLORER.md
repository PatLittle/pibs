# PIB / PIA network explorer

`site/graph.html` is a buildless Cytoscape.js page in the existing GitHub Pages
site. It uses native JavaScript and generated static data, with no database or
backend. Cytoscape.js 3.33.1 is vendored with its MIT licence in `site/vendor/`.
The existing GCDS header, prototype label, colours and navigation are retained.

## Explore

The initial page offers five bilingual, curated starting points: shared security
and staffing classes; the standard network-monitoring bank; CRA human-resources
analytics; and the Privacy Commissioner's Office 365 assessment. Counts come from
the current graph. Represented institutions means distinct institution IDs on
directly connected records, not proven adoption or shared personal information.
Each story opens a bounded view with a few institution paths. Supplied deep links
take precedence over the default view. Search text or either filter replaces the
examples with matching records; clearing all three restores the five examples.

**Start guided tour** offers 36 clickable spotlight stops ordered from starting
points and navigation to details, browsing, provenance, display and sharing.
Back/Next, a menu of every stop, Restart and Exit are always available; Escape
exits. The highlighted controls remain usable. Conditional panels open for their
steps, including on mobile. Finishing or exiting restores the previous graph,
selection, search, browser settings and URL. A fullscreen tour temporarily returns
to the page and restores fullscreen on exit. The GCDS header provides the sole
language switch; exit fullscreen to use it.

Standard PIBs and standard classes have dedicated search/list filter options.
Personal-information categories and PIB types are independent searchable nodes.
Record details show scope, institution, description, direct connection counts,
represented institutions, and expandable attributes such as purpose, people
covered, uses, retention and document types where available.

**Full screen** opens the graph and its record panel together. Browsers that
cannot grant native fullscreen use a viewport-filling workspace instead. The
exit button or Escape restores the page and keyboard focus. **Hide records**
temporarily gives the entire workspace to the graph. The guided tour and
graph controls remain available inside fullscreen, including on mobile.

The record panel has **Record** and **Browse records** tabs. Browse either the
selected record's connections or the full collected inventory, filter bilingual
names/aliases and record types, and choose 8, 16 or 24 records per page. List
pagination is independent of the drawing limit: it can browse all source records
without adding them all to the map. Selecting a list record opens its details;
**Previous record** and **Next record** follow that filtered list. The connection
anchor stays fixed while cycling, so navigation does not silently replace the
list with each new record's neighbours. **Connections of selected record**
explicitly starts a new connection list. Records outside the bounded visible
neighbourhood are brought into view or become a new graph root when necessary.

Cards, badges, list accents and type chips use the same colour values as the
diagram, with text labels so colour is not the only distinction. Record cards
show direct relationship/record counts and clickable neighbour-type counts,
following the active relationship filter.
**Most connected** sorts by observed direct-edge count across the collected
graph; it is a discovery aid, not a privacy-risk or completeness score. References
that need resolution remain labelled. **Highlight direct connections** dims
unrelated visible elements without hiding them or altering the graph's counts.
List paging and evidence inspection preserve the map's positions and viewport;
new topology triggers a layout. Fullscreen resizing fits the current view.

Search bilingual names, identifiers and recorded aliases; filter search by
institution or record type. Selecting a result opens its first 25 connections.
Select another node to retain the path and expand its neighbourhood. Use
**Show more connections** for additional batches, or **Start here** / **Reset
to selected node** to begin a new view. Rendering is capped at 250 nodes; the
interface reports that limit. A native keyboard-accessible connection list
offers the same navigation and evidence inspection even if the diagram fails.

Select an edge or **Inspect evidence** for source excerpts, original URLs,
repository paths, line numbers, collection dates and checksums. Controls and
record/graph labels switch between English and French. Missing source titles
fall back to the available language. Excerpts retain their source language.
Unavailable PIA collection entries remain explicitly labelled in details.

Table dialogs and PIA readers link into the graph; graph details link back to
those pages. **Copy view link** preserves root, selected node or edge,
expansion order/counts, relationship filter and language. Browser Back/Forward
restores these states. Positions, zoom and search-form values are transient.
Record-list filters, anchor and page are also transient. Fullscreen requires a
user action and is not automatically entered from a shared link.

Example using an actual assessment:

`graph.html?node=pia%3Aati-schedule-i-administrative-tribunals-support-service-of-canada%2Fpia-95a42118fc3d&lang=fr`

## Inputs and relationship meaning

| Canonical input | Use |
| --- | --- |
| `institution_registry.csv` | Institution identity, bilingual legal names and source URLs |
| `institutions_infosource_docs/pib_table_en_fr_all.csv` | Institutional PIBs, identifiers, bilingual titles/descriptions |
| `institutions_infosource_docs/cor_table_en_fr_all.csv` | Institutional Classes of Records |
| `spib_en_fr.csv`, `standard_classes_of_records_en_fr.csv` | Government-wide records, kept separate from institutional records |
| `pi_categories_en_fr.csv`, `pib_type_values.csv` | Category vocabulary and controlled PIB type nodes |
| `my_info/categories.py` | Existing deterministic description-based category rules, reused against current source rows |
| `institutions_infosource_docs/pib_cor_links.csv` | Existing compiled PIB/class references and resolution status |
| `PIAs/*/collection.json` | Assessment identities, availability, existing matches and line evidence |
| Referenced PIA Markdown, `PIAs/collection_manifest.json` | Verified source checksums and collection provenance |

| Predicate | Direction and evidence |
| --- | --- |
| `listed_by` | Record → institution: inventory attribution from the existing CSV/collection model |
| `references` | PIA → PIB/class: explicit reference extracted by `PIAs/reference_extraction.py` |
| `related_class` | PIB → class: compiled related-record reference, retaining literal reference, language, scope and resolution |
| `has_type` | PIB → type: exact controlled-value match from the source PIB type field |
| `category_match` | PIB → category: derived description-based match with source field, matched text, rule and confidence; dotted line and explicit derived label |

A citation does **not** assert that a PIA assesses the entire bank. No edges
are inferred from similar titles, shared institutions, laws or programs.
Category links reuse the existing classifier and remain estimated assignments;
they never create institution-to-standard-bank adoption edges or PIA citations.
Standard PIBs' explicit PRN/NDP references also resolve to standard classes;
unknown identifiers remain unresolved reference nodes. A PIA target must resolve to
one existing source-scoped node using upstream `matched_records`. Multiple
matches stay ambiguous rather than creating factual edges to every candidate.
Unresolved citations become `reference` nodes with distinct shape/colour and
dashed edges; these describe literal citations, not invented PIBs or classes.
An absent link does not establish that no assessment or relationship exists.

Opaque, stable node IDs:

- `institution:{institution_id}`
- `pib:{institution_id}:{bank_number_key}` / `pib:standard:{bank_number_key}`
- `class:{institution_id}:{record_number}` / `class:standard:{record_number}`
- `pia:{institution_id}/{pia_id}`
- `category:{PI_CAT_ID}` / `pib-type:{pib_code}`
- Reference/edge IDs are deterministic SHA-256 prefixes of the source/reference
  identity or source/target/predicate, independent of labels.

## Static assets and rebuild

With the repository's Python requirements installed, run from its root:

```sh
python build_site_assets.py
python validate_site.py
```

The existing build refreshes PIA references and reader assets, then generates
the graph. For a graph-only rebuild after the owning pipelines have run:

```sh
python scripts/build_graph.py
python scripts/validate_graph.py
```

`site/data/graph.json` contains schema version 2, nodes/edges, counts, collection
timestamp and SHA-256 hashes of consumed inputs. Each edge has an
`evidence_count` and `evidence_url` pointing to one of 32 static
`site/data/graph-evidence/*.json` shards. Shards map edge IDs to full evidence
arrays; their checksums appear in `evidence_files`. The browser loads and caches
provenance on edge inspection. Record descriptions are excerpts capped at
1,000 characters; complete content remains in the existing tables/readers.
PIB/class nodes also carry available source attributes. Relationships have an
explicit `basis` of `documented` or `derived`; resolution remains separate.
The classifier source hash is part of the consumed-input fingerprint.
Full attributes load on selection from 32 `graph-attributes/*.json` shards,
referenced by each node's `attribute_url`; `attribute_files` records their
checksums. Validation reassembles attributes and rejects stale or orphan shards.
Keeping long purpose/use/retention fields outside the index avoids downloading
all of that detail before a visitor selects a record.

The index is downloaded once and indexed in memory. Only bounded neighbourhoods
are rendered. Future scaling can partition the index while retaining IDs and
the evidence model. This release does not publish RDF/JSON-LD.

Generation is deterministic and offline. Validation reassembles provenance,
checks hashes/counts/endpoints and compares against a fresh canonical build.
It fails on stale graph assets or changed PIA Markdown checksums. The existing
Pages workflow rebuilds and validates the graph. A separate PR workflow checks
the graph and browser interactions without deployment.

## Tests

```sh
python -m unittest tests.test_build_graph tests.test_build_pia_site
node --test tests/graph.test.mjs tests/privacy_assessments.test.mjs
python -m http.server 8766 --directory site
# Another terminal, with Playwright/Chromium installed:
node tests/graph.browser.cjs
node tests/graph-tour.browser.cjs
```

The browser test defaults to `http://127.0.0.1:8766/`; override `GRAPH_TEST_BASE`,
`BROWSER_EXECUTABLE` and `GRAPH_TEST_OUTPUT` if needed. It covers real records,
lazy provenance, bilingual aliases, view URLs/history, expansion, filters,
mobile overflow, unknown records, missing data and diagram failure. It also
checks native/fallback fullscreen and exit, focus containment/restoration,
fixed-map pagination, previous/next record navigation, shared node/card colours,
type-summary shortcuts, hub sorting and portrait fullscreen layout.
Screenshots default to `work/`.
