# Designer Output - Issue #3

## Metadata

- **agent**: designer
- **status**: complete
- **confidence**: 88

## Design Document

# Design Document

## Requirements Analysis

Build a comprehensive real-time operational dashboard for the GaragePro garage management system. The dashboard serves as the primary landing screen for garage owners/managers, providing at-a-glance visibility into jobs, financials, alerts, and supply chain status. The implementation must work with the existing Flask/DynamoDB backend and Flutter/Dart frontend, extending current patterns.

**Key deliverables from the design image:**
- Sidebar with navigation modules + "Today's Overview", "Working Technicians", and "Quick Actions" sections
- Top bar with search (job_id, customer_name, vehicle_plate), notifications badge, and user profile dropdown
- 4 KPI cards: Jobs Today (12), Pending Jobs (5), Revenue (€2,450), Expenses (€1,120)
- Alerts panel with severity-coded operational alerts and "View All" link
- Jobs Snapshot table (Vehicle, Job ID, Issue Type, Status, Technician, Service Status, Delivery Status, Delay Reason)
- Revenue Trend line chart (last 7 days) with total summary (€15,250)
- Supply Issues panel with delayed POs and affected jobs
- Auto-refresh every 60 seconds + manual refresh
- Mobile-responsive with vertical stacking below 768px

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flutter Frontend                          │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │Sidebar  │  │Top Bar   │  │Dashboard  │  │ Chart/Table   │  │
│  │Nav      │  │(Search,  │  │Screen     │  │ Components    │  │
│  │Widget   │  │Notif,    │  │(Stateful) │  │ (KPI, Line,   │  │
│  │         │  │Profile)  │  │           │  │  DataTable)   │  │
│  └─────────┘  └──────────┘  └─────┬─────┘  └───────────────┘  │
│                                    │                            │
│  ┌─────────────────────────────────┴────────────────────────┐  │
│  │              DashboardService (Dio HTTP Client)           │  │
│  └─────────────────────────────────┬────────────────────────┘  │
└────────────────────────────────────┼────────────────────────────┘
                                     │ REST API (JSON)
