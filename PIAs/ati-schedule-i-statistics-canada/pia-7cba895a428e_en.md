---
title: "Cloud Infrastructure Platform - Privacy impact assessment summary"
institution_id: "ati-schedule-i-statistics-canada"
language: "en"
source_url: "https://www.statcan.gc.ca/en/about/pia/cloud"
retrieved_at_utc: "2026-11-12T01:42:42.200738+00:00"
http_status: 200
source_sha256: "61c34656cbf941a8e9369389491975ea0111e35f014dd2923087eecdb399c516"
content_kind: "page"
---

# Cloud Infrastructure Platform - Privacy impact assessment summary

## Introduction

This Privacy Impact Assessment will address the privacy risks and risk mitigation measures associated with the cloud infrastructure platform. Any applications or systems that process personal identifiable information will undergo an extensive analysis to evaluate privacy, confidentiality or security risks to determine if separate privacy impact assessments will be required. The Cloud Services Enablement Project applies all relevant central Agency and Statistics Canada policies related to privacy in the context of the cloud platform. As a result, this privacy impact assessment will focus on the following two components that are important to the safeguarding of personal identifiable information: identity and access management as well as auditing and reporting.

## Objective

A privacy impact assessment for the Cloud Infrastructure Platform was conducted to determine if there were any privacy, confidentiality or security issues with this initiative and, if so, to make recommendations for their resolution or mitigation. It also serves to demonstrate how the Cloud Infrastructure Platform meets the principles of necessity and proportionality.

## Description

Statistics Canada has created a cloud infrastructure platform that resides within a Government of Canada-authorized Microsoft Azure cloud data centre. This cloud infrastructure platform has been authorized to safeguard information categorized up to, and including, Protected-B. Protected-B indicates information that is sensitive. Sensitive information includes personal information (for example, Human Resources records), industry information (for example, trade secrets held in trust), or sensitive government information (for example, Treasury Board Submissions). Documents classified as Secret or Top Secret will not be authorized to reside in the cloud. The cloud infrastructure platform lays the foundation upon which future cloud-based applications and systems, that contain personal identifiable information, can be securely built and accessed by authorized users. This assessment will address the privacy risks associated with this cloud infrastructure platform. Specifically, it will focus on two of the infrastructure's underlying components that are crucial to privacy protection: identity and access management as well as auditing and reporting. Protocols are in place to detect, report on, analyze, and respond to incidents such as a privacy breach. In the event of a privacy breach, corrective actions will be taken and all impacted users will be notified about the measures being taken to minimize the impact on them.

Traditionally, Statistics Canada has stored and accessed information and applications located at government-owned or leased data centres. Authorized personnel would then access information and applications over private network connections provided by telecommunications companies. Because of the privacy and security risks related to the storing and processing of personal identifiable information, these data centres have been assessed and authorized to store and process information categorized up to and including Protected-B. Delivering information technology services in this manner involves utilizing a multitude of out-dated processes developed to manage the legacy data centre environments and infrastructure within them.

