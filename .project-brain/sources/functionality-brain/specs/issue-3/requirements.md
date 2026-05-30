# Requirements - Issue #3

**Title**: EPIC: Dashboard Module Rev2

**Status**: open
**Created**: 2026-05-18 18:16:07+00:00
**Updated**: 2026-05-24 06:09:20+00:00

## Description

EPIC: Dashboard Module
**Purpose**

Provide a centralized real-time operational overview of the garage business, including workflow visibility, financial tracking, operational alerts, and supply chain monitoring.

The dashboard should allow garage owners and managers to quickly understand:

- Current operational status
- Delayed or blocked jobs
- Revenue and payment visibility
- Supplier and inventory issues
- Business performance indicators

---------------------------------------------------------
| Sidebar | Top Bar                                     |
|         ---------------------------------------------|
|         | KPI Cards                                  |
|         | Alerts                                     |
|         | Jobs Snapshot        | Revenue Graph        |
|         | Supply Issues                               |
---------------------------------------------------------


**Component 1 — Sidebar Navigation**
Purpose:
Provide global navigation across all platform modules.
Sidebar Modules

1. Dashboard
2. Jobs
3. Customers
4. Parts
5. Invoices
6. Suppliers
7. Staff
8. Reports
9. Settings

Functional Requirements

- Highlight active module
- Allow click navigation
- Support icon-based navigation (optional future enhancement)

-------------------------------------------------------------------------------------------------
**Component 2 — Top Bar**
Purpose
Provide quick access to search, notifications, and user profile information.
Subcomponents

**Search Bar**
Fields
1. search_query (string)

Search Scope

1. job_id
2. customer_name
3. vehicle_plate

**Notifications Icon**
Notification Types

1. job_blocked
2. supplier_delay
3. low_stock
4. unpaid_invoice

Notification Object

1. Fields
2. id
3. type
4. message
5. severity
6. timestamp
7. related_entity_id

Notifications Example:
🔴 PO101 delayed (Supplier issue)
🔴 Job J103 blocked (No stock)
🟡 Supplier payment pending (€230)

User Profile

1. Fields
2. user_name
3. role

Example
John (Owner)
Logout

---------------------------------------------------------

Component 3 — KPI Cards
Purpose
Display high-level operational and financial metrics.

1) Jobs Today
jobs_today (int)

Definition: Count of jobs created today

2) Pending Jobs
pending_jobs (int)

Definition:status != completed

3) Revenue Today
revenue_today (float)

Definition: Sum of paid invoices for current day

4) Pending Payments
pending_payments (float)

Definition:Sum of unpaid invoice balances

KPI Example:
🟦 Jobs Today: 5
🟨 Pending Jobs: 3
🟩 Revenue Today: €210
🟥 Pending Payments: €530

--------------------------------------------------------------

**Component 4 — Alerts Panel**
Purpose
Highlight operational issues requiring immediate attention.

Alert Fields
1. alert_id
2. type
3. message
4. severity
5. related_entity_id

Alert Types
1. job_blocked
2. supplier_delay
3. low_stock
4. unpaid_invoice
5. delayed_job

Alert Example

🔴 Job J103 blocked (No stock)
🔴 PO101 delayed (Supplier)
🟡 3 unpaid invoices
🟡 Low stock: Brake pads

----------------------------------------------------------------------------

**Component 5 — Jobs Snapshot**
Purpose
Provide quick visibility into active jobs, job progress, and delayed work.

Job Snapshot Fields

1. job_id
2. vehicle
3. issue_type
4. status
5. start_date
6. due_date
7. days_elapsed (derived)
8. delivery_status (derived)
9. Reason for delay

Issue Type Examples

- Brake Pad Change
- Oil Service
- Full Service
- Engine Repair
- AC Service
- Battery Replacement

Example:
Vehicle          | Issue              | Status              | Days | Delivery        | Delay Reason
Toyota Corolla   | Brake Pad Change   | 🟨 In Progress      | 1    | 🟨 On Track      | —
BMW X5           | Oil Service        | 🟩 Completed        | 0    | 🟩 Completed     | —
Audi A4          | Engine Repair      | 🟥 Waiting Parts    | 2    | 🟥 Delayed       | Brake pads unavailable
Honda Civic      | AC Service         | 🟨 In Progress      | 1    | 🟨 On Track      | —
Ford Focus       | Battery Change     | 🟩 Completed        | 0    | 🟩 Completed     | —

-------------------------------------------------------------------------------------------------------------------------------------


**Component 6 — Revenue Graph**
Purpose
Display revenue trends for operational visibility.

Data Fields
1. date
2. revenue_amount
 UI Type
1. Line chart
2. Last 7 days view

Revenue Graph Example:
Day 1 → €200
Day 2 → €350
Day 3 → €300
Day 4 → €450
Day 5 → €210

-------------------------------------------------------------------------------------------------------------------
**Component 7 — Supply Issues**
Purpose
Display supplier-related operational blockers and delayed purchase orders affecting jobs.

