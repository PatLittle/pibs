# My Info V1 — survey logic review

Generated from checked-in contract 2026-09-28.6. This is a review of existing behaviour, not a proposed redesign. The accompanying logic.json contains the complete contract views, selectors, source-linked inventory rows and input fingerprints; pib_mapping.csv supports spreadsheet review.

## Coverage and reading guide

| Reachability (theoretical) | PIBs | Share |
| --- | --- | --- |
| Primary question or named route | 597 | 57.4% |
| Candidate only; hidden in normal web | 423 | 40.7% |
| No current route or question | 20 | 1.9% |

Denominator: 1,040 collected inventory rows. This is a static upper bound before a person's answers and department restrictions. It does not measure accuracy, population prevalence or real-world recall. Question counts below overlap. Follow-up department lists are calculated from the Python engine for each option selected alone; multi-option selections can produce different lists.

### Survey flow

Start → quick check or individual path → next unanswered topic → if yes, select a named activity when offered → timing for each selected activity → department selection when required → repeat → candidate results. No, not sure and prefer not to answer advance without follow-ups. The normal web hides uncertain/possible-only results.

### Quick path

The opening yes means use the shortcut, not yes to every activity. The web preselects tax filing, voting, passport and border crossing; unchecked activities are omitted. Empty selection becomes none_recent, which cannot coexist with another option. Every selected activity uses 0–10 years. Once the shortcut has a refinement, the engine skips q_tax_customs, q_travel_border and q_civic_contact, even when none_recent is selected. This also skips other customs, trusted-traveller and civic activities; absence of results cannot rule these out. The detailed path has 22 gates; the quick path has 19. These counts exclude refinement, date and department screens.

### Department rule

After timing, ask for departments only if the available list has more than one institution; complaints ask even for a singleton. Department options are built from primary-classified rows for that gate, filtered by named selectors unless an Other fallback is chosen. They are not built from all selector records. Several selected activities share one combined department follow-up. Displayed institution hints do not themselves set a department answer. Rows with an empty institution ID pass any department filter.

### Why some follow-ups feel redundant

Veterans-payment selected alone currently yields only Veterans Affairs and skips the department step. Selecting another payment option can create a combined follow-up. CAF-service selected alone yields National Defence and Library and Archives of Canada because the inventory includes archived military records. Asking the person to choose the archive implies knowledge they may not have. A future design should distinguish an activity's responsible institution from later custodians, while retaining source-backed cross-institution cases such as Service Canada delivery.

### Named versus broad matching

A named activity selects every inventory row with one of its exact bank-number keys, subject to department filtering. It does not independently check eligibility or the purpose/class-of-individuals text. Selecting only named activities suppresses the broad parent-question match. Selecting an Other fallback re-enables all primary matches for that topic and, when requested, candidate matches. Exclusive banks (including CSA launch attendance and ERC member reviews) require their named selector route.

### Match confidence

A primary topic or exact named route yields strong_match. Candidate-only topic signals yield possible_match only when include_possible is true. Not sure/prefer not to answer can yield review_if_relevant only when that option is enabled. The ordinary web passes includePossible: false. Strong is the engine's label, not independently validated precision. Personal-information fields such as citizenship or passport numbers can produce misleading topical signals without proving that the person used an immigration or passport service.

### Standard banks and ownership

A standard PIB describes a reusable government-wide record class. It is not evidence that every institution holds that person's information. Standard records often have no institution ID and therefore survive department selection. Work, correspondence, access requests and complaints require an actual institution/activity context; the current model does not bind every standard bank to that context.

### Partial sources and absent results

The denominator is the collected PIB inventory, not all federal holdings. Missing or rejected source pages, incomplete bilingual captures, aliases and poorly parsed titles can hide programs. Federal tax filing and federal voting currently have explicit inventory_gap options with no bank selectors. Asking these questions creates no direct tax/voting result. Institution responsibilities and a program's existence do not alone prove an applicable PIB or retention rule.

### Timing vocabulary

The engine accepts current, within_1_year, 1_to_3_years, 4_to_7_years, 8_to_15_years, more_than_15_years, approximate_year and unknown. Numeric intervals are respectively 0; 0–1; 1–3; 4–7; 8–15; 16+ years. Approximate year subtracts the year from the evaluation year. The shortcut's internal within_10_years means 0–10. Dates describe the latest interaction, which may differ from a file's retention trigger.

### Retention decision order

Missing/unknown timing gives retention_unknown, even for an indefinite rule. Otherwise indefinite retention gives likely_held unless immediate disposal is possible. Unknown, pending, institution-defined, schedule-defined or trigger-based rules give retention_unknown. Mixed immediate/indefinite branches also give unknown. Any reference event other than unspecified start, record creation/receipt or issue date gives unknown because the interaction date cannot establish closure, departure or another trigger.

### Numeric retention decisions

When the entire elapsed interval is beyond the published maximum: destruction yields likely_disposed, while transfer to archives yields likely_held. When the entire interval is strictly below the published minimum/fixed period, it yields likely_held. Boundary overlap and other numeric cases yield may_still_be_held. If several matched activities yield estimates, the engine chooses the most retention-preserving status: likely_held, then may_still_be_held, then unknown, then likely_disposed. These estimates are not confirmation of current holdings or completed destruction.

### Review priorities

Check each named selector against eligible population and actual activity; clarify multi-institution service delivery and archives; split broad Other branches where they overmatch; preserve specialist discoveries without asking everyone specialist questions; remove hidden quick-path coverage losses; repair source gaps before promising comprehensive coverage; and test plain-language English and French with people unfamiliar with government terminology.

## Gate index

| Order | Gate | Displayed English prompt | Options | Primary / candidate rows |
| --- | --- | --- | --- | --- |
| 1 | q_common_start | Many adults in Canada have filed taxes, voted federally, applied for a passport or crossed the border in the past 10 years. Want to check these together? I can ask one by one for more precise timing. | 5 | 0 / 0 |
| 2 | q_government_work | Have you applied for a federal job or worked for one? | 3 | 87 / 388 |
| 3 | q_money_programs | Did a federal program give you money or other help? | 5 | 121 / 385 |
| 4 | q_tax_customs | Did you ever file federal taxes or declare goods at the border? | 3 | 1 / 106 |
| 5 | q_immigration | Have you applied to move to Canada, stay here or become a citizen? | 3 | 38 / 248 |
| 6 | q_travel_border | Have you applied for a passport, crossed the border or used NEXUS? | 4 | 30 / 143 |
| 7 | q_health_disability | Did a federal health program give you care or support? | 3 | 58 / 402 |
| 8 | q_indigenous_services | Have you used a federal service for First Nations, Inuit or Métis people? | 3 | 30 / 159 |
| 9 | q_military_veterans | Have you served in the Armed Forces or received help as a veteran? | 3 | 35 / 176 |
| 10 | q_education_training | Has the Government of Canada helped pay for your school or job training? | 3 | 38 / 213 |
| 11 | q_justice_safety | Did you have a security check or deal with a federal law officer, prison or parole? | 4 | 91 / 474 |
| 12 | q_complaint_appeal | Did you file a complaint or ask a federal office to review a choice it made? | 4 | 56 / 252 |
| 13 | q_access_privacy | Have you asked a federal office for records about you or to fix your records? | 3 | 14 / 268 |
| 14 | q_business_supplier | Did you run a business, get a federal permit or sell goods or services to the government? | 3 | 110 / 577 |
| 15 | q_firearms | Have you had a firearms licence or registered a gun? | 3 | 0 / 0 |
| 16 | q_boating | Have you had a boating card or registered a boat with Transport Canada? | 5 | 0 / 0 |
| 17 | q_housing_property | Have you used a federal program to rent or buy a home? | 3 | 9 / 41 |
| 18 | q_civic_contact | Did you contact a federal office, share your views, sign a petition or vote? | 3 | 14 / 241 |
| 19 | q_culture_volunteer | Have you registered for a federal public event, or joined a federal arts, sports, heritage, parks or volunteer activity? | 4 | 18 / 130 |
| 20 | q_research_survey | Have you taken part in federal research, a survey, testing or a focus group? | 3 | 5 / 82 |
| 21 | q_emergency | Did you ask for federal help in a crisis or after a disaster? | 3 | 6 / 86 |
| 22 | q_family_vital | Did you use a federal service for a birth, wedding, divorce, adoption or death? | 3 | 1 / 224 |

## 1. q_common_start

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Many adults in Canada have filed taxes, voted federally, applied for a passport or crossed the border in the past 10 years. Want to check these together? I can ask one by one for more precise timing. |
| Displayed FR | De nombreux adultes au Canada ont produit une déclaration de revenus, voté à une élection fédérale, demandé ou renouvelé un passeport, ou franchi la frontière au cours des dix dernières années. Voulez-vous vérifier ces quatre activités ensemble? Je peux aussi vous poser les questions séparément pour estimer plus précisément la durée de conservation. |
| Source EN before readability rewrite | Many adult Canadians have filed income taxes, voted federally, applied for or renewed a passport, or crossed the border in the past 10 years. Would you like to check those four activities together? I can also ask about each one separately for a more precise retention estimate. |
| Answers | yes, no |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | The quick check uses one ten-year window. Individual questions let you give separate dates and cover other tax, travel, and civic interactions. |
| FR help note | La vérification rapide utilise une seule période de dix ans. Les questions individuelles permettent de donner des dates distinctes et de couvrir d'autres interactions fiscales, de voyage et civiques. |

Refinement EN: Which of these have you done at least once in the past 10 years? You can say all, none, or name the ones that apply. Uncheck any that do not apply; we will use the same broad ten-year window for the selected activities.

Refinement FR: Qu'avez-vous fait au moins une fois au cours des dix dernières années? Vous pouvez répondre « toutes », « aucune » ou nommer les activités pertinentes. Décochez celles qui ne s'appliquent pas; nous utiliserons la même période approximative de dix ans pour les activités choisies.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### federal_tax_return

| Field | Value |
| --- | --- |
| EN answer | Filed a federal income tax return |
| FR answer | Produit une déclaration fédérale de revenus |
| Implied institution EN | Canada Revenue Agency |
| Implied institution FR | Agence du revenu du Canada |
| Coverage label | inventory_gap |
| Ask timing | False |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### federal_election

| Field | Value |
| --- | --- |
| EN answer | Voted in a federal election |
| FR answer | Voté à une élection fédérale |
| Implied institution EN | Elections Canada |
| Implied institution FR | Élections Canada |
| Coverage label | inventory_gap |
| Ask timing | False |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### passport_application

| Field | Value |
| --- | --- |
| EN answer | Applied for or renewed a Canadian passport |
| FR answer | Demandé ou renouvelé un passeport canadien |
| Implied institution EN | Immigration, Refugees and Citizenship Canada / Service Canada |
| Implied institution FR | Immigration, Réfugiés et Citoyenneté Canada / Service Canada |
| Coverage label | direct |
| Ask timing | False |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | IRCC PPU 081, ESDC PPU 708 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| IRCC PPU 081 | Department of Citizenship and Immigration | Regular and Official Passports (PPU 081) / Passeports réguliers et officiels (PPU 081) | — |
| ESDC PPU 708 | Department of Employment and Social Development | Passport Program (PIB) / Programme de passeport (FRP) | — |
| ESDC PPU 708 | Canada Employment Insurance Commission | Passport Program (PIB) / Programme de passeport (FRP) | — |

### border_crossing

| Field | Value |
| --- | --- |
| EN answer | Crossed Canada's international border |
| FR answer | Franchi la frontière internationale du Canada |
| Implied institution EN | Canada Border Services Agency |
| Implied institution FR | Agence des services frontaliers du Canada |
| Coverage label | direct |
| Ask timing | False |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CBSA PPU 008, CBSA PPU 010, CBSA PPU 014, CBSA PPU 018 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CBSA PPU 018 | Canada Border Services Agency | Traveller Declaration Cards – Personal Information Bank / Carte de déclaration du voyageur – Fichier de renseignements personnels | — |
| CBSA PPU 008 | Canada Border Services Agency | Advance Passenger Information and Passenger Name Record Programs (API/PNR) – Personal Information Bank / Le programme Information préalable sur les voyageurs et du dossier passager (IPV et DP) – Fichier de renseignements personnels | — |
| CBSA PPU 014 | Canada Border Services Agency | Clients Interviewed by an Officer (DOW) – Personal Information Bank / Clients rencontrés par un agent (DOW) – Fichier de renseignements personnels | — |
| CBSA PPU 010 | Canada Border Services Agency | Travellers Entry Processing System (TEPS) / Travellers National Database System (TRANDS) – Personal Information Bank / Système de traitement des déclarations des voyageurs (STDV)/Système de base de données nationale sur les voyageurs (SBDNV) – Fichier de renseignements personnels | — |

### none_recent

| Field | Value |
| --- | --- |
| EN answer | None of these in the past 10 years |
| FR answer | Aucune de ces activités au cours des dix dernières années |
| Implied institution EN | No institution selected |
| Implied institution FR | Aucune institution sélectionnée |
| Coverage label | partial |
| Ask timing | False |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

No primary-topic institution options.

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 2. q_government_work

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you applied for a federal job or worked for one? |
| Displayed FR | Avez-vous déjà postulé ou travaillé au gouvernement du Canada, ou reçu un service lié à cet emploi? |
| Source EN before readability rewrite | Have you ever applied to work for, worked for, or received an employment-related service from the Government of Canada? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Split job applications from employment records; their dates and retention triggers differ. |
| FR help note | Séparer les demandes d'emploi des dossiers d'emploi; leurs dates et leurs déclencheurs de conservation diffèrent. |

Refinement EN: Which federal work situations apply to you? Select all that apply.

Refinement FR: Quelles situations de travail fédéral s'appliquent à vous? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### federal_job_application

