# Designer Output - Issue #5

## Metadata

- **agent**: designer
- **status**: complete
- **confidence**: 88

## Design Document

# Design Document: Invoice Module (Issue #5)

## Requirements Analysis

The Invoice Module is a comprehensive invoicing and payment management system for GarageHQ that integrates with Jobs, Services, Parts, Insurance Claims, Customer Payments, and Accounting Export. It must support:

- Draft → Approval → Locked workflow with invoice locking after approval
- Auto-calculated payment status (never manually set)
- Insurance/Mixed payment handling with split tracking
- Bilingual customer invoice generation (English + Arabic)
- Payment recording with full audit trail
- Credit notes for reversals/adjustments
- Export capabilities for accounting, VAT filing, collections

The existing `invoice.py` model is a simplified skeleton that must be replaced with the full-featured model hierarchy supporting the complete workflow.

## Architecture Overview

**Backend Changes:**
- Replace existing `app/models/invoice.py` with expanded models (InvoiceStatus enum, PayerType, InsurancePaymentStatus, services breakdown, payment entries, credit notes)
- New repository: `InvoiceRepository` (DynamoDB table: `invoices`)
- New repository: `PaymentRepository` (DynamoDB table: `payments`)
- New repository: `CreditNoteRepository` (DynamoDB table: `credit_notes`)
- New service: `InvoiceService` (business logic, auto-calculation, workflow)
- New routes: `invoice_bp` with full CRUD + workflow endpoints

**React Changes:**
- New sidebar section: "Invoices" with sub-navigation
- 6 new pages: Dashboard, Overview, Detail, Pending Payments, Payment History, Credit Notes, Export
- New hooks: `useInvoices`, `useInvoiceDashboard`, `usePayments`, `useCreditNotes`
- New service: `invoiceService.ts`
- New types: `invoice.ts`

**DynamoDB Changes:**
- New table: `invoices` (expanded schema)
- New table: `payments` (payment entry records)
- New table: `credit_notes`

## Components

### Component 1: Backend — Invoice Models (Expanded)

- **Purpose**: Replace existing basic model with full-featured Pydantic models supporting the complete invoice workflow
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/invoice.py` (replace)
- **Dependencies**: `app.models.common.TimestampMixin`

**New Enums:**
```python
class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PayerType(str, Enum):
    CUSTOMER = "customer"
    INSURANCE = "insurance"
    MIXED = "mixed"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    INSURANCE_PAYMENT = "insurance_payment"
    MIXED = "mixed"

class InsurancePaymentStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    REJECTED = "rejected"

class CreditNoteStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    APPLIED = "applied"
    CANCELLED = "cancelled"
```

**Key Models:**
```python
class ServiceLineItem(BaseModel):
    service_id: str
    service_type: str
    labor_cost: Decimal
    parts_cost: Decimal
    additional_charges: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    vat: Decimal
    total: Decimal
    parts: List[PartLineItem] = []

class PartLineItem(BaseModel):
    part_id: str
    part_name: str
    quantity: Decimal
    unit_price: Decimal
    vat: Decimal
    total: Decimal

class InsuranceDetails(BaseModel):
    provider: str
    claim_number: str
    insurance_amount: Decimal
    customer_deductible: Decimal
    insurance_payment_status: InsurancePaymentStatus

class InvoiceCreate(BaseModel):
    job_id: str
    due_date: Optional[date] = None
    payer_type: PayerType = PayerType.CUSTOMER
    insurance_details: Optional[InsuranceDetails] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None

class Invoice(TimestampMixin, BaseModel):
    invoice_id: str
    invoice_number: str  # INV-YYYY-NNNN
    job_id: str
    customer_id: str
    vehicle_id: str
    invoice_date: date
    due_date: Optional[date]
    invoice_status: InvoiceStatus
    payment_status: PaymentStatus
    payer_type: PayerType
    services: List[ServiceLineItem]
    insurance_details: Optional[InsuranceDetails]
    subtotal: Decimal
    vat_total: Decimal
    insurance_amount: Decimal = Decimal("0.00")
    customer_amount: Decimal
    grand_total: Decimal
    paid_amount: Decimal = Decimal("0.00")
    remaining_balance: Decimal
    internal_notes: Optional[str]
    customer_notes: Optional[str]
    invoice_language: str = "en"  # "en" or "en_ar"
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    # Denormalized for table display
    customer_name: Optional[str]
    customer_phone: Optional[str]
    vehicle_display: Optional[str]
    plate_number: Optional[str]
    mileage: Optional[str]
    primary_service: Optional[str]

