# Requirements - Issue #5: Invoice Module

## GitHub Issue
**Title**: Invoice Module
**Issue URL**: https://github.com/aravindmk1011/GreasyNutsIssues/issues/5

## Issue Description
Invoice module will have all the information like other modules. The customer invoice table alone 
will be in two languages — English and Arabic.

## Invoice Module Details

### Invoice_module_details.docx

INVOICE MODULE
Purpose
Provide a centralized invoicing and payment management system integrated with:
Jobs
Services
Parts
Insurance Claims
Customer Payments
Accounting Export
The invoice module should support:
draft invoice workflow
invoice approval workflow
customer invoice generation
payment tracking
insurance payment handling
outstanding collections
accounting exports
bilingual customer invoice generation (English + Arabic)
The module should act as operational financial layer for the garage management platform.
Component 1: Invoice Dashboard
MODULE SIDEBAR STRUCTURE
Invoice Dashboard
Invoice Overview
Pending Payments
Payment History
Credit Notes
Invoice Export
KPI CARD STRUCTURE
Revenue TodayPending PaymentsOverdue InvoicesDraft Invoices
PAYMENT ALERT TABLE
Severity
Alert Type
Message
Related Invoice
🔴
Overdue Invoice
Payment overdue by 7 days
INV-102
🟡
Pending Approval
Invoice awaiting approval
INV-203
🔴
Insurance Pending
Insurance payment delayed
INV-310
Revenue Trend Graph
UI Type
Line Chart
Track:
daily revenue
weekly revenue
payment trends
Component 2:  INVOICE OVERVIEW
Purpose
Provide operational visibility across all invoices.
The table should:
support filtering
support searching
provide quick actions
provide quick financial visibility
allow opening detailed invoice workspace
Entire row should be clickable.
Clicking row:→ Opens Invoice Detail Screen.
TOP BAR
Search Category
Filter
Start Date
End Date
Export
Notifications
User
SEARCH CATEGORY DROPDOWN
Invoice NumberCustomer NameJob IDVehicle PlatePayment StatusInvoice Status
FILTER DROPDOWN
DraftPending ApprovalApprovedPartially PaidPaidOverdueCancelled
INVOICE OVERVIEW TABLE
PAYER TYPE OPTIONS
CustomerInsuranceMixed
PAYMENT STATUS OPTIONS
PendingPartially PaidPaidOverdueCancelled
QUICK ACTIONS DROPDOWN
Approve InvoiceCancel InvoiceOpen Invoice Details
APPROVAL FLOW
Draft Invoice        ↓Manager Reviews        ↓Approve Invoice        ↓Invoice Locked        ↓Customer Invoice Generated        ↓PDF / Print / WhatsApp Enabled
Component 3: INVOICE DETAIL SCREEN
The Invoice Detail Screen should remain hidden until:
user clicks invoice rowOR
user selects “Open Invoice Details”
INVOICE HEADER
Invoice No
Invoice Date
Job ID
Invoice Status
Payment Status
CUSTOMER & VEHICLE DETAILS
Customer Name
Phone
Vehicle
Plate Number
Mileage
INSURANCE PAYMENT SUMMARY
Insurance Provider
Claim Number
Insurance Amount
Customer Deductible
Insurance Payment Status
INSURANCE PAYMENT STATUS OPTIONS
Pending ApprovalApprovedSubmittedPartially PaidPaidRejected
SERVICES & COST SUMMARY TABLE
Expand
Service Type
Labor Cost
Parts Cost
Additional Charges
Discount
VAT
Total
EXPANDED SERVICE VIEW
Expanded rows should appear when:
user clicks expand arrow
Expanded section should display:all parts used under the service.
EXPANDED SERVICE TABLE
Part Name
Quantity
Unit Price
VAT
Total
PAYMENT SUMMARY
Subtotal
VAT Total
Insurance Amount
Customer Amount
Grand Total
Paid Amount
Remaining Balance
INTERNAL & CUSTOMER NOTES
Internal Notes
Purpose:Internal finance/payment comments.
Not visible to customer.
Examples:
approval notes
insurance comments
payment follow-up notes
Customer Notes
Purpose:Visible on customer invoice.
Examples:
thank you message
next service reminder
delivery note
ACTION BAR
Invoice Language
Download PDF
Print Invoice
Send WhatsApp
INVOICE LANGUAGE DROPDOWN
EnglishEnglish + Arabic
PAYMENT STATUS LOGIC:
IMPORTANT PRINCIPLE:
Payment Status should NOT be manually selected.
Payment Status must be auto-calculated based on:
payment entries
remaining balance
due date
PAYMENT STATUS RULES
Payment Status
Rule / Condition
Auto or Manual
Trigger Source
Pending
Paid Amount = 0 AND Remaining Balance > 0
Auto
Invoice approved
Partially Paid
Paid Amount > 0 AND Remaining Balance > 0
Auto
Payment entry
Paid
Remaining Balance = 0
Auto
Payment entry
Overdue
Due Date Passed AND Remaining Balance > 0
Auto
System date check
Cancelled
Invoice manually cancelled by manager
Manual
Quick Actions → Cancel Invoice
PAYMENT STATUS UPDATE FLOW
Action
System Update
Invoice Approved
Payment Status = Pending
Payment Recorded
Paid Amount updated
Paid Amount Updated
Remaining Balance recalculated
Remaining Balance recalculated
Payment Status recalculated
Due Date Passed
Payment Status = Overdue
Invoice Cancelled
Payment Status = Cancelled
PAYMENT METHOD OPTIONS
CashCardBank TransferInsurance PaymentMixed
PAYMENT ENTRY FLOW
Manager Opens:Pending Payments        ↓Record Payment        ↓Payment Entry Form Opens        ↓Manager Enters:- Payment Amount- Payment Method- Transaction Reference        ↓System Updates:- Paid Amount- Remaining Balance- Payment Status- Payment History
PAYMENT ENTRY FORM
Invoice No
Payment Amount
Payment Method
Transaction Reference
Payment Date
Notes
Component 6: PENDING PAYMENTS
SUMMARY CARDS
Total OutstandingOverdue AmountInsurance Pending
PENDING PAYMENTS TABLE
Invoice No
Customer
Payer
Phone
Due Date
Aging Days
Grand Total
Paid Amount
Remaining Balance
QUICK ACTIONS DROPDOWN
Record PaymentSend ReminderOpen Invoice Details
Component 7:  PAYMENT HISTORY
PAYMENT HISTORY TABLE
Payment Date
Invoice No
Customer
Payment Method
Transaction Reference
Amount Paid
Recorded By
Component 8: CREDIT NOTES
Purpose
Handle:
invoice reversals
cancellations
adjustments
corrections
CREDIT NOTES TABLE
Credit Note No
Invoice No
Customer
Reason
Credit Amount
Created Date
Status
Component 9:  INVOICE EXPORT
Purpose
Provide export-ready financial data for:
accounting
VAT filing
collections
reconciliation
EXPORT OPTIONS
Approved InvoicesVAT ExportPending PaymentsPayment History
APPROVED INVOICES EXPORT TABLE
Invoice No
Invoice Date
Customer
Vehicle
Subtotal
VAT Amount
Grand Total
Payment Status
VAT EXPORT TABLE
Invoice No
Invoice Date
Taxable Amount
VAT %
VAT Amount
TRN
PENDING PAYMENTS EXPORT TABLE
Invoice No
Customer
Due Date
Grand Total
Paid Amount
Remaining Balance
Aging Days
PAYMENT HISTORY EXPORT TABLE
Invoice No
Payment Date
Payment Method
Transaction Reference
Amount Paid
EXPORT FLOW
Invoice Export        ↓Select Export Type        ↓Relevant Table Loads        ↓Review Data        ↓Export Excel / CSV / PDF
CUSTOMER INVOICE TEMPLATE (PDF)
Purpose
Generate final customer-facing invoice.
Supports:
PDF download
printing
WhatsApp sharing
bilingual English + Arabic
CUSTOMER INVOICE HEADER
Garage Name
Address
Phone
TRN
CUSTOMER INVOICE INFORMATION
Invoice No
Invoice Date
Job ID
Payment Status
CUSTOMER & VEHICLE DETAILS
Customer Name
Vehicle
Plate Number
Mileage
SERVICES TABLE
Service Type
Labor Cost
Parts Cost
VAT
Total
PARTS TABLE
Part Name
Quantity
Unit Price
Total
PAYMENT SUMMARY TABLE
Subtotal
VAT
Insurance Amount
Customer Amount
Grand Total
INSURANCE SECTION
Visible only if:Payer Type = Insurance OR Mixed
INSURANCE SUMMARY TABLE
Insurance Provider
Claim Number
Insurance Status
CUSTOMER NOTES SECTION
Examples:
thank you message
next service reminder
delivery note
BILINGUAL SUPPORT
Invoice Language Options:
EnglishEnglish + Arabic
Arabic labels should appear beside English labels.
IMPORTANT SYSTEM RULES
Invoice Locking
Once approved:
invoice becomes locked
edits require cancellation or credit note
Payment Status
Must always be auto-calculated.
Never manually selected.
Customer Invoice Generation
Generated only after:
Invoice Status = Approved
MODULE INTEGRATIONS
Module
Integration Purpose
Jobs
Service & job linkage
Inventory
Parts cost & usage
Suppliers
Parts procurement
Customers
Customer information
Dashboard
Revenue & alerts
Reports
Financial analytics
Insurance
Claim handling

