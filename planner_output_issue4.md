# Planner Output - Issue #4

## Metadata

- **agent**: planner
- **status**: complete
- **confidence**: 88

## Execution Plan

# Execution Plan

## Task Breakdown

### Task 1: Fix Missing `role-index` GSI on Users Table (Architect Blocker)
- **ID**: task_1
- **Description**: Add `role-index` GSI to the `users` table in `init_db.py`. This is a pre-existing bug identified by the architect — the `user_repository.py` already references `get_users_by_role()` using this GSI, but it was never created. Required before technician availability endpoint can work.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/db/init_db.py` (modify — add role-index GSI definition to users table)
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 2: Create `service_types` DynamoDB Table Schema
- **ID**: task_2
- **Description**: Add `service_types` table creation to `init_db.py` with PK `service_type_id` and one GSI `category-index` (PK: category). Follow existing table creation patterns in the file.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/db/init_db.py` (modify — add service_types table definition)
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: add_database_model.yaml
- **Approach**: deterministic

### Task 3: Add `assigned_technician_id-created_at-index` GSI to Work Orders Table
- **ID**: task_3
- **Description**: Add the 4th GSI to `work_orders` table in `init_db.py`. PK: `assigned_technician_id`, SK: `created_at`. This enables filtering jobs by assigned technician.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/db/init_db.py` (modify — add GSI to work_orders table)
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: add_database_model.yaml
- **Approach**: deterministic

### Task 4: Extend Work Order Pydantic Models + New Enums
- **ID**: task_4
- **Description**: Extend `WorkOrderStatus` enum with `waiting_parts`, `delayed`, `closed`. Add new enums: `Priority`, `DeliveryStatus`. Add new models: `Recommendation`, `CostBreakdown`, `JobCreateRequest`, `JobListFilter`. All new fields must be `Optional` for backward compatibility with existing records (Architect Warning 1).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/work_order.py` (extend)
- **Dependencies**: []
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 5: Create Service Type Model
- **ID**: task_5
- **Description**: Create new Pydantic model file for `ServiceType` with all fields from design (service_type_id, name, category, standard_duration_hours, base_labor_price, required_parts, maintenance_interval_km, maintenance_interval_months, is_active, created_at, updated_at).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/service_type.py` (new)
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: add_database_model.yaml
- **Approach**: deterministic

### Task 6: Create Service Type Repository
- **ID**: task_6
- **Description**: CRUD repository for `service_types` table. Methods: `create()`, `get_by_id()`, `list_all_active()`, `list_by_category()`, `update()`. Follow patterns from existing repositories (e.g., `work_order_repository.py`). Use scan for list_all (table <50 records), GSI query for list_by_category.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/service_type_repository.py` (new)
- **Dependencies**: [task_2, task_5]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 7: Create Service Type Service
- **ID**: task_7
- **Description**: Business logic layer for service types. Methods: `create_service_type()`, `get_service_type()`, `list_service_types()`, `update_service_type()`. Thin wrapper over repository with validation.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/service_type_service.py` (new)
- **Dependencies**: [task_6]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 8: Create Service Type Routes
- **ID**: task_8
- **Description**: Flask blueprint with 4 endpoints: GET `/api/service-types` (list active), GET `/api/service-types/<id>`, POST `/api/service-types` (admin only), PUT `/api/service-types/<id>` (admin only). Register blueprint in app factory.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/service_types.py` (new)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py` (modify — register blueprint)
- **Dependencies**: [task_7]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 9: Create Service Types Seed Script
- **ID**: task_9
- **Description**: Script to seed 12 initial service types (Oil Change, Brake Repair, Tire Rotation, etc.) with categories, durations, and base prices as specified in design. Idempotent — check if exists before inserting.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/scripts/seed_service_types.py` (new)
- **Dependencies**: [task_6]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 10: Create Recommendation Service
- **ID**: task_10
- **Description**: Implements smart recommendation engine. Logic: (1) Get vehicle's service history from work_orders by vehicle_id-index, (2) Get all service types with maintenance intervals, (3) For each service type with intervals, check if (current_mileage - last_service_mileage) > interval_km OR (today - last_service_date) > interval_months, (4) Return overdue services as recommendations.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/recommendation_service.py` (new)
- **Dependencies**: [task_4, task_6]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 11: Create Job Service
- **ID**: task_11
- **Description**: Orchestrates job workflow. Methods: `list_jobs()` (use status-created_at-index as primary query path with FilterExpression for secondary filters — Architect Warning 5), `get_job_summary()` (full scan with client-side grouping — Architect Warning 2), `get_job()`, `create_job()`, `update_job()`, `get_available_technicians()` (uses role-index GSI from task_1), `calculate_cost_estimate()`. Handle backward compatibility: old records missing new fields should return gracefully with defaults/None.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/job_service.py` (new)
- **Dependencies**: [task_1, task_4, task_6, task_10]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 12: Create Jobs Route Blueprint
- **ID**: task_12
- **Description**: New Flask blueprint `/api/jobs` with all endpoints: GET `/api/jobs` (filtered listing), GET `/api/jobs/summary` (card counts), GET `/api/jobs/<id>` (detail), POST `/api/jobs` (create), PUT `/api/jobs/<id>` (update), GET `/api/jobs/technicians/available`, GET `/api/jobs/recommendations`, GET `/api/jobs/<id>/cost-estimate`. Register in app factory. Document that `/api/jobs` is the "v2" view while `/api/work-orders` remains for existing integrations (Architect Warning 4).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/jobs.py` (new)
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py` (modify — register jobs blueprint)
- **Dependencies**: [task_11]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 13: Create React TypeScript Interfaces
- **ID**: task_13
- **Description**: Create `types/job.ts` with all TypeScript interfaces: `Job`, `JobStatus`, `Priority`, `DeliveryStatus`, `Recommendation`, `CostBreakdown`, `JobSummary`, `JobCreateStepData`, `SearchCategory`, `Technician`, `ServiceType`. This establishes a new `types/` directory convention (Architect Warning 3). All new fields on Job interface should be optional (`?`) for backward compatibility.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/job.ts` (new)
- **Dependencies**: []
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 14: Create Job API Service Functions
- **ID**: task_14
- **Description**: API service layer with functions: `getJobs()`, `getJobSummary()`, `getJob()`, `createJob()`, `updateJob()`, `getAvailableTechnicians()`, `getRecommendations()`, `getCostEstimate()`. Follow existing service patterns in the codebase (e.g., axios/fetch wrapper usage).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/jobService.ts` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 15: Create Service Type API Service Functions
- **ID**: task_15
- **Description**: API service for service types: `getServiceTypes()`, `getServiceType()`. Minimal — only read operations needed by frontend.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/serviceTypeService.ts` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 16: Create useJobs TanStack Query Hooks
- **ID**: task_16
- **Description**: Custom hooks wrapping TanStack Query: `useJobs(filters)` with 60s auto-refresh, `useJobSummary()`, `useJob(id)`, `useCreateJob()`, `useUpdateJob()`, `useAvailableTechnicians(date, duration)`, `useRecommendations(vehicleId, mileage, serviceTypeId)`, `useServiceTypes()`.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useJobs.ts` (new)
- **Dependencies**: [task_14, task_15]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 17: Build JobFilterBar Component
- **ID**: task_17
- **Description**: Search category dropdown with dynamic filter options. Category selection triggers context-specific filter inputs (status dropdown, technician dropdown, date range picker, etc.). Active filters shown as removable chips. Populates from API for technician/service_type categories.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/JobFilterBar.tsx` (new)
- **Dependencies**: [task_16]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 18: Build JobSummaryCards Component
- **ID**: task_18
- **Description**: Row of clickable stat cards (Active, In Progress, Waiting Parts, Delayed, Overdue, Urgent). Each card shows count from summary API. Click applies filter to table. Animated count transitions. Highlighted border on active card. Loading: skeleton cards.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/JobSummaryCards.tsx` (new)
- **Dependencies**: [task_16]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 19: Build JobsTable Component
- **ID**: task_19
- **Description**: TanStack Table with dynamic column sets based on active search category. Universal columns when no filter. Sortable headers. Row click navigates to `/jobs/:id`. Status/priority/delivery_status as colored badges. Pagination (50/page). Horizontal scroll with sticky first column for overflow (Architect Warning re: 12 columns). Handle null values gracefully for old records — show "—" or "Unassigned".
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/JobsTable.tsx` (new)
- **Dependencies**: [task_16]
- **Estimated Effort**: high
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 20: Assemble JobsPage
- **ID**: task_20
- **Description**: Main jobs page composing JobFilterBar, JobSummaryCards, and JobsTable. Wire summary card clicks to filter bar state. "+ New Job" button navigating to `/jobs/new`. Error state with toast + retry. Loading skeletons.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/JobsPage.tsx` (new)
- **Dependencies**: [task_17, task_18, task_19]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 21: Build JobStepper Shell
- **ID**: task_21
- **Description**: Vertical accordion with 6 step indicators (checkmark/active/locked). Only current step expanded. Forward-only progression with back navigation. State managed via useState at parent level. Each step validates before allowing Next. `beforeunload` warning to prevent accidental navigation loss.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/JobStepper.tsx` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 22: Build Step 1 — Customer & Vehicle
- **ID**: task_22
- **Description**: Debounced search input (300ms) searching customers by name/plate. Existing customer: auto-populates fields + shows vehicle history. New customer: inline form. Vehicle selection. Mileage input (always manual). Validates: customer selected, vehicle selected, mileage entered.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepCustomerVehicle.tsx` (new)
- **Dependencies**: [task_16, task_21]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 23: Build Step 2 — Requested Service
- **ID**: task_23
- **Description**: Service type dropdown (from `useServiceTypes` hook). Customer complaint textarea. Auto-display standard duration and pricing from selected service type. Validates: service type selected.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepRequestedService.tsx` (new)
- **Dependencies**: [task_16, task_21]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 24: Build Step 3 — Smart Recommendations
- **ID**: task_24
- **Description**: Auto-fetches recommendations from API using vehicle_id + mileage + service_type_id from previous steps. Loading spinner while fetching. Displays recommendation list with reasons. Each has Approve/Decline toggle. Customer comments field per recommendation. Validates: all recommendations have a decision.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepRecommendations.tsx` (new)
- **Dependencies**: [task_16, task_21]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 25: Build Step 4 — Technician Assignment
- **ID**: task_25
- **Description**: Left panel: Technician dropdown from availability API with status/skills badges. Right panel: Delivery date picker + time picker. Service advisor notes textarea. Validates: technician selected, due_date set.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepTechnicianAssignment.tsx` (new)
- **Dependencies**: [task_16, task_21]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 26: Build Step 5 — Cost Estimation
- **ID**: task_26
- **Description**: Auto-calculated cost breakdown (read-only): per-service labor cost, parts cost, VAT (5%), total. Shows line items for requested service + approved recommendations. Customer estimate approval checkbox. Validates: implicitly valid (read-only display).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepCostEstimation.tsx` (new)
- **Dependencies**: [task_16, task_21]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 27: Build Step 6 — Job Confirmation
- **ID**: task_27
- **Description**: Full review summary (all steps in read-only). Optional toggles: send estimate to customer (labeled "Coming Soon"), send confirmation message (labeled "Coming Soon") — per Architect's directive to NOT build placeholder send logic. Additional notes textarea. "Create Job" button with loading state. Success: toast + redirect to `/jobs/:id`. Error: toast + re-enable button.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/create/StepConfirmation.tsx` (new)
- **Dependencies**: [task_16, task_21]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 28: Assemble CreateJobPage
- **ID**: task_28
- **Description**: Parent page managing all stepper state via useState (`JobCreateStepData`). Passes step data down to each step component. Handles form submission via `useCreateJob` mutation. Coordinates inter-step data flow (e.g., step 3 needs vehicle_id from step 1).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/CreateJobPage.tsx` (new)
- **Dependencies**: [task_22, task_23, task_24, task_25, task_26, task_27]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 29: Build JobHeader Component
- **ID**: task_29
- **Description**: Job number display, status/priority/delivery badges (colored), due date, action buttons (Edit, Update Status, Print). Responsive layout.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobHeader.tsx` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 30: Build JobInfoPanel Component
- **ID**: task_30
- **Description**: Customer info, vehicle info, service type, complaint, assigned technician, mileage, recommendations (approved/declined list), service advisor notes. Handle null fields gracefully for backward compatibility.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobInfoPanel.tsx` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 31: Build JobTimeline Component
- **ID**: task_31
- **Description**: Vertical timeline of status changes with timestamps (created → transitions → completed). Shows who made each change. Derives from job's status history/audit trail.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobTimeline.tsx` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 32: Build JobCostPanel Component
- **ID**: task_32
- **Description**: Cost breakdown table — labor line items, parts line items, subtotal, VAT, total. Shows approval status. Handles case where cost_breakdown is null (old records).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobCostPanel.tsx` (new)
- **Dependencies**: [task_13]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 33: Build JobActionsPanel Component
- **ID**: task_33
- **Description**: Quick actions: Update Status (dropdown with confirmation modal), Update Delivery Status, Mark as Delayed (modal with reason textarea), Mark Complete. Uses `useUpdateJob` mutation.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/jobs/detail/JobActionsPanel.tsx` (new)
- **Dependencies**: [task_16]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 34: Assemble JobDetailPage
- **ID**: task_34
- **Description**: 2-column layout on desktop (info left, actions/timeline right), stacked on mobile. Uses `useJob(id)` hook. Composes all detail sub-components. Handles loading/error states.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/JobDetailPage.tsx` (new)
- **Dependencies**: [task_29, task_30, task_31, task_32, task_33]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 35: Register Routes in App.tsx
- **ID**: task_35
- **Description**: Add 3 new routes to App.tsx: `/jobs` → JobsPage, `/jobs/new` → CreateJobPage, `/jobs/:id` → JobDetailPage. All wrapped in PrivateRoute + DashboardLayout. Import all page components.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx` (modify)
- **Dependencies**: [task_20, task_28, task_34]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 36: Polish & Integration Wiring
- **ID**: task_36
- **Description**: Wire AppLayout "New Job" quick action button to `/jobs/new`. Wire dashboard JobsSnapshot rows (if they exist) to link to `/jobs/:id`. Add loading skeletons to all pages. Add empty states ("No jobs found" with illustration). Add error boundaries around each page.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx` (modify if needed)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/JobsPage.tsx` (modify — add empty state)
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/layout/` (modify — add New Job action if applicable)
- **Dependencies**: [task_35]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

---

## Execution Strategy

**Parallel Groups**:

- **Group 1** (Backend DB + Models — all independent): [task_1, task_2, task_3, task_4, task_5, task_13]
- **Group 2** (Backend Service Types + Recommendation deps): [task_6, task_9] (depend on Group 1)
- **Group 3** (Backend Services layer): [task_7, task_10] (depend on Group 2)
- **Group 4** (Backend Routes + Frontend Services): [task_8, task_11, task_14, task_15] (depend on Group 3)
- **Group 5** (Backend Jobs Route + Frontend Hooks): [task_12, task_16] (depend on Group 4)
- **Group 6** (React UI Components — parallel within): [task_17, task_18, task_19, task_21, task_29, task_30, task_31, task_32, task_33] (depend on Group 5)
- **Group 7** (Stepper Steps — parallel): [task_22, task_23, task_24, task_25, task_26, task_27] (depend on task_21 from Group 6)
- **Group 8** (Page Assembly): [task_20, task_28, task_34] (depend on respective sub-components)
- **Group 9** (Route Registration): [task_35] (depends on Group 8)
- **Group 10** (Polish): [task_36] (depends on Group 9)

---

## Dependencies Graph

```
task_1 (role-index GSI) ──────────────────────────────────┐
task_2 (service_types table) ─┐                           │
task_5 (ServiceType model) ───┼─> task_6 (repo) ─┐       │
                              │                   ├─> task_7 (service) ─> task_8 (routes)
                              │   task_9 (seed) <─┘       │