┌────────────────────────────────────┼────────────────────────────┐
│                        Flask Backend                             │
│  ┌─────────────────────────────────┴────────────────────────┐  │
│  │              /api/dashboard/* Routes                       │  │
│  └─────────────────────────────────┬────────────────────────┘  │
│  ┌─────────────────────────────────┴────────────────────────┐  │
│  │              DashboardService (Business Logic)             │  │
│  └──────┬──────────┬──────────┬──────────┬──────────────────┘  │
│         │          │          │          │                      │
│  ┌──────┴───┐ ┌────┴────┐ ┌──┴───┐ ┌───┴─────┐               │
│  │WorkOrder │ │Invoice  │ │Parts │ │Purchase │               │
│  │Repo      │ │Repo     │ │Repo  │ │OrderRepo│               │
│  └──────────┘ └─────────┘ └──────┘ └─────────┘               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    DynamoDB Tables                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Component 1: Backend — Enhanced Dashboard API
- **Purpose**: Provide all data the frontend dashboard needs via consolidated API endpoints
- **Interactions**: Aggregates data from WorkOrder, Invoice, Parts, PurchaseOrder, and Supplier repositories
- **Implementation**:
  - Extend existing `/api/dashboard/executive` endpoint to include: alerts, jobs snapshot table data, supply issues
  - Add new endpoints:
    - `GET /api/dashboard/alerts` — returns active alerts with severity and related entity
    - `GET /api/dashboard/jobs-snapshot` — returns active jobs with computed fields (days_elapsed, delivery_status)
    - `GET /api/dashboard/supply-issues` — returns delayed POs with affected job counts
    - `GET /api/dashboard/search?q=` — unified search across jobs, customers, vehicles
    - `GET /api/dashboard/notifications` — user notifications with badge count
  - KPI calculations: jobs_today (jobs created today), pending_jobs (status != completed), revenue_today (sum paid invoices today), expenses_today (sum of expenses/costs today)
  - Revenue chart: aggregate invoice amounts by day for last 7 days

### Component 2: Backend — Alerts Engine
- **Purpose**: Generate operational alerts from current data state
- **Interactions**: Reads from work_orders (blocked jobs), purchase_orders (delays), inventory (low stock), invoices (unpaid)
- **Implementation**:
  - Alert generation logic in `DashboardService`:
    - `job_blocked`: jobs with status "waiting_parts" or explicitly blocked
    - `supplier_delay`: POs past expected_delivery_date
    - `low_stock`: parts below reorder_point threshold
    - `unpaid_invoice`: invoices past due_date with status != paid
    - `delayed_job`: jobs past due_date with status != completed
  - Return sorted by severity (critical first), limited to top 10
  - Each alert includes: id, type, message, severity (critical/warning), related_entity_id, timestamp

### Component 3: Frontend — Dashboard Screen (Main Container)
- **Purpose**: Primary screen that orchestrates all dashboard sub-components with auto-refresh
- **Interactions**: Uses DashboardService for data, coordinates child widget state
- **Implementation**:
  - StatefulWidget with Timer for 60-second auto-refresh
  - Single `_loadDashboardData()` method that fetches all endpoints in parallel (Future.wait)
  - Pull-to-refresh on mobile
  - Manual refresh button in top bar
  - Loading skeleton UI during initial load
  - Error state with retry option
  - Responsive layout: `LayoutBuilder` + breakpoints (mobile < 768px, tablet < 1200px, desktop)
  - File: `lib/screens/dashboard/dashboard_rev2_screen.dart`

### Component 4: Frontend — Enhanced Sidebar Navigation
- **Purpose**: Global navigation with contextual dashboard info (Today's Overview, Working Technicians, Quick Actions)
- **Interactions**: Controls active route, provides quick-action buttons
- **Implementation**:
  - Extend existing `sidebar_nav.dart` or create new `dashboard_sidebar.dart`
  - Sections:
    1. Logo/branding (GaragePro)
    2. Navigation items with icons and active state highlight
    3. "Today's Overview" summary section (miniature stats)
    4. "Working Technicians" list (names + active job count)
    5. "Quick Actions" buttons (New Customer, New Job)
  - Collapsible on mobile (hamburger menu)
  - Dark theme sidebar matching design image (dark navy blue `#1a2332`)

### Component 5: Frontend — Top Bar Widget
- **Purpose**: Search, notifications, and user profile access
- **Interactions**: Triggers search queries, shows notification dropdown, profile menu
- **Implementation**:
  - Search: TextField with debounced input (300ms), calls `/api/dashboard/search`
  - Notifications: IconButton with badge count, dropdown showing recent alerts
  - Profile: User name + role display, dropdown with logout action
  - File: `lib/components/dashboard/top_bar.dart`

### Component 6: Frontend — KPI Cards Row
- **Purpose**: Display 4 key metrics with change indicators
- **Interactions**: Receives KPI data from parent dashboard screen
- **Implementation**:
  - Leverage existing `kpi_card.dart` component
  - 4 cards in a responsive Row (wrap to 2x2 grid on mobile):
    1. Jobs Today — blue icon, count
    2. Pending Jobs — amber/yellow icon, count  
    3. Revenue Today — green icon, currency formatted (€ or ₹)
    4. Expenses/Pending Payments — red icon, currency formatted
  - Each card shows: icon, title, value, optional % change indicator
  - Cards are clickable → navigate to filtered module view

### Component 7: Frontend — Alerts Panel Widget
- **Purpose**: Show critical operational alerts with severity color coding
- **Interactions**: Receives alerts list, taps navigate to related entity
- **Implementation**:
  - Card with "Alerts" header + "View All" action link
  - ListView of alert items, each with:
    - Colored severity dot (red = critical, yellow = warning)
    - Alert message text
    - Tap handler to navigate to related entity screen
  - Show max 4 alerts, "View All" navigates to full alerts page
  - Empty state: "No operational alerts" message
  - File: `lib/components/dashboard/alerts_panel.dart`

### Component 8: Frontend — Jobs Snapshot Table
- **Purpose**: Tabular view of active jobs with status and delivery tracking
- **Interactions**: Receives jobs list, taps navigate to job detail
- **Implementation**:
  - Card with "Jobs Snapshot" header
  - DataTable or custom table with columns: Vehicle, Job ID, Issue Type, Status, Technician, Service Status, Delivery Status, Delay Reason
  - Status badges: color-coded chips (green=completed, yellow=in progress, red=waiting parts/blocked)
  - Delivery status indicators (green=on track/completed, yellow=at risk, red=delayed)
  - Row tap → navigate to job detail screen
  - Scrollable horizontally on mobile
  - Show top 5-8 jobs, sorted by urgency (delayed first)
  - File: `lib/components/dashboard/jobs_snapshot_table.dart`

### Component 9: Frontend — Revenue Trend Chart
- **Purpose**: 7-day revenue line chart for financial trend visibility
- **Interactions**: Receives chart data points (date, amount)
- **Implementation**:
  - Leverage existing `line_chart_widget.dart` and `fl_chart` package
  - Line chart with:
    - X-axis: last 7 days (day labels)
    - Y-axis: revenue amount (auto-scaled)
    - Tooltip on hover/tap showing exact value
    - Gradient fill under the line
    - Grid lines for readability
  - Summary below: "Total Revenue (7 days): €X,XXX"
  - Card wrapper with "Revenue Trend — Last 7 Days" header
  - File: `lib/components/dashboard/revenue_chart.dart`

### Component 10: Frontend — Supply Issues Panel
- **Purpose**: Show delayed purchase orders affecting operations
- **Interactions**: Receives supply issues list, taps navigate to supplier/PO
- **Implementation**:
  - Card with "Supply Issues" header
  - Table/list with columns: PO ID, Supplier, Status, Affected Jobs
  - Status indicator (red dot for delayed)
  - "Reorder Now" action button per item
  - Tap row → navigate to Suppliers module
  - Empty state: "No supply issues" 
  - File: `lib/components/dashboard/supply_issues_panel.dart`

### Component 11: Frontend — Dashboard Service Extension
- **Purpose**: HTTP client methods for all new dashboard endpoints
- **Interactions**: Called by dashboard screen, returns typed Dart models
- **Implementation**:
  - Extend existing `dashboard_service.dart` with new methods:
    - `getAlerts()` → `List<DashboardAlert>`
    - `getJobsSnapshot()` → `List<JobSnapshot>`
    - `getSupplyIssues()` → `List<SupplyIssue>`
    - `search(String query)` → `SearchResults`
    - `getNotifications()` → `NotificationList`
  - New model classes in `lib/models/dashboard.dart`:
    - `DashboardAlert`, `JobSnapshot`, `SupplyIssue`, `SearchResult`

## Implementation Approach

### Phase 1: Backend API Enhancement (Priority: High)
1. Define new Pydantic models for alerts, jobs snapshot, supply issues
2. Implement alert generation logic in `DashboardService` (scan work_orders, POs, inventory, invoices)
3. Implement jobs snapshot aggregation (join work_orders with vehicle/technician data, compute derived fields)
4. Implement supply issues aggregation (filter delayed POs, count affected jobs)
5. Add new route handlers: `/alerts`, `/jobs-snapshot`, `/supply-issues`, `/search`
6. Update `/executive` endpoint to include all sections in a single response (for initial load optimization)
7. Add unit tests for each service method

### Phase 2: Frontend Models & Service (Priority: High)
1. Add new Dart model classes matching backend response shapes
2. Extend `DashboardService` with new endpoint methods
3. Add error handling and retry logic

### Phase 3: Frontend UI Components (Priority: High)
1. Build `TopBar` widget (search, notifications, profile)
2. Enhance sidebar with Today's Overview, Working Technicians, Quick Actions
3. Build `AlertsPanel` widget
4. Build `JobsSnapshotTable` widget
5. Build `SupplyIssuesPanel` widget
6. Enhance/rebuild `RevenueChart` widget with 7-day line chart

### Phase 4: Dashboard Screen Assembly (Priority: High)
1. Create `DashboardRev2Screen` as the main orchestrator
2. Implement responsive layout (desktop: 2-column grid, mobile: single column stack)
3. Wire up auto-refresh timer (60 seconds)
4. Implement manual refresh
5. Add loading skeletons and error states
6. Add empty states for each section
7. Wire up navigation actions (KPI clicks, alert clicks, job row taps)

### Phase 5: Polish & Integration (Priority: Medium)
1. Dark sidebar theme matching design image
2. Smooth transitions and animations
3. Pull-to-refresh on mobile
4. Search with debounce and results dropdown
5. Notification badge with real-time count
6. Integration testing with backend

## Complexity Assessment

**Estimated Complexity**: high

**Justification**: 
- Multiple new backend endpoints with cross-repository aggregation logic (alerts engine scanning 4+ tables)
- 8+ new frontend widgets/components with interconnected state
- Responsive layout with 3 breakpoints and significantly different arrangements
- Real-time behavior (auto-refresh, notifications badge)
- Navigation integration (clicks on KPIs, alerts, jobs all route to different screens with filters)
- Existing codebase patterns must be strictly followed for consistency
- Design image shows a polished, production-quality UI with specific visual requirements (dark sidebar, color-coded badges, gradient charts)

## Risks and Concerns

- **Performance risk**: The consolidated `/executive` endpoint fetching from 4+ DynamoDB tables on every 60-second refresh could create latency spikes. Mitigation: implement lightweight individual endpoints for incremental refreshes after initial load.
- **Data consistency**: Alerts derived in real-time from current state may show stale data between refreshes. Mitigation: 60-second refresh is acceptable for this use case; no WebSocket needed initially.
- **DynamoDB scan costs**: Alert generation requires scanning work_orders, inventory, POs, and invoices. Without proper GSIs, this could be expensive at scale. Mitigation: add GSIs on status fields; limit scan scope to recent records.
- **Frontend state complexity**: Managing loading/error/data states for 6+ independent data sections in one screen. Mitigation: use a single `_loadAll()` with `Future.wait` and per-section error boundaries.
- **Mobile table rendering**: Jobs Snapshot table with 8 columns won't fit mobile screens. Mitigation: horizontal scroll with frozen first column, or card-based layout on mobile.
- **Existing code conflicts**: Backend currently uses Flask (per codebase exploration) but issue mentions FastAPI. Need to confirm which framework is in use on the `testing/sdlc-issue-3` branch. Design assumes Flask based on current codebase state.

## Confidence: 88%

High confidence because:
- Requirements are well-defined with specific examples and a clear design image
- Existing codebase provides clear patterns to follow (Flask routes, Pydantic models, Flutter StatefulWidget + service pattern)
- Most infrastructure exists (auth, API client, chart components, KPI card component)
- Primary uncertainty: Flask vs FastAPI on the target branch, exact DynamoDB table schemas for new queries, and whether existing repositories already support the needed queries