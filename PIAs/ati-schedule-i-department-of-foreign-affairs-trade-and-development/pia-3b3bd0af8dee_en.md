---
title: "Integrated Management System (IMS) – Privacy Impact Assessment: Global Affairs Canada"
institution_id: "ati-schedule-i-department-of-foreign-affairs-trade-and-development"
language: "en"
source_url: "https://international.canada.ca/en/global-affairs/corporate/transparency/atip/impact-assessment/ims"
retrieved_at_utc: "2026-11-12T05:48:54.332001+00:00"
http_status: 200
source_sha256: "5a2ca4340da25e286a43cfaefb4b5d410810ecb8c0facbe77207f10ffbcbc8c8"
content_kind: "page"
---

# Integrated Management System (IMS) – Privacy Impact Assessment: Global Affairs Canada

## Executive summary

The Integrated Management System (IMS) is the departmental Enterprise Resource Planning (ERP) application since 1998. It is used for accounting, which include posting pay summary transactions, controlling, budgeting, inventory management, procurement and asset accounting.All financial and material transactions of the department are reflected in IMS.

The system is owned, configured and supported by the Corporate Financial Systems Division (SMSF) and the technical management is under the authority of the Corporate Enterprise Solutions Division.

IMS is classified as a critical application to support program activities for the processing of accounts payable and fund transfers and is therefore subject to Management of Information Technology Security (MITS) compliance, which implies a Preliminary Privacy Impact Assessment (PPIA). Furthermore, since the inception of the Privacy Impact Assessment Policy in May 2002, a PPIA had not been conducted and it was now paramount to complete it to fulfill both MITS and PIA policy requirements.

The DFAIT’s corporate system architecture is complex and includes interfaces between IMS, the Human Resources Management System (HRMS), the Salary Management System (SMS), and Business Intelligence (BI–Cognos). There are also interfaces with central agencies, other internal applications and Other Government Departments (OGDs).

The scope of the PPIA included IMS modules being used in the production environment as of February 2009. However, ALL IMS inbound and outbound interfaces with other applications have been excluded. Consequently, the scope of the PPIA included the following IMS modules:

**FI:** The FI (Financial Accounting) module supports the primary accounting and financial requirements of the department. It is within this module that Financial Managers as well as other Managers from both missions and headquarters can review the financial position of the department in real time. The information is timely and properly supports decision making and strategic planning. The FI (Financial Accounting) Module is integrated with other IMS Modules such as MM (Materials Management), PP (Production Planning), PM (Plant Maintenance), and PS (Project Systems).

**FI–AA:** The Asset Accounting (AA) module is used for managing and monitoring fixed assets. In the Financial Accounting module, it serves as a subsidiary ledger to the General Ledger, providing detailed information on transactions involving fixed assets.

AA is used by specialized users in the Physical Resources Bureau and Information Management and Technology offices at both headquarters and missions. AA encompasses the entire asset lifecycle from acquisition or the commencement of construction through its disposal. This module calculates and accrues amortization of the asset in accordance with the department’s amortization schedules.

**MM:** The Material Management module supports the entire procure–to–pay lifecycle. Although the use of MM has been mandatory at headquarters, it is just in the process of being rolled–out to missions. It includes the following functionality:

## Purchasing

The acquisition of goods and/or services is recorded in IMS with the use of purchase requisitions (PR) and/or purchase orders (PO). PRs and POs create commitments in the FM module thus reducing the applicable funds reservation or the free balance. When goods are received, users

can perform the optional good receipt transaction. To optimize the purchasing processes, request for quotation/proposal and recording of long–term purchase agreements can also be performed in the MM module.

### Logistics Invoice Verification (LIV)

The invoice verification is another component of the MM module. Posted with reference to a purchase order, invoice verification checks invoices for content, price and calculation accuracy. When an invoice is posted, the system creates an open item in the vendor account which is cleared by Financial Accounting on payment.

### Inventory Management (IM)

This component of the MM module is used to manage the quantity and value of stock items. In addition to providing the functions to manage day to day receipts and issues of stock items, functions such as material requirement planning (MRP) are available to generate procurement proposals and physical inventory used for stock verification.

**CO:** The CO (Controlling) module provides additional reporting flexibility at a cost centre level to meet additional business requirements. The additional level of granularity supports the control function and helps managers understanding program costs at both headquarter and mission levels.

For instance, the managers have the ability to create organizational units at a lower level than the fund center – i.e. Cost Centre to plan, record, report and monitor financial transactions. It also offers the use of Internal Orders (I/O) to track financial transactions in a logical grouping for reporting and settlement purposes.

Currently, cost centers and internal order numbers are used.

