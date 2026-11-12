---
title: "Data Infrastructure"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "en"
source_url: "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/protecting-your-privacy/privacy-impact-assessment/data-infrastructure-privacy-impact-assessment-summary-analytics-data-solutions-division.html"
retrieved_at_utc: "2026-11-12T05:49:04.277850+00:00"
http_status: 200
source_sha256: "73451b1b8a8cda11943471fcf2cb721071a56e110e98b782e30f870791d5307e"
content_kind: "page"
---

# Data Infrastructure

## Privacy Impact Assessment (PIA) summary - Analytics and Data Solutions Division

### **Introduction**

This document summarizes the Data Infrastructure Privacy Impact Assessment (PIA) prepared by the Analytics and Data Solutions Division (ADSD) of the Canada Revenue Agency (CRA). The ADSD is responsible for developing and maintaining data marts and data environments that are used for research, analysis, performance measurement, reporting and decision support purposes concerning Collections and Compliance workloads within CRA. This PIA was undertaken to analyze the privacy risks pertaining to confidential taxpayer information stored and used within these data holdings, and document the security measures in place to mitigate these risks.

### **Executive Summary**

The objectives of this Privacy Impact Assessment (PIA) are to analyze the data environments and data marts within ADSD’s Exploratory and Research, Reporting, and Analysis (RR&A) Data Infrastructure Tiers, to identify any privacy issues and risks, and to provide a privacy risk management plan to eliminate or reduce those risks to an acceptable level.

The Integrated Revenue Collections (IRC) initiative was established to provide technological and specialized business tools to support business transformation within CRA. This was driven by several factors, including: CRA's 2010 Strategy; CRA’s Business Development Strategy; continued growth in accounts receivable and aging of inventories; Government of Canada policy objectives to renew existing service delivery mechanisms to better serve Canadians; and the 1994 and 2006 reports by the Office of the Auditor General (OAG). In particular, the following OAG recommendations have led to the development of the dedicated data mart tiers discussed in this PIA:

- The Canada Revenue Agency should identify and collect the data it needs to analyze the makeup of its tax debt and to develop better collection strategies.
- The Canada Revenue Agency should significantly improve its management of information to make it complete and comprehensive. It should develop reliable techniques and information sources to determine on a regular basis the results of its collection efforts and use that information to guide its decision making for each of its major collection modes and actions.
- The Canada Revenue Agency should establish a more comprehensive automated risk-scoring system for tax debts, update the risk scores on an ongoing basis, and use the risk scores to prioritize workload throughout the collections process.

To meet the goals and recommendations outlined above, the RR&A and Exploratory marts were developed and populated with selected taxpayer data. This data is derived from various CRA source systems, and was collected by the Agency during the course of administering and enforcing the programs and legislation under CRA’s mandate. The information pertains to various revenue lines, including (but not limited to) Individual Income Tax (T1), Corporate Tax (T2), GST/HST and Other Levies, and is used for different purposes depending on the Tier.

#### **The Exploratory Tier**

The data marts in the Exploratory Tier are not used in Production, and will not be used in making any administrative decisions regarding taxpayers. These marts are used for data understanding, formulating data requirements, supporting data analysis activities, developing an understanding of metadata, determining the potential value of source system data, and developing data mining models. The Exploratory Tier supports the assessment of data accuracy, business model development, allows for prototype/proof-of-concept development, and the testing of new toolsets by business users.

#### **The Research, Reporting, and Analysis (RR&A) Tier**

The data marts within the RR&A Tier are used in Production, and may be used in an administrative decision making process. The purpose of this tier is to enable Headquarters staff and management to analyze data to discover new facts and relationships in support of business operations. This includes debt management research to understand inventory growth and the breakdown of outstanding debts, ad-hoc queries, trend identification and analysis, studying the effectiveness of existing collection strategies and actions, program evaluation and analysis of program performance, development of predictive data mining models, and business rules development.

### **Analysis of the Ten Privacy Principles**

#### **Principle 1: Accountability for Personal Information**

The CRA has designated the Data Infrastructure Section (formerly DIRS) with responsibility for the custody and control of the personal information stored and used in the ADSD data marts. These marts have been developed in compliance with CRA’s policies concerning Information Management, Security and Privacy, and there is no third-party involvement with other government departments or the private sector.

