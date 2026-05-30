---
agent: designer
status: complete
confidence: 88
---

# Design Document: Invoice Module (Issue #5)

## Requirements Analysis

Build a centralized invoicing and payment management system for GarageHQ that supports:
- Draft invoice creation from completed jobs
- Manager approval workflow with invoice locking
- Auto-calculated payment status (never manual)
- Payment tracking with full history
- Insurance claim handling (split payments)
- Credit notes for reversals/adjustments
- Data export for accounting/VAT
- Bilingual customer invoice generation (English + Arabic)
- KPI dashboard with alerts and revenue trends

The module integrates with Jobs (services/parts), Customers (details), Inventory (parts cost), and feeds Dashboard (KPIs) and Reports (analytics).

## Architecture Overview

**Backend changes:**
- Extend existing `invoices` DynamoDB table with additional fields (status workflow, insurance, VAT, notes)
- Create 2 new DynamoDB tables: `payments`, `credit_notes`
- Extend existing `app/models/invoice.py` with full Pydantic models
- Create `app/repositories/invoice_repository.py` (extends BaseRepository)
- Create `app/repositories/payment_repository.py`
- Create `app/repositories/credit_note_repository.py`
- Create `app/services/invoice_service.py` (business logic + payment status calculation)
- Create `app/routes/invoices.py` (blueprint with all endpoints)
- Register blueprint in `app/__init__.py` at `/api/invoices`

**React changes:**
- Create invoice module pages: Dashboard, Overview, Detail, PendingPayments, PaymentHistory, CreditNotes, Export
- Create hooks: `useInvoices.ts`, `usePayments.ts`, `useCreditNotes.ts`
- Create services: `invoiceService.ts`
- Create types: `invoice.ts`
- Add routes to `App.tsx`
- Update sidebar navigation in `AppLayout.tsx`

**DynamoDB changes:**
- Extend `invoices` table: add 2 new GSIs (total 5), add ~20 new fields
- New `payments` table: PK `payment_id`, 3 GSIs
- New `credit_notes` table: PK `credit_note_id`, 3 GSIs

---

## Components

### Component 1: Backend — Invoice Data Model

- **Purpose**: Define all Pydantic models for invoice CRUD, validation, and response shapes
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/invoice.py`
- **Dependencies**: `pydantic`, `app.models.common`

**Models to define:**

```python
# Enums
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

# Service line items
class ServiceLineItem(BaseModel):
    service_type: str
    labor_cost: Decimal
    parts_cost: Decimal
    additional_charges: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    vat: Decimal
    total: Decimal
    parts: List[PartLineItem] = []

class PartLineItem(BaseModel):
    part_id: str
    part_name: str
    quantity: int
    unit_price: Decimal
    vat: Decimal
    total: Decimal

# Insurance details
class InsuranceDetails(BaseModel):
    insurance_provider: str
    claim_number: str
    insurance_amount: Decimal
    customer_deductible: Decimal
    insurance_payment_status: InsurancePaymentStatus = InsurancePaymentStatus.PENDING_APPROVAL

# Invoice Create (from job completion)
class InvoiceCreate(BaseModel):
    work_order_id: str
    customer_id: str
    vehicle_id: str
    payer_type: PayerType = PayerType.CUSTOMER
    due_date: Optional[str] = None
    services: List[ServiceLineItem]
    insurance_details: Optional[InsuranceDetails] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None

# Invoice Update (limited fields pre-approval)
class InvoiceUpdate(BaseModel):
    services: Optional[List[ServiceLineItem]] = None
    insurance_details: Optional[InsuranceDetails] = None
    due_date: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    payer_type: Optional[PayerType] = None

# Payment entry
class PaymentCreate(BaseModel):
    invoice_id: str
    amount: Decimal
    payment_method: PaymentMethod
    transaction_reference: Optional[str] = None
    payment_date: str  # ISO date
    notes: Optional[str] = None

# Credit note
class CreditNoteCreate(BaseModel):
    invoice_id: str
    reason: str
    credit_amount: Decimal

