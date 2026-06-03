# Planner Output - Issue #6

## Metadata

- **agent**: planner
- **status**: complete
- **confidence**: 85

## Execution Plan

# Execution Plan

## Task Breakdown

### Task 1: DynamoDB Schema Setup — GSIs & New Table
- **ID**: task_1
- **Description**: Add 2 new GSIs (`status-index`, `service_code-index`) to `service_types` table. Create new `service_kits` table with PK `kit_id` and 2 GSIs (`kit_code-index`, `status-index`). Update `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/scripts/init_db.py` or equivalent table creation script.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/scripts/init_db.py`
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: add_database_model.yaml
- **Approach**: deterministic

### Task 2: Backend — Pydantic Models
- **ID**: task_2
- **Description**: Create all Pydantic v2 models for Service Master module: `ServiceCategory` enum (9 values matching existing lowercase), `ServiceStatus` enum, `ProcedureStep`, `StandardPart`, `ReferenceMaterial`, `ServiceCreate`, `ServiceUpdate`, `ServiceResponse`, `ServiceDashboardKPIs`, `ServiceAlert`, `ServiceUsageStats`, `ServiceKitCreate`, `ServiceKitUpdate`, `ServiceKitResponse`.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/service_master.py`
- **Dependencies**: []
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 3: Backend — LaborItem Model Update
- **ID**: task_3
- **Description**: Add optional `service_type_id: Optional[str] = Field(default=None)` to both `LaborItem` and `LaborItemCreate` classes in work_order.py. This enables future work orders to link labor to services for usage tracking without breaking existing consumers.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/work_order.py`
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 4: Backend — ServiceMasterRepository
- **ID**: task_4
- **Description**: Create DynamoDB repository for services operating on existing `service_types` table with single-table design (service items, COUNTER#, STATS# items). Implement: `create()` with dual-write for backward compat, `get_by_id()` with field fallbacks, `generate_service_code()` via atomic counter, `increment_usage_stats()`, `get_usage_stats()`, `get_all_usage_stats()`, `list_by_status()`, `search()` with COUNTER#/STATS# exclusion, `update()`, `_normalize_item()` helper.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/service_master_repository.py`
- **Dependencies**: [task_1, task_2]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 5: Backend — ServiceKitRepository
- **ID**: task_5
- **Description**: Create DynamoDB repository for service kits on new `service_kits` table. Implement: `create()`, `get_by_id()`, `list_all()` (excluding COUNTER# items), `list_by_status()`, `update()`, `delete()`, `generate_kit_code()` via atomic counter (KIT-XXX format).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/service_kit_repository.py`
- **Dependencies**: [task_1, task_2]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_4)
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 6: Backend — ServiceMasterService
- **ID**: task_6
- **Description**: Create business logic service layer. Services CRUD (`create_service`, `get_service`, `list_services`, `update_service`, `deactivate_service`), Dashboard (`get_dashboard_kpis` from STATS# items, `get_dashboard_alerts` with 3 alert types, `get_most_used_services`), Usage (`get_usage_stats`, `record_service_usage`), Kits (`create_kit` with denormalized totals, `get_kit` with resolved services, `list_kits`, `update_kit`, `deactivate_kit`).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/service_master_service.py`
- **Dependencies**: [task_4, task_5]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 7: Backend — Routes Blueprint
- **ID**: task_7
- **Description**: Create Flask blueprint `service_master_bp` at `/api/service-master` with all 12 endpoints using `@require_auth`. Endpoints: GET/POST services, GET/PUT/PUT(deactivate) service by ID, GET usage, GET dashboard, GET/POST kits, GET/PUT/PUT(deactivate) kit by ID. Follow existing error response pattern.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/service_master.py`
- **Dependencies**: [task_6]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 8: Backend — Register Blueprint
- **ID**: task_8
- **Description**: Import and register `service_master_bp` in the Flask app factory. Add blueprint registration with url_prefix if not already in the blueprint definition.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py`
- **Dependencies**: [task_7]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 9: Backend — Work Order Usage Hook
- **ID**: task_9
- **Description**: Add `_update_service_usage_stats()` method to existing work order service. After successful work order creation, iterate labor_items and for each with non-null `service_type_id`, call `ServiceMasterService.record_service_usage(service_type_id, item.total)`. Import is lazy to avoid circular deps.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/work_order_service.py`
- **Dependencies**: [task_3, task_6]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 10: Backend — Migration Script
- **ID**: task_10
- **Description**: Create one-time migration script to: (1) backfill existing services with `service_code` (SRV-001, SRV-002...), `service_name` (from `name`), and `status` (from `is_active`); (2) initialize COUNTER#service_code with current count; (3) initialize COUNTER#kit_code at 0 in `service_kits` table.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/scripts/migrate_service_master.py`
- **Dependencies**: [task_1, task_4]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 11: React — TypeScript Types
- **ID**: task_11
- **Description**: Create all TypeScript interfaces and type definitions: `ServiceCategory`, `ServiceStatus`, `ProcedureStep`, `StandardPart`, `ReferenceMaterial`, `Service`, `ServiceDashboardKPIs`, `ServiceAlert`, `ServiceUsageStats`, `ServiceKit`, payload types, and `DashboardResponse`/`PaginatedResponse` generics.
- **Files**: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/serviceMaster.ts`
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 12: React — API Service Layer
- **ID**: task_12
- **Description**: Create Axios API service with all endpoints mapped to the backend routes. Uses existing `api.ts` interceptor. Methods: `getDashboard`, `listServices`, `getService`, `createService`, `updateService`, `deactivateService`, `getUsageStats`, `listKits`, `getKit`, `createKit`, `updateKit`, `deactivateKit`.
- **Files**: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/serviceMasterService.ts`
- **Dependencies**: [task_11]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 13: React — Custom Hooks (TanStack Query)
- **ID**: task_13
- **Description**: Create TanStack Query hooks with 60s staleTime: `useServiceDashboard`, `useServices`, `useService`, `useServiceUsage`, `useCreateService`, `useUpdateService`, `useDeactivateService`, `useServiceKits`, `useServiceKit`, `useCreateKit`, `useUpdateKit`, `useDeactivateKit`. Mutations invalidate relevant query keys.
- **Files**: `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useServiceMaster.ts`
- **Dependencies**: [task_12]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 14: React — Layout & Navigation
- **ID**: task_14
- **Description**: Create `ServiceMasterLayout.tsx` with left sub-navigation (6 items with icons), Outlet for child routes. Add route config to `App.tsx` with all 12 routes. Add "Service Master" to main sidebar navigation. Create `PlaceholderPage` component for Categories, Procedures, Analytics stubs.
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceMasterLayout.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx` (router config)
- **Dependencies**: [task_11]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_12, task_13)
- **Playbook**: null
- **Approach**: cognitive

### Task 15: React — Dashboard Page & Components
- **ID**: task_15
- **Description**: Build dashboard: `ServiceKPICards.tsx` (4 cards: Total Services, Active Categories, Most Used, Avg Duration), `ServiceAlertsPanel.tsx` (severity badges, clickable rows), `MostUsedServicesChart.tsx` (Recharts horizontal BarChart, top 10), `ServicePerformanceTable.tsx` (TanStack Table, sortable, paginated), `ServiceDashboardPage.tsx` (compose all).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceKPICards.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceAlertsPanel.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/MostUsedServicesChart.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServicePerformanceTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceDashboardPage.tsx`
- **Dependencies**: [task_13, task_14]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 16: React — Catalog Page & Components
- **ID**: task_16
- **Description**: Build catalog: `ServiceCatalogFilters.tsx` (search with 300ms debounce, category dropdown, status toggle, "More Filters"), `ServiceCatalogKPIs.tsx` (mini KPI row), `ServiceCatalogTable.tsx` (TanStack Table with 8 columns, pagination, row click navigation), `ServiceCatalogPage.tsx` (compose + "Add Service" button).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceCatalogFilters.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceCatalogKPIs.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceCatalogTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceCatalogPage.tsx`
- **Dependencies**: [task_13, task_14]
- **Estimated Effort**: high
- **Can Run Parallel**: yes (parallel with task_15)
- **Playbook**: null
- **Approach**: cognitive

### Task 17: React — Service Detail Page
- **ID**: task_17
- **Description**: Build service information view: `ServiceDetailHeader.tsx` (code badge, name, category/status badges, Edit/Deactivate buttons), `ServiceBasicInfoSection.tsx` (summary fields in view + edit modes), `ServiceUsageSection.tsx` (usage stats with informational note for zero state), `ServiceInformationPage.tsx` (compose sections, handle edit toggle, deactivate modal).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceDetailHeader.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceBasicInfoSection.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceUsageSection.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceInformationPage.tsx`
- **Dependencies**: [task_13, task_14]
- **Estimated Effort**: high
- **Can Run Parallel**: yes (parallel with task_15, task_16)
- **Playbook**: null
- **Approach**: cognitive

### Task 18: React — Service Form (Create/Edit)
- **ID**: task_18
- **Description**: Build service creation/edit form: `ServiceProcedureEditor.tsx` (dynamic ordered step list, add/remove/reorder), `ServicePartsEditor.tsx` (dynamic parts list, free-text name), `ServiceReferencesEditor.tsx` (dynamic list with type dropdown), `ServiceForm.tsx` (7-section form composition), `NewServicePage.tsx` (wraps form for create AND edit modes, handles submit/cancel/dirty state).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceProcedureEditor.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServicePartsEditor.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceReferencesEditor.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceForm.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/NewServicePage.tsx`
- **Dependencies**: [task_13, task_14]
- **Estimated Effort**: high
- **Can Run Parallel**: yes (parallel with task_15, task_16, task_17)
- **Playbook**: null
- **Approach**: cognitive

### Task 19: React — Service Kits Pages & Components
- **ID**: task_19
- **Description**: Build kits UI: `ServiceSelector.tsx` (searchable multi-select with checkboxes from active services), `ServiceKitForm.tsx` (kit form with service selector + running totals), `ServiceKitCard.tsx` (kit summary card), `ServiceKitsPage.tsx` (listing with KPI row, table, "Create" button), `ServiceKitDetailPage.tsx` (header, info, services table, summary cards, Edit/Delete buttons), `NewServiceKitPage.tsx` (create/edit kit form page).
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceSelector.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceKitForm.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceKitCard.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceKitsPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceKitDetailPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/NewServiceKitPage.tsx`
- **Dependencies**: [task_13, task_14]
- **Estimated Effort**: high
- **Can Run Parallel**: yes (parallel with task_15, task_16, task_17, task_18)
- **Playbook**: null
- **Approach**: cognitive

## Execution Strategy

**Parallel Groups**:
- Group 1: [task_1, task_2, task_3, task_11] (all independent foundation — DB schema, models, types)
- Group 2: [task_4, task_5] (repositories depend on task_1, task_2; can run parallel with each other)
- Group 3: [task_6] (service depends on both repositories)
- Group 4: [task_7, task_10] (routes depend on service; migration depends on task_1 + task_4)
- Group 5: [task_8, task_9] (blueprint registration + work order hook; depend on task_7 / task_6)
- Group 6: [task_12, task_14] (API service + layout; depend on task_11; parallel with each other)
- Group 7: [task_13] (hooks depend on task_12)
- Group 8: [task_15, task_16, task_17, task_18, task_19] (all UI pages — depend on task_13 + task_14; ALL parallel with each other)

## Dependencies Graph

```
task_1 (DB Schema) ─────────┐
task_2 (Pydantic Models) ───┼─> task_4 (ServiceMasterRepo) ─┐
                            └─> task_5 (ServiceKitRepo) ────┼─> task_6 (Service) ─> task_7 (Routes) ─> task_8 (Register)
                                                            │                   │
task_3 (LaborItem Update) ──────────────────────────────────┼───────────────────┴─> task_9 (WO Hook)
                                                            │
task_1 + task_4 ────────────────────────────────────────────┴─> task_10 (Migration)

task_11 (TS Types) ─┬─> task_12 (API Service) ─> task_13 (Hooks) ─┐
                    │                                              ├─> task_15 (Dashboard)
                    └─> task_14 (Layout/Nav) ──────────────────────├─> task_16 (Catalog)
                                                                   ├─> task_17 (Detail)
                                                                   ├─> task_18 (Form)
                                                                   └─> task_19 (Kits)
```

## Total Estimated Effort

**High** — 15-18 developer-days estimated.

- Backend foundation (tasks 1–10): ~5-6 days
- React service layer (tasks 11–13): ~1.5 days
- React UI (tasks 14–19): ~8-10 days

Justification: 19 tasks total, 6 high-effort (complex components with business logic), 5 medium-effort, 8 low-effort. Backend is mostly CRUD with some complexity in dual-write/backward-compat. Frontend is the bulk — 5 parallel page groups each with multiple components, TanStack Table, Recharts, dynamic form editors.

**Critical path**: task_2 → task_4 → task_6 → task_7 → task_8 (backend), then task_11 → task_12 → task_13 → task_15-19 (frontend). Total serial depth: ~9 tasks on the longest chain.

## Confidence: 85%

High confidence on backend tasks (well-specified in design, clear patterns). Moderate confidence on frontend task scoping — the 5 parallel UI groups are each substantial (3-6 files) and may surface integration issues (routing, state management, component prop threading) that require iterative fixes. The design is thorough enough to implement without ambiguity on data models and API contracts.