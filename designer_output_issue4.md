# Designer Output - Issue #4

## Metadata

- **agent**: designer
- **status**: complete
- **confidence**: 82

## Design Document

# Design Document — Job Module (Main Screen, Create Job, Job Detail)

## Requirements Analysis

Build the full Job Module for GarageHQ consisting of three screens:

1. **Jobs Main Screen** — Operational monitoring with category-based filtering, summary cards that act as quick-filters, and a dynamically-columned jobs table.
2. **Create Job Screen** — 6-step stepper/accordion workflow: Customer & Vehicle → Requested Service → Smart Recommendations → Technician Assignment → Cost Estimation → Job Confirmation.
3. **Job Detail Screen** — Full job view with status tracking, delivery monitoring, cost breakdown, and action controls.

## Architecture Overview

**Backend changes:**
- Extend the `work_orders` DynamoDB table with new fields (priority, delivery_status, due_date, service_type, assigned_technician, recommendations, cost_breakdown)
- Create new `service_types` DynamoDB table (reference/lookup data)
- Add new statuses to WorkOrderStatus enum: `waiting_parts`, `delayed`, `closed`
- New endpoints: job summary stats, filtered job listing with dynamic response, service type CRUD, technician availability, recommendation engine
- Extend existing work order create/update endpoints

**React pages/components:**
- `/jobs` — Jobs Main Screen (filter bar, summary cards, dynamic table)
- `/jobs/new` — Create Job (stepper with 6 steps)
- `/jobs/:id` — Job Detail Screen

**DynamoDB changes:**
- Extend `work_orders` table with ~15 new fields
- Add 1 new GSI: `assigned_technician_id-created_at-index` (4th GSI, within limit)
- New `service_types` table with 1 GSI

---

## Components

### Component 1: Backend — Extended Work Order Models

- **Purpose**: Add new Pydantic models and extend existing ones for job module fields
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/work_order.py` (extend)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/service_type.py` (new)

**New/extended models:**

```python
# New status values
class WorkOrderStatus(str, Enum):
    NEW = "new"
    ESTIMATE_CREATED = "estimate_created"
    CUSTOMER_APPROVED = "customer_approved"
    IN_PROGRESS = "in_progress"
    WAITING_PARTS = "waiting_parts"
    DELAYED = "delayed"
    COMPLETED = "completed"
    CLOSED = "closed"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class DeliveryStatus(str, Enum):
    ON_TRACK = "on_track"
    DELAYED = "delayed"
    WAITING_SUPPLIER = "waiting_supplier"
    WAITING_APPROVAL = "waiting_approval"

class Recommendation(BaseModel):
    service_type_id: str
    service_type_name: str
    reason: str  # "overdue_by_mileage", "overdue_by_time", "previous_recommendation"
    status: str  # "pending", "approved", "declined"
    customer_comment: Optional[str] = None

class CostBreakdown(BaseModel):
    labor_cost: Decimal
    parts_cost: Decimal
    vat_percentage: Decimal = Decimal("5")
    vat_amount: Decimal
    total: Decimal

class JobCreateRequest(BaseModel):
    customer_id: str
    vehicle_id: str
    mileage_at_service: int
    service_type_id: str
    customer_complaint: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    assigned_technician_id: str
    due_date: str  # ISO date
    due_time: Optional[str] = None  # HH:MM
    service_advisor_notes: Optional[str] = None
    recommendations: List[Recommendation] = []
    additional_services: List[str] = []  # approved recommendation service_type_ids
    customer_estimate_approved: bool = False

class JobListFilter(BaseModel):
    search_category: Optional[str] = None  # status, technician, service_type, supplier_delay, overdue, priority, customer, vehicle, delivery_status, date_range
    filter_value: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 50
```

**Service Type model (new file):**
```python
class ServiceType(BaseModel):
    service_type_id: str
    name: str
    category: str  # routine_maintenance, repair, inspection, diagnostic
    standard_duration_hours: Decimal
    base_labor_price: Decimal
    required_parts: List[str] = []  # part_ids
    maintenance_interval_km: Optional[int] = None
    maintenance_interval_months: Optional[int] = None
    is_active: bool = True
    created_at: str
    updated_at: str
```

---

### Component 2: Backend — Service Types Repository & Service

- **Purpose**: CRUD for service types reference data + seed strategy
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/service_type_repository.py` (new)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/service_type_service.py` (new)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/service_types.py` (new)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/scripts/seed_service_types.py` (new)

