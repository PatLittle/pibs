# Targeted Info Source refresh — 2026-11-11, round 3

The owner requested six institutions and the same collect, update, push-to-main and live-site verification workflow used for the preceding two rounds. Stop searching when an institution's official report returns HTTP 404.

| Institution | Outcome | PIBs EN / FR / merged | Classes EN / FR / merged |
| --- | --- | --- | --- |
| Office of the Commissioner of Lobbying | Live collection blocked by HTTP 403 security checks | Not collected | Not collected |
| Office of the Commissioner of Official Languages | Official English and French links return HTTP 404; no replacement search | Not collected | Not collected |
| Office of the Director of Public Prosecutions / PPSC | Collected separate bilingual holdings appendices | 6 / 6 / 6 | 13 / 13 / 13 |
| Office of the Intelligence Commissioner | Collected the official bilingual 2025 PDFs | 0 / 0 / 0 | 1 / 1 / 1 |
| National Security and Intelligence Review Agency Secretariat / NSIRA | Collected the full bilingual report linked from the overview | 2 / 1 / 2 | 2 / 2 / 2 |
| Secretariat of the National Security and Intelligence Committee of Parliamentarians / NSICOP | Collected the official bilingual 2025 report | 0 / 0 / 0 | 1 / 1 / 1 |

## Availability findings

- Lobbying: `https://lobbycanada.gc.ca/en/info-source/` and `https://lobbycanada.gc.ca/fr/info-source/` return HTTP 403 security-check pages. A normal headless browser also received HTTP 403 on the English URL. The web search tool can show indexed report text, but no current report was captured from that cached text. The institution's existing zero extraction is not a finding that it has no banks or classes.
- Official Languages: `https://www.clo-ocol.gc.ca/en/publications/other/2021/info-source-2021` returned HTTP 404. The French URL redirected to `https://www.clo-ocol.gc.ca/fr/publications/etudes-autres-rapports/2021/info-source-2021-sources-renseignements-du-gouvernement`, also HTTP 404. The local TLS certificate chain could not be verified; a single public-page request with certificate verification disabled established each 404. No replacement search was performed after those failures. The certificate limitation and outcomes are recorded in the availability audit.

The machine-readable initial checks and bounded follow-ups are in `data/audits/infosource_source_availability_2026-11-11_round3.json`. Registry validation metadata records the observed 403 and 404 outcomes. Earlier failed-capture manifests remain preserved.

## Captured publications and URL overrides

- PPSC overview: [English](https://www.ppsc-sppc.gc.ca/eng/tra/is/index.html), [French](https://www.ppsc-sppc.gc.ca/fra/tra/is/index.html). Personal information banks: [English](https://www.ppsc-sppc.gc.ca/eng/tra/is/pib-frp.html), [French](https://www.ppsc-sppc.gc.ca/fra/tra/is/frp-pib.html). Classes: [English](https://www.ppsc-sppc.gc.ca/eng/tra/is/cor-cds.html), [French](https://www.ppsc-sppc.gc.ca/fra/tra/is/cds-cor.html). Updated URL overrides for canonical HTTPS and these role-specific appendices.
- NSIRA full report: [English](https://nsira-ossnr.gc.ca/en/secretariat/access-to-information-and-privacy/info-source/sources-of-federal-government-and-employee-information/), [French](https://nsira-ossnr.gc.ca/fr/secretariat/acces-a-l-information-et-a-la-protection-des-renseignements-personnels/info-source/sources-de-renseignements-du-gouvernement-federal-et-sur-les-fonctionnaires-federaux/). Updated overrides from the overview to these directly linked full reports.
- Intelligence Commissioner: the existing overrides already identify the official English and French 2025 PDFs under `https://www.canada.ca/content/dam/oic-bcr/info-source/`; those URLs remain effective.
- NSICOP: the existing overrides already identify the official English and French `info-source/2025.html` publications; those URLs remain effective.

Preserved ten raw HTML/PDF responses, converted Markdown, checksums, roles and provenance in dated supplemental captures under the four institutions' `snapshots/2026-11-11/supplemental/` directories. Each selected role replaces the older publication for extraction while retaining its original capture. The successful-publication URL audit is `data/audits/institution_registry_url_audit_2026-11-11-round3.json`.

## Source limitations and integration

NSIRA's French investigations bank is printed as `SSNR PPU 5`, while the English bank is `NSIR PPU 005`. The malformed single-digit French bank number is preserved in the source; no corrected identifier is invented. The report uses generic bank/class headings, which are retained as published. English/French prefix differences are normalized only by the existing institution-specific merge rules.

The two 2025 publications describe internal services through references to standard Treasury Board holdings. Those references do not create additional institution-specific banks in the compiled tables.

NSICOP's English publication formats its class identifier as `**Record Number: SNSICOP** 001`. The class extractor now recognizes a number whose prefix ends inside the bold label and whose digits follow it. A focused regression test covers the published format; the class is now present in both languages. The raw publication remains intact.

PPSC previously had two French-only banks and 13 French classes. Its six bilingual banks and 13 bilingual classes improve coverage and replace French-only canonical prefixes with the available English prefixes. NSIRA previously had no extracted holdings. This round therefore adds a net **6 PIBs and 2 classes**, producing **1,102 institutional PIBs and 2,542 classes**. Including the 49 standard banks, the refreshed survey inventory has **1,151 records**.

The collection tracker, registry CSV/Excel, comprehensive tables, explorer assets, derived My Info features and generated survey/review outputs are refreshed together. Publication results and live checks are reported after deployment.

## Validation before publication

- All 119 Python tests passed, including the new class-label formatting regression.
- All 14 V2 survey-routing tests passed.
- Collection validation passed for 131 institutions and 558 preserved raw files with no checksum errors.
- Data-model, My Info feature, browser-survey, deployment-boundary and static-site validators passed.
- Inventory snapshot assertions now expect 1,151 total / 1,102 institutional banks.
- The working tree passed the whitespace/diff check before commit.