task_3 (work_orders GSI) ─────┘                           │
                                                          │
task_4 (WO models/enums) ────────────────────────────┐    │
                                                     │    │
task_6 ──────────────────> task_10 (recommendations) ┼────┼─> task_11 (job_service) ─> task_12 (jobs routes)
                                                     │    │
task_1 ──────────────────────────────────────────────┘────┘

task_13 (TS interfaces) ─┬─> task_14 (jobService.ts) ──┬─> task_16 (hooks) ─┬─> task_17 (FilterBar) ──┐
                         │                              │                    ├─> task_18 (SummaryCards)─┼─> task_20 (JobsPage) ──┐
                         ├─> task_15 (serviceTypeSvc) ──┘                    ├─> task_19 (JobsTable) ──┘                        │
                         │                                                   │                                                  │
                         ├─> task_21 (Stepper shell) ──┬─> task_22 (Step1) ──┐                                                  │
                         │                             ├─> task_23 (Step2) ──┤                                                  │
                         │                             ├─> task_24 (Step3) ──┼─> task_28 (CreateJobPage) ───────────────────────┤
                         │                             ├─> task_25 (Step4) ──┤                                                  │
                         │                             ├─> task_26 (Step5) ──┤                                                  │
                         │                             └─> task_27 (Step6) ──┘                                                  │
                         │                                                                                                      │
                         ├─> task_29 (JobHeader) ──────┐                                                                        │
                         ├─> task_30 (JobInfoPanel) ───┤                                                                        │
                         ├─> task_31 (JobTimeline) ────┼─> task_34 (JobDetailPage) ────────────────────────────────────────────┤
                         ├─> task_32 (JobCostPanel) ───┤                                                                        │
                         └────────────────────────────> task_33 (JobActionsPanel) ──┘                                           │
                                                                                                                                │
                                                                                                              task_35 (routes) <┘
                                                                                                                    │
                                                                                                              task_36 (polish)
