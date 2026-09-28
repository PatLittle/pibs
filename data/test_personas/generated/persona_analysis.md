# My Info persona evaluation

Canonical Beta contract `2026-09-28.6` was evaluated as of 2026. Possible matches were excluded.

These are candidate PIBs, not confirmation that an institution holds a record.

## Cross-persona summary

| Personas | Results | Unique PIBs | Inventory gaps | Retention unknown | Expectation failures |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 857 | 415 | 6 | 583 | 5 |

## Ranked business-logic findings

### 1. Fallbacks Flatten To Strong (high)

18 fallback selections are associated with 736 fallback-only results, while 857 of 857 results are labelled strong. The engine retains the broad parent yes for fallback routes instead of lowering match confidence.

Recommendation: Add a fallback-derived match band, or carry route coverage into result confidence and reserve strong_match for explicit selectors.

### 2. Candidate Volume (high)

The four personas return 857 results covering 415 unique PIBs (39.9% of the 1040-PIB snapshot).

Recommendation: Prioritize named institution/program routes for the fallback interactions that contribute the largest candidate sets.

### 3. Retention Unknown (high)

Retention is unknown for 583 of 857 results (68.0%).

Recommendation: Capture the actual retention trigger (for example file closure, departure, licence expiry, or last administrative action) only where it can materially change the estimate.

### 4. Uncategorized Results (medium)

123 persona-results have no derived personal-information category.

Recommendation: Review category extraction evidence for these PIB records.

### 5. Known Inventory Gaps (medium)

The fixtures encounter 6 selected interactions explicitly marked as inventory gaps.

Recommendation: Keep these visible as coverage limitations; do not substitute broad unrelated PIBs merely to return a result.

### 6. Genuine Expectation Failures (high)

5 expectation assertions remain after record-ID format mismatches are excluded.

Recommendation: Review these as genuine coverage or fixture assertion failures.

## Persona summaries

| Persona | Results | Strong | Possible/review | Unknown retention | Route coverage |
| --- | ---: | ---: | ---: | ---: | --- |
| Peter Deloitte | 322 | 322 | 0 | 210 | direct: 8, fallback: 5, inventory_gap: 1, partial: 3 |
| Dominic Vale | 278 | 278 | 0 | 197 | direct: 9, fallback: 6, inventory_gap: 2, partial: 1 |
| Aisha Rahman | 149 | 149 | 0 | 91 | direct: 4, fallback: 3, inventory_gap: 1, partial: 3 |
| Sophie Tremblay | 108 | 108 | 0 | 85 | direct: 10, fallback: 4, inventory_gap: 2, partial: 1 |

## Peter Deloitte

The survey produced **322** candidates across **55** institutions. The state is **complete**.

### Result profile

- Match bands: strong_match 322
- Holding status: likely_disposed 30, likely_held 58, may_still_be_held 24, retention_unknown 210
- Scope: institution_specific 316, standard 6
- Top institutions: Canada Employment Insurance Commission (32), Department of Employment and Social Development (32), Correctional Service of Canada (24), Parks Canada Agency (20), Royal Canadian Mounted Police (19)
- Category coverage: 25 of 25 controlled categories; 50 result(s) uncategorized.
- Inventory gaps: federal_tax_return.

### Fixture expectations

Expectation assertions failed: **3**.
- Missing expected record IDs: institution:ati-schedule-i-department-of-citizenship-and-immigration:IRCC PPU 081
- Missing expected bank numbers: IRCC PPU 081, TC PPU 093
- Expected ambiguities:
  - A boating licence may mean a Pleasure Craft Operator Card, a pleasure craft licence, or vessel registration; this fixture assumes the operator card only.
  - A departmental audit committee appointment may have its own institution-specific records that the federal-contract selector does not isolate.
  - A divorce by itself does not establish that a federal institution holds a record; the family-life-event wording may overmatch.
  - Above-top-secret is retained as user-provided biographical wording, but the survey only sends the controlled security-screening route.
  - Consulting inside departments can sound like federal employment, but a contractor should normally route through federal contracting, not employee PIBs.
  - Transport Canada's 1997 safety investigation is not clearly represented by the generic justice fallback.
  - Tri-council grants and Sport Canada athlete support both fall into a broad payment fallback and should be separate named routes.