# Response models
class InvoiceResponse(BaseModel): ...  # Full invoice with computed fields
class InvoiceListResponse(BaseModel): ...  # Paginated list
class PaymentResponse(BaseModel): ...
class CreditNoteResponse(BaseModel): ...
class InvoiceDashboardResponse(BaseModel): ...  # KPIs + alerts
```

---

### Component 2: Backend — Invoice Repository

- **Purpose**: DynamoDB data access for invoices
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/invoice_repository.py`
- **Dependencies**: `app.repositories.base_repository.BaseRepository`

**DynamoDB access patterns:**

| Operation | Table | Key/GSI | Notes |
|---|---|---|---|
| Get invoice by ID | invoices | PK: `invoice_id` | Primary lookup |
| List by customer | invoices | GSI: `customer_id-index` | Customer's invoices |
| List by work order | invoices | GSI: `work_order_id-index` | Job linkage |
| List by payment status | invoices | GSI: `payment_status-index` | Pending/overdue queries |
| List by invoice status | invoices | GSI: `invoice_status-created_at-index` (NEW) | Draft/approved filtering with date sort |
| Lookup by invoice number | invoices | GSI: `invoice_number-index` (NEW) | Human-readable search |

**Key methods:**
```python
class InvoiceRepository(BaseRepository):
    table_name = "invoices"
    primary_key = "invoice_id"

    def create_invoice(self, data: dict) -> dict
    def get_by_customer(self, customer_id: str) -> List[dict]
    def get_by_work_order(self, work_order_id: str) -> dict
    def get_by_payment_status(self, status: str) -> List[dict]
    def get_by_invoice_status(self, status: str, start_date=None, end_date=None) -> List[dict]
    def get_by_invoice_number(self, invoice_number: str) -> Optional[dict]
    def get_pending_and_overdue(self) -> List[dict]
    def search_invoices(self, query: str, filters: dict) -> List[dict]
```

---

### Component 3: Backend — Payment Repository

- **Purpose**: DynamoDB data access for payment records
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/payment_repository.py`
- **Dependencies**: `app.repositories.base_repository.BaseRepository`

**DynamoDB access patterns:**

| Operation | Table | Key/GSI | Notes |
|---|---|---|---|
| Get payment by ID | payments | PK: `payment_id` | Primary lookup |
| List by invoice | payments | GSI: `invoice_id-payment_date-index` | All payments for an invoice, sorted by date |
| List by date range | payments | GSI: `payment_date-index` | Payment history view |
| List by recorded_by | payments | GSI: `recorded_by-payment_date-index` | Audit trail |

---

### Component 4: Backend — Credit Note Repository

- **Purpose**: DynamoDB data access for credit notes
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/credit_note_repository.py`
- **Dependencies**: `app.repositories.base_repository.BaseRepository`

**DynamoDB access patterns:**

| Operation | Table | Key/GSI | Notes |
|---|---|---|---|
| Get credit note by ID | credit_notes | PK: `credit_note_id` | Primary lookup |
| List by invoice | credit_notes | GSI: `invoice_id-index` | Credit notes linked to invoice |
| List by status | credit_notes | GSI: `status-created_at-index` | Status-based filtering |
| List by customer | credit_notes | GSI: `customer_id-index` | Customer's credit notes |

---

### Component 5: Backend — Invoice Service