```

---

## Architect Warnings — Addressed in Tasks

| Warning | Addressed In |
|---------|--------------|
| W1: Backward compat (Optional fields) | task_4 (Pydantic Optional), task_13 (TS `?`), task_19 (null display), task_30 (null display) |
| W2: Summary grouped COUNT not supported | task_11 (full scan + client-side grouping) |
| W3: New types/ directory convention | task_13 (establishes pattern) |
| W4: Dual /api/jobs vs /api/work-orders | task_12 (document canonical usage) |
| W5: Use GSI as primary query path | task_11 (status-created_at-index first, FilterExpression for secondary) |
| Blocker: Missing role-index GSI | task_1 |

---

## Total Estimated Effort

**High** — 36 tasks spanning full-stack (backend models, repositories, services, routes + frontend types, services, hooks, 3 full pages with ~20 components). Estimated ~5-7 days of focused implementation. Backend foundation (tasks 1-12) is the critical path. Frontend can largely proceed in parallel once types and hooks are established.

## Confidence: 88%

High confidence — the design is well-specified with exact file paths, model definitions, and API contracts. The architect review resolved ambiguities. Remaining uncertainty: (1) exact existing code patterns in the codebase may require adaptation, (2) customer search integration in Step 1 depends on existing customer API capabilities, (3) TanStack Table dynamic column implementation complexity may vary based on existing table patterns in the project.