| Field | Value |
| --- | --- |
| EN answer | I applied for a federal job |
| FR answer | J'ai postulé à un emploi fédéral |
| Implied institution EN | Public Service Commission of Canada or the hiring department |
| Implied institution FR | Commission de la fonction publique du Canada ou ministère d'embauche |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSU 911, PSE 902, PSC PPU 040, PSC PCU 025 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 911 | Government of Canada institutions | Applications for Employment / Demandes d’emploi | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu911) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou911) |
| PSE 902 | Government of Canada institutions | Staffing / Dotation | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse902) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe902) |
| PSC PPU 040 | Public Service Commission | Personnel Selection / Sélection du personnel | — |
| PSC PCU 025 | Public Service Commission | Assessment by the Personnel Psychology Centre / Évaluation par le Centre de psychologie du personnel | — |

### federal_employee

| Field | Value |
| --- | --- |
| EN answer | I worked for the federal government |
| FR answer | J'ai travaillé pour le gouvernement fédéral |
| Implied institution EN | The person's federal employer and central personnel systems |
| Implied institution FR | Employeur fédéral de la personne et systèmes centraux de personnel |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSE 901, PSE 903, PSE 904, PSE 906, PSE 907, PSE 911, PSE 912, PSE 914, PSE 918, PSE 919, PSE 920 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSE 903 | Government of Canada institutions | Attendance and Leave / Présences et congés | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse903) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe903) |
| PSE 911 | Government of Canada institutions | Discipline / Mesures disciplinaires | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse911) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe911) |
| PSE 912 | Government of Canada institutions | Employee Performance Management Program / Programme de gestion du rendement des employés | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse912) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe912) |
| PSE 901 | Government of Canada institutions | Employee Personnel Record / Dossier personnel d’un employé | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse901) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe901) |
| PSE 918 | Government of Canada institutions | Employment Equity and Diversity / Équité en emploi et diversité | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse918) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe918) |
| PSE 919 | Government of Canada institutions | Harassment and Violence / Harcèlement et violence | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse919) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe919) |
| PSE 907 | Government of Canada institutions | Occupational Health and Safety / Santé et sécurité au travail | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse907) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe907) |
| PSE 906 | Government of Canada institutions | Official Languages / Langues officielles | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse906) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe906) |
| PSE 914 | Government of Canada institutions | Parking / Stationnement | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse914) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe914) |
| PSE 904 | Government of Canada institutions | Pay and Benefits / Rémunération et avantages | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse904) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe904) |
| PSE 920 | Government of Canada institutions | Recognition Program / Programme de reconnaissance | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse920) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe920) |

### other_federal_work_service

| Field | Value |
| --- | --- |
| EN answer | Another federal work-related service |
| FR answer | Un autre service lié au travail fédéral |
| Implied institution EN | Government of Canada institution involved |
| Implied institution FR | Institution du gouvernement du Canada concernée |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Centre for Occupational Health and Safety / Centre canadien d’hygiène et de sécurité au travail [ati-schedule-i-canadian-centre-for-occupational-health-and-safety]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Department of Canadian Heritage / Ministère du Patrimoine canadien [ati-schedule-i-department-of-canadian-heritage]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Housing, Infrastructure and Communities / Ministère du Logement, de l’Infrastructure et des Collectivités [ati-schedule-i-department-of-housing-infrastructure-and-communities]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Safety and Emergency Preparedness / Ministère de la Sécurité publique et de la Protection civile [ati-schedule-i-department-of-public-safety-and-emergency-preparedness]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport]; Library and Archives of Canada / Bibliothèque et Archives du Canada [ati-schedule-i-library-and-archives-of-canada]; Parks Canada Agency / Agence Parcs Canada [ati-schedule-i-parks-canada-agency]; Privy Council Office / Bureau du Conseil privé [ati-schedule-i-privy-council-office]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada]; Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police]; Shared Services Canada / Services partagés Canada [ati-schedule-i-shared-services-canada]; Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-centre-for-occupational-health-and-safety | Canadian Centre for Occupational Health and Safety | Centre canadien d’hygiène et de sécurité au travail |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-department-of-canadian-heritage | Department of Canadian Heritage | Ministère du Patrimoine canadien |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-housing-infrastructure-and-communities | Department of Housing, Infrastructure and Communities | Ministère du Logement, de l’Infrastructure et des Collectivités |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-safety-and-emergency-preparedness | Department of Public Safety and Emergency Preparedness | Ministère de la Sécurité publique et de la Protection civile |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-department-of-transport | Department of Transport | Ministère des Transports |
| ati-schedule-i-library-and-archives-of-canada | Library and Archives of Canada | Bibliothèque et Archives du Canada |
| ati-schedule-i-parks-canada-agency | Parks Canada Agency | Agence Parcs Canada |
| ati-schedule-i-privy-council-office | Privy Council Office | Bureau du Conseil privé |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |
| ati-schedule-i-public-service-commission | Public Service Commission | Commission de la fonction publique |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |
| ati-schedule-i-shared-services-canada | Shared Services Canada | Services partagés Canada |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 3. q_money_programs

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did a federal program give you money or other help? |
| Displayed FR | Avez-vous déjà demandé ou reçu une prestation, une subvention, un prêt, un remboursement ou un autre paiement fédéral? |
| Source EN before readability rewrite | Have you ever applied for or received a federal benefit, grant, loan, reimbursement or other payment? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Use named benefit families as child questions; 'other payment' is too broad to route reliably. |
| FR help note | Utiliser des familles de prestations nommées comme sous-questions; « autre paiement » est trop large pour orienter de façon fiable. |

Refinement EN: What kind of federal payment or support was it? Select all that apply.

Refinement FR: Quel type de paiement ou de soutien fédéral était-ce? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### employment_pay_reimbursement

| Field | Value |
| --- | --- |
| EN answer | Federal employee pay, benefits or reimbursement |
| FR answer | Paie, avantages sociaux ou remboursement d'un employé fédéral |
| Implied institution EN | The person's federal employer and Treasury Board systems |
| Implied institution FR | Employeur fédéral de la personne et systèmes du Conseil du Trésor |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSU 931, PSE 904 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 931 | Government of Canada institutions | Accounts Payable / Comptes créditeurs | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu931) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou931) |
| PSE 904 | Government of Canada institutions | Pay and Benefits / Rémunération et avantages | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse904) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#poe904) |

### employment_insurance

| Field | Value |
| --- | --- |
| EN answer | Employment Insurance |
| FR answer | Assurance-emploi |
| Implied institution EN | Employment and Social Development Canada / Service Canada |
| Implied institution FR | Emploi et Développement social Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ESDC PPU 151, ESDC PPU 180, ESDC PPU 501 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 151 | Department of Employment and Social Development | Employment Insurance Claim Files (PIB) / Dossiers de demandes d'assurance-emploi (FRP) | — |
| ESDC PPU 180 | Department of Employment and Social Development | Benefit and Overpayment File (PIB) / Fichier des prestations et des trop-payés (FRP) | — |
| ESDC PPU 501 | Department of Employment and Social Development | Employment Insurance Databank (PIB) / Base de données de l'assurance-emploi (FRP) | — |
| ESDC PPU 151 | Canada Employment Insurance Commission | Employment Insurance Claim Files (PIB) / Dossiers de demandes d'assurance-emploi (FRP) | — |
| ESDC PPU 180 | Canada Employment Insurance Commission | Benefit and Overpayment File (PIB) / Fichier des prestations et des trop-payés (FRP) | — |
| ESDC PPU 501 | Canada Employment Insurance Commission | Employment Insurance Databank (PIB) / Base de données de l'assurance-emploi (FRP) | — |

### cpp_oas

| Field | Value |
| --- | --- |
| EN answer | Canada Pension Plan or Old Age Security |
| FR answer | Régime de pensions du Canada ou Sécurité de la vieillesse |
| Implied institution EN | Employment and Social Development Canada / Service Canada |
| Implied institution FR | Emploi et Développement social Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ESDC PPU 140, ESDC PPU 146 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 146 | Department of Employment and Social Development | Canada Pension Plan Program (PIB) / Régime de pensions du Canada (FRP) | — |
| ESDC PPU 140 | Department of Employment and Social Development | Canada Pension Plan - Record of Earnings (PIB) / Régime de pensions du Canada - Registre des gains (FRP) | — |
| ESDC PPU 146 | Canada Employment Insurance Commission | Canada Pension Plan Program (PIB) / Régime de pensions du Canada (FRP) | — |
| ESDC PPU 140 | Canada Employment Insurance Commission | Canada Pension Plan - Record of Earnings (PIB) / Régime de pensions du Canada - Registre des gains (FRP) | — |

### veterans_payment

| Field | Value |
| --- | --- |
| EN answer | A veterans benefit or payment |
| FR answer | Une prestation ou un paiement pour vétérans |
| Implied institution EN | Veterans Affairs Canada, sometimes delivered with Service Canada |
| Implied institution FR | Anciens Combattants Canada, parfois avec Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | VAC PPU 040, VAC PPU 200, VAC PPU 710, VAC PPU 715, ACC PPU 350, ESDC PPU 701 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Veterans Affairs / Ministère des Anciens Combattants [ati-schedule-i-department-of-veterans-affairs] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 701 | Department of Employment and Social Development | Veterans Affairs Canada Program Delivery (PIB) / Exécution des programmes d'Anciens Combattants Canada (FRP) | — |
| VAC PPU 710 | Department of Veterans Affairs | You are here /  | — |
| VAC PPU 715 | Department of Veterans Affairs | You are here /  | — |
| VAC PPU 040 | Department of Veterans Affairs | You are here /  | — |
| VAC PPU 200 | Department of Veterans Affairs | You are here /  | — |
| ACC PPU 350 | Department of Veterans Affairs |  / Vous êtes ici | — |
| ESDC PPU 701 | Canada Employment Insurance Commission | Veterans Affairs Canada Program Delivery (PIB) / Exécution des programmes d'Anciens Combattants Canada (FRP) | — |

### other_payment_program

| Field | Value |
| --- | --- |
| EN answer | Another grant, loan, benefit or payment |
| FR answer | Une autre subvention, un autre prêt, une autre prestation ou un autre paiement |
| Implied institution EN | Federal institution that ran the program |
| Implied institution FR | Institution fédérale responsable du programme |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Atlantic Canada Opportunities Agency / Agence de promotion économique du Canada atlantique [ati-schedule-i-atlantic-canada-opportunities-agency]; Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canada Revenue Agency / Agence du revenu du Canada [ati-schedule-i-canada-revenue-agency]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Canadian Space Agency / Agence spatiale canadienne [ati-schedule-i-canadian-space-agency]; Department of Agriculture and Agri-Food / Ministère de l’Agriculture et de l’Agroalimentaire [ati-schedule-i-department-of-agriculture-and-agri-food]; Department of Canadian Heritage / Ministère du Patrimoine canadien [ati-schedule-i-department-of-canadian-heritage]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Crown-Indigenous Relations and Northern Affairs / Ministère des Relations Couronne-Autochtones et des Affaires du Nord [ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Finance / Ministère des Finances [ati-schedule-i-department-of-finance]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Housing, Infrastructure and Communities / Ministère du Logement, de l’Infrastructure et des Collectivités [ati-schedule-i-department-of-housing-infrastructure-and-communities]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Department of Industry / Ministère de l’Industrie [ati-schedule-i-department-of-industry]; Department of Justice / Ministère de la Justice [ati-schedule-i-department-of-justice]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Safety and Emergency Preparedness / Ministère de la Sécurité publique et de la Protection civile [ati-schedule-i-department-of-public-safety-and-emergency-preparedness]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Department of the Environment / Ministère de l’Environnement [ati-schedule-i-department-of-the-environment]; Department of Veterans Affairs / Ministère des Anciens Combattants [ati-schedule-i-department-of-veterans-affairs]; Department of Western Economic Diversification / Ministère de la Diversification de l’économie de l’Ouest canadien [ati-schedule-i-department-of-western-economic-diversification]; Economic Development Agency of Canada for the Regions of Quebec / Agence de développement économique du Canada pour les régions du Québec [ati-schedule-i-economic-development-agency-of-canada-for-the-regions-of-quebec]; Federal Economic Development Agency for Northern Ontario / Agence fédérale de développement économique pour le Nord de l’Ontario [ati-schedule-i-federal-economic-development-agency-for-northern-ontario]; National Research Council of Canada / Conseil national de recherches du Canada [ati-schedule-i-national-research-council-of-canada]; Office of the Administrator of the Fund for Railway Accidents Involving Designated Goods / Bureau de l’administrateur de la Caisse d’indemnisation pour les accidents ferroviaires impliquant des marchandises désignées [ati-schedule-i-office-of-the-administrator-of-the-fund-for-railway-accidents-involving-designated-goods]; Office of the Administrator of the Ship-source Oil Pollution Fund / Bureau de l’administrateur de la Caisse d’indemnisation des dommages dus à la pollution par les hydrocarbures causée par les navires [ati-schedule-i-office-of-the-administrator-of-the-ship-source-oil-pollution-fund]; Office of the Chief Electoral Officer / Bureau du directeur général des élections [ati-schedule-i-office-of-the-chief-electoral-officer]; Pacific Economic Development Agency of Canada / Agence de développement économique du Pacifique Canada [ati-schedule-i-pacific-economic-development-agency-of-canada]; Parks Canada Agency / Agence Parcs Canada [ati-schedule-i-parks-canada-agency]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police]; Shared Services Canada / Services partagés Canada [ati-schedule-i-shared-services-canada]; The National Battlefields Commission / Commission des champs de bataille nationaux [ati-schedule-i-the-national-battlefields-commission]; Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-atlantic-canada-opportunities-agency | Atlantic Canada Opportunities Agency | Agence de promotion économique du Canada atlantique |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canada-revenue-agency | Canada Revenue Agency | Agence du revenu du Canada |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-canadian-space-agency | Canadian Space Agency | Agence spatiale canadienne |
| ati-schedule-i-department-of-agriculture-and-agri-food | Department of Agriculture and Agri-Food | Ministère de l’Agriculture et de l’Agroalimentaire |
| ati-schedule-i-department-of-canadian-heritage | Department of Canadian Heritage | Ministère du Patrimoine canadien |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs | Department of Crown-Indigenous Relations and Northern Affairs | Ministère des Relations Couronne-Autochtones et des Affaires du Nord |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-finance | Department of Finance | Ministère des Finances |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-housing-infrastructure-and-communities | Department of Housing, Infrastructure and Communities | Ministère du Logement, de l’Infrastructure et des Collectivités |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-department-of-industry | Department of Industry | Ministère de l’Industrie |
| ati-schedule-i-department-of-justice | Department of Justice | Ministère de la Justice |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-safety-and-emergency-preparedness | Department of Public Safety and Emergency Preparedness | Ministère de la Sécurité publique et de la Protection civile |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-department-of-the-environment | Department of the Environment | Ministère de l’Environnement |
| ati-schedule-i-department-of-veterans-affairs | Department of Veterans Affairs | Ministère des Anciens Combattants |
| ati-schedule-i-department-of-western-economic-diversification | Department of Western Economic Diversification | Ministère de la Diversification de l’économie de l’Ouest canadien |
| ati-schedule-i-economic-development-agency-of-canada-for-the-regions-of-quebec | Economic Development Agency of Canada for the Regions of Quebec | Agence de développement économique du Canada pour les régions du Québec |
| ati-schedule-i-federal-economic-development-agency-for-northern-ontario | Federal Economic Development Agency for Northern Ontario | Agence fédérale de développement économique pour le Nord de l’Ontario |
| ati-schedule-i-national-research-council-of-canada | National Research Council of Canada | Conseil national de recherches du Canada |
| ati-schedule-i-office-of-the-administrator-of-the-fund-for-railway-accidents-involving-designated-goods | Office of the Administrator of the Fund for Railway Accidents Involving Designated Goods | Bureau de l’administrateur de la Caisse d’indemnisation pour les accidents ferroviaires impliquant des marchandises désignées |
| ati-schedule-i-office-of-the-administrator-of-the-ship-source-oil-pollution-fund | Office of the Administrator of the Ship-source Oil Pollution Fund | Bureau de l’administrateur de la Caisse d’indemnisation des dommages dus à la pollution par les hydrocarbures causée par les navires |
| ati-schedule-i-office-of-the-chief-electoral-officer | Office of the Chief Electoral Officer | Bureau du directeur général des élections |
| ati-schedule-i-pacific-economic-development-agency-of-canada | Pacific Economic Development Agency of Canada | Agence de développement économique du Pacifique Canada |
| ati-schedule-i-parks-canada-agency | Parks Canada Agency | Agence Parcs Canada |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |
| ati-schedule-i-shared-services-canada | Shared Services Canada | Services partagés Canada |
| ati-schedule-i-the-national-battlefields-commission | The National Battlefields Commission | Commission des champs de bataille nationaux |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 4. q_tax_customs

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you ever file federal taxes or declare goods at the border? |
| Displayed FR | Avez-vous produit une déclaration de revenus fédérale, payé des droits fédéraux ou fait une déclaration douanière? |
| Source EN before readability rewrite | Have you filed federal taxes, paid federal duties, or made a customs declaration? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Split taxes (CRA) from customs and duties (CBSA); a yes answer otherwise cannot identify the institution. |
| FR help note | Séparer les impôts (ARC) des douanes et droits (ASFC); une réponse affirmative ne permet sinon pas d'identifier l'institution. |