class PaymentEntry(BaseModel):
    payment_id: str
    invoice_id: str
    payment_amount: Decimal
    payment_method: PaymentMethod
    transaction_reference: Optional[str]
    payment_date: date
    notes: Optional[str]
    recorded_by: str
    created_at: datetime

class CreditNote(TimestampMixin, BaseModel):
    credit_note_id: str
    credit_note_number: str  # CN-YYYY-NNNN
    invoice_id: str
    customer_id: str
    reason: str
    credit_amount: Decimal
    status: CreditNoteStatus
    created_by: str
    customer_name: Optional[str]
```

---

### Component 2: Backend — Invoice Repository

- **Purpose**: DynamoDB access layer for invoices table
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/invoice_repository.py`
- **DynamoDB access pattern**:
  - Table: `invoices`
  - PK: `invoice_id`
  - GSI-1: `customer_id-index` (PK: `customer_id`, SK: `invoice_date`)
  - GSI-2: `job_id-index` (PK: `job_id`)
  - GSI-3: `invoice_status-index` (PK: `invoice_status`, SK: `invoice_date`)
  - GSI-4: `payment_status-index` (PK: `payment_status`, SK: `due_date`)
  - GSI-5: `invoice_number-index` (PK: `invoice_number`)
- **Dependencies**: `BaseRepository`

**Key methods:**
```python
class InvoiceRepository(BaseRepository):
    table_name = "invoices"
    primary_key = "invoice_id"

    def get_by_customer(self, customer_id, limit=50)
    def get_by_job(self, job_id)
    def get_by_status(self, invoice_status, limit=50)
    def get_by_payment_status(self, payment_status, limit=50)
    def get_by_invoice_number(self, invoice_number)
    def get_pending_payments(self, limit=100)  # payment_status IN (pending, partially_paid, overdue)
    def get_overdue_invoices(self)  # payment_status = overdue
    def get_draft_invoices(self)  # invoice_status = draft
    def get_invoices_by_date_range(self, start_date, end_date, limit=200)
```

---

### Component 3: Backend — Payment Repository

- **Purpose**: DynamoDB access layer for payment entries
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/payment_repository.py`
- **DynamoDB access pattern**:
  - Table: `payments`
  - PK: `payment_id`
  - GSI-1: `invoice_id-index` (PK: `invoice_id`, SK: `payment_date`)
  - GSI-2: `payment_date-index` (PK: `payment_date_partition`, SK: `payment_date`) — partition by YYYY-MM for efficient date range queries
  - GSI-3: `recorded_by-index` (PK: `recorded_by`, SK: `payment_date`)
- **Dependencies**: `BaseRepository`

---

### Component 4: Backend — Credit Note Repository

- **Purpose**: DynamoDB access layer for credit notes
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/credit_note_repository.py`
- **DynamoDB access pattern**:
  - Table: `credit_notes`
  - PK: `credit_note_id`
  - GSI-1: `invoice_id-index` (PK: `invoice_id`)
  - GSI-2: `customer_id-index` (PK: `customer_id`, SK: `created_at`)
  - GSI-3: `status-index` (PK: `status`, SK: `created_at`)
- **Dependencies**: `BaseRepository`

---

### Component 5: Backend — Invoice Service