- **Purpose**: Business logic for invoice lifecycle, payment status calculation, KPI aggregation
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/invoice_service.py`
- **Dependencies**: `InvoiceRepository`, `PaymentRepository`, `CreditNoteRepository`, `WorkOrderRepository`, `CustomerRepository`

**Key business rules:**

1. **Invoice creation**: Only from completed work orders. Auto-generates `INV-YYYY-NNNN` number.
2. **Invoice locking**: Once approved, no edits allowed (only credit notes).
3. **Payment status auto-calculation**:
   - `pending`: paid_amount == 0 AND remaining_balance > 0
   - `partially_paid`: paid_amount > 0 AND remaining_balance > 0
   - `paid`: remaining_balance == 0
   - `overdue`: due_date passed AND remaining_balance > 0
   - `cancelled`: manually cancelled by manager
4. **Approval flow**: draft → pending_approval → approved (locks invoice)
5. **Payment recording**: Creates payment record, updates invoice paid_amount, recalculates status
6. **Credit note**: Only on approved invoices. Adjusts remaining balance.
7. **Overdue detection**: Cron-like check or on-read calculation comparing due_date to current date.

**Key methods:**
```python
class InvoiceService:
    def create_invoice(self, data: InvoiceCreate, user_id: str) -> Tuple[Optional[dict], Optional[str]]
    def update_invoice(self, invoice_id: str, data: InvoiceUpdate) -> Tuple[Optional[dict], Optional[str]]
    def approve_invoice(self, invoice_id: str, user_id: str) -> Tuple[Optional[dict], Optional[str]]
    def cancel_invoice(self, invoice_id: str, user_id: str) -> Tuple[Optional[dict], Optional[str]]
    def record_payment(self, data: PaymentCreate, user_id: str) -> Tuple[Optional[dict], Optional[str]]
    def create_credit_note(self, data: CreditNoteCreate, user_id: str) -> Tuple[Optional[dict], Optional[str]]
    def get_invoice_dashboard(self) -> dict  # KPIs + alerts
    def get_pending_payments(self) -> List[dict]  # With aging calculation
    def get_payment_history(self, filters: dict) -> List[dict]
    def calculate_payment_status(self, invoice: dict) -> str  # Auto-calculation logic
    def generate_invoice_from_job(self, work_order_id: str) -> Tuple[Optional[dict], Optional[str]]
    def export_invoices(self, export_type: str, filters: dict) -> List[dict]
```

---

### Component 6: Backend — Invoice Routes

- **Purpose**: REST API endpoints for the invoice module
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/invoices.py`
- **Dependencies**: `InvoiceService`, `require_auth`, `require_role`

**Endpoints:**

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/invoices/dashboard` | admin, technician | Invoice dashboard KPIs + alerts |
| GET | `/api/invoices` | admin, technician | List/search invoices with filters |
| POST | `/api/invoices` | admin, technician | Create draft invoice |
| GET | `/api/invoices/<id>` | admin, technician | Get invoice detail |
| PUT | `/api/invoices/<id>` | admin | Update draft invoice |
| POST | `/api/invoices/<id>/approve` | admin | Approve invoice (locks it) |
| POST | `/api/invoices/<id>/cancel` | admin | Cancel invoice |
| POST | `/api/invoices/generate/<work_order_id>` | admin, technician | Generate invoice from completed job |
| GET | `/api/invoices/pending-payments` | admin, technician | Pending payments list |
| POST | `/api/invoices/payments` | admin | Record a payment |
| GET | `/api/invoices/payments/history` | admin, technician | Payment history |
| GET | `/api/invoices/credit-notes` | admin, technician | List credit notes |
| POST | `/api/invoices/credit-notes` | admin | Create credit note |
| GET | `/api/invoices/export/<type>` | admin | Export data (approved, vat, pending, payments) |

**Request/Response shapes:**

```
GET /api/invoices?status=draft&payment_status=pending&search=INV-2026&search_category=invoice_number&start_date=2026-01-01&end_date=2026-05-28&page=1&limit=20

Response: {
  "message": "Invoices retrieved successfully",
  "data": {
    "invoices": [...],
    "total": 45,
    "page": 1,
    "limit": 20
  }
}

GET /api/invoices/dashboard
Response: {
  "message": "Invoice dashboard retrieved",
  "data": {
    "kpis": {
      "revenue_today": { "value": 5200, "change": 12.5 },
      "pending_payments": { "value": 15400, "count": 8 },
      "overdue_invoices": { "value": 3200, "count": 3 },
      "draft_invoices": { "value": 0, "count": 2 }
    },
    "alerts": [
      { "severity": "critical", "type": "overdue", "message": "...", "invoice_id": "..." }
    ],
    "revenue_trend": [
      { "date": "2026-05-21", "revenue": 4800 },
      ...
    ]
  }
}

POST /api/invoices/payments
Request: {
  "invoice_id": "inv_abc123",
  "amount": 500.00,
  "payment_method": "cash",
  "transaction_reference": "TXN-001",
  "payment_date": "2026-05-28",
  "notes": "Partial payment"
}
Response: {
  "message": "Payment recorded successfully",
  "data": { "payment": {...}, "invoice": {...updated status...} }
}
```

---

### Component 7: React — Invoice Types

- **Purpose**: TypeScript type definitions for the invoice module
- **Files**: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/invoice.ts`
- **Dependencies**: None