Refinement EN: Which of these have you done? Select all that apply.

Refinement FR: Qu'avez-vous fait parmi les choix suivants? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### federal_tax_return

| Field | Value |
| --- | --- |
| EN answer | Filed a federal income tax return |
| FR answer | Produit une déclaration fédérale de revenus |
| Implied institution EN | Canada Revenue Agency |
| Implied institution FR | Agence du revenu du Canada |
| Coverage label | inventory_gap |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### customs_declaration

| Field | Value |
| --- | --- |
| EN answer | Declared goods or paid duties at the border |
| FR answer | Déclaré des marchandises ou payé des droits à la frontière |
| Implied institution EN | Canada Border Services Agency |
| Implied institution FR | Agence des services frontaliers du Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CBSA PPU 018 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CBSA PPU 018 | Canada Border Services Agency | Traveller Declaration Cards – Personal Information Bank / Carte de déclaration du voyageur – Fichier de renseignements personnels | — |

### other_tax_customs

| Field | Value |
| --- | --- |
| EN answer | Another federal tax or customs interaction |
| FR answer | Une autre interaction fédérale liée aux impôts ou aux douanes |
| Implied institution EN | Canada Revenue Agency or Canada Border Services Agency |
| Implied institution FR | Agence du revenu du Canada ou Agence des services frontaliers du Canada |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 5. q_immigration

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you applied to move to Canada, stay here or become a citizen? |
| Displayed FR | Avez-vous utilisé un processus canadien d’immigration, d’asile, de visa, de résidence permanente ou de citoyenneté? |
| Source EN before readability rewrite | Have you used a Canadian immigration, refugee, visa, permanent-residence or citizenship process? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Ask the process type next because citizenship, visitor, refugee, and permanent-residence records use different banks. |
| FR help note | Demander ensuite le type de processus, car les dossiers de citoyenneté, de visiteur, d'asile et de résidence permanente utilisent des FRP différents. |

Refinement EN: Which immigration or citizenship processes apply? Select all that apply.

Refinement FR: Quelles démarches d'immigration ou de citoyenneté s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### citizenship_permanent_resident

| Field | Value |
| --- | --- |
| EN answer | Canadian citizenship or a permanent resident card |
| FR answer | Citoyenneté canadienne ou carte de résident permanent |
| Implied institution EN | Immigration, Refugees and Citizenship Canada |
| Implied institution FR | Immigration, Réfugiés et Citoyenneté Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | IRCC PPU 050, IRCC PPU 067 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| IRCC PPU 050 | Department of Citizenship and Immigration | Application and Assessment for Canadian Citizenship (PPU 050) / Citoyenneté canadienne : demandes et évaluation (PPU 050) | — |
| IRCC PPU 067 | Department of Citizenship and Immigration | Permanent Resident Card (PPU 067) / Carte de résident permanent (PPU 067) | — |

### visitor_visa_status

| Field | Value |
| --- | --- |
| EN answer | A visitor visa or visitor status |
| FR answer | Visa de visiteur ou statut de visiteur |
| Implied institution EN | Immigration, Refugees and Citizenship Canada |
| Implied institution FR | Immigration, Réfugiés et Citoyenneté Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | IRCC PPU 055 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| IRCC PPU 055 | Department of Citizenship and Immigration | Visitor Case File (PPU 055) / Dossiers de visiteurs (PPU 055) | — |

### other_immigration_process

| Field | Value |
| --- | --- |
| EN answer | Another immigration, refugee or citizenship process |
| FR answer | Une autre démarche d'immigration, de réfugié ou de citoyenneté |
| Implied institution EN | Immigration, Refugees and Citizenship Canada |
| Implied institution FR | Immigration, Réfugiés et Citoyenneté Canada |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency]; Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport]; Immigration and Refugee Board / Commission de l’immigration et du statut de réfugié [ati-schedule-i-immigration-and-refugee-board] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-border-services-agency | Canada Border Services Agency | Agence des services frontaliers du Canada |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-transport | Department of Transport | Ministère des Transports |
| ati-schedule-i-immigration-and-refugee-board | Immigration and Refugee Board | Commission de l’immigration et du statut de réfugié |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 6. q_travel_border

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you applied for a passport, crossed the border or used NEXUS? |
| Displayed FR | Avez-vous demandé un passeport canadien, franchi la frontière canadienne ou adhéré à un programme de voyageurs dignes de confiance? |
| Source EN before readability rewrite | Have you applied for a Canadian passport, crossed Canada’s border, or joined a trusted-traveller program? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | International travel can imply a CBSA interaction, but passport and NEXUS applications should remain separate child routes. |
| FR help note | Un voyage international peut supposer une interaction avec l'ASFC, mais les demandes de passeport et de NEXUS devraient rester des parcours secondaires distincts. |

Refinement EN: Which travel or border interactions apply? Select all that apply.

Refinement FR: Quelles interactions de voyage ou à la frontière s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### passport_application

| Field | Value |
| --- | --- |
| EN answer | Applied for a Canadian passport |
| FR answer | Demandé un passeport canadien |
| Implied institution EN | Immigration, Refugees and Citizenship Canada / Service Canada |
| Implied institution FR | Immigration, Réfugiés et Citoyenneté Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | IRCC PPU 081, ESDC PPU 708 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| IRCC PPU 081 | Department of Citizenship and Immigration | Regular and Official Passports (PPU 081) / Passeports réguliers et officiels (PPU 081) | — |
| ESDC PPU 708 | Department of Employment and Social Development | Passport Program (PIB) / Programme de passeport (FRP) | — |
| ESDC PPU 708 | Canada Employment Insurance Commission | Passport Program (PIB) / Programme de passeport (FRP) | — |

### border_crossing

| Field | Value |
| --- | --- |
| EN answer | Crossed Canada's international border |
| FR answer | Franchi la frontière internationale du Canada |
| Implied institution EN | Canada Border Services Agency |
| Implied institution FR | Agence des services frontaliers du Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CBSA PPU 008, CBSA PPU 010, CBSA PPU 014, CBSA PPU 018 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CBSA PPU 018 | Canada Border Services Agency | Traveller Declaration Cards – Personal Information Bank / Carte de déclaration du voyageur – Fichier de renseignements personnels | — |
| CBSA PPU 008 | Canada Border Services Agency | Advance Passenger Information and Passenger Name Record Programs (API/PNR) – Personal Information Bank / Le programme Information préalable sur les voyageurs et du dossier passager (IPV et DP) – Fichier de renseignements personnels | — |
| CBSA PPU 014 | Canada Border Services Agency | Clients Interviewed by an Officer (DOW) – Personal Information Bank / Clients rencontrés par un agent (DOW) – Fichier de renseignements personnels | — |
| CBSA PPU 010 | Canada Border Services Agency | Travellers Entry Processing System (TEPS) / Travellers National Database System (TRANDS) – Personal Information Bank / Système de traitement des déclarations des voyageurs (STDV)/Système de base de données nationale sur les voyageurs (SBDNV) – Fichier de renseignements personnels | — |

### trusted_traveller

| Field | Value |
| --- | --- |
| EN answer | Applied for or used NEXUS or another trusted-traveller program |
| FR answer | Demandé ou utilisé NEXUS ou un autre programme de voyageurs dignes de confiance |
| Implied institution EN | Canada Border Services Agency |
| Implied institution FR | Agence des services frontaliers du Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CBSA PPU 013, CBSA PPU 031 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CBSA PPU 013 | Canada Border Services Agency | Remote Area Border Crossing (RABC) Permit Program – Personal Information Bank / Programme de Permis de passage de la frontière en région éloignée – Fichier de renseignements personnels | — |
| CBSA PPU 031 | Canada Border Services Agency | NEXUS – Personal Information Bank / NEXUS – Fichier de renseignements personnels | — |

### other_travel_border

| Field | Value |
| --- | --- |
| EN answer | Another federal travel or border interaction |
| FR answer | Une autre interaction fédérale liée au voyage ou à la frontière |
| Implied institution EN | Federal institution involved |
| Implied institution FR | Institution fédérale concernée |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency]; Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Transportation Agency / Office des transports du Canada [ati-schedule-i-canadian-transportation-agency]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport]; Office of the Superintendent of Financial Institutions / Bureau du surintendant des institutions financières [ati-schedule-i-office-of-the-superintendent-of-financial-institutions]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police]; Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-border-services-agency | Canada Border Services Agency | Agence des services frontaliers du Canada |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-transportation-agency | Canadian Transportation Agency | Office des transports du Canada |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-transport | Department of Transport | Ministère des Transports |
| ati-schedule-i-office-of-the-superintendent-of-financial-institutions | Office of the Superintendent of Financial Institutions | Bureau du surintendant des institutions financières |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 7. q_health_disability

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did a federal health program give you care or support? |
| Displayed FR | Avez-vous reçu un service fédéral de santé, de soins dentaires, de réadaptation, d’invalidité ou d’appareil médical? |
| Source EN before readability rewrite | Have you received a federal health, dental, rehabilitation, disability or medical-device service? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Do not infer Health Canada from being a health professional or receiving ordinary provincial care; ask about a named federal program or report. |
| FR help note | Ne pas déduire Santé Canada du seul fait d'être un professionnel de la santé ou de recevoir des soins provinciaux ordinaires; demander plutôt un programme ou un signalement fédéral nommé. |

Refinement EN: Which federal health or disability services apply? Select all that apply.

Refinement FR: Quels services fédéraux de santé ou d'invalidité s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### canadian_dental_care_plan

| Field | Value |
| --- | --- |
| EN answer | The Canadian Dental Care Plan |
| FR answer | Régime canadien de soins dentaires |
| Implied institution EN | Employment and Social Development Canada / Service Canada |
| Implied institution FR | Emploi et Développement social Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ESDC PPU 712 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 712 | Department of Employment and Social Development | Canadian Dental Care Plan (CoR) / Régime canadien de soins dentaires (CDD) | — |
| ESDC PPU 712 | Canada Employment Insurance Commission | Canadian Dental Care Plan (CoR) / Régime canadien de soins dentaires (CDD) | — |

### medical_device_special_access

| Field | Value |
| --- | --- |
| EN answer | Special access to a medical device |
| FR answer | Accès spécial à un instrument médical |
| Implied institution EN | Health Canada |
| Implied institution FR | Santé Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | HC PPU 430 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| HC PPU 430 | Department of Health | Special Access Program - Medical Devices / Programme d'accès spécial - Matériel médical | — |

### other_federal_health_support