- **Purpose**: Core business logic including invoice generation from jobs, approval workflow, payment status auto-calculation, payment recording
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/invoice_service.py`
- **Dependencies**: `InvoiceRepository`, `PaymentRepository`, `CreditNoteRepository`, `WorkOrderRepository`, `CustomerRepository`, `VehicleRepository`, `InventoryRepository`

**Key methods:**
```python
class InvoiceService:
    def generate_invoice_from_job(self, job_id, user_id, data) -> Tuple[Optional[Dict], Optional[str]]
    def get_invoice(self, invoice_id) -> Tuple[Optional[Dict], Optional[str]]
    def list_invoices(self, filters) -> Tuple[Optional[Dict], Optional[str]]
    def approve_invoice(self, invoice_id, user_id) -> Tuple[Optional[Dict], Optional[str]]
    def cancel_invoice(self, invoice_id, user_id) -> Tuple[Optional[Dict], Optional[str]]
    def record_payment(self, invoice_id, payment_data, user_id) -> Tuple[Optional[Dict], Optional[str]]
    def get_pending_payments(self, filters) -> Tuple[Optional[Dict], Optional[str]]
    def get_payment_history(self, filters) -> Tuple[Optional[Dict], Optional[str]]
    def get_dashboard_data(self) -> Tuple[Optional[Dict], Optional[str]]
    def create_credit_note(self, data, user_id) -> Tuple[Optional[Dict], Optional[str]]
    def export_invoices(self, export_type, filters) -> Tuple[Optional[Dict], Optional[str]]
    def _recalculate_payment_status(self, invoice) -> str  # Auto-calculation logic
    def _check_overdue_invoices(self)  # System date check
    def _generate_invoice_number(self) -> str  # INV-YYYY-NNNN
```

**Payment Status Auto-Calculation Logic:**
```python
def _recalculate_payment_status(self, invoice):
    if invoice['invoice_status'] == 'cancelled':
        return 'cancelled'
    if invoice['paid_amount'] == 0 and invoice['remaining_balance'] > 0:
        if invoice.get('due_date') and date.today() > invoice['due_date']:
            return 'overdue'
        return 'pending'
    if invoice['paid_amount'] > 0 and invoice['remaining_balance'] > 0:
        if invoice.get('due_date') and date.today() > invoice['due_date']:
            return 'overdue'
        return 'partially_paid'
    if invoice['remaining_balance'] <= 0:
        return 'paid'
    return 'pending'
```

---

### Component 6: Backend — Invoice Routes

- **Purpose**: REST API endpoints for the invoice module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/invoices.py`
- **Dependencies**: `InvoiceService`, `require_auth`, response helpers

**API Endpoints:**

| Method | Path | Purpose | Request | Response |
|--------|------|---------|---------|----------|
| GET | `/api/invoices/dashboard` | Dashboard KPIs + alerts | query: `period` | `{kpis, alerts, revenue_trend, payment_status_summary}` |
| GET | `/api/invoices` | List/search/filter invoices | query: `status`, `payment_status`, `search_category`, `search_term`, `start_date`, `end_date`, `page`, `limit` | `{invoices[], total, page, limit}` |
| GET | `/api/invoices/:id` | Get invoice detail | - | `{invoice}` |
| POST | `/api/invoices` | Generate invoice from job | `{job_id, due_date?, payer_type, insurance_details?, notes?}` | `{invoice}` 201 |
| PUT | `/api/invoices/:id` | Update draft invoice | `{due_date?, internal_notes?, customer_notes?}` | `{invoice}` |
| POST | `/api/invoices/:id/approve` | Approve & lock invoice | - | `{invoice}` |
| POST | `/api/invoices/:id/cancel` | Cancel invoice | `{reason?}` | `{invoice}` |
| POST | `/api/invoices/:id/payments` | Record payment | `{payment_amount, payment_method, transaction_reference?, payment_date, notes?}` | `{payment, invoice}` 201 |
| GET | `/api/invoices/pending-payments` | List pending payments | query: `page`, `limit` | `{invoices[], summary}` |
| GET | `/api/invoices/payment-history` | List all payments | query: `start_date`, `end_date`, `page`, `limit` | `{payments[], total}` |
| GET | `/api/invoices/:id/payments` | Payments for one invoice | - | `{payments[]}` |
| POST | `/api/invoices/credit-notes` | Create credit note | `{invoice_id, reason, credit_amount}` | `{credit_note}` 201 |
| GET | `/api/invoices/credit-notes` | List credit notes | query: `status`, `page`, `limit` | `{credit_notes[], total}` |
| GET | `/api/invoices/export` | Export data | query: `type` (approved/vat/pending/history), `start_date`, `end_date`, `format` (json/csv) | `{data[]}` or CSV file |
| POST | `/api/invoices/:id/generate-pdf` | Generate customer PDF | `{language: "en" \| "en_ar"}` | `{pdf_url}` |

---

### Component 7: React — Types