```typescript
export type InvoiceStatus = 'draft' | 'pending_approval' | 'approved' | 'cancelled'
export type PaymentStatus = 'pending' | 'partially_paid' | 'paid' | 'overdue' | 'cancelled'
export type PayerType = 'customer' | 'insurance' | 'mixed'
export type PaymentMethod = 'cash' | 'card' | 'bank_transfer' | 'insurance_payment' | 'mixed'
export type InsurancePaymentStatus = 'pending_approval' | 'approved' | 'submitted' | 'partially_paid' | 'paid' | 'rejected'

export interface Invoice { ... }
export interface ServiceLineItem { ... }
export interface PartLineItem { ... }
export interface InsuranceDetails { ... }
export interface Payment { ... }
export interface CreditNote { ... }
export interface InvoiceDashboard { ... }
export interface InvoiceKPIs { ... }
export interface PaymentAlert { ... }
```

---

### Component 8: React — Invoice Service Layer

- **Purpose**: API calls for invoice module
- **Files**: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/invoiceService.ts`
- **Dependencies**: `@/services/api`

```typescript
export const invoiceService = {
  getDashboard: () => api.get('/invoices/dashboard'),
  listInvoices: (params) => api.get('/invoices', { params }),
  getInvoice: (id) => api.get(`/invoices/${id}`),
  createInvoice: (data) => api.post('/invoices', data),
  updateInvoice: (id, data) => api.put(`/invoices/${id}`, data),
  approveInvoice: (id) => api.post(`/invoices/${id}/approve`),
  cancelInvoice: (id) => api.post(`/invoices/${id}/cancel`),
  generateFromJob: (workOrderId) => api.post(`/invoices/generate/${workOrderId}`),
  getPendingPayments: () => api.get('/invoices/pending-payments'),
  recordPayment: (data) => api.post('/invoices/payments', data),
  getPaymentHistory: (params) => api.get('/invoices/payments/history', { params }),
  getCreditNotes: (params) => api.get('/invoices/credit-notes', { params }),
  createCreditNote: (data) => api.post('/invoices/credit-notes', data),
  exportData: (type, params) => api.get(`/invoices/export/${type}`, { params, responseType: 'blob' }),
}
```

---

### Component 9: React — Invoice Hooks

- **Purpose**: TanStack Query hooks for data fetching and mutations
- **Files**: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useInvoices.ts`
- **Dependencies**: `@tanstack/react-query`, `@/services/invoiceService`

```typescript
// Queries (all with 60s refetchInterval)
export function useInvoiceDashboard()
export function useInvoices(filters)
export function useInvoice(id)
export function usePendingPayments()
export function usePaymentHistory(filters)
export function useCreditNotes(filters)

// Mutations (all invalidate relevant queries on success)
export function useCreateInvoice()
export function useUpdateInvoice()
export function useApproveInvoice()
export function useCancelInvoice()
export function useGenerateInvoiceFromJob()
export function useRecordPayment()
export function useCreateCreditNote()
```

---

### Component 10: React — Invoice Dashboard Page

- **Purpose**: KPIs, alerts table, and revenue trend chart
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/InvoiceDashboardPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceKpiCards.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/PaymentAlertTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/RevenueTrendChart.tsx`
- **Dependencies**: `useInvoiceDashboard`, Recharts, TanStack Table

---

### Component 11: React — Invoice Overview Page

- **Purpose**: Filterable/searchable invoice list with quick actions
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/InvoiceOverviewPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceFilterBar.tsx`
- **Dependencies**: `useInvoices`, TanStack Table

**Table columns**: Invoice No, Customer, Payer Type, Primary Service, Payment Status, Grand Total, Insurance Amount, Customer Amount, Remaining Balance, Due Date, Aging, Quick Actions

**Filter bar**: Search category dropdown, text search, status filter, date range (start/end), export button

**Quick actions dropdown per row**: Approve Invoice, Cancel Invoice, Open Invoice Details

---

### Component 12: React — Invoice Detail Page

