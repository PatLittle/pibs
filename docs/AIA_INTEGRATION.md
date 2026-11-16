# AIA inventory and integration

## Source and storage

Current external source:
<https://patlittle.github.io/aia-eia-js/aia-analysis-data/aia-results.jsonl>.
The location is temporary (expected to move in roughly 6–8 months). It is
configured once in `site/aia-source.json`; review the location after 2027-05-16.
Change `url` there when the publisher moves it, and test both consumers.

The browser fetches JSONL directly over HTTPS. The source currently permits
cross-origin requests (`Access-Control-Allow-Origin: *`). A future location must
also permit browser access. `site/link-aia.html` and `site/graph.html` share
`site/aia-data.mjs`; they normalize and link records in memory. No AIA JSONL,
normalized AIA catalogue, official-name rows, or AIA graph nodes/edges are copied
into this repository or its build outputs. The tracked graph only gains existing
registry aliases, which enable organization matching. The existing graph JSON
download is the **base collected graph**, excluding runtime AIA additions.

A failed, empty, malformed, duplicate-ID or unreachable feed is reported. The
AIA page offers Retry; the network retains the base graph and reports the
unavailable overlay. Requests time out after 15 seconds. No stale local AIA copy
is silently substituted. Counts are recalculated on each successful load.

## Inventory, inspected 2026-11-16

The supplied local file and fetched URL had the same SHA-256:
`bf7040fd7f803d3eb39eee7f0ff282a93d28322ca4022d5aeacb833c9bc9ada7`.
These are aggregate observations, not a committed source snapshot or claims
about every federal AI system. The file's answer text is data, not instructions.

| Measure | Observed |
| --- | ---: |
| Source records / distinct `package_id` UUIDs | 39 / 39 |
| Organizations / unique registry matches | 11 / all 39 records |
| Top-level fields | 18 |
| Distinct fields inside `data` | 250 |
| Distinct fields inside `translationsOnResult` | 89 |
| Named responsible senior officials (`data.ADMresponsible`) | 4 records / 4 organization-scoped names |
| Records without that field populated | 35 |
| Respondent field populated (`projectDetailsRespondent`) | 38 |
| Feed-derived impact levels 1 / 2 / 3 / 4 / missing | 16 / 21 / 1 / 0 / 1 |
| Versions v0.9 / v0.9.1 / v0.10.0 / v1.0.1 | 1 / 9 / 25 / 4 |
| Provenance `published` / `recovered` | 32 / 7 |
| Records with detected explicit references | 19 |
| Unique matched / ambiguous / unresolved reference groups | 27 / 6 / 8 |

All four named senior officials occur in v1.0.1 records. A missing name in an
older survey is not evidence of missing institutional accountability. Respondents
and job titles must not be promoted to senior-official names. The 27 resolved
groups are explicit PIB references in this inspected feed; no explicit PIA URL
or standard-class citation resolved in this feed. More classes are reachable
indirectly through the existing PIB-to-class links, without asserting a direct
AIA-to-class citation. Ambiguity includes the same ESDC identifier appearing in
distinct institution inventories; those legal owners remain separate.

The live page inventories every non-empty leaf field, including its value types
and numerator/denominator, without needing a repository copy of the source.
The charts show the entire feed, while catalogue filters affect only the table.

## Recommended field mappings and implemented links

