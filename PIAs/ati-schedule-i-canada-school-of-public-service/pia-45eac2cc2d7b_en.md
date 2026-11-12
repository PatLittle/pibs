---
title: "CSPS Privacy Impact Assessment (PIA) Summary: Microsoft 365 and ThinkOn Compass Data Protect for M365"
institution_id: "ati-schedule-i-canada-school-of-public-service"
language: "en"
source_url: "https://www.csps-efpc.gc.ca/about_us/currentreport/pia-microsoft-office365-thinkon-eng.aspx"
retrieved_at_utc: "2026-11-12T01:42:29.350260+00:00"
http_status: 200
source_sha256: "c5a85671f6e9d32845353569b31e96721b8a101a6012a41f29efa704e5827881"
content_kind: "page"
---

# CSPS Privacy Impact Assessment (PIA) Summary: Microsoft 365 and ThinkOn Compass Data Protect for M365

## Description

This report summarizes the Canada School of Public Service's privacy impact assessment of its transition and integration to Microsoft Office 365.

**Published:** October 3, 2023  
**Author:** Canada School of Public Service

![](https://www.csps-efpc.gc.ca/icons/report.png)

## Overview and PIA initiation

| Government institution | Canada School of Public Service |
| --- | --- |
| Government official responsible for the PIA | **François Brunet**   Director General Chief Digital Officer |
| Head of the government institution or Delegate for section  10 of the Privacy Act | **Julie Bureau**  Manager  Access to Information and Privacy Office |
| Name of program or activity of the government institution | Microsoft 365 |

### Standard or Institution specific class of record

**Information Technology**  
Class of Record Number: [PRN 932](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-classes-records.html#prn932)

**Information Management**  
Class of Record Number: [PRN 944](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-classes-records.html#prn944)

### Standard or Institution specific personal information bank

|  |  |
| --- | --- |
| Security Incident and Privacy Breaches | Bank Number: [PSU 939](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-personal-information-banks.html#psu939) |
| Electronic Network Monitoring Logs | Bank Number: [PSU 905](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu905) |
| Employee Personnel Record | Bank Number: [PSE 901](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-personal-information-banks.html#pse901) |
| Outreach Activities | Bank Number: [PSU 938](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#psu938) |
| Training and Development | Bank Number: [PSE 905](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html#pse905) |
| Internal Audit | Bank Number: [PSU 941](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-personal-information-banks.html#psu941) |

### Legal authorities for program or activity

- [Canada School of Public Service Act](https://laws-lois.justice.gc.ca/eng/acts/c-10.13/page-1.html)
- [Financial Administration Act](https://laws-lois.justice.gc.ca/eng/acts/F-11/page-3.html#docCont)

## Summary of the project, initiative or change

### Overview of the Program or Activity

This project oversees the transition and integration to Microsoft 365 and the implementation of ThinkOn Compass Data Protect for M365 as a backup solution. This has the purpose of modernizing the Canada School of Public Service infrastructure, improving the tools that are available to employees, protecting organizational data, and providing a higher degree of availability and accessibility.

The project also allows Digital Services to better fulfill its roles and responsibilities. More information about Digital Services and other directorates can be found [here](https://www.csps-efpc.gc.ca/about_us/organizationalstructure-eng.aspx#gs).

## Risk identification and categorization

| Risk Area | Level of Risk | Details |
| --- | --- | --- |
| A) Type of program or activity | 3 | The platform is authorized for data up to Protected B inclusively. Microsoft 365's purpose is to facilitate collaboration and offer productivity tools that will help provide a better service to our clients.  ThinkOn Compass Data Protect for M365's purpose is to back up the data stored on the various M365 services to protect our data from data loss. |
| B) Type of personal information involved and context | 2 | The information required for the creation of a new user in Microsoft 365 can either be collected directly from the user, a manager or from Shared Services Canada.  ThinkOn: The same information will be collected from M365 to be backed up on ThinkOn Compass Data Protect for M365. |
| C) Program or activity partners and private sector involvement | 2 | While Microsoft 365 is a cloud based service hosted on Microsoft's infrastructure, personal information is not being shared with them. The personal information used for managing user accounts is only shared with Shared Services Canada.  While ThinkOn Compass Data Protect for M365 is a cloud based service hosted on ThinkOn's infrastructure, personal information is not being shared with them. The personal information used for managing user accounts is only shared with Shared Services Canada. |
| D) Duration of the program or activity | 3 | Microsoft 365 will be adopted for the foreseeable future. There is currently no end date. The duration of the program will depend on how long Microsoft supports this solution for and also depends on future technology adoption trends.  ThinkOn Compass Data Protect for M365 will be used in conjunction with M365 for the foreseeable future. There is currently no end date. The duration of the program will depend on how long ThinkOn supports this solution, Microsoft supports M365, and also depends on future technology adoption trends. |
| E) Program population | 3 | Microsoft 365 will require contact information about individuals seeking services or collaborating with the Canada School of Public Service. This includes both internal and external users and clients. The contact information required for this activity includes the name, address, telephone number and e-mail address of the individual.  ThinkOn: A copy of this same M365 information will be stored on ThinkOn services for the purpose of backup. |
| F) Technology & privacy | 1. Does the new or modified program or activity involve the implementation of a new electronic system, software or application program including collaborative software (or groupware) that is implemented to support the program or activity in terms of the creation, collection or handling of personal information? | Yes  Laptops have Trusted Platform Module (TPM) chips that will be registered in Microsoft Azure. Also, Active Directory Federation Services (ADFS), Single Sign-On (SSO) and Multi-Factor Authentication (MFA) will be used.  Some functionalities of Microsoft 365 can be leveraged to gather audit trails and to monitor activities.  IP addresses, user names and other network traffic data can be used to monitor connection patterns and identify potential suspicious activity. |
| 2. Does the new or modified program or activity require any modifications to IT legacy systems and / or services? | Yes |  |
| 3. Does the new or modified program or activity involve the implementation of one or more of the following technologies:  - Enhanced identification methods - Use of surveillance - Use of automated personal information analysis, personal information matching and knowledge discovery techniques | Yes |  |
| Yes |  |
| Yes |  |
| G) Personal information transmission | 4 | Microsoft 365: While the servers are using wired internet connections, users may be using wireless connections when connecting to Microsoft 365.  ThinkOn: The servers use wired internet connections, however, administrators will connect to the ThinkOn backup management platform via an internet browser from a workstations which may be using a wireless connection. |
| H) Potential risk impact to the individual or employee in the event of a privacy breach | 2 | For both Microsoft 365 and ThinkOn:  The level of risk is considered low. In order to provide services to School employees as well as other federal government employees, IT system administrators require contact information such as employee names, e-mail addresses, phone numbers, departmental addresses and IP addresses. System administrators are not permitted to access personal and/or protected user files that are being stored on the Microsoft 365, Azure or ThinkOn Compass platforms, however they may be authorised to access this information upon request from a legal authority. |
| I) Potential risk impact to the institution in the event of a privacy breach | 2 | For both Microsoft 365 and ThinkOn:  The level of risk is considered low. The personal information stored on the Microsoft 365, Azure or ThinkOn Compass platforms may be at risk. The credibility and perception of the School may be impacted in the event of a privacy breach. |

[Contact us](https://www.csps-efpc.gc.ca/contact_us/index-eng.aspx)

[Subscribe to the GCLearning newsletter](https://www.csps-efpc.gc.ca/stayconnected/eupdatessubscribe-eng.aspx)

## Stay connected:

- [LinkedIn](https://www.linkedin.com/company/school-ecole "LinkedIn")
- [X](https://x.com/School_GC "X")
- [YouTube](https://www.youtube.com/user/MySchoolMonEcole "YouTube")
- [GCLearning newsletter](https://www.csps-efpc.gc.ca/stayconnected/eupdatessubscribe-eng.aspx "GCLearning newsletter")
- [RSS](https://www.csps-efpc.gc.ca/stayconnected/csps-rss-eng.xml "RSS")

---

## Features

[![](https://www.csps-efpc.gc.ca/series/images/amplifying-black-voices.png)

Podcast: Amplifying Black Voices](https://www.csps-efpc.gc.ca/series/amplifying-black-voices-eng.aspx)

[![](https://www.csps-efpc.gc.ca/events/thumbnails/project-managment.png)

Project Management Learning Path](https://www.csps-efpc.gc.ca/learning-paths/project-management-eng.aspx)

[![](https://www.csps-efpc.gc.ca/learning-paths/images/digital-competencies.png)

GC Digital Competencies Learning Path](https://www.csps-efpc.gc.ca/learning-paths/digital-competencies-eng.aspx)