- **Purpose**: Full invoice workspace with services, parts, insurance, payments, notes, and action bar
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/InvoiceDetailPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/InvoiceHeader.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/CustomerVehicleDetails.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/InsuranceSummary.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/ServicesCostTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/PaymentSummary.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/InvoiceNotes.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/detail/InvoiceActionBar.tsx`
- **Dependencies**: `useInvoice`, `useApproveInvoice`, `useCancelInvoice`

---

### Component 13: React — Pending Payments Page

- **Purpose**: Outstanding payments with summary cards and record payment modal
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/PendingPaymentsPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/PendingPaymentsTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/RecordPaymentModal.tsx`
- **Dependencies**: `usePendingPayments`, `useRecordPayment`, TanStack Table

**Summary cards**: Total Outstanding, Overdue Amount, Insurance Pending

**Table columns**: Invoice No, Customer, Payer, Phone, Due Date, Aging Days, Grand Total, Paid Amount, Remaining Balance, Quick Actions

**Quick actions**: Record Payment, Send Reminder, Open Invoice Details

---

### Component 14: React — Payment History Page

- **Purpose**: Audit trail of all recorded payments
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/PaymentHistoryPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/PaymentHistoryTable.tsx`
- **Dependencies**: `usePaymentHistory`, TanStack Table

**Table columns**: Payment Date, Invoice No, Customer, Payment Method, Transaction Reference, Amount Paid, Recorded By

---

### Component 15: React — Credit Notes Page

- **Purpose**: List and create credit notes for invoice reversals/adjustments
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/CreditNotesPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/CreditNotesTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/CreateCreditNoteModal.tsx`
- **Dependencies**: `useCreditNotes`, `useCreateCreditNote`, TanStack Table

**Table columns**: Credit Note No, Invoice No, Customer, Reason, Credit Amount, Created Date, Status

---

### Component 16: React — Invoice Export Page

- **Purpose**: Export-ready financial data with type selection
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/InvoiceExportPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/ExportTypeSelector.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/ExportPreviewTable.tsx`
- **Dependencies**: `invoiceService.exportData`

**Export types**: Approved Invoices, VAT Export, Pending Payments, Payment History

**Flow**: Select type → Table loads preview → Review data → Export button (Excel/CSV/PDF)

---

### Component 17: React — Invoice Module Layout

- **Purpose**: Module-level sidebar navigation for invoice sub-pages
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/invoices/InvoiceLayout.tsx`
- **Dependencies**: React Router Outlet

**Sidebar items**:
- Invoice Dashboard (`/invoices`)
- Invoice Overview (`/invoices/overview`)
- Pending Payments (`/invoices/pending-payments`)
- Payment History (`/invoices/payment-history`)
- Credit Notes (`/invoices/credit-notes`)
- Invoice Export (`/invoices/export`)

---

## DynamoDB Schema Changes

### Table: `invoices` (EXISTING — extend)

**Primary Key**: `invoice_id` (String)

**GSIs (5 total — at max):**
| # | GSI Name | Partition Key | Sort Key | Status |
|---|---|---|---|---|
| 1 | `customer_id-index` | `customer_id` | — | EXISTS |
| 2 | `work_order_id-index` | `work_order_id` | — | EXISTS |
| 3 | `payment_status-index` | `payment_status` | — | EXISTS |
| 4 | `invoice_status-created_at-index` | `invoice_status` | `created_at` | **NEW** |
| 5 | `invoice_number-index` | `invoice_number` | — | **NEW** |

**New fields added to invoice items:**
```
invoice_number: str          # "INV-2026-0001" (human-readable, unique)
invoice_status: str          # draft | pending_approval | approved | cancelled
payment_status: str          # pending | partially_paid | paid | overdue | cancelled (auto-calculated)
payer_type: str              # customer | insurance | mixed
customer_id: str             # FK to customers table
vehicle_id: str              # FK to vehicles table
work_order_id: str           # FK to work_orders table

# Financial fields
services: List[dict]         # Service line items with nested parts
subtotal: Decimal
vat_rate: Decimal            # e.g., 0.05 for 5%
vat_amount: Decimal
grand_total: Decimal
paid_amount: Decimal         # Sum of all payments
remaining_balance: Decimal   # grand_total - paid_amount - credit_total
insurance_amount: Decimal    # Portion covered by insurance
customer_amount: Decimal     # Portion payable by customer

# Insurance
insurance_details: dict      # InsuranceDetails object (provider, claim, amounts, status)

# Dates
invoice_date: str            # ISO date
due_date: str                # ISO date
approved_at: str             # ISO datetime (null if not approved)
cancelled_at: str            # ISO datetime (null if not cancelled)

# Notes
internal_notes: str          # Not visible to customer
customer_notes: str          # Visible on customer invoice

# Audit
created_by: str              # user_id who created
approved_by: str             # user_id who approved
cancelled_by: str            # user_id who cancelled

# Denormalized for list views (avoid joins)
customer_name: str
vehicle_display: str         # "Make Model (Plate)"
primary_service: str         # Main service type name
```

