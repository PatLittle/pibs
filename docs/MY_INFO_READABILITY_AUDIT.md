# My Info English question readability audit

This audit screens every current English top-level question with the Flesch Reading Ease formula. It is a comparative plain-language screen, not a substitute for user testing or content-design review.

## Method

The score is `206.835 - 1.015 × words per sentence - 84.6 × syllables per word`. Words are English alphabetic tokens; hyphenated and apostrophized terms count as one word, with each component included in the syllable estimate. The syllable heuristic counts vowel groups, treats `y` as a vowel when it is not next to another vowel, removes a likely silent final `e` except consonant + `le`, and assigns at least one syllable to each non-empty word part.

The conventional bands are: 90+ very easy; 80–89 easy; 70–79 fairly easy; 60–69 standard; 50–59 fairly difficult; 30–49 difficult; below 30 very difficult. This audit flags scores below 60 for review. The threshold is configurable in `my_info.readability.flesch_reading_ease`.

Flesch Reading Ease is an English formula. **Do not use these scores to assess the French questions.** French copy needs a French-language measure and fluent plain-language review.

## Results

20 of 21 current questions score below 60. The many flags reflect long grouped questions and unavoidable multisyllabic program terms as well as genuine wording complexity. The proposed wording moves detailed program types into examples or follow-ups.

| Code | Current score | Band | Proposed score | Change |
|---|---:|---|---:|---:|
| `q_government_work` | 36.2 | difficult | 80.3 | 44.1 |
| `q_money_programs` | 37.3 | difficult | 69.8 | 32.5 |
| `q_tax_customs` | 37.5 | difficult | 67.8 | 30.3 |
| `q_immigration` | -9.8 | very difficult | 70.0 | 79.8 |
| `q_travel_border` | 22.4 | very difficult | 67.8 | 45.4 |
| `q_health_disability` | -23.9 | very difficult | 78.2 | 102.1 |
| `q_indigenous_services` | 45.0 | difficult | 65.7 | 20.7 |
| `q_military_veterans` | 41.6 | difficult | 63.5 | 21.9 |
| `q_education_training` | 30.9 | difficult | 70.0 | 39.1 |
| `q_justice_safety` | 26.7 | very difficult | 58.4 | 31.7 |
| `q_complaint_appeal` | 47.6 | difficult | 79.6 | 32.0 |
| `q_access_privacy` | -23.3 | very difficult | 67.5 | 90.8 |
| `q_business_supplier` | 31.7 | difficult | 60.2 | 28.5 |
| `q_firearms` | 37.3 | difficult | 69.8 | 32.5 |
| `q_boating` | 45.3 | difficult | 63.5 | 18.2 |
| `q_housing_property` | 34.2 | difficult | 81.9 | 47.7 |
| `q_civic_contact` | 0.5 | very difficult | 71.8 | 71.3 |
| `q_culture_volunteer` | 10.4 | very difficult | 65.7 | 55.3 |
| `q_research_survey` | 65.7 | standard | — | — |
| `q_emergency` | 11.4 | very difficult | 70.0 | 58.6 |
| `q_family_vital` | 45.3 | difficult | 65.7 | 20.4 |

## Questions flagged for rewording

### `q_government_work`

Current (36.2, difficult): Have you ever applied to work for, worked for, or received an employment-related service from the Government of Canada?

Candidate (80.3, easy): Have you applied for a federal job or worked for one?

### `q_money_programs`

Current (37.3, difficult): Have you ever applied for or received a federal benefit, grant, loan, reimbursement or other payment?

Candidate (69.8, standard): Did a federal program give you money or other help?

### `q_tax_customs`

Current (37.5, difficult): Have you filed federal taxes, paid federal duties, or made a customs declaration?

Candidate (67.8, standard): Did you ever file federal taxes or declare goods at the border?

### `q_immigration`

Current (-9.8, very difficult): Have you used a Canadian immigration, refugee, visa, permanent-residence or citizenship process?

Candidate (70.0, fairly easy): Have you applied to move to Canada, stay here or become a citizen?

### `q_travel_border`

Current (22.4, very difficult): Have you applied for a Canadian passport, crossed Canada’s border, or joined a trusted-traveller program?

Candidate (67.8, standard): Have you applied for a passport, crossed the border or used NEXUS?

### `q_health_disability`