- **Purpose**: TypeScript type definitions for the invoice module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/invoice.ts`

```typescript
export type InvoiceStatus = 'draft' | 'pending_approval' | 'approved' | 'cancelled';
export type PaymentStatus = 'pending' | 'partially_paid' | 'paid' | 'overdue' | 'cancelled';
export type PayerType = 'customer' | 'insurance' | 'mixed';
export type PaymentMethod = 'cash' | 'card' | 'bank_transfer' | 'insurance_payment' | 'mixed';
export type InsurancePaymentStatus = 'pending_approval' | 'approved' | 'submitted' | 'partially_paid' | 'paid' | 'rejected';
export type CreditNoteStatus = 'draft' | 'approved' | 'applied' | 'cancelled';
export type ExportType = 'approved' | 'vat' | 'pending' | 'history';

export interface ServiceLineItem { ... }
export interface PartLineItem { ... }
export interface InsuranceDetails { ... }
export interface Invoice { ... }
export interface PaymentEntry { ... }
export interface CreditNote { ... }
export interface InvoiceDashboard { kpis: KPICard[]; alerts: PaymentAlert[]; revenue_trend: RevenueTrendPoint[]; payment_status_summary: PaymentStatusSummary; }
export interface InvoiceFilters { status?: InvoiceStatus; payment_status?: PaymentStatus; search_category?: string; search_term?: string; start_date?: string; end_date?: string; }
```

---

### Component 8: React — Invoice Service

- **Purpose**: API service layer for invoice endpoints
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/invoiceService.ts`
- **Dependencies**: `@/services/api`

```typescript
export const invoiceService = {
  getDashboard: (period?: string) => api.get('/invoices/dashboard', { params: { period } }),
  getInvoices: (filters: InvoiceFilters) => api.get('/invoices', { params: filters }),
  getInvoice: (id: string) => api.get(`/invoices/${id}`),
  createInvoice: (data: InvoiceCreatePayload) => api.post('/invoices', data),
  updateInvoice: (id: string, data: InvoiceUpdatePayload) => api.put(`/invoices/${id}`, data),
  approveInvoice: (id: string) => api.post(`/invoices/${id}/approve`),
  cancelInvoice: (id: string, reason?: string) => api.post(`/invoices/${id}/cancel`, { reason }),
  recordPayment: (id: string, data: PaymentPayload) => api.post(`/invoices/${id}/payments`, data),
  getInvoicePayments: (id: string) => api.get(`/invoices/${id}/payments`),
  getPendingPayments: (params?: PaginationParams) => api.get('/invoices/pending-payments', { params }),
  getPaymentHistory: (params?: PaymentHistoryParams) => api.get('/invoices/payment-history', { params }),
  createCreditNote: (data: CreditNotePayload) => api.post('/invoices/credit-notes', data),
  getCreditNotes: (params?: CreditNoteParams) => api.get('/invoices/credit-notes', { params }),
  exportData: (type: ExportType, params?: ExportParams) => api.get('/invoices/export', { params: { type, ...params } }),
  generatePdf: (id: string, language: string) => api.post(`/invoices/${id}/generate-pdf`, { language }),
};
```

---

### Component 9: React — Invoice Hooks

- **Purpose**: TanStack Query hooks for data fetching and mutations
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useInvoices.ts`
- **Dependencies**: `@tanstack/react-query`, `invoiceService`

```typescript
// Queries
export function useInvoiceDashboard(period?: string)
export function useInvoices(filters: InvoiceFilters)
export function useInvoice(id: string)
export function usePendingPayments(params?: PaginationParams)
export function usePaymentHistory(params?: PaymentHistoryParams)
export function useCreditNotes(params?: CreditNoteParams)
export function useInvoicePayments(invoiceId: string)

// Mutations
export function useCreateInvoice()
export function useApproveInvoice()
export function useCancelInvoice()
export function useRecordPayment()
export function useCreateCreditNote()
```

All queries use `refetchInterval: 60000` (60s auto-refresh per project convention).

---

### Component 10: React — Invoice Dashboard Page

- **Purpose**: KPI cards, revenue trend chart, payment status donut, payment alerts table
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceDashboardPage.tsx`
- **Dependencies**: `useInvoiceDashboard`, Recharts (LineChart, PieChart), TanStack Table

**Layout (from target design):**
- Row 1: 4 KPI cards (Revenue Today AED, Pending Payments AED, Overdue Invoices count, Draft Invoices count)
- Row 2: Left — Revenue Trend (Line Chart: daily/weekly/monthly), Right — Payment Status Summary (Donut chart)
- Row 3: Payment Alerts table (severity icon, alert type, message, related invoice link)

