---
title: "Authentication and Credential Management Services"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "en"
source_url: "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/protecting-your-privacy/privacy-impact-assessment/privacy-impact-assessment-summary-authentication-credential-management-services-business-transformation-directorate-assessment-benefit-services.html"
retrieved_at_utc: "2026-11-12T05:49:06.688076+00:00"
http_status: 200
source_sha256: "2dc2b2eaf960968509c0c276c1d5d6f15529ff067766f870f102608e893ea9a9"
content_kind: "page"
---

# Authentication and Credential Management Services

## Privacy Impact Assessment (PIA) summary – Business Transformation Directorate, Assessment, Benefit and, Services Branch

### Overview & PIA Initiation

#### **Government institution**

Canada Revenue Agency

#### **Government official responsible for the PIA**

Frank Vermaeten,   
Assistant Commissioner, Assessment, Benefit, and Services Branch

#### **Head of the government institution or Delegate for section 10 of the *Privacy Act***

Marie-Claude Juneau  
 ATIP Coordinator

#### **Name of program or activity of the government institution**

Information Technology

Information Technology Services involve activities undertaken to achieve efficient and effective use of information technology to support government priorities and program delivery, to increase productivity, and to enhance services to the public.

#### **Description of the class of record and personal information bank**

**Standard or institution specific class of record:**   
Information Technology ([PRN 932](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-classes-records.html#prn932))

**Standard or institution specific personal information bank:**   
Authentication and Credential Management Service ([CRA PPU 607](https://www.canada.ca/en/revenue-agency/corporate/about-canada-revenue-agency-cra/access-information-privacy-canada-revenue-agency/information-programs-information-holdings-appendix.html#PPU607))

#### **Legal authority for program or activity**

The Canada Revenue Agency is designated as a separate Agency under Schedule II of the Financial Administration Act and as such has overall responsibility over its administration, contracts and human resources management.

Personal information is collected pursuant to paragraph 31(1)(a) of the Canada Revenue Agency Act which grants the CRA responsibility for general administrative policy in the Agency. Personal information is also collected as required under the Policy on Government Security as per agreement with the President of the Treasury Board.

The legal authority for the Portageur service is under paragraph 5(1)(c) of the Canada Revenue Agency Act, which states that the CRA is responsible for implementing agreements or arrangements between the CRA and departments or agencies of the Government of Canada to administer a program or carry out an activity.

Subsection 241(5) of the Income Tax Act, sections 295 and 328 of the Excise Tax Act, sections 211 and 221 of the Excise Act, 2001, and section 8 of the Privacy Act, authorize the CRA to provide taxpayer information relating to a taxpayer with the consent of the taxpayer, to any other person.

### Summary of the project / initiative / change

The Canada Revenue Agency (CRA) has been a major stakeholder in the Government of Canada (GC) Cyber-Authentication Renewal Initiative. The CRA has played an active role and supports arrangements for federated identity. As part of the Cyber-Authentication Renewal Initiative, the CRA also provides its own authentication and credential management service for individuals, business owners and representatives to use when accessing its online services.

CRA’s Authentication and Credential Management Servicerelies ontheAuthentication Management System (AMS) and Credential Management System (CMS) to provide identity proofing, identity validation, access control or credential management services to the CRA login services.

AMS and CMS provide two separate but interrelated functions. The AMS application is responsible for ensuring that individuals are authenticated prior to associating that individual’s account with an anonymous credential provided by CMS, as well as ensuring that the current status of the individual’s account does not contain any restrictions to access that account. The CMS application is responsible for provisioning and maintaining an anonymous credential that will be associated with an individual’s CRA account.

The following is a list of the CRA login services that use AMS and/or CMS:

- **My Account**: Individuals can view their personal income tax and benefit information, and manage their tax affairs online.
- **My Business Account**: Business owners (including partners, directors, and officers) can access their GST/HST, payroll, corporation income taxes, excise taxes, excise duties and other levies accounts online.
- **Represent a Client**: Employees and representatives can access an account on behalf of their employer or clients. Prior to the CRA granting a representative access to information and services on behalf of individuals or businesses, a representative must first be authorized by the individual or the business owner.
- **Quick Access**: Quick Access gives individuals immediate access to some of their information in My Account for Individuals, provided they correctly identify themselves.

The CRA’s Authentication and Credential Management Service also includes the Portageur service, which leverages the CRA’s authentication and credential systems. Individuals consent to the electronic transfer of personal identity information to another organization. That other organization can then use this trusted information as a part of its own business process (e.g. identification/authentication process in order to validate and authenticate the identity of the individual for access to their online service). Currently, AMS and CMS provide assisted enrolment for users of online programs for Veterans Affairs Canada (VAC), Employment and Social Development Canada (ESDC) and the Province of Nova (NS).

In addition to recognizing credentials issued by the CRA CMS, users may also login with an external credential using a GC service known as SecureKey Concierge through a Credential Broker Service. This is a commercial service that enables the GC to offer access to government services using certain financial institution-issued credentials. The participating financial institutions are referred to as "Sign-In Partners."

A separate privacy impact assessment has been prepared for the [Credential Broker Service/Secure Key Concierge](http://www.ssc-spc.gc.ca/pages/pia-efrvp/pia-efrvp-secureKey-eng.html) by Shared Services Canada. It should be noted that in the case of CMS, SecureKey Concierge and other future credential providers, the individual’s data is not shared with the credential provider; these credential providers are known as anonymous providers. To ensure privacy protection, users of the Credential Broker Service will authenticate through a participating Sign-In Partner, but no personal information will be shared with the GC, including their login information and the identity of their financial institution. Similarly, no information about the government service being accessed by the individual will be shared with the individual’s financial institution.

For more information on the CRA registration and login process please visit:   
[http://www.cra-arc.gc.ca/esrvc-srvce/tx/psssrvcs/menu-eng.html](https://www.canada.ca/en/revenue-agency/services/e-services/cra-login-services.html)

### **Risk identification and categorization**

#### **A) Type of program or activity**

Administration of Programs / Activity and Services

**Level of risk to privacy:** 2

**Details:**Personal information such as the social insurance number (SIN), date of birth and information from the individual’s income tax and benefit return is used to identify the individual for the purpose of registering for the CRA’s My Account, My Business Account, Represent a Client and Quick Access online services.

As part of the registration process, an individual must create a credential (CRA user ID and password), or login with their external credential. The individual no longer needs to validate his/her identity in subsequent logins with that same credential. In order to provide additional security and recovery options, the individual will need to provide security questions and answers. These questions and answers do not reference any specific tax related information, SIN or specific identifying information. There is no credential requirement for Quick Access. Individuals must validate their identity each time they want to access the Quick Access service.

#### **B) Type of personal information involved and context**

Social Insurance Number, medical, financial or other sensitive personal information and/or the context surrounding the personal information is sensitive. Personal information of minors or incompetent individuals or involving a representative acting on behalf of the individual.

**Level of risk to privacy:** 3

**Details:** Personal information collected such as the SIN, date of birth, and information from the individual’s income tax and benefit return is sensitive information. With respect to this identity validation process, only the SIN is retained in the CRA’s directory. The individual’s SIN is associated with his/her anonymous credential.

#### **C) Program or activity partners and private sector involvement**

With other or a combination of federal/ provincial and/or municipal government(s)

**Level of risk to privacy:** 3

**Details:** The personal information collected by the Authentication Management System (AMS) and the Credential Management System (CMS) is not shared with any other institutions; however, the directory that stores the AMS and CMS data is maintained by Shared Services Canada (SSC). The CMS data is anonymous. The CRA also provides assisted enrolment for users of Veterans Affairs Canada (VAC), Employment and Social Development Canada (ESDC) and the Province of Nova Scotia.

#### **D) Duration of the program or activity**

Long-term program

**Level of risk to privacy:** 3

**Details:** There is no ‘sunset date’ for this activity as it is in keeping with the Government On-Line (GOL) initiative, a key component of the Government of Canada’s service strategy.

#### **E) Program population**

The program affects certain individuals for external administrative purposes.

**Level of risk to privacy:** 3

**Details:** The program affects individuals that choose to use the CRA’s login services (My Account, My Business Account, Represent a Client and Quick Access). It also affects individuals who choose to use CRA’s authentication and credential systems as a means of assisted enrolment for VAC, ESDC and the Government of NS.

#### **F) Technology & privacy**

Does the new or modified program or activity involve the implementation of a new electronic system, software or application program including collaborative software (or groupware) that is implemented to support the program or activity in terms of the creation, collection or handling of personal information?

**Risk to privacy:** Yes

Is the new or modified program or activity a modification of a legacy IT systems and services?

**Risk to privacy:** Yes

The new or modified program or activity involves the implementation of one or more of the following technologies:

**Enhanced identification methods** - this includes biometric technology (i.e. facial recognition, gait analysis, iris scan, fingerprint analysis, voice print, radio frequency identification (RFID), etc...) as well as easy pass technology, new identification cards including magnetic stripe cards, "smart cards" (i.e. identification cards that are embedded with either an antenna or a contact pad that is connected to a microprocessor and a memory chip or only a memory chip with non-programmable logic).

**Risk to privacy:** Yes

**Details:** The CRA uses session and persistent cookies for its login services.

**Use of Surveillance** - this includes surveillance technologies such as audio/video recording devices, thermal imaging, recognition devices , RFID, surreptitious surveillance / interception, computer aided monitoring including audit trails, satellite surveillance etc.

**Risk to privacy:** Yes

**Details:** As per the CRA’s Logging and Monitoring of Access to Taxpayer Information Policy, and the CRA’s Monitoring of Employee Electronic Access to Taxpayer Information Directive, all systems with accesses to identifiable taxpayer information (create, view, modify, delete) have an audit trail in place.

The Policy Server generates log files that contain auditing information about the events that occur within the system. These events may have been initiated by the individual, the system, a helpdesk agent, or a headquarter’s officer. These logs are analyzed by SSC for security alerts and forensics purposes.

Audit trail reports are considered Protected B information as defined by the Identifying Protected and Classified Information and Assets Policy. Consequently the communication of the request, the audit trail report, and results of its analysis must be restricted to individuals with "a need to know". The information is retained for a period of 7 years + current year (RDA 98 / 001).

**Use of automated personal information analysis, personal information matching and knowledge discovery techniques -** for the purposes of the Directive on PIA, government institutions are to identify those activities that involve the use of automated technology to analyze, create, compare, identify or extract personal information elements. Such activities would include personal information matching, record linkage, personal information mining, personal information comparison, knowledge discovery, information filtering or analysis. Such activities involve some form of artificial intelligence and/or machine learning to uncover knowledge (intelligence), trends/patterns or to predict behavior.

**Risk to privacy:** Yes

**Details:** In order to verify their identities, individuals will be asked to provide certain information from their income tax and benefit return. This information is then matched to what CRA currently has on record. For the Portageur Service, information such as the name, contact information, date of birth and gender may be sent to the other organization and compared to information on that other department’s systems for authentication purposes.

#### **G) Personal information transmission**

The personal information is used in system that has connections to at least one other system.

**Level of risk to privacy: 2**

**Details:**   
CRA together with SSC use a shared Oracle server. Strict filtering of external network connections, application filtering and architecture restrictions prevent external connection to these systems.

#### **H) Risk impact to the individual or employee**

**Details:** A breach of personal information such as the social insurance number and date of birth could have a financial impact on the individual, as it could lead to identify theft.

#### **I) Risk impact to the institution**

**Details:** A privacy breach of any kind, particularly when it involves sensitive personal information such as tax information and the social insurance number, can cause significant harm to CRA’s reputation and may lead to a loss of credibility.
