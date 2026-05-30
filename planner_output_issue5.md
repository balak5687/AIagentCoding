# Planner Output - Issue #5

## Metadata

- **agent**: planner
- **status**: complete
- **confidence**: 85

## Execution Plan

# Execution Plan

## Task Breakdown

### Task 1: Replace Invoice Models
- **ID**: task_1
- **Description**: Replace `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/invoice.py` with the full-featured model hierarchy (enums: InvoiceStatus, PaymentStatus, PayerType, PaymentMethod, InsurancePaymentStatus, CreditNoteStatus; models: ServiceLineItem, PartLineItem, InsuranceDetails, InvoiceCreate, Invoice, InvoiceUpdate, PaymentEntry, PaymentEntryCreate, CreditNote, CreditNoteCreate). Use `work_order_id` internally (not `job_id`) per architect warning #1. Update `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/__init__.py` to export new classes and remove old ones (PaymentStatus.UNPAID/PARTIAL/PAID → new enum values).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/invoice.py` (replace)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/__init__.py` (update exports)
- **Dependencies**: []
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: add_database_model.yaml
- **Approach**: deterministic

### Task 2: Update DynamoDB Table Definitions
- **ID**: task_2
- **Description**: Update `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/init_db.py` to modify the existing `invoices` table definition (5 GSIs: customer_id-index, work_order_id-index, invoice_status-index, payment_status-index, invoice_number-index) and add new `payments` table (3 GSIs: invoice_id-index, payment_date_partition-index, recorded_by-index) and `credit_notes` table (3 GSIs: invoice_id-index, customer_id-index, status-index). Also add a `counters` table (single PK: `counter_id`) for atomic invoice/credit-note number generation.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/init_db.py` (update)
- **Dependencies**: []
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 3: Create Invoice Repository
- **ID**: task_3
- **Description**: Create `InvoiceRepository` extending `BaseRepository`. Table: `invoices`, PK: `invoice_id`. Methods: `get_by_customer`, `get_by_work_order` (maps to job_id in API), `get_by_status`, `get_by_payment_status`, `get_by_invoice_number`, `get_pending_payments`, `get_overdue_invoices`, `get_draft_invoices`, `get_invoices_by_date_range`. Follow existing repository patterns (e.g., WorkOrderRepository).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/invoice_repository.py` (create)
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 4: Create Payment Repository
- **ID**: task_4
- **Description**: Create `PaymentRepository` extending `BaseRepository`. Table: `payments`, PK: `payment_id`. Methods: `get_by_invoice`, `get_by_date_range` (using payment_date_partition GSI), `get_by_recorder`. Follow same patterns as Task 3.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/payment_repository.py` (create)
- **Dependencies**: [task_1]
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with task_3)
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 5: Create Credit Note Repository
- **ID**: task_5
- **Description**: Create `CreditNoteRepository` extending `BaseRepository`. Table: `credit_notes`, PK: `credit_note_id`. Methods: `get_by_invoice`, `get_by_customer`, `get_by_status`. Follow same patterns as Task 3/4.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/credit_note_repository.py` (create)
- **Dependencies**: [task_1]
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with task_3, task_4)
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 6: Create Invoice Service
- **ID**: task_6
- **Description**: Create `InvoiceService` with core business logic. Key methods: `generate_invoice_from_job` (pulls work order + customer + vehicle data, builds service line items), `get_invoice`, `list_invoices` (with lazy overdue check per architect approval), `approve_invoice` (locks invoice, sets approved_at/approved_by), `cancel_invoice`, `record_payment` (creates PaymentEntry, updates invoice paid_amount/remaining_balance, recalculates payment_status), `get_pending_payments`, `get_payment_history`, `get_dashboard_data` (KPIs), `create_credit_note`, `export_invoices`, `_recalculate_payment_status` (auto-calculation), `_generate_invoice_number` (atomic counter via DynamoDB conditional write on counters table, item PK `COUNTER#invoice`), `_generate_credit_note_number` (same pattern, `COUNTER#credit_note`). Dependencies: InvoiceRepository, PaymentRepository, CreditNoteRepository, WorkOrderRepository, CustomerRepository, VehicleRepository, InventoryRepository. Use `work_order_id` internally, expose as `job_id` in API responses.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/invoice_service.py` (create)
- **Dependencies**: [task_3, task_4, task_5]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 7: Create Invoice Routes
- **ID**: task_7
- **Description**: Create `invoice_bp` Blueprint with all REST endpoints per design. Map `job_id` in request/response to `work_order_id` internally. Endpoints: GET `/api/invoices/dashboard`, GET `/api/invoices`, GET `/api/invoices/<id>`, POST `/api/invoices`, PUT `/api/invoices/<id>`, POST `/api/invoices/<id>/approve`, POST `/api/invoices/<id>/cancel`, POST `/api/invoices/<id>/payments`, GET `/api/invoices/pending-payments`, GET `/api/invoices/payment-history`, GET `/api/invoices/<id>/payments`, POST `/api/invoices/credit-notes`, GET `/api/invoices/credit-notes`, GET `/api/invoices/export`. Use `require_auth` decorator, response helpers. Register blueprint in `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/invoices.py` (create)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py` (update: register invoice_bp)
- **Dependencies**: [task_6]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 8: Update Dashboard Service
- **ID**: task_8
- **Description**: Update `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py` to use new lowercase enum values consistently (`'paid'` not `'PAID'`, `'pending'` not `'UNPAID'`). Per architect warning #3.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py` (update)
- **Dependencies**: [task_1]
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with task_3-5)
- **Playbook**: null
- **Approach**: cognitive