---

### Component 11: React — Invoice Overview Page

- **Purpose**: Filterable, searchable data grid of all invoices with quick actions
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceOverviewPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceFilters.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/QuickActionsDropdown.tsx`
- **Dependencies**: `useInvoices`, TanStack Table, `useNavigate`

**Layout:**
- Top bar: Search category dropdown + search input, filter dropdown, date range picker, export button
- Table columns: Invoice No, Customer, Payer Type, Primary Service, Payment Status, Grand Total, Insurance Amount, Customer Amount, Remaining Balance, Due Date, Aging, Quick Actions
- Entire row clickable → navigates to Invoice Detail
- Quick Actions: Approve Invoice, Cancel Invoice, Open Invoice Details

---

### Component 12: React — Invoice Detail Page

- **Purpose**: Full invoice workspace showing all details, services breakdown, payment summary, actions
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceDetailPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceHeader.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/CustomerVehicleCard.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InsuranceSummaryCard.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/ServicesCostTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/PaymentSummaryCard.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceNotesSection.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceActionBar.tsx`
- **Dependencies**: `useInvoice`, `useApproveInvoice`, route param `:invoiceId`

**Layout (from target design):**
- Header: Invoice No, Date, Job ID, Invoice Status badge, Payment Status badge
- Section: Customer & Vehicle Details (name, phone, vehicle, plate, mileage)
- Section: Insurance Payment Summary (conditional on payer type)
- Section: Services & Cost Summary Table with expandable rows showing parts
- Section: Payment Summary (subtotal, VAT, insurance, customer amount, grand total, paid, remaining)
- Section: Internal Notes + Customer Notes
- Action Bar: Language dropdown, Download PDF, Print Invoice, Send WhatsApp

---

### Component 13: React — Pending Payments Page

- **Purpose**: Track outstanding payments, record payments, send reminders
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/PendingPaymentsPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/RecordPaymentModal.tsx`
- **Dependencies**: `usePendingPayments`, `useRecordPayment`

**Layout:**
- Summary cards: Total Outstanding, Overdue Amount, Insurance Pending
- Table: Invoice No, Customer, Payer, Phone, Due Date, Aging Days, Grand Total, Paid Amount, Remaining Balance, Quick Actions
- Quick Actions: Record Payment (opens modal), Send Reminder, Open Invoice Details
- Record Payment Modal: Invoice No (readonly), Payment Amount, Payment Method dropdown, Transaction Reference, Payment Date, Notes

---

### Component 14: React — Payment History Page

- **Purpose**: Full audit trail of all payments recorded
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/PaymentHistoryPage.tsx`
- **Dependencies**: `usePaymentHistory`

**Layout:**
- Date range filter
- Table: Payment Date, Invoice No, Customer, Payment Method, Transaction Reference, Amount Paid, Recorded By

---

### Component 15: React — Credit Notes Page

- **Purpose**: Manage invoice reversals, adjustments, corrections
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/CreditNotesPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/CreateCreditNoteModal.tsx`
- **Dependencies**: `useCreditNotes`, `useCreateCreditNote`

**Layout:**
- Table: Credit Note No, Invoice No, Customer, Reason, Credit Amount, Created Date, Status
- Action: Create Credit Note button → modal

---

### Component 16: React — Invoice Export Page

- **Purpose**: Export financial data for accounting, VAT, collections
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceExportPage.tsx`
- **Dependencies**: `invoiceService.exportData`

**Layout:**
- Export type selector tabs: Approved Invoices | VAT Export | Pending Payments | Payment History
- Preview table (changes based on selected type)
- Export buttons: Excel, CSV, PDF

---

### Component 17: React — Invoice Sidebar & Routing

- **Purpose**: Navigation structure and route definitions for invoice module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/invoices/InvoiceLayout.tsx` (sidebar + outlet)
  - Update: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx` (add invoice routes)
  - Update: Sidebar component (add Invoices section)

**Routes:**
```
/invoices                  → InvoiceDashboardPage
/invoices/overview         → InvoiceOverviewPage
/invoices/overview/:id     → InvoiceDetailPage
/invoices/pending-payments → PendingPaymentsPage
/invoices/payment-history  → PaymentHistoryPage
/invoices/credit-notes     → CreditNotesPage
/invoices/export           → InvoiceExportPage
```

