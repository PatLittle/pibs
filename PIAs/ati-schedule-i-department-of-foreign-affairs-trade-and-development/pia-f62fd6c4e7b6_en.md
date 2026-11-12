---
title: "Passport Canada’s Mail Tracking System (MTS) - Privacy Impact Assessment: Global Affairs Canada"
institution_id: "ati-schedule-i-department-of-foreign-affairs-trade-and-development"
language: "en"
source_url: "https://international.canada.ca/en/global-affairs/corporate/transparency/atip/impact-assessment/passport-canada/mts"
retrieved_at_utc: "2026-11-12T05:48:55.658044+00:00"
http_status: 200
source_sha256: "a4b82a13a0fb15198a89270a62747af263d893263ff8d563c8bdee7e2edaa691"
content_kind: "page"
---

# Passport Canada’s Mail Tracking System (MTS) - Privacy Impact Assessment: Global Affairs Canada

## Executive summary

The need to implement a mail tracking system at Passport Canada (PPTC) has been identified as an urgent operational priority; the rationale being the critical need to ensure PPTC’s ability to effectively track mail received to issue passports / travel documents prior to the upcoming peak season.

The Operational objective was to deploy the system/solution nationally, starting June 16th, 2008, at the new mail–in processing location, 22 De Varennes in Gatineau. Other than a few technical problems, which were solved, the installation went as planned.

This project provides a complete solution to track applications from the time they enter PPTC facilities to the time a service request is created in IRIS (IRIS is an Integrated Retrieval Information System for Passport Canada’s/Passport issuance System). The project also provides management with a means to generate statistical reports, which have been defined during the design phase of this project.

Currently, applications are only tracked from the moment that they are entered in IRIS. As a result of the volume, applications are sometimes not entered in IRIS for as long as three months (sixty business days). The delay in the processing of applications also resulted in an increase in information requests from the public regarding their application. When the public makes an information request, PPTC must locate the application and action it accordingly. Because of the volume of requests, and the inability to effectively track each application that entered PPTC premises, it could take up to one week to locate the applicant’s file. PPTC staff was forced to physically search through a large number of applications.

Further to the implementation of the Mail Tracking System (MTS), it was expected that the increase in the efficiency of tracking the large volume of mail received by PPTC will improve its capability to respond to the public as well as action applicant requests.

Improving PPTC Mail Tracking ability allows PPTC to alleviate some of the pressure placed on staff to locate files. This project helps PPTC maintain customer service satisfaction by increasing the efficiency of locating applications when requested.

In order to assess the privacy impact of the Mail Tracking System Project, a Privacy Impact Assessment (PIA) was undertaken. The methodology used for the report is found in the Treasury Board Secretariat (TBS) *Privacy Impact Assessment Guidelines*.

The personal information captured in the Mail Tracking System Project consists of two (2) different categories of data:

1. **Information on clients of PPTC:** The personal information collected from the client to be entered into the Mail Tracking System consists of: Surname, Given Name, Date of Birth, Addresses, Telephone number. A tracking code number (a series of letters and numbers located at the bottom of the envelope, such as: TA 052-389-674CA) taken from the envelope in which the application was mailed in is also collected. At a later time, an Electronic Service Request File Number (ESRF) will be allocated to the file.
2. **Mail Tracking System Project User Information:** This is Information on the users of the system that may be contained within the application, such as Password, Access Profile and language, when the user was logged on, any other personal information that may be contained in the system logs. There are no privacy concerns with the collection of this information.

The personal information on clients was previously collected by PPTC for the purpose of issuing a passport to the individual. The privacy concerns for the initial consent and reason for collecting this information were out of scope of the completed PIA. The PIA focused on a subset of the personal information contained in the application, as stated in Paragraph a. and this information is collected for the purpose of tracking the passport application. The information contained in the Mail Tracking System is only used to identify the applicant, and confirm that information on where the application sits in the system at any given time is given only to the person entitled to receive this information.

## Risks and Mitigating Measures

Here is a description of the levels of risks:

- **Low**: There is a possibility that the risk will materialize but there are mitigating factors.
- **Medium**: There is a strong possibility that the risk will materialize if no corrective measures are taken.
- **High**: There is a near certainty that the risk will materialize if no corrective measures are taken.

The following risks have been identified through the PIA Process. The risk factor attributed has been determined by both the likelihood of occurrence and the impact it would have on Passport Canada.

1. **Certification and Accreditation not completed**

   **Risk:** This risk has been identified as medium. The Mail Tracking System has not gone through the Certification and Accreditation process.  
   **Mitigation:** A certification and accreditation should be completed on the Mail Tracking System in accordance with section 3.2.3 of Passport Canada’s IT Security Policy.

   Accreditation signifies that senior management has authorized the Mail Tracking System to be commissioned into production and has accepted the residual risk of operating the system based on the certification evidence and the Threat and Risk Assessment. At the time the PIA was completed, the certification and accreditation had not been preformed, but was included in the action plan to be performed at a later date. The certification and accreditation was conducted in early spring 2009 which reduces the risk to low level.
2. **Proper identification of Clients**

   **Risk:** This risk has been identified as high. Giving out information about an individual to the wrong person could result in a breach of privacy and cause embarrassment to the government of Canada and PPTC.

   **Mitigation:** PPTC must clearly identify the individual before giving or sending any information on the passport application request in question. A procedure must be in place for Call Center agents to be able to properly identify the applicant over the phone.

   At this time, procedures are in place to verify the identity of the person, should that person be requesting information on their own passport. However, should the individual be other than the individual for whom the passport request is being made, procedures needs to be implemented to either have the ability to ascertain that the person has authority to receive information or the call is to be terminated.

   Call Center agents have reviewed and updated their procedures as of January 2009 for their ability to ascertain that the person has authority to receive information or the call is to be terminated.
3. **Single Factor Identification**

   **Risk:** This risk has been identified as medium. MTS uses single factor authentication, i.e. username and password. There could be some hacking into the system. Username and password is not deemed sufficient to protect Protected B information.

   **Mitigation:** This risk will be mitigated when PPTC adopts a multi–factor authentication method in a subsequent version of the MTS.. As of July 9th, 2009, this system had not been designed.
4. **User Identification**

   **Risk:** User identification is required to allow for tracking the individual that performs each task. PPTC has identified the risk and it will be mitigated and fixed at the organisational level.

   **Mitigation:** The solution will be implemented to all systems/applications used at PPTC. The interim solution until Passport Canada is ready for full encryption is to install Entrust Encryption Certificate on the server that DE+ application will be installed.
5. **Encryption**

   **Risk:** This risk has been identified as medium. It affects the confidentiality and integrity of data.

   **Mitigation:** Encryption is an effective safeguard for protecting information from eavesdropping, man–in–the–middle attacks, or other means of interception or manipulation of the information as it is being transmitted. The use of Client Side Encryption will mitigate this risk.
