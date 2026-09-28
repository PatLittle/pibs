# My Info PIB-to-question matching audit

Generated from the current bilingual PIB feature inventory and adaptive-route selectors. Every record is classified in [`my_info_match_coverage.csv`](../data/audits/my_info_match_coverage.csv).

## What the percentages mean

| Reachability | PIBs | Share of 1,040 | Normal web results |
|---|---:|---:|---|
| Direct question or named activity route | 597 | 57.4% | Potentially shown after matching answers/refinements |
| Broad candidate match only | 423 | 40.7% | Hidden; the web uses `includePossible: false` |
| No matching question or route | 20 | 1.9% | Cannot be found by current questions |

The theoretical direct ceiling is **57.4%**. With optional possible matches enabled, the keyword-based ceiling is **98.1%**, but these broad signals can be false positives and should not be presented as confirmed holdings. The percentages are inventory coverage, not recall against real people's records. A single person will normally see far fewer PIBs because activities, department selection, and retention timing differ.
The faster ten-year path also skips the broader tax/customs, travel, and civic questions after its four selected common activities. Its personal reachability is therefore narrower than the full-survey ceiling; the UI discloses that older and other interactions are not ruled out.

## Largest candidate-only clusters

These overlapping counts identify where the question recognizes words in PIB text but lacks strong enough evidence or a named route to show the record in the normal web results.

| Question | Candidate-only PIBs |
|---|---:|
| `q_business_supplier` | 222 |
| `q_government_work` | 156 |
| `q_justice_safety` | 155 |
| `q_money_programs` | 136 |
| `q_health_disability` | 135 |
| `q_civic_contact` | 109 |
| `q_access_privacy` | 100 |
| `q_immigration` | 73 |
| `q_complaint_appeal` | 72 |
| `q_education_training` | 70 |
| `q_family_vital` | 68 |
| `q_indigenous_services` | 62 |
| `q_military_veterans` | 53 |
| `q_travel_border` | 45 |
| `q_culture_volunteer` | 39 |
| `q_research_survey` | 31 |
| `q_tax_customs` | 28 |
| `q_emergency` | 27 |
| `q_housing_property` | 14 |

The institutions with the most candidate-only PIBs are:

| Institution | Candidate-only PIBs |
|---|---:|
| Department of National Defence | 33 |
| Department of Health | 30 |
| Department of Fisheries and Oceans | 23 |
| Treasury Board Secretariat | 22 |
| Government of Canada institutions | 20 |
| Canada Employment Insurance Commission | 20 |
| Department of Employment and Social Development | 18 |
| Canada Border Services Agency | 17 |
| Department of Agriculture and Agri-Food | 14 |
| Public Health Agency of Canada | 14 |
| Public Service Commission | 14 |
| Department of Industry | 13 |
| Library and Archives of Canada | 13 |
| Parks Canada Agency | 13 |
| Royal Canadian Mounted Police | 12 |

## Concrete false-positive and source gaps

- `CSA PPU 020` describes registering to **attend a space mission launch**. Bare “registration” previously made this a direct business match. Registration alone is no longer a business signal; the PIB now requires the named public-event route, and unrelated candidate keywords such as passport or citizenship details cannot surface it.
- `HC PPU 035` is a pesticide-exposure **pilot study**, not an aviation-pilot licensing service. `IRCC PPU 080` involves identity and refugee travel **certificates**, not a business permit. Generic 'pilot' and 'certificate' signals no longer make these direct business matches.
- `ERC PPU 801–805` require the RCMP-member review route. A generic complaint cannot surface them; the department prompt asks who actually handled the complaint or appeal.
- Federal income-tax filing and federal voting remain explicit **source-inventory gaps**: the questionnaire asks about them, but this PIB inventory does not provide defensible named matches for those activity routes. A ten-year shortcut therefore must not invent results for them.
- 3 records with “registration” in the English title are not direct matches; they need a specific activity route or stronger context, not a generic business inference.

## Records the questions cannot discover

These are the current zero-signal cases, not necessarily PIBs that should all be shown to the general public. Several describe internal, technical, professional or institutional workflows; others have poorly parsed titles, so source quality and question design both need review.

| PIB | Institution | Title |
|---|---|---|
| `PSU 904` | Government of Canada institutions | Automated Document, Records, and Information Management Systems |
| `PSU 936` | Government of Canada institutions | Library Services |
| `ESDC PPU 036` | Department of Employment and Social Development | Conciliation Commissioner and Board Members Files (PIB) |
| `ESDC PPU 728` | Department of Employment and Social Development | Workplace Information, Collective Bargaining and Labour Organization Contacts (PIB) |
| `EC PPU 341` | Department of the Environment | Title:** Great Lakes Basin Monitoring and Surveillance program |
| `DFO PPU 680` | Department of Fisheries and Oceans | Habitat Management Referrals and Notifications |
| `DFO PPU 320` | Department of Fisheries and Oceans | Manuscript Reviews |
| `GAC PPU 101` | Department of Foreign Affairs, Trade and Development | Investor Information |
| `ISED PPU 023` | Department of Industry | Telecommunications Engineering and Certification Personal Information Bank |
| `ESDC PPU 706` | Department of Industry | Bank number**: ESDC PPU 706 |
| `PWGSC PPU 030` | Department of Public Works and Government Services | Register of real property appraisers—Personal information bank |
| `CGC PPU 215` | Canadian Grain Commission | ##### Unofficial Sample File (Personal Information Bank) |
| `CSE PPU 007` | Communications Security Establishment | Communications Security Establishment (CSE) - Cyber Defence, CSE PPU 007 - Personal Information Bank |
| `LAC PPU 040` | Library and Archives of Canada | Client Information (Loans to Other Institutions) (PIB) |
| `OPC PPU 003` | Office of the Privacy Commissioner | – Bank Number: OPC PPU 003 |
| `PSC PCE 796` | Public Service Commission | Second Language Evaluation Examiners |
| `STJPA PPU 007` | St. John’s Port Authority | Restricted Area Passes |
| `TBS PCE 722` | Treasury Board Secretariat | Certification |
| `TBS PCE 745` | Treasury Board Secretariat | Executive Group Classification Information System |
| `TBS PCE 729` | Treasury Board Secretariat | Interchange Canada Reporting Application |

## Interpretation and next review priorities

1. Manually review the high-volume candidate-only business, employment, justice, money, and health clusters against the actual class of individuals and purpose text. A matching word may be a piece of information held, not an activity the person performed.
2. Add named, source-backed routes for common activities only when the PIB's purpose and eligible population align. A route should not be added merely to increase the coverage percentage.
3. Repair malformed or generic source titles among the zero-signal cases, then reassess whether a user-facing question is warranted for each service.
4. Keep separate tests for false-positive cases, especially records whose titles use broad words such as registration, service, application, health, or contact.

Rebuild the audit with `.venv/bin/python scripts/audit_my_info_match_coverage.py`. Run `build_my_info_features.py` first after changing classification rules or routes.