Fields
1. po_id
2. supplier_name
3. delay_status
4. affected_jobs_count

Supply Issue Example
🔴 PO101 delayed (AutoParts Ltd)
→ 1 job affected
----------------------------------------------------------------------------------------------------------------------------

Just notes not any modules:

User Actions & Navigation

Functional Requirements:
1)KPI Cards
Clicking KPI should navigate to filtered related data
Example:
Pending Jobs KPI → Open Jobs module with pending jobs filter

2)Alerts
Clicking alert should navigate to related issue
Examples:
Supplier delay alert → Open Suppliers module
Job blocked alert → Open Job Detail
Jobs Snapshot
Clicking job should open Job Detail screen

Data Source mapping:

Dashboard Section-> Source Module
1) KP1 cards->Jobs , Invoices
2) Alerts- Job, Part, Suppliers, Invoices
3) Jobs snapshort- Jobs
4) Revenue Graph- Invoices
5) Supply Issues - Suppliers
6) Low Stock Alerts- Parts
7) Delayed Jobs- Jobs

Refresh Behavior
Requirements
Dashboard auto-refresh every 60 seconds
Manual refresh option available

Empty States
1)No Jobs
 No active jobs today
2)No Alerts
 No operational alerts
3)No Revenue Data
 No revenue data available

Mobile Responsive UX Requirements:

1. Responsive mobile layout
2. Touch-friendly buttons
3. Mobile-first dashboard structure
4. Vertical stacking for smaller screens



## Discussion

### Comment by Shankari22 (2026-05-24 06:09:20+00:00)

Look of the Dashboard main screen:


┌────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR                    │ TOP BAR                                                                                                                    │
│                            ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🏠 Dashboard               │ Search: [ BMW X5 ]            🔔 5 Alerts                     John (Owner) ▼                                             │
│ 📋 Jobs                    └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
│ 👥 Customers                                                                                                                                      │
│ 🧩 Parts                                                                                                                                          │
│ 🧾 Invoices                                                                                                                                       │
│ 🚚 Suppliers                                                                                                                                      │
│ 👨‍🔧 Staff                                                                                                                                         │
│ 📊 Reports                                                                                                                                         │
│ ⚙️ Settings                                                                                                                                       │
│                                                                                                                                                    │
│                                                                                             ┌──────────────────────────────────────────────────────┐ │
│                                                                                             │ KPI CARDS                                            │ │
│                                                                                             ├──────────────────────────────────────────────────────┤ │
│                                                                                             │ 🟦 Jobs Today: 12                                    │ │
│                                                                                             │ 🟨 Pending Jobs: 5                                   │ │
│                                                                                             │ 🟩 Revenue Today: €2,450                             │ │
│                                                                                             │ 🟥 Pending Payments: €1,120                          │ │
│                                                                                             └──────────────────────────────────────────────────────┘ │
│                                                                                                                                                    │
│                                                                                             ┌──────────────────────────────────────────────────────┐ │
│                                                                                             │ ALERTS PANEL                                         │ │
│                                                                                             ├──────────────────────────────────────────────────────┤ │
│                                                                                             │ 🔴 Job J203 blocked (Brake pads unavailable)         │ │
│                                                                                             │ 🔴 Supplier PO101 delayed                            │ │
│                                                                                             │ 🟡 Low stock: Engine Oil                             │ │
│                                                                                             │ 🟡 4 unpaid invoices                                 │ │
│                                                                                             └──────────────────────────────────────────────────────┘ │
│                                                                                                                                                    │
│                                                                                             ┌──────────────────────────────────────────────────────┐ │
│                                                                                             │ JOBS SNAPSHOT                                        │ │
│                                                                                             ├──────────────────────────────────────────────────────┤ │
│                                                                                             │ BMW X5 | Engine Repair | Delayed                     │ │
│                                                                                             │ Audi A4 | Oil Service | In Progress                  │ │
│                                                                                             │ Toyota Corolla | Brake Service | Ready               │ │
│                                                                                             │ Honda Civic | AC Repair | Waiting Parts              │ │
│                                                                                             └──────────────────────────────────────────────────────┘ │
│                                                                                                                                                    │
│                                                                                             ┌──────────────────────────────────────────────────────┐ │
│                                                                                             │ REVENUE GRAPH                                        │ │
│                                                                                             ├──────────────────────────────────────────────────────┤ │
│                                                                                             │ 7-Day Revenue Trend Line Chart                       │ │
│                                                                                             └──────────────────────────────────────────────────────┘ │
│                                                                                                                                                    │
│                                                                                             ┌──────────────────────────────────────────────────────┐ │
│                                                                                             │ SUPPLY ISSUES                                        │ │
│                                                                                             ├──────────────────────────────────────────────────────┤ │
│                                                                                             │ PO101 | Bosch | 2 Jobs Affected                      │ │
│                                                                                             │ PO203 | AutoParts Ltd | 1 Job Affected               │ │
│                                                                                             └──────────────────────────────────────────────────────┘ │
└────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

