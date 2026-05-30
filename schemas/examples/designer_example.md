# Designer Agent Output Example

This shows how Designer agent should format its output.

## Example: Dashboard Module Design

```markdown
---
agent: designer
status: COMPLETE
confidence: 88

design:
  title: "Dashboard Module Implementation"
  summary: "Implement dashboard with 7 components using 3-layer architecture"
  
  architecture:
    pattern: "3-layer"
    layers: ["routes", "services", "repositories"]
    data_flow: "Routes → Services → Repositories → DynamoDB"
    integrations:
      - name: "Backend API → Frontend Service"
        description: "REST API endpoints consumed by Flutter service layer"
        components_involved: ["dashboard_routes", "dashboard_service_flutter"]
  
  components:
    - name: "Dashboard Routes"
      type: "route"
      files:
        - path: "app/routes/dashboard.py"
          description: "API endpoints for dashboard data"
      description: "5 REST endpoints for KPIs, alerts, jobs, revenue, supply issues"
      dependencies: ["dashboard_service"]
    
    - name: "Dashboard Service"
      type: "service"
      files:
        - path: "app/services/dashboard_service.py"
          description: "Business logic for dashboard aggregations"
      description: "Aggregates data from multiple repositories (Jobs, Invoices, Parts)"
      dependencies: ["work_orders_repository", "invoices_repository", "parts_repository"]
  
  approach:
    strategy: "incremental"
    phases:
      - order: 1
        name: "Backend API Implementation"
        description: "Create routes and services for backend"
        deliverables: ["dashboard.py", "dashboard_service.py"]
      - order: 2
        name: "Frontend Widgets"
        description: "Create Flutter widgets for 7 dashboard components"
        deliverables: ["dashboard_screen.dart", "kpi_cards_widget.dart", "..."]
    
    prerequisites:
      - "Work Orders repository exists"
      - "Invoices repository exists"
      - "Authentication middleware in place"
    
    success_criteria:
      - "All 5 API endpoints return valid data"
      - "Dashboard loads without errors"
      - "Real-time updates work (60s refresh)"
  
  risks:
    - id: "performance-001"
      description: "Dashboard may be slow if aggregating large datasets"
      severity: MEDIUM
      mitigation: "Add caching layer for KPIs, use database indexes"
    
    - id: "security-002"
      description: "Dashboard exposes sensitive business metrics"
      severity: HIGH
      mitigation: "Ensure JWT authentication on all endpoints, role-based access"
  
  technical_debt:
    - description: "No caching layer implemented"
      severity: LOW
      reason: "MVP focuses on functionality, caching can be added later"
  
  estimates:
    complexity_score: 6
    files_to_create: 10
    files_to_modify: 2
    estimated_loc: 800
    time_estimate: "3-4 hours for backend, 4-5 hours for frontend"
---

# Dashboard Module Design Document

## Executive Summary

The Dashboard Module provides a real-time operational overview of the GreasyNuts garage management system. It aggregates data from multiple sources (Jobs, Invoices, Suppliers, Parts) to display KPIs, alerts, jobs snapshot, revenue trends, and supply chain issues.

## Architecture Overview

### Pattern: 3-Layer Architecture

```
┌─────────────────┐
│  Flutter UI     │ (7 dashboard widgets)
└────────┬────────┘
         │ HTTP REST
┌────────▼────────┐
│  Routes Layer   │ dashboard.py (5 endpoints)
└────────┬────────┘
         │
┌────────▼────────┐
│ Services Layer  │ dashboard_service.py (aggregation logic)
└────────┬────────┘
         │
┌────────▼────────┐
│ Repository Layer│ work_orders, invoices, parts
└────────┬────────┘
         │
     DynamoDB