| Field | Value |
| --- | --- |
| EN answer | Another named federal health, rehabilitation or disability service |
| FR answer | Un autre service fédéral nommé de santé, de réadaptation ou d'invalidité |
| Implied institution EN | Federal institution that ran the service |
| Implied institution FR | Institution fédérale responsable du service |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Canadian Transportation Agency / Office des transports du Canada [ati-schedule-i-canadian-transportation-agency]; Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport]; Library and Archives of Canada / Bibliothèque et Archives du Canada [ati-schedule-i-library-and-archives-of-canada]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-canadian-transportation-agency | Canadian Transportation Agency | Office des transports du Canada |
| ati-schedule-i-correctional-service-of-canada | Correctional Service of Canada | Service correctionnel du Canada |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-department-of-transport | Department of Transport | Ministère des Transports |
| ati-schedule-i-library-and-archives-of-canada | Library and Archives of Canada | Bibliothèque et Archives du Canada |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 8. q_indigenous_services

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you used a federal service for First Nations, Inuit or Métis people? |
| Displayed FR | Avez-vous utilisé un service fédéral destiné précisément aux membres des Premières Nations, aux Inuit ou aux Métis? |
| Source EN before readability rewrite | Have you used a federal service specifically for First Nations, Inuit or Métis people? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note |  |
| FR help note |  |

Refinement EN: Which federal Indigenous services apply? Select all that apply.

Refinement FR: Quels services fédéraux aux Autochtones s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### first_nations_home_care

| Field | Value |
| --- | --- |
| EN answer | First Nations and Inuit home or community care |
| FR answer | Soins à domicile ou communautaires pour les Premières Nations et les Inuit |
| Implied institution EN | Indigenous Services Canada |
| Implied institution FR | Services aux Autochtones Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ISC PPU 019 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ISC PPU 019 | Department of Indigenous Services | Home and Community Care / Soins à domicile et en milieu communautaire | — |

### indian_status_registration

| Field | Value |
| --- | --- |
| EN answer | Registration under the Indian Act or an Indian status record update |
| FR answer | Inscription en vertu de la Loi sur les Indiens ou mise à jour d'un dossier de statut d'Indien |
| Implied institution EN | Indigenous Services Canada |
| Implied institution FR | Services aux Autochtones Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ISC PPU 110 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ISC PPU 110 | Department of Indigenous Services | Indian Register and Departmentally Administered Band Lists / Registre des Indiens et listes de bandes tenues au ministère | — |

### other_indigenous_service

| Field | Value |
| --- | --- |
| EN answer | Another federal First Nations, Inuit or Métis service |
| FR answer | Un autre service fédéral destiné aux Premières Nations, aux Inuit ou aux Métis |
| Implied institution EN | Federal institution that ran the service |
| Implied institution FR | Institution fédérale responsable du service |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Agriculture and Agri-Food / Ministère de l’Agriculture et de l’Agroalimentaire [ati-schedule-i-department-of-agriculture-and-agri-food]; Department of Crown-Indigenous Relations and Northern Affairs / Ministère des Relations Couronne-Autochtones et des Affaires du Nord [ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Department of Justice / Ministère de la Justice [ati-schedule-i-department-of-justice]; Library and Archives of Canada / Bibliothèque et Archives du Canada [ati-schedule-i-library-and-archives-of-canada] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-department-of-agriculture-and-agri-food | Department of Agriculture and Agri-Food | Ministère de l’Agriculture et de l’Agroalimentaire |
| ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs | Department of Crown-Indigenous Relations and Northern Affairs | Ministère des Relations Couronne-Autochtones et des Affaires du Nord |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-department-of-justice | Department of Justice | Ministère de la Justice |
| ati-schedule-i-library-and-archives-of-canada | Library and Archives of Canada | Bibliothèque et Archives du Canada |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 9. q_military_veterans

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you served in the Armed Forces or received help as a veteran? |
| Displayed FR | Avez-vous servi dans les Forces armées canadiennes ou utilisé un programme fédéral pour les vétérans? |
| Source EN before readability rewrite | Have you served in the Canadian Armed Forces or used a federal veterans program? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Split military service (DND/CAF) from veterans services (VAC); both may be true and usually have different dates. |
| FR help note | Séparer le service militaire (MDN/FAC) des services aux vétérans (ACC); les deux peuvent être vrais et ont habituellement des dates différentes. |

Refinement EN: Which military or veterans situations apply? Select all that apply.

Refinement FR: Quelles situations militaires ou liées aux vétérans s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### caf_service

| Field | Value |
| --- | --- |
| EN answer | Applied to join or served in the Canadian Armed Forces |
| FR answer | Demandé à m'enrôler ou servi dans les Forces armées canadiennes |
| Implied institution EN | Department of National Defence / Canadian Armed Forces and Library and Archives Canada |
| Implied institution FR | Ministère de la Défense nationale / Forces armées canadiennes et Bibliothèque et Archives Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | DND PPU 025, DND PPE 818, LAC PPU 024 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Library and Archives of Canada / Bibliothèque et Archives du Canada [ati-schedule-i-library-and-archives-of-canada] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| DND PPU 025 | Department of National Defence | Enrolment /  | — |
| DND PPE 818 | Department of National Defence | Canadian Forces Member Personal Information File / Fichier des renseignements personnels des membres des Forces canadiennes | — |
| LAC PPU 024 | Library and Archives of Canada | Military Personnel Bank (PIB) / Dossiers du personnel militaire (FRP) | — |

### veterans_program

| Field | Value |
| --- | --- |
| EN answer | Applied for or used a veterans program |
| FR answer | Demandé ou utilisé un programme pour vétérans |
| Implied institution EN | Veterans Affairs Canada, sometimes delivered with Service Canada |
| Implied institution FR | Anciens Combattants Canada, parfois avec Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | VAC PPU 040, VAC PPU 200, VAC PPU 710, VAC PPU 715, ACC PPU 350, ESDC PPU 701 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Veterans Affairs / Ministère des Anciens Combattants [ati-schedule-i-department-of-veterans-affairs] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 701 | Department of Employment and Social Development | Veterans Affairs Canada Program Delivery (PIB) / Exécution des programmes d'Anciens Combattants Canada (FRP) | — |
| VAC PPU 710 | Department of Veterans Affairs | You are here /  | — |
| VAC PPU 715 | Department of Veterans Affairs | You are here /  | — |
| VAC PPU 040 | Department of Veterans Affairs | You are here /  | — |
| VAC PPU 200 | Department of Veterans Affairs | You are here /  | — |
| ACC PPU 350 | Department of Veterans Affairs |  / Vous êtes ici | — |
| ESDC PPU 701 | Canada Employment Insurance Commission | Veterans Affairs Canada Program Delivery (PIB) / Exécution des programmes d'Anciens Combattants Canada (FRP) | — |

### other_military_veterans

| Field | Value |
| --- | --- |
| EN answer | Another military or veterans interaction |
| FR answer | Une autre interaction militaire ou liée aux vétérans |
| Implied institution EN | National Defence or Veterans Affairs Canada |
| Implied institution FR | Défense nationale ou Anciens Combattants Canada |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Veterans Affairs / Ministère des Anciens Combattants [ati-schedule-i-department-of-veterans-affairs]; Library and Archives of Canada / Bibliothèque et Archives du Canada [ati-schedule-i-library-and-archives-of-canada]; Military Grievances External Review Committee / Comité externe d’examen des griefs militaires [ati-schedule-i-military-grievances-external-review-committee]; Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-veterans-affairs | Department of Veterans Affairs | Ministère des Anciens Combattants |
| ati-schedule-i-library-and-archives-of-canada | Library and Archives of Canada | Bibliothèque et Archives du Canada |
| ati-schedule-i-military-grievances-external-review-committee | Military Grievances External Review Committee | Comité externe d’examen des griefs militaires |
| ati-schedule-i-public-service-commission | Public Service Commission | Commission de la fonction publique |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 10. q_education_training

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Has the Government of Canada helped pay for your school or job training? |
| Displayed FR | Avez-vous demandé une aide fédérale aux étudiants, un apprentissage, une bourse ou un programme de formation? |
| Source EN before readability rewrite | Have you applied for federal student aid, an apprenticeship, scholarship or training program? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note |  |
| FR help note |  |

Refinement EN: Which federal education or training support applies? Select all that apply.

Refinement FR: Quel soutien fédéral aux études ou à la formation s'applique? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### canada_student_aid

| Field | Value |
| --- | --- |
| EN answer | A Canada Student Grant or Canada Student Loan |
| FR answer | Bourse canadienne pour étudiants ou prêt d'études canadien |
| Implied institution EN | Employment and Social Development Canada / Service Canada |
| Implied institution FR | Emploi et Développement social Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ESDC PPU 030 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 030 | Department of Employment and Social Development | Canada Student Financial Assistance Program (PIB) / Programme canadien d'aide financière aux étudiants (FRP) | — |
| ESDC PPU 030 | Canada Employment Insurance Commission | Canada Student Financial Assistance Program (PIB) / Programme canadien d'aide financière aux étudiants (FRP) | — |

### canada_apprentice_loan

| Field | Value |
| --- | --- |
| EN answer | A Canada Apprentice Loan |
| FR answer | Prêt canadien aux apprentis |
| Implied institution EN | Employment and Social Development Canada / Service Canada |
| Implied institution FR | Emploi et Développement social Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ESDC PPU 709 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 709 | Department of Employment and Social Development | Canada Apprentice Loans (PIB) / Prêt canadien aux apprentis (FRP) | — |
| ESDC PPU 709 | Canada Employment Insurance Commission | Canada Apprentice Loans (PIB) / Prêt canadien aux apprentis (FRP) | — |

### other_education_training

| Field | Value |
| --- | --- |
| EN answer | Another federal scholarship, training or education program |
| FR answer | Un autre programme fédéral de bourse, de formation ou d'études |
| Implied institution EN | Federal institution that ran the program |
| Implied institution FR | Institution fédérale responsable du programme |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canada Revenue Agency / Agence du revenu du Canada [ati-schedule-i-canada-revenue-agency]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Crown-Indigenous Relations and Northern Affairs / Ministère des Relations Couronne-Autochtones et des Affaires du Nord [ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Department of Industry / Ministère de l’Industrie [ati-schedule-i-department-of-industry]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Safety and Emergency Preparedness / Ministère de la Sécurité publique et de la Protection civile [ati-schedule-i-department-of-public-safety-and-emergency-preparedness]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada]; Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canada-revenue-agency | Canada Revenue Agency | Agence du revenu du Canada |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-correctional-service-of-canada | Correctional Service of Canada | Service correctionnel du Canada |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs | Department of Crown-Indigenous Relations and Northern Affairs | Ministère des Relations Couronne-Autochtones et des Affaires du Nord |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-department-of-industry | Department of Industry | Ministère de l’Industrie |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-safety-and-emergency-preparedness | Department of Public Safety and Emergency Preparedness | Ministère de la Sécurité publique et de la Protection civile |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 11. q_justice_safety

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you have a security check or deal with a federal law officer, prison or parole? |
| Displayed FR | Avez-vous été impliqué dans une affaire relevant de l’application de la loi fédérale, du filtrage de sécurité ou des services correctionnels? |
| Source EN before readability rewrite | Have you been involved in a matter handled by federal law enforcement, security screening or corrections? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Security screening, police matters, and corrections should be separate child routes because they involve different institutions and highly different contexts. |
| FR help note | Le filtrage de sécurité, les affaires policières et les services correctionnels devraient être des parcours secondaires distincts, car ils concernent des institutions et des contextes très différents. |

Refinement EN: What kind of federal public-safety interaction was it? Select all that apply.

Refinement FR: Quel type d'interaction fédérale en matière de sécurité publique était-ce? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### security_screening

| Field | Value |
| --- | --- |
| EN answer | A job, airport, port or government security screening |
| FR answer | Un filtrage de sécurité pour un emploi, un aéroport, un port ou le gouvernement |
| Implied institution EN | The screening institution, such as Transport Canada or a federal employer |
| Implied institution FR | Institution responsable, comme Transports Canada ou un employeur fédéral |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSU 917, DND PPU 834, RCMP PPU 065, TC PPU 093 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 917 | Government of Canada institutions | Personnel Security Screening / Filtrage de sécurité du personnel | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu917) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou917) |
| DND PPU 834 | Department of National Defence | Personnel Security Screening Program /  | — |
| TC PPU 093 | Department of Transport | Transportation Security Clearance Program / Programme d’habilitation de sécurité en matière de transport | — |
| RCMP PPU 065 | Royal Canadian Mounted Police | Security Reliability Screening Records / Dossiers de vérification de sécurité/fiabilité | — |

### police_law_enforcement

| Field | Value |
| --- | --- |
| EN answer | A federal police or law-enforcement matter |
| FR answer | Une affaire de police fédérale ou d'application de la loi |
| Implied institution EN | Royal Canadian Mounted Police or another federal enforcement institution |
| Implied institution FR | Gendarmerie royale du Canada ou autre institution fédérale d'application de la loi |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | RCMP PPU 005, RCMP PPU 010, RCMP PPU 015, RCMP PPU 025, RCMP PPU 030, RCMP PPU 075, RCMP PPU 095, RCMP PPU 139, RCMP PPU 202, RCMP PPU 203 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| RCMP PPU 005 | Royal Canadian Mounted Police | Operational Case Records / Dossiers opérationnels | — |
| RCMP PPU 010 | Royal Canadian Mounted Police | Community Policing Services / Services de police communautaires | — |
| RCMP PPU 015 | Royal Canadian Mounted Police | Criminal Operational Intelligence Records (Exempt bank) / Dossiers opérationnels de renseignements sur la criminalité (fichier inconsultable) | — |
| RCMP PPU 025 | Royal Canadian Mounted Police | National Security Investigations Records (Exempt bank) / Dossiers des enquêtes relatives à la sécurité nationale (fichier inconsultable) | — |
| RCMP PPU 030 | Royal Canadian Mounted Police | Forensic Science and Identification Services and Canadian Criminal Real Time Identification Services / Les Services des sciences judiciaires et de l'identité et le Service canadien d'identification criminelle en temps réels | — |
| RCMP PPU 075 | Royal Canadian Mounted Police | RCMP Police Car Accidents/Claims by or Against the RCMP / Accidents des voitures de police de la GRC demandes de règlements de sinistre déposées par la GRC ou contre celle-ci | — |
| RCMP PPU 095 | Royal Canadian Mounted Police | National Sex Offender Registry / Registre national des délinquants sexuels | — |
| RCMP PPU 139 | Royal Canadian Mounted Police | Victim Services / Services aux victimes | — |
| RCMP PPU 202 | Royal Canadian Mounted Police | National Cybercrime Coordination Centre (NC3) and the Canadian Anti-Fraud Centre (CAFC) / Centre national de coordination en cybercriminalité (CNC3) et Centre antifraude du Canada (CAFC) | — |
| RCMP PPU 203 | Royal Canadian Mounted Police | Forensic Science and Identification Services – Science and Strategic Policy / Services des sciences judiciaires et de l'identité - Travaux scientifiques et politiques stratégiques | — |