---

### Table: `payments` (NEW)

**Primary Key**: `payment_id` (String)

**GSIs (3 total):**
| # | GSI Name | Partition Key | Sort Key |
|---|---|---|---|
| 1 | `invoice_id-payment_date-index` | `invoice_id` | `payment_date` |
| 2 | `payment_date-index` | `payment_date` | `created_at` |
| 3 | `recorded_by-payment_date-index` | `recorded_by` | `payment_date` |

**Fields:**
```
payment_id: str              # "pay_hexstring"
invoice_id: str              # FK to invoices
customer_id: str             # Denormalized for reporting
invoice_number: str          # Denormalized for display
customer_name: str           # Denormalized for display
amount: Decimal
payment_method: str          # cash | card | bank_transfer | insurance_payment | mixed
transaction_reference: str
payment_date: str            # ISO date (user-entered date of payment)
notes: str
recorded_by: str             # user_id
recorded_by_name: str        # Denormalized username
created_at: str              # ISO datetime (system timestamp)
updated_at: str
```

---

### Table: `credit_notes` (NEW)

**Primary Key**: `credit_note_id` (String)

**GSIs (3 total):**
| # | GSI Name | Partition Key | Sort Key |
|---|---|---|---|
| 1 | `invoice_id-index` | `invoice_id` | — |
| 2 | `status-created_at-index` | `status` | `created_at` |
| 3 | `customer_id-index` | `customer_id` | — |

**Fields:**
```
credit_note_id: str          # "cn_hexstring"
credit_note_number: str      # "CN-2026-0001"
invoice_id: str              # FK to invoices
invoice_number: str          # Denormalized
customer_id: str             # FK to customers
customer_name: str           # Denormalized
reason: str
credit_amount: Decimal
status: str                  # draft | approved | applied | cancelled
created_by: str              # user_id
created_at: str
updated_at: str
```

---

## UX Interaction Flow

### Flow 1: Invoice Dashboard
1. User clicks "Invoices" in main sidebar → lands on Invoice Dashboard (`/invoices`)
2. Module sub-sidebar appears on left showing: Dashboard, Overview, Pending Payments, Payment History, Credit Notes, Export
3. Dashboard loads → shows 4 KPI cards (Revenue Today, Pending Payments, Overdue Invoices, Draft Invoices) with loading skeletons
4. Below KPIs: Payment Alert Table with severity badges (red/yellow) and clickable invoice links
5. Below alerts: Revenue Trend Line Chart (daily/weekly toggle)
6. Auto-refreshes every 60s via TanStack Query

### Flow 2: Invoice Overview (List + Quick Actions)
1. User clicks "Invoice Overview" in module sidebar → navigates to `/invoices/overview`
2. Page loads: filter bar on top (search category dropdown, text input, status filter, date range), table below
3. Table shows all invoices with loading skeleton → data populates
4. User selects search category "Invoice Number" → types "INV-2026" → table filters live
5. User selects filter "Overdue" → table shows only overdue invoices
6. User clicks "..." quick actions on a row → dropdown: Approve Invoice, Cancel Invoice, Open Details
7. User clicks "Approve Invoice" → confirmation modal → on confirm: API call → invoice status updates → row refreshes
8. **Entire row is clickable** → clicking anywhere navigates to Invoice Detail

### Flow 3: Invoice Detail Screen
1. User clicks invoice row → navigates to `/invoices/:id`
2. Page loads with sections: Header, Customer & Vehicle, Insurance (if applicable), Services & Cost Table, Payment Summary, Notes, Action Bar
3. **Services table**: expandable rows. User clicks expand arrow → parts used in that service appear in nested table
4. **Action Bar** (bottom sticky): Language selector (English / English + Arabic), Download PDF, Print Invoice, Send WhatsApp
5. If invoice is in "draft" status: edit fields are enabled
6. If invoice is "approved": all fields are read-only (locked), action bar is fully active

