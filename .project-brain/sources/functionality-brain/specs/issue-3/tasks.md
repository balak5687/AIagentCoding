# Tasks - Issue #3

---
agent: planner
status: complete
confidence: 85
---

# Execution Plan

## Task Breakdown

### Task 1: Backend — New Dashboard Pydantic Models
- **ID**: task_1
- **Description**: Add new Pydantic models for alerts, jobs snapshot, and supply issues to `app/models/dashboard.py`. Models: `DashboardAlert` (id, type, message, severity, related_entity_id, timestamp), `JobSnapshot` (vehicle, job_id, work_order_number, issue_type, status, technician, service_status, delivery_status, delay_reason, days_elapsed), `SupplyIssue` (po_id, po_number, supplier_name, status, affected_jobs_count, expected_date, days_overdue), `SearchResult` (id, type, title, subtitle, url), `NotificationItem` (id, message, type, read, timestamp).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/dashboard.py`
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic (follows existing Pydantic model patterns in codebase)

### Task 2: Backend — Alerts Engine in DashboardService
- **ID**: task_2
- **Description**: Add alert generation logic to `DashboardService`. Scan work_orders (status=waiting_parts or blocked → `job_blocked`), purchase_orders (past expected_delivery_date → `supplier_delay`), inventory (qty < min_stock_level → `low_stock`), invoices (past due_date, status != paid → `unpaid_invoice`), work_orders (past estimated completion, status != completed → `delayed_job`). Return sorted by severity (critical first), limited to top 10. Requires importing `WorkOrderRepository` and checking for invoice repository (may need to create one or query work_orders for invoice status).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive (cross-repository aggregation with business rule logic)

### Task 3: Backend — Jobs Snapshot Aggregation
- **ID**: task_3
- **Description**: Add `_get_jobs_snapshot()` method to `DashboardService`. Fetch active work_orders (status != completed), join with vehicle data (via vehicle_id), compute derived fields: days_elapsed (from created_at), delivery_status (on_track/at_risk/delayed based on time estimates), service_status (derived from work_order status). Sort by urgency (delayed first). Return top 8. Requires `WorkOrderRepository` and `VehicleRepository`.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2)
- **Playbook**: null
- **Approach**: cognitive (cross-repo join logic)

### Task 4: Backend — Supply Issues Aggregation
- **ID**: task_4
- **Description**: Add `_get_supply_issues()` method to `DashboardService`. Filter purchase_orders where status is 'sent' and expected_delivery_date < today. For each delayed PO, count affected work_orders (jobs waiting on parts from that PO). Return with days_overdue calculation. Requires `PurchaseOrderRepository` (already imported) and cross-referencing with work_orders.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2, task_3)
- **Playbook**: null
- **Approach**: cognitive

### Task 5: Backend — Revenue Calculations (7-day trend)
- **ID**: task_5
- **Description**: Add `_get_revenue_trend()` method to `DashboardService`. Aggregate invoice amounts (paid invoices) by day for last 7 days. Return as ChartData with type="line". Also add `_get_today_revenue()` and `_get_today_expenses()` for KPI cards. Note: No InvoiceRepository exists yet — will need to create one or compute from work_orders (which have labor_items and parts_used totals).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`, possibly new `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/invoice_repository.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2-4)
- **Playbook**: null
- **Approach**: cognitive

### Task 6: Backend — Unified Search Endpoint
- **ID**: task_6
- **Description**: Add `search()` method to `DashboardService` that searches across work_orders (by job_id, work_order_number, description), customers (by name, phone), and vehicles (by plate, make/model). Return unified `SearchResult` list. Leverage existing `search_work_orders()` in WorkOrderRepository and similar patterns in CustomerRepository.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2-5)
- **Playbook**: null
- **Approach**: cognitive

### Task 7: Backend — New Route Handlers
- **ID**: task_7
- **Description**: Add new Flask route handlers to `app/routes/dashboard.py`: `GET /api/dashboard/alerts` (calls `get_alerts()`), `GET /api/dashboard/jobs-snapshot` (calls `get_jobs_snapshot()`), `GET /api/dashboard/supply-issues` (calls `get_supply_issues()`), `GET /api/dashboard/search?q=` (calls `search(query)`), `GET /api/dashboard/notifications` (returns recent alerts as notifications with badge count). All routes use `@require_auth` decorator. Follow existing route patterns.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/dashboard.py`
- **Dependencies**: [task_2, task_3, task_4, task_5, task_6]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml (partial — follows standard route registration pattern)
- **Approach**: deterministic