### corrections_parole

| Field | Value |
| --- | --- |
| EN answer | A federal corrections, parole or record-suspension matter |
| FR answer | Une affaire fédérale de services correctionnels, de libération conditionnelle ou de suspension du casier |
| Implied institution EN | Correctional Service Canada or Parole Board of Canada |
| Implied institution FR | Service correctionnel Canada ou Commission des libérations conditionnelles du Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CSC PPU 025, CSC PPU 030, CSC PPU 035, CSC PPU 040, CSC PPU 042, CSC PPU 045, CSC PPU 060, CSC PPU 065, CSC PPU 070, CSC PPU 075, CSC PPU 080, CSC PPU 082, CSC PPU 110, CSC PPU 115, CSC PPU 125, CSC PPU 135, PBC PPU 005, PBC PPU 010, PBC PPU 015 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Parole Board of Canada / Commission des libérations conditionnelles du Canada [ati-schedule-i-parole-board-of-canada] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CSC PPU 025 | Correctional Service of Canada | Admission and discharge / Admission et libération | — |
| CSC PPU 042 | Correctional Service of Canada | Case management / Gestion des cas | — |
| CSC PPU 035 | Correctional Service of Canada | Case management: Institution "A" / Gestion des cas : Établissement « A » | — |
| CSC PPU 040 | Correctional Service of Canada | Case management: Institution "B" / Gestion des cas : Établissement « B » | — |
| CSC PPU 030 | Correctional Service of Canada | Case management: Community / Gestion des cas : Collectivité | — |
| CSC PPU 045 | Correctional Service of Canada | Discipline and dissociation / Discipline et isolement | — |
| CSC PPU 125 | Correctional Service of Canada | International transfers / Transfèrements internationaux | — |
| CSC PPU 082 | Correctional Service of Canada | Offender grievances / Griefs des délinquants | — |
| CSC PPU 060 | Correctional Service of Canada | Offender health care / Soins de santé offerts aux délinquants | — |
| CSC PPU 115 | Correctional Service of Canada | Offender information / Renseignements sur les délinquants | — |
| CSC PPU 065 | Correctional Service of Canada | Preventive security and intelligence / Sécurité préventive et renseignement | — |
| CSC PPU 070 | Correctional Service of Canada | Psychology / Psychologie | — |
| CSC PPU 110 | Correctional Service of Canada | Record suspensions / Pardons | — |
| CSC PPU 075 | Correctional Service of Canada | Sentence management / Gestion des peines | — |
| CSC PPU 135 | Correctional Service of Canada | Victims / Victimes | — |
| CSC PPU 080 | Correctional Service of Canada | Visits and correspondence / Visites et correspondance | — |
| PBC PPU 005 | Parole Board of Canada | Conditional Release Decisions (Parole) / Décisions en matière de mise en liberté sous condition (libération conditionnelle) | — |
| PBC PPU 015 | Parole Board of Canada | Conditional Release Openness and Accountability (Victims, Observers and Requests for Access to the Decision Registry) / Application transparente et responsable du processus de mise en liberté sous condition (victimes, observateurs et demandes d’accès au registre des décisions) | — |
| PBC PPU 010 | Parole Board of Canada | Record Suspension Decisions/Clemency Recommendations / Décisions relatives à la suspension du casier et recommandations concernant la clémence | — |

### other_justice_safety

| Field | Value |
| --- | --- |
| EN answer | Another federal law-enforcement or public-safety matter |
| FR answer | Une autre affaire fédérale d'application de la loi ou de sécurité publique |
| Implied institution EN | Federal institution involved |
| Implied institution FR | Institution fédérale concernée |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency]; Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Radio-television and Telecommunications Commission / Conseil de la radiodiffusion et des télécommunications canadiennes [ati-schedule-i-canadian-radio-television-and-telecommunications-commission]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Canadian Transportation Accident Investigation and Safety Board / Bureau canadien d’enquête sur les accidents de transport et de la sécurité des transports [ati-schedule-i-canadian-transportation-accident-investigation-and-safety-board]; Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Industry / Ministère de l’Industrie [ati-schedule-i-department-of-industry]; Department of Justice / Ministère de la Justice [ati-schedule-i-department-of-justice]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Safety and Emergency Preparedness / Ministère de la Sécurité publique et de la Protection civile [ati-schedule-i-department-of-public-safety-and-emergency-preparedness]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Office of the Chief Electoral Officer / Bureau du directeur général des élections [ati-schedule-i-office-of-the-chief-electoral-officer]; Office of the Correctional Investigator of Canada / Bureau de l’enquêteur correctionnel du Canada [ati-schedule-i-office-of-the-correctional-investigator-of-canada]; Office of the Information Commissioner / Commissariat à l’information [ati-schedule-i-office-of-the-information-commissioner]; Office of the Public Sector Integrity Commissioner / Commissariat à l’intégrité du secteur public [ati-schedule-i-office-of-the-public-sector-integrity-commissioner]; Parks Canada Agency / Agence Parcs Canada [ati-schedule-i-parks-canada-agency]; Parole Board of Canada / Commission des libérations conditionnelles du Canada [ati-schedule-i-parole-board-of-canada]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada]; Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-border-services-agency | Canada Border Services Agency | Agence des services frontaliers du Canada |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-radio-television-and-telecommunications-commission | Canadian Radio-television and Telecommunications Commission | Conseil de la radiodiffusion et des télécommunications canadiennes |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-canadian-transportation-accident-investigation-and-safety-board | Canadian Transportation Accident Investigation and Safety Board | Bureau canadien d’enquête sur les accidents de transport et de la sécurité des transports |
| ati-schedule-i-correctional-service-of-canada | Correctional Service of Canada | Service correctionnel du Canada |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-industry | Department of Industry | Ministère de l’Industrie |
| ati-schedule-i-department-of-justice | Department of Justice | Ministère de la Justice |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-safety-and-emergency-preparedness | Department of Public Safety and Emergency Preparedness | Ministère de la Sécurité publique et de la Protection civile |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-office-of-the-chief-electoral-officer | Office of the Chief Electoral Officer | Bureau du directeur général des élections |
| ati-schedule-i-office-of-the-correctional-investigator-of-canada | Office of the Correctional Investigator of Canada | Bureau de l’enquêteur correctionnel du Canada |
| ati-schedule-i-office-of-the-information-commissioner | Office of the Information Commissioner | Commissariat à l’information |
| ati-schedule-i-office-of-the-public-sector-integrity-commissioner | Office of the Public Sector Integrity Commissioner | Commissariat à l’intégrité du secteur public |
| ati-schedule-i-parks-canada-agency | Parks Canada Agency | Agence Parcs Canada |
| ati-schedule-i-parole-board-of-canada | Parole Board of Canada | Commission des libérations conditionnelles du Canada |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |
| ati-schedule-i-public-service-commission | Public Service Commission | Commission de la fonction publique |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 12. q_complaint_appeal

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you file a complaint or ask a federal office to review a choice it made? |
| Displayed FR | Avez-vous présenté une plainte, un grief ou un appel à une institution ou à un tribunal fédéral? |
| Source EN before readability rewrite | Have you made a complaint, grievance or appeal to a federal institution or tribunal? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note |  |
| FR help note |  |

Refinement EN: Which federal complaint or review applies? Select all that apply.

Refinement FR: Quelle plainte ou révision fédérale s'applique? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### air_travel_complaint

| Field | Value |
| --- | --- |
| EN answer | An air-travel complaint |
| FR answer | Plainte concernant le transport aérien |
| Implied institution EN | Canadian Transportation Agency |
| Implied institution FR | Office des transports du Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CTA PPU 014 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canadian Transportation Agency / Office des transports du Canada [ati-schedule-i-canadian-transportation-agency] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CTA PPU 014 | Canadian Transportation Agency | Air Travel Complaints / Plaintes relatives au transport aérien | — |

### cbsa_complaint_review

| Field | Value |
| --- | --- |
| EN answer | A CBSA complaint or request to review a decision |
| FR answer | Plainte à l'ASFC ou demande de révision d'une décision |
| Implied institution EN | Canada Border Services Agency |
| Implied institution FR | Agence des services frontaliers du Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | CBSA PPU 003, CBSA PPU 005 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CBSA PPU 005 | Canada Border Services Agency | Recourse Directorate Records – Personal Information Bank / Documents de la Direction des recours – Fichier de renseignements personnels | — |
| CBSA PPU 003 | Canada Border Services Agency | Complaints – Personal Information Bank / Plaintes – Fichier de renseignements personnels | — |

### rcmp_member_review

| Field | Value |
| --- | --- |
| EN answer | I was an RCMP member whose grievance, conduct, discipline, discharge or demotion matter was referred to the RCMP External Review Committee |
| FR answer | J'étais membre de la GRC et mon grief ou dossier de conduite, de discipline, de renvoi ou de rétrogradation a été renvoyé au Comité externe d'examen de la GRC |
| Implied institution EN | RCMP External Review Committee |
| Implied institution FR | Comité externe d'examen de la GRC |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | True |
| Exact selectors | ERC PPU 801, ERC PPU 802, ERC PPU 803, ERC PPU 804, ERC PPU 805 |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Royal Canadian Mounted Police External Review Committee / Comité externe d’examen de la Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police-external-review-committee] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ERC PPU 804 | Royal Canadian Mounted Police External Review Committee | RCMP Member Appeals of Conduct Decisions/Measures under the *RCMP Act* (s. 45.15) / Appels interjetés par des membres de la GRC contre des décisions ou des mesures disciplinaires en application de la *Loi sur la Gendarmerie royale du Canada* (article 45.15) | — |
| ERC PPU 805 | Royal Canadian Mounted Police External Review Committee | RCMP Member Appeals of Decisions under the *RCMP Regulations* (s.17) / Appels interjetés par des membres de la GRC contre des décisions en application du *Règlement de la Gendarmerie royale du Canada* (article 17) | — |
| ERC PPU 801 | Royal Canadian Mounted Police External Review Committee | RCMP Member Discharge and Demotion Referrals under Part V of the former *RCMP Act / Décisions de licenciement et de rétrogradation de membres de la GRC – renvois en vertu de la partie V de l'ancienne *Loi sur la Gendarmerie royale du Canada | — |
| ERC PPU 803 | Royal Canadian Mounted Police External Review Committee | RCMP Member Discipline Referrals under Part IV of the former *RCMP Act / Décisions relatives aux mesures disciplinaires prises envers les membres de la GRC – renvois en vertu de la partie IV de l'ancienne *Loi sur la Gendarmerie royale du Canada | — |
| ERC PPU 802 | Royal Canadian Mounted Police External Review Committee | RCMP Member Grievance Referrals under Part III of the former *RCMP Act / Griefs des membres de la GRC – renvois en vertu de la partie III de l'ancienne *Loi sur la Gendarmerie royale du Canada | — |

### other_complaint_appeal

