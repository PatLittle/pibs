---
title: "Monitoring of Electronic Access to Taxpayer Information"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "en"
source_url: "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/protecting-your-privacy/privacy-impact-assessment/monitoring-electronic-access-taxpayer-information.html"
retrieved_at_utc: "2026-11-12T05:49:05.849437+00:00"
http_status: 200
source_sha256: "0c2cefc94b46f0aeeaff52a44695349fbcab4d061c2db65c6f307c373ce01581"
content_kind: "page"
---

# Monitoring of Electronic Access to Taxpayer Information

## Privacy Impact Assessment (PIA) summary – Security and Internal Affairs Directorate, Finance and Administration Branch

### Overview & PIA Initiation

#### Government institution

Canada Revenue Agency

#### **Government official responsible for the PIA**

Roch Huppé  
Chief Financial Officer and Assistant Commissioner, Finance and Administration Branch

#### **Head of the government institution or Delegate for section 10 of the *Privacy Act***

Marie-Claude Juneau  
ATIP Coordinator

#### **Name of program or activity of the government institution**

Program Activity: Travel and other administrative services include Government of Canada travel services, as well as those other internal services that do not smoothly fit with any of the internal services categories.

#### **Description of the class of record and personal information bank**

**Standard or institution specific class of record:**   
Security ([PRN 931](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-classes-records.html#prn931))

**Standard or institution specific personal information bank:**   
A new CRA specific personal information bank will be created as the standard personal information bank Electronic Network Monitoring Personal Information Bank ([PSU 905](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-personal-information-banks.html#psu905)) does not account for the use of personal information that was initially collected for human resource purposes.

#### **Legal authority for program or activity**

Personal information is collected under the authority of Paragraph 30(1)(a)(d) and Section 51(1)(f) and (g) of the *Canada Revenue Agency Act*; Sections 220, and 241(1) of the *Income Tax Act;* Sections 275 and 295(2) of the *Excise Tax Act*; Sections 19 and 84(2) of the *Softwood Lumber Products Exports Charge Act*; and Sections 10(1) and 11 of the *Children’s Special Allowances Act* and is used to verify if transactions are in accordance with the Acts and Regulations that the Agency administers by ensuring that employees view or modify taxpayer or other sensitive information solely within their assigned workloads. The social insurance number is collected pursuant to the *Income Tax Act* and is used for identification purposes.

### **Summary of the project / initiative / change**

Any Agency system processing identifiable taxpayer and other similar information must record user accesses in a daily audit trail. These audit trail records must identify a user’s actions in a way which will allow the individual reviewing the audit trail to determine the information that was accessed. Currently, these records are sent to the Agency’s Information Technology Branch for consolidation into the National Audit Trail System (NATS). From there, audit trail records of employee electronic access to taxpayer and other similar information can be extracted using the Audit Trail Search (ATS).

Under the current National Audit Trail Monitoring Program (NATMP), a specific number of employees are randomly selected for review each week and the NATMP Section then requests audit trail records for a predetermined period for the selected employees. The NATMP Section uses the hierarchy from the Corporate Administrative System (CAS) in order to determine the immediate supervisor and second level manager of the employee selected for review. The files are then created and distributed through the Audit Trail Record Analysis Tool (ATRAT).

When an immediate supervisor receives a file for review, they must add information required for the application of the business rules in the ATRAT. Once completed, business rules are applied to the audit trail, flagging records that are at possible risk of being unauthorized. The immediate supervisor is then required to analyze the accesses, and submit a report with their findings.

Given the nature of the current audit trail monitoring program, which requires much of the process to be completed manually, the Agency launched the NATS Modernization Project which is intended to provide the Agency with the ability to continually and proactively verify transactions to determine if they are compliant with CRA’s program legislation as defined in section 2 of the *Canada Revenue Agency Act*. The objective of the project is to improve the protection, confidentiality and integrity of taxpayer and other similar information by improving the management of risk arising from end users viewing and manipulating taxpayer and other similar information using a diverse and complex IT infrastructure.

In order to realize the NATS modernization objectives and to improve its fraud control capabilities, the Agency has procured an Enterprise Fraud Management (EFM) solution that is anticipated to be operational by April 2017. The EFM is a commercial off the shelf software product by Bottomline Technologies. Once in operation the EFM solution will considerably change the manner in which CRA personnel identify and analyze questionable end-user activities. The EFM solution is completely dependent on data capture and data feeds of supplemental information to enable real-time capturing and retroactive review of end user activity. All data will be filtered, sorted and matched automatically to form compliant transaction records. The EFM data will be comprised of live captured network traffic, imported audit trail records, and supplemental data through file transfer processes.

The EFM technology will enable the proactive identification of questionable user activities using business intelligence, such as detection models and data matching, along with increased ability to perform trend and pattern analysis, provide reports, and other responses to enquiries that sustain modern risk management. The EFM solution will include a data feed from the CAS and CRA mainframe systems with information about the employee for more effective and accurate detection of questionable user activities, as well as for creating cases in the case management tool. Information such as, but not limited to, the employee’s SIN, will be used behind the scenes for data matching purposes. Other CAS information such as employee job title, level, type of employment (indeterminate, term), will be used in the case management component of the EFM solution.

The Agency will phase in the EFM solution, with the initial deployment capturing selected applications that the Agency uses to view and manipulate taxpayer and other similar information, and the remaining applications will have audit trail records from the NATS imported into the tool. Applications will continue to be phased into the EFM solution over time as well as the development of detection models.

Given that the process for the monitoring of audit trail records will significantly change through the implementation of the EFM solution, a privacy impact assessment (PIA) is necessary to ensure that any risks to the privacy and protection of employee and taxpayer and other similar information are mitigated prior to the operationalization of the EFM.

### **Risk identification and categorization**

#### **A) Type of program or activity**

Compliance / Regulatory investigations and enforcement

**Level of risk to privacy:** 3

**Details:** The Canada Revenue Agency collects employee and taxpayer and other similar information through the audit trail records. Any Agency system processing identifiable taxpayer and other similar information must record user accesses in a daily audit trail. These audit trail records must identify a user’s actions in a way which will allow the individual reviewing the audit trail to determine the information that was accessed.

The NATMP is a centralized national audit trail monitoring program for the administration, analysis, and reporting of monitoring of employee accesses to electronic taxpayer information to ensure that accesses were in accordance with their workload and duties, and to detect possible fraudulent activities.

CRA policies and directives set out the agency’s approach to managing the risk of internal fraud and misuse, and establishing effective measures for preventing and detecting internal fraud where applicable, including corrective measures, resulting in disciplinary action against an employee where an act of fraud has been committed (e.g. termination of employment). The EFM capture technology will enable the proactive identification of questionable user activities using business intelligence, such as detection models and data matching, along with increased ability to perform trend and pattern analysis, provide reports, and other responses to enquiries that sustain modern risk management.

In some cases, where fraudulent actions contravene the Criminal Code of Canada or the Financial Administration Act, other corrective measures may be taken by the Agency leading to criminal investigations and prosecution by other investigative bodies. While the potential outcomes of these cases will be referred by CRA for investigation purposes, the actual investigations themselves are considered to be out of scope of this PIA.

#### **B) Type of personal information involved and context**

Social Insurance Number, medical, financial or other sensitive personal information and/or the context surrounding the personal information is sensitive. Personal information of minors or incompetent individuals or involving a representative acting on behalf of the individual.

**Level of risk to privacy:** 3

**Details:** It is necessary to maintain an audit trail of all accesses to identifiable taxpayer and other similar information to support the requirements specified in the Acts and Regulations that the Agency administers. In this regard, both employee and taxpayer and other similar information are collected.

With the new EFM solution CAS fields will feed directly into the solution in order to detect and flag questionable activities. Employee personal information from CAS may include: user ID, first name, last name, home address, PRI, cost centre, and SIN.

Taxpayer information captured by the EFM or in audit trails may include, but is not limited to, the following personal information types: account number (SIN, BN, trust, etc.), first name, last name, full name (taxpayer or business), date of birth, street address, city, province, and postal code.

For clarity, the SIN last name of the taxpayers are included as part of the audit trail records. The other personal information types may be included as part of the EFM capture technology. For example, if a CRA employee views a screen with taxpayer credit history, then this information will be captured as part of the capture technology (screen capture). The personal information elements of the employee will be matched against the information contained in audit trail records and captures, which includes taxpayer and other similar information, to ensure that the requirements specified in the Acts and Regulations that the Agency administers are met.

The EFM solution will capture taxpayer information as an employee navigates through CRA systems. Various fields may be matched to employee information based on the detection models, and then flagged for review for potential unauthorized access, internal fraud or misuse. The captures will then be reviewed to verify if the employee’s actions were in accordance with their workload and duties.

Other information may be captured and reviewed, but is not used in the detection models. This information includes, but is not limited to: citizenship status, credit information, date of death, financial information, medical information, and physical attributes.

#### **C) Program or activity partners and private sector involvement**

Within the institution (amongst one or more programs within the same institution)

**Level of risk to privacy:** 1

**Details:** The monitoring of electronic access to taxpayer information is an internal activity administered within CRA.

#### **D) Duration of the program or activity**

Long-term program

**Level of risk to privacy:** 3

**Details:** The monitoring of electronic access to taxpayer information is an ongoing Agency activity with no expected sunset date.

#### **E) Program population**

The program affects certain employees for internal administrative purposes

**Level of risk to privacy:** 1

**Details:** The NATMP is a centralized national audit trail monitoring program for the administration, analysis, and reporting of monitoring of employee accesses to electronic taxpayer information to ensure that all accesses were in accordance with their workload and duties. The program will only impact those employees with access to electronic taxpayer information. The audit trail records, and the EFM solution captures, contain employee accesses made to CRA applications with taxpayer information. Corporate Administrative System (CAS) information is only used in conjunction with the audit trail records or captures.

#### **F) Technology & privacy**

Does the new or modified program or activity involve the implementation of a new electronic system, software or application program including collaborative software (or groupware) that is implemented to support the program or activity in terms of the creation, collection or handling of personal information?

**Risk to privacy:** Yes

Does the new or modified program or activity require any modifications to IT legacy systems and/or services?

**Risk to privacy:** No

The new or modified program or activity involves the implementation of one or more of the following technologies:

**Enhanced identification methods** -this includes biometric technology (i.e. facial recognition, gait analysis, iris scan, fingerprint analysis, voice print, radio frequency identification (RFID), etc...) as well as easy pass technology, new identification cards including magnetic stripe cards, "smart cards" (i.e. identification cards that are embedded with either an antenna or a contact pad that is connected to a microprocessor and a memory chip or only a memory chip with non-programmable logic).

**Risk to privacy:** No

**Details:** N/A

**Use of Surveillance** - this includes surveillance technologies such as audio/video recording devices, thermal imaging, recognition devices , RFID, surreptitious surveillance / interception, computer aided monitoring including audit trails, satellite surveillance etc.

**Risk to privacy:** Yes

**Details:** The Agency has procured an Enterprise Fraud Management (EFM) solution. The EFM is a commercial off the shelf software product by Bottomline Technologies. Once in operation the EFM solution will considerably change the manner in which the CRA personnel identify and analyze questionable end-user activities via transaction captures and audit trails. The EFM capture technology will enable the proactive identification of questionable user activities using business intelligence, such as detection models and data matching, along with increased ability to perform trend and pattern analysis, provide reports, and other responses to enquiries that sustain modern risk management.

The EFM solution is completely dependent on data capture and data feeds of supplemental information to enable real-time capturing and retroactive review of end user activity. All data will be filtered, sorted and matched to form compliant transaction records.

**Use of automated personal information analysis, personal information matching and knowledge discovery techniques** - for the purposes of the Directive on PIA, government institutions are to identify those activities that involve the use of automated technology to analyze, create, compare, identify or extract personal information elements. Such activities would include personal information matching, record linkage, personal information mining, personal information comparison, knowledge discovery, information filtering or analysis. Such activities involve some form of artificial intelligence and/or machine learning to uncover knowledge (intelligence), trends/patterns or to predict behavior.

**Risk to privacy:** Yes

**Details:** The EFM solution will enable real-time capturing and retroactive review of employee accesses to taxpayer and other similar information. All compiled data will be filtered, sorted and matched by the EFM solution to flag possible internal fraud or misuse.

Information contained in employees’ personnel record, including the SIN, is used to monitor employee access to taxpayer and other similar information via CRA information systems. This information is matched against the information contained in audit trail records and captures, which includes taxpayer and other similar information, to ensure that the requirements specified in the Acts and Regulations that the Agency administers is met. The EFM capture technology will enable the proactive identification of questionable user activities using business intelligence, such as detection models and data matching, along with increased ability to perform trend and pattern analysis, provide reports, and other responses to enquiries that sustain modern risk management.

#### **G) Personal information transmission**

The personal information is used in a system that has connections to at least one other system

**Level of risk to privacy:** 2

**Details:** The EFM data will be comprised of live capture of CRA network traffic from applications on the mainframe or eBCI platforms, and import of audit trail records and supplemental data through file transfer processes. This will include, but is not limited to:

- Deployment of network devices to enable real-time data capture.
- One-time migration of historical audit trail records (four years plus current year) stored in the NATS at EFM production date.
- Ongoing import of audit trail record data from applications not yet integrated to EFM.
- Initial and periodic import of supplemental data.

A data feed from CAS will be imported into the EFM on a regularly scheduled basis; however the two systems will not be directly connected.

Once in operation the EFM solution will considerably change the manner in which CRA personnel identify and analyze questionable end-user activities. The EFM capture technology will enable the proactive identification of questionable user activities using business intelligence, such as detection models and data matching, along with increased ability to perform trend and pattern analysis, provide reports, and other responses to enquiries that sustain modern risk management.

#### **H) Risk impact to the individual or employee**

**Details:** The sensitivity of information utilized through the NATMP is considered high (Protected B). Unauthorized use or disclosure of this information could result in loss of privacy, severe personal financial injury and or embarrassment to the employee and/or the taxpayer.

#### **I) Risk impact to the institution**

**Details:** In the event of privacy breach (accidental/deliberate), the Agency could suffer damage to its reputation, which in turn could potentially attract negative public interest or criticism. The Agency could also be subject to civil litigation and liability for privacy breaches that result in harm to an individual; or business (i.e. whereby the business suffers reputational or financial harm as a result of a privacy breach of taxpayer or other similar information that is connected with the business).
