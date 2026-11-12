---
title: "Privacy Impact Assessment for the Conflict of Interest and Declaration System"
institution_id: "ati-schedule-i-shared-services-canada"
language: "en"
source_url: "https://www.canada.ca/en/shared-services/corporate/about-us/transparency/access-information-privacy/publications/privacy-impact-assessment-coids.html"
retrieved_at_utc: "2026-11-12T01:42:18.643331+00:00"
http_status: 200
source_sha256: "8da67b03c838052f3c2430cca65b81f100992ab0973b2494a39d56b84ec7debe"
content_kind: "page"
---

# Privacy Impact Assessment for the Conflict of Interest and Declaration System

Privacy Impact Assessment Summary

# Conflict of Interest and Declaration System

## Executive Summary

On November 28, 2014, the President of SSC sent out an email containing a link to the COID eForm to all SSC staff. The intent of this email was to remind employees of their obligation to disclose and request that if they had not declared, to do so, using the new COID eForm, prior to or by December 12, 2014. The COID eForm was a first attempt at rendering a paper-based form electronic.

The Conflict of Interest Declaration System (COIDS) replaces the COID eForm, previously paper-based, with an electronic system so that SSC employees can disclose assets, liabilities, outside employment, personal relationships and networks, post-employment and other activities that may potentially give rise to a real, apparent or potential conflicts of interest in relation to the official duties and responsibilities of their position.

## Overview

In accordance with the [Values and Ethics Code for the Public Sector](http://www.tbs-sct.gc.ca/pol-cont/25049-eng.pdf), the [Policy on Conflict of Interest and Post-Employment](http://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=25178&section=text), [Shared Services Canada’s (SSC’s) Directive on Conflict of Interest and Post-Employment](http://myssc-monspc.ssc-spc.gc.ca/en/worktools-processes/policy-instruments/hr/conflict-interest-directive), and SSC’s Organizational Code, all federal employees are required to complete a paper-based Confidential Report when they join the public service and also when their situation changes that could put them in a real, apparent or potential conflict of interest situation.

This is not a new activity and the legislative authority is clearly established as per the [Financial Administration Act](http://laws-lois.justice.gc.ca/eng/acts/F-11/) sections 7 and 11.1(1).

To enhance the protection of personal information, a design decision was made to include the Date of Birth (DOB) in the verification process as a way to reduce the possibility of a security or privacy breach. With respect to the Personal Information Bank (PIB) at issue, Treasury Board Secretariat has confirmed that no changes are required to the Standard Personal Information Bank PSE 915 “Values and Ethics Codes for the Public Sector and Organizational code(s) of Conduct”, because PSE 915 includes a reference to “biographical information”.

## Risk Mitigation

A Privacy Impact Assessment (PIA) of the COIDS was conducted to identify possible privacy risks and develop strategies to mitigate these risks.

Concerning the safeguarding of personal information, the Security Assessment and Authorization (SA&A) of the COIDS identified that the following residual risks have been mitigated and accepted:

- Risk that malicious insiders will exploit potential weaknesses in the web front-end, application servers or database to compromise the environment: Security controls exist as evidenced by the Airport Parkway Data Centre (APDC) Certificate of Compliance issued in 2006. SSC Data Center Facilities has accepted the legacy data center risk of MEDIUM since the creation of SSC in 2011.
- Missing evidence of proper Protected B Zoning: SSC Operations provided documented evidence of proper zone segmentation to adequately meet the Protected B needs of the COIDS solution.
- Lack of a vulnerability assessment: Completed in November 2017 and is now conducted on a monthly basis. This resulted in the remediation of high risk vulnerabilities.
- Inadequate encryption protocols: Evidence provided that Communication Security Establishment (CSE) approved PB encryption is enabled on the web connection to mitigate the risk of hijacking allowing unauthorized users to access sensitive personal information stored in COIDS;

A Vulnerability Assessment has been completed to address some of the above noted risks. Currently, vulnerability scans are being conducted monthly to monitor the system. To note, the application will be accessible to SSC on the Government of Canada Network only and not accessible on the Internet.
