---
title: "Export Control Online System (EXCOL) – Privacy Impact Assessment: Global Affairs Canada"
institution_id: "ati-schedule-i-department-of-foreign-affairs-trade-and-development"
language: "en"
source_url: "https://international.canada.ca/en/global-affairs/corporate/transparency/atip/impact-assessment/excol"
retrieved_at_utc: "2026-11-12T05:48:53.882152+00:00"
http_status: 200
source_sha256: "412ae3fdfd7e7b158332b801594e7ea9cfa6be1cf4b993b1182dfe18332d3028"
content_kind: "page"
---

# Export Control Online System (EXCOL) – Privacy Impact Assessment: Global Affairs Canada

## Executive summary

Canada is a partner to international agreements where most of Canada’s export controls exist in order to limit the movement of strategic goods. These regulations are designed to prevent the movement of certain goods that may not be in the strategic interest of Canada or its allies or that may be contrary to Canada’s bilateral or multilateral commitments.

Foreign Affairs and International Trade (DFAIT) Canada’s Export Controls Division (TIE) of the Export Import Controls Bureau (EICB) is responsible for evaluating and approving applications for permits to export controlled and strategic goods and technology. TIE is also responsible for issuing export permits for controlled goods, tracking goods exported against authorized permits and supporting other import/export processes such as delivery verification. Export permit issuance and management process is designed to ensure that Canadian exports do not contribute to the production or use of nuclear, chemical or biological weapons.

In early 2006 the Bureau introduced the Export Controls Online System (EXCOL) to replace the legacy paper- based permit system that has been in operation since 1988. EXCOL is an interactive and computerized application that allows clients to submit export applications and certificates on-line using Secure Channel. A Privacy Impact Assessment (PIA) was required because the legacy paper-based Export Controls System was substantially redesigned as an electronic service, and the delivery mechanisms have changed accordingly. The PIA has been completed.

An enrolment procedure is necessary to gain access to EXCOL. All users must be identified and authorized by the Bureau, and acquire a secure e-Pass from Secure Channel.

The enrolment information is collected initially on paper, and the procedure is finalized electronically at the first login to EXCOL. The individual must read a Privacy Notice Statement and acknowledge he/she has read and understood the notice. This information is used to establish the person’s secure on-line account for EXCOL.

The Export and Import Permits Act (R.S. 1985, c. E-1 9) and the Export Permit Regulations (SOR/97-204) mandate the collection of a minimum amount of personal information on the permit applications. This consists of an individual’s name and business contact information.

Depending on the nature and destination of the export commodities, permit applications pending approval may be disclosed to other Government departments (OGDs) for consultation. The export permit that is presented to the Canadian Border Services Agency (CBSA) at the border at the time of export includes the personal information.

The EXCOL automated system was designed, developed and implemented by a local System Integrator - CGI Group Inc. under a long term system operations, support and development contract with the Bureau’s Administration & Technology Division (TIC). EXCOL was developed to be fully contained and operated within the CGI Data Centre located on Blair Road in Ottawa.

All EXCOL Information is stored in an RDIMS database and an EXCOL account database at the CGI Data Centre, Ottawa. The information is retained for a minimum of two years and a maximum of 7 years. Access to these databases is highly controlled, both physically and electronically.

Inherent in any electronic data system, threats such as deliberate destruction and deliberate or accidental disclosure are always a possible risk. The EXCOL Threat and Risk Assessment document illustrates this topic and details the risk mitigation strategies in place.

The control of the export and import of designated goods under the Export and Import Permits Act (EIPA) is an essential instrument for the achievement of several of the Government’s domestic and foreign policy priorities, inter alia: to protect national security, to implement international non-proliferation agreements (conventional arms and weapons of mass destruction), to protect vulnerable Canadian industries (e.g. textiles), to realize benefits of International Trade Agreements, to support Canada’s supply management programs and to implement United Nations sanctions.

### Clients who enrol with EXCOL (Recognized Clients) are able to perform the following:

