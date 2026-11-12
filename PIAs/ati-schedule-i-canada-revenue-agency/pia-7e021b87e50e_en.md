---
title: "Data Mining"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "en"
source_url: "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/protecting-your-privacy/privacy-impact-assessment/data-mining-privacy-impact-assessment-summary.html"
retrieved_at_utc: "2026-11-12T05:49:04.294293+00:00"
http_status: 200
source_sha256: "b4b1ac8bd90f44cc73b7274539a98b5fd7411b10cebdb81774a46388242b8bd7"
content_kind: "page"
---

# Data Mining

## Privacy Impact Assessment (PIA) summary

### **Introduction**

This document provides a summary of the Privacy Impact Assessment (PIA) concerning Data Mining activities, which are used to enhance the Canada Revenue Agency’s (CRA) Collections and Compliance Programs. This PIA was undertaken to analyze the privacy risks pertaining to confidential taxpayer information used for predictive Data Mining, and document the security measures in place to mitigate these risks.

### **Executive Summary**

The Integrated Revenue Collections (IRC) initiative was established to provide technological and specialized business tools to support business transformation within CRA. This was driven by several factors, including: CRA's 2010 Strategy; CRA’s Business Development Strategy; continued growth in accounts receivable and aging of inventories; Government of Canada policy objectives to renew existing service delivery mechanisms to better serve Canadians; and the 1994 and 2006 reports by the Office of the Auditor General (OAG). In particular, the following OAG recommendations influenced the Agency to develop the Data Mining initiative discussed in this PIA:

- The Canada Revenue Agency should identify and collect the data it needs to analyze the makeup of its tax debt and to develop better collection strategies.
- The Canada Revenue Agency should establish a more comprehensive automated risk-scoring system for tax debts, update the risk scores on an ongoing basis, and use the risk scores to prioritize workload throughout the collections process.

The Data Mining initiative enables CRA to utilize predictive analytics to address the OAG’s recommendations and improve performance for CRA’s Collections and Compliance Programs. During the Data Mining process, a Data Mining tool (software) is applied to large volumes of historical taxpayer data, which was collected by CRA while administering and enforcing programs and legislation under its mandate. The data elements used will vary for each Data Mining model, based on its purpose and scope, and is obtained from internal CRA sources with no third-party data used. These models identify patterns that may enable the Agency to predict future behaviours for a *class of taxpayer* (not individual taxpayers), and attempt to predict which taxpayers, based on certain criteria, are most likely to respond to various treatment strategies. Based on these predictions, a grouping of accounts may then be mapped into appropriate treatment strategies or interventions that will enable CRA to resolve them efficiently.

The Data Mining initiative includes the development of the following ten Data Mining models:

- DM01 – Non-Filer Discovery Model (Not in SUDS);
- DM02 – Arbitrary Assessment Response Model;
- DM04 – Non Filer Potential Model (Entire NF Population);
- DM03 – REMITS Model Replacement;
- DM05 – Accounts Receivable Model – 100%;
- DM06 - Likeliness of Loss to the Crown;
- DM07 - Likeliness to Pay in Full in X Days;
- DM08 - Tax Potential;
- DM09 - Likeliness of Loss Using Non- Filer Elements; and
- Text Mining, Proof-of-Concept using ACSES diary entries.

A Generic Data Mining Mart was created in the Exploratory Tier to facilitate data understanding and the development of these Data Mining models, while data marts in the Research, Reporting, and Analysis (RR&A) Tier are used for testing and validation of the models. There is a risk that some elements such as Age, Gender, and Marital Status may conflict with the *Canadian Human Rights Act* depending on the weight that these elements are accorded by the Data Mining tool. However, the Data Mining Section tests the data mining models with and without sensitive data elements to determine their significance, and will only use sensitive data elements if they are required to generate accurate scores. If testing indicates that a particular data model will not provide beneficial scores, then it will not be used.

In addition to this PIA, Statements of Sensitivity/Threat and Risk Assessments (SoS/TRA) have also been conducted to ensure that appropriate safeguards are in place to protect the confidentiality, integrity and availability of taxpayer information. In accordance with the *Privacy Act*, legislative authority is in place within the *Income Tax Act* and *Excise Tax Act* enabling CRA to use the information in this manner, and this use of personal information has been documented in CRA’s chapter of *Info Source*, to inform the general public of this use of taxpayer data. In addition, data matching activities will follow the Treasury Board Secretariat’s (TBS) Data Matching Policy, and scores generated by Data Mining models that result in an administrative decision involving a taxpayer will be retained in accordance with the Agency’s Information Management policies.

The PIA and SoS/TRA have indicated that privacy risks from data mining activities range from low to high. In response, a risk mitigation plan has been developed, so all risks identified can be reduced to an acceptable level.

### **Analysis of the Ten Privacy Principles**

#### **Principle 1: Accountability for Personal Information**

The CRA has designated the Manager of the Data Infrastructure Section (formerly DIRS) with responsibility for the custody and control of the personal information stored and used for Data Mining. This information will be protected and stored in compliance with CRA’s policies concerning Information Management, security and privacy, as well as the Treasury Board’s Privacy and Data Protection policy, and there is no third-party involvement with other government departments or the private sector.

#### **Principle 2: Collection of Personal Information**

