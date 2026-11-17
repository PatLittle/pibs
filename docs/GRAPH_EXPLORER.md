# PI Network Explorer

The explorer has one task: follow documented connections between records.
`site/graph.html` uses native HTML and SVG, with one search and one selected record.
There are no independent browse modes, relationship filters, layout controls,
fullscreen modes, or tour controls competing with that task.

## Model first

The [complete model diagram](../site/data-model.html) contains every table and
field in the network's owning sources and runtime projection. It provides a
searchable field catalogue, zoom/pan, keyboard navigation, a standalone
[SVG](../site/data/network-schema.svg), and machine-readable
[schema](../site/data/network-schema.json). `data_model.json` declares canonical
CSV keys and foreign keys; the inventory also inspects nested PIA documents,
external AIA field shapes, lazy attributes and evidence shards.

The full schema distinguishes:

- source records: institutions, institutional/standard PIBs and classes;
- Service Inventory services, programs, standards and annual join observations;
- assessments: organization inventories, PIAs, language sources and citations;
- external AIA metadata, survey answers, translations and calculated results;
- controlled vocabularies and supporting derived My Info tables;
- the browser's typed node, edge, evidence and manifest projections.

The PIA collection manifest's organization map is represented as
`organizations.{institution_id}`. Distinct map keys are data, not different fields.
Array contents use `[]` field paths. Parent institution/package IDs on normalized
nested records are explicitly identified as inherited keys. Polymorphic graph
endpoints point to one node type at a time, not all types simultaneously.

PIB type and personal-information category remain bank attributes. Their
supporting tables belong in a schema diagram but are not extra network entities.
AIA senior officials are organization-scoped name observations, not verified
current officeholders or automatically merged people from other collections.

## What changed in the interaction

The previous design exposed traversal implementation choices to visitors. Its
map, record browser, relationship filters, pagination, expansion, layout and tour
were separate navigation systems. The new design follows the data's actual shape:

1. **Find one record.** Search bilingual names, identifiers and recorded aliases.
   PIA/EFVP, PIB/FRP and AIA/EIA also narrow by familiar record type. Three curated
   starting stories provide examples. The landing landscape describes the connected
   real record types; its type-level arrangement is a model illustration, not a
   claim of a direct edge between every pair of records.
2. **Read its connections.** Keep the selected record at the top. Group all its
   neighbours by type, relationship and direction: assessments citing a bank,
   classes a bank references, the owning institution, or officials named in an
   AIA. Each group shows its complete count. The first three records are visible;
   Show more reveals another twelve within that group. No category is omitted
   and records are sorted by localized label, not hash or an opaque score.
3. **Follow the next record.** Clicking a record replaces the focus while adding
   a breadcrumb to the documented path. Previous record or a breadcrumb retraces
   that path. There is no ever-expanding graph to manage. Search starts a new path.
4. **Discover a real bridge.** “Where this record can lead” offers up to four
   two-step paths across citations, related classes and named-official links.
   Each path names the intermediate record and offers both source links. Generic
   shared-institution attribution is excluded from these suggestions. An indirect
   path never becomes an asserted direct edge. Candidates are selected
   deterministically, preferring citation paths, cross-institution records and
   distinct target types; this is navigation ordering, not a confidence score.
5. **Inspect why.** A small, labelled evidence button opens the exact edge in the
   information panel. Evidence starts collapsed and loads when opened. Both
   original sources and repository line evidence remain available. Every node's
   available fields start collapsed; bilingual values and nested evidence are
   retained. Long attributes load from their owning shard when selected.

The branches in the display connect the focus to groups of its actual neighbours;
they do not add relationships between unrelated records. The evidence button on
each record identifies the exact underlying edge. When a neighbour is also
connected to the preceding breadcrumb record, that additional observed connection
is labelled in context.

The information panel has an accessible sidebar icon and a close button. Hiding
it only changes the display. On mobile it becomes a drawer; closing it reveals
the connection map. The selected record, path and source references remain intact.

## Identity and meaning

Canonical source-scoped identities remain unchanged:

- `institution:{institution_id}`
- `pib:{institution_id}:{bank_number_key}` / `pib:standard:{bank_number_key}`
- `class:{institution_id}:{record_number}` / `class:standard:{record_number}`
- `pia:{institution_id}/{pia_id}`
- runtime `aia:{package_id}` and `official:{u_id}`
- unresolved reference and edge IDs derived from their source identity.

| Predicate | Meaning |
| --- | --- |
| `listed_by` | Inventory attribution to an institution |
| `references` | Explicit source citation; it does not establish full assessment coverage |
| `related_class` | Literal PIB-to-class reference, retaining scope and resolution |
| `responsible_official` | AIA explicitly names a responsible senior official |

Unknown or multiple targets remain unresolved/ambiguous reference nodes. They
are not promoted into real holdings or used as intermediates in recommended
paths. Missing links do not establish that an assessment or relationship is absent.
PIB categories preserve derived basis, source-field excerpts, rule and confidence
inside attributes. Risk level and survey version belong to the AIA alone.

“Copy path link” retains selected record, evidence edge, language and breadcrumb
path. Browser Back/Forward and the header language link preserve that context.
Breadcrumbs from URLs are validated against actual adjacency. Older `node`/`root`
links from tables and assessment readers continue to work. Old expansion/filter
parameters are not controls in the new interface. Group reveal counts and panel
visibility are transient.

## Source and schema builds

The graph remains schema version 3, with source hashes, lazy attribute/evidence
shards and deterministic source-evidenced edges. Its canonical inputs are the
institution registry, PIB/class tables and linkage table, standard bank/class
references, category/type vocabularies, classifier, PIA inventories and PIA
collection manifest. The collected graph is generated offline.

The external AIA URL is configured in `site/aia-source.json`. Both the AIA page
and explorer load it in browser memory. No AIA payload, normalized AIA catalogue,
official-name row or runtime AIA graph is stored in this repository. Its schema
inventory stores only field names, types, aggregate counts and source checksum.
An offline schema rebuild retains that last explicitly inspected external shape.
To inspect a changed source, fetch it outside the checkout and supply its path:

```sh
python scripts/build_network_schema.py --aia-file /path/outside/repo/aia-results.jsonl
```

Without that option, no network request or external data copy is made. Schema
artifacts are rebuilt with the regular site build after the graph. Refreshing
external field names does not silently promote new survey codes into interpreted
answers. See [AIA matching methodology](AIA_INTEGRATION.md).

An unavailable AIA feed is labelled and the collected graph remains usable.
An unknown deep link opens the starting stories with an explanation. Failed
attribute/evidence requests can be retried.

## Targeted contrast adjustment

Only two shared tokens in `site/styles.css` changed for this request:

| Target | Before | After | Contrast against white |
| --- | --- | --- | --- |
| Muted text | `#53657a` | `#475668` | 5.98 → 7.50 (about +25%) |
| Light-grey outlines | `#d7dee5` | `#c1c8ce` | 1.36 → 1.69 (about +25%) |

Other global colours, typography, fills, borders' widths and spacing are untouched
by the contrast adjustment. The explorer's structural redesign is a separate change.

## Checks

```sh
python validate_site.py
python validate_data_model.py
python -m unittest tests.test_network_schema tests.test_build_graph tests.test_build_pia_site
node --test tests/graph-focus.test.mjs tests/graph.test.mjs tests/aia.test.mjs tests/privacy_assessments.test.mjs
node tests/graph.browser.cjs
node tests/network-schema.browser.cjs
```

The browser checks use Playwright/Chromium and a synthetic AIA fixture rather
than copying source rows into tests. They cover evidence, traversal, two-step
paths, URL/language restoration, collapsed attributes, display toggling, mobile
width, unavailable sources and the complete searchable model diagram.

## Service Inventory extension

Service, program and service-standard nodes use the same focused navigation,
bilingual search, source evidence and collapsed information panel. The Study
Permit starting story connects an AIA’s literal service ID to its reported program
and standards. Annual fields remain nested observations and every program/standard
edge retains its reporting year. No assessment risk level is propagated to services.

The [Service Inventory field inventory and join ledger](SERVICE_INVENTORY_JOINS.md)
documents all 70 fields, scoped identities, exact institution matching, invalid
program references, code-list discrepancies and the next joinable datasets.
