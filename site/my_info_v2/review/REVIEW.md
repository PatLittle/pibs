# My Info V2 — reviewable survey specification

This is an isolated comparison prototype. V1 and the published site remain unchanged on their existing paths.

## Product promise and flow

Find which federal organizations may have records about you, what those records describe, and where to ask. Start with activities you recognize; dates are optional.

1. Choose recognized activities in eight expandable groups, use the optional common-four shortcut, or search by program/institution. Selecting a group only navigates; it never matches a PIB.
2. A named program infers its source-supported organization. A generic request, contract or workplace interaction asks for the organization; 'not sure' is supported and never means all organizations.
3. Show a short list of relevant published descriptions immediately. Distinguish selected activities, records personally reviewed in the directory, uncertain activities, and source gaps.
4. Optionally refine retention using only reviewed source rules. Ask when the rule's event happened (release, launch, closure, last action), with 'not happened' and 'not sure'. Do not substitute an application date.
5. Offer the full program directory and source links for specialist or indirect records. The person must review the eligible population before adding a directory record.

## Coverage and burden

There are 56 activity statements in 8 expandable groups, not 56 mandatory questions. Search/group navigation reduces the visible list; this still needs user testing for scanning effort.

The reviewed guided routes reach 53 of 1040 inventory rows (5.1%). The directory exposes all 1040 rows; 987 need program/role review there. **Directory access is not 100% automatic matching coverage.** V1's 597 direct-labelled rows include broad classifier/selector matches that have not had the same source review.

There are 972 distinct bank-number keys: publishing the same key under multiple institutions explains part of the 1040-row total. V2 selectors use full institution-scoped record IDs.

Info Source mandate/program context was extracted for 67 institutions in English and 64 in French. Missing context is explicit; extracted text assists navigation and never supplies a personal match.

Only 6 source-checked single-event retention rules are executable in this prototype. Other published rules remain visible and uncertain. This intentionally exposes the remaining curation work.

## Decision rules and edge cases

- Every guided result requires an explicit activity/role selection and an exact reviewed record ID. Personal-information attributes such as passport number or health information cannot nominate a service.
- Unknown veteran benefit identifies Veterans Affairs and asks for program detail in the result guidance; it cannot imply Agent Orange, education or income-replacement eligibility.
- CAF application and Regular Force service are different activities. DND is inferred; a published transfer to Library and Archives Canada is explained as custody, never a redundant department question.
- A common-four selection assigns a ten-year interval only to the selected activity occurrence. It never hides NEXUS, consular help, customs, consultations, or older events. Unchecked items are unreported, not lifetime negatives.
- Voting is linked to ELECTIONS PPU 037 (registration/identification, not ballot choice). Tax filing still has no reviewed direct route in this collected inventory.
- Generic complaints do not select every complaint bank. Ask the institution and then the complaint program. ERC 802 requires both RCMP membership and the specified referral under the former Act.
- Standard PIBs describe reusable classes. Their potential owner is the institution the person selects; they never establish that every government organization has a copy.
- Province-funded or federally funded services do not automatically imply a federal personal record. The program's actual population and collection purpose must support it.
- Indirect records can be found through an explicit role (e.g. passport reference) or source review in the directory. Absence from guided results cannot establish absence from federal holdings.
- No mandatory dates. Multi-branch/age/death/unspecified retention starts remain uncertain. Approximate years use a one-year margin; a boundary overlap stays uncertain. 'Period elapsed' is not evidence that destruction actually occurred.
- A timing answer applies to the selected program and event only; it is not reused across unrelated episodes. Results concern the latest reported episode; older files can follow other timelines.
- The bilingual prototype uses the same rule IDs. It requires fluent French review and public usability testing before a production release.

## Reviewer checklist

For every activity below, check vocabulary, eligible role, institution, exact PIB IDs, exclusions, source excerpt and retention event. The generated routing_ledger.csv and coverage.csv support spreadsheet review. Record proposed changes by activity ID or record ID.

## Activity routing ledger

### tax_return

EN: Filed a federal income tax return

FR: Produit une déclaration fédérale de revenus

Institution: Canada Revenue Agency. Scope: inferred. Coverage: source_gap.

CRA is the place to start. This collected inventory does not yet support a reviewed personal tax-return match.

### federal_vote

EN: Registered or voted in a federal election

FR: Inscription ou vote à une élection fédérale

Institution: Office of the Chief Electoral Officer. Scope: inferred. Coverage: reviewed.

Registration and identification records; this does not describe how you voted.

- `institution:ati-schedule-i-office-of-the-chief-electoral-officer:ELECTIONS PPU 037` — Voter Registration and Identification (PIB)
  - Population: Canadian citizens 18 years of age and older who are registered as electors, and valid electors who have attested to the residency of another elector; individuals whose information has been removed from the National Register of Electors either due to their being ineligible or deceased, or at their request or that of their authorized representative.
  - Purpose: Voter registration and identification information is collected so that eligible voters are included on preliminary, revised and official lists of electors and are able to cast a ballot in a federal election or referendum, in accordance with Parts 7, 9 and 10 of the Canada Elections Act and section 7 of the Referendum Act. Personal information is also collected to update and maintain the National Register of Electors, pursuant to Part 4 of the Canada Elections Act.
  - Source: https://www.elections.ca:443/content.aspx?section=abo&dir=atip/info&document=p7&lang=e

### passport

EN: Applied for or renewed a Canadian passport

FR: Demandé ou renouvelé un passeport canadien

Institution: Immigration, Refugees and Citizenship Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-citizenship-and-immigration:IRCC PPU 081` — Regular and Official Passports (PPU 081)
  - Population: The information described in this bank relates to Canadian citizens and in exceptional cases to non-Canadians who have applied for passports. The program also holds information about individuals who act as guarantors, emergency contacts, personal references, individuals who submit an application on behalf of an applicant (e.g., family members, parents, tutors or guardians), the person(s) authorized to apply for a passport for a child, representatives (e.g. power of attorney, legal representative for incapable individuals, or a third party that acts on behalf of a guarantor), and passport photo service providers.
  - Purpose: The personal information described in this bank is used to determine an applicant’s current and ongoing entitlement to a Canadian passport and to administer passport services. Personal information is collected pursuant to the *Canadian Passport Order* (SI 81-86), as amended and the *Diplomatic and Special Passports Order.
  - Source: https://www.canada.ca/en/immigration-refugees-citizenship/corporate/transparency/access-information-privacy/info-source/personal-information-banks.html

### passport_service_canada

EN: Used Service Canada to apply for a passport

FR: Demandé un passeport par l'intermédiaire de Service Canada

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.

Select this too if Service Canada received your passport application.

- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 708` — Passport Program (PIB)
  - Population: Canadian citizens applying for passports; individuals who are guarantors or personal references; emergency contacts; parents, guardians, or the person who is authorized to apply for a passport for a child, representatives (for example, holders of a power of attorney, legal representative for individuals requiring assistance, or a third party that acts on behalf of a guarantor); and photographers.
  - Purpose: Personal information is used to determine an applicant's entitlement to a Canadian passport and to administer passport services. Personal information is collected pursuant to the *Canadian Passport Order* (SI 81-86) and the *Department of Employment and Social Development Act*, as amended from time to time.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### passport_reference

EN: Was named as a passport guarantor, reference or emergency contact

FR: Nommé comme répondant, référence ou personne à contacter en cas d'urgence pour un passeport

Institution: Immigration, Refugees and Citizenship Canada. Scope: inferred. Coverage: reviewed.

An example of information supplied by somebody else.

- `institution:ati-schedule-i-department-of-citizenship-and-immigration:IRCC PPU 081` — Regular and Official Passports (PPU 081)
  - Population: The information described in this bank relates to Canadian citizens and in exceptional cases to non-Canadians who have applied for passports. The program also holds information about individuals who act as guarantors, emergency contacts, personal references, individuals who submit an application on behalf of an applicant (e.g., family members, parents, tutors or guardians), the person(s) authorized to apply for a passport for a child, representatives (e.g. power of attorney, legal representative for incapable individuals, or a third party that acts on behalf of a guarantor), and passport photo service providers.
  - Purpose: The personal information described in this bank is used to determine an applicant’s current and ongoing entitlement to a Canadian passport and to administer passport services. Personal information is collected pursuant to the *Canadian Passport Order* (SI 81-86), as amended and the *Diplomatic and Special Passports Order.
  - Source: https://www.canada.ca/en/immigration-refugees-citizenship/corporate/transparency/access-information-privacy/info-source/personal-information-banks.html

### border_crossing

EN: Entered Canada and made a traveller declaration

FR: Entré au Canada et fait une déclaration de voyageur

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.

A crossing alone does not imply a NEXUS, penalty, officer interview or customs-payment record.

- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 018` — Traveller Declaration Cards – Personal Information Bank
  - Population: All persons entering Canada, including but not limited to, Canadian citizens, permanent residents, visitors, crew members, diplomats, military personnel, refugees, immigrants, former residents.
  - Purpose: The personal information is collected pursuant to the Customs Act, Customs Tariff, Immigration and Refugee and Protection Act (IRPA), Proceeds of Crime (Money Laundering) and Terrorist Financing Act (PCMLTFA) and Subsection 5(3) of the Reporting of Imported Goods Regulations for the purposes of facilitating compliance with travellers' obligations to report their goods in writing upon entry into Canada including the collection of duty and taxes owing on those goods imported into Canada and to administer laws that enforce, prohibit, control and regulate the importation of goods into Canada and the movement of people coming into Canada.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### commercial_arrival

EN: Travelled to Canada on a commercial flight or other commercial carrier

FR: Voyagé vers le Canada à bord d'un transporteur commercial

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 008` — Advance Passenger Information and Passenger Name Record Programs (API/PNR) – Personal Information Bank
  - Population: General Public – including employees of the commercial transporters – who are travelling on a commercial conveyance destined for Canada.
  - Purpose: The personal information is collected pursuant to section 107.1 of the Customs Act, the Passenger Information (Customs) Regulations (PICR), paragraph 148(1)(d) of the Immigration and Refugee Protection Act (IRPA) and Regulation 269 of the Immigration and Refugee Protection Regulations (IRPR) for the purposes of administering the API and PNR Programs, which involves performing a risk assessment, including a scenario based risk analysis and query for enforcement and intelligence information on individuals prior to their arrival in Canada. API personal information is also used for an Interactive Advance Passenger Information (IAPI) process. This process allows the CBSA to systematically identify travellers who may not meet the documentary requirements to enter Canada and communicate a board/no board message back to the air carriers who may, in turn, prevent the traveller from boarding. The Protection of Passenger Information Regulations govern the processing of PNR data, including access, usage, retention and disclosure.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### nexus

EN: Applied for or renewed NEXUS membership

FR: Demandé ou renouvelé une adhésion NEXUS

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 031` — NEXUS – Personal Information Bank
  - Population: NEXUS Program applicants.
  - Purpose: To determine if an applicant can be approved to participate in an expedited border clearance program. Personal information is collected pursuant to Subsection 11.1(1) of the Customs Act and section 6.1 of the Presentation of Persons (2003) Regulations.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### remote_border_permit

EN: Applied for a Remote Area Border Crossing permit

FR: Demandé un permis de passage à la frontière dans une région éloignée

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 013` — Remote Area Border Crossing (RABC) Permit Program – Personal Information Bank
  - Population: General Public.
  - Purpose: The personal information is used to respond to requests for remote area border crossing permits and will be used to determine his/her eligibility. Personal information is collected pursuant to Sections 107(1), 11(6) and 11.1 of the Customs Act.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### customs_payment

EN: Had duties or taxes assessed on goods brought into Canada

FR: Fait évaluer des droits ou taxes sur des biens apportés au Canada

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 010` — Travellers Entry Processing System (TEPS) / Travellers National Database System (TRANDS) – Personal Information Bank
  - Population: Members of the general public.
  - Purpose: TEPS - Assists the Border Service Officers in the assessment and collection of duties, taxes and other relevant data on travellers' importations. TRANDS - Provides B15 data for Agency queries.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### citizenship

EN: Applied for citizenship or a citizenship certificate

FR: Demandé la citoyenneté ou un certificat de citoyenneté

Institution: Immigration, Refugees and Citizenship Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-citizenship-and-immigration:IRCC PPU 050` — Application and Assessment for Canadian Citizenship (PPU 050)
  - Population: Information described in this bank relates to: individuals who have applied for Canadian citizenship, a citizenship certificate, search of citizenship or renunciation of Canadian citizenship; individuals whose birth outside Canada has been registered with the Canadian government between January 1, 1947 and February 14, 1977 (inclusive); individuals whose Canadian citizenship has been recalled or revoked; citizenship consultants.
  - Purpose: Information described in this bank is used to determine the citizenship status of Canadians, and to facilitate the processing of applications for citizenship. The bank may also serve as a record of issuance of Canadian citizenship certificates. Personal information is collected pursuant to the *Citizenship Act* and the Citizenship Regulations.
  - Source: https://www.canada.ca/en/immigration-refugees-citizenship/corporate/transparency/access-information-privacy/info-source/personal-information-banks.html

### economic_immigration

EN: Submitted an Express Entry profile or economic permanent-residence application

FR: Soumis un profil Entrée express ou une demande de résidence permanente économique

Institution: Immigration, Refugees and Citizenship Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-citizenship-and-immigration:IRCC PPU 042` — Permanent Economic Residents (PPU 042)
  - Population: The program collects, uses, discloses and retains information about foreign nationals who have submitted a Profile under Express Entry or have applied for permanent residency in Canada under an economic class, along with information about family members included in their application.
  - Purpose: The personal information described in this bank is used to determine the eligibility of applicants for permanent residency under an economic class, as authorized under IRPA, and to administer and enforce program requirements.
  - Source: https://www.canada.ca/en/immigration-refugees-citizenship/corporate/transparency/access-information-privacy/info-source/personal-information-banks.html

### consular_help

EN: Registered with a Canadian mission abroad or sought consular help

FR: Inscrit auprès d'une mission canadienne à l'étranger ou demandé une aide consulaire

Institution: Global Affairs Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-foreign-affairs-trade-and-development:GAC PPU 010` — Consular Affairs - Assistance to Canadians
  - Population: Canadian residents in foreign countries who have registered with the nearest Canadian mission; Canadians who have sought or received assistance from Canadian missions; Canadians who have been arrested or detained abroad.
  - Purpose: The information contained in this bank is used to provide consular assistance to Canadian citizens abroad. It may be used, where necessary, to contact, advocate on behalf of, protect, rescue or evacuate Canadians and their family members.
  - Source: https://international.canada.ca/en/global-affairs/corporate/transparency/info-source

### ei

EN: Applied for Employment Insurance benefits

FR: Demandé des prestations d'assurance-emploi

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 150` — Insurance Claim File (PIB)
  - Population: Individuals who have applied for Employment Insurance benefits; individuals who share the benefits, when applicable; children or adults who are critically ill; family members who are gravely ill with a significant risk of death; and medical professionals who provide information when needed.
  - Purpose: Personal information is used to administer the Employment Insurance program. The authority to collect the personal information is provided under sections 7, 10, 22, 23, 152.07, and 152.1 of the *Employment Insurance Act*, and section 8 of the *Employment Insurance (Fishing) Regulations*. The Social Insurance Number is collected pursuant to subsection 28.1 (1) of the *Department of Employment and Social Development Act*.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### cpp

EN: Applied for or received a Canada Pension Plan benefit

FR: Demandé ou reçu une prestation du Régime de pensions du Canada

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 146` — Canada Pension Plan Program (PIB)
  - Population: Individuals who may be eligible for automatic enrolment, who have applied for or are currently receiving a CPP benefit (including individuals who may be subject to a provision), their spouse/common-law partner, children and representatives.
  - Purpose: Personal information is collected pursuant to the *Canada Pension Plan* and its Regulations. The personal information is used to administer CPP benefits, which includes determining eligibility and entitlement. The SIN is collected under the authority of section 52 of the *Canada Pension Plan Regulations* and in accordance with the Treasury Board Secretariat *Directive on the Social Insurance Number*, which names the CPP as an authorized user of the SIN. The SIN is used to ensure an individual's exact identification.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### oas

EN: Applied for or received Old Age Security, GIS or an Allowance

FR: Demandé ou reçu la Sécurité de la vieillesse, le SRG ou une allocation

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 116` — Old Age Security (PIB)
  - Population: Individuals who may be eligible for automatic enrolment, who have applied for or are currently receiving at least 1 of the following benefits: the OAS pension, the GIS, the Allowance or the Allowance for the Survivor, their spouse/common-law partner and representatives.
  - Purpose: Personal information is collected pursuant to the *Old Age Security Act*. The personal information is used to determine eligibility for and entitlement to benefits under the *Old Age Security Act*. The SIN is collected under the authority of Section 18 of the *Old Age Security Regulations*, and in accordance with Treasury Board Secretariat *Directive on the* Social Insurance Number, which lists the OAS program as an authorized user of the SIN. The SIN is used to ensure an individual's exact identification and for income verification purposes with the Canada Revenue Agency (CRA).
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### sin

EN: Applied for or updated a Social Insurance Number

FR: Demandé ou mis à jour un numéro d'assurance sociale

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 390` — Social Insurance Number Register (PIB)
  - Population: Canadian citizens; Registered Indians; permanent residents; temporary residents and others who are authorized to work in Canada; parent(s); representative(s) of the applicant; entity(ies) acting on behalf of an individual; and witnesses.
  - Purpose: Personal information may be used to register persons pursuant to section 138 of the *Employment Insurance Act*, subsection 28.1 (1) of the *Department of Employment and Social Development Act* and section 98 of the *Canada Pension Plan*, and those on whose behalf a SIN application has been received by the Canada Employment Insurance Commission (CEIC). Subsections 28.1 (2) and 28.2 (1) of the *Department of Employment and Social Development Act* authorize the CEIC to maintain a register containing the names of all persons registered and other information, as required, to accurately identify all persons so registered. Personal information may also be used in administering certain acts of Canada, such as the *Employment Insurance Act* and the *Income Tax Act*. Release of information from the Social Insurance Register (SIR) is pursuant to the *Department of Employment and Social Development Act* for the accurate identification of individuals and for the effective use by those individuals of SINs.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### rdsp

EN: Was a beneficiary or holder of a Registered Disability Savings Plan

FR: Bénéficiaire ou titulaire d'un régime enregistré d'épargne-invalidité

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 038` — Canada Disability Savings Program (PIB)
  - Population: Beneficiaries of an RDSP; parents of a beneficiary; a representative of an agency; departments or institutions acting as legal representatives of beneficiaries; and holders of RDSPs or individuals who have received the Canada Child Tax Credit for beneficiaries under the age of 18 or are currently receiving the Canada Child Benefit for beneficiaries under the age of 18.
  - Purpose: Personal information is used to determine: eligibility for a grant or bond; whether a plan should be registered; payment to the beneficiary of funds in the RDSP; the repayment of grants and bonds within 10 years of the termination or deregistration of a plan, or the death of a beneficiary; the repayment of grants and bonds paid within 10 years of a withdrawal from the RDSP, or if a withdrawal from the RDSP is made while the beneficiary is not approved for the Disability Tax Credit (DTC), the repayment of grants and bonds paid within the 10 years prior to loss of the DTC; and whether to waive, in prescribed circumstances, payments of a grant or bond, (or repayment or an amount or earnings of a grant or bond). Personal information is collected pursuant to the *Department of Employment and Social Development Act* (DESDA), sections 6, 7, 8, and 15 of the *Canada Disability Savings Act* and sections 2, 3, and 9 of the *Canada Disability Savings Regulations*, and pursuant to the *Income Tax Act*. The Social Insurance Number is collected pursuant to paragraph 8. (a) of the *Canada Disability Savings Act*, and pursuant to the *Canada Disability Savings Regulations* and the *Income Tax Act*.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### dental_plan

EN: Applied for the Canadian Dental Care Plan

FR: Demandé le Régime canadien de soins dentaires

Institution: Health Canada. Scope: inferred. Coverage: reviewed.

Health Canada's description includes administration with Service Canada and its contracted provider.

- `institution:ati-schedule-i-department-of-health:HC PPU 440` — Canadian Dental Care Plan
  - Population: General public, CDCP applicants and members (and their representatives, if applicable), oral health providers participating in the CDCP (and their representatives, if applicable), and individuals reporting, witnessing and/or alleged to be involved in CDCP-related suspicious activity.
  - Purpose: Personal information is collected pursuant to the Department of Health Act. The Social Insurance Number (SIN) is collected pursuant to section 12 of the Dental Care Measures Act and is used to administer the CDCP. Taxpayer information is used for the administration and evaluation of the CDCP under authorities in the Income Tax Act. Membership applicants that do not wish to provide their SIN will not be enrolled in the CDCP. Membership applications from someone who does not have or cannot get a SIN can be manually processed using a Temporary Taxation Number or through an alternate mechanism through which CRA's information on the individual could be validated between CRA and Service Canada. Personal information is used for verifying eligibility and enrolling members, processing and verifying claims, and registering and/or paying oral health providers for CDCP services, responding to enquiries and authentication.
  - Source: https://www.canada.ca/en/health-canada/corporate/about-health-canada/activities-responsibilities/access-information-privacy/info-source-federal-government-employee-information.html

### caf_application

EN: Applied to join the Canadian Armed Forces

FR: Demandé à m'enrôler dans les Forces armées canadiennes

Institution: National Defence. Scope: inferred. Coverage: reviewed.

Applying does not imply you served or had a member personnel file.

- `institution:ati-schedule-i-department-of-national-defence:DND PPU 025` — Enrolment
  - Population: Enrolment activities apply to individuals who have applied for enrolment, are being considered for enrolment, or are enrolled in the CAF.
  - Purpose: Personal information is used to process applications for enrolment and to assess the eligibility and suitability of applicants for service in the CAF. This includes verifying an applicant’s identity, qualifications, and background; conducting medical, security, and reliability screening; and supporting selection and enrolment decisions. Personal information may also be used to support occupation-specific selection processes that assess candidates against additional requirements, including suitability for specialized roles such as policing or chaplaincy.
  - Source: https://www.canada.ca/en/department-national-defence/corporate/transparency/access-information-privacy/info-source-sources-of-federal-government-and-employee-information.html

### caf_regular_service

EN: Served in the Regular Force

FR: Servi dans la Force régulière

Institution: National Defence. Scope: inferred. Coverage: reviewed.

The source bank specifies Regular Force members. Reserve service can be explored in the program directory.

- `institution:ati-schedule-i-department-of-national-defence:DND PPE 818` — Canadian Forces Member Personal Information File
  - Population: This bank applies to members of the Regular component of the CF.
  - Purpose: The purpose of the electronic file is to maintain a record of significant information regarding service members necessary to provide a support service to those engaged in personnel management or personnel administration of CF Regular Force personnel from enrolment to retirement. Information may be disclosed to appropriate personnel with Veterans Affairs Canada (VAC) for the purpose of administering benefits under the *Pension Act* or the *Canadian Forces Members and Veterans Re-establishment and Compensation Act*.
  - Source: https://www.canada.ca/en/department-national-defence/corporate/transparency/access-information-privacy/info-source-sources-of-federal-government-and-employee-information.html

### veterans_unknown

EN: Used a veterans benefit but do not know its name

FR: Utilisé une prestation pour vétérans sans en connaître le nom

Institution: Veterans Affairs Canada. Scope: inferred. Coverage: needs_detail.

Veterans Affairs is inferred. Choose a specific benefit below or explore its programs to identify relevant records.

### veterans_education

EN: Applied for Veterans Affairs' Education and Training Benefit

FR: Demandé la prestation pour études et formation d'Anciens Combattants

Institution: Veterans Affairs Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-veterans-affairs:VAC PPU 710` — You are here
  - Population: Veterans of the Canadian Forces (Regular and Reserve, including Supplementary Reserve), and/or their representatives.
  - Purpose: The personal information is used to determine eligibility for and administer the Education and Training Benefit. Personal information is collected pursuant to Part 1.1, sections 5.2 to 5.93 and section 78.1 of the *Veterans Well-being Act* formerly known as the *Canadian Forces Members and Veterans Re-establishment and Compensation Act* and its accompanying Regulations.
  - Source: https://www.veterans.gc.ca/en/info-source

### veterans_income

EN: Applied for Veterans Affairs' Income Replacement Benefit

FR: Demandé la prestation de remplacement du revenu d'Anciens Combattants

Institution: Veterans Affairs Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-veterans-affairs:VAC PPU 715` — You are here
  - Population: Former members of the Canadian Armed Forces (CAF), eligible surviving spouse/common-law partner or orphan(s) of a CAF member or Veteran, and/or their representatives.
  - Purpose: The personal information is used to administer benefits, determine eligibility, disburse funds, and provide services under the Income Replacement Benefit program. Personal information is collected pursuant to Part II, subsections 18(1), 22(1), 23(2), 24(1), 25(2), 26(1), 26(2) and Part IV, subsections 76(1), 76 (2), and sections 78.1, 78.2, and 80 of the *Veterans Well-being Act*. The SIN is collected pursuant to section 82 of the *Veterans Well-being Act* and is used for data matching purposes, including income confirmation/verification. In accordance with the *Income Tax Act*, the SIN is also used to issue income reporting slips to individuals, where applicable.
  - Source: https://www.veterans.gc.ca/en/info-source

### war_veterans_allowance

EN: Applied for the War Veterans Allowance

FR: Demandé l'allocation aux anciens combattants

Institution: Veterans Affairs Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-veterans-affairs:VAC PPU 040` — You are here
  - Population: Canadian Armed Forces Veterans, Merchant Navy Veterans, Allied Veterans, civilians who served in close support of the Canadian Armed Forces during wartime, surviving spouses, surviving common-law partners, orphans, dependents, and/or representatives.
  - Purpose: The personal information is used to administer the program, determine eligibility, entitlement, disperse funds, and provide services. Personal information is collected under the authority of section 4 of the *War Veterans Allowance Act*, sections 3 and 4 of the *Veterans Allowance Regulations*, and sections 9, 9.1 and 12 of the *Civilian War-Related Benefits Act*. The SIN is collected pursuant to subsection 30(3) of the *War Veterans Allowance Act* and subsection 57(1) of the *Civilian War-Related Benefits Act*, and is used for data matching purposes, including income verification. Subsections 104(1) and 105(1) under Part 6 of the *Economic Action Plan* 2014 *Act* provide authority for one-time payments to compensate for deductions in certain benefits and allowances that are payable under the *War Veterans Allowance Act* and the *Civilian War-related Benefits Act*.
  - Source: https://www.veterans.gc.ca/en/info-source

### agent_orange

EN: Applied for the Agent Orange ex-gratia payment related to CFB Gagetown in 1966–1967

FR: Demandé le paiement à titre gracieux pour l'agent Orange lié à la BFC Gagetown en 1966–1967

Institution: Veterans Affairs Canada. Scope: inferred. Coverage: reviewed.

Historical and narrowly defined program. It is never inferred from receiving another veterans benefit.

- `institution:ati-schedule-i-department-of-veterans-affairs:VAC PPU 200` — You are here
  - Population: Canadian Forces Members who trained at or were posted to Canadian Forces Base Gagetown (CFB Gagetown), Federal Government employees, civilian contractors or civilians who were posted or were employed at or lived in CFB Gagetown; in 1966 and 1967 and civilians who lived in a community within five kilometres of CFB Gagetown in 1966 and 1967. May also include the applicant’s representative, physician, power of attorney and/or caregiver.
  - Purpose: Information was used to support the decision making process and to administer the Agent Orange ex-gratia payments. Personal information was collected pursuant to *Order in Council* P.C. 2007-1326 September 10, 2007, and *Order in Council* P.C. 2010-1607 December 9, 2010.
  - Source: https://www.veterans.gc.ca/en/info-source

### military_housing

EN: Applied for or occupied housing managed by National Defence

FR: Demandé ou occupé un logement géré par la Défense nationale

Institution: National Defence. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-national-defence:DND PPU 885` — Housing and Accommodations
  - Population: Members of the Canadian Forces, spouses, and dependents, civilians and contractors.
  - Purpose: Information is used to administer the allocation of housing, and related contracting. The SIN may be collected, where required, under the authority of the *Income Tax Act*.
  - Source: https://www.canada.ca/en/department-national-defence/corporate/transparency/access-information-privacy/info-source-sources-of-federal-government-and-employee-information.html

### federal_job

EN: Applied for a federal civilian job

FR: Postulé à un emploi civil fédéral

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSE 902` — Staffing
  - Population: Employees of the institution and other individuals who apply for employment in the institution including through recruitment initiatives, as well as individuals who provide references or are supervisors of applicants.
  - Purpose: Personal information is used to administer recruitment and staffing activities in government institutions, which includes maintaining an inventory of potential candidates for future staffing actions. For most government institutions, personal information is collected pursuant to the Public Service Employment Act, the Employment Equity Act, and the Canadian Human Rights Act (section 16). For those institutions not subject to these Acts, consult the institution’s Access to Information and Privacy Coordinator to determine collection authority.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse902

### federal_employee

EN: Worked as a federal civilian employee

FR: Travaillé comme fonctionnaire fédéral civil

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.

Choose the employer. Military service and contracts have separate activities.

- `standard:PSE 901` — Employee Personnel Record
  - Population: Current and former employees of government institutions, emergency contacts of employees, and may also include spouses, dependants, and beneficiaries.
  - Purpose: Personal information is used to facilitate personnel administration in the employing institution and to ensure continuity and accuracy when an employee is transferred to another institution. For most government institutions, personal information is collected under the authority of the Public Service Employment Act (PSEA). For those institutions not subject to the (PSEA), consult the institution’s Access to Information and Privacy Coordinator to determine the legal authority for the collection. The Social Insurance Number is collected pursuant to the Income Tax Act.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse901

- `standard:PSE 904` — Pay and Benefits
  - Population: Current and former employees of government institutions.
  - Purpose: Personal information is shared with Public Works and Government Services and is used to disburse salaries and allowances and to process deductions and orders for garnishment and diversion of funds. Personal information is collected under various Acts including the Financial Administration Act, the Government Employees Compensation Act, and the Public Service Labour Relations Act. The Social Insurance Number (SIN) is collected pursuant to the Income Tax Act, Canada Pension Plan, and the Employment Insurance Act, and for some institutions, the SIN is shared with Public Works and Government Services to create the Personal Record Identifier.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse904

### employee_grievance

EN: Filed a grievance as a federal civilian employee

FR: Déposé un grief comme fonctionnaire fédéral civil

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSE 910` — Grievances
  - Population: Current and past employees of government institutions, their representatives or bargaining agents, and any other witness or individual who may be involved in the grievance process including individuals who serve as mediators, adjudicators, or arbitrators.
  - Purpose: Personal information is used for informal conflict resolution and/or to administer individual or group grievances at each of the levels in the grievance process. For most government institutions, personal information is collected pursuant to sections 207 and 208 of the Public Service Labour Relations Act and sections 66 and 76 of the Public Service Labour Relations Board Regulations. For those institutions not subject to the Act or Regulations, consult the institution’s Access to Information and Privacy Coordinator to determine the legal authority for the collection.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse910

### employee_assistance

EN: Used an Employee Assistance Program offered by a federal employer

FR: Utilisé un programme d'aide aux employés d'un employeur fédéral

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSE 916` — Employee Assistance
  - Population: Employees of the institution.
  - Purpose: The purpose of these records is to document information necessary for the administration of the Employee Assistance Program. To determine the need for employee assistance counselling, referrals for medical evaluations and participation in rehabilitation programs.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse916

### security_screening

EN: Completed a federal personnel security screening

FR: Fait l'objet d'un filtrage de sécurité du personnel fédéral

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSU 917` — Personnel Security Screening
  - Population: Job applicants, all current and former employees (students, agency and casual employees, persons on loan, assignment or secondment, exempt staff of ministers, ministers of state and parliamentary secretaries, locally engaged staff), volunteers, contractors, foreign and domestic visitors, immediate relatives, current and former spouse/common law partner, associates, cohabitants, individuals who give character references (including neighbours), current/former employers, parents or guardians of job applicants and employees under the age of 18.
  - Purpose: Personal information described in this bank is used to support decisions for granting, denying, revoking, or reviewing for cause the reliability status, security clearance, site access status or site access clearance of individuals working or applying to work through appointment, assignment or contract or other individuals with whom government may share or provide access to sensitive or information or assets, or access to facilities. For most institutions, personal information is collected pursuant to section 7 of the Financial Administration Act and as required under the Standard on Security Screening. That authority carries with it the authority to perform security screenings so as to ensure that individuals being appointed to the public service – and who have access to government information and assets – are reliable and loyal. Institutions may have additional legislative authorities under which security screening is to be performed. For those institutions not subject to the Financial Administration Act or the Standard , consult the institution's Access to Information Coordinator to determine collection authority.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu917

### professional_contract

EN: Bid on or held a federal professional-services contract

FR: Soumissionné ou obtenu un marché fédéral de services professionnels

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSU 912` — Professional Services Contracts
  - Population: Individuals representing themselves or employed through private companies (including temporary help services) who have submitted responses to Requests for Proposals and who have been engaged through contracts or standing offers with government institutions and individuals who are provided as professional references.
  - Purpose: Personal information is used to manage the contracting process, which includes the request for and receipt of proposals, evaluation of bids, selection of contractor, preparation, negotiation, execution, and award of contract, the disbursement of funds for services, deliverables, or both as specified within the contract, and post-contract evaluation. For most government institutions, personal information is collected under the authority of the Financial Administration Act. For those institutions not subject to the Act, consult the institution’s Access to Information and Privacy Coordinator to determine collection authority. The SIN is collected pursuant to the Income Tax Act.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu912