Current (-23.9, very difficult): Have you received a federal health, dental, rehabilitation, disability or medical-device service?

Candidate (78.2, fairly easy): Did a federal health program give you care or support?

### `q_indigenous_services`

Current (45.0, difficult): Have you used a federal service specifically for First Nations, Inuit or Métis people?

Candidate (65.7, standard): Have you used a federal service for First Nations, Inuit or Métis people?

### `q_military_veterans`

Current (41.6, difficult): Have you served in the Canadian Armed Forces or used a federal veterans program?

Candidate (63.5, standard): Have you served in the Armed Forces or received help as a veteran?

### `q_education_training`

Current (30.9, difficult): Have you applied for federal student aid, an apprenticeship, scholarship or training program?

Candidate (70.0, fairly easy): Has the Government of Canada helped pay for your school or job training?

### `q_justice_safety`

Current (26.7, very difficult): Have you been involved in a matter handled by federal law enforcement, security screening or corrections?

Candidate (58.4, fairly difficult): Did you have a security check or deal with a federal law officer, prison or parole?

### `q_complaint_appeal`

Current (47.6, difficult): Have you made a complaint, grievance or appeal to a federal institution or tribunal?

Candidate (79.6, fairly easy): Did you file a complaint or ask a federal office to review a choice it made?

### `q_access_privacy`

Current (-23.3, very difficult): Have you made an access-to-information, personal-information access, or correction request?

Candidate (67.5, standard): Have you asked a federal office for records about you or to fix your records?

### `q_business_supplier`

Current (31.7, difficult): Have you owned or operated a business, held a federal licence or permit, or contracted with the federal government?

Candidate (60.2, standard): Did you run a business, get a federal permit or sell goods or services to the government?

### `q_firearms`

Current (37.3, difficult): Have you applied for, renewed or held a Canadian firearms licence, or registered a restricted firearm?

Candidate (69.8, standard): Have you had a firearms licence or registered a gun?

### `q_boating`

Current (45.3, difficult): Have you held a Pleasure Craft Operator Card or licensed or registered a boat with Transport Canada?

Candidate (63.5, standard): Have you had a boating card or registered a boat with Transport Canada?

### `q_housing_property`

Current (34.2, difficult): Have you used a federal housing, mortgage, home-buying or property program?

Candidate (81.9, easy): Have you used a federal program to rent or buy a home?

### `q_civic_contact`

Current (0.5, very difficult): Have you contacted a federal institution, joined a consultation, signed a petition, or participated in a federal election process?

Candidate (71.8, fairly easy): Did you contact a federal office, share your views, sign a petition or vote?

### `q_culture_volunteer`

Current (10.4, very difficult): Have you participated in or volunteered for a federally run cultural, sport, recreation, heritage or park activity?

Candidate (65.7, standard): Have you joined or helped with a federal arts, sports, heritage or parks event?

### `q_emergency`

Current (11.4, very difficult): Have you requested or received federal help during an emergency, evacuation or disaster?

Candidate (70.0, fairly easy): Did you ask for federal help in a crisis or after a disaster?

### `q_family_vital`

Current (45.3, difficult): Have you used a federal service involving a birth, marriage, divorce, adoption, child support, death or estate?

Candidate (65.7, standard): Did you use a federal service for a birth, wedding, divorce, adoption or death?

## Design observations

- `q_research_survey` is the only current question at or above the audit threshold (65.7). It can remain as written, subject to usability testing.
- `q_justice_safety` remains below 60 even after a shorter rewrite. It combines sensitive, distinct interactions and should be split into short adaptive routing questions.
- `q_business_supplier` crosses the numeric threshold after rewriting, but still combines unrelated contracting, licensing, and permit routes. Its readability score does not remove the need to split it.
- `q_tax_customs`, `q_travel_border`, and `q_military_veterans` also combine activities owned by different institutions. Readability improves when the survey first asks about the familiar activity and infers the likely institution.
- A score can improve by deleting essential meaning. Rewrites therefore need semantic review against the PIB routing rules; the highest score is not automatically the best question.
- Keep examples outside the score-bearing question (for example, in expandable help or the conversational agent's optional explanation). This makes the main prompt short without hiding unfamiliar terms.

Regenerate the CSV and this report with:

```bash
.venv/bin/python scripts/audit_my_info_readability.py
```