- apply for export permits
- apply for certificates (DVC, AC, 1(C)
- search, view and manage their applications, permits and certificates

### Clients who do not enrol with EXCOL (Unrecognized Clients) are only able to apply for export permits by one of two means:

- completing an on-line form under SSL web security, which submits directly into the EXCOL system
- printing an on-line form, completing the fields and mailing in their application

### Users of EXCOL - Internal:

- TIE staff and management
- Administration and Technology Division (TIA), Technical and administration staff
- CBSA resources that have completed the Enrolment Process. CBSA is noted as “internal” as they are the Federal Government end-users of the permit process. They will have “read-only” permissions for on-line verification of issued permits only, as deemed necessary.
- Users of EXCOL — External (Client):
- External Recognized Clients ( EXCOL User-IDs) are known to TIE and entrusted with limited access to internal functionality within EXCOL
- External Un-recognized Clients (without EXCOL User-IDs) may or may not already be known to TIE, are not enrolled in EXCOL and not entrusted with access to any internal functionality within EXCOL. These clients may electronically submit a web application form, or print the form and mail or fax it to the Export Controls Division

## A Note Regarding Databases

Two separate databases are used during the EXCOL enrolment process: (1) the Export and Import Control System (EICS) database for business registration, and (2) the EXCOL database for the secure on-line accounts.

The Export Import Controls Bureau (EICB) allocates EICB Business Numbers, a file number used only internally to identify a business. The EICB numbers are created and maintained within the EICS database. All businesses interacting with the Bureau are assigned a business number, whichever method of interaction is used (electronic or paper).

The business information collected (paper) during the application for an EICB number is:

- Name of Company in full
- Address, Postal/Zip Code
- Telephone, Fax Number
- OST Business Number
- Name of Contact person

When TIA receives a completed EICB number application form as part of an EXCOL enrolment, they assign an EICB number to the client, add the company contact information in EICS and tag the client as ‘EXCOL Registered”.

A data migration (“push”) is immediately performed which copies all new “EXCOL Registered” data to the EXCOL database, which then becomes the user data for the client. The information in the EXCOL on-line account is derived from the EXCOL Enrolment Application Forms and the EICB Number Application Form.

## Mitigation Strategies

This section summarizes specific mitigation strategies to address privacy risks identified through the PIA process.

### Privacy Risk Management Summary Tables

**Privacy risks identified through the PIA process**

| Element | Outsourcing of data storage and handling to CGI |
| Nature of Risks | Disclosure — Inappropriate access to data by personnel (including support personnel); User profiling, data matching |
| Likelihood/Threat | Low |
| Risk Level | Low – Medium |
| Comments | None |
| Mitigating Strategy | Although the 2001 Contract with CGI does not contain any reference to the *Privacy Act* or to the *Personal Information Protection and Electronic Documents Act*, the security clauses are deemed sufficient. The next contract (March 2006) rectified this lack by including specific *Privacy Act* references, as well as any required clauses to address any possible implications regarding the *USA Patriot Act*. Users and personnel have been identified and authenticated. Access is limited to the minimum required for individuals to perform their duties.  Access to the application is controlled. Accesses and updates to all information are all logged. Personnel performing these duties are all trained and screened.  User awareness training and procedures to processing sensitive information include vulnerabilities linked with user-id and password authorization.  Acceptable Use Policy to read and signed by all employees.  Access privileges are withdrawn from individuals who leave the organization, and revised when individuals move to jobs that don’t require the same level of access. |

**Privacy risks identified through the PIA process**

| Element | Plain email transmission of permit application data to OGDs for consultations. |
| Nature of Risks | “Eavesdropping” on email transmissions is a high risk |
| Likelihood/Threat | High |
| Risk Level | High |
| Comments | A “Consultation Email” generated by EXCOL is a two-step process, wherein:  1. EXCOL emails the text to the user who requested it, then 2. The user sends the email to the addressee.  Secure measures are required at each step. |
| Mitigating Strategy | 1. A VPN is established between EXCOL at CGI and the SIGNET desktops, to negate any risk of clear transmissions. 2. EXCOL includes read-only access to the consulted parties, so that they can view the required information and provide feedback within the system, eliminating the need for email containing personal data.  Where this is not technically feasible, PKI Certificates is being used to encrypt attachments to email. |

**Privacy risks identified through the PIA process**

| Element | Data Collecting — personal information for Consignees is provided by the Exporter |
| Nature of Risks | This is contrary to principles of fair information practices. This could lead to Departmental liability should personal information be disclosed in an unauthorized manner. |
| Likelihood/Threat | Low |
| Risk Level | Low |
| Comments | None |
| Mitigating Strategy | Consignees must be made aware that their information is being collected and retained in a Canadian Government database. The collection of this information is dependent on the Exporter, as the Bureau has no dealings with the Consignee. A new “End-Use Statement” including a Privacy Notice, for the consignee’s signature now exists. |

**Privacy risks identified through the PIA process**

| Element | Lack of Memoranda of Understanding (MOU) with Consultees - Other Government Departments (OGDs) |
| Nature of Risks | Lack of a formal agreement means no assurances to avoid inappropriate use of ITCAN data by OGDs. |
| Likelihood/Threat | Low |
| Risk Level | Low |
| Comments | These consultations have been occurring for many years without formal MOUs. The consultations are considered to be consistent use of the original purpose of the collection of information |
| Mitigating Strategy | Memorandums of Understanding will be arranged with the consulted parties.. |

**Privacy risks identified through the PIA process**

| Element | Disclosure or Destruction of Data -Virus |
| Nature of Risks | Loss or exposure of personal information |
| Likelihood/Threat | Medium |
| Risk Level | Medium |
| Comments | Note that frequent backups of the data are available for restoration |
| Mitigating Strategy | Virus protection software, regularly updated, is an integral part of the EXCOL Solution Architecture. Discussions are underway to implement an Intrusion Detection System. |

**Privacy risks identified through the PIA process**

| Element | Disclosure or Destruction of Data - Hacker |
| Nature of Risks | Loss or exposure of personal information |
| Likelihood/Threat | Low |
| Risk Level | Medium |
| Comments | Note that frequent backups of the data are available for restoration |
| Mitigating Strategy | Use of SSL v2 28 bit encryption key used to encrypt all information is end to end on the network. Discussions are underway to implement an Intrusion Detection System. |

**Privacy risks identified through the PIA process**

| Element | Disclosure or Destruction of Data - Technical Means |
| Nature of Risks | Loss or exposure of personal information |
| Likelihood/Threat | Low |
| Risk Level | Medium |
| Comments | Note that frequent backups of the data are available for restoration |
| Mitigating Strategy | EXCOL is physically located in the CGI Building that houses the Data Centre. This facility is considered secure, is under camera surveillance 24/7 into the system/network operations centre. Redundant UPS Units are installed to minimize disruption. UPS Units clean and stabilize power supply for the complete Data Centre. Very restricted access to process centre. All personnel security cleared. The EXCOL Technical Architecture includes a direct communication link between the SC environment and the EXCOL Web server. This is the only component where electronic eavesdropping equipment could be installed that would negatively impact the EXCOL application. This link is completely housed within the CGI Data Centre and monitored by an intrusion detection system. |

**Privacy risks identified through the PIA process**

| Element | Questionnaire A - 7.09 “Are there contingency plans and documented procedures in place to identify and respond to security breaches or disclosures of personal information in error?” |
| Nature of Risks | Inefficient response and delays if these problems arise, |
| Likelihood/Threat | Low |
| Risk Level | Low |
| Comments | Normal departmental procedures would be followed, if such an occasion were to arise, |
| Mitigating Strategy | TIE must maintain operational records that show how incidents were handled, documenting the chain of events during the incident, noting the time when the incident was detected; the actions taken; the rationale for decisions; details of communications; management approvals or direction; and external and internal reports. A post-incident analysis is required summarizing the impact of the incident, identifying security deficiencies and prevention measures.  **NOTE THAT** the nature of any breach or disclosure would determine which Division within the Bureau (TIE or TIA) bears responsibility |

**Privacy risks identified through the PIA process**

| Element | Questionnaire A - 7.10 “Are there documented procedures in place to communicate security violations to the data subject, law enforcement authorities and relevant program managers?” Inefficient response and delays if these |
| Nature of Risks | Inefficient response and delays if these problems arise |
| Likelihood/Threat | Low |
| Risk Level | Low |
| Comments | Normal departmental procedures would be followed, if such an occasion were to arise. |
| Mitigating Strategy | TIE must establish a procedure for notifying the appropriate operational personnel, managers and all affected parties, keeping contact lists up to date. EXCOL must notify the appropriate law enforcement agency if the incident appears to be criminal. Note thatthe nature of any breach or disclosure would determine which Division within the Bureau (TIE or TIA) bears responsibility |

**Privacy risks identified through the PIA process**

| Element | Questionnaire A - 7.11 “Is there a plan for quality assurance and audit programs to assess the ongoing state of the safeguards applicable to the system?” |
| Nature of Risks | Inadvertent misuse of or exposure of data to additional or increasing risk elements. |
| Likelihood/Threat | Low |
| Risk Level | Low |
| Comments | None |
| Mitigating Strategy | TIE must establish a plan for quality assurance and audit programs to assess the ongoing state of the safeguards applicable to EXCOL. **Note that** the nature of any breach or disclosure would determine which Division within the Bureau (TIE or TIA) bears responsibility |