### Flow 4: Record Payment
1. User navigates to Pending Payments (`/invoices/pending-payments`)
2. Summary cards load: Total Outstanding ($15,400), Overdue Amount ($3,200), Insurance Pending ($8,500)
3. Table shows all pending/overdue invoices with aging days calculated
4. User clicks "Record Payment" quick action on a row → Modal opens
5. Modal pre-fills Invoice No (read-only) → user enters: Amount, Payment Method (dropdown), Transaction Reference, Payment Date (date picker), Notes
6. User clicks "Save" → API call → on success: toast "Payment recorded", modal closes
7. Invoice's paid_amount recalculated → payment_status auto-updates → row refreshes
8. If remaining_balance == 0: invoice disappears from pending payments list
9. **Error path**: If amount > remaining_balance → inline validation "Amount exceeds remaining balance"

### Flow 5: Invoice Generation from Job
1. In Job Detail Screen → job status is "completed" → "Generate Invoice" button appears
2. User clicks "Generate Invoice" → API call to `/api/invoices/generate/<work_order_id>`
3. System creates draft invoice pulling: services, parts, labor from work order; customer & vehicle details
4. Success → redirects to Invoice Detail page with new draft invoice
5. Manager reviews services/parts/amounts → can edit if in draft
6. Manager clicks "Submit for Approval" → invoice_status changes to pending_approval

### Flow 6: Export
1. User navigates to Invoice Export (`/invoices/export`)
2. Sees 4 export type cards: Approved Invoices, VAT Export, Pending Payments, Payment History
3. User clicks "Approved Invoices" → table loads preview of export data
4. User reviews → clicks "Export" → dropdown: Excel, CSV, PDF
5. File downloads

### Empty States
- Invoice Overview with no invoices: "No invoices yet. Generate your first invoice from a completed job."
- Pending Payments with nothing pending: "All caught up! No outstanding payments."
- Payment History empty: "No payments recorded yet."

### Loading States
- All pages use skeleton loaders matching the layout (same as existing jobs/dashboard pattern)
- KPI cards show animated pulse skeleton
- Tables show row skeletons (5 rows)

---

## System Component Assessment

| Component | Required? | Justification |
|---|---|---|
| WebSocket / real-time | NO | 60s auto-refresh via TanStack Query is sufficient. Invoices are not updated frequently enough to justify WebSocket. |
| Background job / queue | MAYBE | Overdue status detection could be a scheduled job (daily). However, can be done on-read: check due_date vs current date when fetching. On-read is simpler and acceptable for MVP. |
| Cache (Redis) | NO | Invoice dashboard KPIs are not fetched >10x/min by same user. DynamoDB reads are fast enough. |
| File storage (S3) | MAYBE | PDF generation of customer invoices. However, PDFs can be generated on-demand client-side (react-pdf or server-side with WeasyPrint). No need to store permanently unless required. |
| Third-party API | MAYBE | WhatsApp sharing mentioned in requirements. Could use WhatsApp Web URL scheme (`https://wa.me/?text=`) for MVP instead of official API. No SMS/email needed for MVP. |
| Search engine | NO | Invoice search is bounded (filters + GSI queries). Full-text search across all fields is not required. |

## Architect Escalation

- **Background job (overdue detection)**: For MVP, calculate overdue status on-read by comparing `due_date` to current date in the service layer. This avoids needing a job queue. If invoice volume grows >10,000, consider a nightly Lambda to batch-update overdue statuses. **Risk if skipped**: None for MVP volumes. On-read adds negligible latency.

- **File storage (PDF generation)**: For MVP, generate PDFs on-demand in the browser using a library like `@react-pdf/renderer` for the bilingual customer invoice template. PDFs are not stored — generated fresh each time. **Risk if skipped**: Cannot pre-generate PDFs for batch processing or link sharing. Acceptable for MVP. **Proposed approach**: Client-side PDF generation with `@react-pdf/renderer`, supporting RTL Arabic text.

- **WhatsApp sharing**: For MVP, use the WhatsApp Web share URL scheme: `https://wa.me/?text={encoded_message}`. This opens WhatsApp with pre-filled text containing invoice summary. No WhatsApp Business API integration needed. **Risk if skipped**: Cannot send PDFs directly via WhatsApp API. User must manually attach. Acceptable for MVP.