```

### Data Flow

1. **Frontend requests** dashboard data via `/api/dashboard/kpis`
2. **Routes layer** authenticates request (JWT), calls service
3. **Service layer** aggregates data from multiple repositories
4. **Repository layer** queries DynamoDB
5. **Response flows back** with JSON data

## Components Breakdown

### Component 1: Dashboard Routes (`app/routes/dashboard.py`)

**Endpoints**:
- `GET /api/dashboard/kpis` - Dashboard KPI metrics
- `GET /api/dashboard/alerts` - Operational alerts
- `GET /api/dashboard/jobs-snapshot` - Active jobs with progress
- `GET /api/dashboard/revenue?days=7` - Revenue trend
- `GET /api/dashboard/supply-issues` - Supplier delays

**Authentication**: All endpoints require JWT via `@require_auth` decorator

**Error Handling**: Try-except with logging, standard error responses

### Component 2: Dashboard Service (`app/services/dashboard_service.py`)

**Methods**:
- `get_kpis() -> (dict, error)` - Calculate 4 KPIs
- `get_alerts() -> (list, error)` - Aggregate alerts from multiple sources
- `get_jobs_snapshot(limit=10) -> (list, error)` - Active jobs with status
- `get_revenue_trend(days=7) -> (dict, error)` - Revenue by day
- `get_supply_issues() -> (list, error)` - Delayed POs

**Pattern**: All methods return `(data, error)` tuple

### Component 3-7: Frontend Widgets (Flutter)

See frontend design document for details on:
- Sidebar navigation
- Top bar (search, notifications, profile)
- KPI cards grid
- Alerts panel
- Jobs snapshot table
- Revenue line chart
- Supply issues list

## Implementation Approach

### Phase 1: Backend API (3-4 hours)

1. Create `app/routes/dashboard.py` with 5 endpoints
2. Create `app/services/dashboard_service.py` with aggregation logic
3. Register blueprint in `app/routes/__init__.py`
4. Test endpoints with curl/Postman

### Phase 2: Frontend Widgets (4-5 hours)

1. Create `dashboard_screen.dart` main screen
2. Implement 7 widget components
3. Create `dashboard_service.dart` for API calls
4. Wire up auto-refresh (60s)

### Success Criteria

- ✅ All 5 backend endpoints return valid JSON
- ✅ Dashboard screen loads without errors
- ✅ KPIs show correct values
- ✅ Alerts display properly
- ✅ Auto-refresh works every 60 seconds

## Risks & Mitigation

### Risk 1: Performance Issues ⚠️ MEDIUM

**Problem**: Aggregating data from multiple large tables may cause slow dashboard loads.

**Mitigation**:
- Add database indexes on frequently queried fields
- Implement caching layer for KPIs (Redis or in-memory)
- Consider pre-computing metrics in background job

### Risk 2: Security Exposure 🔴 HIGH

**Problem**: Dashboard exposes sensitive business metrics (revenue, pending payments).

**Mitigation**:
- **CRITICAL**: Ensure JWT authentication on ALL endpoints
- Add role-based access control (only Owners/Managers see revenue)
- Log all dashboard access for audit trail

## Technical Debt

### No Caching Layer

**Debt**: Dashboard recalculates KPIs on every request.

**Why**: MVP focuses on getting functionality working. Caching adds complexity.

**When to address**: After MVP validation, if performance becomes issue.

## Estimates

- **Complexity**: 6/10 (moderate - multiple components, data aggregation)
- **Files to Create**: 10 (5 backend, 5 frontend)
- **Files to Modify**: 2 (routes/__init__.py, frontend routing)
- **Lines of Code**: ~800 total (300 backend, 500 frontend)
- **Time**: 7-9 hours total (3-4 backend, 4-5 frontend)

## Dependencies

**Must exist before starting**:
- ✅ WorkOrdersRepository (already exists)
- ✅ InvoicesRepository (already exists)
- ✅ PartsRepository (already exists)
- ✅ JWT authentication middleware (already exists)
- ✅ Response utilities (success_response, error_response) (already exists)

**No blockers - Ready to implement!**

---

*Generated by Designer Agent - 2026-05-23*
```

## Validation

This output validates against `designer.proto`:
- ✅ All required fields present (agent, status, confidence, design, markdown_body)
- ✅ Confidence 88 is within valid range (0-100)
- ✅ Status is COMPLETE (valid enum value)
- ✅ Components have name, type, files, description
- ✅ Risks have id, description, severity, mitigation
- ✅ Architecture specifies pattern and layers

## Usage

```python
from src.core.schema_validator import validate_agent_output

raw_output = """<markdown content above>"""

is_valid, proto_msg, yaml_data, markdown = validate_agent_output(
    "designer",
    raw_output,
    strict=True
)

if is_valid:
    print(f"Design has {len(proto_msg.design.components)} components")
    print(f"Complexity: {proto_msg.design.estimates.complexity_score}/10")
```