**API endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/service-types` | List all active service types |
| GET | `/api/service-types/<id>` | Get single service type |
| POST | `/api/service-types` | Create (admin only) |
| PUT | `/api/service-types/<id>` | Update (admin only) |

**DynamoDB access pattern:**
- Table: `service_types`
- Primary key: `service_type_id` (HASH)
- GSI: `category-index` (PK: category) — for filtering by category
- List all: scan (small table, <50 records)

**Seed data** (initial service types):
| Name | Category | Duration (hrs) | Base Price |
|------|----------|----------------|------------|
| Oil Change | routine_maintenance | 1.0 | 150 |
| Brake Repair | repair | 2.5 | 450 |
| Tire Rotation | routine_maintenance | 0.5 | 80 |
| Engine Repair | repair | 6.0 | 1200 |
| AC Service | repair | 2.0 | 350 |
| Battery Change | repair | 0.5 | 200 |
| Full Inspection | inspection | 1.5 | 250 |
| Diagnostic Scan | diagnostic | 0.5 | 100 |
| Brake Inspection | inspection | 0.5 | 80 |
| Oil Filter Replacement | routine_maintenance | 0.5 | 60 |
| Air Filter Replacement | routine_maintenance | 0.3 | 50 |
| Transmission Service | repair | 3.0 | 800 |

---

### Component 3: Backend — Extended Job (Work Order) Endpoints

- **Purpose**: New endpoints for job listing with filters, job summary stats, create job (stepper-aware), technician availability, and recommendation engine
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/jobs.py` (new blueprint, registered alongside work_orders)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/job_service.py` (new — orchestrates the full job workflow)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/recommendation_service.py` (new)

**API endpoints:**
| Method | Path | Request | Response | Purpose |
|--------|------|---------|----------|---------|
| GET | `/api/jobs` | `?category=&filter=&date_from=&date_to=&limit=50` | `{ jobs: [...], total: N }` | Filtered job listing |
| GET | `/api/jobs/summary` | — | `{ active: N, in_progress: N, waiting_parts: N, delayed: N, completed: N, closed: N, overdue: N, urgent: N }` | Summary card counts |
| GET | `/api/jobs/<id>` | — | Full job detail | Single job |
| POST | `/api/jobs` | `JobCreateRequest` | Created job | Create job (full stepper data) |
| PUT | `/api/jobs/<id>` | Partial update | Updated job | Update status, delivery, etc. |
| GET | `/api/jobs/technicians/available` | `?date=&duration=` | `[{ user_id, name, current_load, skills }]` | Technician availability |
| GET | `/api/jobs/recommendations` | `?vehicle_id=&mileage=&service_type_id=` | `[{ service_type_id, name, reason }]` | Smart recommendations |
| GET | `/api/jobs/<id>/cost-estimate` | — | `CostBreakdown` | Calculate cost for a job |

**DynamoDB access patterns:**
- List all jobs: scan `work_orders` with FilterExpression (acceptable for single-garage scale <5000 records)
- Filter by status: query `status-created_at-index` with FilterExpression for secondary filters
- Filter by customer: query `customer_id-index`
- Filter by vehicle: query `vehicle_id-index`
- Filter by technician: query new `assigned_technician_id-created_at-index` GSI
- Summary counts: scan with select='COUNT' grouped by status (or maintain a summary item)
- Overdue detection: scan where `due_date < today AND status NOT IN (completed, closed)`

**Recommendation engine logic:**
1. Get vehicle's service history (query work_orders by vehicle_id-index)
2. Get all service types with maintenance intervals
3. For each service type with intervals: check if (current_mileage - last_service_mileage) > interval_km OR (today - last_service_date) > interval_months
4. Return overdue services as recommendations

---

### Component 4: React — Job Types & Service Layer