---

### Invoice_operational_flow.docx

Invoice Operational Flow
INVOICE MODULE — OPERATIONAL FLOWS
1. STANDARD CUSTOMER PAYMENT FLOW
Create Job        ↓Job Execution Completed        ↓Manager Opens:Job Detail Screen        ↓Clicks:Generate Invoice        ↓System Creates:Draft Invoice        ↓Invoice Appears In:Invoice Overview        ↓Manager Reviews:- Services- Parts- VAT- Discounts        ↓Quick Action:Approve Invoice        ↓Invoice Locked        ↓Customer Invoice Generated        ↓PDF / Print / WhatsApp Enabled        ↓Invoice Appears In:Pending Payments        ↓Customer Makes Payment        ↓Manager Clicks:Record Payment        ↓Payment History Updated        ↓Payment Status Auto Updated        ↓Dashboard KPI Updated
2. INSURANCE CLAIM FLOW
Create Job        ↓Payment Type:Insurance / Mixed        ↓Insurance Details Entered:- Insurance Provider- Claim Number- Deductible        ↓Job Execution Completed        ↓Generate Invoice        ↓Draft Invoice Created        ↓Manager Reviews:- Insurance Amount- Customer Amount        ↓Approve Invoice        ↓Customer Invoice Generated        ↓Invoice Split:Insurance Portion+Customer Portion        ↓Customer Pays Deductible        ↓Insurance Payment Pending        ↓Pending Payments Module Tracks:- Insurance Pending- Remaining Balance        ↓Insurance Pays Garage        ↓Record Payment        ↓Payment Status Auto Updated
3. PAYMENT STATUS AUTO-CALCULATION FLOW
Invoice Approved        ↓Remaining Balance > 0        ↓Payment Status:Pending        ↓Payment Recorded        ↓System Updates:Paid AmountRemaining Balance        ↓IF:Remaining Balance > 0        ↓Payment Status:Partially Paid        ↓IF:Remaining Balance = 0        ↓Payment Status:Paid        ↓IF:Due Date PassedANDRemaining Balance > 0        ↓Payment Status:Overdue
4. PENDING PAYMENTS FLOW
Invoice Approved        ↓Invoice Added To:Pending Payments        ↓Owner Reviews:- Outstanding Amounts- Overdue Invoices- Insurance Pending        ↓Quick Actions:- Record Payment- Send Reminder- Open Invoice Details        ↓Payment Recorded        ↓Remaining Balance Recalculated        ↓IF:Remaining Balance = 0        ↓Invoice Removed From:Pending Payments
5. PAYMENT HISTORY FLOW
Record Payment        ↓Payment Entry Form Opens        ↓Manager Enters:- Payment Amount- Payment Method- Transaction Reference        ↓Save        ↓System Creates:Payment History Record        ↓Payment History Table Updated        ↓Audit Trail Maintained
6. CUSTOMER INVOICE GENERATION FLOW
Draft Invoice        ↓Manager Approves Invoice        ↓System Generates:Customer Invoice Template        ↓Language Selection:- English- English + Arabic        ↓Customer Invoice PDF Generated        ↓Actions Enabled:- Download PDF- Print- Send WhatsApp
7. QUICK ACTION APPROVAL FLOW
Invoice Overview Table        ↓Manager Reviews Summary        ↓Quick Actions ▼        ↓Approve Invoice        ↓Invoice Status:Approved        ↓Invoice Locked        ↓Customer Invoice Generated
8. INVOICE DETAIL SCREEN FLOW
Invoice Overview Table        ↓Manager Clicks Invoice Row        ↓Invoice Detail Screen Opens        ↓Manager Reviews:- Services- Parts- Insurance- VAT- Notes- Payment Summary        ↓Manager Performs Actions:- Download PDF- Print Invoice- Send WhatsApp
9. INVOICE EXPORT FLOW
Owner Opens:Invoice Export        ↓Select Export Type:- Approved Invoices- VAT Export- Pending Payments- Payment History        ↓Relevant Export Table Loads        ↓Owner Reviews Data        ↓Clicks:Export Excel / CSV / PDF        ↓Export File Generated
10. CREDIT NOTE FLOW
Approved Invoice Exists        ↓Issue Found:- Cancellation- Adjustment- Correction        ↓Manager Creates:Credit Note        ↓Credit Note Linked To:Original Invoice        ↓Outstanding Balance Recalculated        ↓Payment Status Updated
11. OVERDUE PAYMENT FLOW
Invoice Approved        ↓Due Date PassedANDRemaining Balance > 0        ↓Payment Status:Overdue        ↓Dashboard Alert Triggered        ↓Invoice Appears In:Pending Payments        ↓Manager Sends Reminder        ↓Customer Makes Payment        ↓Payment Status Updated
12. ACCOUNTING EXPORT FLOW
Month End        ↓Owner Opens:Invoice Export        ↓Selects:Approved Invoice Export        ↓System Loads:Approved Invoice Table        ↓Owner Reviews Data        ↓Export Excel / CSV        ↓File Sent To:External Accountant
13. MODULE INTEGRATION FLOW
Job Module        ↓Services + Parts Used        ↓Invoice Draft Generated        ↓Inventory Module:Parts Cost Pulled        ↓Customer Module:Customer Details Pulled        ↓Insurance Details Pulled        ↓Invoice Approval        ↓Pending Payments Updated        ↓Dashboard KPI Updated        ↓Reports Module Updated
INFORMATIONAL FLOW LEGEND
Symbol
Meaning
← PULLED FROM
Information pulled into Invoice Module
→ SENT TO
Information generated from Invoice Module and sent to another module
↔ SHARED
Bidirectional/shared information
1. INVOICE OVERVIEW TABLE — INFORMATION FLOW
Column
Auto / Manual
Information Flow
Source Module → Section
Sent To
Invoice No
Auto
← PULLED FROM
Invoice Module → Invoice Creation Engine
Pending Payments / Payment History / Reports
Customer
Auto
← PULLED FROM
Customer Module → Customer Profile
Customer Invoice PDF
Payer Type
Manual
← PULLED FROM
Jobs Module → Create Job → Payment Type
Pending Payments
Primary Service
Auto
← PULLED FROM
Jobs Module → Service Table
Reports Module
Payment Status
Auto
← PULLED FROM
Invoice Module → Payment Calculation Logic
Dashboard / Pending Payments
Grand Total
Auto
← PULLED FROM
Invoice Module → Cost Calculation Engine
Reports / Customer Invoice
Insurance Amount
Auto
← PULLED FROM
Jobs Module → Insurance Section
Pending Payments
Customer Amount
Auto
← PULLED FROM
Invoice Module → Invoice Calculation
Customer Invoice
Remaining Balance
Auto
← PULLED FROM
Invoice Module → Payment Calculation Logic
Pending Payments
Due Date
Manual
← PULLED FROM
Invoice Module → Invoice Approval Section
Pending Payments
Aging
Auto
← PULLED FROM
Invoice Module → Date Calculation Engine
Dashboard
Quick Actions
Manual Action
↔ SHARED
Invoice Module → Operational Workflow
Invoice Detail Screen
2. INVOICE HEADER — INFORMATION FLOW
Field
Auto / Manual
Information Flow
Source Module → Section
Sent To
Invoice No
Auto
← PULLED FROM
Invoice Creation Engine
Customer Invoice
Invoice Date
Auto
← PULLED FROM
System Timestamp
Reports
Job ID
Auto
← PULLED FROM
Jobs Module → Job Header
Reports
Invoice Status
Auto/Manual
↔ SHARED
Invoice Module → Approval Workflow
Dashboard
Payment Status
Auto
← PULLED FROM
Payment Calculation Engine
Pending Payments
3. CUSTOMER & VEHICLE DETAILS — INFORMATION FLOW
Field
Auto / Manual
Information Flow
Source Module → Section
Sent To
Customer Name
Auto
← PULLED FROM
Customer Module → Customer Profile
Customer Invoice
Phone
Auto
← PULLED FROM
Customer Module → Contact Details
Pending Payments
Vehicle
Auto
← PULLED FROM
Jobs Module → Vehicle Information
Customer Invoice
Plate Number
Auto
← PULLED FROM
Jobs Module → Vehicle Information
Customer Invoice
Mileage
Auto
← PULLED FROM
Jobs Module → Latest Mileage Entry
Service History
4. INSURANCE PAYMENT SUMMARY — INFORMATION FLOW
Field
Auto / Manual
Information Flow
Source Module → Section
Sent To
Insurance Provider
Manual
← PULLED FROM
Jobs Module → Insurance Details
Pending Payments
Claim Number
Manual
← PULLED FROM
Jobs Module → Insurance Details
Reports
Insurance Amount
Manual/Auto
← PULLED FROM
Invoice Calculation Engine
Pending Payments
Customer Deductible
Manual
← PULLED FROM
Jobs Module → Insurance Details
Customer Invoice
Insurance Payment Status
Auto
← PULLED FROM
Payment Calculation Logic
Dashboard
5. SERVICES & COST SUMMARY TABLE — INFORMATION FLOW
Column
Auto / Manual
Information Flow
Source Module → Section
Sent To
Service Type
Auto
← PULLED FROM
Jobs Module → Service Request Table
Customer Invoice
Labor Cost
Auto
← PULLED FROM
Service Master Module → Labor Pricing
Reports
Parts Cost
Auto
← PULLED FROM
Inventory Module → Parts Usage
Inventory Analytics
Additional Charges
Manual
← PULLED FROM
Invoice Module → Invoice Adjustment Section
Customer Invoice
Discount
Manual
← PULLED FROM
Invoice Approval Workflow
Customer Invoice
VAT
Auto
← PULLED FROM
System Settings → VAT Configuration
VAT Export
Total
Auto
← PULLED FROM
Invoice Calculation Engine
Customer Invoice
6. EXPANDED SERVICE VIEW (PARTS TABLE) — INFORMATION FLOW
Column
Auto / Manual
Information Flow
Source Module → Section
Sent To
Part Name
Auto
← PULLED FROM
Inventory Module → Parts Inventory
Customer Invoice
Quantity
Auto/Partial
← PULLED FROM
Job Execution → Parts Usage Section
Inventory Movement
Unit Price
Auto
← PULLED FROM
Inventory Module → Part Pricing
Reports
VAT
Auto
← PULLED FROM
VAT Configuration
VAT Export
Total
Auto
← PULLED FROM
Invoice Calculation Engine
Customer Invoice
7. PAYMENT SUMMARY — INFORMATION FLOW
Field
Auto / Manual
Information Flow
Source Module → Section
Sent To
Subtotal
Auto
← PULLED FROM
Invoice Calculation Engine
Customer Invoice
VAT Total
Auto
← PULLED FROM
VAT Calculation Engine
VAT Export
Insurance Amount
Auto
← PULLED FROM
Insurance Payment Section
Pending Payments
Customer Amount
Auto
← PULLED FROM
Invoice Calculation Engine
Customer Invoice
Grand Total
Auto
← PULLED FROM
Invoice Calculation Engine
Reports
Paid Amount
Auto
← PULLED FROM
Payment Entry Records
Dashboard
Remaining Balance
Auto
← PULLED FROM
Payment Calculation Logic
Pending Payments
8. PAYMENT ENTRY FORM — INFORMATION FLOW
Field
Auto / Manual
Information Flow
Source Module → Section
Sent To
Invoice No
Auto
← PULLED FROM
Invoice Overview Selection
Payment History
Payment Amount
Manual
← PULLED FROM
Payment Entry Form
Payment Calculation
Payment Method
Manual
← PULLED FROM
Payment Entry Form
Payment History
Transaction Reference
Manual
← PULLED FROM
Payment Entry Form
Audit Trail
Payment Date
Manual
← PULLED FROM
Payment Entry Form
Payment History
Notes
Manual
← PULLED FROM
Payment Entry Form
Internal Audit
9. PENDING PAYMENTS TABLE — INFORMATION FLOW
Column
Auto / Manual
Information Flow
Source Module → Section
Sent To
Invoice No
Auto
← PULLED FROM
Invoice Module → Approved Invoices
Collections
Customer
Auto
← PULLED FROM
Customer Module → Customer Profile
Reminders
Payer
Auto
← PULLED FROM
Jobs Module → Payment Type
Reports
Phone
Auto
← PULLED FROM
Customer Module → Contact Details
WhatsApp Reminder
Due Date
Manual
← PULLED FROM
Invoice Approval Section
Overdue Logic
Aging Days
Auto
← PULLED FROM
System Date Calculation
Dashboard
Grand Total
Auto
← PULLED FROM
Invoice Calculation Engine
Reports
Paid Amount
Auto
← PULLED FROM
Payment History Records
Dashboard
Remaining Balance
Auto
← PULLED FROM
Payment Calculation Logic
Collections
Payment Status
Auto
← PULLED FROM
Payment Status Engine
Dashboard
10. PAYMENT HISTORY TABLE — INFORMATION FLOW
Column
Auto / Manual
Information Flow
Source Module → Section
Sent To
Payment Date
Auto
← PULLED FROM
Payment Entry Form
Audit Reports
Invoice No
Auto
← PULLED FROM
Invoice Module
Accounting Export
Customer
Auto
← PULLED FROM
Customer Module
Reports
Payment Method
Auto
← PULLED FROM
Payment Entry Form
Accounting Export
Transaction Reference
Auto
← PULLED FROM
Payment Entry Form
Audit Trail
Amount Paid
Auto
← PULLED FROM
Payment Entry Form
Dashboard
Recorded By
Auto
← PULLED FROM
Logged-In User Session
Audit Trail
11. CREDIT NOTES TABLE — INFORMATION FLOW
Column
Auto / Manual
Information Flow
Source Module → Section
Sent To
Credit Note No
Auto
← PULLED FROM
Credit Note Engine
Reports
Invoice No
Auto
← PULLED FROM
Invoice Module
Accounting Export
Customer
Auto
← PULLED FROM
Customer Module
Audit Reports
Reason
Manual
← PULLED FROM
Credit Note Creation Form
Audit Trail
Credit Amount
Manual
← PULLED FROM
Credit Note Creation Form
Financial Adjustment
Created Date
Auto
← PULLED FROM
System Timestamp
Audit Reports
Status
Auto/Manual
↔ SHARED
Credit Note Workflow
Dashboard
12. CUSTOMER INVOICE TEMPLATE — INFORMATION FLOW
Section
Auto / Manual
Information Flow
Source Module → Section
Sent To
Garage Header
Auto
← PULLED FROM
System Settings → Company Information
Customer PDF
Invoice Information
Auto
← PULLED FROM
Invoice Header
Customer PDF
Customer Details
Auto
← PULLED FROM
Customer Module
Customer PDF
Vehicle Details
Auto
← PULLED FROM
Jobs Module → Vehicle Information
Customer PDF
Services Table
Auto
← PULLED FROM
Services & Cost Summary
Customer PDF
Parts Table
Auto
← PULLED FROM
Inventory → Parts Usage
Customer PDF
Payment Summary
Auto
← PULLED FROM
Payment Summary Section
Customer PDF
Insurance Section
Auto
← PULLED FROM
Insurance Details Section
Customer PDF
Customer Notes
Manual
← PULLED FROM
Customer Notes Entry
Customer PDF
13. INFORMATION SENT FROM INVOICE MODULE TO OTHER MODULES
Information Generated In Invoice Module
→ SENT TO MODULE
Destination Section
Purpose
Approved Revenue
Dashboard Module
KPI Cards
Revenue tracking
Outstanding Balances
Dashboard Module
Alerts Panel
Financial alerts
VAT Totals
Reports Module
VAT Reports
Tax reporting
Payment Transactions
Reports Module
Financial Reports
Audit/reconciliation
Parts Cost Usage
Inventory Module
Inventory Analytics
Cost analysis
Insurance Receivables
Pending Payments
Collections Tracking
Insurance follow-up
Customer Invoice PDF
Customer Communication
WhatsApp / Email
Customer billing
Paid Amount Updates
Pending Payments
Collections Table
Balance recalculation
Invoice Status
Dashboard Module
Invoice Alerts
Operational visibility

---