| Field | Value |
| --- | --- |
| EN answer | Another federal complaint, grievance or appeal |
| FR answer | Une autre plainte, un autre grief ou un autre appel fédéral |
| Implied institution EN | Federal institution or tribunal involved |
| Implied institution FR | Institution ou tribunal fédéral concerné |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency]; Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Radio-television and Telecommunications Commission / Conseil de la radiodiffusion et des télécommunications canadiennes [ati-schedule-i-canadian-radio-television-and-telecommunications-commission]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Canadian Transportation Agency / Office des transports du Canada [ati-schedule-i-canadian-transportation-agency]; Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Department of Crown-Indigenous Relations and Northern Affairs / Ministère des Relations Couronne-Autochtones et des Affaires du Nord [ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Department of Industry / Ministère de l’Industrie [ati-schedule-i-department-of-industry]; Department of Justice / Ministère de la Justice [ati-schedule-i-department-of-justice]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport]; Immigration and Refugee Board / Commission de l’immigration et du statut de réfugié [ati-schedule-i-immigration-and-refugee-board]; Military Grievances External Review Committee / Comité externe d’examen des griefs militaires [ati-schedule-i-military-grievances-external-review-committee]; Montreal Port Authority / Administration portuaire de Montréal [ati-schedule-i-montreal-port-authority]; Office of the Director of Public Prosecutions / Bureau du directeur des poursuites pénales [ati-schedule-i-office-of-the-director-of-public-prosecutions]; Office of the Information Commissioner / Commissariat à l’information [ati-schedule-i-office-of-the-information-commissioner]; Office of the Public Sector Integrity Commissioner / Commissariat à l’intégrité du secteur public [ati-schedule-i-office-of-the-public-sector-integrity-commissioner]; Parks Canada Agency / Agence Parcs Canada [ati-schedule-i-parks-canada-agency]; Prince Rupert Port Authority / Administration portuaire de Prince-Rupert [ati-schedule-i-prince-rupert-port-authority]; Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police]; Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-border-services-agency | Canada Border Services Agency | Agence des services frontaliers du Canada |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-radio-television-and-telecommunications-commission | Canadian Radio-television and Telecommunications Commission | Conseil de la radiodiffusion et des télécommunications canadiennes |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-canadian-transportation-agency | Canadian Transportation Agency | Office des transports du Canada |
| ati-schedule-i-correctional-service-of-canada | Correctional Service of Canada | Service correctionnel du Canada |
| ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs | Department of Crown-Indigenous Relations and Northern Affairs | Ministère des Relations Couronne-Autochtones et des Affaires du Nord |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-department-of-industry | Department of Industry | Ministère de l’Industrie |
| ati-schedule-i-department-of-justice | Department of Justice | Ministère de la Justice |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-transport | Department of Transport | Ministère des Transports |
| ati-schedule-i-immigration-and-refugee-board | Immigration and Refugee Board | Commission de l’immigration et du statut de réfugié |
| ati-schedule-i-military-grievances-external-review-committee | Military Grievances External Review Committee | Comité externe d’examen des griefs militaires |
| ati-schedule-i-montreal-port-authority | Montreal Port Authority | Administration portuaire de Montréal |
| ati-schedule-i-office-of-the-director-of-public-prosecutions | Office of the Director of Public Prosecutions | Bureau du directeur des poursuites pénales |
| ati-schedule-i-office-of-the-information-commissioner | Office of the Information Commissioner | Commissariat à l’information |
| ati-schedule-i-office-of-the-public-sector-integrity-commissioner | Office of the Public Sector Integrity Commissioner | Commissariat à l’intégrité du secteur public |
| ati-schedule-i-parks-canada-agency | Parks Canada Agency | Agence Parcs Canada |
| ati-schedule-i-prince-rupert-port-authority | Prince Rupert Port Authority | Administration portuaire de Prince-Rupert |
| ati-schedule-i-public-service-commission | Public Service Commission | Commission de la fonction publique |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |
| ati-schedule-i-royal-canadian-mounted-police-external-review-committee | Royal Canadian Mounted Police External Review Committee | Comité externe d’examen de la Gendarmerie royale du Canada |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 13. q_access_privacy

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you asked a federal office for records about you or to fix your records? |
| Displayed FR | Avez-vous présenté une demande d’accès à l’information, d’accès à vos renseignements personnels ou de correction? |
| Source EN before readability rewrite | Have you made an access-to-information, personal-information access, or correction request? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note |  |
| FR help note |  |

Refinement EN: What did you ask a federal office to do? Select all that apply.

Refinement FR: Qu'avez-vous demandé à un bureau fédéral de faire? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### access_information_request

| Field | Value |
| --- | --- |
| EN answer | Give me government records or my personal information |
| FR answer | Me donner des documents gouvernementaux ou mes renseignements personnels |
| Implied institution EN | The federal institution involved, including requests sent through the ATIP Online service |
| Implied institution FR | Institution fédérale concernée, y compris les demandes envoyées par le service AIPRP en ligne |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TBS PCE 805, PSU 901 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 901 | Government of Canada institutions | Access to Information Act and Privacy Act Requests / Demandes en vertu de la Loi sur l’accès à l’information et de la Loi sur la protection des renseignements personnels | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu901) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou901) |
| TBS PCE 805 | Treasury Board Secretariat | Access to information and privacy (ATIP) online requests / Demande d’accès à l’information et de protection des renseignements personnels (AIPRP) en ligne | — |

### personal_information_correction

| Field | Value |
| --- | --- |
| EN answer | Correct personal information in a federal file |
| FR answer | Corriger des renseignements personnels dans un dossier fédéral |
| Implied institution EN | The federal institution that holds the record |
| Implied institution FR | Institution fédérale qui détient le dossier |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSU 901 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 901 | Government of Canada institutions | Access to Information Act and Privacy Act Requests / Demandes en vertu de la Loi sur l’accès à l’information et de la Loi sur la protection des renseignements personnels | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu901) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou901) |

### other_access_privacy

| Field | Value |
| --- | --- |
| EN answer | Another access or privacy request |
| FR answer | Une autre demande d'accès ou de protection des renseignements personnels |
| Implied institution EN | Federal institution involved |
| Implied institution FR | Institution fédérale concernée |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSU 901 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 901 | Government of Canada institutions | Access to Information Act and Privacy Act Requests / Demandes en vertu de la Loi sur l’accès à l’information et de la Loi sur la protection des renseignements personnels | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu901) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou901) |

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-parole-board-of-canada | Parole Board of Canada | Commission des libérations conditionnelles du Canada |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 14. q_business_supplier

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you run a business, get a federal permit or sell goods or services to the government? |
| Displayed FR | Avez-vous possédé ou exploité une entreprise, détenu une licence ou un permis fédéral, ou conclu un marché avec le gouvernement fédéral? |
| Source EN before readability rewrite | Have you owned or operated a business, held a federal licence or permit, or contracted with the federal government? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Use named child routes for contracting, aviation and other regulatory interactions. Firearms and boating are asked separately. |
| FR help note | Utiliser des parcours secondaires nommés pour les marchés, l'aviation et les autres interactions réglementaires. Les armes à feu et la navigation sont demandées séparément. |

Refinement EN: Which business, licence or permit interactions apply? Select all that apply.

Refinement FR: Quelles interactions liées aux entreprises, licences ou permis s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### federal_contract

| Field | Value |
| --- | --- |
| EN answer | Bid on or held a federal government contract |
| FR answer | Soumissionné ou détenu un marché du gouvernement fédéral |
| Implied institution EN | The contracting department and Public Services and Procurement Canada |
| Implied institution FR | Ministère contractant et Services publics et Approvisionnement Canada |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PSU 912 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PSU 912 | Government of Canada institutions | Professional Services Contracts / Marchés de services professionnels | [EN](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu912) / [FR](https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-protection-reseignements-personnels/acces-information/info-source/fichiers-renseignements-personnels-ordinaires.html#pou912) |

### aviation_licence_clearance

| Field | Value |
| --- | --- |
| EN answer | Held a federal aviation licence, medical certificate or airport clearance |
| FR answer | Détenu une licence d'aviation, un certificat médical ou une habilitation aéroportuaire fédérale |
| Implied institution EN | Transport Canada |
| Implied institution FR | Transports Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TC PPU 005, TC PPU 011, TC PPU 020, TC PPU 031, TC PPU 085, TC PPU 093 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| TC PPU 020 | Department of Transport | Medical Assessments / Examens médicaux | — |
| TC PPU 031 | Department of Transport | Civil Aviation Medical Examiners (CAME) / Médecins examinateurs de l’Aviation civile (MEAC) | — |
| TC PPU 011 | Department of Transport | Aircraft Maintenance Engineer Licensing / Délivrance des licences de techniciens d’entretien d’aéronefs | — |
| TC PPU 005 | Department of Transport | Civil Aviation Personnel Licensing / Délivrance des licences du personnel de l’aviation civile | — |
| TC PPU 093 | Department of Transport | Transportation Security Clearance Program / Programme d’habilitation de sécurité en matière de transport | — |
| TC PPU 085 | Department of Transport | Airside Vehicle Operators’ Permits (AVOPs) / Permis d’exploitation de véhicules côté piste | — |

### other_business_regulatory

| Field | Value |
| --- | --- |
| EN answer | Another federal business, licence, inspection or permit interaction |
| FR answer | Une autre interaction fédérale liée à une entreprise, une licence, une inspection ou un permis |
| Implied institution EN | Federal regulator or institution involved |
| Implied institution FR | Organisme de réglementation ou institution fédérale concernée |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Atlantic Canada Opportunities Agency / Agence de promotion économique du Canada atlantique [ati-schedule-i-atlantic-canada-opportunities-agency]; Canada Border Services Agency / Agence des services frontaliers du Canada [ati-schedule-i-canada-border-services-agency]; Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Canadian Food Inspection Agency / Agence canadienne d’inspection des aliments [ati-schedule-i-canadian-food-inspection-agency]; Canadian Grain Commission / Commission canadienne des grains [ati-schedule-i-canadian-grain-commission]; Canadian Radio-television and Telecommunications Commission / Conseil de la radiodiffusion et des télécommunications canadiennes [ati-schedule-i-canadian-radio-television-and-telecommunications-commission]; Department of Agriculture and Agri-Food / Ministère de l’Agriculture et de l’Agroalimentaire [ati-schedule-i-department-of-agriculture-and-agri-food]; Department of Citizenship and Immigration / Ministère de la Citoyenneté et de l’Immigration [ati-schedule-i-department-of-citizenship-and-immigration]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Foreign Affairs, Trade and Development / Ministère des Affaires étrangères, du Commerce et du Développement [ati-schedule-i-department-of-foreign-affairs-trade-and-development]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Industry / Ministère de l’Industrie [ati-schedule-i-department-of-industry]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Department of the Environment / Ministère de l’Environnement [ati-schedule-i-department-of-the-environment]; Department of Transport / Ministère des Transports [ati-schedule-i-department-of-transport]; Montreal Port Authority / Administration portuaire de Montréal [ati-schedule-i-montreal-port-authority]; Office of the Chief Electoral Officer / Bureau du directeur général des élections [ati-schedule-i-office-of-the-chief-electoral-officer]; Parks Canada Agency / Agence Parcs Canada [ati-schedule-i-parks-canada-agency]; Prince Rupert Port Authority / Administration portuaire de Prince-Rupert [ati-schedule-i-prince-rupert-port-authority]; Privy Council Office / Bureau du Conseil privé [ati-schedule-i-privy-council-office]; Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission]; Royal Canadian Mounted Police / Gendarmerie royale du Canada [ati-schedule-i-royal-canadian-mounted-police]; Sept-Îles Port Authority / Administration portuaire de Sept-Îles [ati-schedule-i-sept-iles-port-authority]; St. John’s Port Authority / Administration portuaire de St. John’s [ati-schedule-i-st-john-s-port-authority]; Treasury Board Secretariat / Secrétariat du Conseil du Trésor [ati-schedule-i-treasury-board-secretariat] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-atlantic-canada-opportunities-agency | Atlantic Canada Opportunities Agency | Agence de promotion économique du Canada atlantique |
| ati-schedule-i-canada-border-services-agency | Canada Border Services Agency | Agence des services frontaliers du Canada |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-canadian-food-inspection-agency | Canadian Food Inspection Agency | Agence canadienne d’inspection des aliments |
| ati-schedule-i-canadian-grain-commission | Canadian Grain Commission | Commission canadienne des grains |
| ati-schedule-i-canadian-radio-television-and-telecommunications-commission | Canadian Radio-television and Telecommunications Commission | Conseil de la radiodiffusion et des télécommunications canadiennes |
| ati-schedule-i-department-of-agriculture-and-agri-food | Department of Agriculture and Agri-Food | Ministère de l’Agriculture et de l’Agroalimentaire |
| ati-schedule-i-department-of-citizenship-and-immigration | Department of Citizenship and Immigration | Ministère de la Citoyenneté et de l’Immigration |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-foreign-affairs-trade-and-development | Department of Foreign Affairs, Trade and Development | Ministère des Affaires étrangères, du Commerce et du Développement |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-industry | Department of Industry | Ministère de l’Industrie |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-department-of-the-environment | Department of the Environment | Ministère de l’Environnement |
| ati-schedule-i-department-of-transport | Department of Transport | Ministère des Transports |
| ati-schedule-i-montreal-port-authority | Montreal Port Authority | Administration portuaire de Montréal |
| ati-schedule-i-office-of-the-chief-electoral-officer | Office of the Chief Electoral Officer | Bureau du directeur général des élections |
| ati-schedule-i-parks-canada-agency | Parks Canada Agency | Agence Parcs Canada |
| ati-schedule-i-prince-rupert-port-authority | Prince Rupert Port Authority | Administration portuaire de Prince-Rupert |
| ati-schedule-i-privy-council-office | Privy Council Office | Bureau du Conseil privé |
| ati-schedule-i-public-service-commission | Public Service Commission | Commission de la fonction publique |
| ati-schedule-i-royal-canadian-mounted-police | Royal Canadian Mounted Police | Gendarmerie royale du Canada |
| ati-schedule-i-sept-iles-port-authority | Sept-Îles Port Authority | Administration portuaire de Sept-Îles |
| ati-schedule-i-st-john-s-port-authority | St. John’s Port Authority | Administration portuaire de St. John’s |
| ati-schedule-i-treasury-board-secretariat | Treasury Board Secretariat | Secrétariat du Conseil du Trésor |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 15. q_firearms

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you had a firearms licence or registered a gun? |
| Displayed FR | Avez-vous demandé, renouvelé ou détenu un permis canadien d'armes à feu, ou enregistré une arme à feu à autorisation restreinte? |
| Source EN before readability rewrite | Have you applied for, renewed or held a Canadian firearms licence, or registered a restricted firearm? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | The licence and registration routes can both apply, but their PIB coverage differs. |
| FR help note | Les parcours liés au permis et à l'enregistrement peuvent tous deux s'appliquer, mais leur couverture des FRP diffère. |

Refinement EN: Which firearms-program interactions apply? Select all that apply.

Refinement FR: Quelles interactions avec le programme des armes à feu s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### firearms_licence

| Field | Value |
| --- | --- |
| EN answer | Applied for, renewed or held a firearms licence |
| FR answer | Demandé, renouvelé ou détenu un permis d'armes à feu |
| Implied institution EN | Royal Canadian Mounted Police / Canadian Firearms Program |
| Implied institution FR | Gendarmerie royale du Canada / Programme canadien des armes à feu |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | RCMP PPU 007, RCMP PPU 037, RCMP PPU 100 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| RCMP PPU 007 | Royal Canadian Mounted Police | Inquiries by Firearms Owners, Licence Applicants and the general public / Demandes de renseignements faites par des propriétaires d'armes à feu, des demandeurs de permis et le grand public | — |
| RCMP PPU 037 | Royal Canadian Mounted Police | Canadian Firearms Information System (CFIS) / Système canadien d'information relativement aux armes à feu (SCIRAF) | — |
| RCMP PPU 100 | Royal Canadian Mounted Police | Canadian Firearms Program / Programme canadien des armes à feu | — |

