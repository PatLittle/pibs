---
title: "Business Rules Engine"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "en"
source_url: "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/protecting-your-privacy/privacy-impact-assessment/business-rules-engine-privacy-impact-assessment-summary.html"
retrieved_at_utc: "2026-11-12T05:49:03.093281+00:00"
http_status: 200
source_sha256: "6fdc17ed9aef6fc113ec1e747d4ab365af7e409bf7b71f28dde8d5ccd537ba31"
content_kind: "page"
---

# Business Rules Engine

## Privacy Impact Assessment (PIA) summary

### **Introduction**

This document provides a summary of the Privacy Impact Assessment (PIA) performed for the Business Rules Engine (BRE), which is used by the Canada Revenue Agency (CRA) to enhance automated Collections functions in the Integrated Revenue Collections (IRC) environment. The BRE enables Headquarters to develop and manage the business rules which govern the automated Collections application for Individual (T1) Income Tax inventories, and make necessary changes as the business need arises, thereby reducing their dependency on IT to write code or implement changes based on scheduled annual releases. This PIA was undertaken to identify any privacy risks concerning the BRE, and document the security measures in place to mitigate these risks.

### **Executive Summary**

The IRC initiative was established within the CRA to provide technological and specialized business support to the Taxpayer Services and Debt Management Branch (TSDMB) Business Transformation Strategy. The BRE is one component of many new integrated technological tools that were developed by the Agency to modernize automated collections processes and workload distribution, provide a holistic view of taxpayer accounts, improve risk scoring, develop more effective strategies, isolate business rules from legacy systems in order to provide Headquarters with more control over the timing and implementation of system changes, and facilitate program analysis and performance reporting.

The BRE is a software product that replaces the need for all business requirements (rules) to be imbedded in IT application codes. This provides business users with a better understanding of the rules, as they are clearly visible through the BRE, and allows TSDMB to develop and manage its own rules without having to program software application code. This enables authorized CRA users to “change rules on the fly,” a significant shift from ITB programmed changes that can only be implemented through annual system releases. Business Analysts can change the rules parameters and selection criteria to perform “What If” scenarios with the data, in order to test and implement new and improved collections strategies.

The major privacy concern with the BRE centers around the new functionality provided to Business Analysts, which could lead to privacy issues if personal information is used in a manner inconsistent with the purpose for which it was originally collected. Before the BRE was developed, Analysts followed a structured process to change the parameters and rules, as any changes required a modification of the code by ITB staff. The BRE gives business owners greater freedom to change parameters, and the flexibility to ‘play’ with the data to experiment with different scenarios and analyze results, without the involvement of IT or other working groups to provide feedback. The risk is assessed as **Moderate**.

This risk was addressed by implementing an accountability structure that monitors changes to the Business Rules and parameters, and ensures that all changes are based on historical precedent or policy. In addition, users of the BRE receive Privacy training, and are advised to be sensitive to situations where there is potential for conflict with the *Canadian Human Rights Act*.

### **Analysis of the Ten Privacy Principles**

#### **Principle 1: Accountability for Personal Information**

The CRA has designated the Manager of the Data Infrastructure Section (formerly DIRS) with responsibility for the custody and control of the personal information used by the BRE. It should be noted that the BRE itself does not save or hold any data; it merely applies business rules to accounts in the automated inventory, and sends messages to the application which routes accounts into appropriate strategies and actions. Personal information is stored in a separate location under the responsibility of the Data Infrastructure Section (within the Analytics and Data Solutions Division), while the BRE itself falls under the responsibility of the Front End Technology Division. Statements of Sensitivity/Threat and Risk Assessments have been conducted for the Data Marts holding the personal information used, created and saved via the automated collections technology. All personal information is protected and stored in compliance with CRA’s policies concerning Information Management, Security and Privacy, as well as the Treasury Board’s Privacy and Data Protection Policy, and there is no third-party involvement with other government departments or the private sector.

#### **Principle 2: Collection of Personal Information**

The BRE does not collect or store personal information. However, it does interact with personal information when applying business rules to accounts in the automated inventory. This information includes data elements such as Age, Marital Status, Date of Birth, Social Insurance Number (SIN) and client identifiers created by CRA, which are relevant to Collections and Compliance workloads. All of this data is obtained as a copy from various Source Systems within CRA, most of which is originally collected from taxpayers or their authorized representatives. Some information is obtained from third parties, including information slips, forms and information returns that are required for tax purposes, and other information collected in the course of resolving accounts with outstanding returns or unpaid tax balances. All information is collected to administer and enforce the legislation and programs under the Agency’s mandate, and the *Income Tax* *Act, Excise Tax Act*, and the *Canada Revenue Agency Act* provide legislative authority to enable the Agency to collect this personal information and use it for this purpose.