### Task 8: Backend — Enhanced Executive Endpoint
- **ID**: task_8
- **Description**: Update the existing `get_executive_dashboard()` in the service to optionally include all new sections (alerts, jobs_snapshot, supply_issues, revenue_chart) in a single consolidated response for initial page load optimization. Add an `include_all=true` query parameter to `/api/dashboard/executive`. Update the `DashboardSummary` model or create a new `FullDashboardResponse` model to accommodate the extra fields.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`, `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/dashboard.py`, `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/dashboard.py`
- **Dependencies**: [task_7]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 9: Backend — Unit Tests
- **ID**: task_9
- **Description**: Write pytest unit tests for new service methods: `test_get_alerts()`, `test_get_jobs_snapshot()`, `test_get_supply_issues()`, `test_search()`, `test_get_revenue_trend()`. Mock repositories. Follow existing test pattern in `tests/test_purchase_orders.py` (pytest fixtures, Mock repos, Arrange-Act-Assert).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/tests/test_dashboard.py`
- **Dependencies**: [task_8]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: add_unit_tests.yaml
- **Approach**: deterministic

### Task 10: Frontend — New Dart Models
- **ID**: task_10
- **Description**: Add new model classes to `lib/models/dashboard.dart`: `DashboardAlert` (id, type, message, severity, relatedEntityId, timestamp — with `fromJson` factory), `JobSnapshot` (vehicle, jobId, workOrderNumber, issueType, status, technician, serviceStatus, deliveryStatus, delayReason, daysElapsed), `SupplyIssue` (poId, poNumber, supplierName, status, affectedJobsCount, expectedDate, daysOverdue), `SearchResult` (id, type, title, subtitle). Follow existing `fromJson` factory pattern.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/models/dashboard.dart`
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with backend tasks)
- **Playbook**: null
- **Approach**: deterministic

### Task 11: Frontend — Dashboard Service Extension
- **ID**: task_11
- **Description**: Extend `lib/services/dashboard_service.dart` with new methods: `getAlerts()` → `List<DashboardAlert>`, `getJobsSnapshot()` → `List<JobSnapshot>`, `getSupplyIssues()` → `List<SupplyIssue>`, `search(String query)` → `List<SearchResult>`, `getNotifications()` → map with items list and badge count. Follow existing Dio pattern with `ApiConfig.dashboard` base URL.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/services/dashboard_service.dart`
- **Dependencies**: [task_10]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 12: Frontend — Top Bar Widget
- **ID**: task_12
- **Description**: Create `lib/components/dashboard/top_bar.dart`. Contains: search TextField with debounced input (300ms) calling search service, notifications IconButton with badge count (red dot with number), profile section showing user name + role with dropdown. Callbacks for onSearch, onNotificationTap, onProfileTap. Use existing `ApiClient` for user context.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/top_bar.dart`
- **Dependencies**: [task_11]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 13: Frontend — Enhanced Sidebar Widget
- **ID**: task_13
- **Description**: Create `lib/components/dashboard/dashboard_sidebar.dart` or extend existing `sidebar_nav.dart`. Add three new sections below navigation items: "Today's Overview" (miniature KPI stats — jobs count, revenue), "Working Technicians" (list of tech names with active job count), "Quick Actions" (New Customer, New Job buttons). Dark navy theme (#1a2332). Collapsible on mobile.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/dashboard_sidebar.dart`
- **Dependencies**: [task_11]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_12)
- **Playbook**: null
- **Approach**: cognitive

