# My Info Beta persona findings

Four synthetic personas were evaluated against questionnaire contract
`2026-08-22.3` as of 2026. The fixtures are test assertions, not claims that a
real person has records in any institution.

## Decision

The Beta should not treat a result reached only through a broad fallback as a
direct match. In this run, the four personas produced 908 candidates across
425 unique PIBs. All 908 were labelled `strong_match`, even though 780 results
were attributable only to fallback selections. This is the first logic change
to make before using the results as a citizen-facing estimate.

## Prioritized changes

1. Carry route coverage into confidence. Reserve `strong_match` for an
   explicit selector-to-PIB mapping. Label fallback-derived candidates as
   possible or review-only, and explain why they are broader.
2. Ask for a named institution or program after a broad selection. The highest
   value branches are grants and contributions, federal consulting and
   contracting, complaints and grievances, justice and investigations,
   housing, health support, consultations, and family events.
3. Support more than one episode for an interaction. A current relationship
   can coexist with an older closed file, and dismissal, grievance,
   reinstatement, and departure need separate dates and retention triggers.
4. Capture the event that starts the retention clock where the published rule
   depends on it: file closure, employment departure, licence expiry or
   revocation, final appeal, last administrative action, and sentence or parole
   completion. In this run, 619 of 908 candidates had unknown retention.
5. Add role-sensitive justice routing without requesting case details. A person
   may be an applicant, complainant, witness, victim, suspect, offender, or
   collateral contact; selecting every investigative PIB is not defensible.
6. Add targeted routes revealed by the personas: tri-council and Sport Canada
   support, nonprofit contribution agreements, CRA committee appointments,
   marine-occurrence investigations, CMHC mortgage insurance, correctional
   health, labour grievances and adjudication, public-service pension and back
   pay, workplace accommodation, and FINTRAC or departmental security
   screening.
7. Complete category enrichment for the 118 persona-results that lack a
   derived category, while keeping the published source evidence alongside the
   derived assignment.
8. Keep the known tax-return and federal-election inventory gaps visible. A
   broad unrelated result is not an acceptable substitute for missing source
   coverage.

## Interface consistency

The PDF renderer consumes the same controlled fixture and engine evaluation as
the web survey, and mirrors its status and institution hierarchy. Its markup is
currently a separate deterministic print template. Before production, extract
the results cards, labels, ordering, and print styles into one shared rendering
module so the live web results and generated PDF cannot drift.

## Persona-level observations

- Peter Deloitte exposes contractor-versus-employee ambiguity, multi-agency
  grant and sport support, marine investigation, committee appointments, and
  security-screening gaps.
- Dominic Vale shows why justice role and agency disambiguation are essential:
  an investigation or conviction cannot justify every RCMP or correctional PIB.
- Aisha Rahman shows that organizational funding, volunteering, emergency help,
  and evaluation surveys do not necessarily create personal client records.
- Sophie Tremblay shows that one date per question cannot model a multi-event
  employment, grievance, reinstatement, access, correction, and departure
  sequence.

The detailed counts, expected ambiguities, and known false-positive and
false-negative risks are in
`data/test_personas/generated/persona_analysis.md`.
