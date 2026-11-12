---
title: "Identity and Access Management - Phase 4"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "en"
source_url: "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/protecting-your-privacy/privacy-impact-assessment/identity-and-access-management-phase-4.html"
retrieved_at_utc: "2026-11-12T05:49:05.224389+00:00"
http_status: 200
source_sha256: "3aa371cb8fad60ed1f94e3728b3199a91ccd92a5e4fb3862d7b32936c2de64e9"
content_kind: "page"
---

# Identity and Access Management - Phase 4

## **Security and Internal Affairs Directorate - Finance and Administration Branch**

## **Overview & PIA Initiation**

**Government institution**   
Canada Revenue Agency

**Government official responsible for the PIA**   
Roch Huppé  
Chief Financial Officer and Assistant Commissioner, Finance and Administration Branch

**Head of the government institution or Delegate for section 10 of the Privacy Act**   
Marie-Claude Juneau  
ATIP Coordinator

**Name of program or activity of the government institution**   
Information Technology

**Description of the class of record and personal information bank**  
**Standard or institution specific class of record:**  
Information Technology  
Record Number: PRN 932  
  
**Standard or institution specific personal information bank:**  
CRA Internal Identity and Credential Management Services  
Bank Number: CRA PPU 165

## **Legal authority for program or activity**

Personal information is collected pursuant to paragraph 30(1)(a) of the Canada Revenue Agency Act, which grants responsibility to CRA for “general administrative policy in the Agency”.  The Canada Revenue Agency Act is supplemented with Treasury Board Secretariat – Policy of Government Security and - Directive on Identity Management.

**Legal Authority for Canada Revenue Agency (CRA) to collect Canada Border Services Agency (CBSA) employee information:**

For the administration of user accounts by the Canada Revenue Agency on behalf of the Canada Border Services Agency. The CRA is responsible under paragraph 5(1)(c) of the Canada Revenue Agency Act for implementing agreements or arrangements between the CRA and departments or agencies of the Government of Canada to carry out an activity or administer a program.

**Legal Authority for CRA to collect SSC employee information:**

CRA has a written collaborative arrangement with SSC that is made pursuant to section 61 of the CRA Act and is supported by the paragraph 5(1)(c) mandate provision of the CRA Act.  A written collaborative arrangement to govern this is found in the “SSC-CRA IT Governance Framework for the Provision of Information Technology Services”, and an “Operating Protocol” between SSC and the CRA.  The foregoing authorities and the MOU makes the provision by the CRA of support and management of the SSC user accounts an authorized activity or program of the CRA.  Collecting the subject personal information from SSC is part of that activity or program of the CRA.

**CBSA’s Legal Authority for the Program or Activity:**

The collection of personal information that will be used in the IAM project complies with s. 4 of the Privacy Act.  When  CBSA’s contractual work arrangements support CBSA’s ability to carry out its mandate as described in s. 5 of the Canada Borders Services Agency Act (CBSA Act), CBSA has the authority to enter into such agreements pursuant to s. 13(2)(b) of  that Act and the personal information collected is directly related to this activity.