- **Purpose**: TypeScript interfaces and API service functions for the job module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/job.ts` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/jobService.ts` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/serviceTypeService.ts` (new)

**Key interfaces (job.ts):**
```typescript
interface Job {
  work_order_id: string;
  work_order_number: string;
  customer_id: string;
  customer_name: string;
  vehicle_id: string;
  vehicle: { make: string; model: string; license_plate: string; };
  service_type_id: string;
  service_type_name: string;
  customer_complaint?: string;
  status: JobStatus;
  priority: Priority;
  assigned_technician_id: string;
  assigned_technician_name: string;
  delivery_status: DeliveryStatus;
  due_date: string;
  due_time?: string;
  delay_reason?: string;
  days_overdue?: number;
  estimated_labor_hours: number;
  cost_breakdown?: CostBreakdown;
  recommendations: Recommendation[];
  service_advisor_notes?: string;
  mileage_at_service: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

type SearchCategory = 'status' | 'technician' | 'service_type' | 'supplier_delay' | 'overdue' | 'priority' | 'customer' | 'vehicle' | 'delivery_status' | 'date_range';

interface JobSummary {
  active: number;
  in_progress: number;
  waiting_parts: number;
  delayed: number;
  completed: number;
  closed: number;
  overdue: number;
  urgent: number;
}

interface JobCreateStepData {
  step1: { customer_id: string; vehicle_id: string; mileage_at_service: number; is_new_customer: boolean; };
  step2: { service_type_id: string; customer_complaint?: string; };
  step3: { recommendations: Recommendation[]; };
  step4: { assigned_technician_id: string; due_date: string; due_time?: string; service_advisor_notes?: string; };
  step5: { cost_breakdown: CostBreakdown; customer_estimate_approved: boolean; };
  step6: { confirmed: boolean; send_estimate?: boolean; additional_notes?: string; };
}
```

**Service functions (jobService.ts):**
```typescript
getJobs(params: { category?: string; filter?: string; date_from?: string; date_to?: string; limit?: number }): Promise<{ jobs: Job[]; total: number }>
getJobSummary(): Promise<JobSummary>
getJob(id: string): Promise<Job>
createJob(data: JobCreateRequest): Promise<Job>
updateJob(id: string, data: Partial<Job>): Promise<Job>
getAvailableTechnicians(date: string, duration: number): Promise<Technician[]>
getRecommendations(vehicleId: string, mileage: number, serviceTypeId: string): Promise<Recommendation[]>
getCostEstimate(jobId: string): Promise<CostBreakdown>
```

---

### Component 5: React — Jobs Main Screen

- **Purpose**: The primary job listing screen with filter bar, summary cards, and dynamic table
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/JobsPage.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/JobFilterBar.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/JobSummaryCards.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/JobsTable.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useJobs.ts` (new)

**JobFilterBar** — Search category dropdown + dynamic filter options:
- Category selection triggers dynamic filter options (as per spec)
- Active filters shown as removable chips
- Date range picker for date_range category

**JobSummaryCards** — Row of clickable stat cards:
- Active Jobs, In Progress, Waiting Parts, Delayed, Overdue, Urgent
- Click applies filter to table (sets category=status, filter=value)
- Animated count transitions

**JobsTable** — TanStack Table with dynamic columns:
- Column set changes based on active search category (exact mapping from spec)
- Universal columns shown when no category selected
- Sortable headers, row click navigates to `/jobs/:id`
- Status/priority/delivery_status shown as colored badges
- Pagination (50 per page)

**useJobs hook:**
```typescript
useJobs(filters) → { data, isLoading, refetch } // 60s auto-refresh
useJobSummary() → { data, isLoading }
```

---

### Component 6: React — Create Job Stepper

- **Purpose**: 6-step accordion/stepper workflow for creating a job
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/CreateJobPage.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/JobStepper.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepCustomerVehicle.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepRequestedService.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepRecommendations.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepTechnicianAssignment.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepCostEstimation.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepConfirmation.tsx` (new)

**Stepper behavior:**
- Vertical accordion with step indicators (checkmark/active/locked)
- Only current step is expanded; completed steps show summary
- Forward-only progression (must complete current before next)
- Back navigation allowed (returns to editable state)
- State managed via React useState at CreateJobPage level
- Each step validates before allowing Next

**Step 1 — Customer & Vehicle:**
- Search input (debounced, searches by name or plate number)
- Existing customer: auto-populates all fields, shows vehicle history
- New customer: inline form for manual entry
- Mileage update field (always manual)

**Step 2 — Requested Service:**
- Service type dropdown (from service_types API)
- Customer complaint textarea
- Auto-display: standard duration, pricing (from service type data)

**Step 3 — Smart Recommendations:**
- System calls `/api/jobs/recommendations` with vehicle_id, mileage, service_type_id
- Shows recommended services with reason
- Each has Approve/Decline toggle
- Customer comments field per recommendation

**Step 4 — Technician Assignment:**
- Left panel: Technician dropdown (from availability API), shows status/skills
- Right panel: Delivery date picker + time picker
- Service advisor notes textarea

**Step 5 — Cost Estimation:**
- Auto-calculated breakdown (read-only):
  - Per-service labor cost
  - Parts cost (from approved recommendations + requested service)
  - VAT amount
  - Total
- Customer estimate approval checkbox

**Step 6 — Job Confirmation:**
- Full review summary (all steps collapsed with data)
- Optional: send estimate to customer toggle
- Optional: send confirmation message toggle
- Additional notes textarea
- "Create Job" button (primary action)

---

### Component 7: React — Job Detail Screen

- **Purpose**: Full view of a single job with all details, timeline, and action controls
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/JobDetailPage.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobHeader.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobInfoPanel.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobTimeline.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobCostPanel.tsx` (new)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobActionsPanel.tsx` (new)

**Layout:** 2-column on desktop (info left, actions/timeline right), stacked on mobile.

**JobHeader:** Job number, status badge, priority badge, delivery status badge, due date, action buttons (Edit, Update Status, Print).

**JobInfoPanel:** Customer info, vehicle info, service type, complaint, technician, mileage, recommendations (approved/declined), service advisor notes.

**JobTimeline:** Vertical timeline of status changes with timestamps (created → status transitions → completed). Shows who made each change.

**JobCostPanel:** Breakdown table — labor line items, parts line items, subtotal, VAT, total. Shows approval status.

**JobActionsPanel:** Quick actions: Update Status (dropdown), Update Delivery Status, Mark as Delayed (with reason), Mark Complete.

---

### Component 8: React — Route Integration

- **Purpose**: Register new routes in App.tsx
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx` (modify)

**New routes:**
```tsx
<Route path="/jobs" element={<PrivateRoute><DashboardLayout><JobsPage /></DashboardLayout></PrivateRoute>} />
<Route path="/jobs/new" element={<PrivateRoute><DashboardLayout><CreateJobPage /></DashboardLayout></PrivateRoute>} />
<Route path="/jobs/:id" element={<PrivateRoute><DashboardLayout><JobDetailPage /></DashboardLayout></PrivateRoute>} />
```

---

## DynamoDB Schema Changes

### Table: `work_orders` (EXTENDED)

| Field | Type | Notes |
|-------|------|-------|
| work_order_id | S | PK (existing) |
| **service_type_id** | S | NEW — reference to service_types |
| **service_type_name** | S | NEW — denormalized |
| **customer_complaint** | S | NEW |
| **priority** | S | NEW — low/medium/high/urgent |
| **assigned_technician_id** | S | NEW — primary assigned tech |
| **assigned_technician_name** | S | NEW — denormalized |
| **delivery_status** | S | NEW — on_track/delayed/waiting_supplier/waiting_approval |
| **due_date** | S | NEW — ISO date string |
| **due_time** | S | NEW — HH:MM |
| **delay_reason** | S | NEW |
| **estimated_labor_hours** | N | NEW |
| **service_advisor_notes** | S | NEW |
| **recommendations** | L | NEW — list of recommendation objects |
| **cost_breakdown** | M | NEW — map with labor_cost, parts_cost, vat_percentage, vat_amount, total |
| **customer_estimate_approved** | BOOL | NEW |
| **customer_name** | S | NEW — denormalized for list display |
| **vehicle_info** | M | NEW — denormalized { make, model, license_plate } |

**GSIs (4 of 5 used):**
1. `customer_id-index` — PK: customer_id (existing)
2. `vehicle_id-index` — PK: vehicle_id (existing)
3. `status-created_at-index` — PK: status, SK: created_at (existing)
4. `assigned_technician_id-created_at-index` — PK: assigned_technician_id, SK: created_at (NEW)

**Leaves 1 GSI slot reserved for future use.**

### Table: `service_types` (NEW)

| Field | Type | Notes |
|-------|------|-------|
| service_type_id | S | PK |
| name | S | Display name |
| category | S | routine_maintenance/repair/inspection/diagnostic |
| standard_duration_hours | N | Decimal |
| base_labor_price | N | Decimal |
| required_parts | L | List of part_id strings |
| maintenance_interval_km | N | Optional — for recommendations |
| maintenance_interval_months | N | Optional — for recommendations |
| is_active | BOOL | Soft delete |
| created_at | S | ISO timestamp |
| updated_at | S | ISO timestamp |

**GSIs (1 of 5 used):**
1. `category-index` — PK: category

---

## UX Interaction Flow

### Jobs Main Screen

1. User navigates to `/jobs` → sees page with:
   - Filter bar (empty, showing "Select Search Category" placeholder)
   - Summary cards row (Active: N, In Progress: N, Waiting Parts: N, Delayed: N, Overdue: N, Urgent: N) — data from `/api/jobs/summary`
   - Jobs table showing universal columns (all jobs, sorted by created_at desc)
   - Loading: skeleton cards + skeleton table rows

2. **Summary card click** → User clicks "Delayed (3)":
   - Filter bar auto-populates: Category = "Status", Filter = "Delayed"
   - Table re-fetches with filter applied
   - Table columns switch to Status-category columns
   - Active card gets highlighted border

3. **Manual filter** → User selects "Technician" from category dropdown:
   - Dynamic filter options appear (technician name dropdown, populated from API)
   - User selects "Alex"
   - Table re-fetches, columns switch to Technician-category columns
   - Filter shown as removable chip

4. **Row click** → User clicks a job row → navigates to `/jobs/:id`

5. **Create Job** → User clicks "+ New Job" button → navigates to `/jobs/new`

6. **Error state** → API failure shows toast notification, table shows "Failed to load" with retry button

### Create Job Stepper

1. User lands on `/jobs/new` → sees stepper with Step 1 expanded, Steps 2-6 locked

2. **Step 1** — User types customer name/plate in search:
   - Debounced API call (300ms) searches customers
   - Dropdown shows matching results
   - User selects existing customer → all fields auto-populate (name, phone, email, vehicle list)
   - User selects vehicle → vehicle details populate
   - User enters current mileage
   - Clicks "Next" → Step 1 collapses showing summary, Step 2 expands

3. **Step 2** — User selects service type from dropdown:
   - Standard duration and pricing auto-display below
   - User types customer complaint
   - Clicks "Next"

4. **Step 3** — System auto-fetches recommendations:
   - Loading spinner while fetching
   - Shows list: "Oil Filter Replacement — overdue by 5,000 km"
   - User toggles Approve/Decline for each
   - Clicks "Next"

5. **Step 4** — Technician selection:
   - Dropdown shows available technicians with status badges
   - User selects technician
   - Date picker for delivery date, time picker for time
   - Optional advisor notes
   - Clicks "Next"

6. **Step 5** — System calculates and displays cost:
   - Line items (requested service + approved recommendations)
   - Labor subtotal, parts subtotal, VAT, total
   - Customer estimate approval checkbox
   - Clicks "Next"

7. **Step 6** — Review all data:
   - All steps shown in read-only summary
   - Toggle options: send estimate, send confirmation
   - "Create Job" button
   - On click: loading state on button, API call
   - Success: toast "Job WO-2026-0045 created", redirect to `/jobs/:id`
   - Error: toast with error message, button re-enables

### Job Detail Screen

1. User lands on `/jobs/:id` → sees full job layout:
   - Header: Job number, status/priority/delivery badges, due date
   - Left column: Customer & Vehicle info, Service details, Recommendations, Cost breakdown
   - Right column: Timeline, Quick actions

2. **Update Status** → User clicks status dropdown → selects "In Progress":
   - Confirmation modal
   - API call to update
   - Optimistic update on timeline
   - Status badge updates

3. **Mark Delayed** → User clicks "Mark Delayed":
   - Modal with delay reason textarea
   - On submit: status → delayed, delivery_status → delayed
   - Timeline updates

---

## System Component Assessment

| Component | Required? | Justification |
|---|---|---|
| WebSocket / real-time | NO | 60s TanStack Query polling is sufficient for garage scale. Jobs don't change frequently enough to need push. |
| Background job / queue | NO | All operations (create job, calculate cost, generate recommendations) complete in <1s. No long-running tasks. |
| Cache (Redis) | NO | Service types table is small (<50 rows), scanned infrequently. Job list queries serve a single garage's data. DynamoDB latency is acceptable. |
| File storage (S3) | NO | No file/photo upload in this feature scope. |
| Third-party API | MAYBE | Spec mentions "Send Estimate To Customer" and "Send Confirmation Message" — implies SMS/email. However, these are marked as Optional (M) in the spec, so can be implemented as UI-only placeholders in Phase 1. |
| Search engine | NO | Filtering is category-based with known fields. DynamoDB FilterExpressions are adequate for single-garage volume. |

## Architect Escalation

- **Third-party API (SMS/Email)**: The "Send Estimate" and "Send Confirmation" options in Step 6 imply sending messages to customers. For Phase 1, these will be UI toggles that set flags on the job record. Actual message delivery requires a notification service (e.g., AWS SES for email, Twilio for SMS) and should be designed separately when the Notifications Module is built. **Risk if skipped:** Users see toggle but no message is sent — acceptable for MVP if labeled "Coming Soon" or similar.

---

## Implementation Phases

### Phase 1: Backend Foundation
1. Create `service_types` table + repository + service + routes
2. Run seed script for initial service types
3. Extend `work_orders` table schema (add new GSI via migration)
4. Extend WorkOrderStatus enum + new Pydantic models
5. Create `job_service.py` with list/filter/summary/create/update logic
6. Create `recommendation_service.py`
7. Create `/api/jobs` route blueprint with all endpoints
8. Register blueprint in app factory

### Phase 2: React Service Layer
1. Create `types/job.ts` with all interfaces
2. Create `services/jobService.ts` API functions
3. Create `services/serviceTypeService.ts`
4. Create `hooks/useJobs.ts` with TanStack Query hooks

### Phase 3: React UI — Jobs Main Screen
1. Build `JobFilterBar` component
2. Build `JobSummaryCards` component
3. Build `JobsTable` component with dynamic columns
4. Assemble `JobsPage`
5. Register `/jobs` route

### Phase 4: React UI — Create Job Stepper
1. Build `JobStepper` shell with step state management
2. Build Step 1: StepCustomerVehicle (with customer search)
3. Build Step 2: StepRequestedService
4. Build Step 3: StepRecommendations
5. Build Step 4: StepTechnicianAssignment
6. Build Step 5: StepCostEstimation
7. Build Step 6: StepConfirmation
8. Assemble `CreateJobPage`
9. Register `/jobs/new` route

### Phase 5: React UI — Job Detail Screen
1. Build `JobHeader`
2. Build `JobInfoPanel`
3. Build `JobTimeline`
4. Build `JobCostPanel`
5. Build `JobActionsPanel`
6. Assemble `JobDetailPage`
7. Register `/jobs/:id` route

### Phase 6: Polish & Integration
1. Wire summary card clicks to filter bar
2. Wire AppLayout "New Job" quick action to `/jobs/new`
3. Wire dashboard JobsSnapshot rows to `/jobs/:id`
4. Add loading skeletons, empty states, error boundaries
5. Test end-to-end flow

---

## Risks and Concerns

- **DynamoDB scan performance for filtered job listing**: For a single garage (~1000-5000 active jobs), scan with FilterExpression is acceptable. If multi-tenancy is added later, this needs a tenant-level partition key. Mitigation: use status-created_at-index as primary query path (most users filter by status first), reducing scan scope.

- **Denormalized fields (customer_name, vehicle_info, assigned_technician_name)**: These can drift if customer/vehicle/user records are updated. Mitigation: update denormalized fields on job when source entity changes (add to respective update service methods), or accept eventual staleness since job records are point-in-time.

- **Recommendation engine accuracy**: Simple mileage/time-based rules may produce irrelevant recommendations for vehicles without full service history. Mitigation: show confidence indicator, allow technicians to add/remove recommendations manually.

- **Stepper state loss**: If user navigates away mid-stepper, all progress is lost (client state only). Mitigation: add browser `beforeunload` warning. localStorage draft persistence can be added later if users report frustration.

- **Column count in universal table**: 12 columns may overflow on smaller screens. Mitigation: horizontal scroll with sticky first column (Job ID), and column visibility toggle for users who want fewer columns.

---

## Confidence: 82%

High confidence on architecture and data model — patterns are well-established in the codebase. Moderate uncertainty on:
- Exact DynamoDB scan performance at scale (mitigated by GSI usage for primary queries)
- Whether the spec's "Supplier Delay" filter requires a join to purchase_orders table (designed as a filter on delay_reason field containing supplier-related values, not a cross-table join)
- Whether the "Smart Recommendations" engine needs more sophisticated rules than mileage/time thresholds (designed simple first, extensible later)
- The "Job Detail Screen" spec is sparse ("delivery status, delay duration are additional columns") — designed a full detail page based on data available from create flow