### restricted_firearm_registration

| Field | Value |
| --- | --- |
| EN answer | Registered a restricted or prohibited firearm |
| FR answer | Enregistré une arme à feu à autorisation restreinte ou prohibée |
| Implied institution EN | Royal Canadian Mounted Police / Canadian Firearms Program |
| Implied institution FR | Gendarmerie royale du Canada / Programme canadien des armes à feu |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | RCMP PPU 037, RCMP PPU 100, RCMP PPU 101 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| RCMP PPU 037 | Royal Canadian Mounted Police | Canadian Firearms Information System (CFIS) / Système canadien d'information relativement aux armes à feu (SCIRAF) | — |
| RCMP PPU 100 | Royal Canadian Mounted Police | Canadian Firearms Program / Programme canadien des armes à feu | — |
| RCMP PPU 101 | Royal Canadian Mounted Police | Restricted Weapons Registration System (RWRS) / Système d'enregistrement des armes à autorisation restreinte (SEAAR) | — |

### other_firearms_program

| Field | Value |
| --- | --- |
| EN answer | Another Canadian Firearms Program interaction |
| FR answer | Une autre interaction avec le Programme canadien des armes à feu |
| Implied institution EN | Royal Canadian Mounted Police |
| Implied institution FR | Gendarmerie royale du Canada |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | RCMP PPU 007, RCMP PPU 037, RCMP PPU 100, RCMP PPU 101 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| RCMP PPU 007 | Royal Canadian Mounted Police | Inquiries by Firearms Owners, Licence Applicants and the general public / Demandes de renseignements faites par des propriétaires d'armes à feu, des demandeurs de permis et le grand public | — |
| RCMP PPU 037 | Royal Canadian Mounted Police | Canadian Firearms Information System (CFIS) / Système canadien d'information relativement aux armes à feu (SCIRAF) | — |
| RCMP PPU 100 | Royal Canadian Mounted Police | Canadian Firearms Program / Programme canadien des armes à feu | — |
| RCMP PPU 101 | Royal Canadian Mounted Police | Restricted Weapons Registration System (RWRS) / Système d'enregistrement des armes à autorisation restreinte (SEAAR) | — |

### Broad / Other department list

No primary-topic institution options.

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 16. q_boating

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you had a boating card or registered a boat with Transport Canada? |
| Displayed FR | Avez-vous détenu une carte de conducteur d'embarcation de plaisance, ou obtenu un permis ou une immatriculation pour un bateau auprès de Transports Canada? |
| Source EN before readability rewrite | Have you held a Pleasure Craft Operator Card or licensed or registered a boat with Transport Canada? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Keep operator cards, pleasure-craft licences and vessel registration as separate child routes because the records and retention rules differ. |
| FR help note | Séparer les cartes de conducteur, les permis d'embarcation de plaisance et l'immatriculation des bâtiments, car les dossiers et règles de conservation diffèrent. |

Refinement EN: Which federal boating interactions apply? Select all that apply.

Refinement FR: Quelles interactions fédérales liées à la navigation s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### pleasure_craft_operator_card

| Field | Value |
| --- | --- |
| EN answer | Got a Pleasure Craft Operator Card |
| FR answer | Obtenu une carte de conducteur d'embarcation de plaisance |
| Implied institution EN | Transport Canada |
| Implied institution FR | Transports Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TC PPU 023 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| TC PPU 023 | Department of Transport | National Pleasure Craft Operator Competency Program / Programme national de compétence des conducteurs d’embarcations de plaisance | — |

### pleasure_craft_licence

| Field | Value |
| --- | --- |
| EN answer | Licensed a pleasure craft |
| FR answer | Obtenu un permis d'embarcation de plaisance |
| Implied institution EN | Transport Canada |
| Implied institution FR | Transports Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TC PPU 044 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| TC PPU 044 | Department of Transport | Pleasure Craft Licenses / Permis d’embarcation de plaisance | — |

### vessel_registration

| Field | Value |
| --- | --- |
| EN answer | Registered a vessel with Transport Canada |
| FR answer | Immatriculé un bâtiment auprès de Transports Canada |
| Implied institution EN | Transport Canada |
| Implied institution FR | Transports Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TC PPU 041 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| TC PPU 041 | Department of Transport | Vessel Registration Query System / Système de recherche d'informations sur l'immatriculation des bâtiments | — |

### professional_seafarer

| Field | Value |
| --- | --- |
| EN answer | Got a federal seafarer certificate or identity document |
| FR answer | Obtenu un brevet ou une pièce d'identité fédérale de marin |
| Implied institution EN | Transport Canada |
| Implied institution FR | Transports Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TC PPU 030, TC PPU 040 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| TC PPU 040 | Department of Transport | Canadian Seafarers’ Identity Documents, Discharge Books and Records of Sea Service /  | — |
| TC PPU 030 | Department of Transport | Seafarers’ Certificates and Documents / Certificats de compétence et documents des gens de mer | — |

### other_federal_boating

| Field | Value |
| --- | --- |
| EN answer | Another Transport Canada boating interaction |
| FR answer | Une autre interaction nautique avec Transports Canada |
| Implied institution EN | Transport Canada |
| Implied institution FR | Transports Canada |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | TC PPU 021, TC PPU 023, TC PPU 041, TC PPU 044, TC PPU 048 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| TC PPU 023 | Department of Transport | National Pleasure Craft Operator Competency Program / Programme national de compétence des conducteurs d’embarcations de plaisance | — |
| TC PPU 041 | Department of Transport | Vessel Registration Query System / Système de recherche d'informations sur l'immatriculation des bâtiments | — |
| TC PPU 021 | Department of Transport | Marine Safety Enforcement Program / Programme d’application de la loi de la Sécurité maritime | — |
| TC PPU 048 | Department of Transport | Marine Occurrences and Hazardous Occurrences / Incidents maritimes et événements dangereux | — |
| TC PPU 044 | Department of Transport | Pleasure Craft Licenses / Permis d’embarcation de plaisance | — |

### Broad / Other department list

No primary-topic institution options.

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 17. q_housing_property

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you used a federal program to rent or buy a home? |
| Displayed FR | Avez-vous utilisé un programme fédéral de logement, d’hypothèque, d’achat d’une maison ou de propriété? |
| Source EN before readability rewrite | Have you used a federal housing, mortgage, home-buying or property program? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Ask about named federal programs; buying a home or having a mortgage alone does not establish a direct federal PIB interaction. |
| FR help note | Demander des programmes fédéraux nommés; l'achat d'une maison ou le simple fait d'avoir une hypothèque n'établit pas à lui seul une interaction directe avec un FRP fédéral. |

Refinement EN: Which named federal housing service applies? Select all that apply.

Refinement FR: Quel service fédéral de logement nommé s'applique? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### on_reserve_housing

| Field | Value |
| --- | --- |
| EN answer | The On-Reserve Housing Program or its loan guarantee |
| FR answer | Programme de logement dans les réserves ou sa garantie de prêt |
| Implied institution EN | Indigenous Services Canada |
| Implied institution FR | Services aux Autochtones Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ISC PPU 011 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ISC PPU 011 | Department of Indigenous Services | On-Reserve Housing Program – Ministerial Loan Guarantee / Garanties d'emprunt ministérielles pour le Programme de logement dans les réserves | — |

### canadian_forces_housing

| Field | Value |
| --- | --- |
| EN answer | Canadian Forces housing |
| FR answer | Logements des Forces canadiennes |
| Implied institution EN | Department of National Defence / Canadian Armed Forces |
| Implied institution FR | Ministère de la Défense nationale / Forces armées canadiennes |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | DND PPU 885 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| DND PPU 885 | Department of National Defence | Housing and Accommodations / Logement et lieux d'hébergement | — |

### other_federal_housing

| Field | Value |
| --- | --- |
| EN answer | Another named federal housing or home-buying program |
| FR answer | Un autre programme fédéral nommé de logement ou d'achat d'une habitation |
| Implied institution EN | Federal institution that ran the program |
| Implied institution FR | Institution fédérale responsable du programme |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Department of Housing, Infrastructure and Communities / Ministère du Logement, de l’Infrastructure et des Collectivités [ati-schedule-i-department-of-housing-infrastructure-and-communities]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Prince Rupert Port Authority / Administration portuaire de Prince-Rupert [ati-schedule-i-prince-rupert-port-authority] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-department-of-housing-infrastructure-and-communities | Department of Housing, Infrastructure and Communities | Ministère du Logement, de l’Infrastructure et des Collectivités |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-prince-rupert-port-authority | Prince Rupert Port Authority | Administration portuaire de Prince-Rupert |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 18. q_civic_contact

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you contact a federal office, share your views, sign a petition or vote? |
| Displayed FR | Avez-vous communiqué avec une institution fédérale, participé à une consultation, signé une pétition ou pris part à un processus électoral fédéral? |
| Source EN before readability rewrite | Have you contacted a federal institution, joined a consultation, signed a petition, or participated in a federal election process? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Split voting, petitions, direct correspondence, and consultations; they are not interchangeable and often route to different standard or institution-specific banks. |
| FR help note | Séparer le vote, les pétitions, la correspondance directe et les consultations; ces interactions ne sont pas interchangeables et mènent souvent à différents FRP ordinaires ou propres à une institution. |

Refinement EN: Which civic or public-participation activities apply? Select all that apply.

Refinement FR: Quelles activités civiques ou de participation publique s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### federal_election

| Field | Value |
| --- | --- |
| EN answer | Registered or applied to vote in a federal election |
| FR answer | Inscription ou demande de vote à une élection fédérale |
| Implied institution EN | Elections Canada |
| Implied institution FR | Élections Canada |
| Coverage label | inventory_gap |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### federal_consultation

| Field | Value |
| --- | --- |
| EN answer | Took part in a federal public consultation |
| FR answer | Participation à une consultation publique fédérale |
| Implied institution EN | The department conducting the consultation, such as Health Canada |
| Implied institution FR | Ministère responsable de la consultation, comme Santé Canada |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | HC PPU 051 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| HC PPU 051 | Department of Health | Consultation on Health Protection Legislation / Consultation au sujet de la législation sur la protection de la santé | — |

### other_civic_contact

| Field | Value |
| --- | --- |
| EN answer | Contacted a federal office, signed a petition or took part in another way |
| FR answer | Communication avec un bureau fédéral, signature d'une pétition ou autre participation |
| Implied institution EN | Federal institution involved |
| Implied institution FR | Institution fédérale concernée |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canadian Radio-television and Telecommunications Commission / Conseil de la radiodiffusion et des télécommunications canadiennes [ati-schedule-i-canadian-radio-television-and-telecommunications-commission]; Canadian Security Intelligence Service / Service canadien du renseignement de sécurité [ati-schedule-i-canadian-security-intelligence-service]; Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; Office of the Auditor General of Canada / Bureau du vérificateur général du Canada [ati-schedule-i-office-of-the-auditor-general-of-canada]; Office of the Chief Electoral Officer / Bureau du directeur général des élections [ati-schedule-i-office-of-the-chief-electoral-officer]; Privy Council Office / Bureau du Conseil privé [ati-schedule-i-privy-council-office]; Public Service Commission / Commission de la fonction publique [ati-schedule-i-public-service-commission] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canadian-radio-television-and-telecommunications-commission | Canadian Radio-television and Telecommunications Commission | Conseil de la radiodiffusion et des télécommunications canadiennes |
| ati-schedule-i-canadian-security-intelligence-service | Canadian Security Intelligence Service | Service canadien du renseignement de sécurité |
| ati-schedule-i-correctional-service-of-canada | Correctional Service of Canada | Service correctionnel du Canada |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-office-of-the-auditor-general-of-canada | Office of the Auditor General of Canada | Bureau du vérificateur général du Canada |
| ati-schedule-i-office-of-the-chief-electoral-officer | Office of the Chief Electoral Officer | Bureau du directeur général des élections |
| ati-schedule-i-privy-council-office | Privy Council Office | Bureau du Conseil privé |
| ati-schedule-i-public-service-commission | Public Service Commission | Commission de la fonction publique |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 19. q_culture_volunteer

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you registered for a federal public event, or joined a federal arts, sports, heritage, parks or volunteer activity? |
| Displayed FR | Vous êtes-vous inscrit ou avez-vous assisté à un événement public fédéral, ou participé à une activité fédérale de culture, de sport, de loisir, de patrimoine, de parc ou de bénévolat? |
| Source EN before readability rewrite | Have you registered for or attended a federal public event, or participated in a federal cultural, sport, recreation, heritage, park or volunteer activity? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Prefer named events or programs that required registration. Simply visiting a park or museum does not necessarily create an identifiable personal record. |
| FR help note | Privilégier les événements ou programmes nommés qui exigeaient une inscription. La simple visite d'un parc ou d'un musée ne crée pas nécessairement un dossier personnel identifiable. |

Refinement EN: Which federal public events, culture, recreation or volunteer activities apply? Select all that apply.

Refinement FR: Quels événements publics ou quelles activités fédérales de culture, de loisirs ou de bénévolat s'appliquent? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### space_launch_attendance

| Field | Value |
| --- | --- |
| EN answer | Registered to attend a Canadian Space Agency mission launch |
| FR answer | Inscription pour assister au lancement d'une mission de l'Agence spatiale canadienne |
| Implied institution EN | Canadian Space Agency |
| Implied institution FR | Agence spatiale canadienne |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | True |
| Exact selectors | CSA PPU 020 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| CSA PPU 020 | Canadian Space Agency | Registration to Attend Space Missions Launches /  | — |

### canada_day_challenge