The Data Mining models use a variety of different data elements, including personal taxpayer information elements such as Age, Marital Status, Date of Birth, Social Insurance Number (SIN) and client identifiers created by CRA. All of this data is obtained as a copy from various source systems within CRA, and most was originally collected from taxpayers or their authorized representatives. Some information was obtained from third parties, including information slips such as T4s and T5s, as well as other forms or information returns that these third parties are required by law to submit to CRA for tax purposes. All of this information is collected to administer and enforce the legislation and programs under the Agency’s mandate, and the *Income Tax* *Act, Excise Tax Act*, and the *Canada Revenue Agency Act* provide legislative authority to enable the Agency to collect this personal information and use it for this purpose.

#### **Principle 3: Consent**

The Data Mining Section and the Data Infrastructure Section (which manages the data marts used for Data Mining activities) do not obtain consent from taxpayers. The information is collected from taxpayers’ Income Tax Returns, applications for benefits and credits and other forms concerning programs administered by CRA, and housed in source systems which feed data to the ADSD data marts. When taxpayers provide this information to CRA, they are aware that it will be used for the administration and enforcement of programs and legislation under the Agency’s authority, and consent is therefore implied. In addition, the Individual (T1) Income Tax Return and Schedules contain a statement informing taxpayers that the information collected will be stored in Personal Information Bank (PIB) CRA PPU 005.This PIB is available for the general public to view online, and describes the purposes for which the information will be used.

#### **Principle 4: Use of Personal Information**

Legislative authority is in place within the *Income* *Tax Act, Excise Tax Act*, and other Acts of Parliament permitting the Agency to use this personal information for the purpose of Data Mining, as it is a supporting function of CRA’s Collections and Compliance Programs. Therefore the Data Mining models are used for the administration and enforcement of programs and legislation under CRA’s mandate, in a manner consistent with the purposes for which it was collected, and satisfies subsection 7(a) of the *Privacy Act*. This personal information has historically been used by CRA for Collections and Compliance activities. The use of Data Mining models simply allows the Agency to leverage modern technology to enhance the efficiency of these Programs, and more effectively use the data that was collected for this purpose. Data matching does occur during the Data Mining process, and is performed in compliance with the Treasury Board Secretariat’s *Policy on Data Matching*. The Data Mining section will make every effort to ensure that data elements such as Gender, Age, and other sensitive information will be used only when necessary, in order to minimize risks of violating the *Canadian Human Rights Act*.

#### **Principle 5: Disclosure and Disposition of Personal Information**

Personal information will not be disclosed to the public or other governmental departments, and the data elements will not be shared with other areas in the Agency. The only sharing of information occurs when scores generated by the Data Mining models are fed into the Agency’s automated Source Systems, to be considered in conjunction with other information during automated processes. Scores are retained in accordance with the Agency’s Information Management Policy, and data in the Exploratory Environment is destroyed when no longer needed.

#### **Principle 6: Accuracy of Personal Information**

Data contained in the RR&A Tier is a copy of Production data that may or may not be up-to-date, depending on the frequency of data refreshes, and quality control is performed by business owners of the Source Systems that originally captured the information. Data in the Exploratory Tier is not updated and it is not used for Production, therefore it is not necessary to validate the accuracy of this information.

#### **Principle 7: Safeguarding Personal Information**

Threat and Risk Assessments/Statements of Sensitivity have been carried out for the data environments, but not the individual Data Mining models. CRA has established Security and Privacy Policies, which detail the guidelines and requirements to protect personal taxpayer information from loss, theft, unauthorized access, disclosure, use or modification, and to document and report security violations. Procedures are in place concerning the use, security and disclosure of personal information with regard to work stations, removable media, and local drives. Access rights are provided only to authorized business users and information technology workers with a valid CRA network account on a need-to-know basis, and all accesses are recorded by User ID. In addition, all CRA systems are periodically reviewed in accordance with the Government Security Policy.

#### **Principle 8: Openness of Information**

In accordance with CRA’s *Policy on the Conduct and Administration of Privacy Impact Assessments*, the results of this PIA are published online on the CRA website. Class of Records (CoR) CRA TSB 550 has been created and published online in *Info* *Source,* and a Personal Information Bank (PIB) has been drafted (likely to be published in *Info Source* in 2013), which describe the types of personal information contained in the ADSD data marts used for Data Mining, as well as the purpose of collection and consistent uses of this information. This provides the general public with sufficient information to clearly understand how personal taxpayer information is used for the Data Mining initiative.

#### **Principle 9: Individual Access to Personal Information**

CRA’s website [www.cra.gc.ca/atip](https://www.canada.ca/en/revenue-agency/corporate/about-canada-revenue-agency-cra/access-information-privacy-canada-revenue-agency.html) provides information to assist taxpayers in making Access to Information and Privacy (ATIP) Requests, a CoR has been published online in *Info Source*, and a PIB to document this information usage will be published as well. These resources will enable members of the public to make informed ATIP requests. Taxpayer requests concerning ATIP will be mostly handled by the Source Systems that originally collected the information used for the Data Mining Models, and those that received the data mining scores that are used and saved in their respective systems. The Data Mining section will retain any personal information used in administrative decisions for a minimum of two years.

#### **Principle 10: Challenging Compliance**

Formal complaint procedures developed by CRA’s ATIP Directorate will be addressed by the Source System business owners. As the information used for the Data Mining models is a copy of Production data, any issues regarding the accuracy of information must be handled at the Source System level, where the information is collected or created. If source systems make any changes to their data based on such complaints, it is that area’s responsibility to inform the Data Mining Section, so that corrections and/or changes can be made to the models as needed.
