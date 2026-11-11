# Targeted Info Source refresh — 2026-11-11

Checked the four institutions requested by the owner. Added bilingual URL overrides for Natural Resources Canada, Statistics Canada and FINTRAC. Preserved their full official publications as dated supplemental captures, replacing the older sources for extraction while retaining the original captures and collection-job identity.

| Institution | English report | French report | Result |
| --- | --- | --- | --- |
| Department of Natural Resources | https://natural-resources.canada.ca/corporate/transparency/info-source-sources-federal-government-employee-information | https://ressources-naturelles.canada.ca/organisation/transparence/info-source-sources-renseignements-gouvernement-federal-fonctionnaires-federaux | Both HTTP 200. Replaces legacy numeric routes and access-request landing pages. |
| Statistics Canada | https://www.statcan.gc.ca/en/about/transparency/publications-information-holdings/info-source/2025 | https://www.statcan.gc.ca/fr/a-propos/transparence/publications-fonds-renseigments/info-source/2025 | Both HTTP 200. The current Info Source index links to the 2025 full chapters. |
| Financial Transactions and Reports Analysis Centre of Canada | https://fintrac-canafe.canada.ca/atip-aiprp/infosource-eng.php | https://fintrac-canafe.canada.ca/atip-aiprp/infosource-fra.php | Both HTTP 200. Replaces obsolete HTTP `.gc.ca` / `.asp` routes. |
| Financial Consumer Agency of Canada | https://www.canada.ca/en/financial-consumer-agency/corporate/transparency/infosource.html | https://www.canada.ca/fr/agence-consommation-matiere-financiere/organisation/transparence/infosource.html | Both HTTP 404. No verified current replacement found; no URL override added. |

## FCAC evidence

The [agency's transparency page](https://www.canada.ca/en/financial-consumer-agency/corporate/transparency.html) and the [Treasury Board Info Source directory](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/list-institutions.html) still link to the unavailable FCAC report. The French transparency page also links to its unavailable French report. An alternative `info-source.html` spelling also returned 404. Searches did not establish a current alternative. This remains a source-availability failure, rather than evidence that FCAC has no personal information banks.

## Extraction checks

| Institution | PIBs EN | PIBs FR | Merged PIBs | Classes EN | Classes FR | Merged classes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Natural Resources Canada | 19 | 19 | 19 | 23 | 24 | 24 |
| Statistics Canada | 61 | 60 | 61 | 55 | 55 | 56 |
| FINTRAC | 3 | 3 | 3 | 4 | 4 | 4 |

Natural Resources uses numbered bold titles (`PIB PPU ...`, `FRP PPU ...`, and one `RFP` spelling), several French bank-label variants, and abbreviated `PPU 142` and `PPU 145` bank numbers. The extractor now recognizes those titles and labels. It inherits an agency prefix for an abbreviated labelled number only when all fully qualified bank labels in that document identify the same agency; references to other agencies in prose do not supply ownership. These additional label variants and abbreviated-number rules apply only to documents with numbered PIB/FRP titles, preserving the existing parser contract for other layouts. Only the three requested institutions' extractions are included in this refresh.

Source discrepancies remain explicit: Statistics Canada's French child-welfare bank ends with `Numéro de fichier : StatCan SSD 813`, whereas the English bank uses `StatCan PPU 813`. The parser preserves the published identifier rather than inventing a French PPU correction; the French SSD entry appears among classes. Natural Resources' French report also has a class without a matching extracted English entry. Counts describe extraction from the publications and do not assert perfect bilingual equivalence.

Raw HTML, Markdown, checksums, fetch status and provenance are under each institution's `snapshots/2026-11-11/supplemental/` directory and `source_manifest.json`. The machine-readable URL check is `data/audits/institution_registry_url_audit_2026-11-11.json`.

## Validation and delivery scope

The registry CSV/Excel, collection status, comprehensive holdings tables, and explorer data were refreshed locally. My Info survey generation and publication are separate downstream steps.

- 37 registry/extractor tests passed, including numbered titles, French label variants, abbreviated numbers and ambiguous-agency handling.
- Collection validation passed for 131 institutions and 540 raw source files, with no checksum errors.
- The compiled tables contain 1,074 PIBs and 2,455 classes from 130 institutions (the compiler consolidates Canadian Forces under National Defence).
- Data-model and static-site validation passed; no broken local site links were found.
- The three new report pairs add 83 PIB rows and 84 class rows to the compiled data.