| Field | Value |
| --- | --- |
| EN answer | Entered the Canada Day Challenge |
| FR answer | Participation au Défi de la fête du Canada |
| Implied institution EN | Canadian Heritage |
| Implied institution FR | Patrimoine canadien |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PCH PPU 027 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PCH PPU 027 | Department of Canadian Heritage | Canada Day Challenge / Défi de la fête du Canada | — |

### federal_volunteer_program

| Field | Value |
| --- | --- |
| EN answer | Registered with a federally run volunteer program |
| FR answer | Inscription à un programme de bénévolat fédéral |
| Implied institution EN | Canadian Heritage or the federal institution running the program |
| Implied institution FR | Patrimoine canadien ou institution fédérale responsable du programme |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PCH PPU 070 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Canadian Heritage / Ministère du Patrimoine canadien [ati-schedule-i-department-of-canadian-heritage] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PCH PPU 070 | Department of Canadian Heritage | Volunteer Centre / Centre des bénévoles | — |

### other_culture_recreation

| Field | Value |
| --- | --- |
| EN answer | Another named federal arts, sport, heritage or parks activity |
| FR answer | Une autre activité fédérale nommée liée aux arts, aux sports, au patrimoine ou aux parcs |
| Implied institution EN | Federal institution that ran the activity |
| Implied institution FR | Institution fédérale responsable de l'activité |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Employment Insurance Commission / Commission de l’assurance-emploi du Canada [ati-schedule-i-canada-employment-insurance-commission]; Correctional Service of Canada / Service correctionnel du Canada [ati-schedule-i-correctional-service-of-canada]; Department of Canadian Heritage / Ministère du Patrimoine canadien [ati-schedule-i-department-of-canadian-heritage]; Department of Employment and Social Development / Ministère de l’Emploi et du Développement social [ati-schedule-i-department-of-employment-and-social-development]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Indigenous Services / Ministère des Services aux Autochtones [ati-schedule-i-department-of-indigenous-services]; Parks Canada Agency / Agence Parcs Canada [ati-schedule-i-parks-canada-agency] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-employment-insurance-commission | Canada Employment Insurance Commission | Commission de l’assurance-emploi du Canada |
| ati-schedule-i-correctional-service-of-canada | Correctional Service of Canada | Service correctionnel du Canada |
| ati-schedule-i-department-of-canadian-heritage | Department of Canadian Heritage | Ministère du Patrimoine canadien |
| ati-schedule-i-department-of-employment-and-social-development | Department of Employment and Social Development | Ministère de l’Emploi et du Développement social |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-indigenous-services | Department of Indigenous Services | Ministère des Services aux Autochtones |
| ati-schedule-i-parks-canada-agency | Parks Canada Agency | Agence Parcs Canada |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 20. q_research_survey

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Have you taken part in federal research, a survey, testing or a focus group? |
| Displayed FR | Avez-vous participé à une recherche, un sondage, un test ou un groupe de discussion du gouvernement fédéral? |
| Source EN before readability rewrite | Have you taken part in federal research, a survey, testing or a focus group? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Separate survey respondent or study participant from researcher or peer reviewer; the bank and information collected differ. |
| FR help note | Séparer le répondant à un sondage ou le participant à une étude du chercheur ou de l'évaluateur par les pairs; le FRP et les renseignements recueillis diffèrent. |

Refinement EN: What was your role in federal research? Select all that apply.

Refinement FR: Quel était votre rôle dans la recherche fédérale? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### research_participant

| Field | Value |
| --- | --- |
| EN answer | I answered a survey, joined a study or took part in testing |
| FR answer | J'ai répondu à un sondage, participé à une étude ou pris part à des essais |
| Implied institution EN | The institution conducting the research, such as Health Canada |
| Implied institution FR | Institution responsable de la recherche, comme Santé Canada |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | HC PPU 035, HC PPU 314 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| HC PPU 314 | Department of Health | Research into the Health Effects of Air Pollution / Étude des effets de la pollution atmosphérique sur la santé | — |
| HC PPU 035 | Department of Health | Pesticide Exposure Assessment Pilot Study / Étude pilote sur l'évaluation de l'exposition aux pesticides | — |

### researcher_reviewer

| Field | Value |
| --- | --- |
| EN answer | I led, reviewed or supported a federal research project |
| FR answer | J'ai dirigé, évalué ou soutenu un projet de recherche fédéral |
| Implied institution EN | The research institution, such as the Public Health Agency of Canada |
| Implied institution FR | Institution de recherche, comme l'Agence de la santé publique du Canada |
| Coverage label | partial |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | PHAC PPU 290 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| PHAC PPU 290 | Public Health Agency of Canada | Research Projects / Projets de recherche | — |

### other_research_survey

| Field | Value |
| --- | --- |
| EN answer | Another federal research, survey or focus-group activity |
| FR answer | Une autre activité fédérale de recherche, de sondage ou de groupe de discussion |
| Implied institution EN | Federal institution that ran the activity |
| Implied institution FR | Institution fédérale responsable de l'activité |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Department of Health / Ministère de la Santé [ati-schedule-i-department-of-health]; Department of National Defence / Ministère de la Défense nationale [ati-schedule-i-department-of-national-defence]; Department of Public Works and Government Services / Ministère des Travaux publics et des Services gouvernementaux [ati-schedule-i-department-of-public-works-and-government-services]; National Film Board / Office national du film [ati-schedule-i-national-film-board] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-department-of-health | Department of Health | Ministère de la Santé |
| ati-schedule-i-department-of-national-defence | Department of National Defence | Ministère de la Défense nationale |
| ati-schedule-i-department-of-public-works-and-government-services | Department of Public Works and Government Services | Ministère des Travaux publics et des Services gouvernementaux |
| ati-schedule-i-national-film-board | National Film Board | Office national du film |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 21. q_emergency

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you ask for federal help in a crisis or after a disaster? |
| Displayed FR | Avez-vous demandé ou reçu de l’aide fédérale lors d’une urgence, d’une évacuation ou d’une catastrophe? |
| Source EN before readability rewrite | Have you requested or received federal help during an emergency, evacuation or disaster? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Ask which federal service responded; many emergency services are provincial, territorial, municipal, or delivered through another organization. |
| FR help note | Demander quel service fédéral est intervenu; de nombreux services d'urgence sont provinciaux, territoriaux, municipaux ou fournis par un autre organisme. |

Refinement EN: Which federal emergency service helped you? Select all that apply.

Refinement FR: Quel service d'urgence fédéral vous a aidé? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### search_and_rescue

| Field | Value |
| --- | --- |
| EN answer | A Canadian Armed Forces search-and-rescue response |
| FR answer | Intervention de recherche et sauvetage des Forces armées canadiennes |
| Implied institution EN | Department of National Defence / Canadian Armed Forces |
| Implied institution FR | Ministère de la Défense nationale / Forces armées canadiennes |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | DND PPU 050 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| DND PPU 050 | Department of National Defence | Search and Rescue / Recherche et sauvetage | — |

### fishery_ice_assistance

| Field | Value |
| --- | --- |
| EN answer | Temporary fishery help after severe ice conditions |
| FR answer | Aide temporaire aux pêches après de graves conditions de glace |
| Implied institution EN | Fisheries and Oceans Canada |
| Implied institution FR | Pêches et Océans Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | DFO PPU 045 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans] |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| DFO PPU 045 | Department of Fisheries and Oceans | Ice Assistance Emergency Program / Programme d’urgence d’aide liée aux conditions des glaces | — |

### other_federal_emergency

| Field | Value |
| --- | --- |
| EN answer | Another named federal emergency or disaster service |
| FR answer | Un autre service fédéral nommé d'urgence ou de catastrophe |
| Implied institution EN | Federal institution that provided the service |
| Implied institution FR | Institution fédérale qui a fourni le service |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | True |
| Department options EN / FR | Canada Revenue Agency / Agence du revenu du Canada [ati-schedule-i-canada-revenue-agency]; Department of Agriculture and Agri-Food / Ministère de l’Agriculture et de l’Agroalimentaire [ati-schedule-i-department-of-agriculture-and-agri-food]; Department of Fisheries and Oceans / Ministère des Pêches et des Océans [ati-schedule-i-department-of-fisheries-and-oceans]; Department of Public Safety and Emergency Preparedness / Ministère de la Sécurité publique et de la Protection civile [ati-schedule-i-department-of-public-safety-and-emergency-preparedness]; Public Health Agency of Canada / Agence de la santé publique du Canada [ati-schedule-i-public-health-agency-of-canada] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-canada-revenue-agency | Canada Revenue Agency | Agence du revenu du Canada |
| ati-schedule-i-department-of-agriculture-and-agri-food | Department of Agriculture and Agri-Food | Ministère de l’Agriculture et de l’Agroalimentaire |
| ati-schedule-i-department-of-fisheries-and-oceans | Department of Fisheries and Oceans | Ministère des Pêches et des Océans |
| ati-schedule-i-department-of-public-safety-and-emergency-preparedness | Department of Public Safety and Emergency Preparedness | Ministère de la Sécurité publique et de la Protection civile |
| ati-schedule-i-public-health-agency-of-canada | Public Health Agency of Canada | Agence de la santé publique du Canada |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## 22. q_family_vital

| Field | Exact text / values |
| --- | --- |
| Displayed EN | Did you use a federal service for a birth, wedding, divorce, adoption or death? |
| Displayed FR | Avez-vous utilisé un service fédéral concernant une naissance, un mariage, un divorce, une adoption, une pension alimentaire, un décès ou une succession? |
| Source EN before readability rewrite | Have you used a federal service involving a birth, marriage, divorce, adoption, child support, death or estate? |
| Answers | yes, no, not_sure, prefer_not_to_answer |
| EN timing (non-route) | About what year did this interaction last happen? |
| FR timing (non-route) | Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois? |
| EN help note | Replace the broad life-event wording with named federal services. Birth, marriage, and death registration are ordinarily provincial or territorial activities. |
| FR help note | Remplacer le libellé général sur les événements de la vie par des services fédéraux nommés. L'enregistrement des naissances, mariages et décès relève habituellement des provinces ou des territoires. |

Refinement EN: Which named federal life-event service applies? Select all that apply.

Refinement FR: Quel service fédéral nommé lié à un événement de vie s'applique? Sélectionnez toutes les réponses pertinentes.

Select one or more activity options. Each selected option asks its own timing unless noted below. Route timing EN: About when did this last happen: {selected English label}? FR: Vers quand cela s'est-il produit pour la dernière fois : {selected French label}?

### cpp_survivor_death_benefit

| Field | Value |
| --- | --- |
| EN answer | A Canada Pension Plan survivor or death benefit |
| FR answer | Prestation de survivant ou de décès du Régime de pensions du Canada |
| Implied institution EN | Employment and Social Development Canada / Service Canada |
| Implied institution FR | Emploi et Développement social Canada / Service Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ESDC PPU 146 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ESDC PPU 146 | Department of Employment and Social Development | Canada Pension Plan Program (PIB) / Régime de pensions du Canada (FRP) | — |
| ESDC PPU 146 | Canada Employment Insurance Commission | Canada Pension Plan Program (PIB) / Régime de pensions du Canada (FRP) | — |

### first_nations_estate

| Field | Value |
| --- | --- |
| EN answer | Administration of a First Nations estate |
| FR answer | Administration d'une succession des Premières Nations |
| Implied institution EN | Indigenous Services Canada |
| Implied institution FR | Services aux Autochtones Canada |
| Coverage label | direct |
| Ask timing | True |
| Re-enable broad parent matches | False |
| Exclusive selector required | False |
| Exact selectors | ISC PPU 105 |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | None |

| PIB selector | Inventory holder | PIB title EN / FR | Source |
| --- | --- | --- | --- |
| ISC PPU 105 | Department of Indigenous Services | First Nations Estates / Successions des Premières Nations | — |

### other_federal_life_event

| Field | Value |
| --- | --- |
| EN answer | Another named federal birth, marriage, divorce, adoption or death service |
| FR answer | Un autre service fédéral nommé lié à une naissance, un mariage, un divorce, une adoption ou un décès |
| Implied institution EN | Federal institution that ran the service |
| Implied institution FR | Institution fédérale responsable du service |
| Coverage label | fallback |
| Ask timing | True |
| Re-enable broad parent matches | True |
| Exclusive selector required | False |
| Exact selectors | None |
| Missing selector bank keys | None |
| Ask department if selected alone | False |
| Department options EN / FR | Department of Justice / Ministère de la Justice [ati-schedule-i-department-of-justice] |

No exact-selector inventory rows. A fallback can still match the parent topic; an inventory gap cannot invent a matching PIB.

### Broad / Other department list

| Institution ID | EN | FR |
| --- | --- | --- |
| ati-schedule-i-department-of-justice | Department of Justice | Ministère de la Justice |

All broad primary/candidate PIB associations for this gate are in pib_mapping.csv. Candidate associations alone do not produce ordinary web results; exclusive-route guards still apply.

## Provenance and regeneration

Run .venv/bin/python scripts/export_my_info_v1_review.py from the repository root. Review source evidence before treating any selector or keyword match as validated. Exact input hashes follow so this document's snapshot can be compared with future runtime changes.

| Input | SHA-256 |
| --- | --- |
| data/derived/my_info/my_info_questionnaire.json | 63558f1d81d9e35b4d995cac1c389af7eed5596ac3b05b3572fe46701c666b95 |
| data/derived/my_info/my_info_pib_features.csv | 42c9534cd279a62d8289eed6d41517d77149063f7220dfd0a0f1a117ca2007a2 |
| my_info/agent_tools.py | 9b446f0cb306a5300d36883895bf0d3ddd31d2f2ec780a718b767dab3ac8c3f9 |
| my_info/web/app.mjs | b5d04ab52c7e7be3d0594fd74a6c36eca546fa8359b9093bf9c0a834a06ce926 |
| packages/my-info-mcp/src/engine.mjs | 41b60dfc48e22ed83d43d1d7d0a9af88f747b0aec652013b480713ff1bf8bbcc |
