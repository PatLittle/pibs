---
title: "Receiver General Buy Button upgrade: Privacy impact assessment summary"
institution_id: "ati-schedule-i-department-of-public-works-and-government-services"
language: "en"
source_url: "https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2009-2010/receiver-general-buy-button-upgrade-summary.html"
retrieved_at_utc: "2026-11-12T01:42:17.657514+00:00"
http_status: 200
source_sha256: "722256c0bddfb572758fa9373dca3cda8b36e97a3de4932e4c7d408e0260ba2a"
content_kind: "page"
---

# Receiver General Buy Button upgrade: Privacy impact assessment summary

## On this page

- [Introduction and background](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2009-2010/receiver-general-buy-button-upgrade-summary.html#a1)
- [Personal information collected by the existing Receiver General Buy Button service](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2009-2010/receiver-general-buy-button-upgrade-summary.html#a2)
- [New personal information collected by the upgrade Receiver General Buy Button service](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2009-2010/receiver-general-buy-button-upgrade-summary.html#a3)
- [Privacy risks](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2009-2010/receiver-general-buy-button-upgrade-summary.html#a4)
- [Conclusion](https://www.canada.ca/en/public-services-procurement/corporate/transparency/access-information-privacy/consulting-privacy-impact-assessments/2009-2010/receiver-general-buy-button-upgrade-summary.html#a5)

## Introduction and background

The Receiver General Buy Button service modernization will continue to enable buy button clients to use the buy button for credit card and now also Interac as payment processing methods. The payment information is processed electronically using the buy button service from buy button clients' websites (also known as storefronts) that accept electronic payments.

Buy button clients will continue to use the buy button service as a means to process payments from individuals of the general public. The buy button provides the necessary tools to allow buy button clients to manage online, mail orders and in-person payment for goods or services, through the provision of authentication and administration processes. The use of these processes facilitates secure and private exchange of customer payment data with payment processing service providers on behalf of buy button clients.

The user community for the buy button service consists of:

- buy button clients including any government department, agency or other levels of government who want to use the buy button service to accept payments from their web storefront for goods or services procured by customers
- customers wanting to make payments to buy button client for goods or services

## Personal information collected by the existing Receiver General Buy Button service

The different clusters of personal information collected or used during the various buy button business processes are as follows:

- **Credit card number:** Identifies the credit card number required to process the customer's request to pay for the goods or services using their credit card
- **Expiry date:** Identifies the credit card expiration date to confirm if the credit card is active or expired
- **Address:** Identifies the address of the cardholder for billing or address verification purposes
- **Reason codes:** Reason codes collected by the buy button are personal information since they are linked to the credit card number or cardholder name. The reason codes are contained in the buy button relational database repository, and are accessed by the application components to verify the validity of payment processing details presented by the buy button clients' customers, but does not contain any information that identifies an individual. The reason codes are displayed in plain text

The application also collects and retains transaction data from the selling department that is required for processing the transaction. This information includes the selling department's identification (ID), transaction type, departmental reference number, transaction amount and the language last used by the customer on the department's website (so that the buy button web pages can be presented in the same language for consistency). Transaction data collected from the department is assigned a buy button transaction ID and the data collected from the customer is appended to that record.

## New personal information collected by the upgrade Receiver General Buy Button service

The new personal information collected or used during the various upgraded buy button business processes is as follows:

- **Name:** Identifies the name of the credit card holder buying the service/product from the buy button client storefront
- **Address:** Email or physical address of the cardholder as required for transaction receipt purposes

Other information elements pertaining to the customers' online transactions are also collected or used, such as customer session logs, content of temporary cookies and signature verification logs. The architecture design specifications, however, do not permit these information elements to identify individuals or to be linked to individuals.

The customer is provided with the opportunity to review the buy button privacy statement on the payment page where they are required to submit personal information. The privacy statement describes the reason for collection, the specific use, the retention period, disposal procedures and personal information bank (PIB) where the personal information is stored.

The buy button administrative web interface is used to perform the following:

- initiate credit card sales or authorization (possibly Interac sales in the future)
- perform refund or void of transactions previously completed by a merchant
- automate end-of-day processing of funds settlement and deposit
- securely store transaction data
- support execution of ad hoc queries and reports as well as profile maintenance-related activities

## Privacy risks

Privacy risks and potential risk mitigation measures have been identified in the privacy impact assessment report. These risks are summarized below.

- Ensuring that personal information is maintained in a secure and robust infrastructure and physical location.
- Ensuring that privacy and security obligations on data are addressed in third-party agreements (terms of engagement and set-up forms) between Public Works and Government Services Canada, other government departments and the Receiver General Buy Button service vendor via interface information exchange or supporting the related services
- Publishing a harmonized retention and disposal procedures that meet government requirements, Personal Information Protection and Electronic Documents Act and Payment Card Industry Data Security Standard (PCI DSS) including the physical safeguards of that data until disposal
- Documenting the changes and updating the personal information bank (PIB) to reflect the updated buy button service data collection requirements
- Developing a harmonized privacy notice that reflects the Privacy Act and the Personal Information Protection and Electronic Documents Act requirements adequately

## Conclusion

A number of privacy risks have been identified with the Receiver General Buy Button upgrade service and are evaluated at "low" in severity with a plan to mitigate these risks within an acceptable timeframe.

It is important to note that the buy button basic business model has not changed only the service provider and the collection of two additional pieces of personal information which will ensure accurate and secure payments are processed. The introduction of a payment gateway with multiple options within the buy button may raise privacy concerns. In that context, customers should be reminded that privacy protection was and remains a pivotal factor for the buy button's choice of subcontracting to a Payment Card Industry Data Security Standard (PCI DSS) Level 1 certified processing vendor. Customers who wish to further protect their privacy can also elect to procure buy button client services using different payment options such as credit card and Interac, thereby rendering the credit card number a payment processing specific identifier, and not a common identifier.