### Task 14: Frontend — Alerts Panel Widget
- **ID**: task_14
- **Description**: Create `lib/components/dashboard/alerts_panel.dart`. Card with "Alerts" header + "View All" link. ListView of alert items with colored severity dot (red=critical, yellow=warning), message text, tap handler. Show max 4 alerts. Empty state: "No operational alerts". Use existing `StatusBadge` component pattern for severity indication.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/alerts_panel.dart`
- **Dependencies**: [task_10]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 15: Frontend — Jobs Snapshot Table Widget
- **ID**: task_15
- **Description**: Create `lib/components/dashboard/jobs_snapshot_table.dart`. Card with "Jobs Snapshot" header. DataTable with columns: Vehicle, Job ID, Issue Type, Status, Technician, Service Status, Delivery Status, Delay Reason. Color-coded status chips (green=completed, yellow=in_progress, red=blocked). Row tap → navigate to job detail. Horizontal scroll on mobile. Show top 5-8 rows sorted by urgency.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/jobs_snapshot_table.dart`
- **Dependencies**: [task_10]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_14)
- **Playbook**: null
- **Approach**: cognitive

### Task 16: Frontend — Revenue Trend Chart Widget
- **ID**: task_16
- **Description**: Create `lib/components/dashboard/revenue_chart.dart`. Card with "Revenue Trend — Last 7 Days" header. Use existing `fl_chart` package and `line_chart_widget.dart` as reference. Line chart with X-axis (7 day labels), Y-axis (auto-scaled revenue), gradient fill, tooltips. Summary below: "Total Revenue (7 days): €X,XXX".
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/revenue_chart.dart`
- **Dependencies**: [task_10]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_14, 15)
- **Playbook**: null
- **Approach**: cognitive

### Task 17: Frontend — Supply Issues Panel Widget
- **ID**: task_17
- **Description**: Create `lib/components/dashboard/supply_issues_panel.dart`. Card with "Supply Issues" header. Table/list showing: PO ID, Supplier, Status (red dot), Affected Jobs count. Row tap → navigate to Suppliers module. Empty state: "No supply issues". Optional "Reorder Now" action button per item.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/supply_issues_panel.dart`
- **Dependencies**: [task_10]
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with task_14-16)
- **Playbook**: null
- **Approach**: deterministic

### Task 18: Frontend — KPI Cards Enhancement
- **ID**: task_18
- **Description**: Ensure existing `kpi_card.dart` supports the 4 required KPIs: Jobs Today (blue), Pending Jobs (amber), Revenue Today (green), Expenses/Pending (red). Verify existing KPICardsGrid wraps to 2x2 on mobile. Add clickable navigation callbacks. May need minor color/icon updates to support new card types (amber color, work-order icon).
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/kpi_card.dart`
- **Dependencies**: [task_10]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 19: Frontend — Dashboard Rev2 Screen (Main Orchestrator)
- **ID**: task_19
- **Description**: Create `lib/screens/dashboard/dashboard_rev2_screen.dart`. StatefulWidget orchestrating all sub-components. Implements: parallel data fetch via `Future.wait` on all endpoints, 60-second auto-refresh Timer, manual refresh button, pull-to-refresh, loading skeleton during initial load, error state with retry. Responsive layout using `LayoutBuilder`: desktop (2-column grid), tablet (mixed), mobile (single column stack). Wire up navigation actions (KPI clicks, alert taps, job row taps).
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/screens/dashboard/dashboard_rev2_screen.dart`
- **Dependencies**: [task_11, task_12, task_13, task_14, task_15, task_16, task_17, task_18]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 20: Frontend — Route Registration & Navigation
- **ID**: task_20
- **Description**: Register the new `DashboardRev2Screen` in the app routing. Update `app_routes.dart` to add route. Update sidebar navigation to point to new dashboard as default landing screen. Ensure back-navigation works from child screens.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/routes/app_routes.dart`, potentially `lib/screens/main/new_main_screen.dart`
- **Dependencies**: [task_19]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 21: Frontend — Responsive & Polish
- **ID**: task_21
- **Description**: Final responsive testing and polish. Verify: mobile layout (< 768px) stacks vertically, tablet layout uses 2-col where appropriate, desktop uses full grid. Dark sidebar theme consistency. Smooth transitions. Pull-to-refresh gesture on mobile. Search debounce working. Notification badge updating on refresh.
- **Files**: Multiple — `dashboard_rev2_screen.dart`, `dashboard_sidebar.dart`, `top_bar.dart`
- **Dependencies**: [task_20]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

## Execution Strategy

**Parallel Groups**:
- **Group 1** (Foundation — can all start simultaneously):
  - task_1: Backend models
  - task_10: Frontend models
- **Group 2** (Backend service logic — after task_1, all parallel):
  - task_2: Alerts engine
  - task_3: Jobs snapshot
  - task_4: Supply issues
  - task_5: Revenue calculations
  - task_6: Unified search
- **Group 3** (Backend routes — after Group 2):
  - task_7: New route handlers
  - task_8: Enhanced executive endpoint
- **Group 4** (Backend tests — after Group 3):
  - task_9: Unit tests
- **Group 5** (Frontend service — after task_10):
  - task_11: Dashboard service extension
- **Group 6** (Frontend widgets — after task_10/task_11, all parallel):
  - task_12: Top bar
  - task_13: Enhanced sidebar
  - task_14: Alerts panel
  - task_15: Jobs snapshot table
  - task_16: Revenue chart
  - task_17: Supply issues panel
  - task_18: KPI cards enhancement
- **Group 7** (Frontend assembly — after Group 6):
  - task_19: Dashboard Rev2 screen
- **Group 8** (Integration — after task_19):
  - task_20: Route registration
  - task_21: Responsive & polish

## Dependencies Graph

```
task_1 (Backend Models) ────┬──> task_2 (Alerts) ─────────────┐
                            ├──> task_3 (Jobs Snapshot) ───────┤
                            ├──> task_4 (Supply Issues) ───────┼──> task_7 (Routes) ──> task_8 (Enhanced EP) ──> task_9 (Tests)
                            ├──> task_5 (Revenue) ─────────────┤
                            └──> task_6 (Search) ──────────────┘