Safeguarding personal identifiable information is a priority that must be protected throughout its lifecycle. Security plays an important role in enhancing privacy and although they are closely related, privacy and security are independent and separate disciplines. The government of Canada has addressed these cloud computing-related risks by publishing mandatory safeguards that must be implemented when accessing, storing, and processing personal identifiable information from authorized cloud service providers. The government of Canada organizations responsible for publishing these mandatory safeguards are the Canadian Centre for Cyber Security; the Treasury Board of Canada Secretariat; and, Shared Services Canada. With their assistance, Statistics Canada has taken a coordinated approach to identifying and managing its cloud-related privacy and security risks. Statistics Canada has created a cloud environment with the mandatory privacy and security controls for information classified up to Protected-B, based on guidance from a federal publication entitled [IT Security Risk Management: A Lifecycle Approach](https://www.statcan.gc.ca/en/about/pia/IT%20Security%20Risk%20Management:%20A%20Lifecycle%20Approach). This publication is a catalog of privacy and security controls that are used to protect the Government of Canada and its information assets from threats and risks. The cloud infrastructure platform lays the foundation upon which future cloud-based IT applications used by Statistics Canada can be developed and accessed by authorized users. It will provide future cloud projects with significant cost savings, while safely increasing service availability, reliability, security, and speed.

Before internal or external stakeholders (ex. University researchers, Provincial statistical office researchers, etc) can access these cloud-based applications and services, they must login to a centralized identification and access management system. This component of the cloud infrastructure platform logs a user identity, their activity, and other relevant information. Logged information is subject to auditing and reporting. As a result, this privacy impact assessment will focus on the following two components that are important to the safeguarding of personal identifiable information: identity and access management as well as auditing and reporting.

## Identity and Access Management

The purpose of identity and access management is to ensure that only authorized individuals with a mission-critical work requirement can access the appropriate information and data. This practice ensures that access to personal identifiable information is restricted only to those employees who need to know this information to fulfill their professional duties and responsibilities. To that end, strict authentication and authorization security controls have been put in place to mitigate the risk of any unauthorized disclosure of personal identifiable information. Identity and access management tools are centrally managed and all relevant information, including the user's first name and last name, are recorded in a log for future auditing and reporting activities.

## Auditing and Reporting

Statistics Canada's cloud infrastructure platform has implemented significant logging, auditing, and reporting capabilities. Together, these capabilities allow Statistics Canada to retain public trust in its data stewardship by always keeping track of what applications and services were accessed by whom and for what purpose. Logs can be held for up to two years or more depending on the requirements.

## Risk Area Identification and Categorization

The PIA identifies the level of potential risk (level 1 is the lowest level of potential risk and level 4 is the highest) associated with the following risk areas:

The PIA identifies the level of potential risk (level 1 is the lowest level of potential risk and level 4 is the highest) associated with the following risk areas:

|  | Risk Scale |
| --- | --- |
| Type of program or activity  Program or activity that does NOT involve a decision about an identifiable individual | 1 |
| Type of personal information involved and context  Only personal information, with no contextual sensitivities, collected directly from the individual or provided with the consent of the individual for disclosure under an authorized program. | 1 |
| Program or activity partners and private sector involvement  Private sector organizations, international organizations or foreign governments | 4 |
| Duration of the program or activity  Long-term program or activity | 3 |
| Individuals affected by the program  The program's use of personal information for external administrative purposes affects certain individuals. | 3 |
| Personal information transmission  The personal information is transmitted using wireless technologies. | 4 |
| Technology and privacy  Does the new or substantially modified program or activity involve implementation of a new electronic system or the use of a new application or software, including collaborative software (or groupware), to support the program or activity in terms of the creation, collection or handling of personal information?  Yes, the platform provides new solutions and services to deliver infrastructure support to cloud-based applications and services.  Does the new or substantially modified program or activity require any modifications to information technology legacy systems?  No. | |
| Specific technological issues and privacy  Does the new or substantially modified program or activity involve implementation of new technologies or one or more of the following activities:  - enhanced identification methods (e.g., biometric technology); - surveillance; or - Automated personal information analysis, personal information matching and knowledge discovery techniques?  Yes, the Microsoft Azure data centre, the Statistics Canada cloud infrastructure platform, and the private network between Statistics Canada and the Microsoft cloud Azure data centre have all been assessed and authorized by the appropriate Government of Canada entities to transmit, store, and process personal identifiable information classified up to Protected-B. All required technical, management, and operational privacy and security controls for personal identifiable information have been implemented; for example, federally approved multi-factor authentication has been implemented along with the required level of logging, monitoring, auditing, and reporting of user activities. | |
| Potential risk that in the event of a privacy breach, there will be an impact on the individual or employee.  The components in scope for this privacy impact assessment (Identity and Access Management; Auditing and Logging) process and store a limited amount of personal information (e.g., username, login time, first and last name). The impact of a breach is low. | |
| Potential risk that in the event of a privacy breach, there will be an impact on the institution.  The impact on the institution is considered low due to the security controls implemented. | |

## Conclusion

This assessment of the Cloud Infrastructure Platform did not identify any privacy risks that cannot be managed using existing safeguards. It also demonstrates that the personal or sensitive information collected through this initiative is necessary and proportional to its specific purpose.