**Sidebar structure:**
- Invoice Dashboard
- Invoice Overview
- Pending Payments
- Payment History
- Credit Notes
- Invoice Export

---

## DynamoDB Schema Changes

### Table: `invoices` (replace existing if any, or new)

| Field | Type | Description |
|-------|------|-------------|
| `invoice_id` (PK) | String | `inv_<16chars>` |
| `invoice_number` | String | `INV-YYYY-NNNN` |
| `job_id` | String | Link to job |
| `customer_id` | String | Link to customer |
| `vehicle_id` | String | Link to vehicle |
| `invoice_date` | String (ISO date) | Date created |
| `due_date` | String (ISO date) | Payment due date |
| `invoice_status` | String | draft/pending_approval/approved/cancelled |
| `payment_status` | String | pending/partially_paid/paid/overdue/cancelled |
| `payer_type` | String | customer/insurance/mixed |
| `services` | List<Map> | Service line items with nested parts |
| `insurance_details` | Map | Provider, claim, amounts (nullable) |
| `subtotal` | Number (Decimal) | |
| `vat_total` | Number (Decimal) | |
| `insurance_amount` | Number (Decimal) | |
| `customer_amount` | Number (Decimal) | |
| `grand_total` | Number (Decimal) | |
| `paid_amount` | Number (Decimal) | |
| `remaining_balance` | Number (Decimal) | |
| `internal_notes` | String | |
| `customer_notes` | String | |
| `invoice_language` | String | en / en_ar |
| `approved_at` | String (ISO datetime) | |
| `approved_by` | String | |
| `customer_name` | String | Denormalized |
| `customer_phone` | String | Denormalized |
| `vehicle_display` | String | Denormalized |
| `plate_number` | String | Denormalized |
| `mileage` | String | Denormalized |
| `primary_service` | String | Denormalized |
| `created_at` | String (ISO datetime) | |
| `updated_at` | String (ISO datetime) | |

**GSIs (5 max):**
1. `customer_id-index` — PK: `customer_id`, SK: `invoice_date`
2. `job_id-index` — PK: `job_id`
3. `invoice_status-index` — PK: `invoice_status`, SK: `invoice_date`
4. `payment_status-index` — PK: `payment_status`, SK: `due_date`
5. `invoice_number-index` — PK: `invoice_number`

### Table: `payments`

| Field | Type | Description |
|-------|------|-------------|
| `payment_id` (PK) | String | `pmt_<16chars>` |
| `invoice_id` | String | Link to invoice |
| `payment_amount` | Number (Decimal) | |
| `payment_method` | String | cash/card/bank_transfer/insurance_payment/mixed |
| `transaction_reference` | String | |
| `payment_date` | String (ISO date) | |
| `payment_date_partition` | String | YYYY-MM (for GSI partition) |
| `notes` | String | |
| `recorded_by` | String | User ID |
| `customer_id` | String | Denormalized for queries |
| `customer_name` | String | Denormalized |
| `invoice_number` | String | Denormalized |
| `created_at` | String (ISO datetime) | |

**GSIs (3 used of 5 max):**
1. `invoice_id-index` — PK: `invoice_id`, SK: `payment_date`
2. `payment_date_partition-index` — PK: `payment_date_partition`, SK: `payment_date`
3. `recorded_by-index` — PK: `recorded_by`, SK: `payment_date`

### Table: `credit_notes`

| Field | Type | Description |
|-------|------|-------------|
| `credit_note_id` (PK) | String | `cn_<16chars>` |
| `credit_note_number` | String | `CN-YYYY-NNNN` |
| `invoice_id` | String | |
| `customer_id` | String | |
| `reason` | String | |
| `credit_amount` | Number (Decimal) | |
| `status` | String | draft/approved/applied/cancelled |
| `created_by` | String | User ID |
| `customer_name` | String | Denormalized |
| `invoice_number` | String | Denormalized |
| `created_at` | String (ISO datetime) | |
| `updated_at` | String (ISO datetime) | |

**GSIs (3 used of 5 max):**
1. `invoice_id-index` — PK: `invoice_id`
2. `customer_id-index` — PK: `customer_id`, SK: `created_at`
3. `status-index` — PK: `status`, SK: `created_at`