task_10 (Frontend Models) ──┬──> task_11 (FE Service) ─┬──> task_12 (Top Bar) ──────────┐
                            │                          └──> task_13 (Sidebar) ───────────┤
                            ├──> task_14 (Alerts Panel) ────────────────────────────────┤
                            ├──> task_15 (Jobs Table) ──────────────────────────────────┼──> task_19 (Dashboard Screen) ──> task_20 (Routes) ──> task_21 (Polish)
                            ├──> task_16 (Revenue Chart) ───────────────────────────────┤
                            ├──> task_17 (Supply Panel) ────────────────────────────────┤
                            └──> task_18 (KPI Cards) ───────────────────────────────────┘
```

## Key Implementation Notes

1. **No InvoiceRepository exists** — The invoice model exists but there's no repository. For revenue/expenses KPIs, either create a lightweight `InvoiceRepository` extending `BaseRepository` or derive financial data from work_order totals (labor_items + parts_used sums). Recommend creating a minimal `InvoiceRepository` with table_name="invoices" for clean separation.

2. **WorkOrderStatus values** — The existing `WorkOrderStatus` enum has: new, estimate_created, customer_approved, in_progress, completed. There is no "waiting_parts" or "blocked" status. The alerts engine should treat `estimate_created` + missing parts as a proxy for "waiting parts", or the design should adapt to available statuses.

3. **No technician/user names in work_orders** — Work orders store `technician_ids` (list of strings). The Jobs Snapshot table needs technician names, requiring a join with the Users table via `UserRepository`.

4. **Vehicle plate not directly in work_order** — Work orders reference `vehicle_id`. Need to fetch vehicle details (plate, make, model) from `VehicleRepository`.

5. **Purchase order "expected_delivery_date"** — Need to verify this field exists in the PO schema. The PO model has `order_date` but may not have `expected_delivery_date`. May need to use `order_date` + standard lead time or check actual DynamoDB table schema.

6. **Branch constraint** — All work must be committed to `testing/sdlc-issue-3` branch only.

## Total Estimated Effort

**High** — 21 tasks spanning both backend (9 tasks) and frontend (12 tasks). Backend involves cross-repository aggregation logic with 4+ tables. Frontend involves 7+ new widgets, a complex orchestrator screen with responsive layouts, and real-time refresh behavior. Estimated 3-4 days of focused development for a senior full-stack developer.

## Confidence: 85%

**Rationale**: High confidence because existing patterns are clear and well-established in both codebases. Deductions for:
- Uncertainty about InvoiceRepository existence (-5%)
- WorkOrder status values not mapping 1:1 to design requirements (-3%)
- Unknown DynamoDB table schemas for expected_delivery_date on POs (-4%)
- Cross-repo joins in DynamoDB (no native joins) requiring multiple queries (-3%)