### aviation_licence

EN: Applied for a flight-crew or air-traffic-controller licence

FR: Demandé une licence de membre d'équipage de conduite ou de contrôleur aérien

Institution: Transport Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-transport:TC PPU 005` — Civil Aviation Personnel Licensing
  - Population: Aircraft flight crew members, air traffic controllers, and those applying for such licenses and permits.
  - Purpose: The personal information is used to administer the Canadian civil aviation flight crew and air traffic controller licensing program or activity and determine eligibility for the flight crew and air traffic controller permits and licenses. Personal information is collected pursuant to section 4.9 of the Aeronautics Act and Part IV of the Canadian Aviation Regulations - Personnel Licensing and Training - Subpart 1 - Flight Crew Permits, Licenses and Ratings.
  - Source: https://tc.canada.ca/en/corporate-services/transparency/info-source

### transport_clearance

EN: Applied for an airport or marine-facility security clearance

FR: Demandé une habilitation de sécurité pour un aéroport ou une installation maritime

Institution: Transport Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-transport:TC PPU 093` — Transportation Security Clearance Program
  - Population: Individuals who apply for a security clearance at airports and marine facilities. The application form also requests information about the application’s current and former spouse(s)/common-law partner(s). If the applicant is a minor, a parent/guardian/tutor must sign on his/her behalf.
  - Purpose: The information is used to conduct background checks to grant or refuse security clearances under the Transportation Security Clearance Program. For airport security clearances, the collection of personal information is authorized under subsection 4.8 of the Aeronautics Act. For marine security clearances, the personal information is collected pursuant to part 5 of the Marine Transportation Security Regulations.
  - Source: https://tc.canada.ca/en/corporate-services/transparency/info-source

### boating_card

EN: Obtained a Pleasure Craft Operator Card or an online-test token

FR: Obtenu une carte de conducteur d'embarcation de plaisance ou un jeton d'examen en ligne

Institution: Transport Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-transport:TC PPU 023` — National Pleasure Craft Operator Competency Program
  - Population: Individuals who have received a PCOC; individuals who have received a token to take their online test; and users of the PCOCDS.
  - Purpose: Personal information is collected pursuant to Section 207 1 of the Canada Shipping Act, 2001, and is used to populate a database, enabling Transport Canada to protect cardholder information and facilitate the replacement of lost or stolen cards.
  - Source: https://tc.canada.ca/en/corporate-services/transparency/info-source

### pleasure_craft_licence

EN: Licensed, transferred or cancelled a pleasure-craft licence

FR: Obtenu, transféré ou annulé un permis d'embarcation de plaisance

Institution: Transport Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-transport:TC PPU 044` — Pleasure Craft Licenses
  - Population: Current and previous owner(s) of pleasure craft.
  - Purpose: The personal information is collected to issue/transfer/cancel pleasure craft licenses; verify the identity of current and previous owner(s) of pleasure craft; and enforce pleasure craft regulatory compliance in keeping with the program’s objective of promoting safety. The authority to collect personal information is authorized pursuant to Part 10 of the Canada Shipping Act, 2001 and the Small Vessel Regulations.
  - Source: https://tc.canada.ca/en/corporate-services/transparency/info-source

### vessel_registration

EN: Registered a vessel with Transport Canada

FR: Immatriculé un bâtiment auprès de Transports Canada

Institution: Transport Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-transport:TC PPU 041` — Vessel Registration Query System
  - Population: Current and previous vessel owner(s), authorized representatives, mortgagers/mortgagees of vessels, marine surveyors, and tonnage measurers.
  - Purpose: The personal information is collected by Transport Canada for the purposes of registering a vessel. Personal information is collected under the authority of the Canada Shipping Act, 2001, pursuant to sections 43, 51, 53, 54, 58, 59, 65, 71, 72, 73, 75.01, 75.03, 75.1, 75.11 and 76.
  - Source: https://tc.canada.ca/en/corporate-services/transparency/info-source

### firearms_licence

EN: Applied for a firearms licence or related authorization

FR: Demandé un permis d'armes à feu ou une autorisation connexe

Institution: Royal Canadian Mounted Police. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-royal-canadian-mounted-police:RCMP PPU 100` — Canadian Firearms Program
  - Population: Non-resident individuals who have declared their firearms, and resident individuals who have applied for licences, registrations and other privileges or authorizations under the firearms legislation and have been issued them, or had licences, registration certificates and authorizations refused or revoked; or have been prohibited from possessing firearms, ammunition or other explosive substance. Individuals who are designated as Instructors by the CFO. Individuals who are named by applicants as references, guarantors or partners. Individuals who provide personal information about themselves or the applicant in support of the application (for example, parents/guardians, aboriginal community members, religious community members).
  - Purpose: Personal information in this bank is collected under the statutory authority of sections 54 and 55 of the Firearms Act and related Regulations and is used by federal and provincial officials in the administration of this legislation. The bank describes the administration and enforcement of firearms control legislation and regulations in Canada and at Canadian borders.
  - Source: https://rcmp.ca/en/corporate-information/access-information-and-privacy/info-source/rcmp-specific-personal-information-banks

### firearm_registration

EN: Applied to register a firearm

FR: Demandé l'enregistrement d'une arme à feu

Institution: Royal Canadian Mounted Police. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-royal-canadian-mounted-police:RCMP PPU 037` — Canadian Firearms Information System (CFIS)
  - Population: Individuals or businesses who have applied to register non-restricted, restricted or prohibited firearms in Canada and have been issued a registration certificate or been refused or have had a licence, authorization or certificate revoked. Individuals or businesses who have applied or been refused or have had a licence, authorization or certificate revoked; or have been prohibited from possessing firearms. Individual who are designated Instructors and certified to deliver safety course training. Individuals who are named by applicants as references, guarantors or partners. Individuals who provide personal information about themselves or the applicant in support of the application (for example, parents/guardians, aboriginal community members, religious community members). Public agencies who have reported inventories of agency firearms for use by agency employees and public agencies reporting protected firearms in agency custody following seizure, surrender of for some other reason.
  - Purpose: Information in this data bank is collected and maintained by the Canadian Firearms Program (CFP), under the authority of sections 54 and 55 of the Firearms Act and related Regulations and is used for the administration and enforcement of firearms control legislation in Canada.
  - Source: https://rcmp.ca/en/corporate-information/access-information-and-privacy/info-source/rcmp-specific-personal-information-banks

### student_finance

EN: Applied for Canada Student Loans or Grants, repayment assistance or loan forgiveness

FR: Demandé un prêt ou une bourse d'études du Canada, une aide au remboursement ou une remise de prêt

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 030` — Canada Student Financial Assistance Program (PIB)
  - Population: Full- and part-time students, students with permanent, persistent, or prolonged disabilities, students with Canadian citizenship or landed immigrant status, reservists (in the Canadian Forces Reserves), additional contact persons, parents/legal guardians or spouse/common-law partner of a borrower requesting eligibility for the Repayment Assistance Plan (RAP), and a borrower requesting eligibility to have a portion of his or her loan(s) forgiven under the Canada Student Loan forgiveness measure for doctors and nurses practicing in underserved rural or remote communities or under the Severe Permanent Disability Benefit.
  - Purpose: The personal information collected is used to administer student financial assistance through the CSFA Program, including: assessment of applications; determining eligibility to receive Canada Student Loans and Grants; management of the in-study/non-repayment period, student loan consolidation and repayment; and management of the repayment assistance plan, loan forgiveness under the Canada Student Loan forgiveness measure for doctors and nurses practicing in underserved rural or remote communities, loans forgiveness under the Severe Permanent Disability Benefit, and debt collections. Personal information is collected pursuant to the *Canada Student Financial Assistance Act* and Regulations, and the *Canada Student Loans Act* and Regulations. The SIN is collected pursuant to the *Canada Student Financial Assistance Act* and Regulations, and the *Canada Student Loans* *Regulations*.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### resp

EN: Was a beneficiary or subscriber of a Registered Education Savings Plan

FR: Bénéficiaire ou souscripteur d'un régime enregistré d'épargne-études

Institution: Employment and Social Development Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-employment-and-social-development:ESDC PPU 506` — Canada Education Savings Program (PIB)
  - Population: Subscribers; primary caregivers and their cohabitating spouse or common-law partner, beneficiaries of RESPs, individuals potentially eligible for incentives, and parents of newborns participating in the ESRS through their province's or territory's birth registry.
  - Purpose: Personal information is used to administer the *Canada Education Savings Act* (CESA) and to deliver funds for federally administered provincial education savings incentives. Personal information is collected pursuant to the *Department of Employment and Social Development Act,* the CESA and the *Canada Education Savings Regulations,* which govern the payment and administration of the CESG and the CLB held in RESPs. Through the ESRS, the provincial and/or territorial government collects personal information through a newborn registry or similar service on behalf of ESDC for the promotion of RESPs and the federal education savings incentives, pursuant to subsection 3.1 of the CESA. Personal information is also collected on behalf of the Canada Revenue Agency (CRA) for the administration of subsection 146.1 of the *Income Tax Act*, which governs the use of the RESPs into which the Government of Canada may deposit the CESG and CLB. The SIN is collected pursuant to section 7 and sub-section 12.1 of the CESA and is used to assess eligibility for the CESG and the CLB, and to register an education savings plan with the CRA for tax purposes.
  - Source: https://www.canada.ca/en/employment-social-development/corporate/transparency/access-information/reports/infosource-2023-2024/infosource-detailed.html

### phac_research

EN: Led, reviewed or supported a Public Health Agency research project

FR: Dirigé, examiné ou soutenu un projet de recherche de l'Agence de la santé publique

Institution: Public Health Agency of Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-public-health-agency-of-canada:PHAC PPU 290` — Research Projects
  - Population: Federal Government employees and other individuals including collaborators and supporters from external organizations such as universities, research institutes, granting and international bodies.
  - Purpose: Personal information is used in support of the funding, approval and management of research projects, as well as the review of the research process. Personal information is collected pursuant to Section 3 of the Public Health Agency of Canada Act and section 4 of the Department of Health Act.
  - Source: https://www.canada.ca/en/public-health/corporate/mandate/about-agency/access-information-privacy/info-source-federal-government-employee-information.html

### on_reserve_loan

EN: Received an on-reserve housing loan backed by a Ministerial Loan Guarantee

FR: Reçu un prêt au logement dans une réserve garanti par une garantie d'emprunt ministérielle

Institution: Indigenous Services Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-indigenous-services:ISC PPU 011` — On-Reserve Housing Program – Ministerial Loan Guarantee
  - Population: Persons registered under the Indian Act
  - Purpose: The purpose of this bank is to establish records of loans for housing from the Canada Mortgage and Housing Corporation (CMHC), a lender approved pursuant to the National Housing Act (NHA), made to applicants living on land as defined in the terms and conditions approved by the Order in Council P.C. 1999-2000, dated November 4, 1999. Loans are then monitored and administered under the terms of the Ministerial Guarantee.
  - Source: https://www.sac-isc.gc.ca/eng/1639748667069/1639748703555

### first_nations_estate

EN: Was involved in a First Nations estate administered by Indigenous Services

FR: Participé à une succession des Premières Nations administrée par Services aux Autochtones

Institution: Indigenous Services Canada. Scope: inferred. Coverage: reviewed.

The published population concerns people residing or ordinarily resident on reserve and specified relatives or representatives.

- `institution:ati-schedule-i-department-of-indigenous-services:ISC PPU 105` — First Nations Estates
  - Population: First Nations individuals residing/ordinarily resident on a reserve and may also include common-law partner, spouse, dependents, parents and relatives of the deceased, those declared incapable of managing their own affairs, minors, and appointed individuals.
  - Purpose: The personal information is to establish official records of First Nations estates. The bank is used in the administration of First Nations estates. Personal information is collected pursuant to sections 4.1, 4(3) and 42-52 of the Indian Act, and the Estates Regulations.
  - Source: https://www.sac-isc.gc.ca/eng/1639748667069/1639748703555

### cbsa_complaint

EN: Complained to CBSA about its staff or procedures

FR: Porté plainte à l'ASFC au sujet de son personnel ou de ses procédures

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 003` — Complaints – Personal Information Bank
  - Population: Members of the general public.
  - Purpose: The purpose of this bank is to maintain a record of complaints related to personnel and procedures.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### cbsa_recourse

EN: Asked CBSA to review an enforcement decision or seizure

FR: Demandé à l'ASFC de réviser une décision d'exécution ou une saisie

Institution: Canada Border Services Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 005` — Recourse Directorate Records – Personal Information Bank
  - Population: Travellers, importers, exporters and transportation companies, brokers, and warehouse operators.
  - Purpose: The principal purpose of the record is to assist Adjudicators and Officers of the Recourse Directorate in determining whether there is a contravention under the law and if the monetary terms should be mitigated or cancelled, or goods forfeited or returned. The records are also used for reporting purposes.
  - Source: https://www.cbsa-asfc.gc.ca/agency-agence/reports-rapports/pia-efvp/atip-aiprp/infosource-eng.html

### erc_grievance

EN: Was an RCMP member whose grievance was referred to the External Review Committee under the former RCMP Act

FR: Membre de la GRC dont le grief a été renvoyé au Comité externe d'examen sous l'ancienne Loi sur la GRC

Institution: RCMP External Review Committee. Scope: inferred. Coverage: reviewed.

A public complaint about police does not establish this referral or employment role.

- `institution:ati-schedule-i-royal-canadian-mounted-police-external-review-committee:ERC PPU 802` — RCMP Member Grievance Referrals under Part III of the former *RCMP Act
  - Population: Members of the RCMP who have submitted grievances which have been referred to the RCMP External Review Committee pursuant to the former *RCMP Act*; any other person mentioned in the records related to proceedings leading to a decision. **Purpose of Collection:** The information is used by the RCMP External Review Committee in reviewing grievances referred to it pursuant to the former *RCMP Act*.
  - Purpose:
  - Source: https://www.canada.ca/en/rcmp-external-review-committee/corporate/transparency/access-information-privacy/info-source-sources-federal-government-employee-information.html

### other_complaint

EN: Made another complaint or appeal to a federal organization

FR: Présenté une autre plainte ou un autre appel à une organisation fédérale

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: needs_detail.

Choose the organization, then explore its programs. The complaint type is needed to identify the appropriate bank.

### search_rescue

EN: Was the subject of or provided information for a military search-and-rescue operation

FR: Visé par une opération militaire de recherche et sauvetage ou fourni des renseignements à son sujet

Institution: National Defence. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-national-defence:DND PPU 050` — Search and Rescue
  - Population: Information described in this bank applies to individuals who were the objects of a search and/or rescue and those who provide information in support of a SAR operation. It may also include information about individuals involved in a SAR incident.
  - Purpose: Information described in this bank is used to help locate and rescue lost, injured, or otherwise distressed person, or to recover victims from a disaster. Information stored in the NSP MIS is used for reporting purposes, and for the management of the NSP.
  - Source: https://www.canada.ca/en/department-national-defence/corporate/transparency/access-information-privacy/info-source-sources-of-federal-government-and-employee-information.html

### access_request

EN: Made a formal access-to-information, personal-information or correction request

FR: Présenté une demande officielle d'accès à l'information, de renseignements personnels ou de correction

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSU 901` — Access to Information Act and Privacy Act Requests
  - Population: Individuals and their representatives who make formal requests to either obtain information or correct personal information under the control of the government institution.
  - Purpose: The personal information is used to process and respond to formal requests made under the Access to Information Act and the Privacy Act, including subsequent complaints, investigations and judicial review when applicable. Personal information is collected pursuant to section 13 of the Privacy Act, sections 8 and 11 of the Privacy Regulations, sections 6 and 11 of the Access to Information Act and section 4 of the Access to Information Regulations. The SIN is collected when required to locate personal information held by a program authorized through legislation or policy approval to use the SIN.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu901

### executive_correspondence

EN: Wrote to a federal minister or head of an institution

FR: Écrit à un ministre fédéral ou au dirigeant d'une institution

Institution: Ask which institution; unknown allowed. Scope: choose_institution. Coverage: reviewed.



- `standard:PSU 902` — Executive Correspondence
  - Population: General public, Members of Parliament, and officials representing other levels of government or international governments and agencies, external organizations and/or businesses.
  - Purpose: To manage, in a consistent and time-efficient manner, the receipt of, and responses to, correspondence or inquiries received from outside the institution that require replies from senior executives of the institution.
  - Source: https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu902

### health_consultation

EN: Took part in a Health Canada health-protection consultation

FR: Participé à une consultation de Santé Canada sur la protection de la santé

Institution: Health Canada. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-health:HC PPU 051` — Consultation on Health Protection Legislation
  - Population: Private citizens with an interest in health protection, public interest groups, health institutions, health professionals, representatives of all levels of government, members of federal departments, members of the industry, Canadian corporations and other interested parties.
  - Purpose: To create a mailing list and tracking system for consultation and follow-up purposes in the process of renewing Canada's health protection legislation, and for other consultations relating to the health protection program.
  - Source: https://www.canada.ca/en/health-canada/corporate/about-health-canada/activities-responsibilities/access-information-privacy/info-source-federal-government-employee-information.html

### space_launch

EN: Registered with the Canadian Space Agency to attend a mission launch

FR: Inscrit auprès de l'Agence spatiale canadienne pour assister au lancement d'une mission

Institution: Canadian Space Agency. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-canadian-space-agency:CSA PPU 020` — Registration to Attend Space Missions Launches
  - Population: Guests for the space missions launches.
  - Purpose: The personal information is used to obtain the necessary authorizations from the National Aeronautics and Space Administration (NASA), US, to allow guests to attend the launch of space mission. All the information requested in the application form is transmitted to NASA. They will then be kept and handled at NASA's discretion. A notice to this effect is available in the terms and conditions section of the form.
  - Source: https://www.asc-csa.gc.ca/eng/transparency/aipa/info-source.asp

### heritage_volunteer

EN: Registered with Canadian Heritage's Volunteer Centre

FR: Inscrit au Centre de bénévolat de Patrimoine canadien

Institution: Canadian Heritage. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-canadian-heritage:PCH PPU 070` — Volunteer Centre
  - Population: General public.
  - Purpose: Personal information is used to manage the volunteer registration process, which includes the request for and receipt of registrations and the selection of volunteers.
  - Source: https://www.canada.ca/en/canadian-heritage/corporate/publications/general-publications/information-programs-holdings.html

### canada_day_challenge

EN: Entered the Canada Day Challenge as a youth, or was their parent or guardian

FR: Participé au Défi de la fête du Canada comme jeune, parent ou tuteur

Institution: Canadian Heritage. Scope: inferred. Coverage: reviewed.