- Known false-positive risks:
  - government employee records from consultant work
  - unrelated family and vital-event banks
  - unrelated grant and benefit programs from fallback routing
- Known false-negative risks:
  - CRA departmental audit committee appointments
  - FINTRAC working-group and clearance records
  - Sport Canada high-performance athlete support
  - Transport Canada marine-occurrence investigation
  - tri-council grant administration

### Business-logic flags

- `fallback_route_selected`: 5 selected route(s) fall back to broad parent matching.
- `partial_route_selected`: 3 selected route(s) have only partial inventory coverage.
- `inventory_gap`: 1 selected interaction(s) have no defensible direct PIB.
- `retention_unknown_majority`: Retention is unknown for 210 of 322 results.
- `uncategorized_results`: 50 result(s) have no derived personal-information category.
- `expectation_failure`: 3 fixture expectation assertion(s) failed.

## Dominic Vale

The survey produced **278** candidates across **42** institutions. The state is **complete**.

### Result profile

- Match bands: strong_match 278
- Holding status: likely_disposed 28, likely_held 40, may_still_be_held 13, retention_unknown 197
- Scope: institution_specific 270, standard 8
- Top institutions: Department of Health (28), Correctional Service of Canada (23), Department of National Defence (19), Royal Canadian Mounted Police (19), Canada Employment Insurance Commission (17)
- Category coverage: 25 of 25 controlled categories; 48 result(s) uncategorized.
- Inventory gaps: federal_tax_return, federal_election.

### Fixture expectations

Expectation assertions failed: **0**.
- Expected ambiguities:
  - A CMHC-insured mortgage is hidden behind a generic housing fallback.
  - Being investigated does not mean every RCMP investigative PIB applies; the police route intentionally has partial coverage and can overmatch.
  - Correctional health care is a federal health interaction, but the current health fallback does not isolate Correctional Service Canada health records.
  - Old revoked licences and vessel records are useful retention stress tests, but disposition depends on trigger events not captured by the survey.
  - Tax-compliance and criminal-investigation records are not represented by the tax-return inventory-gap route.
  - The engine does not distinguish investigation, charge, conviction, victim, witness or collateral contact roles.
- Known false-positive risks:
  - all Correctional Service Canada offender banks
  - all RCMP investigative banks
  - unrelated health and housing programs from fallback routing
- Known false-negative risks:
  - CMHC mortgage-insurance records
  - CRA criminal-investigation and compliance records
  - Correctional Service Canada health records
  - FINTRAC intelligence records
  - integrated proceeds-of-crime records

### Business-logic flags

- `fallback_route_selected`: 6 selected route(s) fall back to broad parent matching.
- `partial_route_selected`: 1 selected route(s) have only partial inventory coverage.
- `inventory_gap`: 2 selected interaction(s) have no defensible direct PIB.
- `retention_unknown_majority`: Retention is unknown for 197 of 278 results.
- `uncategorized_results`: 48 result(s) have no derived personal-information category.

## Aisha Rahman

The survey produced **149** candidates across **44** institutions. The state is **complete**.

### Result profile

- Match bands: strong_match 149
- Holding status: likely_held 53, may_still_be_held 5, retention_unknown 91
- Scope: institution_specific 143, standard 6
- Top institutions: Canada Employment Insurance Commission (29), Department of Employment and Social Development (29), Government of Canada institutions (6), Office of the Chief Electoral Officer (6), Department of Agriculture and Agri-Food (5)
- Category coverage: 25 of 25 controlled categories; 16 result(s) uncategorized.
- Inventory gaps: federal_tax_return.

### Fixture expectations