---

## Implementation Phases

### Phase 1: Backend Foundation
1. Extend `app/models/invoice.py` with full Pydantic models (enums, request/response shapes)
2. Create `app/repositories/invoice_repository.py`
3. Create `app/repositories/payment_repository.py`
4. Create `app/repositories/credit_note_repository.py`
5. Create `app/services/invoice_service.py` with all business logic
6. Create `app/routes/invoices.py` with all endpoints
7. Register blueprint in `app/__init__.py`
8. Update `scripts/init_db.py` to create `payments` and `credit_notes` tables + new GSIs on `invoices`
9. Create seed data script for test invoices

### Phase 2: React Service Layer
1. Create `src/types/invoice.ts`
2. Create `src/services/invoiceService.ts`
3. Create `src/hooks/useInvoices.ts`
4. Add routes to `src/App.tsx`
5. Update sidebar in `AppLayout.tsx`

### Phase 3: React UI — Core Pages
1. `InvoiceLayout.tsx` (module sub-sidebar)
2. `InvoiceDashboardPage.tsx` + KPI cards + alerts table + revenue chart
3. `InvoiceOverviewPage.tsx` + filter bar + table with quick actions
4. `InvoiceDetailPage.tsx` + all detail sub-components

### Phase 4: React UI — Payment & Credit
1. `PendingPaymentsPage.tsx` + summary cards + table + record payment modal
2. `PaymentHistoryPage.tsx` + table
3. `CreditNotesPage.tsx` + table + create modal

### Phase 5: React UI — Export & PDF
1. `InvoiceExportPage.tsx` + type selector + preview tables + download
2. Customer invoice PDF template (bilingual English + Arabic) using `@react-pdf/renderer`
3. WhatsApp share integration (URL scheme)

---

## Risks and Concerns

1. **DynamoDB GSI limit on invoices table (5 max)**: Using all 5 GSIs. If additional query patterns emerge, must use scan + client-side filtering or restructure. **Mitigation**: Current 5 GSIs cover all required access patterns.

2. **Payment status consistency**: On-read overdue calculation means the `payment_status` field in DynamoDB may show "pending" when it should be "overdue". GSI queries on `payment_status-index` for "overdue" won't work unless we update the field. **Mitigation**: Run overdue check in `get_pending_payments()` and `list_invoices()` service methods. Update the DynamoDB record in-place when overdue detected (lazy update pattern). GSI will then reflect correct status.

3. **Bilingual PDF (Arabic RTL)**: `@react-pdf/renderer` has limited RTL support. **Mitigation**: Use explicit RTL styling with `direction: 'rtl'` and test with Arabic fonts. Fallback: use server-side WeasyPrint with proper Arabic font support if client-side is insufficient.

4. **Invoice number uniqueness**: `INV-YYYY-NNNN` format requires an atomic counter. **Mitigation**: Use DynamoDB conditional write with a `counters` table (PK: `counter_name`, field: `current_value`). Increment atomically with `ADD` expression. Same pattern used for work orders (`WO-YYYY-NNNN`).

5. **Data denormalization staleness**: Customer name, vehicle display stored on invoice. If customer updates their name, old invoices show old name. **Mitigation**: Acceptable — invoices are point-in-time documents. The name at time of invoicing is the correct name for that invoice.

6. **Export file size**: Large exports (1000+ invoices) could be slow client-side. **Mitigation**: Server generates CSV/Excel as stream. For MVP, client-side export with a 500-record limit is acceptable.

---

## Confidence: 88%

High confidence because:
- Existing patterns (repos, routes, services, hooks) are well-established and consistent
- Invoice table already exists with 3 GSIs — extending is straightforward
- Requirements are extremely detailed — minimal ambiguity
- Similar financial patterns already exist (purchase orders, work order cost tracking)

Reduced from 100% because:
- Bilingual PDF (Arabic RTL) is a known complexity area that may need iteration
- WhatsApp integration details depend on customer's WhatsApp setup
- Overdue lazy-update pattern needs careful testing to avoid race conditions
- Counter-based invoice numbering needs DynamoDB conditional write testing
