# Targeted Info Source refresh — 2026-11-11, round 2

The owner requested Copyright Board, Canadian Nuclear Safety Commission (CNSC), Canadian Institutes of Health Research (CIHR), and Social Sciences and Humanities Research Council (SSHRC). Follow official navigation and redirects; if an official report returns HTTP 404, record the failure and stop searching for that report. No report in this round returned 404. All eight final English/French report URLs returned HTTP 200 and substantive Info Source content.

| Institution | English report | French report | PIBs EN / FR / merged | Classes EN / FR / merged |
| --- | --- | --- | --- | --- |
| Copyright Board | https://cb-cda.gc.ca/en/transparency/info-source-copyright-board-of-canada | https://cb-cda.gc.ca/fr/transparence/info-source-commission-du-droit-dauteur-du-canada | 0 / 0 / 0 | 0 / 0 / 0 |
| Canadian Nuclear Safety Commission | https://www.cnsc-ccsn.gc.ca/eng/corporate/transparency/access-to-information-and-privacy/info-source/ | https://www.cnsc-ccsn.gc.ca/fra/corporate/transparency/access-to-information-and-privacy/info-source/ | 11 / 10 / 11 | 18 / 18 / 18 |
| Canadian Institutes of Health Research | https://cihr-irsc.gc.ca/e/47695.html | https://cihr-irsc.gc.ca/f/47695.html | 8 / 8 / 8 | 38 / 38 / 38 |
| Social Sciences and Humanities Research Council | https://sshrc-crsh.canada.ca/en/about-sshrc/transparency/info-source.aspx | https://sshrc-crsh.canada.ca/fr/sujet-crsh/transparence/info-source.aspx | 3 / 3 / 3 | 19 / 23 / 29 |

## Discovery and source limitations

- Copyright Board's official access-request page links directly to the full report. The report describes four institutional functions/programs and links to Treasury Board standard classes and banks, but contains no numbered institution-specific records suitable for the institution tables. Zero extraction is not an assertion that the Board holds no personal information.
- The official directory's CNSC address redirects to the current `cnsc-ccsn.gc.ca` domain. The French report prints `CCSN PPU 05` for participation in Commission proceedings; the English report uses `CNSC PPU 005`. The malformed two-digit French number remains in the preserved source, without inventing a corrected bank identifier.
- The official directory's CIHR link reaches the full publication via canonical HTTPS without `www`. Both reports are titled **Info Source 2020**; the collection date does not imply that CIHR revised the publication in 2026.
- SSHRC's legacy directory addresses reset the connection; they did not return 404. One targeted search identified the current official-domain report, whose language switch links to the French report. Repeated references to the same bank are deduplicated by bank identifier. One French occurrence of `CRSH PPU 055` uses a compliance-bank title with grants-and-awards content; the source inconsistency is preserved. English and French classes have differing identifiers/coverage, so the merged count is a union rather than an assertion of one-to-one translation.

## Integration

Updated the four rows in `data/institution_registry_overrides.csv`, registry CSV/Excel and site copy. Preserved each report's raw HTML, Markdown, URL, HTTP result, SHA-256 and provenance under the institution's `snapshots/2026-11-11/supplemental/` directory. Rebuilt only these four institutions' extraction outputs, compiled comprehensive tables, and refreshed collection status and explorer assets.

Round 2 adds **22 PIBs and 85 classes**. Both rounds together add **105 PIBs and 169 classes**, producing **1,096 PIBs and 2,540 classes** in the compiled institutional tables. The first-round FCAC failure remains recorded separately. My Info derived data and generated survey/review outputs are refreshed for the new source rows so the triggered site workflows can build consistently.

The machine-readable URL audit is `data/audits/institution_registry_url_audit_2026-11-11-round2.json`. Publication/build results and live-page checks are recorded in the delivery conversation after deployment.

## Validation before publication

- Collection validation: 131 institutions, 548 preserved raw files, no checksum errors.
- Data-model, My Info feature, browser-survey, deployment-boundary and static-site validators passed.
- All 14 V2 routing tests passed with the new inventory totals.
- The 118-test Python run found two fixed inventory-count expectations for the earlier 1,040-row snapshot. Those expectations were updated to 1,145 total / 1,096 institutional banks; all 26 model, agent-tool and persona tests passed when rerun. The other tests passed in the full run.
- Updated the persona fixture's snapshot version to match the refreshed questionnaire. No fixture answers were changed.
- Verified all 105 newly collected bank records from both rounds appear in the generated V2 directory.