---

## UX Interaction Flow

### Flow 1: Invoice Dashboard
1. User clicks "Invoices" in main sidebar → lands on Invoice Dashboard
2. Sees 4 KPI cards (Revenue Today, Pending Payments AED, Overdue count, Draft count) with loading skeletons during fetch
3. Revenue Trend line chart loads below (daily/weekly toggle)
4. Payment Status donut chart shows distribution
5. Payment Alerts table shows actionable items — clicking "Related Invoice" navigates to detail

### Flow 2: Invoice Overview & Filtering
1. User clicks "Invoice Overview" in invoice sub-sidebar → sees full table
2. Empty state: "No invoices found" message with link to Jobs module
3. User selects search category (Invoice Number, Customer Name, etc.) → types in search box → table filters live after 300ms debounce
4. User selects filter (Draft, Approved, Overdue, etc.) → table updates
5. User sets date range → table scopes to range
6. User clicks any row → navigates to `/invoices/overview/:id` (Invoice Detail)
7. User clicks Quick Actions → dropdown shows: Approve (only if draft/pending), Cancel, Open Details

### Flow 3: Invoice Detail & Approval
1. User arrives at Invoice Detail → full invoice loads with all sections
2. Services table shows expandable rows — clicking expand arrow reveals parts used
3. If invoice is Draft:
   - Action bar shows "Approve Invoice" button (primary)
   - User clicks Approve → confirmation dialog → invoice locks
   - Success toast: "Invoice approved and locked"
   - PDF/Print/WhatsApp buttons become enabled
4. If invoice is Approved:
   - Download PDF, Print Invoice, Send WhatsApp are available
   - Language dropdown (English / English + Arabic) changes PDF language
   - No edit actions available (locked)
5. Error: If approval fails → error toast with reason, invoice stays in current state

### Flow 4: Recording Payment
1. User navigates to "Pending Payments" → sees summary cards + table
2. User clicks Quick Actions → "Record Payment" on a row
3. Modal opens with Invoice No (readonly), pre-filled remaining balance
4. User enters: Payment Amount, selects Payment Method, Transaction Reference, Payment Date, Notes
5. Validation: amount must be > 0 and <= remaining balance
6. User clicks "Save" → optimistic UI updates paid amount
7. System recalculates: paid_amount, remaining_balance, payment_status
8. If remaining_balance = 0 → row removed from pending payments table
9. Payment appears in Payment History
10. Error: "Insufficient amount" or network error → toast, modal stays open

### Flow 5: Credit Note Creation
1. User navigates to "Credit Notes" → sees table of existing credit notes
2. User clicks "Create Credit Note" button
3. Modal: select invoice (search by number), enter reason, enter credit amount
4. Validation: credit amount <= invoice grand total
5. Save → credit note created in Draft status
6. Manager approves → credit note applied → invoice balance recalculated

### Flow 6: Export
1. User navigates to "Invoice Export"
2. Selects export type tab (Approved Invoices, VAT Export, Pending Payments, Payment History)
3. Relevant table loads with preview data
4. User reviews → clicks "Export Excel" or "Export CSV" or "Export PDF"
5. File downloads to browser

---

## System Component Assessment

| Component | Required? | Justification |
|---|---|---|
| WebSocket / real-time | NO | 60s TanStack Query auto-refresh is sufficient for invoice status updates; no real-time collaboration needed |
| Background job / queue | MAYBE | Overdue status check could run on a cron/scheduled basis to update payment_status to "overdue" when due_date passes. However, can also check lazily at query time |
| Cache (Redis) | NO | Invoice data changes with each payment; dashboard KPIs can be computed from DynamoDB scans with reasonable limits; not fetched >10x/min |
| File storage (S3) | YES | PDF generation requires storing generated invoice PDFs for download/sharing |
| Third-party API | MAYBE | WhatsApp sharing (could be a simple `wa.me` link with text rather than API integration); PDF generation library (server-side) |
| Search engine | NO | Filtered queries via DynamoDB GSIs are sufficient for the expected data volume per garage |

## Architect Escalation

