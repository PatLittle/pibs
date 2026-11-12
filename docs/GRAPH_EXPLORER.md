# PIB / PIA network explorer

`site/graph.html` is a buildless Cytoscape.js page in the existing GitHub Pages
site. It uses native JavaScript and generated static data, with no database or
backend. Cytoscape.js 3.33.1 is vendored with its MIT licence in `site/vendor/`.
The existing GCDS header, prototype label, colours and navigation are retained.

## Explore

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

Example using an actual assessment:

`graph.html?node=pia%3Aati-schedule-i-administrative-tribunals-support-service-of-canada%2Fpia-95a42118fc3d&lang=fr`

## Inputs and relationship meaning

| Canonical input | Use |
| --- | --- |
| `institution_registry.csv` | Institution identity, bilingual legal names and source URLs |
| `institutions_infosource_docs/pib_table_en_fr_all.csv` | Institutional PIBs, identifiers, bilingual titles/descriptions |
| `institutions_infosource_docs/cor_table_en_fr_all.csv` | Institutional Classes of Records |
| `spib_en_fr.csv`, `standard_classes_of_records_en_fr.csv` | Government-wide records, kept separate from institutional records |
| `institutions_infosource_docs/pib_cor_links.csv` | Existing compiled PIB/class references and resolution status |
| `PIAs/*/collection.json` | Assessment identities, availability, existing matches and line evidence |
| Referenced PIA Markdown, `PIAs/collection_manifest.json` | Verified source checksums and collection provenance |

| Predicate | Direction and evidence |
| --- | --- |
| `listed_by` | Record → institution: inventory attribution from the existing CSV/collection model |
| `references` | PIA → PIB/class: explicit reference extracted by `PIAs/reference_extraction.py` |
| `related_class` | PIB → class: compiled related-record reference, retaining literal reference, language, scope and resolution |

A citation does **not** assert that a PIA assesses the entire bank. No edges
are inferred from similar titles, shared institutions, categories, laws or
programs. The graph adds no matching algorithm: a PIA target must resolve to
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

`site/data/graph.json` contains schema version 1, nodes/edges, counts, collection
timestamp and SHA-256 hashes of consumed inputs. Each edge has an
`evidence_count` and `evidence_url` pointing to one of 32 static
`site/data/graph-evidence/*.json` shards. Shards map edge IDs to full evidence
arrays; their checksums appear in `evidence_files`. The browser loads and caches
provenance on edge inspection. Record descriptions are excerpts capped at
1,000 characters; complete content remains in the existing tables/readers.

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
```

The browser test defaults to `http://127.0.0.1:8766/`; override `GRAPH_TEST_BASE`,
`BROWSER_EXECUTABLE` and `GRAPH_TEST_OUTPUT` if needed. It covers real records,
lazy provenance, bilingual aliases, view URLs/history, expansion, filters,
mobile overflow, unknown records, missing data and diagram failure.
Screenshots default to `work/`.