| AIA field(s) | Target / treatment | Rule and status |
| --- | --- | --- |
| `package_id` | AIA primary key; graph `aia:{UUID}` | Implemented. Require a valid unique UUID; reject duplicates. Stable across changes to title, scores and resource URL. |
| `title_en`, `title_fr` | Bilingual AIA titles | Implemented. Preserve source titles and fall back to available language. |
| `organization_en`, `organization_fr` | Registry `institution_id` | Implemented. Split bilingual pipe-delimited labels and require one exact normalized registry name/alias match. No fuzzy factual links. |
| `data.projectDetailsDepartment-NS` | Department-number crosswalk candidate | Retained in inventory. Do not equate it to `gc_orgID`, Open Canada org UUID, or legal institution ID without a verified crosswalk. |
| `data.ADMresponsible`, `translationsOnResult.ADMresponsible` | Official `name_en`, `name_fr`, `u_id`; graph `official:{u_id}` | Implemented. Preserve full names; do not guess given/family-name boundaries or translate personal names. Only this explicit role creates `responsible_official` edges. |
| `data.projectDetailsRespondent`, `projectDetailsJob` | Respondent / role context | Kept separate from responsible officials; respondent visible in AIA details. |
| `derived.impact_level`, `impact_level_label` | Risk/impact level | Display the supplied numerical level (1–4), with missing shown separately. Scores are feed-derived, not a new PIBS risk calculation or independent validation. |
| `version` | Survey version | Implemented as a filter, distribution, detail and graph attribute. It is not `projectAIAnumber`. |
| `derived.raw_risk_score`, `mitigation_score`, `final_score`, `project_phase`, `completeness_pct` | Source-derived context | Display in details; do not compare raw survey answer codes or recalculate across versions without their definitions. |
| `data.aboutDataSource12` and other explicit text references in `data` / translations | PIB identifiers → source-scoped PIBs | Implemented. Match literal identifier aliases; owner-scope bare institutional numbers; preserve full prefixes for cross-institution references. Standard PSE/PSU targets stay separate. |
| Literal `PRN` / `NDP` IDs in answer text | Standard Class of Records | Implemented unique exact lookup. General institution-specific class-reference extraction is a future extension; existing PIB → class paths already work. |
| Explicit URLs in answer text matching a collected PIA's `sources` | PIA → AIA cross-navigation in the undirected explorer | Implemented as directed AIA `references` PIA edges; source URL must match. Query/fragment/trailing slash do not change page identity. |
| `privacyImplementation5/6`, corresponding `privacyDesign*` narratives, project/program titles | PIA review leads | Display privacy narratives and provide a PIA search link. Similar titles, mentions of a completed PIA, shared programs or generic privacy answers do not create factual edges. |
| `data.projectDetailsProgram`, `projectDetailsTitle`, `projectDetailsBranch`, project description | Program/activity and holdings candidates | Search/review context. Future review queue can combine institution + exact project/program names, then verify original evidence. No current title-similarity graph edges. |
| `data.projectDetailsID` (28 populated), `projectAIAnumber` (2), `ServiceID` (3) | Project/service crosswalk candidates | Retained, with project/service IDs visible in detail. Not global AIA keys; missing and placeholder values are not minted into source identifiers. Service inventory linking needs a verified target dataset. |
| `source`, `dataset_url`, `resource_url(s)`, `recovered_path`, metadata timestamps | Provenance | Show published/recovered distinction, original dataset link and modified date. A recovered record is not represented as a currently downloadable published resource. |

Names are preserved as EN/source and FR/translation fields because the feed uses
`data` and `translationsOnResult`; their language is not independently verified
here. Free-text answers can retain their original language. Raw item codes are
not translated or interpreted using the wrong version's questionnaire.

### Official identifiers

`u_id = "aia-official-" + first 24 hex characters of SHA-256(JSON.stringify([
institution_id (or unmatched source organization), normalized source name]))`.
Normalization removes accents, punctuation and case, and collapses whitespace.
This creates a stable **organization-scoped name key**, not a verified global
person identity or current-employment assertion. Missing `ADMresponsible` does
not create a person node. The French form is retained separately. Renamed people
or organization changes may need an explicitly reviewed alias table later.

For the existing `gc_snr_officials` collection, the recommended next match is
normalized full name + canonical organization + temporal evidence. Treat
nickname/position-only similarities as candidates; retain source observations
and never merge people automatically based on a common name. This phase adds
AIA official nodes and their connections without altering that collection.

### Relationship semantics

- `listed_by`: AIA → institution, backed by unique exact name/alias matching.
- `responsible_official`: AIA → named official, backed by `ADMresponsible`.
- `references`: AIA → PIB, standard class or PIA, backed by an explicit code or
  matching source URL. Several language observations with identical candidate
  targets consolidate into one reference group with all evidence retained.
- Unmatched/multiple targets become separate unresolved/ambiguous `reference`
  nodes with dashed edges, rather than invented holdings or asserted links to
  every candidate. Organization non-matches keep candidate IDs in memory.

A citation does not assert assessment coverage, data sharing, adoption of a
standard bank or an institution's overall risk. Risk and survey version are
attributes of the AIA, never inherited by its bank, institution, class or person.
Both directions can be traversed in the network. Existing table dialogs and PIA
readers already enter that network, so AIA connections are discoverable there.

## Checks

Use Node 20.19+ or the workflow's Node 22 (older Node 18 cannot import the existing
privacy-assessment `.js` modules using syntax detection):

```sh
python scripts/build_graph.py
python validate_site.py
python -m unittest tests.test_build_graph tests.test_build_pia_site
node --test tests/aia.test.mjs tests/graph.test.mjs tests/privacy_assessments.test.mjs
node --check site/aia-data.mjs
node --check site/link-aia.mjs
node --check site/graph.mjs
```

The new matching tests use synthetic records rather than copying AIA source rows
into the repository. Browser smoke testing on 2026-11-16 used the real external
feed and checked 39 catalogue rows, four officials, composed filters, details,
French, mobile width, AIA graph deep links, official-only relationship filtering,
inline evidence and failure recovery without a stored AIA fallback.
