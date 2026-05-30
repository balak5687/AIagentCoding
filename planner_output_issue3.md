# Planner Output - Issue #3

## Metadata

- **agent**: planner
- **status**: complete
- **confidence**: 85

## Execution Plan

# Execution Plan

## Task Breakdown

### Task 1: Backend — Dashboard Alert Models & Supply Issue Models
- **ID**: task_1
- **Description**: Add new Pydantic models for `DashboardAlert`, `JobSnapshot`, `SupplyIssue`, `SearchResult`, and `NotificationItem` to `/app/models/dashboard.py`. These models define the response shapes for the new endpoints.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/dashboard.py`
- **Dependencies**: []
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 2: Backend — Alerts Engine in DashboardService
- **ID**: task_2
- **Description**: Add alert generation logic to `DashboardService`. Scan work_orders (blocked/waiting_parts), purchase_orders (past expected_delivery_date), inventory (below minimum_stock_level), and invoices (past due_date + unpaid). Return sorted by severity, limited to top 10.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 3: Backend — Jobs Snapshot Aggregation
- **ID**: task_3
- **Description**: Add `get_jobs_snapshot()` to `DashboardService`. Query active work_orders, join with vehicle/technician data, compute derived fields (days_elapsed, delivery_status, delay_reason). Sort by urgency (delayed first), return top 8.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2)
- **Playbook**: null
- **Approach**: cognitive

### Task 4: Backend — Supply Issues Aggregation
- **ID**: task_4
- **Description**: Add `get_supply_issues()` to `DashboardService`. Filter POs with status != received/cancelled where expected_delivery_date is past. Count affected jobs per PO (work_orders waiting on those parts).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2, task_3)
- **Playbook**: null
- **Approach**: cognitive

### Task 5: Backend — Search Endpoint Logic
- **ID**: task_5
- **Description**: Add `search(query)` to `DashboardService`. Unified search across work_orders (by work_order_number), customers (by name), and vehicles (by plate/VIN). Return grouped results.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`
- **Dependencies**: [task_1]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes (parallel with task_2, task_3, task_4)
- **Playbook**: null
- **Approach**: cognitive

### Task 6: Backend — New Dashboard Route Handlers
- **ID**: task_6
- **Description**: Add new route handlers to `/app/routes/dashboard.py`: `GET /api/dashboard/alerts`, `GET /api/dashboard/jobs-snapshot`, `GET /api/dashboard/supply-issues`, `GET /api/dashboard/search?q=`, `GET /api/dashboard/notifications`. All require `@require_auth`. Use existing response patterns (`success_response`, `error_response`).
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/dashboard.py`
- **Dependencies**: [task_2, task_3, task_4, task_5]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: add_crud_endpoint.yaml
- **Approach**: deterministic

### Task 7: Backend — Enhanced Executive Endpoint
- **ID**: task_7
- **Description**: Update the existing `/api/dashboard/executive` endpoint to also return `alerts`, `jobs_snapshot`, `supply_issues` in its response (consolidated payload for initial load optimization). Add revenue_trend_7_days to charts.
- **Files**: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py`, `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/dashboard.py`
- **Dependencies**: [task_6]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 8: Frontend — New Dashboard Dart Models
- **ID**: task_8
- **Description**: Add new model classes to `/lib/models/dashboard.dart`: `DashboardAlert`, `JobSnapshot`, `SupplyIssue`, `SearchResult`, `NotificationItem`, `DashboardOverview` (consolidated response). Include `fromJson` factories matching backend response shapes.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/models/dashboard.dart`
- **Dependencies**: [task_1]
- **Estimated Effort**: low
- **Can Run Parallel**: yes (parallel with backend tasks 2-7)
- **Playbook**: null
- **Approach**: deterministic

### Task 9: Frontend — Dashboard Service Extension
- **ID**: task_9
- **Description**: Add new methods to existing `DashboardService`: `getAlerts()`, `getJobsSnapshot()`, `getSupplyIssues()`, `search(query)`, `getNotifications()`, `getDashboardOverview()`. Follow existing Dio + error handling pattern.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/services/dashboard_service.dart`
- **Dependencies**: [task_8]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

### Task 10: Frontend — Top Bar Widget
- **ID**: task_10
- **Description**: Create `lib/components/dashboard/top_bar.dart`. Search TextField with 300ms debounce calling `DashboardService.search()`. Notifications IconButton with badge count. User profile dropdown with name/role and logout. Refresh button.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/top_bar.dart`
- **Dependencies**: [task_9]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 11: Frontend — Alerts Panel Widget
- **ID**: task_11
- **Description**: Create `lib/components/dashboard/alerts_panel.dart`. Card with "Alerts" header + "View All" link. ListView of alerts with colored severity dots (red=critical, yellow=warning), message text, tap handler. Max 4 items displayed.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/alerts_panel.dart`
- **Dependencies**: [task_8]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 12: Frontend — Jobs Snapshot Table Widget
- **ID**: task_12
- **Description**: Create `lib/components/dashboard/jobs_snapshot_table.dart`. DataTable with columns: Vehicle, Job ID, Issue Type, Status, Technician, Service Status, Delivery Status, Delay Reason. Color-coded status chips. Row tap navigates to job detail. Horizontal scroll on mobile.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/jobs_snapshot_table.dart`
- **Dependencies**: [task_8]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 13: Frontend — Supply Issues Panel Widget
- **ID**: task_13
- **Description**: Create `lib/components/dashboard/supply_issues_panel.dart`. Card with "Supply Issues" header. Table/list with PO ID, Supplier, Status, Affected Jobs count. Red status dot for delayed items. Empty state message.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/supply_issues_panel.dart`
- **Dependencies**: [task_8]
- **Estimated Effort**: low
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: deterministic

