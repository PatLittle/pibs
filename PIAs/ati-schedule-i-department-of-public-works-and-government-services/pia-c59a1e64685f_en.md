---
title: "Compensation Web Applications: Privacy impact assessment summary"
institution_id: "ati-schedule-i-department-of-public-works-and-government-services"
language: "en"
source_url: "https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html"
retrieved_at_utc: "2026-11-12T01:42:17.347828+00:00"
http_status: 200
source_sha256: "97894d9c208599335cc6b1822e550dfaf87579d0bfde1429b0c9510b2d24dc4d"
content_kind: "page"
---

# Compensation Web Applications: Privacy impact assessment summary

## On this page

- [Introduction](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html#a1)
- [Business benefits](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html#a2)
- [Data analysis](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html#a3)
- [Privacy risk management](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html#a4)
- [Communications plan](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html#a5)
- [Conclusion](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2005-2006/compensation-web-applications-summary.html#a6)

## Introduction

In support of the Government On-Line initiative and, as recommended in the compensation modernization study, the Compensation Sector of the Accounting, Banking and Compensation Branch of Public Works and Government Services Canada is progressively implementing a series of secure, online, electronically delivered, services known as Compensation Web Applications for access by all Government of Canada employees. The following reflect the current services offered by the Compensation Web Applications.

- Pension and benefits statement
- Payment stub on the web
- Request for changes to voluntary deductions via web
- Gross-to-net regular pay estimate calculator
- Compensation advisor access to web applications for employees
- Compensation common services database and classification reform

Additional functionality will be introduced within this framework in future upgrades to the service.  
The Access and Identity Management Services infrastructure provides online registration and enrolment functionality in support of these business level applications. This functionality is based on Internal Credential Management public key infrastructure (PKI). The following reflects these major services.

- Creation of an **anonymous certificate** for each registering employee
- A **customization service** to the G-Pass self-administration server that allows anonymous registration and integration through a G-Pass secret service
- A G-Pass **secret service** to allow for recovery and revocation as a PKI self-administration function
- A **personal identification number service** to assist the enrolment service in the identification of enrolled users
- A **mapping service** to manage the PKI to application user identifiers

For all systems, the Treasury Board of Canada Secretariat-published Privacy Impact Assessment Policy requires that a formal assessment of how the service offering ensure the privacy of any personal information collected or made available throughout the service's life cycle. The process encompasses the ten privacy principles reflected in that policy.

This summary of the formal privacy impact assessment reflects the finding and decisions emanating from that assessment. Its presentation in this forum is intended to assure both public and private sector Canadians that these services reflect the strong and total commitment to privacy that the Government of Canada adheres to in all its activities. **This privacy impact assessment is restricted to the business applications functions level only. A separate assessment of the supporting infrastructure has been undertaken.**

The formal review process of this privacy impact assessment is now complete and the Office of the Privacy Commissioner has confirmed that it is satisfied that the Compensation Web Applications service poses a low risk to the privacy of government employees.

## Business benefits

The Compensation Web Application services developed and implemented allow the Compensation Sector of the Accounting, Banking and Compensation Branch of Public Works and Government Services Canada to greatly reduce the need to, and very high cost of, having to regularly print and distribute employee pay and pension summaries. The online services have also permitted the branch to achieve a reduction in the number of administrative staff that has traditionally been required to assist Government of Canada employees in reviewing and initiating any changes required to their personal accounts.

As the service expands to incorporate additional capabilities, cost and manpower savings will continue to be realized.

## Data analysis

**Table 1: Compensation Web Applications data flow table**   
The following table summarizes the types of personal information collected, processed and/or displayed to accessing employees by the business level functional applications.

Table 1: Compensation Web Applications data flow table

| Personal information cluster | Description of personal information cluster | Collected by | Type of format (for example, paper or electronic) | Used by | Purpose of collection | Disclosed to | Storage or retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pension and benefits statement and related applications | Pension and benefits data | Pension and benefits master file | Electronic | - individuals - compensation advisors - pension calculator - service buyback estimator | To provide current and projected pension benefit data to the individual and advisors | - individual employees - compensation Advisors | - pension and benefits statement member - the pension and benefits statement information table are wiped out and reloaded every month; the access information table is then updated |
| Pay stub web and related applications | Employee regular and supplemental pay and tax slips | - regional pay register database - pay stub on the web application | Electronic | - individuals - database load utility and database batch programs - compensation advisors - gross-to-net regular pay estimate calculator - voluntary deductions | - to provide current and historical pay stub data to the individual and advisor - to provide a gross-to-net regular pay calculation - to allow employees to directly initiate, change or terminate voluntary deductions | - individual - compensation advisors - regional pay system | The data is stored on the departmental mainframe |
| Compensation advisor access and compensation common services database and classification reform applications | Compensation common services database and classification reform integrated database management system and Integrated Data Dictionary table data and spreadsheets | Compensation and benefits administrators | Electronic | Advisors to determine and update employee classification data | Maintain employee classification data for pay and benefits purposes | Specifically-authorized advisors | Departmental mainframe |

## Privacy risk management

The Privacy Risk Management Plan summarizes specific privacy issues and risks identified through the assessment process. Mitigating measures taken to reduce or eliminate these risks have been identified and implemented. There are no unresolved risks that might jeopardize the privacy of individual employee users.  
There were only two outstanding privacy concerns identified in the Compensation Web Applications privacy impact assessment. The associated risks and mitigation strategies identified are summarized in the following subparagraphs.

### Privacy Act principle 3: Consent

#### Privacy risk #1

Data relating to employees who do not wish to enrol for the online service offerings must not be available to unauthorized users.

#### Privacy risk mitigation measure

An employee will be required to submit a written request to be excluded. In such cases, the employee data is then removed from the database and it becomes impossible for anyone to enrol as that employee. It should be noted that such an "opting out" also results in the employee being deleted from all of the Compensation Web Applications service offerings. Should the employee later change his or her mind, a formal request that his or her data is to be reinserted into the database must be submitted. The need for a more automated "opting out" process will be re-evaluated after the results of a one year evaluation period using the manual process is concluded.

### Privacy Act principle 7: Safeguarding of personal information

#### Privacy risk #2

That misuse may go undetected.

#### Privacy risk mitigation measure

A "last logged-in" and all unsuccessful attempts made from the time of an employee's last successful log-in is uploaded to the employee at each log-in by the Internal Credential Management session verification module and also be the pension and benefits statement application. The employee is advised to notify the service if the advisory is not correct. In addition, an extensive intrusion detection system is being implemented within the Access and Identity Management Services infrastructure to detect otherwise unnoticed attempts to misuse the services.

## Communications plan

A variety of communications documents has been prepared to allow a progressively rolled out to employees. These documents include the key messages required, various messages or components, responsibility roles and consultation process required prior to release.

## Conclusion

It is evident that the Compensation Web Applications business level implementation has been designed with the view to improving and maintaining privacy throughout the system lifecycle. The implementation of anonymous certificates, session cookies, and other technical mitigating measures, such as encryption of "shared secrets", limiting read/write access to the central services database, making use of the proven Internal Credential Management capability, conducting a threat and risk assessment, implementing processes such as annual audit and quality assurance, and system security certification and accreditation, makes notable contributions to meeting privacy expectations and requirements.