- **File storage (S3)**: PDF generation must store files somewhere downloadable. Proposed approach: generate PDF server-side using a Python library (e.g., `weasyprint` or `reportlab`), store in S3 with signed URLs (24h expiry). Risk if skipped: no PDF download/print/share capability (core feature). **Phase 3+ item** — can initially return HTML-rendered invoice for print.

- **Background job (overdue check)**: Payment status should flip to "overdue" when `due_date` passes. Two approaches:
  1. **Lazy check**: On every query/list, compare `due_date` with today and return computed status (no stored update) — simpler, no infrastructure
  2. **Cron job**: Run daily, scan `payment_status=pending` + `payment_status=partially_paid` where `due_date < today`, update status — ensures dashboard KPIs are accurate without query-time computation.
  
  **Recommendation**: Start with lazy check (Phase 1), add cron if dashboard accuracy becomes an issue.

- **WhatsApp sharing**: Use `https://wa.me/?text=...` deep link pattern (no API needed). PDF URL can be included in the message text. No third-party API required.

---

## Implementation Phases

### Phase 1: Backend Foundation
1. Expand `app/models/invoice.py` with full model hierarchy
2. Create DynamoDB tables: `invoices`, `payments`, `credit_notes` with GSIs
3. Create `InvoiceRepository`, `PaymentRepository`, `CreditNoteRepository`
4. Create `InvoiceService` with core logic (generate, approve, cancel, record payment, auto-status)
5. Create `app/routes/invoices.py` with all endpoints
6. Register blueprint in `app/__init__.py`
7. Seed test data (sample invoices in various states)

### Phase 2: React Service Layer
1. Create `src/types/invoice.ts`
2. Create `src/services/invoiceService.ts`
3. Create `src/hooks/useInvoices.ts`
4. Add invoice routes to `App.tsx`
5. Add Invoices section to sidebar

### Phase 3: React UI — Core Pages
1. `InvoiceLayout.tsx` (sub-sidebar + Outlet)
2. `InvoiceDashboardPage.tsx` (KPIs, charts, alerts)
3. `InvoiceOverviewPage.tsx` (table, filters, search)
4. `InvoiceDetailPage.tsx` (full detail with expandable services)

### Phase 4: React UI — Payment & Operations
1. `PendingPaymentsPage.tsx` + `RecordPaymentModal.tsx`
2. `PaymentHistoryPage.tsx`
3. `CreditNotesPage.tsx` + `CreateCreditNoteModal.tsx`
4. `InvoiceExportPage.tsx`

### Phase 5: PDF & Bilingual (can be deferred)
1. Server-side PDF generation endpoint
2. Bilingual template (English + Arabic)
3. S3 storage integration
4. WhatsApp share link

---

## Risks and Concerns

- **Existing model replacement**: The current `invoice.py` model is basic (unpaid/partial/paid only). Replacing it requires ensuring no other part of the codebase depends on the old model shape. Mitigation: search for imports of `invoice.py` models before replacing.

- **DynamoDB scan for dashboard KPIs**: Computing "Revenue Today" and "Overdue count" requires scanning or querying across invoices. Mitigation: Use GSI queries (not full table scans); for Revenue Today, query `invoice_status-index` where status=approved and filter by date.

- **Denormalization consistency**: Customer name/phone are denormalized on invoices. If customer updates their info, old invoices show stale data. Mitigation: This is acceptable — invoices are point-in-time financial records and SHOULD reflect the data at time of creation.

- **Invoice number sequence**: `INV-YYYY-NNNN` requires an atomic counter. DynamoDB doesn't have auto-increment. Mitigation: Use a separate DynamoDB item as a counter with conditional write (optimistic locking) or use timestamp-based numbering with collision detection.

- **Lazy overdue check performance**: Computing overdue status at query time adds per-item logic. Mitigation: DynamoDB filter expression can handle date comparison server-side; for dashboard KPIs, a dedicated query with date filter on the GSI SK is efficient enough.

---

## Confidence: 88%

High confidence because:
- Existing codebase patterns are well-established and this follows them exactly
- DynamoDB schema fits within 5 GSI limit per table
- Requirements are extremely detailed leaving little ambiguity
- Target design image confirms the UI structure

Uncertainty factors:
- PDF generation approach (S3 vs inline) needs architect decision
- Invoice number atomicity pattern in DynamoDB (counter item approach assumed)
- Exact integration point with Jobs module (how `job_id` maps to services/parts data) needs verification against actual Job model schema