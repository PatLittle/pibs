# My Info business logic

## Purpose

My Info is an estimate of which Government of Canada personal information banks (PIBs)
may describe records about a person, based on interactions the person chooses to report.
It is a discovery aid, not a confirmation that a record exists and not a substitute for an
institution's Access to Information and Privacy office.

The first implementation phase derives auditable structure from the bilingual narrative fields
in the standard and institution-specific PIB datasets. Every derived value retains its matching
evidence, method, and confidence. The source text remains authoritative.

## Source population and identifiers

- Standard PIBs use `standard:<bank_number_key>` as their My Info record ID.
- Institution-specific PIBs use
  `institution:<institution_id>:<bank_number_key>` as their My Info record ID.
- Standard PIBs are reusable descriptions that may apply across many institutions; a standard
  PIB match must not imply that every institution holds that person's information.
- Institution-specific PIBs remain associated with the publishing institution.

## Derived feature families

### Categories of Personal Information

Each PIB can receive zero or more IDs from `pi_categories_en_fr.csv`. Assignments are derived
from explicit phrases in the English or French title, description, class, note, purpose, and
consistent-use fields. Output includes the matched phrase and source field. An empty assignment
means the rule set found no defensible evidence; it does not mean that the PIB contains no
personal information.

These assignments are estimates because the Info Source publications define the controlled
vocabulary but do not publish authoritative PIB-to-category relationships.

### Interaction and role signals

Narrative fields are mapped to a small citizen-facing topic taxonomy and a role taxonomy. The
questionnaire should ask about recognizable life events or government interactions rather than
PIB terminology. One affirmative answer can nominate several PIBs. Institution and role
follow-ups narrow the candidates when they provide useful discrimination.

### Retention and disposition

Retention text is parsed into a structured rule only where the wording supports it. The model
distinguishes fixed durations, minimum durations, ranges, event-triggered periods, age-based
rules, permanent or archival transfers, and unknown or under-development rules. It records the
trigger because an interaction year is not necessarily the same as a departure date, case
closure, last administrative action, or warrant expiry date.

## Questionnaire flow

1. Explain that the tool runs an estimate and that answers should not include account numbers,
   health details, case facts, or other sensitive free text.
2. Ask broad, multi-select interaction questions derived from the topic taxonomy.
3. Ask only the role and institution follow-ups that can reduce the candidate set.
4. For each selected interaction group, ask for an approximate year or bounded period.
5. If a candidate PIB uses a different retention trigger and the distinction can change the
   result, ask one plain-language trigger question, such as the year employment ended.
6. Score candidates and show why each matched, including whether it is a standard or
   institution-specific PIB.
7. Separate results into `likely still held`, `may still be held`, `likely disposed`, and
   `retention unknown`. Always link back to the source description when a link is available.

Answers should remain in the browser for the website implementation. No answer history or
analytics event should contain a person's selections unless a future, separately reviewed
privacy design explicitly authorizes it.

## Retention assessment rules

The assessment date and the user's approximate trigger year produce an elapsed-year interval,
not a falsely precise age. Conservative classification follows these principles:

- During an explicit minimum retention period, classify the PIB as `likely still held`.
- After a minimum-only period, classify it as `may still be held`; a minimum is not an expiry.
- After an explicit fixed maximum followed by destruction, classify it as `likely disposed`,
  while disclosing the approximate-date assumption.
- Transfer to Library and Archives Canada, archival retention, selective preservation, or an
  enduring-value exception prevents a simple `disposed` conclusion.
- Missing, under-development, institution-contact, event-dependent, and unparsed rules classify
  as `retention unknown` unless the known portion establishes a minimum still-held period.
- A standard PIB whose retention rule tells the user to contact the institution remains unknown;
  the existence of a Records Disposition Authority number is not itself a duration.

## Candidate scoring

The first-phase scorer should favour recall while making uncertainty visible. Candidate evidence
can include topic, role, institution, explicit action, category, and related-bank references.
Negative answers may suppress a candidate only when the question and rule are specific enough to
make that inference. Missing answers reduce confidence but do not become negative answers.

The generated data keeps both `primary` question mappings and broader `candidate` mappings.
Primary mappings require direct action, title-level topic evidence, or compatible topic-and-role
evidence. Candidate mappings maximize recall and can support the lower-confidence review band;
they must not be treated as equally strong merely because a term appears in a description.

Suggested display bands are:

- `strong match`: direct topic/action plus compatible role or institution evidence;
- `possible match`: one direct feature or several weaker features;
- `review if relevant`: broad standard or administrative PIB with insufficient discrimination.

The numeric score is an internal ordering aid and should not be presented as a probability that a
record exists.

## Known limitations requiring continued review

- Narrative text is inconsistent across institutions and some source rows have blank fields.
- Retention practices may differ from published descriptions or may have changed since capture.
- Standard PIB applicability must eventually be related to the institutions that actually use
  each standard bank.
- A deterministic keyword match can miss synonyms and can over-match negated or historical text.
- The category vocabulary includes overlapping concepts, such as biometric, medical, and
  physical-attribute information.
- Historical PIB descriptions may describe records no longer actively collected but still held.

The generated dataset is therefore a reviewable baseline. High-impact rules and low-confidence
records should be curated through an override layer rather than by silently changing source data.