#### **Principle 2: Collection of Personal Information**

These data marts contain a significant amount of personal taxpayer information. However, no new information is collected. All data is obtained as a copy from various source systems within CRA, which has been collected in the course of administering and enforcing the legislation and programs under the Agency’s mandate. The *Income Tax* *Act, Excise Tax Act*, and the *Canada Revenue Agency Act* provide legislative authority to enable the Agency to collect this personal information and use it for this purpose.

#### **Principle 3: Consent**

ADSD does not obtain consent from taxpayers. The information is collected from taxpayers’ Income Tax Returns, applications for benefits and credits, and various other forms concerning programs administered by CRA, and housed in source systems which feed data to the ADSD data marts. When taxpayers provide this information to CRA, they are aware that this information will be used for the administration and enforcement of the Agency’s Programs and legislation, and consent is therefore implied. In addition, the Individual (T1) Income Tax Return and Schedules contain a statement that informs taxpayers that the information collected will be stored in Personal Information Bank (PIB) CRA PPU 005; this PIB is available for the general public to view online, and describes the purposes for which the information will be used.

#### **Principle 4: Use of Personal Information**

Legislative authority is in place within the *Income* *Tax Act, Excise Tax Act, Employment Insurance Act*, and other Acts of Parliament to permit the Agency to use this personal information for this purpose. All information within these data marts is used for the administration and enforcement of programs and legislation under CRA’s mandate, in a manner consistent with the purposes for which it was collected.

#### **Principle 5: Disclosure and Disposition of Personal Information**

Personal information will not be disclosed to the public or other governmental departments; it will only be disclosed within the Agency, for the purposes outlined in the Executive Summary above. Data in the RR&A Tier is retained in accordance with the Agency’s Information Management Policy. Data in the Exploratory Tier is volatile and has a limited life span, is not used in making administrative decisions concerning taxpayers, and therefore is not retained for the minimum two year period. Periodic audits are conducted to identify data marts that are no longer being used, and business owners are consulted to determine if/when a data mart is no longer required.

#### **Principle 6: Accuracy of Personal Information**

Data contained in the RR&A Tier is a copy of Production data; quality control is performed by business owners of the Source Systems that originally captured the information. Data in the Exploratory Tier is not updated and is designed to be temporary. When any data elements from the Exploratory Tier are used for validating predictive data mining models, their accuracy is first verified by comparing them to the information held in the Source System.

#### **Principle 7: Safeguarding Personal Information**

The CRA computing environment provides acceptable security of information for the Data Infrastructure environments. Threat and Risk Assessments/Statements of Sensitivity have been carried out, and procedures are in place concerning the use, security and disclosure of personal information with regard to work stations, removable media, and local drives. Access rights are provided only to authorized business users and Information Technology workers on a need-to-know basis, and all accesses are recorded by User ID. CRA Security and Privacy Policies will be followed, which detail the guidelines and requirements to protect personal taxpayer information from loss, theft, unauthorized access, disclosure, use or modification.

#### **Principle 8: Openness of Information**

Class of Records (CoR) CRA TSB 550 has been created and published online in *Info* *Source,* and a Personal Information Bank (PIB) has been drafted (likely to be published in *Info Source* in 2013), which describe the types of personal information contained in ADSD’s data marts, as well as the purpose of collection and consistent uses for this information. This provides the general public with sufficient information to clearly understand the functions of this work area and the use of personal information.

#### **Principle 9: Individual Access to Personal Information**

CRA’s website [www.cra.gc.ca/atip](https://www.canada.ca/en/revenue-agency/corporate/about-canada-revenue-agency-cra/access-information-privacy-canada-revenue-agency.html) provides information to assist taxpayers in making Access to Information Requests, and a CoR and PIB will be available online in *Info Source*. These resources will enable members of the public to make informed requests for information concerning these data marts.

#### **Principle 10: Challenging Compliance**

Formal complaint procedures developed by the Access to Information and Privacy Directorate will be addressed by the Source System business owners. As the information contained in ADSD’s data marts is a copy of Production data, any issues regarding the accuracy of information must be handled at the Source System level, where the information is collected or created.