### Task 14: Frontend — Revenue Trend Chart (7-day)
- **ID**: task_14
- **Description**: Create `lib/components/dashboard/revenue_chart.dart`. Leverage existing `fl_chart` and `LineChartWidget` patterns. 7-day line chart with gradient fill, tooltips, day labels on X-axis. Summary showing total revenue below.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/revenue_chart.dart`
- **Dependencies**: [task_8]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 15: Frontend — Enhanced Sidebar with Dashboard Sections
- **ID**: task_15
- **Description**: Create `lib/components/dashboard/dashboard_sidebar.dart` or extend existing sidebar. Add sections: Today's Overview (mini stats), Working Technicians list (name + active job count), Quick Actions (New Customer, New Job buttons). Dark theme (#1a2332). Collapsible on mobile.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/components/dashboard/dashboard_sidebar.dart`
- **Dependencies**: [task_9]
- **Estimated Effort**: medium
- **Can Run Parallel**: yes
- **Playbook**: null
- **Approach**: cognitive

### Task 16: Frontend — Dashboard Rev2 Screen (Main Orchestrator)
- **ID**: task_16
- **Description**: Create `lib/screens/dashboard/dashboard_rev2_screen.dart`. StatefulWidget with 60-second Timer auto-refresh. Calls `getDashboardOverview()` for initial load, then individual endpoints for incremental refresh. Responsive layout: desktop 2-column grid, mobile single column stack. Loading skeletons, error states with retry, pull-to-refresh on mobile. Coordinates all child widgets (TopBar, KPI Cards, Alerts, Jobs Table, Revenue Chart, Supply Issues).
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/screens/dashboard/dashboard_rev2_screen.dart`
- **Dependencies**: [task_9, task_10, task_11, task_12, task_13, task_14, task_15]
- **Estimated Effort**: high
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: cognitive

### Task 17: Frontend — Route Integration & Navigation Wiring
- **ID**: task_17
- **Description**: Register `DashboardRev2Screen` in app routes. Wire up navigation actions: KPI card taps → filtered module views, alert taps → related entity screens, job row taps → work order detail, supply issue taps → supplier module. Update sidebar nav to set Dashboard Rev2 as default landing screen.
- **Files**: `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/routes/app_routes.dart`, `/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype/lib/screens/main/new_main_screen.dart`
- **Dependencies**: [task_16]
- **Estimated Effort**: low
- **Can Run Parallel**: no
- **Playbook**: null
- **Approach**: deterministic

## Execution Strategy

**Parallel Groups**:
- Group 1: [task_1] — Backend models (foundation)
- Group 2: [task_2, task_3, task_4, task_5, task_8] — Service logic + frontend models (all depend only on task_1)
- Group 3: [task_6, task_9, task_11, task_12, task_13, task_14] — Routes + frontend components (depend on Group 2)
- Group 4: [task_7, task_10, task_15] — Enhanced endpoint + top bar + sidebar (depend on task_6/task_9)
- Group 5: [task_16] — Dashboard screen assembly (depends on all UI components)
- Group 6: [task_17] — Route wiring (depends on task_16)

## Dependencies Graph

```
task_1 ─────┬──────────────────────────────────────────────────────┐
            │                                                       │
            ├─> task_2 ─┐                                          │
            ├─> task_3 ─┤                                          │
            ├─> task_4 ─┼─> task_6 ─> task_7                      │
            ├─> task_5 ─┘                                          │
            │                                                       │
            └─> task_8 ─┬─> task_9 ─┬─> task_10 ─┐               │
                        │           └─> task_15 ──┤               │
                        ├─> task_11 ──────────────┤               │
                        ├─> task_12 ──────────────┼─> task_16 ─> task_17
                        ├─> task_13 ──────────────┤
                        └─> task_14 ──────────────┘
```

## Total Estimated Effort

**High** — 17 tasks spanning backend API extension (5 new endpoints + enhanced executive), 8 new frontend widgets, a complex orchestrator screen with auto-refresh and responsive layout, and navigation integration. Core complexity lies in:
- Alert generation logic scanning 4 DynamoDB tables
- Jobs snapshot with computed derived fields (delivery status, delay reason)
- Dashboard Rev2 screen managing 6+ data sections with loading/error/data states
- Responsive layout with 3 breakpoints

Estimated implementation time: 6-8 focused hours for an experienced developer familiar with both codebases.

## Confidence: 85%

Solid confidence due to:
- Well-defined requirements with design image
- Existing patterns clearly established in both backend and frontend
- Existing infrastructure (auth, API client, charts, KPI cards) reduces boilerplate
- Slight uncertainty around: exact DynamoDB query performance for alert scans, whether vehicle/technician data is readily joinable for jobs snapshot, and mobile layout edge cases for the 8-column table