### Task 9: Create React Types
- **ID**: task_9
- **Description**: Create TypeScript type definitions for the invoice module: InvoiceStatus, PaymentStatus, PayerType, PaymentMethod, InsurancePaymentStatus, CreditNoteStatus, ExportType type unions; ServiceLineItem, PartLineItem, InsuranceDetails, Invoice, InvoiceCreate, InvoiceUpdate, PaymentEntry, PaymentPayload, CreditNote, CreditNotePayload, InvoiceDashboard, KPICard, PaymentAlert, RevenueTrendPoint, PaymentStatusSummary, InvoiceFilters, PaginationParams, PaymentHistoryParams, CreditNoteParams, ExportParams interfaces.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/invoice.ts` (create)
- **Dependencies**: []
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 10: Create React Invoice Service
- **ID**: task_10
- **Description**: Create API service layer with all invoice endpoints. Import `api` from `@/services/api`. Methods match the API contract from Component 8 of the design. Note: use `job_id` in the API layer (backend handles the mapping to `work_order_id`).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/invoiceService.ts` (create)
- **Dependencies**: [task_9]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 11: Create React Invoice Hooks
- **ID**: task_11
- **Description**: Create TanStack Query hooks: queries (`useInvoiceDashboard`, `useInvoices`, `useInvoice`, `usePendingPayments`, `usePaymentHistory`, `useCreditNotes`, `useInvoicePayments`) with `refetchInterval: 60000`; mutations (`useCreateInvoice`, `useApproveInvoice`, `useCancelInvoice`, `useRecordPayment`, `useCreateCreditNote`) with cache invalidation.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useInvoices.ts` (create)
- **Dependencies**: [task_10]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 12: Create Invoice Routing & Layout
- **ID**: task_12
- **Description**: Create `InvoiceLayout.tsx` (sub-sidebar with 6 nav items + Outlet). Update `App.tsx` to add invoice route group (`/invoices/*`). Update main sidebar component to add "Invoices" section with receipt/document icon.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceLayout.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx` (update)
  - Sidebar component (identify and update)
- **Dependencies**: [task_11]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 13: Create Invoice Dashboard Page
- **ID**: task_13
- **Description**: Build `InvoiceDashboardPage.tsx` with: 4 KPI cards (Revenue Today AED, Pending Payments AED, Overdue Invoices count, Draft Invoices count), Revenue Trend LineChart (Recharts), Payment Status donut PieChart, Payment Alerts table (TanStack Table) with severity icons and clickable invoice links. Use `useInvoiceDashboard` hook. Loading skeletons during fetch.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceDashboardPage.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: high
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 14: Create Invoice Overview Page
- **ID**: task_14
- **Description**: Build `InvoiceOverviewPage.tsx` with search bar (category dropdown + input with 300ms debounce), filter dropdown, date range picker, export button. Build `InvoiceTable.tsx` (TanStack Table, clickable rows → navigate to detail), `InvoiceFilters.tsx`, `QuickActionsDropdown.tsx` (Approve/Cancel/Open Details). Empty state with link to Jobs module.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceOverviewPage.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceFilters.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceTable.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/QuickActionsDropdown.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: high
- **Can Run Parallel**: yes (parallel with task_13)
- **Playbook**: null
- **Approach**: cognitive

### Task 15: Create Invoice Detail Page
- **ID**: task_15
- **Description**: Build `InvoiceDetailPage.tsx` as full invoice workspace with sub-components: `InvoiceHeader.tsx` (invoice no, date, job ID, status badges), `CustomerVehicleCard.tsx`, `InsuranceSummaryCard.tsx` (conditional on payer_type), `ServicesCostTable.tsx` (expandable rows showing parts), `PaymentSummaryCard.tsx`, `InvoiceNotesSection.tsx` (internal + customer notes), `InvoiceActionBar.tsx` (language dropdown, Download PDF, Print, WhatsApp — enabled only when approved). Approve button triggers confirmation dialog. Use `useInvoice` and `useApproveInvoice`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceDetailPage.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceHeader.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/CustomerVehicleCard.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InsuranceSummaryCard.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/ServicesCostTable.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/PaymentSummaryCard.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceNotesSection.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceActionBar.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: high
- **Can Run Parallel**: yes (parallel with task_13, task_14)
- **Playbook**: null
- **Approach**: cognitive

### Task 16: Create Pending Payments Page
- **ID**: task_16
- **Description**: Build `PendingPaymentsPage.tsx` with summary cards (Total Outstanding, Overdue Amount, Insurance Pending), pending payments table with Quick Actions (Record Payment, Send Reminder, Open Details). Build `RecordPaymentModal.tsx` with form: Invoice No (readonly), Payment Amount (validated: > 0, <= remaining_balance), Payment Method dropdown, Transaction Reference, Payment Date, Notes. Optimistic UI update on save. Use `usePendingPayments` and `useRecordPayment`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/PendingPaymentsPage.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/RecordPaymentModal.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_13-15)
- **Playbook**: null
- **Approach**: cognitive

### Task 17: Create Payment History Page
- **ID**: task_17
- **Description**: Build `PaymentHistoryPage.tsx` with date range filter and payments table (Payment Date, Invoice No, Customer, Payment Method, Transaction Reference, Amount Paid, Recorded By). Use `usePaymentHistory`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/PaymentHistoryPage.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with task_13-16)
- **Playbook**: null
- **Approach**: deterministic

### Task 18: Create Credit Notes Page
- **ID**: task_18
- **Description**: Build `CreditNotesPage.tsx` with table (Credit Note No, Invoice No, Customer, Reason, Credit Amount, Created Date, Status) and "Create Credit Note" button. Build `CreateCreditNoteModal.tsx` with form: invoice search, reason, credit amount (validated: <= invoice grand_total). Use `useCreditNotes` and `useCreateCreditNote`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/CreditNotesPage.tsx` (create)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/CreateCreditNoteModal.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_13-17)
- **Playbook**: null
- **Approach**: cognitive

### Task 19: Create Invoice Export Page
- **ID**: task_19
- **Description**: Build `InvoiceExportPage.tsx` with tab selector (Approved Invoices, VAT Export, Pending Payments, Payment History), preview table that changes columns based on selected type, and export buttons (Excel, CSV, PDF triggering browser file download). Use `invoiceService.exportData`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceExportPage.tsx` (create)
- **Dependencies**: [task_12]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_13-18)
- **Playbook**: null
- **Approach**: cognitive

### Task 20: Seed Test Data
- **ID**: task_20
- **Description**: Create a seed script or extend existing seed data to populate sample invoices in various states (draft, pending_approval, approved, cancelled) with varying payment statuses (pending, partially_paid, paid, overdue), sample payments, and sample credit notes. This enables frontend development and testing without waiting for full backend integration.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/seed_invoices.py` (create or extend existing seed)
- **Dependencies**: [task_7, task_2]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

---

## Execution Strategy

**Parallel Groups**:
- **Group 1** (independent foundations): [task_1, task_2, task_9]
- **Group 2** (backend repos + dashboard fix, depends on task_1): [task_3, task_4, task_5, task_8]
- **Group 3** (backend service, depends on Group 2): [task_6]
- **Group 4** (backend routes + React service layer in parallel): [task_7, task_10] (task_10 depends on task_9 only)
- **Group 5** (React hooks, depends on task_10): [task_11]
- **Group 6** (React routing/layout, depends on task_11): [task_12]
- **Group 7** (all UI pages, depends on task_12): [task_13, task_14, task_15, task_16, task_17, task_18, task_19]
- **Group 8** (seed data, depends on task_7 + task_2): [task_20]

## Dependencies Graph

```
task_1 ──┬──> task_3 ──┐
         ├──> task_4 ──┤
         ├──> task_5 ──┼──> task_6 ──> task_7 ──> task_20
         └──> task_8   │
                       │
task_2 ────────────────┼──────────────────────────> task_20
                       │
task_9 ──> task_10 ──> task_11 ──> task_12 ──┬──> task_13
                                             ├──> task_14
                                             ├──> task_15
                                             ├──> task_16
                                             ├──> task_17
                                             ├──> task_18
                                             └──> task_19
```

## Architect Warnings Addressed

| Warning | Resolution |
|---------|-----------|
| #1 `job_id` vs `work_order_id` | Store `work_order_id` in DynamoDB; map to `job_id` in API responses/requests (Task 6 & 7) |
| #2 Existing invoices table GSIs | Update `init_db.py` with new GSI set (Task 2) |
| #3 Dashboard service enum values | Update dashboard_service.py to lowercase values (Task 8) |
| #4 Existing model imports | Update `__init__.py` exports when replacing model (Task 1) |
| #5 Invoice number atomicity | Use `counters` table with conditional write, PK `COUNTER#invoice` / `COUNTER#credit_note` (Task 2 + Task 6) |
| #6 New tables in init_db | Added to Task 2 explicitly |

## Total Estimated Effort

**High** — 20 tasks spanning full-stack implementation (6 backend, 1 infra, 12 React, 1 seed data). Critical path is 7 tasks deep (task_1 → task_3 → task_6 → task_7 → ... or task_9 → task_10 → task_11 → task_12 → UI pages). Backend and React service layers can progress in parallel after their respective foundation tasks complete. UI pages (Group 7) are all independent of each other, offering maximum parallelism in Phase 3-4.

## Confidence: 85%

High confidence because the design is extremely detailed, architect has approved feasibility, and existing codebase patterns are well-established. Remaining uncertainty: exact structure of existing sidebar component (need to identify file), how WorkOrderRepository returns service/parts data for invoice generation (Task 6 integration logic), and whether Recharts is already a project dependency for the dashboard charts.