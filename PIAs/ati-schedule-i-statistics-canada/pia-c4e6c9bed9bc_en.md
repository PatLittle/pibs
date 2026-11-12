---
title: "Privacy impact assessment - StatsCAN app"
institution_id: "ati-schedule-i-statistics-canada"
language: "en"
source_url: "https://www.statcan.gc.ca/en/about/pia/app"
retrieved_at_utc: "2026-11-12T01:42:41.031944+00:00"
http_status: 200
source_sha256: "c7eba95775faf19d5643d1fc742a8751933d29c42616e24868fd912ad5c0c210"
content_kind: "page"
---

# Privacy impact assessment - StatsCAN app

## Appendix 1 – PIA Summary

### StatsCAN app Privacy Impact Assessment Summary

**Introduction**

Under the authority of the *Statistics Act*[Footnote 1](https://www.statcan.gc.ca/en/about/pia/app#fn1), Statistics Canada publishes statistical information to inform Canadians about the general activities and condition of the people. To support these dissemination activities, the StatsCAN app was made available in the [Apple App Store](https://apps.apple.com/ca/app/statscan/id1581143394) and [Google Play Store](https://play.google.com/store/apps/details?id=com.statcan.StatCan&pcampaignid=web_share) on January 31, 2022. This free app lets Canadians tap into expert analysis, fun facts, visuals, short stories and insights that bring together data, tools and publications to provide them with the latest information on Canada's economy, society and environment.

The app provides timely and convenient access to trusted, unbiased facts right from Statistics Canada and provides a personalized browsing journey allowing users to follow subjects of interest to know when the latest publications become available, save publications for reading later, or opt-in to in-app notifications that provide a comprehensive overview of the country's latest statistical news.

The StatsCAN app supports the five pillars of Statistics Canada's modernization agenda[Footnote 2](https://www.statcan.gc.ca/en/about/pia/app#fn2), which align with the agency's mission, vision, and values. These pillars respond to the ever-changing data landscape and to users' and stakeholders' requirements for more data, provided faster, and made available in multiple formats and from multiple access points.

The initial StatsCAN app was not intended or built to collect, use, or disclose any user personal information aside from standard aggregate app metrics and Key Performance Indicators (KPI) provided by the respective app stores hosting the app to measure app performance, such as number of downloads, uninstalls, number of active users, etc., and only in-app notifications were available to users. As such, the initial implementation did not require a Privacy Impact Assessment.

However, in Statistics Canada’s efforts to enhance the app and deliver additional features to improve the user experience, some new functionalities (a feedback form, in-app metrics, and push notifications), are being implemented that utilize some user data. As such, this Privacy Impact Assessment (PIA) was created to describe these uses in more detail and analyze potential privacy implications. These new features may be implemented simultaneously or sequentially.

**Objective**

A privacy impact assessment for StatsCAN app was conducted to determine if there were any privacy, confidentiality or security issues with the new functionalities being introduced to the app and, if so, to make recommendations for their resolution or mitigation.

**Description**

### Feedback form

**Purpose**

The purpose of the feedback form is to receive feedback from StatsCAN app users regarding their thoughts and opinions about the app, any improvements they would like to see, or as a mechanism to report issues or bugs. This information will assist the StatsCAN app team in decision-making about the app. The advantage of this feedback form mechanism over the current one is that it will allow users to communicate more easily and directly with Statistics Canada’s app team (users may not wish to publicly post on their app store, and may similarly not wish to leave the app to submit feedback). Unlike the generic [Contact Us form](https://www.statcan.gc.ca/en/) that exists on the StatCan website, the new feedback form will be specific to the StatsCAN app, making it easier for users to identify any technical bugs, and provide device information to assist the team in resolving the bugs reported. The StatsCAN app feedback form is not intended to replace the Contact Us form where users wish to contact Statistics Canada regarding the agency’s products and services, or to inquire about concepts, methods or data quality of releases.

The form is hosted on the Statistics Canada website but is not linked to the homepage, or any other public-facing pages on the StatCan website. The form has been developed to be ‘hidden’ and will only be accessible from a desktop if the user has a direct link. Although the form will be hosted on the website, it will be directly integrated within the StatsCAN app and accessible through the Settings screen.

Submission of identifiable personal information (email address) is not mandatory. If the user chooses to leave their email address when reporting an issue or sending a comment or suggestion, the app team may follow up with the user (if more details are required). However, if the user does not want to leave contact information, feedback can be submitted anonymously, without direct identifiers.

### In-app metrics

**Purpose**

New in-app metrics (detailed below) will be analyzed by the StatsCAN app team to better understand their users. These metrics will inform what type of content users are interested in and what types of features are being used most often. In-app metrics will enable the app team to continue building a product that meets users’ needs and delivers an ideal user experience.

Google Analytics for Firebase ("Firebase”) will be the technology used to collect and analyze detailed in-app metrics for both Android OS and iOS users. Firebase was selected due to project parameters and budgetary considerations, as the estimated time and effort for implementation by the StatsCAN app IT[Footnote 3](https://www.statcan.gc.ca/en/about/pia/app#fn3) team was much lower compared to other analytics services for mobile. Firebase was also identified as an industry standard for collecting and analyzing in-app metrics. In-app metrics are collected using an Application Program Interface (API) that is plugged into the back-end of the StatsCAN app allowing it to process certain information in accordance with the relevant Firebase Terms of Service[Footnote 4](https://www.statcan.gc.ca/en/about/pia/app#fn4). This functionality will be appropriately assessed to ensure compliance with applicable Canadian legislation and TBS direction before going into live production (operationalization). Any risks or vulnerabilities found within the assessment will be mitigated and approved by the relevant partners.

For more information on how the StatsCAN app’s third-party analytics service provider uses and safeguards user data, please consult:

- Firebase services: [Privacy and Security in Firebase](https://firebase.google.com/support/privacy)
- Google Analytics: [Safeguarding your data](https://support.google.com/analytics/answer/6004245#info_for_visitors&zippy=%2cwhat-is-the-data-used-for)
- Google: [How Google uses information from sites or apps that use our services](https://policies.google.com/technologies/partner-sites)

Users can learn more and manage their information used by Google services at [Privacy Policy – Privacy & Terms – Google](https://policies.google.com/privacy).

If users do not want their information to be used by the third-party analytics service provider, they may alternatively access the same published content on [Statistics Canada’s website](https://www.statcan.gc.ca/), which adheres to Statistics Canada’s [general privacy notice](https://www.statcan.gc.ca/en/about/transparency/privacy).

### Push notifications

**Purpose**

The purpose of push notifications is to improve the user experience by better notifying users of the availability of StatCan products and releases that interest them. Users will no longer need to access the app directly to be notified of new releases, should they choose to enable push notifications. Notifying users of new content that has been published in the app will also increase the visibility and use of new data, as well as its timeliness. This will, in turn, increase the agency’s relevance and reach to the Canadian public.

**Risk Area Identification and Categorization**

The PIA identifies the level of potential risk (level 1 is the lowest level of potential risk and level 4 is the highest) associated with the following risk areas:

| a) Type of program or activity  Risk scale | |
| --- | --- |
| Program or activity that does not involve a decision about an identifiable individual. | 1 |
| **b) Type of personal information involved and context** | |
| Personal information, with no contextual sensitivities after the time of collection, provided by the individual with consent to also use personal information held by another source. | 2 |
| **c) Program or activity partners and private sector involvement** | |
| Within the institution (among one or more programs within the same institution) | 1 |
| **d) Duration of the program or activity** | |
| Long-term program or activity. | 3 |
| **e) Program population** | |
| \* The program’s use of personal information is not for administrative purposes. Information is collected for client information and public communications purposes and will not be used to make a decision about any identifiable individual. | N/A |
| **f) Personal information transmission** | |
| The personal information is transmitted using wireless technologies. | 4 |
| **g) Technology and privacy** | |
| To implement in-app metrics, Firebase, a mobile application development platform developed & operated by Google will be collecting and handling personal information. Firebase will collect user behaviour metrics within the StatsCAN mobile application. | |
| **h) Potential risk that in the event of a privacy breach, there will be an impact on the individual or employee.** | |
| There is a very low risk of a breach of some of the personal information being disclosed without proper authorization. The impact on the individual would be minor. | |
| **i) Potential risk that in the event of a privacy breach, there will be an impact on the institution.** | |
| There is a very low risk of a breach of some of the personal information being disclosed without proper authorization. The impact on the institution would be minor. | |