Expectation assertions failed: **2**.
- Missing expected record IDs: institution:ati-schedule-i-department-of-citizenship-and-immigration:IRCC PPU 081
- Missing expected bank numbers: IRCC PPU 081
- Expected ambiguities:
  - A federally funded volunteer activity is not necessarily federally run; the current wording can create a false positive.
  - A nonprofit employee administering contribution agreements may not consider herself the recipient of a benefit, grant or payment.
  - Current broad grant fallback cannot distinguish the funding departments or contribution-agreement program records.
  - Emergency assistance requested on behalf of an organization may create organizational rather than personal records.
  - Operating a nonprofit is not the same as owning a business or being a federal supplier, making the business question legitimately uncertain.
  - Program evaluation surveys should route to the funding institution, not only generic Health Canada research PIBs.
- Known false-positive risks:
  - Health Canada research records from a nonprofit program evaluation
  - federal volunteer records where the program is only federally funded
  - personal emergency-service records for an organizational request
- Known false-negative risks:
  - Canadian Heritage community funding
  - Employment and Social Development Canada grant administration
  - IRCC-funded settlement volunteer program records
  - Women and Gender Equality Canada contribution agreements

### Business-logic flags

- `fallback_route_selected`: 3 selected route(s) fall back to broad parent matching.
- `partial_route_selected`: 3 selected route(s) have only partial inventory coverage.
- `inventory_gap`: 1 selected interaction(s) have no defensible direct PIB.
- `retention_unknown_majority`: Retention is unknown for 91 of 149 results.
- `uncategorized_results`: 16 result(s) have no derived personal-information category.
- `expectation_failure`: 2 fixture expectation assertion(s) failed.

## Sophie Tremblay

The survey produced **108** candidates across **22** institutions. The state is **complete**.

### Result profile

- Match bands: strong_match 108
- Holding status: likely_disposed 3, likely_held 14, may_still_be_held 6, retention_unknown 85
- Scope: institution_specific 90, standard 18
- Top institutions: Department of Health (19), Government of Canada institutions (18), Department of Employment and Social Development (12), Canada Employment Insurance Commission (10), Department of National Defence (8)
- Category coverage: 25 of 25 controlled categories; 9 result(s) uncategorized.
- Inventory gaps: federal_tax_return, federal_election.

### Fixture expectations

Expectation assertions failed: **0**.
- Expected ambiguities:
  - A dismissal, grievance, reinstatement and final departure need separate event dates; one timing for federal employment cannot express that sequence.
  - An internal administrative investigation is not necessarily federal law enforcement and should not be inferred from the security-screening answer.
  - Back pay, regular pay, pension adjustment and Employment Insurance have different institutions and retention triggers.
  - Divorce and child-support administration can be provincial, federal tax-related or interjurisdictional; a generic life-event fallback overmatches.
  - The generic complaint fallback cannot distinguish a labour grievance, adjudication, staffing complaint or human-rights complaint.
  - Workplace accommodation and disability records may live in employee, benefits and institution-specific systems rather than a generic federal-health program.
- Known false-positive risks:
  - generic health-program banks for workplace accommodation
  - generic research PIBs for an internal employee survey
  - unrelated family and vital-event banks
  - unrelated federal complaint and tribunal banks
- Known false-negative risks:
  - CMHC or CRA home-buying program records
  - department-specific performance-management and discipline files
  - labour grievance and adjudication records
  - public-service pension adjustments
  - reinstatement and back-pay calculations
  - workplace accommodation files

### Business-logic flags

- `fallback_route_selected`: 4 selected route(s) fall back to broad parent matching.
- `partial_route_selected`: 1 selected route(s) have only partial inventory coverage.
- `inventory_gap`: 2 selected interaction(s) have no defensible direct PIB.
- `retention_unknown_majority`: Retention is unknown for 85 of 108 results.
- `uncategorized_results`: 9 result(s) have no derived personal-information category.

## Interpretation guardrails

- An expected PIB is a test assertion, not proof that a real record exists.
- A likely false positive is reported only when the fixture names it, or when an explicit allowlist is supplied.
- High result counts and unknown retention are diagnostics for review, not automatic failures.