- `institution:ati-schedule-i-department-of-canadian-heritage:PCH PPU 027` — Canada Day Challenge
  - Population: Canadian youth between the ages of 5 to 18 years of age, as well as parents / legal guardians.
  - Purpose: The personal information was collected to administer the contest, to disburse prizes to the winners and finalists, to coordinate travel and accommodation arrangements for the winners and finalists and to promote the contest. The personal information was collected pursuant to paragraph 4(1) of the [Department of Canadian Heritage Act](https://laws-lois.justice.gc.ca/eng/acts/C-17.3/FullText.html).
  - Source: https://www.canada.ca/en/canadian-heritage/corporate/publications/general-publications/information-programs-holdings.html

## Retention rule ledger

Only the following reviewed single-event rules are executable. Other source schedules remain readable, with no automatic date conclusion.

### institution:ati-schedule-i-canadian-space-agency:CSA PPU 020

Event: the mission launch took place / le lancement de la mission a eu lieu

Disposition model: fixed; period: 2 years.

Source: Records will be retained for 2 years after the mission launch it concerned and then will be destroyed.

### institution:ati-schedule-i-department-of-national-defence:DND PPE 818

Event: you were released from the Canadian Forces / vous avez été libéré des Forces canadiennes

Disposition model: archive_after; period: 5 years.

Source: Records are retained for five years after release from the CF and then transferred to Library and Archives Canada.

### institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 018

Event: the most recent declaration card or kiosk receipt was dated / la plus récente carte de déclaration ou le reçu de la borne a été daté

Disposition model: fixed; period: 7 years.

Source: Files are retained for seven years from the date stamped on the traveller's declaration card (date of the interview between the traveller and the border services officer or date stamped on the traveller receipt when the traveller uses the Automated Border Clearance or NEXUS kiosk). After this period, the records are destroyed.

### institution:ati-schedule-i-canada-border-services-agency:CBSA PPU 003

Event: CBSA closed the complaint file / l'ASFC a fermé le dossier de plainte

Disposition model: minimum; period: 6 years.

Source: Files are retained for six (6) years after the file is closed.

### institution:ati-schedule-i-department-of-health:HC PPU 440

Event: the last administrative action on your dental-plan record took place / la dernière mesure administrative concernant votre dossier de soins dentaires a eu lieu

Disposition model: minimum; period: 2 years.

Source: Personal information will be retained for a minimum of two (2) years after the last administrative action and will follow the disposition standards set out by Library and Archives Canada.

### institution:ati-schedule-i-department-of-canadian-heritage:PCH PPU 070

Event: you left the volunteer program / vous avez quitté le programme de bénévolat

Disposition model: fixed; period: 2 years.

Source: Records are kept for two years after a volunteer leaves and then destroyed.

## Acceptance cases

Use [ACCEPTANCE_CASES.md](ACCEPTANCE_CASES.md) for reviewer stories and the public-release checklist.

## Source context

These are extracted local snapshot excerpts. They are navigation context, not personal-record matching evidence.

### Accessibility Standards Canada

EN — `institutions_infosource_docs/ati-schedule-i-canadian-accessibility-standards-development-organization/classes_of_records_en.md:118` — Background

Accessibility Standards Canada is a departmental corporation created in 2019 under the *Accessible Canada Act* (the Act). We are committed to creating accessibility standards for [federally-regulated entities and federal organizations](https://accessible.canada.ca/about-us#fedRule "About us"). These include government buildings, banks, and federal courts, among others. We are an accredited standards development organization. This means our standards are recognized as National Standards of Canada. This helps us open doors so that Canada can influence and be a global leader on matters related to accessibility.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-accessibility-standards-development-organization/classes_of_records_en.md:127` — Responsibilities

1. Developing accessibility standards
2. Advancing accessibility research
3. Sharing information related to accessibility

These activities are aligned with the priority areas in the [Act](https://laws-lois.justice.gc.ca/eng/acts/A-0.6/).

We specialize in creating and revising accessibility standards that aim to help federally-regulated entities and federal organizations eliminate barriers to accessibility. Our process involves gathering insights from experts, including individuals with lived experience, to ensure the standards address the needs of diverse groups. The public is invited to comment on each standard.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-accessibility-standards-development-organization/classes_of_records_fr.md:118` — Contexte

Normes d'accessibilité Canada est une organisation publique créée en 2019 en vertu de la *Loi canadienne sur l'accessibilité* (la Loi). Nous nous engageons à créer des normes d'accessibilité pour les [entités sous réglementation fédérale et les organisations fédérales](/a-propos-de-nous#compfed "À propos de nous"). Il s'agit entre autres des immeubles gouvernementaux, des banques et des tribunaux fédéraux. Nous sommes un organisme d'élaboration de normes accrédité. Cela signifie que nos normes sont reconnues comme des normes nationales du Canada. Cela nous aide à ouvrir des portes pour que le Canada puisse influencer et être un leader mondial sur les questions liées à l'accessibilité.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-accessibility-standards-development-organization/classes_of_records_fr.md:127` — Responsabilités

Nous avons le mandat essentiel de contribuer à la réalisation d'un Canada sans obstacles d'ici 2040. Nous y parvenons en :

1. Élaborant des normes d'accessibilité
2. Faisant progresser la recherche sur l'accessibilité
3. Partageant l'information relative à l'accessibilité

Ces activités sont alignées sur les domaines prioritaires de la [Loi](https://laws-lois.justice.gc.ca/fra/lois/a-0.6/).

### Administrative Tribunals Support Service of Canada

EN — `institutions_infosource_docs/ati-schedule-i-administrative-tribunals-support-service-of-canada/classes_of_records_en.md:67` — Background

The [Administrative Tribunals Support Service of Canada (ATSSC)](https://www.canada.ca/en/administrative-tribunals-support-service/index.html) was established with the coming into force on November 1, 2014, of the Administrative Tribunals Support Service of Canada Act. The ATSSC is responsible for providing the support services and the facilities that are needed by each of the administrative tribunals it serves to enable them to exercise their powers and perform their duties and functions in accordance with their legislation and rules.

The ATSSC reports to Parliament through the Minister of Justice and Attorney General of Canada.

EN — `institutions_infosource_docs/ati-schedule-i-administrative-tribunals-support-service-of-canada/classes_of_records_en.md:73` — Responsibilities

The ATSSC is responsible for providing support services and facilities to 12 federal administrative tribunals and the National Joint Council by way of a single, integrated organization.

These services include the specialized services required to support the mandate of each tribunal (registry services, legal services and mandate and member services), as well as internal services (human resources, financial services, information management and technology, accommodation, security, planning, and communications). Through these specialized services, the ATSSC supports improving access to justice for Canadians. [Supported tribunals:](https://www.canada.ca/en/administrative-tribunals-support-service/index.html)

Please visit our website for more information on the [ATSSC’s mandate, program responsibilities, and major policies](https://www.canada.ca/en/administrative-tribunals-support-service.html).

FR — `institutions_infosource_docs/ati-schedule-i-administrative-tribunals-support-service-of-canada/classes_of_records_fr.md:68` — Contexte

Le [Service canadien d’appui aux tribunaux administratifs (SCDATA)](https://www.canada.ca/fr/service-canadien-appui-tribunaux-administratifs.html) a été créé avec l’entrée en vigueur, le 1er novembre 2014, de la *Loi sur le Service canadien d’appui aux tribunaux administratifs*. Le SCDATA est responsable de la prestation des services de soutien et de la fourniture des installations qui sont nécessaires à chacun des tribunaux administratifs qu’il sert, afin qu’ils puissent exercer leurs pouvoirs et s’acquitter de leurs devoirs et fonctions en conformité avec les lois et les règles qui les régissent.

Le SCDATA rend des comptes au Parlement par l’entremise du ministre de la Justice et procureur général du Canada.

FR — `institutions_infosource_docs/ati-schedule-i-administrative-tribunals-support-service-of-canada/classes_of_records_fr.md:74` — Responsabilités

Le SCDATA est responsable de fournir des services de soutien et des installations à 12 tribunaux administratifs fédéraux et le Conseil national mixte au moyen d’un guichet unique et intégré.

Ces services comprennent les services spécialisés requis par chacun des tribunaux (Service de greffe, services juridiques et services liés aux mandats et aux membres), ainsi que des services internes (ressources humaines, services financiers, gestion et technologies de l’information, aménagement des locaux, sécurité, planification et communications). Grâce à ces services spécialisés, le SCDATA contribue à améliorer l’accès à la justice pour les Canadiennes et Canadiens. [Tribunaux appuyés:](https://www.canada.ca/fr/service-canadien-appui-tribunaux-administratifs.html)

Veuillez consulter notre site web pour plus d’informations sur [le mandat, les responsabilités des programmes et les principales politiques du SCDATA](https://www.canada.ca/fr/service-canadien-appui-tribunaux-administratifs.html).

### Agriculture and Agri-Food Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-agriculture-and-agri-food/classes_of_records_en.md:144` — Background

Agriculture and Agri-Food Canada's (AAFC) history goes back to the late 1860s when Jean-Charles Chapais presided over the pre-confederation Bureau of Agriculture until 1868. Although, he was formally appointed by Order in Council as Canada's first Minister of Agriculture on July 1, 1867, AAFC was formalized in 1868 by an Act for the Organization of the Department of Agriculture. This act was passed by Parliament, followed by the formation of the Experimental Farms System in 1886.

The department has evolved over the years and, today, AAFC has offices and facilities from coast to coast.

AAFC, along with its portfolio partners, report to Parliament and Canadians through the Minister of Agriculture and Agri-Food.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-agriculture-and-agri-food/classes_of_records_en.md:156` — Responsibilities

AAFC's mandate is based on the [Department of Agriculture and Agri-Food Act](https://lois-laws.justice.gc.ca/eng/acts/A-9/) (DAAFA).

AAFC provides information, research and technology, and policies and programs to help Canada's agriculture, agri-food and agri-based products sector compete in markets at home and abroad, manage risk and embrace innovation.

The activities of the department extend from the farmer to the consumer, from the farm to global markets, through all phases of the sustainable production, processing and marketing of agriculture and agri-food products. In this regard, and in recognition that agriculture is a shared jurisdiction, AAFC works closely with provincial and territorial governments.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-agriculture-and-agri-food/classes_of_records_fr.md:144` — Contexte

Les origines d'agriculture et Agroalimentaire Canada remontent à la fin des années 1860. Le Bureau de l'agriculture, créé avant la Confédération, sera présidé par Jean-Charles Chapais jusqu'en 1868. Le 1er juillet 1867, monsieur Chapais est nommé par décret et devient le tout premier ministre de l'Agriculture du Canada, mais ce n'est qu'en 1868 que sera promulguée la loi qui porte création du ministère de l'Agriculture, ce qui officialise la création d'AAC. Le Parlement adopte cette loi, et elle sera suivie par la création du réseau de fermes expérimentales en 1886.

Le Ministère a évolué au fil des ans et, aujourd'hui, AAC compte des bureaux et des installations partout au Canada.

AAC, au même titre que ses partenaires de portefeuille, est responsable devant le Parlement et la population canadienne par l'intermédiaire du ministre de l'Agriculture et de l'Agroalimentaire.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-agriculture-and-agri-food/classes_of_records_fr.md:156` — Responsabilités

Le mandat d'AAC est fondé sur la [Loi sur le ministère de l'Agriculture et de l'Agroalimentaire](https://lois-laws.justice.gc.ca/fra/lois/a-9/) (LMAA).

AAC diffuse de l'information, fait de la recherche et met au point des technologies et offre des politiques et des programmes qui aident les secteurs canadiens de l'agriculture, de l'agroalimentaire et des produits agro-industriels à soutenir la concurrence sur les marchés nationaux et internationaux, à gérer les risques et à faire preuve d'innovation.

Les activités du Ministère touchent toutes les phases de la production, de la transformation et de la mise en marché durables des produits agricoles et agroalimentaires, de l'agriculteur au consommateur, des exploitations agricoles aux marchés mondiaux. Dans ce contexte, et compte tenu du fait que l'agriculture est une compétence partagée, AAC collabore étroitement avec les gouvernements provinciaux et territoriaux.

### Atlantic Canada Opportunities Agency

EN — `institutions_infosource_docs/ati-schedule-i-atlantic-canada-opportunities-agency/classes_of_records_en.md:84` — Background

The Atlantic Canada Opportunities Agency (ACOA) is the federal department responsible for the Government of Canada’s economic development efforts in the provinces of New Brunswick, Prince Edward Island, Nova Scotia, and Newfoundland and Labrador. ACOA reports to Parliament via the Minister of Justice and Attorney General of Canada and Minister responsible for the Atlantic Canada Opportunities Agency. The Agency was established in 1987, with legislative status under the [*Government Organization Act*, Atlantic Canada, 1987](http://laws-lois.justice.gc.ca/eng/acts/G-5.7/index.html). Part I of the act (cited as the *Atlantic Canada Opportunities Agency Act*) established the Agency, while Part II established Enterprise Cape Breton Corporation (ECBC). ECBC was dissolved on June 19, 2014, and its economic business and community development activities were transferred to ACOA.

EN — `institutions_infosource_docs/ati-schedule-i-atlantic-canada-opportunities-agency/classes_of_records_en.md:88` — Responsibilities

The Atlantic Canada Opportunities Agency works in partnership with Atlantic Canadians to improve the economy of communities throughout the region and to enhance the region’s competitiveness. Working with partners in government, the private sector, academia and other non-government sectors, ACOA seeks to advance economic opportunities and innovation to serve the needs of businesses, organizations, individuals and communities. This work addresses the Agency’s mandate “to enhance the growth of earned income and employment opportunities in Atlantic Canada.”

The Agency’s head office is in Moncton, N.B. Regional offices are located in the four provincial capitals in Atlantic Canada, each led by a vice-president. The Agency also provides services via local field offices throughout the four provinces. In addition, through its Ottawa office, ACOA ensures that Atlantic Canada’s interests are reflected in the policies and programs developed by other departments and agencies of the federal government.

Please refer to the Agency’s annual [Departmental Plan and Departmental Results Report](https://www.canada.ca/en/atlantic-canada-opportunities/corporate/transparency.html) for more information on initiatives and specific plans.

FR — `institutions_infosource_docs/ati-schedule-i-atlantic-canada-opportunities-agency/classes_of_records_fr.md:85` — Contexte

L’Agence de promotion économique du Canada atlantique (APECA ou l’Agence) est le ministère fédéral chargé des activités de développement économique du gouvernement du Canada dans les provinces du Nouveau-Brunswick, de l’Île-du-Prince-Édouard, de la Nouvelle-Écosse et de Terre-Neuve-et-Labrador. L’APECA relève du Parlement par l’entremise du ministre des Langues officielles et ministre responsable de l’Agence de promotion économique du Canada atlantique. L’Agence a été fondée à titre législatif en 1987, en vertu de la [*Loi organique de 1987* *sur le Canada atlantique*](https://laws-lois.justice.gc.ca/fra/lois/g-5.7/index.html). La partie I de la Loi, nommée *Loi sur l’Agence de promotion économique du Canada atlantique,* prévoyait la création de l’APECA, alors que la partie II prévoyait la constitution de la Société d’expansion du Cap-Breton (SECB). La SECB a été dissoute le 19 juin 2014 et les activités de développement économique des entreprises et des collectivités ont été transférées à l’APECA.

FR — `institutions_infosource_docs/ati-schedule-i-atlantic-canada-opportunities-agency/classes_of_records_fr.md:89` — Responsabilités

L’Agence travaille en partenariat avec les Canadiens et Canadiennes de la région de l’Atlantique au renforcement de l’économie des collectivités et de la capacité concurrentielle de l’ensemble de la région. En collaboration avec ses partenaires du gouvernement, du secteur privé, des universités et d’autres secteurs non gouvernementaux, l’APECA s’emploie à promouvoir la création de débouchés économiques et l’innovation afin de répondre aux besoins des entreprises, des organismes, des particuliers et des collectivités. Elle remplit ainsi le mandat qui lui est confié, soit de « favoriser la croissance des revenus et la création d’emplois au Canada atlantique ».

Le siège social de l’Agence est situé à Moncton (Nouveau-Brunswick). Les bureaux régionaux sont basés dans les quatre capitales provinciales du Canada atlantique, chacun étant dirigé par un vice-président régional. L’Agence fournit également des services à partir de ses bureaux locaux situés un peu partout dans les quatre provinces. De plus, par l’intermédiaire de son bureau d’Ottawa, elle veille à ce que les intérêts du Canada atlantique soient pris en compte dans les politiques et les programmes établis par d’autres ministères et organismes du gouvernement fédéral.

Veuillez consulter les [Plans ministériels et les Rapports sur les résultats ministériels](https://www.canada.ca/fr/promotion-economique-canada-atlantique/organisation/transparence.html) diffusés chaque année par l’Agence pour obtenir de plus amples renseignements sur des initiatives et des plans particuliers.

### Canada Border Services Agency

EN — `institutions_infosource_docs/ati-schedule-i-canada-border-services-agency/classes_of_records_en.md:88` — Background

The Canada Border Services Agency (CBSA) was created on December 12, 2003. Its creation brought together the Customs function of the former Canada Customs and Revenue Agency (CCRA), the Enforcement function of Immigration, Refugees and Citizenship Canada (IRCC), and the Import Inspection at Ports of Entry function of the Canadian Food Inspection Agency.

On November 3, 2005, the Canada Border Services Agency Act, an Act to establish the Canada Border Services Agency (CBSA) (Bill C-26), received Royal Assent. This Act defines the Canada Border Services Agency's (CBSA) mandate, powers and authorities.

The Canada Border Services Agency (CBSA) reports to Parliament as part of the Public Safety Portfolio.

EN — `institutions_infosource_docs/ati-schedule-i-canada-border-services-agency/classes_of_records_en.md:96` — Responsibilities

Read about the Canada Border Services Agency's (CBSA) [mandate, its program responsibilities and its major policies](/agency-agence/actreg-loireg/legislation-eng.html).

FR — `institutions_infosource_docs/ati-schedule-i-canada-border-services-agency/classes_of_records_fr.md:88` — Historique

L'Agence des services frontaliers du Canada (ASFC) a été créée de 12 décembre 2003.  Sa création a réuni la fonction douanière de l'ancienne Agence des douanes et du revenu du Canada (ADRC), la fonction d'exécution de L'Immigration, Réfugiés et Citoyenneté du Canada (IRCC) et l'importation inspection au poste d'entrée de l'Agence canadienne d'inspection des aliments.

Le 3 novembre 2005, la *Lois sur l'Agence des services frontaliers du Canada*, Loi constituent l'Agence des services frontaliers du Canada (ASFC) (projet de loi C-26), a reçu la sanction royale.  Cette loi définit le mandate, les pouvoirs et autorités de l'Agence des services frontaliers du Canada (ASFC).

L'Agence des services frontaliers du Canada (ASFC) fait rapport au Parlement dans le cadre du Portefeuille de la sécurité publique.

FR — `institutions_infosource_docs/ati-schedule-i-canada-border-services-agency/classes_of_records_fr.md:96` — Responsabilités

Lisez le [mandat de l'Agence des services frontaliers du Canada](/agency-agence/actreg-loireg/legislation-fra.html), ainsi que les responsabilités de ses programmes et ses politiques majeures.

### Canada Economic Development for Quebec Regions

EN — `institutions_infosource_docs/ati-schedule-i-economic-development-agency-of-canada-for-the-regions-of-quebec/classes_of_records_en.md:110` — Background

For more information on the history of the Economic Development Agency of Canada for the Regions of Quebec (“the Agency”), visit our [website](/en/economic-development-quebec-regions.html).

With the entry into force of the  [*Economic Development Agency of Canada for the Regions of Quebec Act*](https://laws-lois.justice.gc.ca/eng/acts/e-1.3/index.html)  on October 5, 2005, the Agency has a legal status to promote the economic development and diversification of the regions of Quebec.

The Agency reports to Parliament through the Minister of Tourism and Minister responsible for the Economic Development Agency of Canada for the Regions of Quebec.

EN — `institutions_infosource_docs/ati-schedule-i-economic-development-agency-of-canada-for-the-regions-of-quebec/classes_of_records_en.md:118` — Responsibilities

Information on the raison d’être, mandate and role of the Agency can be found on our [website.](/en/economic-development-quebec-regions/about.html)

Information on the three major programs that cover the various financial assistance measures offered by the Agency can be found on our [website](/en/economic-development-quebec-regions.html).

As a funding agency, the Agency's [main policies](https://www.tbs-sct.canada.ca/pol/index-eng.aspx) are those of the Treasury Board.

FR — `institutions_infosource_docs/ati-schedule-i-economic-development-agency-of-canada-for-the-regions-of-quebec/classes_of_records_fr.md:128` — Contexte

Pour en savoir plus sur l’historique de l’Agence de développement économique du Canada pour les régions du
Québec (ci-après, l’Agence), consultez notre [site
Web](/fr/developpement-economique-regions-quebec.html).

Avec l’entrée en vigueur de la [*Loi sur
l'Agence de développement économique du Canada pour les régions du Québec*](https://laws-lois.justice.gc.ca/fra/lois/E-1.3/index.html) le 5 octobre 2005,
l’Agence possède une base juridique propre pour promouvoir le développement et la diversification de
l’économie des régions du Québec.

L’Agence rend compte au Parlement par l’entremise de la ministre du Tourisme et ministre responsable de
l’Agence de développement économique du Canada pour les régions du Québec.

FR — `institutions_infosource_docs/ati-schedule-i-economic-development-agency-of-canada-for-the-regions-of-quebec/classes_of_records_fr.md:142` — Responsabilités

Des renseignements sur la raison d’être, le mandat et le rôle de l'Agence se trouvent sur notre [site Web.](/fr/developpement-economique-regions-quebec/a-propos.html)

Des renseignements sur les trois grands programmes qui regroupent les diverses mesures d’aide financière
offertes par l’Agence se trouvent sur notre [site
Web](/fr/developpement-economique-regions-quebec.html).

En tant qu’organisme de financement, [les
principales politiques](https://www.tbs-sct.canada.ca/pol/index-fra.aspx) de l’Agence sont celles du Conseil du Trésor.

### Canada Energy Regulator

EN — `institutions_infosource_docs/ati-schedule-i-canadian-energy-regulator/classes_of_records_en.md:90` — Responsibilities

Please refer to the [CER’s Departmental Plan](/en/about/publications-reports/departmental-plan/) and its [Departmental Results Reports](/en/about/publications-reports/departmental-results-reports/) for more information on specific plans and initiatives.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-energy-regulator/classes_of_records_fr.md:90` — Responsabilités

Veuillez vous reporter au plan ministériel de la Régie et à ses [rapports sur les résultats ministériels](/fr/regie/publications-rapports/rapport-resultats-ministeriels/) pour un complément d’information sur des plans et initiatives précis.

### Canada Foundation for Innovation

EN — `institutions_infosource_docs/ati-schedule-i-canada-foundation-for-innovation/classes_of_records_en.md:93` — Background

The Canada Foundation for Innovation (CFI) is an independent corporation established by the Government of Canada through Part 1 of the Budget Implementation Act, 1997 to fund research infrastructure. The CFI reports to a Board of Directors. The CFI Board is composed of a maximum of 13 individuals from a variety of backgrounds. Each Director has a unique perspective and understanding of the research community and brings expertise from one or more of the private, institutional, academic, research or government sectors. The Government of Canada appoints six Directors, including the Chair, while the remaining Directors are appointed by CFI Members. Directors are nominated and appointed for three-year terms. The CFI reports to Parliament through the Minister of Science.

EN — `institutions_infosource_docs/ati-schedule-i-canada-foundation-for-innovation/classes_of_records_en.md:97` — Responsibilities

The Canada Foundation for Innovation (CFI) funds research infrastructure which consists of state-of-the-art equipment, buildings, laboratories, and databases required to conduct research. The CFI's mandate is to strengthen the capacity of Canadian universities, colleges, research hospitals, and non-profit research institutions to carry out world-class research and technology development that benefits Canadians.

FR — `institutions_infosource_docs/ati-schedule-i-canada-foundation-for-innovation/classes_of_records_fr.md:99` — Historique

La Fondation canadienne pour l'innovation (FCI) est un organisme autonome établi par le gouvernement du Canada en vertu de la Partie I de la *Loi d'exécution du budget de 1997* pour financer l'infrastructure de recherche. La FCI relève d'un conseil d'administration. Le Conseil est composé d’au plus 13 personnes provenant de divers milieux. Chacun des administrateurs apporte une perspective et une compréhension particulières ainsi qu’une expertise du monde de la recherche acquise dans le secteur privé, les établissements d’enseignement ou de recherche, ou l’administration fédérale. Le gouvernement du Canada nomme six administrateurs, dont le président du Conseil. Les autres administrateurs sont désignés par les membres de la FCI pour un mandat de trois ans. La FCI fait rapport à la ministre des sciences.

FR — `institutions_infosource_docs/ati-schedule-i-canada-foundation-for-innovation/classes_of_records_fr.md:103` — Responsabilités

La FCI a été créée pour financer l'infrastructure de recherche (équipements, immeubles, laboratoires et bases de données de pointe) nécessaires à la recherche. Son mandat est de renforcer la capacité des universités, des collèges et des hôpitaux de recherche, de même que des établissements de recherche à but non lucratif du Canada à mener des projets de recherche et de développement technologique de calibre mondial qui produisent des retombées pour les Canadiens.

### Canada Revenue Agency

EN — `institutions_infosource_docs/ati-schedule-i-canada-revenue-agency/classes_of_records_en.md:117` — Background

In 1927, the *Department of National Revenue Act* established the Department of National Revenue by renaming the Department of Customs and Excise. The Department was responsible for assessing and collecting duty and tax, monitoring the movement of people and goods across the Canadian border, and protecting Canadian industries from foreign competition.

The same act created a second department to collect income tax, a responsibility that a commissioner from the Department of Finance had been meeting. Both departments had the same minister, but each had its own departmental organization and deputy minister.

On April 29, 1999, Parliament passed the *Canada Customs and Revenue Agency Act*, which established the Canada Customs and Revenue Agency (now the Canada Revenue Agency). The change in status from department to agency, which took place on November 1, 1999, has helped build a modern organization that is committed to leadership, innovation, and client service.

EN — `institutions_infosource_docs/ati-schedule-i-canada-revenue-agency/classes_of_records_en.md:129` — Responsibilities

The Canada Revenue Agency (CRA) is the principal revenue collector in the country and is responsible for distributing benefit payments to millions of Canadians each year.

The Agency was created to: provide better service to Canadians; offer more efficient and more effective delivery of government programs; foster closer relationships with provinces and other levels of government for which the CRA delivers programs; and provide better accountability.

The CRA’s [mission](/en/revenue-agency/corporate/about-canada-revenue-agency-cra/mission-vision-values.html) is to administer tax, benefits, and related programs, and ensure compliance on behalf of governments across Canada, thereby contributing to the ongoing economic and social well-being of Canadians. The CRA exercises its mission within a framework of complex laws enacted by Parliament, as well as by provincial and territorial legislatures. Our mission reflects the broad role that we assume in the lives of Canadians.

FR — `institutions_infosource_docs/ati-schedule-i-canada-revenue-agency/pibs_fr.md:117` — Historique

Le ministère du Revenu national a été créé en 1927 par suite de l'adoption de la *Loi sur le ministère de Revenu national*, qui donnait un nouveau nom au ministère des Douanes et de l'Accise. Les responsabilités du Ministère englobaient alors l'imposition et la perception de droits et de taxes, le contrôle du mouvement des personnes et des biens à la frontière canadienne et la protection des industries canadiennes contre la concurrence étrangère.

Cette même loi créait en outre un second ministère chargé du recouvrement de l'impôt sur le revenu, une responsabilité auparavant confiée à un commissaire du ministère des Finances. Un seul ministre était responsable des deux ministères, qui comptaient deux organisations ministérielles toutefois dirigées par des sous-ministres distincts.

Le 29 avril 1999, le Parlement a adopté la *Loi sur l'Agence des douanes et du revenu du Canada* constituant l'Agence des douanes et du revenu du Canada (maintenant l'Agence du Revenu du Canada). Le passage du statut de ministère à celui d'agence, qui a eu lieu le 1er novembre 1999, a favorisé la création d'une organisation moderne qui s'engage à faire preuve de leadership et d'innovation et à bien servir la clientèle.

FR — `institutions_infosource_docs/ati-schedule-i-canada-revenue-agency/pibs_fr.md:129` — Responsabilités

L'Agence du revenu du Canada (ARC) est le principal percepteur de recettes au pays et est responsable de verser des prestations à des millions de Canadiens chaque année.

L'Agence a été créée pour les raisons suivantes : procurer un meilleur service aux Canadiens; offrir une prestation plus efficiente et efficace des programmes gouvernementaux; favoriser des liens plus étroits avec les provinces et les autres niveaux de gouvernement pour lesquels l'ARC exécute des programmes; et offrir une meilleure reddition de comptes.

L'ARC a pour mission d’exécuter les programmes fiscaux, de prestation et autres, et d’assurer l’observation fiscale pour le compte de gouvernements dans l’ensemble du Canada, de façon à contribuer au bien-être économique et social continu des Canadiens. L'ARC procède à l'exercice de sa mission dans le cadre de lois complexes adoptées par le Parlement et d'assemblées législatives provinciales et territoriales. Notre mandat reflète le rôle élargi que nous jouons dans la vie des Canadiens

### Canada School of Public Service

EN — `institutions_infosource_docs/ati-schedule-i-canada-school-of-public-service/classes_of_records_en.md:131` — Background

The Canada School of Public Service (the School) was created on April 1, 2004, when the legislative provisions of Part IV of the Public Service Modernization Act came into force. The School has been part of the Treasury Board Portfolio since July 2004. Operating under the authority of the Canada School of Public Service Act, the School was created from an amalgamation of the following three organizations: the Canadian Centre for Management Development, Training and Development Canada and Language Training Canada. It reports to Parliament through the Minister of the Treasury Board, who is the Minister responsible for the School.

For information about the School's core responsibilities, planned results and resources, reporting framework and more, consult our [Departmental Plan 2025-2026.](/about_us/currentreport/dp-pm2025-26/index-eng.aspx)

EN — `institutions_infosource_docs/ati-schedule-i-canada-school-of-public-service/classes_of_records_en.md:137` — Responsibilities

The School has the legislative mandate to provide a range of enterprise‐wide learning activities to build individual and organizational capacity and management excellence within the core public service. Using a broad ecosystem of learning products, delivery approaches, and an online learning platform, the School provides public servants with the foundational knowledge, skills, and competencies now in the future, to serve Canadians with excellence.

FR — `institutions_infosource_docs/ati-schedule-i-canada-school-of-public-service/classes_of_records_fr.md:132` — Historique

L'École de la fonction publique du Canada (l'École) a été créée le 1er avril 2004, lorsque les dispositions législatives de la partie IV de la Loi sur la modernisation de la fonction publique est entrée en vigueur. L'École fait partie du portefeuille du Conseil du Trésor depuis juillet 2004. Fonctionnement sous l'autorité de la Lois de l'École de la fonction publique du Canada, l'École a été créé par la fusion de trois organismes suivants : le Centre canadien de gestion, Formation et perfectionnement Canada et Formation linguistique Canada. Il rend compte au Parlement par l'entremise du ministre du Conseil du Trésor, qui est le ministre responsable de l'École.

Pour obtenir des renseignements sur les principales responsabilités de l'École, les résultats prévus et les ressources, cadre de présentation de rapports et plus, consulter notre [Plan ministériel 2025-2026](/about_us/currentreport/dp-pm2025-26/index-fra.aspx).

FR — `institutions_infosource_docs/ati-schedule-i-canada-school-of-public-service/classes_of_records_fr.md:138` — Responsabilités

L'École a le mandat législatif de fournir un éventail de Enterprise ‐ large des activités d'apprentissage pour bâtir la capacité individuelle et organisationnelle et l'excellence en gestion au sein de l'administration publique centrale. En utilisant une vaste écosystème de produits d'apprentissage, les méthodes de prestation, et une plateforme d'apprentissage en ligne, l'École offre aux fonctionnaires les connaissances fondamentales, des habiletés et des compétences maintenant dans l'avenir, à servir les Canadiens avec excellence.

### Canadian Centre for Occupational Health and Safety

EN — `institutions_infosource_docs/ati-schedule-i-canadian-centre-for-occupational-health-and-safety/classes_of_records_en.md:773` — Background

The Canadian Centre for Occupational Health and Safety (CCOHS) is a federal departmental
corporation under Schedule II of the[*Financial Administration Act*](https://laws-lois.justice.gc.ca/eng/acts/f-11/) and reports to Parliament through the Minister of Labour and Seniors.

CCOHS operates under the legislative authority of the
[*Canadian Centre for Occupational Health and
Safety Act S.C., 1977-78, c. 29*](https://laws-lois.justice.gc.ca/eng/acts/c-13/) which was passed by unanimous vote in the Canadian Parliament.

If you would like more information on the background of CCOHS please see [About
CCOHS](/ccohs.html).

EN — `institutions_infosource_docs/ati-schedule-i-canadian-centre-for-occupational-health-and-safety/classes_of_records_en.md:785` — Responsibilities

As Canada’s national occupational health and safety resource, CCOHS is dedicated to the advancement
of workplace health
and safety. It does this by providing information and knowledge transfer services; education and
online courses;
cost-effective tools for improving occupational health and safety performance; management systems
services supporting
health and safety programs; injury and illness prevention initiatives and promoting the total
well-being – physical,
psychosocial and mental health – of working people.

CCOHS is a recognized leader in providing effective programs, products and services, which are based
on the Centre’s
core knowledge, collection of occupational health and safety information, and application of
information management
technologies.

CCOHS is governed by a tripartite council representing governments (federal, provincial and territorial), employers, and labour organizations.
The Council of Governors assists in overseeing a policy framework for a trustworthy and complete
occupational health and safety service that reflects the joint perspectives of government, labour and
employers. Council members are directly involved in the policy, governance and strategic planning for the organization.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-centre-for-occupational-health-and-safety/classes_of_records_fr.md:774` — Contexte

Le Centre canadien d’hygiène et de sécurité au travail (CCHST) est un organisme du gouvernement fédéral au titre de l’ Annexe II de la
[Loi sur la gestion des finances publiques](https://laws-lois.justice.gc.ca/fra/lois/f-11/page-21.html#h-224729)
et il rend compte au Parlement du Canada, par l’entremise du Ministre du Travail et des Aînés.

Le CCHST est régi par la
[*Loi sur le Centre canadien d’hygiène et de sécurité au travail*](https://laws-lois.justice.gc.ca/fra/lois/c-13/)
(L.R.C. 1977-1978, chap. 29), qui a été adoptée à l’unanimité par le Parlement du Canada.

Pour obtenir de plus amples renseignements sur le CCHST, veuillez consulter la rubrique [Ce que fait le CCHST](/ccohs.html).

FR — `institutions_infosource_docs/ati-schedule-i-canadian-centre-for-occupational-health-and-safety/classes_of_records_fr.md:786` — Responsabilités

En tant que ressource nationale du Canada en matière de santé et de sécurité au travail, le CCHST se consacre à l’avancement de la santé et de
la sécurité au travail. Pour ce faire, il fournit : des services de transfert de l’information et du savoir, de l’éducation et des cours en
ligne, des outils rentables permettant d’améliorer le rendement en matière de santé et de sécurité au travail, des systèmes de gestion
appuyant les programmes de santé et de sécurité, des initiatives visant la prévention des blessures et des maladies. Il fait aussi la
promotion du mieux-être global – c’est-à-dire de la santé physique, psychologique et mentale – des travailleurs.

Le CCHST est un chef de file reconnu dans la prestation de programmes, de produits et de services efficaces, qui reposent sur son corpus de
connaissances bâti au fil du temps, sur sa collection d’information en santé et en sécurité au travail et sur la mise en application des
technologies de gestion de l’information.

Le CCHST est administré par un conseil tripartite qui représente les gouvernements (fédéral, provinciaux et territoriaux), les employeurs et
les associations syndicales. Le conseil des gouverneurs du CCHST contribue à la supervision d’un cadre stratégique pour la prestation de
services fiables et complets de santé et de sécurité au travail qui reflète les perspectives des gouvernements, des syndicats et des
employeurs. Les membres du conseil prennent part à la gouvernance et à la planification stratégique de l’organisation.

### Canadian Food Inspection Agency

EN — `institutions_infosource_docs/ati-schedule-i-canadian-food-inspection-agency/classes_of_records_en.md:63` — Background

The Canadian Food Inspection Agency's (CFIA) plans and priorities link directly to the Government of Canada's priorities for safeguarding the food supply, bolstering economic prosperity, strengthening security at the border, protecting the environment and contributing to the health of Canadians.

The CFIA is one of Canada's largest science-based regulatory agencies. The agency's vision is to excel as a science-based regulator, trusted and respected by Canadians and the international community. The CFIA's mission is to safeguard food, animals and plants, which enhances the health and well-being of Canada's people, environment and economy. Learn more about the CFIA's [mandate](/en/about-cfia/organizational-structure/mandate).

The CFIA has more than 6,000 professionals working across Canada in the National Capital Region and in 4 operational regions — Atlantic, Quebec, Ontario and Western. Every day, the agency's employees help to safeguard plant and animal health, prevent food safety hazards, manage food safety investigations and recalls, and protect the marketplace from unfair practices.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-food-inspection-agency/classes_of_records_en.md:75` — Responsibilities

The CFIA bases its activities on science, effective risk management, commitment to service and efficiency, and collaboration with domestic and international organizations that share its objectives.

The CFIA is responsible for administering and enforcing 10 federal statutes and 22 regulations that govern the safety and labelling of food sold in Canada and support a sustainable plant and animal resource base.

The CFIA shares many areas of responsibility with other federal departments and agencies, provincial, territorial and municipal authorities, and other stakeholders. Within this complex operating environment, the agency works with its partners to implement food safety measures, manage food, animal and plant risks and emergencies, and promote the development of food safety and disease control systems to maintain the safety of Canada's high-quality agriculture, agri-food, aquaculture and fishery products. The agency's activities include: verifying the compliance of imported products; registering and inspecting establishments; testing food, animals and plants, and their related products; and approving the use of many agricultural inputs. The agency also provides scientific advice, develops new technologies, provides testing services and conducts regulatory research.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-food-inspection-agency/classes_of_records_fr.md:60` — Contexte

Les plans et priorités de l'Agence canadienne d'inspection des aliments (ACIA) se rapportent directement aux priorités du gouvernement du Canada, soit renforcer la salubrité de l'approvisionnement alimentaire, soutenir la prospérité économique, consolider la sécurité à la frontière, protéger l'environnement et contribuer à la bonne santé des Canadiens.

L'ACIA est l'un des plus grands organismes de réglementation à vocation scientifique du Canada. L'agence a pour vision d'exceller en tant qu'organisme de réglementation à vocation scientifique, fiable respecté des Canadiens et de la communauté internationale. La mission de l'ACIA consiste à veiller à la santé et au bien-être des Canadiens, à l'environnement et à l'économie en préservant la salubrité des aliments, la santé des animaux et la protection des végétaux. En savoir plus sur le [mandat](/fr/propos-lacia/structure-organisationnelle/mandat) de l'ACIA.

L'agence compte plus de 6 000 professionnels à l'échelle du Canada, soit dans la région de la capitale nationale (RCN) et dans ses 4 centres opérationnels (Atlantique, Québec, Ontario et Ouest). Chaque jour, ces employés aident à préserver la santé des animaux et des végétaux, à prévenir les risques associés à la salubrité des aliments, à gérer les enquêtes sur la salubrité des aliments ainsi que les rappels et à protéger les marchés des pratiques déloyales.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-food-inspection-agency/classes_of_records_fr.md:72` — Responsabilités

L'ACIA élabore des exigences législatives et dispense des services d'inspection et autres pour :

Les activités de l'ACIA sont fondées sur des principes scientifiques, la gestion efficace des risques, l'engagement à l'égard de la prestation des services et de l'efficacité, ainsi que la collaboration avec des organismes nationaux et internationaux investis du même mandat.

L'ACIA est chargée d'administrer et d'appliquer 10 lois fédérales et 22 règlements qui régissent la salubrité et l'étiquetage des aliments vendus au Canada, et qui contribuent au maintien des ressources végétales et animales.

### Canadian Forces

EN — `institutions_infosource_docs/ati-schedule-i-canadian-forces/classes_of_records_en.md:116` — Background

In most respects, DND is an organization like other departments of government. It was established in 1923 by the [*National Defence Act*](http://laws-lois.justice.gc.ca/eng/acts/N-5/), which sets out the Minister's responsibilities, including the Minister's responsibility for the Department and the CAF. Under the *Act*, the CAF are an entity separate and distinct from the Department.

The Governor General of Canada is the Commander-in-Chief of Canada. DND reports to parliament via the [Minister of National Defence](/en/government/ministers/bill-blair.html). The [Deputy Minister of National Defence](/en/department-national-defence/corporate/organizational-structure/deputy-minister-national-defence.html) is the Department's senior civil servant and the CAF are headed by the [Chief of the Defence Staff](/en/department-national-defence/corporate/organizational-structure/chief-defence-staff.html).

On behalf of the people of Canada, the Canadian Armed Forces (CAF), with the support of the Department of National Defence (DND), stand ready to perform three key roles:

EN — `institutions_infosource_docs/ati-schedule-i-canadian-forces/classes_of_records_en.md:132` — Responsibilities

The Defence mission is to defend Canada and Canadian interests and values while contributing to international peace and security.

The Canadian Armed Forces and the Department of National Defence have complementary roles to play in providing advice and support to the Minister of National Defence and in implementing the decisions of the Government on the defence of Canada and of Canadian interests at home and abroad. The separate authorities of the Deputy Minister and the Chief of the Defence Staff give rise to different responsibilities.

View the [Departmental Organizational Structure](/en/department-national-defence/corporate/organizational-structure.html) here.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-forces/classes_of_records_fr.md:116` — Historique

À bien des égards, le ministère de la Défense nationale s'apparente aux autres ministères. Il a été créé en 1923 en vertu de la [*Loi sur la défense nationale*](http://laws-lois.justice.gc.ca/fra/lois/N-5/), qui énonce les responsabilités du Ministre et qui rend ce dernier responsable notamment du ministère et des Forces armées canadiennes. En vertu de la *Loi*, les FAC sont une entité séparée et distincte du ministère.

Le gouverneur général du Canada est le commandant en chef du Canada. Le MDN relève du Parlement par l'intermédiaire du [ministre de la Défense nationale](/fr/gouvernement/ministres/bill-blair.html). Le [sous-ministre de la Défense nationale](/fr/ministere-defense-nationale/organisation/structure-organisationnelle/sous-ministre-defense-nationale.html) est le plus haut fonctionnaire du Ministère. Les FAC sont sous les ordres du [chef d'état-major de la Défense](/fr/ministere-defense-nationale/organisation/structure-organisationnelle/chef-etat-major-defense.html).

Au nom de la population canadienne, les Forces armées canadiennes (FAC), avec l'appui du ministère de la Défense nationale (MDN), sont prêtes à exécuter trois rôles essentiels :

FR — `institutions_infosource_docs/ati-schedule-i-canadian-forces/classes_of_records_fr.md:132` — Responsabilités

La mission de la Défense consiste à défendre le Canada, ses intérêts et ses valeurs, tout en contribuant à la paix et à la sécurité internationales.

Les Forces armées canadiennes et le ministère de la Défense nationale ont des rôles complémentaires à jouer pour conseiller et appuyer le ministre de la Défense nationale et appliquer les décisions du gouvernement qui intéressent la défense du Canada et les intérêts du Canada au pays et à l'étranger. Les pouvoirs distincts du sous-ministre et du Chef d'état-major de la Défense mettent en évidence des responsabilités différentes.

Voir la [Structure organisationnelle du ministère](/fr/ministere-defense-nationale/organisation/structure-organisationnelle.html) ici.

### Canadian Grain Commission

EN — `institutions_infosource_docs/ati-schedule-i-canadian-grain-commission/classes_of_records_en.md:27` — Background

The Canadian Grain Commission was established in 1912 and is the federal government department responsible for administering the provisions of the [*Canada Grain Act*](http://laws-lois.justice.gc.ca/eng/acts/G-10/index.html).

The CGC reports to Parliament through the Minister of Agriculture and Agri-Food (AAF) and is led by a three-member Commission consisting of a Chief Commissioner, an Assistant Chief Commissioner, and a Commissioner.

In accordance with the *Canada Grain Act*, the Canadian Grain Commission establishes and maintains standards of quality for Canadian grain and regulates grain handling in Canada to ensure a valuable and dependable commodity for domestic and export markets. The Canadian Grain Commission is the official certifier of Canadian grain export shipments and is mandated to undertake, sponsor, and promote research related to grain and grain products.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-grain-commission/classes_of_records_en.md:37` — Responsibilities

The Canadian Grain Commission is a federal government department which administers the provisions of the *Canada Grain Act*. The Canadian Grain Commission’s mandate, as set out in the Act, is to, “in the interests of the grain producers, establish and maintain standards of quality for Canadian grain and regulate grain handling in Canada, to ensure a dependable commodity for domestic and export markets.” Its vision is: “to be a world class, science-based quality assurance provider”. The Minister of Agriculture and Agri-Food is responsible for the Canadian Grain Commission.

The Canadian Grain Commission’s Core Responsibility is Grain Regulation, or, to regulate grain handling in Canada and to establish and maintain science based standards for Canadian grain. The commission regulates the handling of 20 grains[Footnote1](#fn1) grown in Canada to protect producer rights and ensure the integrity of grain transactions.

The Departmental Results of this Core Responsibility are that domestic and international markets regard Canadian grain as dependable and safe and that farmers are fairly compensated for their grain. The Canadian Grain Commission supports its Core Responsibility through its programs: Grain Quality, Grain Research, and Safeguards for Grain Farmers.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-grain-commission/classes_of_records_fr.md:27` — Contexte

Créée en 1912, la Commission canadienne des grains est l’organisme fédéral responsable de l’administration des dispositions de la [*Loi sur les grains du Canada*](http://laws-lois.justice.gc.ca/fra/lois/G-10/index.html).

Relevant du Parlement, par l’entremise du ministre de l’Agriculture et de l’Agroalimentaire, la Commission canadienne des grains est dirigée par une commission composée de trois membres, soit un commissaire en chef, un commissaire en chef adjoint et un commissaire.

Conformément à la *Loi sur les grains du Canada*, la Commission canadienne des grains établit et maintient des normes de qualité pour le grain canadien et régit la manutention des grains au Canada pour garantir un produit fiable pour les marchés intérieurs et d’exportation. En tant qu’organisme officiel de certification des exportations de grain canadien, la Commission canadienne des grains a le mandat d’entreprendre, de parrainer et de promouvoir des travaux de recherche sur les grains et les produits céréaliers.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-grain-commission/classes_of_records_fr.md:37` — Responsabilités

Conformément à la *Loi sur les grains du Canada*, la Commission canadienne des grains a pour mission « de fixer et de faire respecter, au profit des producteurs de grain, des normes de qualité pour le grain canadien et de régir la manutention des grains au pays afin d’en assurer la fiabilité sur les marchés intérieur et extérieur ». Sa vision est la suivante : « être un fournisseur de classe mondiale en matière de services d’assurance de la qualité fondés sur la science ».

La réglementation du grain, soit la réglementation de la manutention du grain au Canada ainsi que l’établissement et le maintien de normes fondées sur la science pour le grain canadien, est la responsabilité essentielle de la Commission canadienne des grains. Elle régit la manutention de 21 grains[Note de bas de page1](#fn1) cultivés au Canada pour protéger les droits des producteurs et assurer l’intégrité des transactions de grain.

Comme la réglementation du grain est la responsabilité essentielle de la Commission canadienne des grains, il en résulte pour le Ministère que les marchés canadien et internationaux estiment que le grain canadien est fiable et salubre et que les producteurs sont dûment rémunérés pour leur grain. La Commission canadienne des grains appuie cette responsabilité essentielle par l’entremise des programmes Suivants : Qualité des grains, Recherche sur les grains et Mesures de protection des producteurs de grain.

### Canadian Heritage

EN — `institutions_infosource_docs/ati-schedule-i-department-of-canadian-heritage/classes_of_records_en.md:102` — Background

The [Department of Canadian Heritage](/en/canadian-heritage.html) was created on June 25, 1993. The [Department of Canadian Heritage Act](https://laws-lois.justice.gc.ca/eng/acts/C-17.3/FullText.html) establishing the Department of Canadian Heritage and amending or repealing certain other associated acts was proclaimed on June 12, 1996.

The Minister of Canadian Heritage is accountable to Parliament for the Department and the 18 other organizations that make up the [Canadian Heritage portfolio](/en/canadian-heritage/corporate/portfolio-organizations.html).

EN — `institutions_infosource_docs/ati-schedule-i-department-of-canadian-heritage/classes_of_records_en.md:108` — Responsibilities

The Department of Canadian Heritage is responsible for formulating and implementing cultural policies related to copyright, foreign investment and broadcasting, as well as policies related to arts, heritage, official languages, sports, state ceremonial and protocol, and Canadian symbols. The Department's main activities involve funding community and other third-party organizations to promote the benefits of culture, identity, and sport for Canadians.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-canadian-heritage/classes_of_records_fr.md:102` — Historique

Le [ministère du Patrimoine canadien](/fr/patrimoine-canadien.html) a été créé le 25 juin 1993. La [Loi sur le ministère du Patrimoine canadien](http://laws-lois.justice.gc.ca/fra/lois/C-17.3/TexteComplet.html) constituant le ministère du Patrimoine canadien et modifiant ou abrogeant certaines lois connexes a été promulguée le 12 juin 1996.

Le ministre du Patrimoine canadien est responsable devant le Parlement des activités du Ministère et des 18 autres organismes qui composent son [portefeuille](/fr/patrimoine-canadien/organisation/organismes-portefeuille.html).

FR — `institutions_infosource_docs/ati-schedule-i-department-of-canadian-heritage/classes_of_records_fr.md:108` — Responsabilités

Plus précisément, le ministère du Patrimoine canadien est responsable de formuler et de mettre en œuvre des politiques culturelles liées au droit d'auteur, aux investissements étrangers et à la radiodiffusion, ainsi que des politiques relatives aux arts, au patrimoine, aux langues officielles, au sport, au cérémonial d'État et au protocole, et aux symboles canadiens. Les principales activités du Ministère visent à financer des organismes communautaires et d'autres organismes externes afin de promouvoir les avantages de la culture, de l'identité et du sport auprès de la population canadienne.

### Canadian Museum for Human Rights

EN — `institutions_infosource_docs/ati-schedule-i-canadian-museum-for-human-rights/classes_of_records_en.md:135` — Background

The Canadian Museum for Human Rights (CMHR) was established by Parliament through amendments to the Museums Act which came into force on August 10, 2008. It is a distinct legal entity, wholly‐owned by the Crown, which operates at arm's length from the Government in its day to day operations, activities and programming. The Museum is governed by the regime for Crown Corporation control and accountability established under Part X of the Financial Administration Act. It is a member of the Canadian Heritage Portfolio and reports to Parliament through the Minister of Canadian Heritage and Official Languages.

The Museum's Board of Trustees serves as its governing body and is accountable to Parliament for the stewardship of the Museum through the Minister of Canadian Heritage and Official Languages. The Board represents various regions of the country and is appointed by the Governor in Council.

The CMHR plays an essential role in: preserving and promoting our heritage at home and abroad; contributing to the collective memory and sense of identity of all Canadians; and inspiring research, learning, and entertainment that belong to all Canadians.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-museum-for-human-rights/classes_of_records_en.md:143` — Responsibilities

The purpose of the CMHR is to explore the subject of human rights, with special but not exclusive reference to Canada, in order to enhance the public's understanding of human rights, to promote respect for others and to encourage reflection and dialogue.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-museum-for-human-rights/classes_of_records_fr.md:135` — Historique

Le Musée canadien pour les droits de la personne (MCDP) a été constitué par le Parlement en vertu d'amendements à la Loi sur les musées, entrant en vigueur le 10 août 2008. Le Musée est une entité juridique distincte appartenant entièrement à l'État, qui fonctionne de façon indépendante du gouvernement dans ses opérations journalières, ses activités et sa programmation. Le Musée est gouverné par le régime de contrôle et de responsabilité des sociétés d'État, créé en vertu de la Partie X de la Loi sur la gestion des finances publiques. Le Musée fait partie du portefeuille du Patrimoine canadien et rend des comptes au Parlement par l'entremise du ministre du Patrimoine canadien.

Le conseil d'administration du Musée canadien pour les droits de la personne est son instance dirigeante et il est responsable envers le Parlement de l'administration du Musée par l'entremise du ministre du Patrimoine canadien. Le conseil d'administration représente toutes les régions du pays, et ses membres sont nommés par le gouverneur en conseil.

Le Musée joue un rôle essentiel pour : préserver et faire connaître le patrimoine canadien au Canada et à l'étranger; contribuer à la mémoire collective et au sentiment d'identité de tous les Canadiens et de toutes les Canadiennes; et influencer la recherche, l'apprentissage et le divertissement qui appartiennent à toute la population canadienne.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-museum-for-human-rights/classes_of_records_fr.md:143` — Responsabilités

Le mandat du Musée et d'étudier le thème pour les droits de la personne en mettant un accent particulier, mais non exclusif, sur le Canada, dans le but d'accroître la compréhension qu'a le public pour les droits de la personne, de promouvoir le respect des autres et de favoriser la réflexion et le dialogue.

### Canadian Radio-television and Telecommunications Commission

EN — `institutions_infosource_docs/ati-schedule-i-canadian-radio-television-and-telecommunications-commission/classes_of_records_en.md:73` — Background

The [Canadian Radio-television and Telecommunications Commission (CRTC)](/eng/home-accueil.htm) was established to sustain and promote Canadian culture and to achieve key social and economic objectives. The CRTC fulfills this mandate by regulating and supervising Canadian broadcasting and telecommunications in the public interest. The CRTC is governed by the [Broadcasting Act](http://laws-lois.justice.gc.ca/eng/acts/B-9.01/)of 1991 and the [Telecommunications Act](http://laws-lois.justice.gc.ca/eng/acts/t-3.4/)of 1993.

Since 1928, when the Government of Canada created the first Royal Commission on Broadcasting, the government has sought to develop policies to keep pace with changing technology.

Today, the CRTC is an independent public authority and reports to Parliament through the Minister of [Canadian Heritage](http://www.pch.gc.ca/eng/1266237377392/1266193946168).

EN — `institutions_infosource_docs/ati-schedule-i-canadian-radio-television-and-telecommunications-commission/classes_of_records_en.md:81` — Responsibilities

The Canadian Radio-television and Telecommunications Commission (CRTC) is an independent public organization that regulates and supervises the Canadian broadcasting and telecommunications systems.

The CRTC does not regulate newspapers, magazines, cell phone rates, the quality of service and business practices of cell phone companies, or the quality and content of TV and radio programs.

As an independent organization, the CRTC works to serve the needs and interests of citizens, industries, interest groups and the government

FR — `institutions_infosource_docs/ati-schedule-i-canadian-radio-television-and-telecommunications-commission/classes_of_records_fr.md:71` — Historique

Le [Conseil de la radiodiffusion et des télécommunications canadiennes (CRTC](https://crtc.gc.ca/fra/accueil-home.htm)) a été constitué en vue de soutenir et de promouvoir la culture canadienne et d'atteindre des objectifs sociaux et économiques fondamentaux. Régi par la *[Loi sur la radiodiffusion](https://laws-lois.justice.gc.ca/fra/lois/B-9.01/)* de 1991 et la *[Loi sur les télécommunications](https://laws-lois.justice.gc.ca/fra/lois/T-3.4/)* de 1993, le CRTC s’acquitte de son mandat en réglementant et en surveillant les industries canadiennes de la radiodiffusion et des télécommunications dans l'intérêt public.
Depuis la création de la première Commission royale sur la radiodiffusion en 1928, le gouvernement du Canada s’emploie sans cesse à élaborer des politiques qui sont adaptées à l'évolution de la technologie.
Le CRTC est maintenant un organisme public autonome relevant du Parlement par l'intermédiaire du ministre du [Patrimoine canadien](http://www.pch.gc.ca/fra/1266037002102/1265993639778).

FR — `institutions_infosource_docs/ati-schedule-i-canadian-radio-television-and-telecommunications-commission/classes_of_records_fr.md:77` — Responsabilités

Le Conseil de la radiodiffusion et des télécommunications canadiennes (CRTC) est un organisme public indépendant qui réglemente et surveille les systèmes canadiens de la radiodiffusion et des télécommunications.
Il ne réglemente pas les journaux, les magazines, les tarifs de la téléphonie cellulaire, la qualité du service et des pratiques commerciales des entreprises de téléphonie cellulaire, ni la qualité et le contenu des émissions de radio et de télévision.
En tant qu’organisme indépendant, le CRTC vise à répondre aux besoins et aux intérêts des citoyens, des industries, des groupes d’intérêts et du gouvernement.

### Canadian Security Intelligence Service

EN — `institutions_infosource_docs/ati-schedule-i-canadian-security-intelligence-service/classes_of_records_en.md:59` — Background

The Canadian Security Intelligence Service reports to Parliament through the Minster of Public Safety.

To better understand CSIS, watch this [video](https://www.youtube.com/watch?v=XbfrSTf4aNY) and read about its [legislative foundation](https://www.canada.ca/en/security-intelligence-service/corporate/legislation.html).

EN — `institutions_infosource_docs/ati-schedule-i-canadian-security-intelligence-service/classes_of_records_en.md:65` — Responsibilities

Read about the CSIS [mandate](https://www.canada.ca/en/security-intelligence-service/corporate/mandate.html) and responsibilities.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-security-intelligence-service/classes_of_records_fr.md:61` — Historique

Le Service canadien du renseignement de sécurité rend compte au Parlement par l’entremise du ministre de la Sécurité publique.

Pour avoir une meilleur compréhension du SCRS, regardez ce [vidéo](https://www.youtube.com/watch?v=5rnANG2lZbc) et lisez son [fondement législatif](https://www.canada.ca/fr/service-renseignement-securite/organisation/la-legislation.html).

FR — `institutions_infosource_docs/ati-schedule-i-canadian-security-intelligence-service/classes_of_records_fr.md:67` — Responsabilités

Lisez le [mandat](https://www.canada.ca/fr/service-renseignement-securite/organisation/mandat.html) du SCRS ainsi que les responsabilitées de ses programmes.

### Canadian Space Agency

EN — `institutions_infosource_docs/ati-schedule-i-canadian-space-agency/classes_of_records_en.md:79` — Background

Established in March 1989, the Canadian Space Agency (CSA) is an independent federal agency responsible for managing all of Canada's civil space-related activities. The objects and functions of the CSA are set out in the [*Canadian Space Agency Act,* S.C. 1990, c. 13](http://laws-lois.justice.gc.ca/eng/acts/C-23.2/FullText.html). The CSA was created from divisions of the former Ministry of State for Science and Technology (MOSST), the National Research Council of Canada (NRC), the Department of Communications (DOC) and Energy Mines and Resources (EMR). The CSA reports to Parliament through the Minister of Innovation, Science and Economic development Canada.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-space-agency/classes_of_records_en.md:85` — Responsibilities

The [mandate](/eng/about/mission.asp) of the Canadian Space Agency is to promote the peaceful use and development of space, to advance the knowledge of space through science and to ensure that space science and technology provide social and economic benefits for Canadians. The CSA is achieving this mandate in collaboration with Canadian industry, academia, Government of Canada (GoC) organizations, and other international space agencies or organizations. Such partnering maximizes the economic, scientific, and technological benefits and enhances synergies between institutions across the country and with other nations. The founding legislation voted in 1990 attributed four main functions to the CSA: Assisting the Minister in the coordination of the space policies and programs; Planning and implementing programs and projects related to scientific or industrial space research and development, and application of space technology; Promoting the transfer and diffusion of space technology to and throughout Canadian industry; and, Encouraging commercial exploitation of space capabilities, technology, facilities and systems.

The [CSA's Space Strategy for Canada](/eng/publications/space-strategy-for-canada/) highlights the role that science and research play in our space pursuits. Canada's space scientists are world-renowned and experts in many disciplines, including astronomy, atmospheric, Earth systems, planetary, solar-terrestrial, and space life sciences. Canadian scientists are helping further humanity's understanding of the causes of climate change, the effects of pollution on our environment, and the origins of the universe. Canada's participation in national and international missions has afforded our space scientists the chance to share in discovery opportunities and to deepen our understanding of our world and our universe.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-space-agency/classes_of_records_fr.md:79` — Contexte

Créée en mars 1989, l'Agence spatiale canadienne (ASC) est un organisme fédéral indépendant chargé de gérer tous les volets civils des activités du Canada dans l'espace. La mission et les fonctions de l'ASC sont définies dans la [*Loi sur l'Agence spatiale canadienne*](https://laws-lois.justice.gc.ca/fra/lois/c-23.2/TexteComplet.html) (L.C. 1990, ch. 13). L'ASC a été créée à la suite du regroupement de divisions de l'ancien ministère d'État chargé des Sciences et de la Technologie, du Conseil national de recherches du Canada, du ministère des Communications et du ministère de l'Énergie, des Mines et des Ressources. L'ASC rend compte au Parlement par l'entremise du ministre de l'Innovation, des Sciences et du Développement économique du Canada.

Pour en savoir plus sur [l'histoire de l'ASC](/fra/a-propos/asc-organisation.asp), consulter le site Web.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-space-agency/classes_of_records_fr.md:85` — Responsabilités

L'ASC a pour [mandat](/fra/a-propos/mission.asp) de promouvoir l'exploitation et l'usage pacifiques de l'espace, de faire progresser la connaissance de l'espace au moyen de la science et de faire en sorte que les Canadiens tirent profit des sciences et techniques spatiales sur les plans tant social qu'économique. L'ASC s'acquitte de son mandat en collaboration avec le secteur privé, le milieu universitaire, des organismes du gouvernement du Canada (GC) et d'autres agences spatiales et organisations internationales. Ces partenariats maximisent les avantages économiques, scientifiques et technologiques et renforcent les synergies entre les organisations de partout au Canada et avec d'autres pays. La loi habilitante adoptée en 1990 attribue quatre fonctions principales à l'ASC : assister le ministre pour la coordination de la politique et des programmes du gouvernement canadien en matière spatiale; concevoir, réaliser, diriger et gérer des programmes et travaux liés à des activités scientifiques et industrielles de recherche et développement dans le domaine spatial et à l'application des techniques spatiales; promouvoir la diffusion et le transfert des techniques spatiales au profit de l'industrie canadienne; et encourager l'exploitation commerciale du potentiel offert par l'espace, des techniques et installations spatiales et des systèmes spatiaux.

La [Stratégie spatiale pour le Canada](/fra/publications/strategie-spatiale-pour-le-canada/) de l'ASC met l'accent sur le rôle que jouent la science et la recherche dans les projets spatiaux. Les spécialistes canadiens en sciences spatiales sont réputés mondialement et sont des experts dans de nombreux domaines, notamment l'astronomie, les sciences atmosphériques et du système terrestre, les sciences planétaires et l'étude du système Soleil‑Terre, ainsi que les sciences de la vie dans l'espace. Les scientifiques canadiens aident à faire avancer les connaissances de l'humanité sur les causes des changements climatiques, les effets de la pollution sur l'environnement et l'origine de l'Univers. La participation du Canada à des missions nationales et internationales a permis aux scientifiques du secteur spatial canadien de saisir des occasions de faire des découvertes et d'approfondir notre compréhension de notre monde et de l'Univers.

### Canadian Transportation Agency

EN — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-agency/classes_of_records_en.md:48` — Background

The Canadian Transportation Agency (the Agency) is an independent, quasi-judicial tribunal and economic regulator responsible for making decisions and determinations on a wide range of matters involving air, rail and marine modes of transportation under the authority of Parliament, as set out in the *Canada Transportation Act* (S.C. 1996, c. 10) as amended and other legislation.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-agency/classes_of_records_en.md:57` — Responsibilities

The Agency supports the goal of a competitive and accessible national transportation system that fulfills the needs of Canadians and the Canadian economy.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-agency/classes_of_records_fr.md:48` — Historique

L'Office des transports du Canada (Office) est un tribunal quasi judiciaire indépendant et un organisme de réglementation économique. Il est chargé de prendre des décisions sur un vaste éventail de questions au sujet des modes de transport aérien, ferroviaire et maritime relevant de l'autorité du Parlement, comme le prévoit la *Loi sur les transports au Canada* (L.C. 1996, ch. 10), modifiée, et d'autres textes législatifs.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-agency/classes_of_records_fr.md:57` — Responsabilités

L'Office appuie l'objectif d'un réseau de transport national concurrentiel et accessible qui répond aux besoins des Canadiens et de l'économie canadienne.
Pour en savoir plus sur ses responsabilités :

### College of Patent Agents and Trademark Agents

EN — `institutions_infosource_docs/ati-schedule-i-college-of-patent-agents-and-trademark-agents/classes_of_records_en.md:258` — Background

The Government of Canada enacted the College of Patent Agents and Trademark Agents Act (the *CPATA Act*) as part of the National Innovation Strategy. On June 28, 2021, the *CPATA Act* came into force and responsibility for licensure was officially transferred to CPATA.

CPATA reports to Parliament through the Minister of Innovation, Science and Economic Development.

EN — `institutions_infosource_docs/ati-schedule-i-college-of-patent-agents-and-trademark-agents/classes_of_records_en.md:267` — Responsibilities

As an independent regulator, CPATA protects the public interest by strengthening the competencies of patent agents and trademark agents, and building confidence in accessible, ethical and expert intellectual property services in Canada. Our commitment to supporting the rigour and sophistication of the profession plays an important part in driving innovation and stimulating Canada’s economic growth.

In accordance with the *CPATA Act*, Regulations, By-laws and Regulatory Objectives, the College is responsible for protecting the public interest by:

FR — `institutions_infosource_docs/ati-schedule-i-college-of-patent-agents-and-trademark-agents/classes_of_records_fr.md:262` — Contexte

Le gouvernement du Canada a promulgué la *Loi sur le Collège des agents de brevets et des agents de marques de commerce* (la *Loi sur le CABAMC*), dans le cadre de la Stratégie nationale d’innovation. Le 28 juin 2021, la *Loi sur le CABAMC* est entrée en vigueur et la responsabilité du permis d’exercice a été officiellement transférée au CABAMC.

Le CABAMC rend compte au Parlement par l’entremise du ministre de l’Innovation, des Sciences et du Développement économique.

FR — `institutions_infosource_docs/ati-schedule-i-college-of-patent-agents-and-trademark-agents/classes_of_records_fr.md:271` — Responsabilités

En tant qu’organisme de réglementation indépendant, le CABAMC protège l’intérêt public en renforçant les compétences des agent(e)s de brevets et des agent(e)s de marques de commerce et en bâtissant la confiance dans des services de propriété intellectuelle accessibles, éthiques et spécialisés au Canada. En favorisant la rigueur et la spécialisation dans la profession, nous jouons un rôle moteur dans la propulsion de l’innovation et la stimulation de la croissance économique au Canada.

### Communications Security Establishment Canada

EN — `institutions_infosource_docs/ati-schedule-i-communications-security-establishment/classes_of_records_en.md:69` — Background

The Communications Security Establishment reports to Parliament through the Minister of National Defence.

Read about CSE, including its [History](/en/culture-and-community/history), [Legislation](/en/accountability/governance), and [Accountabilities](/en/accountability).

FR — `institutions_infosource_docs/ati-schedule-i-communications-security-establishment/classes_of_records_fr.md:69` — Contexte

Le Centre de la sécurité des télécommunications relève du Parlement par l’entremise du ministre de la Défense nationale.

Renseignez-vous au sujet du CST, y compris de son [histoire](/fr/culture-et-communaute/histoire), [de la loi qui le régit](/fr/reddition-comptes/gouvernance) et de ses mécanismes de [reddition de comptes](/fr/reddition-comptes).

FR — `institutions_infosource_docs/ati-schedule-i-communications-security-establishment/classes_of_records_fr.md:75` — Responsabilités

Renseignez-vous au sujet [du mandat et des responsabilités](/fr/renseignements-organisationnels/mandat) du CST.

### Correctional Service Canada

EN — `institutions_infosource_docs/ati-schedule-i-correctional-service-of-canada/classes_of_records_en.md:83` — Background

Correctional Service Canada (CSC) was formed in 1979 through the amalgamation of the Canadian Penitentiary Service and the Parole Board of Canada.  Learn more about CSC’s [history](/en/correctional-service/corporate/history-csc.html) and background.

CSC is an agency within the Public Safety Portfolio. The Portfolio brings together key federal agencies dedicated to public safety, including:

CSC has the fundamental obligation to contribute to public safety by actively encouraging and assisting offenders to become law-abiding citizens, while exercising reasonable, safe, secure and humane control. It does this by operating under the rule of law, in particular, the *Corrections and Conditional Release Act* (the CCRA), which provides its legislative framework. The Commissioner of CSC has the authority, extending from the *CCRA*, to issue directives, procedures and guidelines to carry out the agency’s operations.

EN — `institutions_infosource_docs/ati-schedule-i-correctional-service-of-canada/classes_of_records_en.md:101` — Responsibilities

CSC contributes to public safety by administering court-imposed sentences for offenders sentenced to two years or more. This involves managing institutions (penitentiaries) of various security levels and supervising offenders on different forms of conditional release, while assisting them to become law-abiding citizens. CSC also administers post-sentence supervision of offenders with Long Term Supervision Orders for up to 10 years.

CSC provides services across the country, from large urban centres with their increasingly diverse populations, to remote Inuit communities across the North. CSC manages:

In addition, CSC has five regional headquarters that provide management and administrative support and serve as the delivery arm of CSC's programs and services. CSC also manages:

FR — `institutions_infosource_docs/ati-schedule-i-correctional-service-of-canada/classes_of_records_fr.md:83` — Contexte

Le Service correctionnel Canada (SCC) a été formé en 1979 par la fusion du Service canadien des pénitenciers et du Service national de libération conditionnelle. Pour en savoir plus sur [l'historique](/fr/service-correctionnel/organisation/histoire-scc.html) et l'arrière-plan du SCC.

Le SCC est un organisme du Portefeuille de la sécurité publique. Le Portefeuille réunit des organismes fédéraux clés qui s'occupent de la sécurité publique, notamment :

Le Service correctionnel du Canada se rapporte au Parlement par l'intermédiaire du ministre de la Sécurité publique.

FR — `institutions_infosource_docs/ati-schedule-i-correctional-service-of-canada/classes_of_records_fr.md:101` — Responsabilités

Le SCC contribue à la sécurité publique en administrant les peines d'emprisonnement de deux ans ou plus imposées aux délinquants par les tribunaux. Cette responsabilité comprend la gestion des établissements (pénitenciers) de divers niveaux de sécurité et la surveillance des délinquants mis en liberté conditionnelle tout en les aidant à devenir des citoyens respectueux des lois. Le SCC assure également la surveillance postpénale des délinquants visés par une Ordonnance de surveillance de longue durée (OSLD), pouvant aller jusqu'à dix ans.

Le Service fournit des services dans tout le pays tant dans les grands centres urbains aux populations de plus en plus diversifiées que dans les collectivités inuites éloignées du Nord. Le SCC gère :

De plus, le SCC possède cinq administrations régionales qui fournissent des services de soutien administratif et qui gèrent les programmes et services offerts par l'organisation. Le Service gère aussi :

### Crown-Indigenous Relations and Northern Affairs Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs/classes_of_records_en.md:50` — Background

Crown-Indigenous Relations and Northern Affairs Canada (CIRNAC) continues to renew the nation-to-nation, Inuit-Crown, government-to-government relationship between Canada and First Nations, Inuit and Métis; modernize Government of Canada structures to enable Indigenous peoples to build capacity and support their vision of self-determination; and lead the Government of Canada's work in the North.

The Crown-Indigenous Relations and Northern Affairs Canada mandate derives from the Department of Indian Affairs and Northern Development Act, the Indian Act and from a number of recent statutes designed to provide Indigenous peoples with powers beyond the Indian Act, such as the First Nations Land Management Act and the First Nations Jurisdiction Over Education in British Columbia Act; as well as more specific statutes enabling modern treaties and self-government agreements, such as the Maanulth First Nations Final Agreement Act (S.C. 2009, c18) and the Eeyou Marine Region Land Claims Agreement Act (S.C. 2011, c20).

FR — `institutions_infosource_docs/ati-schedule-i-department-of-crown-indigenous-relations-and-northern-affairs/classes_of_records_fr.md:50` — Contexte

Relations Couronne-Autochtones et Affaires du Nord Canada (RCAANC) poursuit ses efforts en vue de renouveler les relations du gouvernement du Canada avec les Premières Nations, les Inuit et les Métis (relations de nation à nation, de gouvernement à gouvernement et entre les Inuit et la Couronne), de moderniser les structures du gouvernement du Canada pour aider les peuples autochtones à renforcer leurs capacités et à concrétiser leur vision de l'autodétermination, et de diriger les activités du gouvernement du Canada dans le Nord.

Le mandat de Relations Couronne-Autochtones et Affaires du Nord Canada s'inspire de la Loi sur le ministère des Affaires indiennes et du Nord canadien, de la Loi sur les Indiens et de certaines lois récentes conférant aux Autochtones des pouvoirs autres que ceux prévus dans la Loi sur les Indiens, comme la Loi sur la gestion des terres des premières nations et la Loi sur la compétence des premières nations en matière d'éducation en Colombie-Britannique. Il s'appuie également sur d'autres lois qui mettent en vigueur des traités modernes et des ententes sur l'autonomie gouvernementale, comme la Loi sur l'Accord définitif concernant les premières nations maanulthes (L.C. 2009, ch. 18) et la Loi sur l'accord sur les revendications territoriales concernant la région marine d'Eeyou (L.C. 2011, ch. 20).

### Department of Finance Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-finance/classes_of_records_en.md:81` — Background

The background of the department can be viewed on the [About Us](https://www.canada.ca/en/department-finance/corporate/mandate.html#a02) page.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-finance/classes_of_records_en.md:85` — Responsibilities

The responsibilities of the department can be viewed on the [About Us](https://www.canada.ca/en/department-finance/corporate/mandate.html#a01) page.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-finance/classes_of_records_fr.md:83` — Historique

L’historique du Ministère est affiché dans la page [Le Ministère](/fr/ministere-finances/organisation/mandat.html#a02)

FR — `institutions_infosource_docs/ati-schedule-i-department-of-finance/classes_of_records_fr.md:87` — Responsabilités

Les responsabilités du Ministère sont affichées dans la page [Le Ministère](/fr/ministere-finances/organisation/mandat.html#a01).

### Federal Economic Development Agency for Northern Ontario

EN — `institutions_infosource_docs/ati-schedule-i-federal-economic-development-agency-for-northern-ontario/classes_of_records_en.md:93` — Background

The Federal Economic Development Agency for Northern Ontario (FedNor) was established on August 12, 2021, to strengthen the economic development of Northern Ontario. The agency was previously positioned as an initiative under Innovation, Science and Economic Development Canada (ISED) and was formed in 1987 to promote economic development in areas of low income and slow economic growth; emphasize long-term economic development and sustainable employment and income creation; and focus on small and medium-sized enterprises (SMEs) and the development of entrepreneurial talent.

FedNor was established as a standalone agency through [Order in Council P.C. 2021-0840](https://orders-in-council.canada.ca/attachment.php?attach=41207&lang=en "https://orders-in-council.canada.ca/attachment.php?attach=41207&lang=en") dated August 6, 2021, and coming into force on August 12, 2021, (1) transferring from the Department of Industry to the Federal Economic Development Agency for Northern Ontario the control and supervision of that portion of the federal public administration in the Department of Industry known as the Federal Economic Development Initiative for Northern Ontario; and (2) ordering the Minister of Economic Development and Official Languages to preside over the Federal Economic Development Agency for Northern Ontario.

Other Orders in Council brought FedNor under relevant legislation, such as the *Public Service Employment Act, Access to Information Act and Privacy Act.*

EN — `institutions_infosource_docs/ati-schedule-i-federal-economic-development-agency-for-northern-ontario/classes_of_records_en.md:107` — Responsibilities

Additional information on FedNor's [mandate](/en/about-us "About us"), its [role](/en/about-us/our-organization "Our Organization"), [and its programs](/en/our-programs "Our programs") is available on the agency's [website](/en/federal-economic-development-agency-northern-ontario "Federal Economic Development Agency for Northern Ontario").

FR — `institutions_infosource_docs/ati-schedule-i-federal-economic-development-agency-for-northern-ontario/classes_of_records_fr.md:93` — Contexte

L'Agence fédérale de développement économique pour le Nord de l'Ontario (FedNor) a été créée le 12 août 2021 pour renforcer le développement économique du Nord de l'Ontario. L'Agence, qui était auparavant une initiative du ministère de l'Innovation, des Sciences et du Développement économique (ISDE), a été créée en 1987 dans le but de promouvoir le développement économique des régions de l'Ontario à faibles revenus et faible croissance économique, de mettre l'accent sur le développement économique à long terme et sur la création d'emplois et de revenus durables et de concentrer les efforts sur les petites et moyennes entreprises (PME) et sur la valorisation des capacités d'entreprise.

FedNor a ensuite été établie à titre d'agence autonome à part entière [Décrêt C.P. 2021-0840](https://decrets.canada.ca/attachment.php?attach=41207&lang=fr) daté du 6 août 2021 et prenant effet le 12 août 2021, 1) transférant du ministère de l'Industrie à l'Agence fédérale de développement économique pour le Nord de l'Ontario la responsabilité à l'égard du secteur de l'administration publique fédérale au sein du ministère de l'Industrie connu sous le nom d'Initiative fédérale de développement économique pour le Nord de l'Ontario et 2) plaçant l'Agence fédérale de développement économique pour le Nord de l'Ontario sous l'autorité du ministre du Développement économique et des Langues officielle.

D'autres décrets ont assujetti FedNor à des lois pertinentes, comme *la Loi sur l'emploi dans la fonction publique*, *la Loi sur l'accès à l'information et la Loi sur la protection des renseignements personnels.*

FR — `institutions_infosource_docs/ati-schedule-i-federal-economic-development-agency-for-northern-ontario/classes_of_records_fr.md:107` — Responsabilités

Des renseignements sur le [mandat](/fr/propos-nous "À propos de nous") de FedNor, son [rôle](/fr/propos-nous/notre-organisme "Notre organisme"), et ses [programmes](/fr/nos-programmes/programme-developpement-collectivites "Le Programme de développement des collectivités") figurent sur le [site Web](/fr/agence-federale-developpement-economique-pour-nord-lontario "Agence fédérale de développement économique pour le Nord de l’Ontario") de l'Agence.

### Federal Public Service Health Care Plan Administration Authority

EN — `institutions_infosource_docs/ati-schedule-i-federal-public-service-health-care-plan-administration-authority/classes_of_records_en.md:90` — Background

The Federal Public Service Health Care Plan Administration Authority (referred to as the Administration Authority) is charged with the oversight of the administration of the Public Service Health Care Plan (PSHCP).

The Administration Authority is a corporation without share capital established under authority of subsection 7.2(1) of the [Financial Administration Act](http://laws-lois.justice.gc.ca/eng/acts/F-11/) by Letters Patent issued by the President of the Treasury Board effective on May 1, 2007.

The Administration Authority is governed by a Board of Directors and is accountable to the Treasury Board of Canada and to the Public Service Health Care Plan Partners Committee, which is a committee established by the President of the Treasury Board, with the objective of developing the Plan and recommending changes to the Treasury Board. The Committee comprises seven members: three employer representatives, three representatives of employee bargaining agents, and one pensioner representative.

EN — `institutions_infosource_docs/ati-schedule-i-federal-public-service-health-care-plan-administration-authority/classes_of_records_en.md:100` — Responsibilities

The Administration Authority is charged with the administration of the PSHCP. The mandate of the Administration Authority is to ensure that benefits and services to Plan members and their covered dependents, as defined in PSHCP documentation, are delivered in a manner that ensures the effective and efficient administration of the PSHCP.

Learn more about the responsibilities of the Administration Authority [here](https://www.pshcp.ca/about-the-pshcp/about-the-administration-authority/).

© 2026 PSHCP-AA. [Privacy Policy](https://www.pshcp.ca/about-the-pshcp/atip/privacy-policy/). [Legal Disclaimer](https://www.pshcp.ca/legal-disclaimer/).

FR — `institutions_infosource_docs/ati-schedule-i-federal-public-service-health-care-plan-administration-authority/classes_of_records_fr.md:91` — Historique

L’Administration du Régime de soins de santé de la fonction publique fédérale (ci-dessous l’Administration) a pour mission de superviser l’administration du Régime de soins de santé de la fonction publique (RSSFP).

Le président du Conseil du Trésor a constitué une personne morale sans capital-actions en vertu des pouvoirs prévus au paragraphe 7.2 (1) de la [Loi sur la gestion des finances publiques](http://laws-lois.justice.gc.ca/fra/lois/F-11/), en délivrant des lettres patentes entrant en vigueur le 1er mai 2007. Le Conseil d’administration de l’Administration comprend dix membres. L’Administration est redevable auprès du Conseil du Trésor et du Comité des partenaires du Régime de soins de santé de la fonction publique. Ce comité, créé par le président du Conseil du Trésor, a pour objectif d’élaborer le Régime et de porter des recommandations à son attention. Il est composé de sept membres, soit trois représentants de l’employeur, trois représentants des agents négociateurs des employés et d’un représentant des retraités.

L’Administration rend compte au Parlement par l’intermédiaire du président du Conseil du Trésor.

FR — `institutions_infosource_docs/ati-schedule-i-federal-public-service-health-care-plan-administration-authority/classes_of_records_fr.md:99` — Responsabilités

L’Administration est chargée d’administrer le RSSFP. Elle a pour mandat de veiller à ce que les prestations et les services aux membres du Régime et à leurs personnes à charge assurées, selon les définitions figurant dans les documents du RSSFP, soient offerts de façon à assurer l’administration efficace et efficiente du RSSFP.

Informez-vous sur les responsabilités de l’Administration [ici](https://www.rssfp.ca/a-propos-du-rssfp/au-sujet-de-ladministration/).

### Fisheries and Oceans Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-fisheries-and-oceans/classes_of_records_en.md:106` — Background

Fisheries and Oceans Canada (DFO) has existed as a department under various names, dating back to the birth of the country. Its mandate was established by the [*Constitution Act, 1867*](http://laws-lois.justice.gc.ca/eng/Const/) and the *1868 Fisheries Act*, which gave Parliament jurisdiction over “Sea, Coast and Inland Fisheries.”

In 1978, the [*Department of Fisheries and Oceans Act*](http://laws-lois.justice.gc.ca/eng/acts/F-15/) established the current department and its responsibility to oversee coastal and inland fisheries, fishing and recreational harbours, hydrography and marine sciences and policies and programs respecting oceans.

Today, DFO has the lead federal role in managing Canada's fisheries and oceans resources and safeguarding its waters.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-fisheries-and-oceans/classes_of_records_en.md:116` — Responsibilities

Follow the links provided to read about [DFO's mandate](/about-notre-sujet/mandate-mandat-eng.htm), [program responsibilities](/dp-pm/2024-25/index-eng.html) and [major policies](/acts-lois/interpretation-eng.htm).

FR — `institutions_infosource_docs/ati-schedule-i-department-of-fisheries-and-oceans/classes_of_records_fr.md:106` — Contexte

Pêches et Océans Canada (MPO) existe en tant que ministère sous divers noms depuis la fondation du pays. Son mandat a été établi par la [*Loi constitutionnelle de 1867*](http://laws-lois.justice.gc.ca/fra/Const/) et la *Loi sur les pêches* de 1868, qui conféraient au Parlement des compétences relatives aux « pêches dans les eaux côtières et les eaux intérieures ».

En 1978, la [*Loi sur le ministère des Pêches et des Océans*](http://laws-lois.justice.gc.ca/fra/lois/F-15/) a créé le ministère actuel et lui a confié la responsabilité de superviser les pêches dans les eaux côtières et les eaux intérieures, les ports de pêche et de plaisance, l’hydrographie et les sciences marines ainsi que les politiques et les programmes relatifs aux océans.

Aujourd’hui, le MPO assume le principal rôle lorsqu’il s’agit de gérer la pêche et de protéger les étendues d’eau du Canada.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-fisheries-and-oceans/classes_of_records_fr.md:116` — Responsabilités

Veuillez suivre les liens suivants pour plus d’information concernant [le mandat du MPO](/about-notre-sujet/mandate-mandat-fra.htm), les [responsabilités des programmes](/dp-pm/2024-25/index-fra.html) et les [politiques principales](/acts-lois/interpretation-fra.htm).

### Global Affairs Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-foreign-affairs-trade-and-development/classes_of_records_en.md:75` — Background

In June 1909, the Canadian Government established an office to handle Canada’s relations with other foreign governments. The office transformed over the years to reflect the changing international context and Canada’s evolving foreign-policy priorities. Today, this office is referred to as Global Affairs Canada (GAC). Some notable changes in GAC’s [history](https://www.international.gc.ca/gac-amc/history-histoire/index.aspx?lang=eng) include adding the foreign operations of the Immigration Service in 1981 and combining the Department and the Trade Commissioner Service into a single trade and foreign-policy ministry in 1982. In 1992, the Department transferred its responsibilities for aid and immigration to other departments to focus on advancing Canadian interests abroad. Finally, in June 2013, the Department was amalgamated with the Canadian International Development Agency which resulted in an expansion of GAC’s mandate to include Canada’s international assistance to deliver effective and sustainable development programming.

GAC’s legal responsibilities are detailed in the *Department of Foreign Affairs, Trade and Development Act*. The department operates under the leadership the Minister of Foreign Affairs, the Minister of International Trade and the Minister of International Development and La Francophonie. GAC reports to Parliament through the Minister of Foreign Affairs.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-foreign-affairs-trade-and-development/classes_of_records_en.md:81` — Responsibilities

Global Affairs Canada (GAC) is responsible for Canada's foreign policy and all matters relating to Canada's external affairs, including international trade and commerce, and international development. GAC’s specific areas of responsibility include international peace and security, international development assistance, global trade and commerce, diplomatic and consular relations, administration of the Foreign Service and Canada's missions abroad, and development of international law and its application to Canada.

As the federal government's centre of expertise on foreign affairs, trade and development, the department leads the government-wide approach to Canada's foreign affairs, trade and development policies; promotes international trade and commerce through initiatives such as negotiating agreements to open and/or expand markets; provides advice and services to help Canadian businesses succeed abroad and attract foreign direct investment to Canada; facilitates two-way trade and investment and supports international innovation, science and technology; offers consular and international commercial services; provides timely and practical information on international issues and travel; manages Canada’s official development assistance to deliver sustainable development programming; and manages Canada's missions worldwide, thereby delivering the Government of Canada's international platform.

GAC’s portfolio consists of the International Development Research Centre, Export Development Canada, the International Joint Commission (Canadian Section), the Canadian Commercial Corporation, and the Roosevelt Campobello International Park.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-foreign-affairs-trade-and-development/classes_of_records_fr.md:75` — Contexte

En juin 1909, le gouvernement du Canada a établi un bureau pour gérer les relations du Canada avec d’autres gouvernements étrangers. Ce bureau s’est transformé au fil des années pour refléter l’évolution du contexte international ainsi que des priorités du Canada en matière de politique étrangère. Aujourd’hui, ce bureau s’appelle Affaires mondiales Canada (AMC). Le Ministère a connu quelques changements remarquables au cours de son[histoire](https://www.international.gc.ca/gac-amc/history-histoire/index.aspx?lang=fra), dont l’ajout des opérations à l’étranger pour le Service d’immigration en 1981 et le regroupement du ministère et du Service des délégués commerciaux en un seul et même ministère consacré au commerce et à la politique étrangère en 1982. En 1992, le Ministère a transféré ses responsabilités en matière d’aide et d’immigration à d’autres ministères afin de concentrer son attention sur la promotion des intérêts du Canada à l’étranger. Enfin, en juin 2013, le Ministère a fusionné avec l’Agence canadienne de développement international, ce qui a donné lieu à l’élargissement du mandat d’AMC pour y inclure l’aide internationale apportée par le Canada en vue d’offrir des programmes de développement efficace et durable.

Les responsabilités juridiques d’AMC sont décrites en détail dans la*Loi sur le ministère des Affaires étrangères, du Commerce et du Développement*.Le Ministère opère sous la direction de la ministre des Affaires étrangères, du ministre du Commerce international et de la ministre du Développement international et de la Francophonie. AMC rend compte au Parlement par l’entremise du ministre des Affaires étrangères.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-foreign-affairs-trade-and-development/classes_of_records_fr.md:81` — Responsabilités

Affaires mondiales Canada (AMC) est responsable de la politique étrangère du Canada et de toutes les questions relatives aux affaires extérieures, notamment le commerce international et le développement international. Les principaux domaines de responsabilités d’AMC sont la paix et la sécurité internationales, l’aide au développement international, le commerce international, les relations diplomatiques et consulaires, l’administration du service extérieur et les missions du Canada à l’étranger, ainsi que l’élaboration du droit international et son application au Canada.

À titre de centre d’expertise du gouvernement fédéral en matière d’affaires étrangères, de commerce et de développement, le Ministère dirige la stratégie pangouvernementale des politiques du Canada relatives aux affaires étrangères, au commerce et au développement; il favorise le commerce et les échanges internationaux par différentes activités telles que la négociation d’accords visant à ouvrir ou à agrandir des marchés; il offre des conseils et des services aux entreprises canadiennes pour les aider à réussir à l’étranger et pour attirer des investissements directs étrangers au Canada; il facilite les échanges et les investissements bilatéraux; il encourage l’innovation, la science et la technologie à l’échelle internationale; il dispense des services consulaires et des services de commerce international, il diffuse des renseignements opportuns et pratiques sur les questions internationales et les voyages à l’étranger; enfin, il gère l’aide publique au développement du Canada et met à exécution des programmes de développement durable, de même que les missions canadiennes établies dans le monde entier qui constituent la plateforme internationale du gouvernement du Canada.

Le portefeuille d’AMC est composé du Centre de recherches pour le développement international, d’Exportation et développement Canada, de la Commission mixte internationale (section canadienne), de la Corporation commerciale canadienne et du Parc international Roosevelt de Campobello.

### Gwich’in Land Use Planning Board

EN — `institutions_infosource_docs/ati-schedule-i-gwich-in-land-use-planning-board/classes_of_records_en.md:57` — Background

The Gwich'in Land Use Planning Board is an institution of public government provided for by the Gwich'in Comprehensive Land Claim Agreement (1992) and established by the Mackenzie Valley Resource Management Act (1998). The Gwich'in Interim Land Use Planning Board was incorporated as a society in 1993 and acted in the Board's capacity until 1998.

EN — `institutions_infosource_docs/ati-schedule-i-gwich-in-land-use-planning-board/classes_of_records_en.md:61` — Responsibilities

The Planning Board is responsible for developing and implementing a land use plan for the Gwich'in Settlement Area that provides for the conservation, development and use of land, water and other resources.

FR — `institutions_infosource_docs/ati-schedule-i-gwich-in-land-use-planning-board/classes_of_records_fr.md:57` — Historique

L'Office Gwich'in d'aménagement territorial est un organisme gouvernemental prévu dans l'Entente sur la revendication territoriale globale des Gwich'in (1992) et créé en vertu de la Loi sur la gestion des ressources de la vallée du Mackenzie (1998). L'Office Gwich'in d'aménagement territorial provisoire a été constitué en personne morale en 1993 et a rempli les fonctions de l'Office jusqu'en 1998.

FR — `institutions_infosource_docs/ati-schedule-i-gwich-in-land-use-planning-board/classes_of_records_fr.md:61` — Responsabilités

L'Office d'aménagement est chargé d'élaborer et de mettre en œuvre un plan d'aménagement territorial de la région désignée concernant la conservation, le développement et l'utilisation des terres, des eaux et des autres ressources.

### Gwich’in Land and Water Board

FR — `institutions_infosource_docs/ati-schedule-i-gwich-in-land-and-water-board/classes_of_records_fr.md:57` — Historique

L'Office Gwich'in des terres et des eaux (OGTE) est un organisme de réglementation créé aux termes de l'Entente sur la revendication territoriale globale des Gwich'in. Il a commencé à exercer ses activités le 28 décembre 1998, au moment de l'entrée en vigueur de la Loi sur la gestion des ressources de la vallée du Mackenzie (LGRVM) (projet de loi C-6).

FR — `institutions_infosource_docs/ati-schedule-i-gwich-in-land-and-water-board/classes_of_records_fr.md:61` — Responsabilités

L'OGTE a été créé afin d'offrir un système intégré et coordonné de gestion des terres dans la vallée du Mackenzie, dans les Territoires du Nord-Ouest.

L'OGTE a pour objectif d'assurer la conservation, la mise en valeur et l'utilisation des terres et des eaux dans la région visée par l'entente avec les Gwich'in, de manière à permettre aux habitants actuels et futurs de la région visée par l'entente et de la vallée du Mackenzie ainsi qu'à tous les Canadiens d'en tirer le plus d'avantages possible.

La LGRVM autorise l'OGTE à réglementer l'utilisation des terres et des eaux en délivrant, en modifiant, en renouvelant et en suspendant des permis d'utilisation des terres et des eaux à l'échelle de la région visée par l'entente avec les Gwich'in, laquelle comprend toutes les terres de la Couronne visées par l'entente avec les Gwich'in et les terres privées.

### Health Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-health/classes_of_records_en.md:125` — Background

Health Canada was established in 1996 through the Department of Health Act. It is the federal department responsible for helping Canadians maintain and improve their health. Health Canada is committed to improving the lives of all Canadians and to making this country's population among the healthiest in the world as measured by longevity, lifestyle and effective use of the public health care system.

On an annual basis, the federal Minister of Health is required to report to Parliament on the administration and operation of the Canada Health Act, as set out in section 23 of the Act. The vehicle for so doing is the [Canada Health Act Annual Report](/en/health-canada/services/health-care-system/reports-publications/canada-health-act-annual-reports.html). While the principal and intended audience for the Report is Parliamentarians, a public document offers a comprehensive report on insured services in each of the provinces and territories. The Annual Report is structured to address the mandated reporting requirements of the Act; as such, its scope does not extend to commenting on the status of the Canadian health care system as a whole. (Source: [Health Canada](/en/health-canada.html))

For more information, please consult [About Health Canada](/en/health-canada/corporate/about-health-canada/activities-responsibilities/mission-values-activities.html).

EN — `institutions_infosource_docs/ati-schedule-i-department-of-health/classes_of_records_en.md:133` — Responsibilities

Health Canada has many [roles and responsibilities](/en/health-canada/corporate/about-health-canada/activities-responsibilities/mission-values-activities.html) that help Canadians maintain and improve their health. Health Canada's mandate is to improve the lives of all Canada's people and to make the country's population among the healthiest in the world as measured by longevity, lifestyle and effective use of the public health care system.

First, as a regulator, Health Canada is responsible for the regulatory regime governing the safety of products including food, pharmaceuticals, medical devices, natural health products, consumer products, chemicals, radiation emitting devices, cosmetics and pesticides. It also regulates tobacco products and controlled substances, public health on aircraft, ships and other passenger conveyances, and helps manage the health risks posed by environmental factors such as air, water, radiation and contaminants.

In 2018, Health Canada transferred service provider responsibilities for First Nations to the newly created Indigenous Services Canada. The federal government has provided basic health services to First Nations since 1904. Today, the federal government provides basic primary care services in approximately 200 remote First Nations communities, home and community care in 600 First Nations communities, support for health promotion programs in Inuit communities across four regions and a limited range of medically-necessary health-related goods and services not insured by private or other public health insurance plans to eligible First Nations and Inuit. The government funds or delivers community-based health programs and public health activities to First Nations and Inuit. These activities promote health, prevent chronic disease and address issues such as substance abuse and the spread of infectious diseases.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-health/classes_of_records_fr.md:125` — Contexte

Santé Canada a été créé en 1996 par la *Loi sur le ministère de la Santé*. Ce ministère fédéral est chargé d'aider les Canadiennes et les Canadiens à maintenir et à améliorer leur état de santé. Santé Canada s'engage également à améliorer la vie de tous les citoyens afin qu'ils se classent parmi les populations ayant la meilleure santé au monde, comme en témoignent leur longévité et leur mode de vie, ainsi que l'utilisation réelle du système de santé public.

Chaque année, le ministre fédéral de la Santé doit rendre compte au Parlement de l'application de la *Loi canadienne sur la santé*, comme le prévoit l'article 23 de la Loi. Le moyen utilisé à cette fin est le [Rapport annuel sur l'application de la *Loi canadienne sur la santé*](/fr/sante-canada/services/systeme-soins-sante/rapports-publications/loi-canadienne-sante-rapports-annuels.html). Même s'il s'adresse d'abord aux parlementaires, le rapport est un document public qui rend compte en détail des services assurés dans chaque province et territoire. Le rapport annuel est structuré de manière à satisfaire aux obligations de rapport prévues dans la Loi; ainsi, son objet n'est pas de commenter l'état du système de soins de santé canadien dans sa globalité. (Source: [Santé Canada](/fr/sante-canada.html))

Pour plus de renseignements, veuillez consulter la page [Mission, valeurs, activités](/fr/sante-canada/organisation/a-propos-sante-canada/activites-responsabilites/mission-valeurs-activites.html).

FR — `institutions_infosource_docs/ati-schedule-i-department-of-health/classes_of_records_fr.md:133` — Responsabilités

Santé Canada assume plusieurs [rôles et responsabilités](/fr/sante-canada/organisation/a-propos-sante-canada/activites-responsabilites/mission-valeurs-activites.html) afin d'aider la population canadienne à préserver et à améliorer sa santé. Le mandat de Santé Canada est d'améliorer la vie de tous les peuples du Canada et de faire du Canada l'un des pays où les gens sont les plus en santé au monde, comme en témoignent la longévité, les habitudes de vie et l'utilisation efficace du système public de soins de santé.

Tout d'abord, à titre d'organisme de réglementation, Santé Canada est responsable du régime de réglementation régissant l'innocuité des produits, notamment des aliments, des médicaments, du matériel médical, des produits de santé naturels, des produits de consommation, des produits chimiques, des dispositifs émettant des radiations, des cosmétiques et des pesticides. Le ministère réglemente également les produits du tabac, les substances contrôlées et la santé publique à bord des aéronefs, des navires et d'autres moyens de transport de passagers, et contribue à la gestion des risques pour la santé présentée par des facteurs environnementaux comme l'air, l'eau, les rayonnements et les contaminants.

En 2018, Santé Canada a transféré les responsabilités de fournisseur de services aux Premières Nations au nouvellement créé Services aux Autochtones Canada. Le gouvernement fédéral fournit des services de base en santé aux Premières Nations depuis 1904. Aujourd'hui le gouvernement fédéral offre des services de soins primaires dans environ 200 collectivités éloignées des Premières Nations, des soins à domicile ou en milieu communautaire dans 600 collectivités des Premières Nations, du soutien aux programmes de promotion de la santé dans les collectivités inuites de quatre régions et une gamme limitée de biens et services liés à la santé et nécessaires d'un point de vue médical qui ne sont pas couverts par les régimes privés ou publics d'assurance maladie aux Premières Nations et aux Inuits admissibles. Le gouvernement finance et offre des programmes de santé fondés sur la collectivité et des activités de santé publique aux Premières Nations et aux Inuits. Ces activités visent la promotion de la santé, la prévention des maladies chroniques et abordent les enjeux comme l'abus de substance et la propagation des maladies infectieuses.

### Historic Sites and Monuments Board of Canada

EN — `institutions_infosource_docs/ati-schedule-i-historic-sites-and-monuments-board-of-canada/classes_of_records_en.md:53` — Background

The Historic Sites and Monuments Board of Canada grew out of the interplay of disparate elements of public opinion concerned with heritage preservation and government policy before the First World War. A growing heritage movement encouraged the government to preserve and develop sites with important historical associations. At the same time, the government was looking to extend its national parks system from the west into the east and the idea of creating historic parks around significant historic structures was conceived. The War delayed the introduction of a government program to identify and preserve Canadian heritage; however, in 1919, James B. Harkin, the Commissioner of Dominion Parks, suggested that "An Advisory Board for Historic Site Preservation" be established, and the Historic Sites and Monuments Board of Canada was born.

The Board was given a statutory base for its operations through the Historic Sites and Monuments Act of 1953.

EN — `institutions_infosource_docs/ati-schedule-i-historic-sites-and-monuments-board-of-canada/classes_of_records_en.md:59` — Responsibilities

The Historic Sites and Monuments Board of Canada has the statutory responsibility to advise the Minister of the Environment and, through him or her, Parks Canada on the commemoration of nationally significant aspects of Canada’s past, including the designation of national historic sites, persons and events.

The Board also advises the Minister on the designation of heritage railway stations and other matters relating to the implementation of the Heritage Railway Stations Protection Act. The Board also serves as the advisory committee to the Minister for the implementation of the Heritage Lighthouse Protection Act.

Normally, the Board meets in plenary two times a year to consider submissions from the general public, heritage organizations, provincial and municipal governments, and others regarding matters of possible national significance. The various committees which it has established to expedite its work, such as the Cultural Communities Committee, the Built Environment Committee, the Status of Designations Committee, the Inscriptions Committee, the Persons Committee, the Events Committee and the Lighthouse Committee meet as required.

FR — `institutions_infosource_docs/ati-schedule-i-historic-sites-and-monuments-board-of-canada/classes_of_records_fr.md:53` — Historique

La Commission des lieux et monuments historiques du Canada est née de l’action réciproque de divers segments de l’opinion publique préoccupés par la préservation du patrimoine et par la politique gouvernementale, avant la Première Guerre mondiale. La montée du mouvement pour la préservation du patrimoine incita le gouvernement à préserver et à aménager divers lieux ayant des associations historiques importantes. Le gouvernement chercha parallèlement à étendre son réseau de parcs nationaux vers l’est et conçut l’idée de créer des parcs historiques autour de structures historiques majeures. La guerre retarda l’introduction d’un programme gouvernemental visant à identifier et à préserver le patrimoine du Canada, mais en 1919, James B. Harkin, Commissaire des parcs du Dominion, suggéra la création d’un « Comité consultatif pour la préservation des lieux historiques ». La Commission des lieux et monuments historiques du Canada était née.

La Loi sur les lieux et monuments historiques de 1953 constitue le fondement législatif de la Commission.

FR — `institutions_infosource_docs/ati-schedule-i-historic-sites-and-monuments-board-of-canada/classes_of_records_fr.md:59` — Responsabilités

En vertu de la Loi, la Commission des lieux et monuments historiques du Canada est chargée de conseiller le ministre de l’Environnement et, par son entremise, Parcs Canada, sur la commémoration d’aspects du passé du Canada qui revêtent une importance nationale et notamment sur la désignation des lieux, personnes et événements historiques nationaux.

La Commission conseille également le ministre au sujet de la désignation des gares ferroviaires patrimoniales et d’autres questions liées à l’application de la Loi sur la protection des gares ferroviaires patrimoniales. La Commission a aussi la responsabilité d’aviser le ministre quant à la mise en œuvre de la Loi sur la protection des phares patrimoniaux.

En général, la Commission se réunit en plénière deux fois l’an pour discuter des demandes du public, des organismes patrimoniaux, des administrations provinciales et municipales et autres concernant des questions d’importance nationale possible. Pour accélérer le traitement de ces demandes, la Commission a créé divers comités - sur les communautés culturelles, sur l’environnement bâti, sur l’état des désignations, sur les inscriptions, sur les personnages, sur les événements et sur les phares - qui se réunissent au besoin.

### Housing, Infrastructure and Communities Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-housing-infrastructure-and-communities/classes_of_records_en.md:72` — Background

The Department of Housing, Infrastructure and Communities (commonly referred to as Housing, Infrastructure and Communities Canada (HICC)) was initially established in 2002 as Infrastructure Canada to ensure Canadians benefit from world-class public infrastructure from coast to coast to coast. On June 20, 2024, with the passing of Bill C-59, Infrastructure Canada (INFC) became the Department of Housing, Infrastructure and Communities enacting its enabling legislation, the *Department of Housing, Infrastructure and Communities Act.* The Act establishes a Minister of Infrastructure and Communities and a Minister of Housing, both supported by the Department and a single deputy minister.

This legislation sets out the powers, duties, and functions of both Ministers and provides a framework for the activities to be undertaken by the department, notably managing government programs, distributing funding, convening partners, conducting research, collecting and publishing data, and establishing and remunerating advisory committees or councils. The enabling instruments are listed in the [Housing, Infrastructure and Communities Canada's 2025-26 Departmental Plan](/pub/dp-pm/2025-26/2025-dp-pm-02-eng.html#toc04) in the departmental profile.

If no Minister of Housing is appointed, the Minister of Infrastructure and Communities is authorized to exercise the powers and perform the duties and functions of the Minister of Housing under the departmental legislation. The Department currently reports to Parliament through the Minister of Housing and Infrastructure.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-housing-infrastructure-and-communities/classes_of_records_en.md:82` — Responsibilities

Housing, Infrastructure and Communities Canada's [mandate and program responsibilities](/about-apropos/index-eng.html#1.1) are posted on its publicly available website.

As a funding organization, Housing, Infrastructure and Communities Canada's [major policies](https://tbs-sct.gc.ca/pol/index-eng.aspx) are those of the Treasury Board Secretariat.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-housing-infrastructure-and-communities/classes_of_records_fr.md:74` — Contexte

Le ministère du Logement, de l'Infrastructure et des Collectivités (communément appelé Logement, Infrastructures et Collectivités Canada (LICC)) a été initialement créé en 2002 sous le nom d'Infrastructure Canada pour veiller à ce que les Canadiens bénéficient d'infrastructures publiques de calibre mondial d'un océan à l'autre. Le 20 juin 2024, avec l'adoption du projet de loi C-59, Infrastructure Canada (INFC) est devenu le ministère du Logement, de l'Infrastructure et des Collectivités en promulguant sa loi habilitante, la *Loi sur le ministère du Logement, de l'Infrastructure et des Collectivités*. La Loi établit un ministre de l'Infrastructure et des Collectivités et un ministre du Logement, tous deux appuyés par le Ministère et un seul sous-ministre.

Cette loi définit les pouvoirs, les devoirs et les fonctions des deux ministres et fournit un cadre pour les activités à entreprendre par le Ministère, notamment la gestion des programmes gouvernementaux, la distribution du financement, la convocation de partenaires, la conduite de recherches, la collecte et la publication de données, ainsi que la création et la rémunération de comités ou de conseils consultatifs. Les instruments habilitants sont énumérés dans le [Plan ministériel 2025-2026 de Logement, Infrastructures et Collectivités Canada](/pub/dp-pm/2025-26/2025-dp-pm-02-fra.html) dans le profil du ministère.

Si aucun ministre du Logement n'est nommé, le ministre de l'Infrastructure et des Collectivités est autorisé à exercer les pouvoirs et à remplir les devoirs et fonctions du ministre du Logement en vertu de la législation ministérielle. Le Ministère rend actuellement compte au Parlement par l'intermédiaire du ministre du Logement et de l'Infrastructure.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-housing-infrastructure-and-communities/classes_of_records_fr.md:84` — Responsabilités

Pour en savoir plus sur [le mandat et les responsabilités du programme](https://www.infrastructure.gc.ca/about-apropos/index-fra.html) de Logement, Infrastructures et Collectivités Canada, consultez l'hyperlien fourni.

En tant qu'organisme de financement, les [principales politiques](https://www.tbs-sct.gc.ca/pol/index-fra.aspx) de Logement, Infrastructures et Collectivités Canada sont celles du Secrétariat du Conseil du Trésor.

### Immigration and Refugee Board of Canada

EN — `institutions_infosource_docs/ati-schedule-i-immigration-and-refugee-board/classes_of_records_en.md:102` — Background

The Immigration and Refugee Board of Canada (IRB) was created in 1989. In 2002, the
*Immigration Act* was replaced by the
*[Immigration and Refugee Protection Act](http://www.lois-laws.justice.gc.ca/eng/acts/I-2.5/index.html)* (IRPA) from which each IRB division gets its mandate.

The IRB is an independent, accountable tribunal whose work reflects Canada's humanitarian and security values and respect for our international obligations. As an organization responsible for applying administrative justice, the IRB adheres to the principles of natural justice and its resolutions and decisions are rendered in accordance with the law, including the Canadian Charter of Rights and Freedom Its mission, on behalf of Canadians, is to resolve immigration and refugee cases, efficiently, fairly, and in accordance with the law. The IRB reports to Parliament through the Minister of Citizenship, Immigration and Multiculturalism.

EN — `institutions_infosource_docs/ati-schedule-i-immigration-and-refugee-board/classes_of_records_en.md:110` — Responsibilities

The role of the IRB is to make decisions on immigration and refugee matters in Canada. Specifically, it decides who needs refugee protection, hears appeals on certain immigration matters and conducts admissibility hearings and detention reviews. The decisions affect the lives and liberty of the people appearing before it and contribute to the security of Canadians and the integrity of our immigration and refugee system.

FR — `institutions_infosource_docs/ati-schedule-i-immigration-and-refugee-board/classes_of_records_fr.md:103` — Historique

La Commission de l'immigration et du statut de réfugié du Canada (CISR) a été créée en 1989. En 2002, la
*Loi sur l'immigration* a été remplacée par la
*[Loi sur l'immigration et la protection des réfugiés](http://www.lois-laws.justice.gc.ca/fra/lois/I-2.5/index.html)* (LIPR), dont est tiré le mandat de chaque section de la CISR.

La CISR est un tribunal administratif indépendant et responsable, dont le travail reflète les valeurs humanitaires et celles relatives à la sécurité au Canada et le respect de nos obligations internationales. À titre d'organisme chargé d'appliquer la justice administrative, la CISR respecte les principes de justice naturelle, et ses décisions sont rendues conformément à la loi, notamment la Charte canadienne des droits et libertés. Sa mission, au nom des Canadiens, consiste à régler, de manière efficace, équitable et conforme à la loi, les cas d'immigration et de statut de réfugié. La CISR rend des comptes au Parlement par l'intermédiaire du ministre de la Citoyenneté, de l'Immigration et du Multiculturalisme.

FR — `institutions_infosource_docs/ati-schedule-i-immigration-and-refugee-board/classes_of_records_fr.md:111` — Responsabilités

Le rôle de la CISR consiste à rendre des décisions sur les questions d'immigration et de statut de réfugié au Canada. Plus particulièrement, elle tranche les demandes d'asile, entend les appels sur certaines questions d'immigration, tient des enquêtes et contrôle les motifs de détention. Elle rend des décisions qui ont une incidence sur la vie et la liberté des personnes qui comparaissent devant elle et contribuent à assurer la sécurité des Canadiens et l'intégrité de notre système d'immigration et de protection des réfugiés.

### Immigration, Refugees and Citizenship Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-citizenship-and-immigration/classes_of_records_en.md:59` — Background

Immigration, Refugees and Citizenship Canada (IRCC) was created through legislation in 1994 to link immigration services with citizenship registration. This Department helps build a stronger Canada by taking a broad and integrated approach to helping immigrants settle in Canada, and encouraging and facilitating their ultimate acquisition of Canadian citizenship. Immigration is also an area of shared jurisdiction with the provinces and territories, with federal legislation prevailing under section 95 of the *Constitution Act, 1867*.

IRCC reports to Parliament through its Minister. The Minister is also responsible for the Immigration and Refugee Board of Canada (IRB)—an independent tribunal established by the Parliament of Canada. The IRB’s functions are separate from those of the Department.

IRCC selects and processes foreign nationals as both permanent and temporary residents, assists with immigrant settlement and integration, and offers Canada’s protection to refugees. The work of IRCC helps to reunite families and meet Canada’s humanitarian obligations. IRCC also supports Canada’s economy by assisting in the strengthening of the national labour force. As such, IRCC contributes to the country’s long-term prosperity while helping to protect and build a stronger Canada.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-citizenship-and-immigration/classes_of_records_en.md:71` — Responsibilities

IRCC’s broad mandate is derived from the *Department of Citizenship and Immigration Act*. More specifically, the Minister of Citizenship, Immigration and Multiculturalism is responsible for the *Citizenship Act* of 1977, and shares responsibility with the Minister of Public Safety Canada for the *Immigration and Refugee Protection Act* (IRPA), which was enacted following a major legislative reform in 2002.

IRCC brings together a broad range of activities. These include the selection of immigrants and refugees and the issuance of temporary resident visas abroad; the facilitation and control of immigrants and foreign visitors in Canada; the settlement and integration of immigrants and refugees; and the processing of applications for Canadian citizenship and proof of citizenship.

IRCC and the [Canada Border Services Agency](http://www.cbsa-asfc.gc.ca/menu-eng.html) (CBSA) support their respective ministers in the administration and enforcement of IRPA. These organizations work collaboratively to achieve and balance the facilitation and enforcement objectives of the immigration and refugee programs.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-citizenship-and-immigration/classes_of_records_fr.md:59` — Historique

Immigration, Réfugiés et Citoyenneté Canada (IRCC) a été créé par voie législative en 1994 afin d’établir un lien entre les services d’immigration et l’enregistrement des citoyens. Le Ministère contribue au renforcement du Canada en adoptant une vaste approche intégrée visant à aider les immigrants à s’établir au Canada, ainsi qu’à encourager et à faciliter leur acquisition de la citoyenneté canadienne. En vertu de l’article 95 de la *Loi constitutionnelle de 1867*, l’immigration est un domaine de compétence partagée avec les provinces et les territoires, la Loi fédérale ayant préséance.

IRCC rend compte au Parlement par l’entremise de son ministre. Celui-ci est également responsable de la Commission de l’immigration et du statut de réfugié du Canada (CISR), tribunal indépendant constitué par le Parlement canadien. Les fonctions de la CISR sont distinctes de celles du Ministère.

IRCC traite les demandes présentées par des étrangers et procède à la sélection des résidents permanents et temporaires, aide les immigrants à s’établir et à s’intégrer au Canada, et offre la protection du Canada aux réfugiés. Par son mandat, IRCC contribue à la réunification des familles et aide le Canada à respecter ses obligations humanitaires. Il appuie également l’économie canadienne en facilitant le développement de la main-d’œuvre nationale. IRCC contribue ainsi à la prospérité à long terme du pays tout en aidant à protéger et à bâtir un Canada plus fort.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-citizenship-and-immigration/classes_of_records_fr.md:71` — Responsabilités

IRCC tire son mandat général de la *Loi sur le ministère de la Citoyenneté et de l’Immigration*. Plus précisément, le ministre de la Citoyenneté, de l’Immigration et du Multiculturalisme est chargé d’appliquer la *Loi sur la citoyenneté* de 1977, de concert avec le ministre de la Sécurité publique du Canada, la *Loi sur l’immigration et la protection des réfugiés* (LIPR), entrée en vigueur en 2002 à la suite d’une importante réforme législative. IRCC rend compte au Parlement par l’entremise de son ministre. Celui-ci est également responsable de la Commission de l’immigration et du statut de réfugié du Canada (CISR), tribunal indépendant constitué par le Parlement canadien. Les fonctions de la CISR sont distinctes de celles du Ministère.

IRCC regroupe un large éventail d’activités : la sélection des immigrants et des réfugiés et la délivrance des visas de résidents temporaires à l’étranger, la facilitation et le suivi des immigrants et des visiteurs étrangers au Canada, l’établissement et l’intégration des immigrants et des réfugiés, et le traitement des demandes de citoyenneté canadienne et de preuve de citoyenneté.

IRCC et l’[Agence des services frontaliers du Canada](http://www.cbsa-asfc.gc.ca/menu-fra.html) (ASFC) appuient leurs ministres respectifs dans l’exécution et l’administration de la LIPR et travaillent de concert en vue d’atteindre et de concilier les objectifs de facilitation et d’exécution des programmes concernant les immigrants et les réfugiés.

### Impact Assessment Agency of Canada

EN — `institutions_infosource_docs/ati-schedule-i-impact-assessment-agency-of-canada/classes_of_records_en.md:76` — Background

Established in 1994, the Canadian Environmental Assessment Agency (the Agency) came into being to prepare for the implementation of the Canadian Environmental Assessment Act, which came into effect in early 1995. The Agency is a federal body accountable to the [Minister of Environment and Climate Change](/en/government/ministers/catherine-mckenna.html). The Agency provides high-quality environmental assessments (EA) that contribute to informed decision making, in support of sustainable development. The Agency is the responsible authority for most federal EAs. The current Canadian Environmental Assessment Act, 2012 (CEAA 2012) came into effect on July 6, 2012. CEAA 2012 and its accompanying regulations provide the legislative framework for environmental assessments. To better understand the Agency, read about our [legislative foundation](/en/impact-assessment-agency/corporate/acts-regulations.html).

EN — `institutions_infosource_docs/ati-schedule-i-impact-assessment-agency-of-canada/classes_of_records_en.md:80` — Responsibilities

Read about the Agency's [mandate](/en/impact-assessment-agency/corporate/mandate.html) and responsibilities.

The Agency's main responsibilities in conducting the environmental assessment (EA) process are to identify opportunities to avoid, eliminate or reduce a project's potential adverse impact on the environment before the project is undertaken; ensure that mitigation measures are applied; encourage public participation; promote high-quality assessment through training and guidance; provide administrative and advisory support for review panels; promote the use of strategic EA as a key tool to support sustainable decision making; promote and verify compliance with decision statements and legislative requirements; and act as the Crown Consultation Coordinator to integrate the Government of Canada's Indigenous consultation activities into the EA processes it manages to the greatest extent possible.

FR — `institutions_infosource_docs/ati-schedule-i-impact-assessment-agency-of-canada/classes_of_records_fr.md:76` — Contexte

L’Agence canadienne d’évaluation environnementale (l’Agence) a été instituée en 1994 pour préparer la mise en œuvre de la Loi canadienne sur l’évaluation environnementale, qui est entrée en vigueur au début de 1995. L’Agence est un organisme fédéral qui relève de la [ministre de l’Environnement et du Changement climatique](/fr/gouvernement/ministres/catherine-mckenna.html). Elle fournit des évaluations environnementales (EE) de grande qualité qui contribuent à une prise de décisions éclairées favorisant le développement durable. L’Agence est l’autorité responsable de la plupart des évaluations environnementales fédérales. La version actuelle de la Loi canadienne sur l’évaluation environnementale (2012) (LCEE 2012) est entrée en vigueur le 6 juillet 2012. La LCEE 2012 et ses règlements connexes fournissent le cadre législatif pour les évaluations environnementales. Pour mieux comprendre l’Agence, lisez notre [fondement législatif](/fr/agence-evaluation-impact/organisation/lois-reglements.html).

FR — `institutions_infosource_docs/ati-schedule-i-impact-assessment-agency-of-canada/classes_of_records_fr.md:80` — Responsabilités

Consultez le [mandat](/fr/agence-evaluation-impact/organisation/mandat.html) et les responsabilités de l’Agence.

Les principales responsabilités de l’Agence dans le processus d’évaluation environnementale (EE) consistent à déceler les occasions d’éviter, d’éliminer ou de réduire les répercussions négatives potentielles d’un projet sur l’environnement avant qu’il ne soit mis en œuvre, à veiller à ce que des mesures d’atténuation soient appliquées, à encourager la participation du public, à promouvoir une évaluation de grande qualité au moyen de la formation et de conseils, à fournir un soutien administratif et consultatif aux commissions d’examen, à promouvoir l’évaluation environnementale stratégique comme principal outil d’aide à la prise de décisions durables, à promouvoir et à vérifier la conformité aux déclarations de décision et aux exigences législatives, et à agir comme coordonnateur des consultations de la Couronne, dans la mesure du possible, pour intégrer les activités de consultation des Autochtones du gouvernement du Canada aux processus d’EE qu’il gère.

### Indigenous Services Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-indigenous-services/classes_of_records_en.md:68` — Background

The Indigenous Services Canada (ISC) mandate is to work with First Nations, Inuit and Métis to improve access to high-quality services; improve well-being in Indigenous communities across Canada; and support Indigenous peoples in assuming control of the delivery of services at the pace and in the ways they choose.

ISC was first established by Order–in-Council (P.C. 2017-79) on November 30, 2017. The Budget Implementation Act of 2019 dissolved the Department of Indian Affairs and Northern Development (Indian Act) and formally established the Department of Indigenous Services with the enactment of the [Department of Indigenous Services Act](https://laws-lois.justice.gc.ca/eng/acts/I-7.88/FullText.html) on July 15, 2019.

ISC is 1 of the 2 federal departments that are primarily responsible for meeting the Government of Canada's obligations and commitments to First Nations, Inuit and Métis, and for fulfilling the federal government's constitutional responsibilities in the North. ISC's overall mandate and wide-ranging responsibilities are shaped by centuries of history and unique demographic and geographic challenges. ISC's programs and services, representing a majority of its spending, are delivered through partnerships with Indigenous communities and federal-provincial or federal-territorial agreements.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-indigenous-services/classes_of_records_fr.md:68` — Contexte

Services aux Autochtones Canada (SAC) a pour mandat de travailler avec les Premières Nations, les Inuit et les Métis pour améliorer l'accès à des services de haute qualité, améliorer le bien-être des communautés autochtones au Canada et aider les peuples autochtones à prendre le contrôle de la prestation des services au rythme et de la manière qui leur conviennent.

SAC a été créé en vertu d'un décret en conseil (C.P. 2017-79) le 30 novembre 2017. La Loi d'exécution du budget de 2019 a dissous le ministère des Affaires indiennes et du Développement du Nord canadien (Loi sur les Indiens) et a officiellement créé le ministère des Services aux Autochtones avec l'adoption de la [Loi sur le ministère des Services aux Autochtones](https://laws.justice.gc.ca/fra/lois/i-7.88/page-1.html) le 15 juillet 2019.

SAC est l'un de 2 ministères fédéraux qui sont principalement appelés à respecter les obligations et les engagements du gouvernement du Canada envers les membres des Premières Nations, les Inuit et les Métis, et à assumer les responsabilités constitutionnelles du gouvernement fédéral dans le Nord. Le mandat général du ministère et les nombreuses responsabilités dont il est investi sont façonnés par des siècles d'histoire et par des défis démographiques et géographiques uniques. La plupart des programmes et services de SAC, qui comptent pour la majorité de ses dépenses, sont exécutés dans le cadre de partenariats avec des communautés autochtones ou d'ententes fédérales-provinciales ou fédérales-territoriales.

### Innovation, Science and Economic Development Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-industry/classes_of_records_en.md:120` — Background

The department's work is enabled by the [*Department of Industry Act*](https://laws.justice.gc.ca/eng/acts/I-9.2/index.html), and through 56 other pieces of legislation that pertain to the department's operating programs, listed here: [List of acts](https://ised-isde.canada.ca/site/acts-regulations/en/list-acts).

Mission: ISED's mission is to foster a growing, competitive and knowledge-based Canadian economy.

ISED's Info Source includes the reporting requirements for its four special operating agencies (wholly owned subsidiaries): the Canadian Intellectual Property Office, the Competition Bureau, Measurement Canada, and the Office of the Superintendent of Bankruptcy, which do not report separately.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-industry/classes_of_records_fr.md:122` — Contexte

Le travail du ministère est rendu possible par la [*Loi sur le ministère de l'Industrie*](https://laws.justice.gc.ca/fra/lois/i-9.2/index.html), et par 56 autres Lois du Parlement relatifs aux programmes opérationnels du ministère, répertoriés ici : [Liste des lois](https://ised-isde.canada.ca/site/lois-reglements/fr/liste-lois).

Mission : La mission d'ISDE consiste à favoriser l'essor d'une économie canadienne concurrentielle et axée sur le savoir.

L'Info Source d'ISDE comprend les exigences de déclaration de ses quatre filiales en propriété exclusive — le Bureau de la concurrence, le Bureau du surintendant des faillites, Mesures Canada, et l'Office de la propriété intellectuelle du Canada — qui ne produisent pas de rapports distincts.

### Military Grievances External Review Committee

EN — `institutions_infosource_docs/ati-schedule-i-military-grievances-external-review-committee/classes_of_records_en.md:58` — Background

The Military Grievances External Review Committee (MGERC) (*formerly the Canadian Forces Grievance Board*)[Footnote 1](/en/military-grievances-external-review/corporate/transparency/info-source-sources-federal-government-employee-information.html#fnb1) was established on March 1, 2000 as a result of legislation that contained comprehensive amendments to modernize the [*National Defence Act* (NDA)](http://laws-lois.justice.gc.ca/eng/acts/n-5/index.html). These amendments are designed to help renew the Canadian Armed Forces (CAF). One of the reforms was aimed at creating an independent review of grievances through the establishment of the Committee. The establishment of the Committee is defined in section 29.16 of the NDA. Article 7.21 of the *Queen's Regulations and Orders applicable to the Canadian Forces* (QR and O) that govern the types of grievances referred to the Committee came into effect on June 15, 2000. The Committee is an independent administrative tribunal reporting to Parliament through the Minister of National Defence.

EN — `institutions_infosource_docs/ati-schedule-i-military-grievances-external-review-committee/classes_of_records_en.md:62` — Responsibilities

The Committee reviews military grievances referred to it and provides findings and recommendations (F&R) to the Chief of the Defence Staff (CDS) and the officer or non-commissioned member who submitted the grievance.

The Committee also has the obligation to deal with all matters before it as informally and expeditiously as the circumstances and the considerations of fairness permit.

FR — `institutions_infosource_docs/ati-schedule-i-military-grievances-external-review-committee/classes_of_records_fr.md:58` — Historique

Le Comité externe d’examen des griefs militaires (CEEGM) (*anciennement le Comité des griefs des Forces canadiennes*)[Note de bas de page 1](/fr/externe-examen-griefs-militaires/organisation/transparence/info-source-sources-renseignements-gouvernement-federal-fonctionnaires-federaux.html#fnb1) a été créé le 1er mars 2000 suite à des dispositions législatives qui contenaient des modifications étendues visant à moderniser la [*Loi sur la défense nationale*](http://laws-lois.justice.gc.ca/fra/lois/n-5/index.html) (LDN). Ces modifications ont été conçues pour favoriser le renouveau des Forces armées canadiennes (FAC). Entre autres, l'une de ces réformes portait sur la mise sur pied d'un processus indépendant d'examen des griefs par le biais de la création du CEEGM. Cette procédure est définie à l'article 29.16 de la LDN. L'article 7.21 des *Ordonnances et règlements royaux applicables aux Forces canadiennes* (ORFC) gouvernant le type de griefs renvoyés au Comité est entré en vigueur le 15 juin 2000. Le Comité est un tribunal administratif indépendant qui relève du Parlement par l'entremise du ministre de la Défense nationale.

FR — `institutions_infosource_docs/ati-schedule-i-military-grievances-external-review-committee/classes_of_records_fr.md:62` — Responsabilités

Le Comité examine les griefs des militaires qui lui sont référés et il formule des conclusions et des recommandations (C et R) à l'intention du Chef d'état-major de la Défense (CEMD) et de l'officier ou du militaire du rang qui a soumis le grief.

Dans la mesure où les circonstances et l'équité le permettent, le Comité doit également agir avec célérité et sans formalisme.

### National Defence

EN — `institutions_infosource_docs/ati-schedule-i-department-of-national-defence/classes_of_records_en.md:116` — Background

In most respects, DND is an organization like other departments of government. It was established in 1923 by the [*National Defence Act*](http://laws-lois.justice.gc.ca/eng/acts/N-5/), which sets out the Minister's responsibilities, including the Minister's responsibility for the Department and the CAF. Under the *Act*, the CAF are an entity separate and distinct from the Department.

The Governor General of Canada is the Commander-in-Chief of Canada. DND reports to parliament via the [Minister of National Defence](/en/government/ministers/bill-blair.html). The [Deputy Minister of National Defence](/en/department-national-defence/corporate/organizational-structure/deputy-minister-national-defence.html) is the Department's senior civil servant and the CAF are headed by the [Chief of the Defence Staff](/en/department-national-defence/corporate/organizational-structure/chief-defence-staff.html).

On behalf of the people of Canada, the Canadian Armed Forces (CAF), with the support of the Department of National Defence (DND), stand ready to perform three key roles:

EN — `institutions_infosource_docs/ati-schedule-i-department-of-national-defence/classes_of_records_en.md:132` — Responsibilities

The Defence mission is to defend Canada and Canadian interests and values while contributing to international peace and security.

The Canadian Armed Forces and the Department of National Defence have complementary roles to play in providing advice and support to the Minister of National Defence and in implementing the decisions of the Government on the defence of Canada and of Canadian interests at home and abroad. The separate authorities of the Deputy Minister and the Chief of the Defence Staff give rise to different responsibilities.

View the [Departmental Organizational Structure](/en/department-national-defence/corporate/organizational-structure.html) here.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-national-defence/classes_of_records_fr.md:116` — Historique

À bien des égards, le ministère de la Défense nationale s'apparente aux autres ministères. Il a été créé en 1923 en vertu de la [*Loi sur la défense nationale*](http://laws-lois.justice.gc.ca/fra/lois/N-5/), qui énonce les responsabilités du Ministre et qui rend ce dernier responsable notamment du ministère et des Forces armées canadiennes. En vertu de la *Loi*, les FAC sont une entité séparée et distincte du ministère.

Le gouverneur général du Canada est le commandant en chef du Canada. Le MDN relève du Parlement par l'intermédiaire du [ministre de la Défense nationale](/fr/gouvernement/ministres/bill-blair.html). Le [sous-ministre de la Défense nationale](/fr/ministere-defense-nationale/organisation/structure-organisationnelle/sous-ministre-defense-nationale.html) est le plus haut fonctionnaire du Ministère. Les FAC sont sous les ordres du [chef d'état-major de la Défense](/fr/ministere-defense-nationale/organisation/structure-organisationnelle/chef-etat-major-defense.html).

Au nom de la population canadienne, les Forces armées canadiennes (FAC), avec l'appui du ministère de la Défense nationale (MDN), sont prêtes à exécuter trois rôles essentiels :

FR — `institutions_infosource_docs/ati-schedule-i-department-of-national-defence/classes_of_records_fr.md:132` — Responsabilités

La mission de la Défense consiste à défendre le Canada, ses intérêts et ses valeurs, tout en contribuant à la paix et à la sécurité internationales.

Les Forces armées canadiennes et le ministère de la Défense nationale ont des rôles complémentaires à jouer pour conseiller et appuyer le ministre de la Défense nationale et appliquer les décisions du gouvernement qui intéressent la défense du Canada et les intérêts du Canada au pays et à l'étranger. Les pouvoirs distincts du sous-ministre et du Chef d'état-major de la Défense mettent en évidence des responsabilités différentes.

Voir la [Structure organisationnelle du ministère](/fr/ministere-defense-nationale/organisation/structure-organisationnelle.html) ici.

### National Film Board

EN — `institutions_infosource_docs/ati-schedule-i-national-film-board/classes_of_records_en.md:77` — Background

The National Film Board (NFB) was created by an Act of Parliament, the [*National Film Act*](http://lois-laws.justice.gc.ca/eng/acts/N-8/page-1.html), in 1939 and is a federal agency that reports to Parliament through the Minister of Canadian Heritage.

EN — `institutions_infosource_docs/ati-schedule-i-national-film-board/classes_of_records_en.md:81` — Responsibilities

The National Film Board’s (NFB) mandate is to create and produce relevant, innovative audiovisual content that reflects the diversity of Canada and interprets the country to both domestic and global audiences. The NFB collaborates with filmmakers and artists from all regions of Canada to produce documentaries, animated films, and interactive/immersive works that are deeply rooted in Canadian experiences and realities. A long-standing leader in technological and film innovation on both the national and international stages, the NFB consistently champions the perspectives and experiences of communities underrepresented in mainstream media. Furthermore, the NFB is committed to exploring and adopting new storytelling forms and approaches.

Since its founding, the NFB has produced over 14,000 titles, earning more than 5,000 awards and inspiring generations of filmmakers across Canada and the world. Notably, the NFB has supported the work of First Nations, Métis, and Inuit directors since 1968, resulting in more than 450 titles. This deep and enduring partnership with Indigenous filmmakers and communities forms the foundation of the NFB’s Indigenous Action Plan, aimed at fostering the accessibility of these works to audiences throughout Canada.

As Canada's public producer and distributor of audiovisual content, the NFB documents the nation’s history and culture, offering unique insights into its diversity and vibrancy. By working with a broad range of creators and co-producers—including Indigenous, linguistic, racialized, and other underrepresented groups—the NFB ensures that a wide array of voices and viewpoints are represented. With a focus on seizing new artistic and technological opportunities, the NFB invests in innovative formats such as documentary, auteur animation, and interactive media, prioritizing creativity and social relevance at the heart of its productions.

### National Research Council Canada

EN — `institutions_infosource_docs/ati-schedule-i-national-research-council-of-canada/classes_of_records_en.md:283` — Background

The National Research Council of Canada (NRC) is an agency of the Government of Canada established in 1916. Operating under the [*NRC Act*](http://www.laws.justice.gc.ca/eng/acts/N-15/), its mission is to work with clients and partners, provide innovation support, strategic research, scientific and technical services to develop and deploy solutions to meet Canada's current and future industrial and societal needs. The NRC reports to Parliament through the Minister of Industry. It is governed by a council of appointees drawn from its client community.

EN — `institutions_infosource_docs/ati-schedule-i-national-research-council-of-canada/classes_of_records_en.md:287` — Responsibilities

As stated in the *NRC Act*, the agency is responsible for: undertaking, assisting or promoting scientific and industrial research in different fields of importance to Canada; establishing, operating and maintaining a national science library; publishing and selling or otherwise distributing such scientific and technical information as the Council deems necessary; investigating standards and methods of measurement; working on the standardization and certification of scientific and technical apparatus and instruments and materials used or usable by Canadian industry; operating and administering any astronomical observatories established or maintained by the Government of Canada; administering NRC's research and development activities, including contributions used to support a number of international activities; and providing vital scientific and technological services to the research and industrial communities.

FR — `institutions_infosource_docs/ati-schedule-i-national-research-council-of-canada/classes_of_records_fr.md:280` — Historique

Le Conseil national de recherches Canada (CNRC) est un organisme fédéral créé en 1916. En vertu de la [Loi sur le CNRC](http://www.laws.justice.gc.ca/fra/lois/N-15/), sa mission est de collaborer avec ses clients et ses partenaires, de soutenir l'innovation, d'effectuer des recherches stratégiques et d'offrir des services scientifiques et techniques pour développer et déployer des solutions qui répondront aux besoins actuels et futurs de l'industrie et de la société canadienne. Le CNRC fait rapport au Parlement par le biais du ministre de l'industrie. Il est administré par un conseil de membres choisis parmi sa clientèle.

FR — `institutions_infosource_docs/ati-schedule-i-national-research-council-of-canada/classes_of_records_fr.md:284` — Responsabilités

La Loi du CNRC stipule que cet organisme fédéral a le rôle suivant : entreprendre, aider ou promouvoir des recherches scientifiques et industrielles, en particulier dans les domaines d'importance pour le Canada; mettre sur pied une bibliothèque scientifique nationale et en assurer le fonctionnement selon son évaluation des besoins; vendre ou diffuser par tout autre moyen de l'information scientifique et technique; mener des recherches sur les unités et les techniques de mesure; normaliser et homologuer des appareils et instruments scientifiques et techniques, et les matériaux à l'usage de l'industrie canadienne; assurer le fonctionnement et la gestion des observatoires astronomiques mis sur pied ou exploités par le gouvernement du Canada; administrer ses activités de recherche et de développement, y compris les contributions soutenant diverses activités internationales; et dispenser des services scientifiques et technologiques essentiels à la collectivité scientifique et industrielle.

### Nunavut Water Board

EN — `institutions_infosource_docs/ati-schedule-i-nunavut-water-board/classes_of_records_en.md:33` — Background

The Nunavut Water Board (NWB or Board) is an Institution of Public Government established in 1996 pursuant to Article 13 of the *Nunavut Land Claims Agreement*.  The Board’s mandate and jurisdiction are further detailed in the *Nunavut Waters and Nunavut Surface Rights Tribunal Act*proclaimed on April 30, 2002 and its associated *Regulations*, effective since April 18, 2013*.*

The Board is composed of nine (9) members, including the Chairperson who is also the Chief Executive Officer of the Board, appointed for a term of three (3) years by the Minister of Aboriginal Affairs and Northern Development Canada.

As for the other members of the Board, one half are appointed on the nomination of the Designated Inuit Organization; one quarter are appointed on the nomination of the territorial minister responsible for renewable resources, and the territorial minister or ministers designated by an instrument of the Executive Council of Nunavut; and one quarter are appointed by the Minister of Aboriginal Affairs and Northern Development Canada.

EN — `institutions_infosource_docs/ati-schedule-i-nunavut-water-board/classes_of_records_en.md:41` — Responsibilities

The Board provides for the conservation and utilization of waters in Nunavut, except in a National Park, in a manner that will provide the optimum benefit from those waters for the residents of Nunavut in particular and Canadians in general.

Under the *Nunavut Waters and Nunavut Surface Rights Tribunal Act*, any use of water or deposit of waste into water must be approved by the Board. The requirement to obtain approval of the Board applies equally to departments and agencies of the federal and territorial government. The only exclusions are the use of water for domestic purposes, for extinguishing a fire or, in an emergency, for controlling or preventing a flood.

FR — `institutions_infosource_docs/ati-schedule-i-nunavut-water-board/classes_of_records_fr.md:117` — Historique

L'Office des eaux du Nunavut (OEN ou l'Office) est un organisme public créé en 1996 conformément à l'article 13 de l'*Accord sur les revendications territoriales du Nunavut*. Le mandat et la juridiction de l’Office sont définis davantage dans la *Loi sur les eaux du Nunavut et le Tribunal des droits de surface du Nunavut* promulguée le 30 Avril 2002 ainsi que par ses règlements d'application, en vigueur depuis le 18 Avril 2013.

Le Conseil est composé de neuf (9) membres, dont le président, qui est aussi le chef de la direction du Conseil et qui est nommé pour un mandat de trois (3) ans par le ministre des Affaires autochtones et Développement du Nord Canada (AADNC).

En ce qui a trait aux autres membres du Conseil, la moitié sont nommés sur proposition de l'organisation inuit désignée; un quart sont nommés sur proposition du ministre territorial chargé des ressources renouvelables, et le ministre territorial ou ministres territoriaux désigné(s) par un instrument du Conseil exécutif du Nunavut; et un quart sont nommés par le ministre des Affaires autochtones et Développement du Nord Canada.

FR — `institutions_infosource_docs/ati-schedule-i-nunavut-water-board/classes_of_records_fr.md:125` — Responsabilités

L'Office a pour mission de veiller à la conservation et à l'utilisation des eaux du Nunavut, à l'exclusion des parcs nationaux, de la façon la plus avantageuse pour les habitants du Nunavut en particulier et les Canadiens en général.

En vertu de la *Loi sur les eaux du Nunavut et le Tribunal des droits de surface du Nunavut*, toute utilisation des eaux ou tout rejet de déchet dans les eaux doivent être autorisés par l'Office. L'obligation d'obtenir l'autorisation de l'Office s'applique également à tout ministère et agence du gouvernement fédéral et territorial. Les seules exceptions sont l'utilisation des eaux à des fins domestiques, en vue d'éteindre un incendie ou, en cas d'urgence, de contenir ou de prévenir une inondation.

### Office of the Administrator of the Fund for Railway Accidents Involving Designated Goods

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-administrator-of-the-fund-for-railway-accidents-involving-designated-goods/classes_of_records_en.md:78` — Background

Ship and Rail Compensation Canada is Canada's compensation hub for anyone affected by oil spills from ships or boats and by major rail accidents involving crude oil.

Our mission is to help victims, responders, and anyone else affected get financial compensation and to hold polluters responsible for damages, losses, and response costs.

Ship and Rail Compensation Canada is an independent federal office, financed by industry, managing two compensation funds: the Ship Fund and the Rail Fund. Both Funds were originally created in response to major environmental and human disasters.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-administrator-of-the-fund-for-railway-accidents-involving-designated-goods/classes_of_records_fr.md:78` — Contexte

Indemnisation Navire et Rail Canada est le centre d'indemnisation canadien destiné aux personnes touchées par des déversements d'hydrocarbures provenant de navires ou de bateaux et par des accidents ferroviaires majeurs impliquant du pétrole brut.

Notre mission est d'aider les victimes, les intervenants et toutes les autres personnes touchées à obtenir une indemnisation et de tenir les pollueurs responsables des dommages, des pertes et des coûts d'intervention.

Indemnisation Navire et Rail Canada est une organisation fédérale indépendante financée par l'industrie qui gère deux fonds d'indemnisation : le Fonds Navire et le Fonds Rail. Les deux fonds ont été créés en réponse à des désastres environnementaux et humains majeurs.

### Office of the Administrator of the Ship-source Oil Pollution Fund

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-administrator-of-the-ship-source-oil-pollution-fund/classes_of_records_en.md:78` — Background

Ship and Rail Compensation Canada is Canada's compensation hub for anyone affected by oil spills from ships or boats and by major rail accidents involving crude oil.

Our mission is to help victims, responders, and anyone else affected get financial compensation and to hold polluters responsible for damages, losses, and response costs.

Ship and Rail Compensation Canada is an independent federal office, financed by industry, managing two compensation funds: the Ship Fund and the Rail Fund. Both Funds were originally created in response to major environmental and human disasters.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-administrator-of-the-ship-source-oil-pollution-fund/classes_of_records_fr.md:78` — Contexte

Indemnisation Navire et Rail Canada est le centre d'indemnisation canadien destiné aux personnes touchées par des déversements d'hydrocarbures provenant de navires ou de bateaux et par des accidents ferroviaires majeurs impliquant du pétrole brut.

Notre mission est d'aider les victimes, les intervenants et toutes les autres personnes touchées à obtenir une indemnisation et de tenir les pollueurs responsables des dommages, des pertes et des coûts d'intervention.

Indemnisation Navire et Rail Canada est une organisation fédérale indépendante financée par l'industrie qui gère deux fonds d'indemnisation : le Fonds Navire et le Fonds Rail. Les deux fonds ont été créés en réponse à des désastres environnementaux et humains majeurs.

### Office of the Auditor General of Canada

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-auditor-general-of-canada/classes_of_records_en.md:145` — Background

The Auditor General of Canada is an Officer of Parliament, who is independent from the government and reports directly to Parliament through the Speaker of the House of Commons. Established in 1878, the Auditor General audits federal government departments and agencies, most Crown corporations, and many other federal organizations, and reports publicly to the House of Commons on matters that the Auditor General believes should be brought to its attention. The Auditor General of Canada is also the auditor for the governments of Nunavut, the Yukon, and the Northwest Territories, and reports directly to their legislative assemblies. The Auditor General’s powers and responsibilities are set forth in the *[Auditor General Act](https://laws.justice.gc.ca/eng/acts/A-17/)*.

Information on the Auditor General’s history, reference to its legislative foundation and how it reports to Parliament can be found on our “[Who We Are](https://www.canada.ca/en/auditor-general/about-us.html#who-are-we)” web page.

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-auditor-general-of-canada/classes_of_records_en.md:151` — Responsibilities

The Auditor General’s duties are set out in the *Auditor General Act*, the *[Financial Administration Act](https://laws.justice.gc.ca/eng/acts/F-11/)*, and other acts and orders-in-council. These duties relate to legislative auditing and, in certain cases, to monitoring of federal departments and agencies, Crown corporations, territorial governments, and other entities.

Further information on the Auditor General’s mandate and responsibilities can be found on our “[What We Do](https://www.canada.ca/en/auditor-general/about-us.html#what-we-do)” web page.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-auditor-general-of-canada/classes_of_records_fr.md:145` — Historique

Le vérificateur général est un mandataire du Parlement. Il est indépendant du gouvernement et relève directement du Parlement par l’entremise du Président de la Chambre des communes. Établi en 1878, le Bureau du vérificateur général du Canada audite les ministères et les organismes fédéraux, la plupart des sociétés d’État et de nombreuses autres organisations gouvernementales. Il signale, publiquement, à la Chambre des communes des questions qui, selon lui, devraient être portées à son attention. Le vérificateur général du Canada audite également les administrations du Nunavut, du Yukon et des Territoires du Nord‑Ouest et présente ses rapports directement aux assemblées législatives respectives. Les responsabilités et les pouvoirs du vérificateur général sont énoncés dans la *[Loi sur le vérificateur général](https://laws.justice.gc.ca/fra/lois/a-17/)*.

Vous trouverez l’information sur l’historique du Bureau du vérificateur général, son fondement législatif et son mécanisme de reddition de comptes au Parlement sur notre page Web « [Qui nous sommes](https://www.canada.ca/fr/verificateur-general/a-propos-de-nous.html#who-are-we) ».

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-auditor-general-of-canada/classes_of_records_fr.md:151` — Responsabilités

Les fonctions du vérificateur général sont décrites dans la *Loi sur le vérificateur général,* la *[Loi sur la gestion des finances publiques](https://laws.justice.gc.ca/fra/lois/f-11/)* et d’autres lois et décrets. Ces fonctions ont trait à l’audit législatif et, dans certains cas, à la surveillance des ministères et organismes fédéraux, des sociétés d’État, des administrations territoriales et d’autres entités.

Vous trouverez d’autres renseignements sur le mandat et les responsabilités du vérificateur général sur notre page Web « [Ce que nous faisons](https://www.canada.ca/fr/verificateur-general/a-propos-de-nous.html#what-we-do) ».

### Office of the Information Commissioner

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-information-commissioner/classes_of_records_en.md:88` — Background

The Office of the Information
Commissioner of Canada (OIC) is an independent public body set up in 1983 under the *Access to Information Act* (the Act). The Information Commissioner is appointed by and reports directly to Parliament. The OIC ensures that federal institutions respect the rights that the [*Access to Information Act*](https://laws-lois.justice.gc.ca/eng/acts/A-1/index.html) confers to information requesters. Protecting and advancing the right of access to public sector information ultimately enhances the transparency and accountability of the federal government.

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-information-commissioner/classes_of_records_en.md:93` — Responsibilities

The Office is headed by the Information Commissioner who is supported by one Assistant Information Commissioner also appointed by the Governor in Council. Our primary responsibility is to conduct efficient, fair and confidential investigations into complaints about federal institutions’ handling of access to information requests. We strive to maximize compliance with the Act while fostering disclosure of public sector information using the full range of tools, activities and powers at the Commissioner’s disposal, from information and mediation to persuasion and litigation, where required.

We use mediation and persuasion to resolve complaints. In doing so, we give complainants, heads of federal institutions and all third parties affected by complaints an opportunity to make representations. We encourage institutions to disclose information as a matter of course and to respect Canadians’ rights to request and receive information, in the name of transparency and accountability.

We also support the Information Commissioner in her advisory role to Parliament and parliamentary committees on all access to information matters. We actively make the case for greater freedom of information in Canada through targeted initiatives such as Right to Know Week, and ongoing dialogue with Canadians, Parliament and federal institutions.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-information-commissioner/classes_of_records_fr.md:88` — Historique

Le Commissariat à l’information du Canada (CI) est un organisme public indépendant, créé en 1983 en vertu de la *Loi sur l’accès à l’information* (la *Loi*). La commissaire à l’information est nommée par le Parlement et relève directement de celui-ci. La Commissariat veille à ce que les institutions gouvernementales respectent les droits que la [*Loi sur l’accès à l’information*](https://laws-lois.justice.gc.ca/fra/lois/A-1/index.html) confère aux demandeurs d’information. La protection et la promotion du droit d’accès à l’information du secteur public favorisent en fin de compte la transparence et la reddition de comptes de l’administration fédérale.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-information-commissioner/classes_of_records_fr.md:92` — Responsabilités

Le Commissariat est dirigé par la commissaire à l'information avec l’appui du commissaire à l'information adjoint qui est également nommé par le gouverneur en conseil. Notre principale responsabilité consiste à réaliser des enquêtes efficaces, équitables et confidentielles lorsqu’une plainte est formulée quant au traitement d’une demande d’accès à l’information par une institution fédérale. Nous nous efforçons de maximiser la conformité à la *Loi* tout en encourageant la divulgation de l’information du secteur public en utilisant toute la gamme d’outils, d’activités et de pouvoirs qui sont à la disposition du Commissariat.

Nous privilégions le recours à la médiation et à la persuasion afin de résoudre les plaintes. Ainsi, nous accordons aux plaignants, aux responsables d’institutions fédérales et aux tiers concernés par les plaintes une possibilité raisonnable de présenter leurs observations. Au nom de la transparence et de la reddition de comptes, nous encourageons les institutions à divulguer leur information dans le cadre de leurs activités courantes et à respecter le droit des Canadiens de demander et d’obtenir des renseignements. Nous portons des affaires devant la Cour fédérale pour veiller à ce que la *Loi* soit correctement appliquée et interprétée afin de maximiser la divulgation de l’information.

Le Commissariat soutient également la commissaire dans son rôle consultatif auprès du Parlement et des comités parlementaires sur toutes les questions se rapportant à l’accès à l’information. Il fait la promotion active d’un plus grand accès à l’information au Canada au moyen d’initiatives ciblées comme la [Semaine du droit à l’information](http://www.oic-ci.gc.ca/rtk-dai-fra/) et d’un [dialogue constant](http://www.oic-ci.gc.ca/fra/rrm-slr-consult.aspx) avec les Canadiens, le Parlement et les institutions fédérales.

### Office of the Privacy Commissioner

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-privacy-commissioner/classes_of_records_en.md:66` — Background

The OPC was created when the *[Privacy Act](https://laws-lois.justice.gc.ca/eng/acts/P-21/)* came into force on July 1, 1983 expanding the privacy rights and protections formerly contained in Part IV of the *[Canadian Human Rights Act](http://laws-lois.justice.gc.ca/eng/acts/h-6/)*.

The OPC’s role was expanded in April, 2000 with the enactment of the *[Personal Information Protection and Electronic Documents Act](http://laws-lois.justice.gc.ca/eng/acts/P-8.6/index.html)* (PIPEDA).

The Privacy Commissioner of Canada is an Officer of Parliament who reports directly to the House of Commons and the Senate.

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-privacy-commissioner/classes_of_records_en.md:74` — Responsibilities

As an ombudsman and guardian of privacy in Canada, the Commissioner enforces two federal laws that focus on the protection of personal information: the *[Privacy Act](https://laws-lois.justice.gc.ca/eng/acts/P-21/)*, which applies to the federal public sector; and PIPEDA, Canada's private-sector privacy law. The [mission](/en/about-the-opc/what-we-do/mm/) of the Office is to protect and promote the privacy rights of individuals.

Learn more about the Office of the Privacy Commissioner here:  [mandate](/en/about-the-opc/what-we-do/mm/), [program responsibilities](/en/about-the-opc/who-we-are/organizational-structure/) and [corporate privacy policy](/en/privacy-and-transparency-at-the-opc/pp/).

The Commissioner's functions and powers to further the privacy rights of Canadians include: investigating complaints, conducting audits and pursuing court action under two federal laws; publicly reporting on the personal information-handling practices of public and private-sector organizations; supporting, undertaking and publishing research into privacy issues; and promoting public awareness and understanding of privacy issues. The Commissioner works independently from other parts of the government to investigate complaints from individuals with respect to the federal public sector and the private sector.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-privacy-commissioner/classes_of_records_fr.md:66` — Historique

Le Commissariat à la protection de la vie privée du Canada (CPVP) a été créé par l’adoption de la [*Loi sur la protection des renseignements personnels*](https://laws-lois.justice.gc.ca/fra/lois/p-21/) le 1er juillet 1983. Cette loi a rehaussé la protection et les droits en matière de vie privée déjà accordés aux personnes par la partie IV de la *[Loi canadienne sur les droits de la personne](http://laws-lois.justice.gc.ca/fra/lois/h-6/)*.

En avril 2000, le rôle du CPVP a pris de l’ampleur lorsque la *[Loi sur la protection des renseignements personnels et les documents électroniques](http://laws-lois.justice.gc.ca/fra/lois/P-8.6/index.html)* (LPRPDE) a été promulguée.

Le commissaire à la protection de la vie privée est un haut fonctionnaire du Parlement qui relève directement de la Chambre des communes et du Sénat.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-privacy-commissioner/classes_of_records_fr.md:74` — Responsabilités

À titre d’ombudsman et de défenseur du droit à la vie privée au Canada, le commissaire est chargé d’appliquer deux lois fédérales relatives à la protection des renseignements personnels : la *Loi sur la protection des renseignements personnels*, qui s’applique au secteur public fédéral, et la LPRPDE, qui s’applique aux activités commerciales du secteur privé canadien. Le Commissariat à la protection de la vie privée du Canada a pour [mission](/fr/a-propos-du-commissariat/ce-que-nous-faisons/mm/) de protéger et de promouvoir le droit des personnes à la vie privée.

Apprenez en plus sur le Commissariat à la protection de la vie privée ici : [mandat](/fr/a-propos-du-commissariat/ce-que-nous-faisons/mm/), [responsabilités de programmes](/fr/a-propos-du-commissariat/qui-nous-sommes/structure-de-lorganisation/), [politique sur la protection des renseignements personnels du Commissariat](/fr/protection-de-la-vie-privee-et-transparence-au-commissariat/pp/).

Les fonctions et pouvoirs du commissaire visant à favoriser le respect du droit à la vie privée sont les suivants : enquêter sur les plaintes, mener des vérifications et intenter des poursuites judiciaires en vertu de deux lois fédérales; publier de l’information sur les pratiques relatives au traitement des renseignements personnels dans les secteurs public et privé; appuyer et effectuer des recherches sur des enjeux liés à la protection de la vie privée et en faire connaître les conclusions; et promouvoir la connaissance et la compréhension des enjeux en matière de vie privée auprès du public. Le commissaire enquête sur les plaintes déposées par des personnes et touchant le gouvernement fédéral et le secteur privé. Il mène ses enquêtes indépendamment de toute autre structure du gouvernement fédéral.

### Office of the Superintendent of Financial Institutions Canada

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-superintendent-of-financial-institutions/classes_of_records_en.md:55` — Background

The background of the department can be viewed on the [About Us](/en/about-osfi "About OSFI") page.

EN — `institutions_infosource_docs/ati-schedule-i-office-of-the-superintendent-of-financial-institutions/classes_of_records_en.md:59` — Responsibilities

The responsibilities of the department can be viewed on the [About Us](/en/about-osfi "About OSFI") page.

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-superintendent-of-financial-institutions/classes_of_records_fr.md:55` — Historique

L'historique du BSIF est affiché dans la page [Qui nous sommes](/fr/propos-du-bsif "À propos du BSIF").

FR — `institutions_infosource_docs/ati-schedule-i-office-of-the-superintendent-of-financial-institutions/classes_of_records_fr.md:59` — Responsabilités

Les responsabilités du BSIF sont affichées dans la page [Qui nous sommes](/fr/propos-du-bsif "À propos du BSIF").

### Parole Board of Canada

EN — `institutions_infosource_docs/ati-schedule-i-parole-board-of-canada/classes_of_records_en.md:81` — Background

For information on the [Board’s history](/en/parole-board/corporate/history-of-parole-in-canada.html), [legislative foundation, and how the PBC reports to Parliament](https://www.canada.ca/en/parole-board/corporate/mandate-and-role.html), follow the links provided.

EN — `institutions_infosource_docs/ati-schedule-i-parole-board-of-canada/classes_of_records_en.md:85` — Responsibilities

The Board carries out its responsibilities through its national office in Ottawa, as well as five regional offices across the country (Pacific/Yukon, Prairies/NWT, Ontario/Nunavut, Quebec and Atlantic). Conditional release decisions are made by Board members in the regions. Board members are supported by staff who schedule hearings, provide information for decision-making, ensure that information for decision-making is shared with offenders, and communicate conditional release decisions to the offender, Correctional Service of Canada (CSC) representatives and others as required. Regional staff also provides information to victims, make arrangements for individuals to observe hearings, and manage requests for access to the Board's decision registry. Board members located at National Office make record suspension decisions and conditional release appeal decisions. Staff at National Office deliver the record suspension and clemency program; develop conditional release, record suspensions and clemency policy; coordinate Board member training; and deliver a program of public information. As well, National Office provides leadership for strategic and operational planning, resource management, performance monitoring, audits and investigations, appeals and an array of internal services.

Follow the links provided to read about the [Board’s mandate](/en/parole-board/corporate/mandate-and-role.html) and [major policies](/en/parole-board/corporate/publications-and-forms/decision-making-policy-manual-for-board-members.html).

FR — `institutions_infosource_docs/ati-schedule-i-parole-board-of-canada/classes_of_records_fr.md:81` — Contexte

Pour obtenir des renseignements sur l’[historique de la Commission](/fr/commission-liberations-conditionnelles/organisation/historique-de-la-liberation-conditionnelle-au-canada.html), son [fondement législatif et la façon dont elle rend des comptes au Parlement](/fr/commission-liberations-conditionnelles/organisation/mandat-et-role.html), veuillez cliquer sur les hyperliens.

FR — `institutions_infosource_docs/ati-schedule-i-parole-board-of-canada/classes_of_records_fr.md:85` — Responsabilités

La Commission exerce ses activités à son bureau national situé à Ottawa et dans ses cinq bureaux régionaux au pays (Pacifique/Yukon, Prairies/Territoires du Nord‑Ouest, Ontario/Nunavut, Québec et Atlantique). Des décisions concernant la mise en liberté sous condition sont prises par les commissaires dans les régions. Les commissaires sont appuyés par des employés qui planifient les audiences, veillent à ce que tous les renseignements nécessaires à la prise de décisions soient remis aux commissaires et transmis aux délinquants et communiquent les décisions sur la mise en liberté sous condition aux délinquants, aux représentants du Service correctionnel du Canada (SCC) et à d’autres personnes intéressées, au besoin. Le personnel des bureaux régionaux fournit aussi des renseignements aux victimes, prend les dispositions requises pour permettre à des personnes d’assister à des audiences à titre d’observateurs et traite les demandes d’accès au registre des décisions de la Commission. Au bureau national, les commissaires prennent des décisions concernant la suspension du casier et les décisions sur la mise en liberté sous condition qui sont portées en appel. Le personnel du bureau national exécute le programme de suspension du casier et d’exercice de la prérogative royale de clémence, élabore des politiques sur la mise en liberté sous condition, la suspension du casier et la clémence, coordonne la formation des commissaires et gère un programme d’information du public. Le bureau national assure également un leadership pour la planification stratégique et opérationnelle, la gestion des ressources, la surveillance du rendement, les vérifications et enquêtes, les appels et divers services internes.

Cliquez sur les hyperliens pour en savoir davantage sur le [mandat de la Commission](/fr/commission-liberations-conditionnelles/organisation/mandat-et-role.html) et les [politiques pertinentes](/fr/commission-liberations-conditionnelles/organisation/publications-et-formulaires/manuel-des-politiques-decisionnelles-a-l-intention-des-commissaires.html).

### Patented Medicine Prices Review Board Canada

EN — `institutions_infosource_docs/ati-schedule-i-patented-medicine-prices-review-board/classes_of_records_en.md:88` — Background

The Patented Medicine Prices Review Board (PMPRB) is an independent quasi-judicial body created as a result of revisions to the [*Patent Act*](http://www.laws-lois.justice.gc.ca/eng/acts/P-4/) (Bill C-22) and came into force on December 7, 1987. Subsequent revisions to the *Patent Act* in 1993 (Bill C-91) shifted ministerial responsibility to the Minister of Health and increased the Board’s remedial powers. The Minister of Health is responsible for the pharmaceutical provisions of the *Patent Act* as set out in sections 79 to 103. Although part of the Health Portfolio, the PMPRB carries out its [mandate](http://www.pmprb-cepmb.gc.ca/about-us/mandate-and-jurisdiction) at arm’s length from the Minister of Health. It also operates independently of other bodies such as Health Canada, which approves drugs for safety and efficacy; federal, provincial, and territorial public drug plans, which are responsible for approving the listing of drugs on their respective formularies and determining price levels for the purpose of reimbursement; and the Common Drug Review, which provides listing recommendations based on cost-effectiveness to participating public drug plans.

EN — `institutions_infosource_docs/ati-schedule-i-patented-medicine-prices-review-board/classes_of_records_en.md:92` — Responsibilities

The *Patent Act* provides that the [Board](http://www.pmprb-cepmb.gc.ca/about-us/organizational-structure) is to consist of no more than five members, appointed, on a part-time basis, by the Governor in Council, including a Chairperson and Vice-Chairperson. The Board’s [Chairperson](http://www.pmprb-cepmb.gc.ca/about-us/organizational-structure#Chairperson) is designated under the legislation as the Chief Executive Officer of the Board and is granted authority and responsibility to supervise and direct the work of the Board, including the management of its internal affairs and the work of its staff.

The Executive Director manages the work of the staff. Senior staff consists of the Director of Regulatory Affairs and Outreach, the Director of Policy and Economic Analysis, the Director of Corporate Services, the Director of the Board Secretariat, Communications and Strategic Planning, and General Counsel.

The staff provides an information and education program; data collection, storage and dissemination; economic and scientific analysis; case preparation and related services for the registry; and administrative assistance to the Board. It also provides for hearings prior to the making of remedial orders by the Board.

### Prince Rupert Port Authority

EN — `institutions_infosource_docs/ati-schedule-i-prince-rupert-port-authority/classes_of_records_en.md:245` — Background

The Prince Rupert Port Authority (PRPA) is a local port authority constituted under the [Canada Marine Act](https://laws-lois.justice.gc.ca/eng/acts/C-6.7/page-1.html), and [Letters Patent](https://www.rupertport.com/letters-patent/) issued under the Act, to operate the Port in the Prince Rupert Harbour. We’re an autonomous and commercially viable agency, governed by an independent Board of Directors with full control over all Port decisions. Our mandate is to facilitate and expand the movement of cargo and passengers through the Port of Prince Rupert.

The PRPA reports to Parliament through the Minister of Transport. For more information about the history of the PRPA, visit the [About Page](https://www.rupertport.com/about/).

FR — `institutions_infosource_docs/ati-schedule-i-prince-rupert-port-authority/classes_of_records_fr.md:242` — Contexte

L’Administration portuaire de Prince Rupert est une administration portuaire locale constituée en vertu de la [Loi maritime du Canada](https://laws-lois.justice.gc.ca/fra/lois/c-6.7/page-1.html) et des [lettres patentes](https://www.rupertport.com/fr/lettres-patentes/) délivrées au titre de cette loi, pour exploiter le port dans le havre de Prince Rupert. Nous sommes une agence autonome et commercialement viable, dirigée par un conseil d’administration indépendant qui contrôle toutes les décisions du port. Notre mandat est de faciliter et de développer le mouvement des marchandises et des passagers dans le port de Prince Rupert.

L’APPR donne ses rapports au Parlement parmi le ministre de Transports. Pour plus d’information à propos du patrimoine de l’APPR, visitez : [À propos de.](https://www.rupertport.com/fr/)

### Privy Council Office

EN — `institutions_infosource_docs/ati-schedule-i-privy-council-office/classes_of_records_en.md:71` — Background

Privy Council Office (PCO) came into being under the *Constitution Act of 1867* to "aid and advise in the Government of Canada."

The Federal-Provincial Relations Office (FPRO), formerly established as a federal department on January 1, 1975, was re-integrated with the Privy Council Office effective June 25, 1993.

The Privy Council Office (PCO) reports directly to the Prime Minister and is headed by the Clerk of the Privy Council and the Secretary to the Cabinet. PCO is both the Cabinet secretariat and the Prime Minister’s source of public service advice across the entire spectrum of policy questions and operational issues facing the Government.

EN — `institutions_infosource_docs/ati-schedule-i-privy-council-office/classes_of_records_en.md:79` — Responsibilities

The [Privy Council Office](/en/privy-council.html) is the hub of public service support to the Prime Minister, other Ministers in the Prime Minister’s portfolio, and Cabinet and its decision-making structures. Led by the Clerk of the Privy Council, PCO facilitates the smooth and effective operations of Cabinet and the Government of Canada through the work of PCO secretariats.

The main roles of PCO are to: provide professional, non-partisan advice and operational support to the Prime Minister and other Ministers in the Prime Minister's portfolio, and to Cabinet, on questions of national, intergovernmental and international importance; manage the Cabinet's decision-making system by challenging and co-ordinating departmental policy, legislative and communications proposals, conducting policy, legal, legislative and communications analysis, and providing secretariat support to the Cabinet and its committees and on the practices and conventions of our Westminster system of government; provide advice on the appropriate structure and organization of the government and its entities; advance the development of the government's agenda across federal departments and agencies and with external stakeholders; help foster a high-performing and accountable public service for the 21st century; manage the appointment process for senior positions in federal departments, Crown corporations and agencies; and provide administrative support to the Prime Minister's Office, Ministers' offices within the Prime Minister's portfolio, commissions of inquiry, task forces and other independent bodies considering matters associated with good governance in Canada.

FR — `institutions_infosource_docs/ati-schedule-i-privy-council-office/classes_of_records_fr.md:71` — Historique

Le Bureau du Conseil privé (BCP) a été établi en vertu de la *Loi constitutionnelle de 1867* pour « aider et aviser, dans l’administration du gouvernement du Canada ».

Le Bureau des relations fédérales-provinciales (BRFP), devenu un ministère fédéral le 1er janvier 1975, a été réintégré au BCP le 25 juin 1993.

Le Bureau du Conseil privé (BCP) relève directement du Premier ministre, et il est dirigé par le greffier du Conseil privé et secrétaire du Cabinet. Le BCP est à la fois le secrétariat du Cabinet et l’organisme de la fonction publique qui conseille le Premier ministre sur toute la gamme des questions stratégiques et opérationnelles intéressant le gouvernement.

FR — `institutions_infosource_docs/ati-schedule-i-privy-council-office/classes_of_records_fr.md:79` — Responsabilités

Le [BCP](/fr/conseil-prive.html) est le principal centre d’activités à partir duquel la fonction publique soutient le Premier ministre, les autres ministres de son portefeuille ainsi que le Cabinet et ses structures décisionnelles. Sous la direction du greffier du Conseil privé, le BCP, par l’intermédiaire de ses secrétariats, favorise le bon fonctionnement du Cabinet et du gouvernement du Canada.

Les principaux rôles du BCP sont : fournir des conseils professionnels et impartiaux ainsi que du soutien opérationnel au Premier ministre, aux ministres relevant de son portefeuille et au Cabinet sur des questions de portée nationale, intergouvernementale et internationale; administrer le système décisionnel du Cabinet, c’est-à-dire exercer une fonction d’examen critique concernant les projets de politiques, de législation et de communication des ministères et les coordonner, faire l’analyse politique, juridique, législative et des communications, et fournir au Cabinet et à ses comités des services de secrétariat et du soutien concernant les pratiques et les conventions propres au système de gouvernement britannique; fournir des conseils sur la structure et l’organisation du gouvernement et des entités qui le composent; favoriser la concrétisation du programme du gouvernement dans les ministères et les organismes, ainsi qu’auprès des intervenants externes; promouvoir pour le XXIe siècle une fonction publique efficace et responsable; gérer le processus de nomination aux postes de cadres supérieurs dans les ministères fédéraux, les sociétés d’État et les organismes; fournir du soutien administratif aux cabinets du Premier ministre et des ministres relevant de son portefeuille, aux commissions d’enquête, aux groupes de travail et aux autres entités indépendantes qui ont pour mandat d’examiner des questions liées à la bonne gouvernance du Canada.

### Public Health Agency of Canada

EN — `institutions_infosource_docs/ati-schedule-i-public-health-agency-of-canada/classes_of_records_en.md:89` — Background

In September 2004, the Public Health Agency of Canada (PHAC or the Agency) was established and confirmed as a legal entity in December 2006, by the Public Health Agency of Canada Act. The Agency's primary goal is to strengthen Canada's capacity to protect and improve the health of Canadians and to help reduce pressures on the health care system. The Agency's activities focus on prevention and control of chronic and infectious diseases, injury prevention and public health emergency preparedness and response.

The Agency is one of six departments and agencies that make up the federal government's Health Portfolio and reports to Parliament through the Minister of Health. The Agency is managed by the Chief Public Health Officer of Canada and the President of [the Public Health Agency of Canada](/en/public-health.html).

For more information, please consult: [Background](/en/public-health/corporate/mandate/about-agency/background.html)

EN — `institutions_infosource_docs/ati-schedule-i-public-health-agency-of-canada/classes_of_records_en.md:97` — Responsibilities

Public health involves the organized efforts of society to keep people healthy and to prevent injury, illness and premature death. It includes programs, services and policies that protect and promote the health of all Canadians. In Canada, public health is a responsibility that is shared by the three levels of government, the private sector, non-government organizations, health professionals and the public.

FR — `institutions_infosource_docs/ati-schedule-i-public-health-agency-of-canada/classes_of_records_fr.md:87` — Contexte

En septembre 2004, l'Agence de la santé publique du Canada (l'ASPC ou l'Agence) a été créée et son statut de personne morale a été confirmé en décembre 2006 dans la Loi sur l'Agence de la santé publique du Canada. Son principal objectif est de renforcer la capacité du Canada de protéger et d'améliorer la santé de la population et d'aider à réduire les pressions sur le système de soins de santé. L'Agence concentre ses activités sur la prévention et le contrôle des maladies chroniques et infectieuses, la prévention des lésions, ainsi que les mesures et interventions d'urgence en santé publique.

L'ASPC est l'un des six ministères et organismes qui composent le portefeuille de la Santé du gouvernement fédéral et qui rendent des comptes au Parlement par l'intermédiaire du ministre de la Santé. L'Agence est gérée par l'administrateur en chef de la santé publique et la présidente de [l'Agence de la santé publique du Canada](/fr/sante-publique.html).

Pour de plus amples informations, veuillez consulter le site de l'Agence à l'adresse suivante : [Contexte](/fr/sante-publique/organisation/mandat/a-propos-agence/contexte.html).

FR — `institutions_infosource_docs/ati-schedule-i-public-health-agency-of-canada/classes_of_records_fr.md:95` — Responsabilités

La santé publique englobe les efforts organisés de la société pour tenir les gens en santé et pour prévenir les blessures, les maladies et les décès prématurés. Elle comprend des programmes, des services et des politiques qui protègent et favorisent la santé de tous les Canadiens. Au Canada, la santé publique constitue une responsabilité que se partagent les trois paliers de gouvernement, le secteur privé, des organisations non gouvernementales, les professionnels de la santé et le public.

### Public Safety Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-public-safety-and-emergency-preparedness/classes_of_records_en.md:115` — Background

Public Safety Canada was created in 2003 through the amalgamation of the former Department of the Solicitor General, the Office of Critical Infrastructure Protection and Emergency Preparedness (from the Department of National Defence), and Justice Canada's National Crime Prevention Centre. The Department was created to improve integration, efficiency and effectiveness of government safety and security efforts.

The Department of Public Safety and Emergency Preparedness (PSEP) plays a key role in discharging the Government's fundamental responsibility for the safety and security of its citizens. The legislative foundations of the Department are: the [*Department of Emergency Preparedness Act 2005*](https://laws-lois.justice.gc.ca/eng/acts/P-31.55/index.html) and the [*Emergency Management Act 2007*](https://laws-lois.justice.gc.ca/eng/acts/E-4.56/). The Department's Report on Plans and Priorities sets out three essential roles for the Department: (i) support the Minister's responsibility for all matters related to public safety and emergency management not assigned to another federal organization; (ii) support the Minister's responsibility to exercise leadership at the national level for national security and emergency preparedness; and (iii) support the Minister's responsibility for the coordination of Public Safety's Portfolio entities and for setting their strategic priorities. As part of the Main Estimates process, Public Safety Canada reports to Parliament twice per year through the annual submission of [Public Safety Canada Departmental Plan](/cnt/rsrcs/pblctns/index-en.aspx?t=dprtmntl-plnnng) and the [Departmental Results Report](/cnt/rsrcs/pblctns/index-en.aspx?t=dprtmntl-prfrmnc).

The Public Safety Portfolio encompasses nine organizations which directly contribute to the safety and security of Canadians. In addition to Public Safety Canada, the Portfolio includes: Canada Border Service Agency (CBSA); Canadian Security Intelligence Service (CSIS); Correctional Service of Canada (CSC); Parole Board of Canada (PBC); the Royal Canadian Mounted Police (RCMP); the RCMP External Review Committee (ERC); the Civilian Review and Complaints Commission for the RCMP (CRCC); and the Office of the Correctional Investigator (OCI). While Portfolio agencies deliver public security operations according to their mandates, Public Safety Canada, in its portfolio coordination role, brings strategic focus to the overall safety and security agenda.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-public-safety-and-emergency-preparedness/classes_of_records_en.md:123` — Responsibilities

The mandate of Public Safety Canada is to keep Canadians safe from a range of risks such as natural disasters, crime and terrorism.

The Department provides strategic policy advice and support to the Minister of PSEP on a range of issues, including: national security, border strategies, countering crime, emergency management and interoperability. While respecting the separate accountability of each Portfolio agency, the Department supports the Minister in all aspects of his mandate.

The Department also delivers a number of grant and contribution programs related to emergency management, national security and community safety. In addition, Public Safety Canada's Government Operations Centre provides strategic-level coordination and direction on behalf of the Government of Canada in response to events that affect the national interest. Through the development and implementation of clearly articulated policies and programs, the Department works towards the achievement of its strategic outcome: "A safe and resilient Canada".

FR — `institutions_infosource_docs/ati-schedule-i-department-of-public-safety-and-emergency-preparedness/classes_of_records_fr.md:115` — Historique

Le ministère de la Sécurité publique et de la Protection civile (ou Sécurité publique Canada) a été créé en 2003 et regroupe l'ancien ministère du Solliciteur général, le Bureau de la protection des infrastructures essentielles et de la protection civile (qui faisait partie du ministère de la Défense nationale), et le Centre national de la prévention du crime de Justice Canada. L'intention derrière la création du Ministère était de mieux coordonner les efforts du gouvernement fédéral pour assurer la sécurité et la protection de sa population et d'accroître l'efficacité et la rentabilité de ces efforts.

Sécurité publique Canada joue un rôle clé en assumant la responsabilité fondamentale du gouvernement pour la sécurité de ses citoyens. [*La Loi sur le ministère de la Sécurité publique et de la Protection civile (2005)*](https://laws-lois.justice.gc.ca/fra/lois/P-31.55/TexteComplet.html) et la [*Loi sur la gestion des urgences (2007)*](https://laws-lois.justice.gc.ca/fra/lois/E-4.56/). Le Rapport sur les plans et les priorités établit trois rôles essentiels pour le Ministère: (i) appuyer le ministre dans ses responsabilités quant aux questions liées à la sécurité publique et à la gestion des mesures d'urgence qui ne sont pas attribuées à un autre ministre fédéral, ii) appuyer le ministre dans ses responsabilités liées à assumer, à l'échelle nationale, un rôle de premier plan en matière de sécurité publique et de protection civile, et (ii) appuyer le ministre dans ses responsabilités liées à la coordination des organismes du portefeuille de Sécurité publique et à l'établissement de leurs priorités stratégiques. Dans le cadre du processus de Budget principal des dépenses, Sécurité publique Canada rend des comptes deux fois l'an par le biais de la présentation annuelle du [Plan ministériel de Sécurité publique Canada](/cnt/rsrcs/pblctns/index-fr.aspx?t=dprtmntl-plnnng) et du [Rapport sur les résultats ministériels](/cnt/rsrcs/pblctns/index-fr.aspx?t=dprtmntl-prfrmnc).

Le Portefeuille de Sécurité publique compte neuf organismes contribuant directement à la sécurité des Canadiens. En plus du ministère de la Sécurité publique, le Portefeuille comprend: l'Agence des services frontaliers du Canada (ASFC); le Service canadien du renseignement de sécurité (SCRS); le Service correctionnel du Canada (SCC); la Commission nationale des libérations conditionnelles (CNLC); et la Gendarmerie royale du Canada (GRC). Le Portefeuille englobe également trois organes d'examen autonomes : le Comité externe d'examen de la GRC; la Commission des plaintes du public contre la GRC; et le Bureau de l'enquêteur correctionnel. Bien que les agences du Portefeuille livrent des opérations de sécurité publique selon leurs mandats, Sécurité publique Canada, dans son rôle de coordination de portefeuille, permet un alignement stratégique du programme fédéral de sécurité.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-public-safety-and-emergency-preparedness/classes_of_records_fr.md:123` — Responsabilités

Le mandat de Sécurité publique Canada est de travailler à la sécurité du Canada sur tous les plans, allant des catastrophes naturelles aux crimes et au terrorisme.

Le Ministère offre des conseils et du soutien stratégiques au ministre de la SPPC sur divers enjeux, notamment la sécurité nationale, les stratégies frontalières, la lutte contre le crime, la gestion des mesures d'urgence et l'interopérabilité. Tout en respectant l'imputabilité responsabilité distincte de chaque organisme du Portefeuille, le Ministère appuie le ministre dans tous les aspects de son mandat.

Le Ministère offre également un certain nombre de programmes de subventions et de contributions liés à la gestion des mesures d'urgences et à la sécurité des collectivités. En outre, le Centre des opérations du gouvernement de Sécurité publique Canada assure la coordination stratégique au nom du gouvernement du Canada des interventions en cas d'incident possible ou réel qui touche l'intérêt national par l'élaboration et la mise en œuvre de politiques et de programmes clairement définis, le Ministre contribue à l'atteinte de notre objectif stratégique : « un Canada sécuritaire et résilient ».

### Public Service Commission of Canada

EN — `institutions_infosource_docs/ati-schedule-i-public-service-commission/classes_of_records_en.md:95` — Responsibilities

The PSC is responsible for promoting and safeguarding merit-based appointments that are free from political influence and, in collaboration with other stakeholders, for protecting the non-partisan nature of the public service.

FR — `institutions_infosource_docs/ati-schedule-i-public-service-commission/classes_of_records_fr.md:95` — Responsabilités

La CFP est responsable de promouvoir et de protéger les nominations fondées sur le mérite qui sont exemptes de toute influence politique et, de concert avec les autres intervenants, de préserver l'impartialité politique de la fonction publique

### Public Services and Procurement Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-public-works-and-government-services/classes_of_records_en.md:67` — Background

Founded in 1841 and originally known as The Board of Works, the department became Public Services and Procurement Canada (PSPC) in 2015. It was formerly known as Public Works and Government Services Canada (PWGSC) through the joining of the former Supply and Services Canada, Public Works Canada, Government Telecommunications Agency (previously at Communications Canada), and the Translation Bureau (previously at the Secretary of State of Canada).

However, as the title of the department has yet to be legally modified, the title of Public Works and Government Services Canada and its acronym are still in use for legislation, orders in council and contracting purposes only. The department's approved applied title of Public Services and Procurement Canada and its acronym must be used in all other instances.

The Department of Public Works and Government Services Act, passed in 1996, establishes the current department and sets out the legal authorities for PSPC services.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-public-works-and-government-services/classes_of_records_en.md:79` — Responsibilities

PSPC plays an important role in the daily operations of the Government of Canada. It supports federal departments and agencies in reaching their mandated objectives. This is done through its role as their central purchasing agent, real property manager, linguistic authority, treasurer, accountant, pay and pension administrator, and common service provider. Its mission is to deliver high‑quality, central programs and services that ensure sound stewardship on behalf of Canadians and meet the program needs of federal institutions.

As an organization providing government departments, boards and agencies with support services, PSPC delivers on its mandate through 5 core responsibilities: government-wide support, payments and accounting, Procurement Ombud, property and infrastructure and purchase of goods and services.

The Office of the Procurement Ombud (OPO) operates at arm's length from the department. Although it is a PSPC program, the OPO reports to the Minister and is required to operate in an impartial and independent manner. It reviews complaints from suppliers as well as procurement practices in departments and agencies. It also makes recommendations for the improvement of those practices to ensure improved fairness, openness, and transparency in the procurement process.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-public-works-and-government-services/classes_of_records_fr.md:65` — Contexte

Mis sur pied en 1841 et initialement connu comme le Conseil des travaux, le ministère est devenu en 2015 Services publics et Approvisionnement Canada (SPAC), anciennement connu comme Travaux publics et Services gouvernementaux Canada (TPSGC) grâce à la fusion d'Approvisionnements et Services Canada, de Travaux publics Canada, de l'Agence des télécommunications gouvernementales (Communication Canada), et du Bureau de la traduction (Secrétariat d'État du Canada).

Toutefois, comme le titre du ministère n'a pas encore été légalement modifié, le titre de Travaux publics et Services gouvernementaux Canada ainsi que son sigle (TPSGC) continuent d'être utilisés à des fins législatives, de décrets et passation de marchés seulement. Le titre d'usage approuvé du ministère, « Services publics et Approvisionnement Canada », et son acronyme, doivent être utilisés dans tous les autres cas.

La Loi sur le ministère des Travaux publics et des Services gouvernementaux, promulguée en 1996, a créé le Ministère actuel et défini les fondements législatifs de SPAC.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-public-works-and-government-services/classes_of_records_fr.md:77` — Responsabilités

SPAC joue un rôle important dans les activités quotidiennes du gouvernement du Canada. En sa qualité d'acheteur central, de gestionnaire de biens immobiliers, de spécialiste des questions linguistiques, de trésorier, de comptable et d'administrateur de la paye et des pensions du gouvernement et de fournisseur de services communs, il aide les ministères et organismes fédéraux à réaliser les objectifs visés par leur mandat. Sa mission est d'offrir des programmes et des services centraux de première qualité qui favorisent une saine intendance au profit de la population canadienne et qui répondent aux besoins des programmes des institutions fédérales.

En tant qu'organisme chargé de fournir aux ministères, aux conseils et aux organismes fédéraux des services à l'appui de leurs programmes, SPAC réalise son mandat par le truchement de 5 responsabilités essentielles : soutien à l'échelle du gouvernement, paiements et comptabilité, Ombud de l'approvisionnement, biens et infrastructure et achat de biens et de services.

Le Bureau de l'Ombud de l'approvisionnement (BOA) mène ses activités sans lien de dépendance avec le ministère. Bien qu'il s'agisse d'un programme de SPAC, le BOA relève du ministre et doit exercer ses activités de façon impartiale et indépendante. Il examine les plaintes des fournisseurs ainsi que les pratiques d'approvisionnement des ministères et des organismes, et il formule des recommandations dans le but de les améliorer afin de s'assurer de maintenir et d'améliorer l'équité, l'ouverture et la transparence du processus d'approvisionnement.

### RCMP External Review Committee

EN — `institutions_infosource_docs/ati-schedule-i-royal-canadian-mounted-police-external-review-committee/classes_of_records_en.md:79` — Background

The RCMP External Review Committee (ERC) was created through [Part II](http://laws-lois.justice.gc.ca/eng/acts/R-10/) of the *Royal Canadian Mounted Police Act* on December 18, 1986 following the recommendation of the 1976 Report of the Commission of Inquiry Relating to Public Complaints, Internal Discipline and Grievance Procedure within the Royal Canadian Mounted Police. The ERC reports directly to Parliament through the Minister of Public Safety and Emergency Preparedness.

The [*RCMP Act*](http://laws-lois.justice.gc.ca/eng/acts/R-10/index.html) and [*RCMP Regulations*](http://laws.justice.gc.ca/eng/regulations/SOR-2014-281/) were amended on November 28, 2014, following the coming into force of provisions of the *Enhancing RCMP Accountability Act* (2013).

EN — `institutions_infosource_docs/ati-schedule-i-royal-canadian-mounted-police-external-review-committee/classes_of_records_en.md:85` — Responsibilities

The [ERC](https://www.canada.ca/en/rcmp-external-review-committee/corporate/organization/mandate.html) is an independent and impartial administrative tribunal that contributes to fair and equitable labour relations within the Royal Canadian Mounted Police (RCMP). To this end, the ERC conducts an independent review of certain categories of grievances, and appeals relating to certain conduct measures imposed on RCMP members and written decisions involving harassment complaints, revocations of appointments, discharges and demotions and ordered stoppages of pay and allowances, all as referred to it pursuant to the *RCMP Act* and the *RCMP Regulations*. The ERC's jurisdiction is restricted to employment and labour matters that relate to regular members and civilian members of the RCMP.

FR — `institutions_infosource_docs/ati-schedule-i-royal-canadian-mounted-police-external-review-committee/classes_of_records_fr.md:79` — Contexte

Le [Comité externe d'examen de la GRC](/fr/comite-externe-examen-grc/organisation/propos-notre-organisation/bienvenue-au-comite-externe-dexamen-de-la-grc.html) (CEE) a été créé en vertu de la [Partie II](http://laws-lois.justice.gc.ca/fra/lois/R-10/index.html) de la *Loi sur la Gendarmerie royale du Canada*, le 18 décembre 1986, à la suite d'une recommandation du Rapport de la Commission d'enquête sur les plaintes du public, la discipline interne et le règlement des griefs au sein de la Gendarmerie royale (1976). Le CEE rend compte de ses activités directement au Parlement par l'entremise du ministre de la Sécurité publique et de la Protection civile.

La *[Loi sur la Gendarmerie royale du Canada](http://laws-lois.justice.gc.ca/fra/lois/R-10/index.html)* et le *[Règlement de la Gendarmerie royale du Canada](http://laws.justice.gc.ca/fra/reglements/DORS-2014-281/)* ont été modifiés le 28 novembre 2014, après l'entrée en vigueur de dispositions de la *Loi visant à accroître la responsabilité de la GRC* (2013).

FR — `institutions_infosource_docs/ati-schedule-i-royal-canadian-mounted-police-external-review-committee/classes_of_records_fr.md:85` — Responsabilités

Le [CEE](/fr/comite-externe-examen-grc/organisation/propos-notre-organisation/mandat.html) est un tribunal administratif indépendant et impartial qui favorise des relations de travail justes et équitables au sein de la Gendarmerie royale du Canada (GRC). À cette fin, le CEE assure un examen indépendant de certaines catégories de griefs et des appels visant les mesures disciplinaires prises envers les membres de la GRC et les décisions écrites liées à des plaintes de harcèlement, des révocations de nomination, des licenciements et des rétrogradations ainsi que des ordonnances de cessation de la solde et des indemnités qui lui sont renvoyés en vertu de la *Loi sur la Gendarmerie royale du Canada* et du *Règlement de la Gendarmerie royale du Canada*. La compétence du CEE se limite aux questions relatives à l'emploi et aux relations de travail des membres réguliers et des membres civils de la GRC.

### Secretariat of the National Security and Intelligence Committee of Parliamentarians

EN — `institutions_infosource_docs/ati-schedule-i-secretariat-of-the-national-security-and-intelligence-committee-of-parliamentarians/classes_of_records_en.md:73` — Background

The Secretariat assists the National Security and Intelligence Committee of Parliamentarians in fulfilling its mandate, which is to review:

EN — `institutions_infosource_docs/ati-schedule-i-secretariat-of-the-national-security-and-intelligence-committee-of-parliamentarians/classes_of_records_en.md:81` — Responsibilities

The Secretariat assists the National Security and Intelligence Committee of Parliamentarians in fulfilling its mandate. It ensures the Committee receives timely access to relevant, classified information and strategic and expert advice in the exercise of Committee reviews. It assists in the development of Committee reports and provides support to ensure compliance with security requirements.

FR — `institutions_infosource_docs/ati-schedule-i-secretariat-of-the-national-security-and-intelligence-committee-of-parliamentarians/classes_of_records_fr.md:73` — Contexte

Le Secrétariat aide le Comité des parlementaires sur la sécurité nationale et le renseignement à s’acquitter de son mandat, qui consiste à examiner :

FR — `institutions_infosource_docs/ati-schedule-i-secretariat-of-the-national-security-and-intelligence-committee-of-parliamentarians/classes_of_records_fr.md:81` — Responsabilités

Le Secrétariat aide le Comité des parlementaires sur la sécurité nationale et le renseignement à remplir son mandat. Il veille à ce que le Comité ait rapidement accès à l’information classifiée pertinente, ainsi qu’à des conseils stratégiques et d’experts dans le cadre de ses examens. Il contribue à l’élaboration des rapports du Comité et fournit un soutien pour assurer le respect des exigences de sécurité.

### Sept-Îles Port Authority

EN — `institutions_infosource_docs/ati-schedule-i-sept-iles-port-authority/classes_of_records_en.md:57` — Background

The Port of Sept-Îles is a large deep-water (over 80 m) natural harbour located 650 km downstream from Quebec City on the North Shore of the St. Lawrence that is open to year-round navigation.

The Sept-Îles Port Authority was created on May 1, 1999, by letters patent issued by the Minister of Transport under Section 8 of the *Canada Marine Act*. It is therefore a Canadian Port Authority and an agent of Her Majesty in right of Canada under the aforementioned Act.

The Port of Sept-Îles is governed by a Board of Directors and reports to Parliament through the Minister of Transport.

EN — `institutions_infosource_docs/ati-schedule-i-sept-iles-port-authority/classes_of_records_en.md:69` — Responsibilities

The Sept-Îles Port Authority helps implement the *National Marine Policy*, which provides Canada with the necessary marine infrastructure and effective support to achieve its local, regional and national economic and social objectives while ensuring and protecting the country’s competitiveness and trade.

Navigable waters under the jurisdiction of the Sept-Îles Port Authority and federal real property under its purview and those it occupies, or holds are listed in appendices A and B of its letters patent.

The Sept-Îles Port Authority has the powers of a natural person. Its jurisdiction to manage a port is limited to the power to undertake port activities involving shipping, navigation, passenger transportation and the handling and storage of goods, to the extent that they are contained in the letters patent, and other activities deemed necessary to support the operation of the port in accordance with the letters patent.

FR — `institutions_infosource_docs/ati-schedule-i-sept-iles-port-authority/classes_of_records_fr.md:57` — Historique

Situé à 650 km en aval de Québec, sur la rive nord du Saint-Laurent, le port en eau profonde de Sept-Îles est un vaste havre naturel de plus de 80 m de profondeur ouvert à la navigation toute l’année.

L’Administration portuaire de Sept-Îles a été fondée le 1er mai 1999 par lettres patentes du ministère des Transports émises en vertu du paragraphe 8 de la Loi maritime du Canada. Il s’agit ainsi d’une administration portuaire canadienne et d’une mandataire de Sa Majesté du chef du Canada dans le cadre de la loi susmentionnée.

Dirigée par un conseil d’administration, elle rend compte au Parlement par l’intermédiaire du ministre des Transports.

FR — `institutions_infosource_docs/ati-schedule-i-sept-iles-port-authority/classes_of_records_fr.md:69` — Responsabilités

L’Administration portuaire de Sept-Îles contribue à la mise en œuvre de la Politique maritime nationale qui offre au Canada l’infrastructure maritime nécessaire et un appui efficace à l’atteinte de ses objectifs économiques et sociaux locaux, régionaux et nationaux tout en assurant et en protégeant la compétitivité et les échanges commerciaux du pays.

Les eaux navigables relevant de la compétence de l’Administration portuaire de Sept-Îles ainsi que les biens immobiliers fédéraux sous sa direction et ceux qu’elle occupe ou détient sont énumérés aux annexes A et B de ses lettres patentes.

L’Administration portuaire de Sept-Îles a les pouvoirs d’une personne physique; sa compétence à gérer un port se limite au pouvoir d’entreprendre des activités portuaires relatives à l’expédition, à la navigation, au transport de passagers ainsi qu’à la manutention et à l’entreposage de marchandises, dans la mesure où elles se trouvent dans les lettres patentes, et d’autres activités jugées nécessaires pour soutenir l’exploitation du port selon lesdites lettres.

### Shared Services Canada

EN — `institutions_infosource_docs/ati-schedule-i-shared-services-canada/classes_of_records_en.md:78` — Background

The Government of Canada created Shared Services Canada (SSC) on August 4, 2011, by integrating the Information Technology (IT) budgets, systems and personnel from 43 of the largest federal departments and agencies. SSC is responsible for operating and modernizing the Government of Canada’s IT infrastructure across the public sector.

Since SSC was created, the Department’s role has matured to reflect evolving business practices. In 2017, amendments to the [Shared Services Canada Act](http://laws-lois.justice.gc.ca/eng/acts/S-8.9/index.html) made it more efficient for SSC customers to purchase some of the most frequently requested IT goods and services without the need to go through the Department.

SSC reports directly to the Minister of Digital Government, emphasizing the Government of Canada’s increased focus on the role SSC has to play in the transition to a more digital government.

EN — `institutions_infosource_docs/ati-schedule-i-shared-services-canada/classes_of_records_en.md:97` — Responsibilities

SSC is responsible for digitally enabling government programs and services. This department enables the public service to effectively deliver services to Canadians by providing networks and network security, data centres and Cloud offerings, digital communications and IT tools.

SSC’s [mandate](https://www.canada.ca/en/shared-services/corporate/mandate.html) is to deliver email, data centre, and telecommunications services to federal government organizations. The Department also provides services related to cyber and IT security and the purchase of workplace technology devices, as well as offering other optional services to federal government organizations on a cost-recovery basis.

FR — `institutions_infosource_docs/ati-schedule-i-shared-services-canada/classes_of_records_fr.md:78` — Contexte

Le gouvernement du Canada a créé Services partagés Canada (SPC) le 4 août 2011 en intégrant les budgets, les systèmes et le personnel de technologie de l’information (TI) de 43 des plus grands ministères et organismes fédéraux. SPC est responsables de l’exploitation et de la modernisation de l’infrastructure de TI du gouvernement du Canada dans l’ensemble de la fonction publique.

Des [décrets](https://www.canada.ca/fr/conseil-prive/services/decrets.html) ont établi SPC en tant que ministère, ont désigné son président et ont transféré certaines parties de l’administration publique fédérale. La [*Loi sur Services partagés Canada*](http://laws-lois.justice.gc.ca/fra/lois/S-8.9/index.html), qui a reçu la sanction royale le 29 juin 2012, désigne l’autorité légale de SPC en matière de collecte de renseignements personnels pour ses programmes.

Les [articles 15 et 16 de la *Loi sur Services partagés Canada*](http://laws-lois.justice.gc.ca/fra/lois/S-8.9/page-1.html) précisent que pour l’application de la [*Loi de l’accès à l’information*](http://laws-lois.justice.gc.ca/fra/lois/A-1/index.html) et de la [*Loi sur la protection des renseignements personnels*](http://laws-lois.justice.gc.ca/fra/lois/P-21/index.html), les documents qui relèvent d’autres institutions gouvernementales – ou les renseignements personnels recueillis par elles – qui sont conservés dans l’infrastructure de TI de SPC continuent de relever des organisations partenaires de SPC. Il est entendu que :

FR — `institutions_infosource_docs/ati-schedule-i-shared-services-canada/classes_of_records_fr.md:97` — Responsabilités

SPC est chargé de faciliter la prestation des programmes et services gouvernementaux sur le plan numérique. Ce ministère permet à la fonction publique de livrer efficacement des services aux Canadiens en fournissant des réseaux et de la sécurité des réseaux, des centres de données et des services infonuagiques, des communications numériques et des outils informatiques.

SPC a le [mandat](https://www.canada.ca/fr/services-partages/organisation/mandat1.html) de fournir les services de courriel, de centres de données et de télécommunications aux organismes du gouvernement fédéral. Le Ministère offre également des services liés à la cyber sécurité et à la sécurité de la TI, à l’achat d’appareils technologiques en milieu de travail, ainsi que d’autres services facultatifs aux organismes du gouvernement fédéral selon le principe du recouvrement des coûts.

### The National Battlefields Commission

EN — `institutions_infosource_docs/ati-schedule-i-the-national-battlefields-commission/classes_of_records_en.md:169` — Background

The National Battlefields Commission (NBC) derives its [mandate](http://www.ccbn-nbc.gc.ca/en/about-us/commission/) and powers from a 1908 Act of the Parliament of Canada, the [*Act respecting The National Battlefields at Quebec*](http://www.ccbn-nbc.gc.ca/en/about-us/rights-and-responsibilities/), 7-8 Edward VII, ch. 57, and its amendments.

Administratively, the Commission is designated as a departmental corporation and is listed in Schedule II of the Financial Administration Act. The Commission reports to Parliament through the Minister of Canadian Heritage.

EN — `institutions_infosource_docs/ati-schedule-i-the-national-battlefields-commission/classes_of_records_en.md:175` — Responsibilities

The [role](http://www.ccbn-nbc.gc.ca/en/about-us/commission/) of the National Battlefields Commission is to make the great historical battlefields in Quebec City a national park numbered among the most prestigious parks in the world where the use of historic park in a urban setting is balanced and safe and where the awareness of the assets of the area, as well as its history and the history of the country, is assured. The NBC is responsible for the acquisition, administration, governance and development of the battlefields and for managing the funds allocated to them.

The National Battlefields Commission administers the Battlefields Park, including the Plains of Abraham (98 hectares in area), which commemorates the historic battle of 1759, and Des Braves Park (5 hectares in area), which marks the battle of 1760. Apart from these two parks, three major thoroughfares come within the Commission's jurisdiction, namely Des Braves Avenue, De Laune Avenue and De Bernières Avenue. The Commission also operates Pierre Dugua de Mons Terrace, east of the Citadel, and manages Martello Towers #1, #2 and #4, the Plains of Abraham Museum and the Louis S. St. Laurent Heritage House.

### Transport Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-transport/classes_of_records_en.md:142` — Background

The Department of Transport was established in 1936 by the *Department of Transport Act*, which amalgamated the functions of the Department of Railways and Canals, the Department of Marine, and the Civil Aviation Branch of the Department of National Defense. The structure and activities of Transport Canada are governed by the *Canada Transportation Act*. Transport Canada reports to Parliament through the Minister of Transport.

In addition to the National Capital Region (NCR), there are five regional offices representing the Pacific, Prairie and Northern, Ontario, Quebec and Atlantic regions, led by Regional Directors General. Regional offices are located in Vancouver, Winnipeg, Toronto, Montreal and Moncton. These offices provide transportation policy advice and coordination; regulatory surveillance, inspection, licensing and certification; regulatory compliance and enforcement; and transportation safety promotion.

In the construction of its railways, ports, airports, the Seaway and the Trans-Canada Highway, transportation has been the key to building Canada. For the first hundred years of Confederation, the federal role was to build, maintain, subsidize and regulate the infrastructure and services needed to meet the needs of a new nation. Managing change in the transportation sector has been a recurrent theme for Transport Canada in recent decades.

EN — `institutions_infosource_docs/ati-schedule-i-department-of-transport/classes_of_records_en.md:152` — Responsibilities

Transport Canada is responsible for the Government of Canada’s transportation policies and programs. Under the *Canada Transportation Act*, the Department has the added responsibility of monitoring the safety and security of the national transportation system. While Transport Canada is not directly responsible for all aspects or modes of transportation, it plays a leadership role in ensuring that all parts of the transportation system work together effectively.

The Department, headed by a Minister, Deputy Minister and an Associate Deputy Minister, is organized according to three Strategic Outcomes (SOs): 1) An Efficient Transportation System; 2) A Clean Transportation System; and 3) A Safe and Secure Transportation System, as well as Internal Services.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-transport/pibs_fr.md:141` — Contexte

Le ministère des Transports, établi en 1936 par la *Loi sur le ministère des Transports*, fusionne les responsabilités du ministère de la Marine et des Pêcheries, du ministère des Chemins de fer et des Canaux, et de la Direction de l’aviation civile du ministère de la Défense nationale. La structure et les activités de Transports Canada sont régies par la *Loi sur les transports au Canada*. Transports Canada relève du Parlement par l’entremise du ministre des Transports.

Outre la Région de la capitale nationale (RCN), cinq bureaux régionaux représentent les régions du Pacifique, des Prairies et du Nord, de l’Ontario, du Québec et de l’Atlantique, dirigés par les directeurs généraux régionaux. Les bureaux régionaux sont situés à Vancouver, Winnipeg, Toronto, Montréal et Moncton. Ces bureaux assument des fonctions de coordination et de conseils stratégiques en matière de transports; de surveillance réglementaire, d’inspection, de délivrance de permis et de certification; de conformité réglementaire et d’application de la loi; et de promotion de la sécurité des transports.

Les transports se sont avérés indispensables à l’édification du Canada grâce à la construction des routes, des ports, des aéroports, de la voie maritime et de la route transcanadienne. Au cours des cent premières années de la Confédération, le rôle du gouvernement fédéral était de construire, d’entretenir, de subventionner et de réglementer l’infrastructure et les services requis afin de répondre aux besoins d’une nouvelle nation. La gestion du changement dans le secteur des transports a été un thème récurrent pour Transports Canada lors des dernières décennies.

FR — `institutions_infosource_docs/ati-schedule-i-department-of-transport/pibs_fr.md:151` — Responsabilités

Transports Canada est responsable des politiques et programmes en matière de transport du gouvernement du Canada. Le Ministère a la responsabilité supplémentaire, en vertu de la *Loi sur les transports au Canada*, de surveiller la sécurité et la sûreté continues du réseau national des transports. Par conséquent, même si Transports Canada n’est pas directement responsable de tous les aspects ni de tous les modes de transport, il joue un rôle de leadership en veillant à ce que tous les intervenants du réseau de transport travaillent efficacement de façon intégrée.

Le Ministère, dirigé par un ministre, un sous-ministre et un sous-ministre délégué, est organisé en fonction de trois résultats stratégiques (RS) : 1) un réseau de transport efficace; 2) un réseau de transport respectueux de l’environnement; et 3) un réseau de transport sécuritaire et sûr, ainsi que des services internes.

### Transportation Safety Board of Canada

EN — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-accident-investigation-and-safety-board/classes_of_records_en.md:144` — Background

The [Transportation Safety Board of Canada (TSB)](https://www.tsb.gc.ca/eng/qui-about/index.html) is an independent agency created in 1990 by an Act of Parliament ([*Canadian Transportation Accident Investigation and Safety Board Act*](http://laws-lois.justice.gc.ca/eng/acts/C-23.4/page-1.html)). It operates at arm's length from other government departments and agencies to ensure that there are no real or perceived conflicts of interest. The TSB reports to Parliament through the Leader of the Government in the House of Commons.

EN — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-accident-investigation-and-safety-board/classes_of_records_en.md:148` — Responsibilities

Under the legislation, the [TSB's only objective](https://www.tsb.gc.ca/eng/qui-about/index.html#3) is the advancement of transportation safety in the federally-regulated elements of the air, marine, rail and pipeline transportation systems. This mandate is fulfilled by conducting independent investigations into selected transportation occurrences. The purpose is to identify the causes and contributing factors of the occurrences and the safety deficiencies evidenced by an occurrence. The TSB then makes recommendations to improve safety and reduce or eliminate risks to people, property and the environment.

The TSB may also represent Canadian interests in foreign investigations of transportation accidents involving Canadian registered, licensed or manufactured aircraft, ships or railway rolling stock. In addition, the TSB carries out some of Canada's obligations related to transportation safety at the International Civil Aviation Organization (ICAO) and the International Maritime Organization (IMO).

The Act provides for a Board consisting of up to five full-time members, including the Chairperson. The Act requires that members be collectively knowledgeable about marine, commodity pipeline, rail and air transportation. They are appointed by the Governor in Council. Members' duties include establishing policies respecting the classes of occurrences to be investigated and policies to be followed in the conduct of investigations, reviewing investigation reports, determining findings as to causes and contributing factors, identifying safety deficiencies and making safety recommendations.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-accident-investigation-and-safety-board/classes_of_records_fr.md:144` — Contexte

Le [Bureau de la sécurité des transports du Canada (BST)](https://www.tsb.gc.ca/fra/qui-about/index.html) est un organisme indépendant qui a été créé en 1990 par une loi du Parlement ([*Loi sur le Bureau canadien d'enquête sur les accidents de transport et de la sécurité des transports*](http://laws-lois.justice.gc.ca/fra/lois/C-23.4/index.html)). Le BST fonctionne de manière indépendante des autres ministères et organismes du gouvernement afin d'éviter tout conflit d'intérêt réel ou perçu. Le BST relève du Parlement par l'entremise du chef du gouvernement à la Chambre des communes.

FR — `institutions_infosource_docs/ati-schedule-i-canadian-transportation-accident-investigation-and-safety-board/classes_of_records_fr.md:148` — Responsabilités

En vertu de la loi, le [seul objectif du BST consiste](https://www.tsb.gc.ca/fra/qui-about/index.html#3) à promouvoir la sécurité dans les réseaux de transport aérien, maritime et ferroviaire et le réseau de transport par pipeline de compétence fédérale. Le Bureau s'acquitte de sa mission en procédant à des enquêtes indépendantes sur des événements particuliers survenus dans le domaine des transports. L'objet de ces enquêtes est de déceler les causes et les facteurs contributifs des événements ainsi que les lacunes de sécurité. Le BST fait ensuite des recommandations visant à renforcer la sécurité et à réduire ou éliminer les dangers auxquels sont exposés les personnes, les biens et l'environnement.

Le BST peut également représenter les intérêts canadiens dans le cadre d'enquêtes à l'étranger sur des accidents de transport mettant en cause des aéronefs, des navires ou du matériel roulant de compagnies de chemin de fer immatriculés ou construits au Canada ou pour lesquels une licence a été délivrée au Canada. De plus, le BST s'acquitte de certaines obligations du Canada dans le domaine de la sécurité des transports au sein de l'Organisation de l'aviation civile internationale (OACI) et de l'Organisation maritime internationale (OMI).

La Loi prévoit la formation d'un Bureau composé d'au plus cinq membres à plein temps, son président compris. Ces personnes doivent, collectivement, connaître les secteurs du transport maritime, ferroviaire et aérien ainsi que le secteur du transport par pipeline. Elles sont nommées par le gouverneur en conseil. Leurs responsabilités consistent entre autres à établir des politiques relatives aux types d'événements devant faire l'objet d'une enquête et des politiques à respecter dans le cadre d'une enquête, de l'examen des rapports d'enquête, de la détermination de conclusions quant aux causes et aux facteurs contributifs, de la détermination des lacunes de sécurité et de la formulation de recommandations en matière de sécurité.

### Treasury Board of Canada Secretariat

EN — `institutions_infosource_docs/ati-schedule-i-treasury-board-secretariat/classes_of_records_en.md:72` — Background

The Treasury Board is a Cabinet committee of the King’s Privy Council of Canada. It was established in 1867 and given statutory powers in 1869.

The formal role of the President is to chair the Treasury Board. The President carries out the responsibility for the management of the government by translating the policies and programs approved by Cabinet into operational reality and by providing departments with the resources and the administrative environment they need to do their work. The Treasury Board has an administrative arm, the Treasury Board of Canada Secretariat (TBS), which was part of the Department of Finance Canada until it was proclaimed a separate department in 1966.

The legislative foundation for the Treasury Board and TBS is the [*Financial Administration Act*](http://laws-lois.justice.gc.ca/eng/acts/F-11/).

EN — `institutions_infosource_docs/ati-schedule-i-treasury-board-secretariat/classes_of_records_en.md:89` — Responsibilities

As the administrative arm of the Treasury Board, TBS has a dual mandate to support the Treasury Board as a committee of ministers and to fulfill the statutory responsibilities of a central government agency. The Treasury Board is responsible for:

The formal role of the President is to chair the Treasury Board. The President carries out the responsibility for the management of the government by translating the policies and programs approved by Cabinet into operational reality. Refer to TBS’s mandate, Departmental Plan and Departmental Results Report for more information:

FR — `institutions_infosource_docs/ati-schedule-i-treasury-board-secretariat/classes_of_records_fr.md:72` — Contexte

Le Conseil du Trésor est un comité du Cabinet du Conseil privé du Roi pour le Canada. Il a été établi en 1867 et il est doté de pouvoirs législatifs depuis 1869.

Le rôle officiel du président consiste à présider le Conseil du Trésor. Le président s’acquitte de sa responsabilité de gestion du gouvernement en mettant en œuvre les politiques et les programmes approuvés par le Cabinet et en fournissant aux ministères et organismes les ressources et l’appui administratif dont ils ont besoin pour effectuer leur travail. Le Conseil du Trésor est doté d’un organe administratif, le Secrétariat du Conseil du Trésor du Canada (SCT), qui faisait autrefois partie du ministère des Finances Canada, mais qui, depuis 1966, constitue un ministère distinct.

Le fondement législatif du Conseil du Trésor et du SCT est la [*Loi sur la gestion des finances publiques*](https://laws-lois.justice.gc.ca/fra/lois/f-11/).

FR — `institutions_infosource_docs/ati-schedule-i-treasury-board-secretariat/classes_of_records_fr.md:89` — Responsabilités

À titre d’organe administratif du Conseil du Trésor, le SCT doit exercer un double mandat : appuyer le Conseil du Trésor, à titre de comité de ministres, et assumer ses responsabilités législatives d’organisme central fédéral. Le Conseil du Trésor est chargé :

Le rôle officiel du président consiste à présider le Conseil du Trésor. Il s’acquitte de sa responsabilité de gestion du gouvernement en mettant en œuvre les politiques et les programmes approuvés par le Cabinet. Se reporter au mandat du SCT, à notre plan ministériel et à notre rapport sur les résultats ministériels ci-dessous pour obtenir d’autres renseignements :

### Veterans Affairs Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-of-veterans-affairs/classes_of_records_en.md:901` — 2.1.1 Benefits, Services, and Support

Support the care and well-being of Veterans and their dependents or survivors through a range of benefits, services, research, partnerships and advocacy.

### Women and Gender Equality Canada

EN — `institutions_infosource_docs/ati-schedule-i-department-for-women-and-gender-equality/classes_of_records_en.md:69` — Background

Women and Gender Equality Canada (WAGE) history and legislative foundation can be found at this link: [Women and Gender Equality Canada mandate](/en/women-gender-equality/mandate.html).

EN — `institutions_infosource_docs/ati-schedule-i-department-for-women-and-gender-equality/classes_of_records_en.md:75` — Responsibilities

Women and Gender Equality Canada (WAGE) mandate, program responsibilities and major policies, can be found at this link: [Women and Gender Equality Canada mandate](/en/women-gender-equality/mandate.html).

FR — `institutions_infosource_docs/ati-schedule-i-department-for-women-and-gender-equality/classes_of_records_fr.md:69` — Contexte

L’histoire et le fondement législatif de Femmes et Égalité des genres Canada (FEGC) peuvent être consultés à partir de ce lien : [Mandat Femmes et Égalité des genres Canada](/fr/femmes-egalite-genres/mandat.html).

FEGC fait rapport au Parlement par l’intermédiaire de la ministre des Femmes et de l’Égalité des genres et de la Jeunesse.

FR — `institutions_infosource_docs/ati-schedule-i-department-for-women-and-gender-equality/classes_of_records_fr.md:75` — Responsabilités

Le mandat, les responsabilités de programme et les principales politiques de Femmes et Égalité des genres Canada (FEGC) peuvent être consultés à partir de ce lien : [Mandat Femmes et Égalité des genres Canada](/fr/femmes-egalite-genres/mandat.html).