### Conclusion

This assessment of the StatsCAN app did not identify any privacy risks that cannot be managed using existing safeguards.

## Footnotes

Footnote 1
:   Paragraph 3(a) of the *Statistics Act* mandates Statistics Canada to collect, compile, analyse, abstract and publish statistical information relating to the commercial, industrial, financial, social, economic and general activities and condition of the people. The StatsCAN app serves the publication requirement.

    [Return to footnote 1 referrer](https://www.statcan.gc.ca/en/about/pia/app#fn1-rf)

Footnote 2
:   The Statistics Canada modernization program is broad-based in its approach. It encompasses client relations, workplace culture, and the methods, policies and practices followed for collecting and producing statistics. The principles guiding the Agency's modernization are reflected in its five pillars of modernization: user-centric service delivery; leading-edge methods and data integration; statistical capacity building and leadership; sharing and collaboration; and modern workforce and flexible workplace.

    [Return to footnote 2 referrer](https://www.statcan.gc.ca/en/about/pia/app#fn2-rf)

Footnote 3
:   The StatsCAN IT team is comprised of 3-6 people.

    [Return to footnote 3 referrer](https://www.statcan.gc.ca/en/about/pia/app#fn3-rf)

Footnote 4
:   The Terms of Service generally stipulate that some end-user data related to their app usage may be processed in order to provide the analytics services. Moreover, these terms also state that operations and processing are compliant with local and international legal requirements, advanced security measures are in place at all times (backed by ISO 27001 Certification), and Statistics Canada has the ability to audit Firebase operations and have its data deleted. For reference, see:

    - Privacy and Security in Firebase
    - Google Analytics for Firebase Use Policy
    - Firebase Data Processing and Security Terms
    - Terms of Service for Firebase Services

    [Return to footnote 4 referrer](https://www.statcan.gc.ca/en/about/pia/app#fn4-rf)