#### **Principle 3: Consent**

Neither the Front End Technology Division nor the Data Infrastructure Section obtains consent from taxpayers. Most of the information is collected from taxpayers’ Income Tax Returns, applications for benefits and credits and other forms concerning programs administered by CRA. When taxpayers provide this information to CRA, they are aware that it will be used for the administration and enforcement of programs and legislation under the Agency’s authority, and consent is therefore implied. In addition, the Individual (T1) Income Tax Return and Schedules contain a statement informing taxpayers that the information collected will be stored in Personal Information Bank (PIB) CRA PPU 005; this PIB is available for the general public to view online, and describes the purposes for which the information will be used. All additional information is obtained from other sources during the course of Collections and Compliance activities performed by the Agency. This information is collected from third parties without the consent of taxpayers in accordance with Section 5(3) of the *Privacy Act*, as direct collection (and seeking consent) would result in the collection of inaccurate information or defeat the purpose for which it is collected.

#### **Principle 4: Use of Personal Information**

The *Income* *Tax Act, Excise Tax Act*, and other Acts of Parliament provide legislative authority for CRA to use personal information, including the SIN, for the administration and enforcement of programs and legislation under the Agency’s mandate. The BRE is using personal information for the automated processing of delinquent tax accounts, and the SIN is used to match taxpayer account information with other information linked to internal Client Identifiers, in order to gain a complete picture of the account before applying business rules. As this is a function within the Accounts Receivable Program, the information is being used in a manner consistent with the purposes for which it was collected, and satisfies subsection 7(a) of the *Privacy Act*.

#### **Principle 5: Disclosure and Disposition of Personal Information**

Personal information will not be disclosed to the public, other governmental departments or other areas in the Agency. Data used and created by the BRE will be retained and disposed of in accordance with the Agency’s Information Management Policy.

#### **Principle 6: Accuracy of Personal Information**

All personal information used by the BRE is a copy of Production data, which is obtained from various CRA Source Systems. Business owners of the Source Systems capturing this data are responsible for validation and quality control, so the section responsible for the BRE does not take any additional measures to ensure accuracy.

#### **Principle 7: Safeguarding Personal Information**

Threat and Risk Assessments/Statements of Sensitivity have been carried out for the BRE, and for the data environments storing the information used and created by the BRE. CRA has established Security and Privacy Policies, which detail the guidelines and requirements to protect personal taxpayer information from loss, theft, unauthorized access, disclosure, use or modification, and to document and report security violations. Access rights are provided only to authorized business users and information technology workers with a valid CRA network account on a need-to-know basis, and all accesses are recorded by User ID. In addition, all CRA systems are periodically reviewed in accordance with the Government Security Policy.

#### **Principle 8: Openness of Information**

In accordance with CRA’s *Policy on the Conduct and Administration of Privacy Impact Assessments*, the results of this PIA are published online on the CRA website. Class of Records (CoR) CRA TSB 190 and Personal Information Bank (PIB) CRA PPU 050 have been published in *Info* *Source,* to provide the public with information concerning how personal taxpayer information is used by the BRE for Accounts Receivable Collection activities.

#### **Principle 9: Individual Access to Personal Information**

CRA’s website [www.cra.gc.ca/atip](https://www.canada.ca/en/revenue-agency/corporate/about-canada-revenue-agency-cra/access-information-privacy-canada-revenue-agency.html) provides information to assist taxpayers in making Access to Information and Privacy (ATIP) Requests, and a CoR and PIB have been published online in *Info Source*. These resources will enable members of the public to make informed ATIP requests. As the BRE does not collect or store personal information, taxpayer requests concerning ATIP will be handled by the Source Systems that originally collected the information used by the BRE.

#### **Principle 10: Challenging Compliance**

Formal complaint procedures have been developed by CRA’s ATIP Directorate. As the BRE does collect or save any personal information, ATIP complaints regarding the collection or accuracy of information used by the BRE will be addressed by the Source System business owners. Any issues concerning the manner in which personal information is used by the BRE will be addressed by the IRC Steering Committee, which is responsible for overseeing all IRC projects.
