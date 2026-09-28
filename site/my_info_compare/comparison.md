# My Info — V1 and V2 comparison

Both versions are preserved on feature branches. `main` and the live GitHub Pages survey remain at the baseline while this design is reviewed.

- V1: `codex/my-info-v1-review` — existing survey plus a generated, printable logic document.
- V2: `codex/my-info-v2` — additive prototype at `site/my_info_v2/`; the V1 application, classifier, data and MCP endpoint are unchanged.

## Open and review

From a checkout of the V2 branch, run `python3 -m http.server 8766 --directory site`, then open `http://localhost:8766/my_info_compare/`.

The comparison page links to both runnable versions and their printable review documents. For spreadsheet review, use `docs/my_info_v1/pib_mapping.csv`, `docs/my_info_v2/routing_ledger.csv`, and `docs/my_info_v2/coverage.csv`.

V1's document is generated from its actual 22 gates, 76 options, source selectors, timing and department rules. V2's document states the proposed flow, exact selectors, source population/purpose excerpts, retention rules, edge cases and remaining work.

## What changed and why

| Decision | V1 | V2 |
|---|---|---|
| Entry | Up to 22 broad yes/no gates and child questions | Recognizable activities in eight expandable groups, with program search |
| Known department | Sometimes asks people to distinguish delivery or archive institutions | Infers the institution from the program; explains custody separately |
| Record selection | Broad keyword classifier plus bank-number selectors | Exact institution-scoped selectors, supported by purpose and population |
| Less-common programs | Only classifier-reachable PIBs appear | Full source directory; explicit population review required to add a record |
| Dates | Asked for each selected activity even if unusable | Results first; optional dates only for a reviewed event-based rule |
| Common four | Skips full tax/travel/civic gates | Resolves only selected activities and leaves all others available |
| Uncertainty | Often absent from normal results | Separate unsure, source-gap and unresolved-program guidance |
| Standard PIB | Generic government-wide description | Tied to the organization the person identifies, or explicitly unknown |

## Source findings that changed the design

The Info Source introductions distinguish organizational responsibilities and service delivery; the PIB population and purpose establish personal applicability. For example IRCC's introduction names Service Canada passport delivery, DND describes CAF administration, Health Canada describes the transfer of First Nations service responsibilities to ISC, and VAC's program section distinguishes its benefits.

- Voting was labelled a gap even though ELECTIONS PPU 037 is already collected. V2 uses its registration/identification description.
- Generic veteran routes included VAC PPU 200, the narrowly historical Agent Orange payment. V2 requires that named activity.
- CAF applicant and Regular Force personnel files describe different populations. V2 distinguishes the roles and does not ask the person to choose an archive.
- General border crossing did not establish commercial passenger, duties-payment or regional immigration-interview records. V2 has distinct activities.
- CPP/OAS routing omitted the actual OAS bank, ESDC PPU 116. V2 selects CPP 146 and OAS 116 separately.
- Bank keys are repeated across institutional publishers. V2 uses the full publisher-and-bank record ID.
- V1's derived retention start is unspecified for 630 records. V2 cannot borrow an activity date for an unspecified start. CSA020 starts at launch; DND818 starts at release and transfers to LAC.

## Measured interaction paths

These are executable scenario replays, not usability timing measurements. V2's one activity-selection submission still involves reading/selecting activities. The table must not be read as proof that a large checklist takes one decision. Optional program search and directory review add effort, and optional timing is shown separately.

| Scenario | V1 mandatory screens | V1 department prompts | V1 date prompts | V2 selection + required prompts | V2 optional date prompts |
|---|---:|---:|---:|---:|---:|
| No reported activity | 22 | 0 | 0 | 1 | 0 |
| Veterans education benefit | 25 | 1 | 1 | 1 | 0 |
| Regular Force service | 25 | 1 | 1 | 1 | 1 |
| NEXUS application | 24 | 0 | 1 | 1 | 0 |
| Federal voting | 24 | 0 | 1 | 1 | 0 |
| Space launch attendance | 24 | 0 | 1 | 1 | 1 |
| CBSA service complaint | 25 | 1 | 1 | 1 | 1 |
| Common four plus NEXUS | 20 | 0 | 0 | 1 | 1 |

V1 dates are answered 'unknown' to expose its mandatory path. V2 dates are deferred. Record-bank outputs for every replay are in `docs/my_info_v2/comparison.json`; more records is not automatically a better result.

## Coverage, quality and release boundary

V2 currently has 56 reviewed activity statements reaching 53/1040 inventory rows (5.1%). All 1040 records can be discovered through the directory, with 987 requiring that additional program/population review. V1's 597 direct-labelled rows are a broader theoretical ceiling; these two measures use different evidentiary thresholds.

Institutional context is available from local captures for 67 English and 64 French institutions. There are 33 flagged titles, 7 missing populations and 13 missing purposes in the source inventory. These are exposed, not silently repaired.

Only 6 unambiguous rules are executable in V2. Other schedules remain available to read. Expand that ledger and the guided catalogue with source review before claiming production-level coverage.

This branch is a reviewable design prototype. Public release still needs broader program curation, more retention review, fluent French review, accessibility/user testing, and tests with realistic stories including indirect records. The structured V2 engine supports the same next-step/evaluation contract a future voice adapter can use; the existing public MCP service has not been replaced.

## Rebuild and verify

```bash
python3 scripts/build_my_info_v2.py
node --test tests/my_info_v2.test.mjs
node scripts/compare_my_info_surveys.mjs
```