**CBSA`s Legal Authority to collect CBSA employee information:**

CBSA has the authority to appoint staff pursuant to s. 11(a), s. 15(1) and s. 29 of the Public Service Employment Act (PSEA) and the personal information collected is directly related to this activity.  When  CBSA’s contractual work arrangements support CBSA’s ability to carry out its mandate as described in s. 5 of the Canada Borders Services Agency Act (CBSA Act), CBSA has the authority to enter into such agreements pursuant to s. 13(2)(b) of  that Act and the personal information collected is directly related to this activity.

## **Summary of the project / initiative / change**

Access Management: in execution for implementation June 30, 2017.

In 2013 a PIA was completed for Phase 2 and then updated in 2015 to include Phase 3.  The PIA is now being updated to include the Phase 4 additions/improvements.   Phase 4 Consists of Improvements to the following Identity and Access Management functions:  
   
**Identity Management (IM):** This function provides the ability to uniquely identify a person and provision them to access the information/data required to perform their duties. Improvements to the generation of basic accounts and efficient removal of accounts will be delivered through the Authoritative Identity Store (created using CA Identity Manager in Phase 2).  This includes all types of system accounts; standard, non-standard, and external partners.

**Request Management:** This function provides the ability to add, remove, or update access permissions through a centralized management tool.  The process follows established approval workflows and is subject to tracking and logging of the requests. Improvements to how managers request User IDs, system accounts and access permissions will be developed through the existing internal solution - IT Self-Service Portal (ITSSP). This includes request management for all Non-Standard accounts, ICS (Integrated Customs System) for CBSA, eBCI, and CAS for both CRA and CBSA.

**Access Review and Certification (ARC):** Access review and Certification is a risk management activity. The compliance, enforcement, and certification of accesses are a result of steady increases in regulations, internal controls, and external audit pressures. For the CRA, ARC replaces the existing employee system access review (ESAR) system (CBSA currently does not use a tool equivalent to ARC).  ARC will provide managers an efficient and comprehensive view of what permissions their employees have including non-standard accounts.  ARC will send notifications to managers reminding them to start their review and certification as well as notifying them if they are late with their review.  ARC will also provide managers with the ability to request the deletion of access permissions.

Due to the complexity of Phase 4, this phase has been split into four releases.  This version of the PIA includes details of all 4 releases as summarized below:

**July 2016: Non-Standard Account Administration (NSAA)**  
This release allows the ability to uniquely identify non-standard accounts and their owners through the IT Self-Service Portal request management processes.  Logic was included to support the routing and approvals of the various types on non-standard accounts.

**November 2016: CAS Request Management (ITSSP)**  
CAS (Corporate Administration System) Request Management centralizes all requests for CRA and CBSA for CAS accounts and access permissions through the IT Self-Service Portal.

**May 2017: eBCI Request Management (ITSSP)**  
eBCI Request Management centralizes requests for specific CRA and CBSA applications for eBCI accounts and access through the IT Self-Service Portal. There are no CBSA applications in scope for this eBCI ITSSP release.

**June 2017: Final Release**  
This is the final integrated release with the AIS delivering Identity Management, Request Management Automation using ITSSP, Access Review and Certification (ARC) tool, and a Reporting component

## **Risk identification and categorization**

**A) Type of program or activity**  
Administration of Programs / Activity and Services  
   
**Level of risk to privacy:** 2  
**Details:** Phase 4 continues to leverage the Authoritative Identity Store (AIS) delivered by IAM Phase 2, and integrates several electronic forms within an internal website used for IT request management, the IT Self-Service Portal (ITSSP) to support the request and approval workflows of various types of computer accounts.  Off-boarding of accounts is introduced, which is automated via triggers from CAS.  The personal information being used all relates to the employee/user data information which is being pulled from CAS for phase 2, and in addition information from CAS to link the appropriate approvers to their subordinates.  The system also stores detailed information of the access permissions related to all user and non-standard accounts.  This information is used by managers to review and approve the related access permissions, both on a regular basis and before approving changes to access permissions.

**B) Type of personal information involved and context**  
Personal information, with no contextual sensitivities after the time of collection, provided by the individual with consent to also use personal information held by another source.  
  
**Level of risk to privacy:** 2  
  
**Details:** The system will contain all of the above information, and will include:

- Details of supervisory relationships of managers to employees, obtained from CAS;
- History of requests for identity and access management requests and their associated approvals;
- Access permissions associated to individuals;
- The owners of non-standard accounts;

Identity management information pertaining to external partners (organizations outside of the CRA and CBSA that require access to specific CRA/CBSA applications).  
  
**C) Program or activity partners and private sector involvement**  
With other federal institutions  
  
**Level of risk to privacy:** 2  
  
**Details:** The working relationship continues with CBSA as a project partner and SSC supporting the infrastructure. For Phase 4 – we are now managing External Partner Identities however, IAM Project Phase 4 does not create system account or provision accounts to External Partners. The CRA External Partner-Coordinator (EP-C) will receive a request (form TF469) from the External Partner Organization that a new end user requires access to CRA system. EP-C will then fill out an ITSSP EP Create Form which submits the EP end users name and place of work (Partner Org) into the AIS.

Once the User ID and External Partner (EP) ID# is generated in the AIS, the personal information is retained until a request is sent to delete the EP-ID.   
Phase 4 for External Partners – does not grant access but we provide a Digital Identity in AIS

**D) Duration of the program or activity**  
Long-term program  
  
**Level of risk to privacy:** 3  
  
**Details:** The CRA is establishing a long-term Identity and Access Management Program to gain efficiencies and bring consistency in the overall management of identities and access to CRA systems. Projects are currently ongoing to make improvements to current processes and technology to enable the Program to attain its objectives to continue making improvements to identity management.

**E) Program population**  
The program affects all employees for internal administrative purposes.  
  
**Level of risk to privacy:** 2  
  
**Details:** All internal CRA, CBSA and SSC employees which use the CRA/CBSA internal network are in scope.  Identity information pertaining to external partners is also in scope, which is collected and used to create digital identities and user ID’s.  
   
For CRA - External Partner (EP) information will be generated and kept in AIS. The following EP attributes that will be generated and retained in the AIS are the following: First and last Name, Partner Org Name, and an External Partner ID number (this EP-ID will be generated in AIS, which will be a random 7 character number). Examples of external partners include Revenu Quebec, and Provincial Government partners for various programs.  The external partners have access to specific applications within the internal network.

For CBSA - information collected from airline carrier representatives are the full name and company name. Air carrier representatives are provided with a User ID to access CBSA’s Internet API Gateway (IAG), a CBSA web portal, in order to send the required Interactive Advance Passenger Information (IAPI) data to CBSA.

**F) Technology & privacy**  
Does the new or modified program or activity involve the implementation of a new electronic system, software or application program including collaborative software (or groupware) that is implemented to support the program or activity in terms of the creation, collection or handling of personal information?  
  
**Risk to privacy:** Yes

Does the new or modified program or activity require any modifications to IT legacy systems and/or services?  
  
**Risk to privacy:** Yes

The new or modified program or activity involves the implementation of one or more of the following technologies:  
**Enhanced identification methods** - this includes biometric technology (i.e. facial recognition, gait analysis, iris scan, fingerprint analysis, voice print, radio frequency identification (RFID), etc...) as well as easy pass technology, new identification cards including magnetic stripe cards, "smart cards" (i.e. identification cards that are embedded with either an antenna or a contact pad that is connected to a microprocessor and a memory chip or only a memory chip with non-programmable logic).  
  
**Risk to privacy**: No  
  
**Details:** None

**Use of Surveillance -** this includes surveillance technologies such as audio/video recording devices, thermal imaging, recognition devices , RFID, surreptitious surveillance / interception, computer aided monitoring including audit trails, satellite surveillance etc.  
  
**Risk to privacy:** Yes  
  
**Details:** The application server log and directory server log file information is the same as Phase 3, above.  Also, all records of requests and approvals for modifications to access permissions, all records of approvals of access reviews, and all records of requests to create and delete accounts (standard, non-standard and external partner identities) are stored in the system.

**Use of automated personal information analysis, personal information matching and knowledge discovery techniques -** for the purposes of the Directive on PIA, government institutions are to identify those activities that involve the use of automated technology to analyze, create, compare, identify or extract personal information elements. Such activities would include personal information matching, record linkage, personal information mining, personal information comparison, knowledge discovery, information filtering or analysis. Such activities involve some form of artificial intelligence and/or machine learning to uncover knowledge (intelligence), trends/patterns or to predict behavior.  
  
**Risk to privacy:** Yes  
  
**Details:** IAM Phase 4 generates new data for External Partners. Phase 4 generates the External Partner’s User ID and External Partner Identification Number (EP-ID#). These new attributes are associated to the EP – First and Last Name and Partner Org of the External Partner end user.

**G) Personal information transmission**  
The personal information is transferred to a portable device or is printed.  
  
**Level of risk to privacy:** 3  
  
**Details:** The same details apply as Phase 3, above.  There are 8 reports that can be generated for Phase 4 release – they are the following:

- Rogue creation, reactivation and deletion report
- NSAA request completion report
- NSAA Request Report
- ARC state of certifications
- External Partners Report
- Privileged access status report
- Identity and account status report

These reports will contain these attributes:

- First and Last Names
- User ID
- Account names
- Dates
- Status attributes – active, inactive, deleted

These reports are generated by the CRA AIS Support Group in SIAD Security. The data will be segregated so that each agency can only see their own data.

**H) Risk impact to the individual or employee**  
**Details:** In the event of a privacy or security breach, there could be significant impacts due to a compromise of confidentiality of the data processed on the IAM platform, because of the “Protected” data stored on the servers. A loss of confidentiality could result in the following impacts:

1. Embarrassment to CRA/CBSA and Government of Canada (GC) due to criticism of mishandling protected data.
2. Financial losses by CRA/CBSA due to cost of response to fix problem while in production (i.e. cost of running alternate manual/paper process).
3. Legal action by individuals and corporations against CRA/CBSA if their expectation of privacy of information is not met.
4. Serious injury to CRA/CBSA’s reputation within GC and increase in governance and oversight by GC.
5. Loss of employee’s and client’s trust in CRA/CBSA’s capability to protect their privacy.
6. Injury to CRA’s reputation as the national tax authority and associated public embarrassment.
7. Risk that CRA/CBSA will not meet their performance goals due to stoppage in service.
8. Inconvenience, embarrassment or financial stress to taxpayers in the event that taxpayer data is modified.  If data is modified the potential for internal fraud may occur.