**PM:** The Plant Maintenance (PM) module allows the user to manage pieces of equipment independently. A piece of equipment is an individual object. Each piece of equipment is managed independently in the system, so that you can:

- Manage individual data from a maintenance perspective
- Perform individual maintenance tasks
- Keep a record of the maintenance tasks performed
- Collect and evaluate data over a long period of time

The equipment and functional location functionalities of PM are currently used at DFAIT.

Pieces of equipment can be installed and dismantled at functional locations. A functional location represents a system area at which pieces of equipment may be installed, dismantled or where a maintenance task may be performed. The usage times for a piece of equipment at a functional location are documented over the course of time. Currently, Procurement, Material Management and Logistics uses the PM module to track office furniture and equipment over its useful life; Visual Art Collection uses it to track hospitality items and art; Information Management and Technology maintains its IT inventory in ITAMS which is the linking of the Plant Maintenance module with Remedy software from acquisition through disposal.

**SD:** The Sales Distribution (SD) module is used by Passport Canada only. SD allows the users to execute different business transactions based on sales documents defined in the system. Passport uses it for sales orders. Entries in SD are generated through an interface with IRIS (not an IMS module). There is an MOU in place between DFAIT and Passport.

**SPL:** The Special Purpose Ledger (SPL) module allows the user to define ledgers for reporting purposes. The user–defined ledgers can be used as general ledgers or subsidiary ledgers with various account assignment objects. Account assignment objects can either be SAP dimensions from various applications (such as account, cost center, business area, and profit center) or customer–defined dimensions (such as region).

The SPL enables the user to report at various levels using the values from the various application components. The functions available in the SPL enable you to collect and combine information, create and modify totals, and distribute actual and plan values. The values are transferred to the SPL from other SAP modules and external systems.

The personal information contained in IMS is limited and includes the vendor and customer name, business number, home or business address, bank account numbers and other related information for processing transactions. The information is collected directly from them or through contractual agreements. An employee can be a vendor or a supplier for the processing of payments or recoveries. In all instances, consent to the collection, use, disclosure and disposal of their personal information is implicit in contractual arrangements when doing business with the department. For employees, it is implicit when submitting travel claims.

DFAIT is also registered against TBS Revised Standard Classes of Records PRN 914 (Financial Management), PRN 912 (Procurement and Contracting), PRN 934 (Travel) and TBS Standard Personal Information Banks PSU 912 (Professional Services Contracts) and PSU 909 (Travel), which are also listed in Treasury Board Secretariat Info Source.

There are approximately a total of 1,650 IMS users at headquarter and in missions abroad. However, only 180 users can create and maintain vendor and customer master data. Access to the system is granted on a need to know basis depending on the employee’s job duties. IMS access is controlled and restricted via IMS roles, user accounts, strong password protection, ongoing monitoring, audit trails, and disclosure of access reports to management. Also, a Threat and Risk Assessment completed in December 2006 has not raised security issues within IMS.

Full system backups and database backups are conducted daily, and the critical database tapes are kept on site at the same location as the servers in a fire–proof vault.

The current departmental retention schedule for financial and administration information is seven years. IMS contains both master data for which there is a continuing use and enduring data (transactional) that is currently available since the implementation of IMS in 1998. The rationale for keeping data beyond the departmental retention period of seven years is that there is no archiving solution readily available in the Government of Canada SAP footprint. The IMS strategy is to follow the footprint and archive the data once the functionality becomes available to departments. At this point, although archiving is on the list of items to address by the SAP Cluster, its availability date remains unknown.

Individuals to whom the information pertains have the right to protection of and access to their personal information under the Privacy Act subject to certain exceptions and exemptions.

There is no plan at this point to conduct a full PIA. The PPIA was conducted primarily to comply with MITS and TBS PIA Policy requirements. Furthermore, the findings and observations resulting from the completion of the PPIA concluded that the personal information contained within IMS is considered low risk and that there is no privacy issue to address or justify the need for a comprehensive PIA.

## Privacy Risks

The following privacy risks were identified in the development of the PPIA and are considered low level:

### Collection, use and accuracy of personal information

The risk to collect and use inaccurate personal information is low as the personal information is collected directly from the vendor/customer and employees. Ongoing updates/maintenance to vendor and customer master records based on contracts, invoices and vendor/customer/employee feedback helps mitigate this risk.

A vendor or a customer can be a DFAIT employee. To ensure banking information, address and name are accurate, a void cheque is provided to verify accuracy.

### Inappropriate disclosure of personal information

The risk to inappropriately disclose personal information is low. Controlling and restricting user access via user accounts, strong password protection, ongoing monitoring and disclosure of access reports to management is the mitigation strategy for this risk. Also, IMS has audit trails to ensure that changes made by users to master data records or transactions are properly tracked.
