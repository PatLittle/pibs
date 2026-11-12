---
title: "CSPS Privacy Impact Assessment (PIA) Summary: Brightspace – Power BI Reporting Tool"
institution_id: "ati-schedule-i-canada-school-of-public-service"
language: "en"
source_url: "https://www.csps-efpc.gc.ca/about_us/currentreport/pia-brightspace-power-bi-eng.aspx"
retrieved_at_utc: "2026-11-12T01:42:28.532926+00:00"
http_status: 200
source_sha256: "7b5f41fd70b0143b0f5c039adf666dacb13d50b1eea9dacd9c900a0bf0b33d97"
content_kind: "page"
---

# CSPS Privacy Impact Assessment (PIA) Summary: Brightspace – Power BI Reporting Tool

## Description

This report summarizes the Canada School of Public Service's privacy impact assessment of Brightspace, Power BI and Synapse Analytics.

**Published:** October 3, 2023  
**Author:** Canada School of Public Service

![](https://www.csps-efpc.gc.ca/icons/report.png)

## Overview and PIA initiation

| Government institution | Canada School of Public Service |
| --- | --- |
| Government official responsible for the PIA | **François Brunet**  Director General Chief Digital Officer |
| Head of the government institution or Delegate for section  10 of the Privacy Act | **Julie Bureau**  Manager  Access to Information and Privacy Office |
| Name of program or activity of the government institution | Brightspace Digital Learning Environment |

### Standard or Institution specific class of record

**Training and Development**  
Class of Record Number: [PRN 927](https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/standard-classes-records.html#prn927)

### Standard or Institution specific personal information bank

**Integrated Learning Management System (ILMS)**  
Bank Number: [CSPS PPU 015](https://www.csps-efpc.gc.ca/about_us/currentreport/infosource-eng.aspx#annex)

### Legal authority for program or activity

- [Canada School of Public Service Act](https://laws-lois.justice.gc.ca/eng/acts/c-10.13/page-1.html), section 4 and 5
- [Financial Administration Act](https://laws-lois.justice.gc.ca/eng/acts/F-11/page-3.html#docCont), paragraph 12(1)(a)

## Summary of the project, initiative or change

### Overview of the Program or Activity

CSPS Learning Services uses Brightspace to deliver, manage and report on the training authorized by CSPS for GoC learners. Brightspace replaces legacy systems (e.g. GCcampus and Saba) with a single Learning Management System that meet CSPS requirements. Brightspace is used to deliver training, events and professional development opportunities to GoC employees, so that the GoC departments can develop their full potential while fulfilling their legal and legislative responsibilities. In essence, it is a management tool that regulates the actual delivery of training and events. The catalogue of courses that Brightspace delivers includes over 450 courses and numerous events in both official languages. Some of this training is developed in-house and some is developed by third parties. Simply put, the application associates the following with the GoC Learner:

- what training will take place
- when the training will take place
- how the training will be delivered
- who will deliver the training
- results of any tests taken during the training
- attendance at the training
- if the training has been completed
- learner activities associated with the training

If the training has been successfully completed, Brightspace provides the ability to print a certificate of completion and a transcript. It is important to consider that Brightspace, Synapse Analytics and Power BI connect these records with a learner profile.

1. CSPS acquired its own instance of a digital learning management system (LMS) known as Brightspace.
2. The reason that a PIA is being conducted is to ensure that the activities meets current privacy requirements, and mitigate any privacy risks and reduces potential impacts with privacy implications.

Synapse Analytics is a cloud-based PaaS application that serves as the School’s new data warehouse i.e. a single repository and source of truth for the School’s data. Synapse Analytics serves as the back-end system for Power BI, the School's data visualization tool (see next entry). Data collected in Brightspace is regularly copied into Synapse Analytics.

Power BI is a cloud-based SaaS application that serves as the School’s data visualization tool. Data that has been copied into Synapse Analytics (including data collected in Brightspace) is visualized and made available to stakeholders in the form of dashboards and reports.

## Risk identification and categorization

| Risk Area | Level of Risk | Details |
| --- | --- | --- |
| A) Type of program or activity | 4 | The information associated with a learner can be used to make decisions that directly affect the individual.  Data collected in Brightspace is then in turn stored in the Synapse Analytics data warehouse and reported using the Power Bi application.  Information collected in Brightspace, stored in Synapse Analytics and reported in Power BI is used for compliance and could be used for investigations and enforcement. |
| B) Type of personal information involved and context | 2 | Brightspace, Synapse Analytics and Power BI link this personal information with information on courses and events that the learner has taken namely:   - what training will take place - when the training will take place - how the training will be delivered - who will deliver the training - attendance at the training - the results of any tests that are associated with the course - if the training has been completed - learner activities associated with the training |
| C) Program or activity partners and private sector involvement | 2 | The program and activity participants are as follows:   - CSPS management and staff that are involved in the delivery, management and reporting on training and events - Management and staff of client organizations with whom the School has signed data-sharing agreements that are involved in reporting on training and events - Central agency representatives working on compliance or policy activities - GoC learners who get to see their training   The private sector organizations are D2L, as the vendor of Brightspace, and Microsoft, as the vendor of Synapse Analytics and Power BI. |
| D) Duration of the program or activity | 3 | The management of training and events at CSPS has a long history and Brightspace is an upgrade of technology that will provide better, more efficient and effective training and events operations to the GoC learners.  Providing better business intelligence to business lines and client organizations is a key goal driving the adoption of Synapse Analytics as a data warehousing tool and Power BI as a reporting tool. |
| E) Program population | 2 | The program affects various GoC Learners including indeterminate, term, students, casual and consultants engaged in mandatory and optional external training and events. |
| F) Technology & privacy | 1. Does the new or modified program or activity involve the implementation of a new electronic system, software or application program including collaborative software (or groupware) that is implemented to support the program or activity in terms of the creation, collection or handling of personal information? | Yes.  Once Power BI is fully implemented, Cognos (legacy data visualization tool) will be switched off and all reports and dashboards will be developed and distributed through Power BI.  D2L is fully implemented, SABA (legacy LMS) is discontinued.  Once Synapse Analytics is fully implemented, the legacy data warehouse will continue to remain in use until SABA (legacy LMS) is fully replaced by D2L. Once SABA is fully replaced by D2L, the legacy data warehouse will be shut down, and all required legacy data will be migrated in a one-time export into Synapse Analytics.  Brightspace uses an audit trail to track unauthorized access, modification and deletion.  Synapse Analytics uses an audit trail to track when Azure resources are used (e.g. a database is paused or resumed), when files are created or modified, and when changes are made to the code base.  Power BI uses an audit trail to track which users viewed reports and dashboards. |
| 2. Does the new or modified program or activity require any modifications to IT legacy systems and / or services? | Yes |  |
| 3. Does the new or modified program or activity involve the implementation of one or more of the following technologies:  - Enhanced identification methods - Use of surveillance - Use of automated personal information analysis, personal information matching and knowledge discovery techniques | No |  |
| Yes |  |
| No |  |
| G) Personal information transmission | 4 | Data collected in Brightspace is then in turn stored in the Synapse Analytics data warehouse and reported using the Power BI application.  Brightspace, Synapse Analytics and Power BI are web-based platforms accessed via the HTTPS protocol.  The platforms allow printing of the information that the person has access to.  It is also important to note that the platforms assign roles to the various classes of users. It is through these roles that the platforms’ administrators regulate the amount of information that a user is allowed to view. As web-based platforms, personal information may be transmitted using wireless technologies. |
| H) Potential risk impact to the individual or employee in the event of a privacy breach | 3 | The potential harm associated with a privacy breach would be the knowledge of:   - whether or not an employee had the required training associated with the performance of their job; - the results of any testing associated with a completed course. |
| I) Potential risk impact to the institution in the event of a privacy breach | 4 | The potential risk impact to the institution in the event of a privacy breach to CSPS would be whether or not an employee had the mandatory training associated with the performance of their job. This may also incur reputation harm, embarrassment and/or loss of credibility to the department. |

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
