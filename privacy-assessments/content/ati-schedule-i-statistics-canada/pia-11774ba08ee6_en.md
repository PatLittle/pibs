---
title: "Vitali-T-Stat Mobile Application - Privacy impact assessment summary"
institution_id: "ati-schedule-i-statistics-canada"
language: "en"
source_url: "https://www.statcan.gc.ca/en/about/pia/vitali-t-stat-mobile-application"
retrieved_at_utc: "2026-11-12T01:42:47.915760+00:00"
http_status: 200
source_sha256: "a80eaf332c503e9ddc4e9fdf60a9d4fce6b9991fe7c77a217e44a4d5dc894e8e"
content_kind: "page"
---

# Vitali-T-Stat Mobile Application - Privacy impact assessment summary

## Introduction

Under the authority of the *Statistics Act*[Footnote 1](https://www.statcan.gc.ca/en/about/pia/vitali-t-stat-mobile-application#fn1), Statistics Canada is developing and implementing a mobile application as a new method to invite respondents to access the agency’s secure survey collection infrastructure and complete a survey. The application itself does not collect any personal information; it simply prompts respondents and points them to the secure collection environment housed at Statistics Canada where they complete the survey questionnaire. It will first be used in the context of the longitudinal Pilot Study on Everyday Well-being which will collect data on the well-being of Canadians, and for which a separate supplement to Statistics Canada’s Generic PIA supplement was developed.

## Objective

A privacy impact assessment (PIA) for the Vitali-T-Stat Mobile Application was conducted to determine if there were any privacy, confidentiality or security issues with this initiative and, if so, to make recommendations for their resolution or mitigation.

## Description

The application will be hosted on the Google Play and Apple App stores, and this first iteration will be named Vitali-T-Stat.

Canadians will be invited to participate in the voluntary longitudinal study and given instructions on how to download the application. The mobile application is a hybrid application which means that it includes a native component that is stored and operates on a mobile device, and links to web-based components that are stored on a web portal and accessed through a web browser.

The native component of the application enables a person to download the application from an app store and store it on their device, secure it with a password and a security question, and receive notifications to participate in the study. It also contains Getting Started information specific to the Pilot Study on Everyday Well-being, Terms and Conditions for using the application, contact information for Statistics Canada, Frequently Asked Questions for using the application, and a settings menu. Within the settings menu, the respondent can customize their notification settings.

The application links to two web-based components that require the respondent to be connected to data or Wi-Fi while in use:

1. START  
   This component will connect the respondent to Statistics Canada’s secure anonymous collection portal where they will complete and submit their questionnaires.
2. Results  
   This component will connect the respondent to a secure Statistics Canada web portal where they can review aggregated trends of their personal data.

When the respondent selects either of these components, an Application Programming Interface (API) will be activated. An API is a software intermediary which allows two applications to talk to each other through a secure channel. The API will authorize access to Statistic’s Canada secure collection web portal through the API connection, and will present the respondent with the questionnaire if they select START, or their personalized data dashboard if they select Results. The questionnaire and the dashboard are presented within the application, but they both remain stored on Statistics Canada secure web portals where the information will reside.

## Risk Area Identification and Categorization

The PIA identifies the level of potential risk (level 1 is the lowest level of potential risk and level 4 is the highest) associated with the following risk areas:

### a) Type of program or activity

Program or activity that does not involve a decision about an identifiable individual.  
Risk scale: 1

### b) Type of personal information involved and context

Not-applicable. The Vitali-T-Stat mobile application does not collect or handle any personal information. The survey itself is collected on Statistics Canada’s secure collection infrastructure which is assessed in Statistics Canada’s Generic Privacy Impact Assessment.  
Risk scale: N/A

### c) Program or activity partners and private sector involvement

Private sector organizations, international organizations or foreign governments.  
Risk scale: 4

### d) Duration of the program or activity

Short-term program or activity.  
Risk scale: 2

### e) Program population

Not-applicable. The Vitali-T-Stat mobile application does not collect or handle any personal information. The survey itself is collected on Statistics Canada’s secure collection infrastructure for statistical purposes, under the authority of the *Statistics Act*.  
Risk scale: N/A

### f) Personal information transmissionn

Not-applicable. The Vitali-T-Stat mobile application does not collect or transmit any personal information. The survey itself is collected on Statistics Canada’s secure collection infrastructure for statistical purposes, under the authority of the *Statistics Act*.  
Risk scale: N/A

### g) Technology and privacy

This application has been developed as a new way for respondents to access the agency’s existing secure survey collection infrastructure. After respondents select the START menu item in the application, they will be redirected with an Application Programming Interface (API - a software intermediary which allows two applications to talk to each other through a secure channel) to Statistics Canada’s secure anonymous collection portal, where the respondent will complete and submit their questionnaire(s). This secure portal is entirely autonomous from the application.

The mobile hybrid application does not create, collect or handle any personal information.

A unique identifier will be generated by the application when the respondent installs it. This unique identifier will be sent to Statistics Canada’s server when the respondent submits their questionnaire data. This will enable Statistics Canada to complete record linkages both to populate the respondent’s results dashboard, as well as for analytical purposes. To populate the results dashboard, the unique identifier will be sent with the questionnaire responses to Statistics Canada’s secure server. The server will then create a secure access code (SAC) and assign it to the unique identifier. The questionnaire data will then be released to a secure Statistics Canada web portal. When the respondent selects the results dashboard in the application, the unique identifier in the respondent’s application will be validated against the SAC on the secure web portal. If the validation is successful, a static image of aggregate results specific to the respondent will be presented. If the validation is not successful, the dashboard will remain blank.

Statistics Canada’s Collection Management Portal was modified to enable the generation of the SAC, process the respondent’s data, generate a static image presenting the respondent’s aggregate individual dashboard, and complete the validation to release the image back to the respondent.

In addition, minor modifications were made to present the electronic questionnaire, accessible from Statistics Canada’s secure collection web portal, in a mobile application-friendly look and feel. These modifications were cosmetic and did not impact functionality.

### h) Potential risk that in the event of a privacy breach, there will be an impact on the individual or employee.

There is a very low risk of personal information being disclosed without proper authorization. The impact on the individual would be low as the Vitali-T-Stat mobile application itself does not collect or handle any personal information.

### i) Potential risk that in the event of a privacy breach, there will be an impact on the institution.

There is a very low risk of personal information being disclosed without proper authorization. The impact on the institution would be low as the Vitali-T-Stat mobile application itself does not collect or handle any personal information.

## Conclusion

This assessment concludes that the Vitali-T-Stat mobile application does not add risk to Statistics Canada’s data collection practices and did not identify any privacy risks that cannot be managed using existing safeguards.

## Footnotes

Footnote 1
:   Paragraph 3(a) of the Statistics Act mandates Statistics Canada to collect, compile, analyse, abstract and publish statistical information relating to the commercial, industrial, financial, social, economic and general activities and condition of the people. Paragraph 5(a)(i) provides the Chief Statistician with the duty to decide, based strictly on professional statistical standards that he or she considers appropriate, the methods and procedures for carrying out statistical programs regarding the collection, compilation, analysis, abstraction and publication of statistical information that is produced or is to be produced by Statistics Canada.

    [Return to footnote 1 referrer](https://www.statcan.gc.ca/en/about/pia/vitali-t-stat-mobile-application#fn1-rf)
