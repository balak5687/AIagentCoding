# Designer Output - Issue #6

## Metadata

- **agent**: designer
- **status**: complete
- **confidence**: 88

## Design Document

# Design Document — Service Master Module (Issue #6, Revision 2)

## Architect Feedback Resolution

| Blocker/Warning | Resolution |
|---|---|
| **Blocker 1: No `service_type_id` in LaborItem** | Option (B) adopted: Add optional `service_type_id` to `LaborItem` and `LaborItemCreate` models. Dashboard KPIs and usage history start from zero — only future work orders with the field populated contribute to usage stats. UI shows informational note: "Usage data available for work orders created after this feature's deployment." Historical data is NOT backfilled. Additionally, usage stats are stored as denormalized STATS# items in the `service_types` table (NOT via work_orders table scans). |
| **Blocker 2: Category enum mismatch** | Fixed. Pydantic enum uses existing lowercase values: `maintenance, brakes, tires, transmission, electrical, ac_heating, inspection`. Two new categories added: `engine, body_work`. No migration needed — existing records remain valid with their current category values. |
| **Warning 1: `required_parts` not in seed data** | Removed from backward-compat list. Field exists in the model definition but is unused/unpopulated. Not referenced in the new design. |
| **Warning 2: Dashboard KPI aggregation** | Resolved by NOT scanning the work_orders table. Usage stats are denormalized into `STATS#<service_type_id>` items in the `service_types` table. Stats are atomically incremented when a work order is created/updated with a `service_type_id` in its labor items. Dashboard reads only from `service_types` table — fast single-table queries. |
| **Warning 3: `service_name` read strategy** | Read with fallback: `item.get('service_name') or item.get('name')`. All writes via the new service master endpoints set both fields. No one-time backfill migration needed for reads — the fallback handles pre-existing records seamlessly. |
| **Warning 4: Atomic counter safety net** | Removed. DynamoDB atomic counter (`SET #val = if_not_exists(#val, :zero) + :incr` with `ReturnValues: UPDATED_NEW`) guarantees uniqueness. No post-generation GSI lookup. |
| **Warning 5: Redis cache** | Confirmed moot for MVP. With denormalized stats (not work_order scans) and <500 services, all dashboard queries are fast DynamoDB reads. No cache layer needed. |

---

## Requirements Analysis

The Service Master Module is a centralized library for managing all garage services offered by the workshop. It extends the existing `service_types` DynamoDB table into a full-featured management module with:

1. **Service Dashboard** — KPIs (total services, active/inactive counts, most used, revenue), alerts panel, usage chart, performance table
2. **Service Catalog** — Searchable/filterable listing of all services with status indicators
3. **Service Information** — Detail view with inline edit capability, procedure steps, parts, references, usage stats
4. **New Service** — Multi-section creation form with auto-generated service code
5. **Service Kits** — Bundle multiple services into packages with combined pricing/hours

**Key constraint**: This extends the existing `service_types` table and must be fully backward-compatible with the existing `/api/service-types` endpoints. The existing `ServiceTypeRepository` is NOT modified — a new `ServiceMasterRepository` operates on the same table with extended field handling.

**Service Code Format**: `SRV-001`, `SRV-002`, etc. (per screen designs).
**Kit Code Format**: `KIT-001`, `KIT-002`, etc.

---

## Architecture Overview

**Backend changes:**
- New Pydantic models: `/app/models/service_master.py`
- Minor update to `/app/models/work_order.py`: add optional `service_type_id` to `LaborItem`
- New `ServiceMasterRepository`: CRUD + atomic code generation + denormalized stats
- New `ServiceKitRepository`: kit CRUD
- New `ServiceMasterService`: business logic, KPI aggregation, kit totals
- New routes blueprint: `service_master_bp` at `/api/service-master`
- Hook in work order service: increment usage stats when `service_type_id` present

**React frontend:**
- New page group under `/service-master` with tab sub-navigation
- Pages: Dashboard, Catalog, Information (detail/edit), New Service, Kits, Kit Detail, New Kit
- Components: KPI cards, alerts panel, charts (Recharts), tables (TanStack Table), multi-section forms
- Custom hooks: TanStack Query with 60s staleTime
- Service layer: Axios API calls via existing `api.ts` interceptor

**DynamoDB changes:**
- Extend `service_types` table with new fields + 2 new GSIs (total: 3 GSIs, within 5 max)
- Add `COUNTER#service_code` and `STATS#<id>` items to `service_types` table (single-table design)
- New `service_kits` table with 2 GSIs (within 5 max)
- Add `COUNTER#kit_code` item to `service_kits` table

---

## Components

### Component 1: Backend — Pydantic Models

- **Purpose**: Request/response validation models for the Service Master module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/service_master.py`
- **Dependencies**: Pydantic v2, `decimal.Decimal`

**Key Models:**

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class ServiceCategory(str, Enum):
    MAINTENANCE = "maintenance"
    BRAKES = "brakes"
    TIRES = "tires"
    TRANSMISSION = "transmission"
    ELECTRICAL = "electrical"
    AC_HEATING = "ac_heating"
    INSPECTION = "inspection"
    ENGINE = "engine"
    BODY_WORK = "body_work"


class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ProcedureStep(BaseModel):
    step: int = Field(..., ge=1)
    description: str = Field(..., min_length=1, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=500)


class StandardPart(BaseModel):
    part_id: Optional[str] = None
    part_name: str = Field(..., min_length=1, max_length=200)
    part_number: Optional[str] = Field(default=None, max_length=50)
    quantity: float = Field(..., gt=0)
    unit: str = Field(default="pcs", max_length=20)
    notes: Optional[str] = Field(default=None, max_length=200)


class ReferenceMaterial(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., description="PDF Manual | Video Tutorial | OEM Procedure | Internal SOP")
    url: str = Field(..., min_length=1, max_length=500)


class ServiceCreate(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=200)
    category: ServiceCategory
    status: ServiceStatus = ServiceStatus.ACTIVE
    description: Optional[str] = Field(default=None, max_length=2000)
    standard_price: Optional[Decimal] = Field(default=None, ge=0)
    estimated_duration_hours: Optional[float] = Field(default=None, ge=0)
    warranty_period: Optional[str] = Field(default=None, max_length=50)
    service_interval_km: Optional[int] = Field(default=None, ge=0)
    service_interval_months: Optional[int] = Field(default=None, ge=0)
    procedure_steps: Optional[List[ProcedureStep]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    standard_parts: Optional[List[StandardPart]] = None
    reference_materials: Optional[List[ReferenceMaterial]] = None


class ServiceUpdate(BaseModel):
    service_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[ServiceCategory] = None
    status: Optional[ServiceStatus] = None
    description: Optional[str] = Field(default=None, max_length=2000)
    standard_price: Optional[Decimal] = Field(default=None, ge=0)
    estimated_duration_hours: Optional[float] = Field(default=None, ge=0)
    warranty_period: Optional[str] = Field(default=None, max_length=50)
    service_interval_km: Optional[int] = Field(default=None, ge=0)
    service_interval_months: Optional[int] = Field(default=None, ge=0)
    procedure_steps: Optional[List[ProcedureStep]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    standard_parts: Optional[List[StandardPart]] = None
    reference_materials: Optional[List[ReferenceMaterial]] = None


class ServiceResponse(BaseModel):
    service_type_id: str
    service_code: str
    service_name: str
    category: ServiceCategory
    status: ServiceStatus
    description: Optional[str] = None
    standard_price: Optional[Decimal] = None
    estimated_duration_hours: Optional[float] = None
    warranty_period: Optional[str] = None
    service_interval_km: Optional[int] = None
    service_interval_months: Optional[int] = None
    procedure_steps: Optional[List[ProcedureStep]] = None
    notes: Optional[str] = None
    standard_parts: Optional[List[StandardPart]] = None
    reference_materials: Optional[List[ReferenceMaterial]] = None
    usage_count: int = 0
    revenue_generated: Decimal = Decimal("0.00")
    last_used_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ServiceDashboardKPIs(BaseModel):
    total_services: int = 0
    active_services: int = 0
    inactive_services: int = 0
    most_used_service: Optional[str] = None
    most_used_service_count: int = 0
    total_revenue: Decimal = Decimal("0.00")


class ServiceAlert(BaseModel):
    service_type_id: str
    service_name: str
    service_code: str
    severity: str
    alert_type: str
    message: str


class ServiceUsageStats(BaseModel):
    service_type_id: str
    usage_count: int = 0
    revenue_generated: Decimal = Decimal("0.00")
    last_used_at: Optional[str] = None


class ServiceKitCreate(BaseModel):
    kit_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: ServiceStatus = ServiceStatus.ACTIVE
    service_ids: List[str] = Field(..., min_length=1)


class ServiceKitUpdate(BaseModel):
    kit_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[ServiceStatus] = None
    service_ids: Optional[List[str]] = Field(default=None, min_length=1)


class ServiceKitResponse(BaseModel):
    kit_id: str
    kit_code: str
    kit_name: str
    description: Optional[str] = None
    status: ServiceStatus
    service_ids: List[str]
    services: Optional[List[ServiceResponse]] = None
    total_services: int = 0
    total_estimated_hours: float = 0.0
    total_price: Decimal = Decimal("0.00")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

---

### Component 2: Backend — LaborItem Model Update

- **Purpose**: Add optional `service_type_id` to LaborItem so future work orders can link labor to services for usage tracking
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/work_order.py`
- **Change**: Add one optional field to both `LaborItem` and `LaborItemCreate`:

```python
# Add to LaborItem class:
service_type_id: Optional[str] = Field(default=None, description="Service type ID for usage tracking")

# Add to LaborItemCreate class:
service_type_id: Optional[str] = Field(default=None, description="Service type ID for usage tracking")
```

- **Backward compatibility**: Field is `Optional` with `default=None`. All existing work orders deserialize correctly (missing field defaults to None). Existing API consumers sending work order payloads without `service_type_id` are unaffected.

---

### Component 3: Backend — ServiceMasterRepository

- **Purpose**: DynamoDB data access for services (extended service_types table) including denormalized usage stats
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/service_master_repository.py`
- **DynamoDB Table**: `service_types` (reuse existing)
- **Primary Key**: `service_type_id` (HASH)
- **Item types in this table** (single-table design):
  - Regular service items: `service_type_id` starts with `"svc"`
  - Counter item: `service_type_id = "COUNTER#service_code"`
  - Stats items: `service_type_id = "STATS#<actual_service_type_id>"`

**DynamoDB access patterns:**

| Operation | Key/Index | Query |
|---|---|---|
| Get service by ID | PK: `service_type_id` | `get_item(Key={service_type_id: id})` |
| List by category | GSI: `category-index` | `query(KeyCondition: category = :cat)` |
| List by status | GSI: `status-index` | `query(KeyCondition: status = :st)` |
| Get by service_code | GSI: `service_code-index` | `query(KeyCondition: service_code = :code)` |
| List all services | Table scan | `scan(FilterExpression: NOT begins_with(service_type_id, 'COUNTER#') AND NOT begins_with(service_type_id, 'STATS#'))` |
| Generate service_code | PK: `COUNTER#service_code` | Atomic increment |
| Increment usage stats | PK: `STATS#<service_type_id>` | Atomic increment usage_count + ADD revenue |
| Get usage stats for service | PK: `STATS#<service_type_id>` | `get_item` |
| Get all usage stats | Table scan with prefix | `scan(FilterExpression: begins_with(service_type_id, 'STATS#'))` |

**Key methods:**

```python
class ServiceMasterRepository:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table('service_types')

    def create(self, data: dict) -> dict:
        """Create service with dual-write for backward compat"""
        service_code = self.generate_service_code()
        item = {
            'service_type_id': f"svc_{uuid4().hex[:12]}",
            'service_code': service_code,
            # Dual-write: new + old field names
            'service_name': data['service_name'],
            'name': data['service_name'],  # backward compat
            'category': data['category'],
            'status': data.get('status', 'active'),
            'is_active': data.get('status', 'active') == 'active',  # backward compat
            'standard_price': data.get('standard_price'),
            'base_labor_price': data.get('standard_price'),  # backward compat
            'estimated_duration_hours': data.get('estimated_duration_hours'),
            'standard_duration_hours': data.get('estimated_duration_hours'),  # backward compat
            'service_interval_km': data.get('service_interval_km'),
            'maintenance_interval_km': data.get('service_interval_km'),  # backward compat
            'service_interval_months': data.get('service_interval_months'),
            'maintenance_interval_months': data.get('service_interval_months'),  # backward compat
            # New fields only
            'warranty_period': data.get('warranty_period'),
            'description': data.get('description'),
            'procedure_steps': data.get('procedure_steps'),
            'notes': data.get('notes'),
            'standard_parts': data.get('standard_parts'),
            'reference_materials': data.get('reference_materials'),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        self.table.put_item(Item=item)
        return item

    def get_by_id(self, service_type_id: str) -> Optional[dict]:
        response = self.table.get_item(Key={'service_type_id': service_type_id})
        item = response.get('Item')
        if item:
            # Read with fallback for name field
            item['service_name'] = item.get('service_name') or item.get('name')
            item['status'] = item.get('status') or ('active' if item.get('is_active', True) else 'inactive')
            item['estimated_duration_hours'] = item.get('estimated_duration_hours') or item.get('standard_duration_hours')
            item['standard_price'] = item.get('standard_price') or item.get('base_labor_price')
            item['service_interval_km'] = item.get('service_interval_km') or item.get('maintenance_interval_km')
            item['service_interval_months'] = item.get('service_interval_months') or item.get('maintenance_interval_months')
        return item

    def generate_service_code(self) -> str:
        response = self.table.update_item(
            Key={'service_type_id': 'COUNTER#service_code'},
            UpdateExpression='SET #val = if_not_exists(#val, :zero) + :incr',
            ExpressionAttributeNames={'#val': 'counter_value'},
            ExpressionAttributeValues={':zero': 0, ':incr': 1},
            ReturnValues='UPDATED_NEW'
        )
        count = int(response['Attributes']['counter_value'])
        return f"SRV-{count:03d}"

    def increment_usage_stats(self, service_type_id: str, revenue: Decimal) -> None:
        self.table.update_item(
            Key={'service_type_id': f'STATS#{service_type_id}'},
            UpdateExpression='SET usage_count = if_not_exists(usage_count, :zero) + :incr, '
                            'revenue_generated = if_not_exists(revenue_generated, :zero_dec) + :rev, '
                            'last_used_at = :now',
            ExpressionAttributeValues={
                ':zero': 0,
                ':incr': 1,
                ':zero_dec': Decimal('0'),
                ':rev': revenue,
                ':now': datetime.now(timezone.utc).isoformat()
            }
        )

    def get_usage_stats(self, service_type_id: str) -> dict:
        response = self.table.get_item(Key={'service_type_id': f'STATS#{service_type_id}'})
        return response.get('Item', {
            'usage_count': 0,
            'revenue_generated': Decimal('0'),
            'last_used_at': None
        })

    def get_all_usage_stats(self) -> list:
        """Scan STATS# items for dashboard KPI aggregation"""
        response = self.table.scan(
            FilterExpression=Attr('service_type_id').begins_with('STATS#')
        )
        return response.get('Items', [])

    def list_by_status(self, status: str, limit: int = 100) -> list:
        response = self.table.query(
            IndexName='status-index',
            KeyConditionExpression=Key('status').eq(status),
            Limit=limit
        )
        return [self._normalize_item(i) for i in response.get('Items', [])]

    def search(self, query: str = None, category: str = None, status: str = None, limit: int = 50) -> list:
        """Scan with filters. Excludes COUNTER# and STATS# items."""
        filter_parts = [
            ~Attr('service_type_id').begins_with('COUNTER#'),
            ~Attr('service_type_id').begins_with('STATS#')
        ]
        if category:
            filter_parts.append(Attr('category').eq(category))
        if status:
            filter_parts.append(Attr('status').eq(status))
        if query:
            filter_parts.append(
                Attr('service_name').contains(query) | Attr('name').contains(query) | Attr('service_code').contains(query)
            )
        filter_expr = filter_parts[0]
        for part in filter_parts[1:]:
            filter_expr = filter_expr & part
        response = self.table.scan(FilterExpression=filter_expr, Limit=limit)
        return [self._normalize_item(i) for i in response.get('Items', [])]

    def _normalize_item(self, item: dict) -> dict:
        """Apply field fallbacks for backward compat reads"""
        item['service_name'] = item.get('service_name') or item.get('name', '')
        item['status'] = item.get('status') or ('active' if item.get('is_active', True) else 'inactive')
        item['estimated_duration_hours'] = item.get('estimated_duration_hours') or item.get('standard_duration_hours')
        item['standard_price'] = item.get('standard_price') or item.get('base_labor_price')
        return item
```

- **Dependencies**: `boto3`, existing DynamoDB connection pattern from `BaseRepository`

---

### Component 4: Backend — ServiceKitRepository

- **Purpose**: DynamoDB data access for service kits (new table)
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/service_kit_repository.py`
- **DynamoDB Table**: `service_kits` (NEW)
- **Primary Key**: `kit_id` (HASH)
- **Item types**: regular kit items + `COUNTER#kit_code`

**DynamoDB access patterns:**

| Operation | Key/Index | Query |
|---|---|---|
| Get kit by ID | PK: `kit_id` | `get_item(Key={kit_id})` |
| Get by kit_code | GSI: `kit_code-index` | `query(KeyCondition: kit_code = :code)` |
| List by status | GSI: `status-index` | `query(KeyCondition: status = :st)` |
| List all kits | Table scan | `scan(FilterExpression: NOT begins_with(kit_id, 'COUNTER#'))` |
| Generate kit_code | PK: `COUNTER#kit_code` | Atomic increment |

**Key methods:**

```python
class ServiceKitRepository:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table('service_kits')

    def create(self, data: dict) -> dict
    def get_by_id(self, kit_id: str) -> Optional[dict]
    def list_all(self, limit: int = 50) -> list
    def list_by_status(self, status: str, limit: int = 50) -> list
    def update(self, kit_id: str, updates: dict) -> dict
    def delete(self, kit_id: str) -> None
    def generate_kit_code(self) -> str  # KIT-001, KIT-002...
```

- **Dependencies**: `boto3`, `BaseRepository` pattern

---

### Component 5: Backend — ServiceMasterService

- **Purpose**: Business logic — validation, code generation, stats aggregation, kit totals, dashboard KPIs
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/service_master_service.py`
- **Dependencies**: `ServiceMasterRepository`, `ServiceKitRepository`

**Key methods:**

```python
class ServiceMasterService:
    def __init__(self):
        self.repo = ServiceMasterRepository()
        self.kit_repo = ServiceKitRepository()

    # --- Services ---
    def create_service(self, data: ServiceCreate) -> ServiceResponse
    def get_service(self, service_type_id: str) -> ServiceResponse
    def list_services(self, category: str = None, status: str = None, search: str = None, limit: int = 50) -> dict
    def update_service(self, service_type_id: str, data: ServiceUpdate) -> ServiceResponse
    def deactivate_service(self, service_type_id: str) -> ServiceResponse

    # --- Dashboard ---
    def get_dashboard_kpis(self) -> ServiceDashboardKPIs
    def get_dashboard_alerts(self) -> List[ServiceAlert]
    def get_most_used_services(self, limit: int = 10) -> list

    # --- Usage ---
    def get_usage_stats(self, service_type_id: str) -> ServiceUsageStats
    def record_service_usage(self, service_type_id: str, revenue: Decimal) -> None

    # --- Kits ---
    def create_kit(self, data: ServiceKitCreate) -> ServiceKitResponse
    def get_kit(self, kit_id: str) -> ServiceKitResponse
    def list_kits(self, status: str = None, limit: int = 50) -> dict
    def update_kit(self, kit_id: str, data: ServiceKitUpdate) -> ServiceKitResponse
    def deactivate_kit(self, kit_id: str) -> ServiceKitResponse
```

**Dashboard KPI logic (reads from denormalized stats — NO work_orders scan):**

```python
def get_dashboard_kpis(self) -> ServiceDashboardKPIs:
    # Count services (exclude COUNTER# and STATS# items)
    all_services = self.repo.search(limit=500)
    total = len(all_services)
    active = sum(1 for s in all_services if s.get('status') == 'active')
    inactive = total - active

    # Get usage stats from STATS# items
    all_stats = self.repo.get_all_usage_stats()
    total_revenue = sum(Decimal(str(s.get('revenue_generated', 0))) for s in all_stats)

    # Find most used service
    most_used = None
    most_used_count = 0
    for stat in all_stats:
        count = int(stat.get('usage_count', 0))
        if count > most_used_count:
            most_used_count = count
            # Extract service_type_id from STATS#<id>
            sid = stat['service_type_id'].replace('STATS#', '')
            service = self.repo.get_by_id(sid)
            most_used = service.get('service_name') if service else None

    return ServiceDashboardKPIs(
        total_services=total,
        active_services=active,
        inactive_services=inactive,
        most_used_service=most_used,
        most_used_service_count=most_used_count,
        total_revenue=total_revenue
    )
```

**Dashboard alerts logic:**
- Services with `status=active` and no corresponding STATS# item (or `usage_count=0`) created >30 days ago → severity "medium", alert_type "Unused Service"
- Services with `standard_price` is None → severity "low", alert_type "Missing Pricing"
- Services with `procedure_steps` is None or empty → severity "low", alert_type "Missing Procedure"

---

### Component 6: Backend — Routes

- **Purpose**: REST API endpoints for the Service Master module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/service_master.py`
- **Blueprint**: `service_master_bp` registered at `/api/service-master`
- **Registration**: Add to app factory in `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py`

**Endpoints:**

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| GET | `/api/service-master/dashboard` | KPIs + alerts + chart data | — | `{data: {kpis, alerts, most_used_chart}}` |
| GET | `/api/service-master/services` | List/search catalog | Query: `?category=&status=&search=&limit=50` | `{data: {items: [...], total, kpis}}` |
| GET | `/api/service-master/services/<id>` | Service detail | — | `{data: ServiceResponse}` |
| POST | `/api/service-master/services` | Create service | Body: `ServiceCreate` | `{data: ServiceResponse}` (201) |
| PUT | `/api/service-master/services/<id>` | Update service | Body: `ServiceUpdate` | `{data: ServiceResponse}` |
| PUT | `/api/service-master/services/<id>/deactivate` | Deactivate | — | `{data: ServiceResponse}` |
| GET | `/api/service-master/services/<id>/usage` | Usage stats | — | `{data: ServiceUsageStats}` |
| GET | `/api/service-master/kits` | List kits | Query: `?status=&limit=50` | `{data: {items: [...], total}}` |
| GET | `/api/service-master/kits/<id>` | Kit detail (with resolved services) | — | `{data: ServiceKitResponse}` |
| POST | `/api/service-master/kits` | Create kit | Body: `ServiceKitCreate` | `{data: ServiceKitResponse}` (201) |
| PUT | `/api/service-master/kits/<id>` | Update kit | Body: `ServiceKitUpdate` | `{data: ServiceKitResponse}` |
| PUT | `/api/service-master/kits/<id>/deactivate` | Deactivate kit | — | `{data: ServiceKitResponse}` |

All endpoints use `@require_auth` decorator.

**Error responses follow existing pattern:**
```python
{"error": {"code": "SERVICE_NOT_FOUND", "message": "Service not found"}}  # 404
{"error": {"code": "VALIDATION_ERROR", "message": "...", "details": [...]}}  # 422
{"error": {"code": "INTERNAL_ERROR", "message": "..."}}  # 500
```

---

### Component 7: Backend — Work Order Hook for Usage Tracking

- **Purpose**: Increment service usage stats when a work order is created/updated with `service_type_id` in labor items
- **Files**:
  - `/home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/work_order_service.py` (modify existing — add post-create hook)
- **Change**: After successful work order creation, iterate `labor_items`. For each item with a non-null `service_type_id`, call `ServiceMasterService.record_service_usage(service_type_id, item.total)`.
- **Backward compatibility**: Only triggers if `service_type_id` is present in a labor item. Existing work orders without the field are completely unaffected. The hook is additive — no existing behavior is modified.

```python
# In work_order_service.py, after successful create:
def _update_service_usage_stats(self, labor_items: list):
    """Increment denormalized usage stats for services referenced in labor items."""
    from app.services.service_master_service import ServiceMasterService
    svc = ServiceMasterService()
    for item in labor_items:
        if item.get('service_type_id'):
            svc.record_service_usage(item['service_type_id'], Decimal(str(item.get('total', 0))))
```

---

### Component 8: React — TypeScript Types

- **Purpose**: Type definitions for the Service Master module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/types/serviceMaster.ts`
- **Dependencies**: None (pure types)

```typescript
export type ServiceCategory =
  | 'maintenance'
  | 'brakes'
  | 'tires'
  | 'transmission'
  | 'electrical'
  | 'ac_heating'
  | 'inspection'
  | 'engine'
  | 'body_work';

export type ServiceStatus = 'active' | 'inactive';

export interface ProcedureStep {
  step: number;
  description: string;
  notes?: string;
}

export interface StandardPart {
  part_id?: string;
  part_name: string;
  part_number?: string;
  quantity: number;
  unit: string;
  notes?: string;
}

export interface ReferenceMaterial {
  title: string;
  type: string;
  url: string;
}

export interface Service {
  service_type_id: string;
  service_code: string;
  service_name: string;
  category: ServiceCategory;
  status: ServiceStatus;
  description?: string;
  standard_price?: number;
  estimated_duration_hours?: number;
  warranty_period?: string;
  service_interval_km?: number;
  service_interval_months?: number;
  procedure_steps?: ProcedureStep[];
  notes?: string;
  standard_parts?: StandardPart[];
  reference_materials?: ReferenceMaterial[];
  usage_count: number;
  revenue_generated: number;
  last_used_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ServiceDashboardKPIs {
  total_services: number;
  active_services: number;
  inactive_services: number;
  most_used_service?: string;
  most_used_service_count: number;
  total_revenue: number;
}

export interface ServiceAlert {
  service_type_id: string;
  service_name: string;
  service_code: string;
  severity: 'high' | 'medium' | 'low';
  alert_type: string;
  message: string;
}

export interface ServiceUsageStats {
  service_type_id: string;
  usage_count: number;
  revenue_generated: number;
  last_used_at?: string;
}

export interface ServiceKit {
  kit_id: string;
  kit_code: string;
  kit_name: string;
  description?: string;
  status: ServiceStatus;
  service_ids: string[];
  services?: Service[];
  total_services: number;
  total_estimated_hours: number;
  total_price: number;
  created_at?: string;
  updated_at?: string;
}

export interface ServiceCreatePayload {
  service_name: string;
  category: ServiceCategory;
  status?: ServiceStatus;
  description?: string;
  standard_price?: number;
  estimated_duration_hours?: number;
  warranty_period?: string;
  service_interval_km?: number;
  service_interval_months?: number;
  procedure_steps?: ProcedureStep[];
  notes?: string;
  standard_parts?: StandardPart[];
  reference_materials?: ReferenceMaterial[];
}

export interface ServiceUpdatePayload extends Partial<ServiceCreatePayload> {}

export interface ServiceKitCreatePayload {
  kit_name: string;
  description?: string;
  status?: ServiceStatus;
  service_ids: string[];
}

export interface ServiceKitUpdatePayload extends Partial<ServiceKitCreatePayload> {}

export interface DashboardResponse {
  kpis: ServiceDashboardKPIs;
  alerts: ServiceAlert[];
  most_used_chart: Array<{ service_name: string; usage_count: number }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
```

---

### Component 9: React — API Service Layer

- **Purpose**: Axios API calls for Service Master module
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/serviceMasterService.ts`
- **Dependencies**: `@/services/api.ts` (existing Axios instance with JWT interceptor)

```typescript
import api from '@/services/api';
import type {
  Service, ServiceKit, DashboardResponse, ServiceUsageStats,
  ServiceCreatePayload, ServiceUpdatePayload,
  ServiceKitCreatePayload, ServiceKitUpdatePayload,
  PaginatedResponse, ServiceDashboardKPIs,
} from '@/types/serviceMaster';

const BASE = '/api/service-master';

export const serviceMasterApi = {
  // Dashboard
  getDashboard: () =>
    api.get<{ data: DashboardResponse }>(`${BASE}/dashboard`),

  // Services
  listServices: (params?: { category?: string; status?: string; search?: string; limit?: number }) =>
    api.get<{ data: { items: Service[]; total: number; kpis: ServiceDashboardKPIs } }>(`${BASE}/services`, { params }),

  getService: (id: string) =>
    api.get<{ data: Service }>(`${BASE}/services/${id}`),

  createService: (data: ServiceCreatePayload) =>
    api.post<{ data: Service }>(`${BASE}/services`, data),

  updateService: (id: string, data: ServiceUpdatePayload) =>
    api.put<{ data: Service }>(`${BASE}/services/${id}`, data),

  deactivateService: (id: string) =>
    api.put<{ data: Service }>(`${BASE}/services/${id}/deactivate`),

  getUsageStats: (id: string) =>
    api.get<{ data: ServiceUsageStats }>(`${BASE}/services/${id}/usage`),

  // Kits
  listKits: (params?: { status?: string; limit?: number }) =>
    api.get<{ data: { items: ServiceKit[]; total: number } }>(`${BASE}/kits`, { params }),

  getKit: (id: string) =>
    api.get<{ data: ServiceKit }>(`${BASE}/kits/${id}`),

  createKit: (data: ServiceKitCreatePayload) =>
    api.post<{ data: ServiceKit }>(`${BASE}/kits`, data),

  updateKit: (id: string, data: ServiceKitUpdatePayload) =>
    api.put<{ data: ServiceKit }>(`${BASE}/kits/${id}`, data),

  deactivateKit: (id: string) =>
    api.put<{ data: ServiceKit }>(`${BASE}/kits/${id}/deactivate`),
};
```

---

### Component 10: React — Custom Hooks

- **Purpose**: TanStack Query hooks for data fetching with 60s auto-refresh
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useServiceMaster.ts`
- **Dependencies**: `@tanstack/react-query`, `@/services/serviceMasterService`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceMasterApi } from '@/services/serviceMasterService';
import type { ServiceCreatePayload, ServiceUpdatePayload, ServiceKitCreatePayload, ServiceKitUpdatePayload } from '@/types/serviceMaster';

const STALE_TIME = 60_000; // 60s auto-refresh

// --- Dashboard ---
export function useServiceDashboard() {
  return useQuery({
    queryKey: ['service-master', 'dashboard'],
    queryFn: () => serviceMasterApi.getDashboard().then(r => r.data.data),
    staleTime: STALE_TIME,
  });
}

// --- Services ---
export function useServices(params?: { category?: string; status?: string; search?: string }) {
  return useQuery({
    queryKey: ['service-master', 'services', params],
    queryFn: () => serviceMasterApi.listServices(params).then(r => r.data.data),
    staleTime: STALE_TIME,
  });
}

export function useService(id: string) {
  return useQuery({
    queryKey: ['service-master', 'services', id],
    queryFn: () => serviceMasterApi.getService(id).then(r => r.data.data),
    staleTime: STALE_TIME,
    enabled: !!id,
  });
}

export function useServiceUsage(id: string) {
  return useQuery({
    queryKey: ['service-master', 'services', id, 'usage'],
    queryFn: () => serviceMasterApi.getUsageStats(id).then(r => r.data.data),
    staleTime: STALE_TIME,
    enabled: !!id,
  });
}

export function useCreateService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ServiceCreatePayload) => serviceMasterApi.createService(data).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-master'] }),
  });
}

export function useUpdateService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ServiceUpdatePayload }) =>
      serviceMasterApi.updateService(id, data).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-master'] }),
  });
}

export function useDeactivateService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => serviceMasterApi.deactivateService(id).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-master'] }),
  });
}

// --- Kits ---
export function useServiceKits(params?: { status?: string }) {
  return useQuery({
    queryKey: ['service-master', 'kits', params],
    queryFn: () => serviceMasterApi.listKits(params).then(r => r.data.data),
    staleTime: STALE_TIME,
  });
}

export function useServiceKit(id: string) {
  return useQuery({
    queryKey: ['service-master', 'kits', id],
    queryFn: () => serviceMasterApi.getKit(id).then(r => r.data.data),
    staleTime: STALE_TIME,
    enabled: !!id,
  });
}

export function useCreateKit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ServiceKitCreatePayload) => serviceMasterApi.createKit(data).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-master', 'kits'] }),
  });
}

export function useUpdateKit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ServiceKitUpdatePayload }) =>
      serviceMasterApi.updateKit(id, data).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-master', 'kits'] }),
  });
}

export function useDeactivateKit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => serviceMasterApi.deactivateKit(id).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['service-master', 'kits'] }),
  });
}
```

---

### Component 11: React — Pages & Layout

- **Purpose**: Page components and layout with sub-navigation
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceMasterLayout.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceDashboardPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceCatalogPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceInformationPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/NewServicePage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceKitsPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/ServiceKitDetailPage.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/service-master/NewServiceKitPage.tsx`
- **Dependencies**: React Router v6, TanStack Query hooks, Tailwind CSS

**Layout sub-navigation items** (from screen designs):
- Service Dashboard → `/service-master` (icon: LayoutDashboard)
- Service Catalog → `/service-master/catalog` (icon: BookOpen)
- Service Categories → `/service-master/categories` (placeholder page for MVP)
- Service Procedures → `/service-master/procedures` (placeholder page for MVP)
- Service Kits → `/service-master/kits` (icon: Package)
- Reports & Analytics → `/service-master/analytics` (placeholder page for MVP)

**Route structure** (add to existing router config in App.tsx):
```typescript
{
  path: '/service-master',
  element: <ServiceMasterLayout />,
  children: [
    { index: true, element: <ServiceDashboardPage /> },
    { path: 'catalog', element: <ServiceCatalogPage /> },
    { path: 'services/new', element: <NewServicePage /> },
    { path: 'services/:id', element: <ServiceInformationPage /> },
    { path: 'services/:id/edit', element: <NewServicePage /> },
    { path: 'kits', element: <ServiceKitsPage /> },
    { path: 'kits/new', element: <NewServiceKitPage /> },
    { path: 'kits/:id', element: <ServiceKitDetailPage /> },
    { path: 'kits/:id/edit', element: <NewServiceKitPage /> },
    { path: 'categories', element: <PlaceholderPage title="Service Categories" /> },
    { path: 'procedures', element: <PlaceholderPage title="Service Procedures" /> },
    { path: 'analytics', element: <PlaceholderPage title="Reports & Analytics" /> },
  ]
}
```

---

### Component 12: React — Dashboard Components

- **Purpose**: KPI cards, alerts panel, usage chart, performance table for dashboard page
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceKPICards.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceAlertsPanel.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/MostUsedServicesChart.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServicePerformanceTable.tsx`
- **Dependencies**: Recharts (BarChart horizontal), TanStack Table, Tailwind

**KPI Cards** (4 cards in a responsive grid):
1. Total Services — count with blue icon, "View Service Catalog" link
2. Active Categories — count with orange icon, "View Categories" link
3. Most Used Service — name + count with green icon, "View Analytics" link
4. Average Service Duration — hours with red icon

**Alerts Panel**: Table with columns: Severity (icon/badge), Alert Type, Message. Clickable rows navigate to service detail.

**Most Used Services Chart**: Recharts horizontal BarChart showing top 10 services by usage_count. Dark blue bars, service names on Y-axis.

**Performance Table**: TanStack Table with sortable columns: Service Code, Service Name, Category, Labor Cost, Est. Time, No. of Jobs (usage_count), Revenue, Status. Pagination.

---

### Component 13: React — Catalog Components

- **Purpose**: Searchable/filterable service catalog
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceCatalogTable.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceCatalogFilters.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceCatalogKPIs.tsx`
- **Dependencies**: TanStack Table, Tailwind

**Filters**: Search input (debounced 300ms), Category dropdown (All + 9 categories), Status toggle (All/Active/Inactive), "More Filters" button

**Table columns**: Service Code, Service Name, Category (badge), Estimated Hours, Labor Cost, Suggested Price, Status (green/orange badge), Last Updated

**KPI row above table**: Total Services, Active Services, Inactive Services, Categories count

---

### Component 14: React — Service Detail & Form Components

- **Purpose**: Service information view and create/edit form
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceDetailHeader.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceBasicInfoSection.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceProcedureEditor.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServicePartsEditor.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceReferencesEditor.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceUsageSection.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceForm.tsx`
- **Dependencies**: Tailwind, controlled form components

**Service Form sections** (from screen4.png):
1. Basic Service Information — Service Code (auto, read-only), Service Name, Category dropdown, Status dropdown, Description textarea
2. Pricing — Standard Price, Estimated Duration Hours, Warranty Period
3. Intervals — Service Interval KM, Service Interval Months
4. Standard Parts — Dynamic list with "+ Add Part" button, part name search, quantity, unit, notes
5. Service Procedure (SOP) — Dynamic ordered list with "+ Add Step" button, step description, notes
6. Reference Materials — Dynamic list with title, type dropdown, URL
7. Service Notes — Optional textarea

**Detail page (view mode)** sections:
- Header: service_code badge, service_name, category badge, status badge, "Edit" / "Deactivate" buttons
- Summary: price, duration, warranty, interval, description
- Standard Parts table
- Procedure steps (numbered list)
- Reference Materials (clickable links)
- Usage Stats section with note: "Usage data tracks work orders created after feature deployment"

**Edit mode**: Toggle via "Edit" button → fields become editable → "Save" button enables

---

### Component 15: React — Service Kits Components

- **Purpose**: Kit listing, detail view, and creation form
- **Files**:
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceKitCard.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceKitForm.tsx`
  - `/home/ubuntu/greasynuts/dev/GreasyNutsReact/src/components/service-master/ServiceSelector.tsx`
- **Dependencies**: Tailwind

**Kit Form:**
- Kit Name, Description, Status
- Service Selector: searchable multi-select from active services catalog (checkboxes)
- Selected services table: shows service_code, name, description, estimated_hours
- Kit Summary: auto-calculated totals (Total Services, Total Estimated Hours, Total Price)

**Kit Detail page** (from screen2.png):
- Header: kit_code, kit_name, status badge, "Edit Kit" / "Delete Kit" buttons
- Kit Information section: name, code, description, status, created/updated dates
- Services Included table: #, Service Code, Service Name, Description, Estimated Hours
- Kit Summary: 3 metric cards (Total Services, Total Hours, Total Price)

---

## DynamoDB Schema Changes

### Table: `service_types` (EXISTING — extended)

**Primary Key**: `service_type_id` (HASH)

**Item types (single-table design):**
1. Service items: `service_type_id` starts with `"svc"` (existing pattern)
2. Counter item: `service_type_id = "COUNTER#service_code"` (NEW)
3. Stats items: `service_type_id = "STATS#<service_type_id>"` (NEW)

**Fields on service items:**

| Field | Type | New? | Notes |
|---|---|---|---|
| `service_type_id` | String (PK) | No | Existing primary key, prefix "svc" |
| `name` | String | No | Existing — kept for backward compat |
| `service_name` | String | **Yes** | Canonical name (dual-write with `name`) |
| `service_code` | String | **Yes** | Auto-generated `SRV-XXX` |
| `category` | String | No | Existing. Values: `maintenance, brakes, tires, transmission, electrical, ac_heating, inspection, engine, body_work` |
| `status` | String | **Yes** | `active` or `inactive` (dual-write with `is_active`) |
| `is_active` | Boolean | No | Existing — kept for backward compat |
| `standard_price` | Number | **Yes** | Price (dual-write with `base_labor_price`) |
| `base_labor_price` | Number | No | Existing — kept for backward compat |
| `estimated_duration_hours` | Number | **Yes** | Duration (dual-write with `standard_duration_hours`) |
| `standard_duration_hours` | Number | No | Existing — kept for backward compat |
| `service_interval_km` | Number | **Yes** | KM interval (dual-write with `maintenance_interval_km`) |
| `maintenance_interval_km` | Number | No | Existing — kept for backward compat |
| `service_interval_months` | Number | **Yes** | Month interval (dual-write with `maintenance_interval_months`) |
| `maintenance_interval_months` | Number | No | Existing — kept for backward compat |
| `description` | String | **Yes** | Service description |
| `warranty_period` | String | **Yes** | e.g., "3 months", "1 year" |
| `procedure_steps` | List | **Yes** | `[{step, description, notes}]` |
| `notes` | String | **Yes** | Free-text notes |
| `standard_parts` | List | **Yes** | `[{part_id, part_name, part_number, quantity, unit, notes}]` |
| `reference_materials` | List | **Yes** | `[{title, type, url}]` |
| `created_at` | String | No | Existing |
| `updated_at` | String | No | Existing |

**Fields on COUNTER# item:**

| Field | Type | Notes |
|---|---|---|
| `service_type_id` | String (PK) | Value: `"COUNTER#service_code"` |
| `counter_value` | Number | Atomic increment for SRV-XXX generation |

**Fields on STATS# items:**

| Field | Type | Notes |
|---|---|---|
| `service_type_id` | String (PK) | Value: `"STATS#<actual_service_type_id>"` |
| `usage_count` | Number | Times this service was used in work orders |
| `revenue_generated` | Number | Total revenue from this service |
| `last_used_at` | String | ISO timestamp of last usage |

**GSIs on `service_types` (total: 3 of 5 max):**

| GSI Name | Partition Key | Sort Key | Status | Purpose |
|---|---|---|---|---|
| `category-index` | `category` | — | EXISTING | Filter by category |
| `status-index` | `status` | `created_at` | **NEW** | Filter active/inactive services |
| `service_code-index` | `service_code` | — | **NEW** | Lookup by service code |

---

### Table: `service_kits` (NEW)

**Primary Key**: `kit_id` (HASH)

**Item types:**
1. Kit items: `kit_id` starts with `"kit"` prefix
2. Counter item: `kit_id = "COUNTER#kit_code"`

**Fields on kit items:**

| Field | Type | Notes |
|---|---|---|
| `kit_id` | String (PK) | Auto-generated UUID with "kit" prefix |
| `kit_code` | String | Auto-generated `KIT-XXX` |
| `kit_name` | String | Kit display name |
| `description` | String | Optional description |
| `status` | String | `active` or `inactive` |
| `service_ids` | List[String] | References to `service_type_id` values |
| `total_services` | Number | Denormalized count |
| `total_estimated_hours` | Number | Denormalized sum of service durations |
| `total_price` | Number | Denormalized sum of service prices |
| `created_at` | String | ISO timestamp |
| `updated_at` | String | ISO timestamp |

**Fields on COUNTER# item:**

| Field | Type | Notes |
|---|---|---|
| `kit_id` | String (PK) | Value: `"COUNTER#kit_code"` |
| `counter_value` | Number | Atomic increment for KIT-XXX generation |

**GSIs on `service_kits` (total: 2 of 5 max):**

| GSI Name | Partition Key | Sort Key | Purpose |
|---|---|---|---|
| `kit_code-index` | `kit_code` | — | Lookup by kit code |
| `status-index` | `status` | `created_at` | Filter by status |

---

## UX Interaction Flow

### Flow 1: Service Dashboard (Landing)

1. User clicks "Service Master" in main sidebar → navigates to `/service-master`
2. Sub-navigation appears on left with active "Dashboard" item
3. **Loading state**: Skeleton placeholders for KPI cards (4 gray rectangles), alerts table (5 gray rows), chart area, performance table
4. Data arrives → KPI cards animate in: Total Services, Active Categories, Most Used Service, Avg Duration
5. **If usage data is empty** (fresh deployment): Most Used Service card shows "—" with tooltip: "Usage tracking begins with new work orders"
6. Alerts panel shows actionable items with severity badges; clicking a row navigates to `/service-master/services/:id`
7. Most Used Services chart renders (Recharts horizontal bars); hover shows tooltip with exact count
8. Performance table populates with sortable columns; clicking a row navigates to service detail
9. Pagination at bottom: "Showing 1 to X of Y services"

### Flow 2: Service Catalog

1. User clicks "Service Catalog" in sub-nav → navigates to `/service-master/catalog`
2. **Loading**: Skeleton for filter bar, KPI row, and table
3. Page shows: breadcrumb "Service Master > Service Catalog", blue "Add Service" button top-right
4. Filter bar: search input + category dropdown + status toggle + "More Filters"
5. KPI row: Total Services, Active, Inactive, Categories count
6. Table renders all services (default: no filters applied)
7. User types in search → 300ms debounce → API call with `?search=` → table updates
8. User selects category "maintenance" → API call with `?category=maintenance` → table filters
9. User clicks a table row → navigates to `/service-master/services/:id`
10. User clicks "Add Service" button → navigates to `/service-master/services/new`
11. **Empty state** (no services match filter): "No services found matching your criteria" with "Clear Filters" button

### Flow 3: Create New Service

1. User navigates to `/service-master/services/new` (from catalog or direct)
2. Form loads with: "← Back to Service Catalog" link, "New Service Information" heading
3. Service Code field shows "SRV-XXX — Auto Generated" (read-only, greyed)
4. User fills required fields: Service Name, Category (dropdown with 9 options)
5. User fills optional fields: Price, Duration, Warranty, Description, etc.
6. **Procedure Steps**: User clicks "+ Add Step" → new numbered row appears → enters description + optional notes → can reorder/remove
7. **Standard Parts**: User clicks "+ Add Part" → row appears → types part name (no autocomplete in MVP — free text) → sets quantity/unit
8. **Reference Materials**: User clicks "+ Add Reference" → title + type dropdown (PDF Manual, Video Tutorial, OEM Procedure, Internal SOP) + URL
9. **Notes**: Optional textarea
10. User clicks "Save Service" → button shows loading spinner, form fields disabled
11. **Success (201)**: Toast "Service SRV-XXX created successfully" → redirect to `/service-master/services/:newId`
12. **Validation error (422)**: Inline errors shown on specific fields (red border + message), form re-enabled
13. **Server error (500)**: Toast "Failed to create service. Please try again." → form re-enabled
14. User clicks "Cancel" → navigates back to catalog (confirm if form is dirty)

### Flow 4: Service Information (View/Edit)

1. User navigates to `/service-master/services/:id` → **loading**: skeleton for header + sections
2. Header renders: service_code badge (e.g., "SRV-001"), service_name, category badge, status badge
3. Action buttons: "Edit Service" (blue), "Deactivate" (outline/red)
4. Sections render: Summary (price, duration, warranty, intervals, description), Standard Parts (table), Procedure (numbered steps), References (link list), Usage Stats
5. **Usage Stats section**: Shows usage_count, revenue_generated, last_used_at. If all zero: "No usage data yet. Usage tracking begins with new work orders that reference this service."
6. **Edit mode**: User clicks "Edit Service" → fields become editable (inputs replace text), "Save" button appears (blue), "Cancel" appears
7. User modifies fields → clicks "Save" → PUT request → success toast → reverts to view mode with updated data
8. **Deactivate**: User clicks "Deactivate" → confirmation modal ("Are you sure? This service will no longer appear in active searches.") → on confirm: PUT request → status badge changes to "Inactive" orange badge → toast "Service deactivated"
9. **404**: If service not found, show "Service not found" page with "Back to Catalog" link

### Flow 5: Service Kits

1. User clicks "Service Kits" in sub-nav → navigates to `/service-master/kits`
2. Page shows: "Service Kits" heading, subtitle, "Create Service Kit" blue button
3. KPI row: Total Kits, Active Kits, Inactive Kits, Total Services in Kits
4. Table: Kit Code, Kit Name, Description, Services (count), Total Hours, Status, Last Updated
5. User clicks "Create Service Kit" → navigates to `/service-master/kits/new`
6. **Kit create form**: Kit Name, Description, Status dropdown
7. **Service selector**: Searchable list of active services with checkboxes. Selected services appear in a "Services Included" panel showing service_code, name, hours. Running totals update (Total Services, Total Hours, Total Price)
8. User clicks "Save Kit" → POST request → success → redirect to `/service-master/kits/:newId`
9. User clicks existing kit row in table → navigates to `/service-master/kits/:id` (detail)
10. **Kit detail**: Header with kit_code, name, status. Sections: Kit Information, Services Included table, Kit Summary cards. Action buttons: "Edit Kit", "Delete Kit"
11. **Delete Kit**: Confirmation modal → on confirm: DELETE request → redirect to kits list → toast "Kit deleted"

### Error States (all flows):
- **Network error**: TanStack Query auto-retries 3 times with exponential backoff. If all fail: red banner "Unable to load data. Check your connection and try again." with "Retry" button
- **Auth expired (401)**: Axios interceptor redirects to login page
- **404**: "Not found" page with navigation back
- **Rate limit (429)**: Handled by TanStack Query retry logic

### Loading States:
- All pages: skeleton placeholders matching expected layout dimensions
- Mutations: button shows spinner + disabled state, form fields disabled
- Auto-refresh: silent background refetch every 60s (no visible loading indicator for background refreshes)

---

## System Component Assessment

| Component | Required? | Justification |
|---|---|---|
| WebSocket / real-time | **NO** | Service master is configuration/reference data. TanStack Query 60s auto-refresh is sufficient. No collaborative editing scenario. |
| Background job / queue | **NO** | All operations are fast CRUD. Usage stats are updated atomically inline (single DynamoDB UpdateItem). No batch processing needed. |
| Cache (Redis) | **NO** | Dashboard KPIs read from denormalized STATS# items (not work_order scans). With <500 services, all queries complete in <500ms. No cache layer needed for MVP. |
| File storage (S3) | **NO** | Reference materials store URLs only (links to external docs). Screen4 "Upload Procedure Doc" is treated as a link/URL input for MVP, not actual file upload. |
| Third-party API | **NO** | No SMS, email, payment, or maps needed. All data is internal to the garage system. |
| Search engine (OpenSearch) | **NO** | Service catalog uses DynamoDB scan with `contains` filter. With <500 services, scan completes in <500ms. Full-text search not needed. |

## Architect Escalation

*(None — all components are NO)*

---

## Seed Data Strategy

**1. Service code counter initialization:**

```python
# One-time: initialize counter based on existing service count
existing_count = len(service_type_repository.list_all_active())
table.put_item(Item={
    'service_type_id': 'COUNTER#service_code',
    'counter_value': existing_count
})
```

**2. Backfill existing services with new fields:**

```python
# One-time migration script
# /home/ubuntu/greasynuts/dev/backend/GreasyNuts/scripts/migrate_service_master.py

counter = 0
for item in existing_service_type_items:
    counter += 1
    table.update_item(
        Key={'service_type_id': item['service_type_id']},
        UpdateExpression='SET service_code = :code, service_name = :name, #st = :status',
        ExpressionAttributeNames={'#st': 'status'},
        ExpressionAttributeValues={
            ':code': f'SRV-{counter:03d}',
            ':name': item.get('name', ''),
            ':status': 'active' if item.get('is_active', True) else 'inactive'
        }
    )
# Update counter to match
table.put_item(Item={
    'service_type_id': 'COUNTER#service_code',
    'counter_value': counter
})
```

**3. Kit counter initialization:**

```python
kit_table.put_item(Item={
    'kit_id': 'COUNTER#kit_code',
    'counter_value': 0
})
```

**4. New categories**: `engine` and `body_work` are valid immediately (categories are just string values matched by the Pydantic enum, no category table exists). Existing seed data categories (`maintenance, brakes, tires, transmission, electrical, ac_heating, inspection`) remain unchanged and valid.

---

## Implementation Phases

### Phase 1: Backend Foundation (2-3 days)
1. Create `/app/models/service_master.py` — all Pydantic models with correct category enum
2. Update `/app/models/work_order.py` — add optional `service_type_id` to `LaborItem` and `LaborItemCreate`
3. Create `/app/repositories/service_master_repository.py` — CRUD + code generation + stats + dual-write
4. Create `/app/repositories/service_kit_repository.py` — kit CRUD + code generation
5. Create `/app/services/service_master_service.py` — business logic + dashboard KPIs from STATS# items
6. Create `/app/routes/service_master.py` — all endpoints with `@require_auth`
7. Register blueprint in `/app/__init__.py`
8. Add usage tracking hook to work_order_service.py
9. Create DynamoDB table `service_kits` + add GSIs to `service_types`
10. Run migration script: backfill existing services with service_code, service_name, status

### Phase 2: React Service Layer (1 day)
1. Create `/src/types/serviceMaster.ts` — TypeScript interfaces
2. Create `/src/services/serviceMasterService.ts` — API calls
3. Create `/src/hooks/useServiceMaster.ts` — TanStack Query hooks

### Phase 3: React UI — Layout & Navigation (1 day)
1. Create `ServiceMasterLayout.tsx` with sub-navigation
2. Add routes to router config in `App.tsx`
3. Add "Service Master" item to main sidebar
4. Create placeholder pages for Categories, Procedures, Analytics

### Phase 4: React UI — Dashboard (2 days)
1. `ServiceKPICards.tsx` — 4 KPI cards with icons and links
2. `ServiceAlertsPanel.tsx` — alerts table with severity, clickable rows
3. `MostUsedServicesChart.tsx` — Recharts horizontal BarChart
4. `ServicePerformanceTable.tsx` — TanStack Table with pagination
5. `ServiceDashboardPage.tsx` — compose all dashboard components

### Phase 5: React UI — Catalog & Detail (2-3 days)
1. `ServiceCatalogFilters.tsx` — search, category, status filters
2. `ServiceCatalogKPIs.tsx` — mini KPI row
3. `ServiceCatalogTable.tsx` — full data table with pagination
4. `ServiceCatalogPage.tsx` — compose catalog components
5. `ServiceDetailHeader.tsx` — code badge, name, status, action buttons
6. `ServiceBasicInfoSection.tsx` — summary fields (view + edit modes)
7. `ServiceUsageSection.tsx` — usage stats with informational note
8. `ServiceInformationPage.tsx` — compose detail sections

### Phase 6: React UI — Create/Edit Service & Kits (2-3 days)
1. `ServiceProcedureEditor.tsx` — dynamic ordered step list
2. `ServicePartsEditor.tsx` — dynamic parts list (free-text part name for MVP)
3. `ServiceReferencesEditor.tsx` — dynamic reference list with type dropdown
4. `ServiceForm.tsx` — full form composition (used for both create and edit)
5. `NewServicePage.tsx` — wraps ServiceForm with create/edit logic
6. `ServiceSelector.tsx` — searchable multi-select for kits
7. `ServiceKitForm.tsx` — kit form with service selector and running totals
8. `ServiceKitCard.tsx` — kit summary card component
9. `ServiceKitsPage.tsx` — kit listing with KPIs and table
10. `ServiceKitDetailPage.tsx` — kit detail with services table
11. `NewServiceKitPage.tsx` — kit creation/edit form

### Phase 7: Work Order Integration (0.5 days)
1. Update work_order_service.py to call `_update_service_usage_stats()` after work order creation
2. Manual test: create a work order with `service_type_id` in a labor item → verify STATS# item is created/incremented

---

## Risks and Concerns

1. **Risk: DynamoDB scan for "list all services" with COUNTER# and STATS# items in same table**
   - Mitigation: FilterExpression excludes items where `service_type_id` begins with `COUNTER#` or `STATS#`. With <500 service items + <500 stats items + 1 counter item, scan is fast (<1s). FilterExpression is applied server-side by DynamoDB, so only matching items are returned.

2. **Risk: Existing `/api/service-types` endpoints break after schema changes**
   - Mitigation: Dual-write ensures all old field names are always present. The existing `ServiceTypeRepository` is NOT modified — it continues reading `name`, `is_active`, `standard_duration_hours`, etc. Only the new `ServiceMasterRepository` uses the new field names. New fields are purely additive.

3. **Risk: Usage stats drift from actual work orders (no correction on WO deletion/modification)**
   - Mitigation: Accepted trade-off for MVP. Stats only increment (never decrement). If a work order is deleted after creation, the stat is not rolled back. Acceptable because: (a) work order deletion is rare in garage workflows, (b) stats are directionally correct for dashboard purposes. Future enhancement: add decrement on WO deletion, or nightly reconciliation.

4. **Risk: STATS# items accumulate for deleted/deactivated services**
   - Mitigation: STATS# items are tiny (3 fields) and bounded by total service count. Even with 1000 services over the lifetime of the system, this is negligible storage. No cleanup needed.

5. **Risk: Service code format collision if counter is manually tampered with**
   - Mitigation: Counter item is internal (not exposed via API). DynamoDB conditional writes ensure atomic increment. Codes are append-only and never reused even if services are deleted.

6. **Risk: Category mismatch between old UI and new UI**
   - Mitigation: Both old and new UIs read from the same `category` field. The new enum includes all 7 existing categories + 2 new ones. Old records with `maintenance`, `brakes`, etc. are valid enum values. No migration needed.

---

## Confidence: 88%

**High confidence because:**
- All architect blockers resolved with concrete, implementable solutions
- Category enum exactly matches existing codebase values (lowercase: `maintenance, brakes, tires, transmission, electrical, ac_heating, inspection`) + 2 new values
- Usage tracking uses denormalized STATS# items in same table — no expensive work_orders scans
- GSI counts are well within limits: `service_types` = 3/5, `service_kits` = 2/5
- Backward compatibility maintained via dual-write + read-with-fallback strategy
- No new infrastructure required (no Redis, no S3, no WebSocket, no queues)

**Remaining uncertainty (12%):**
- Exact DynamoDB item structure of existing services may have minor field name variations (need to verify with actual `service_types` table scan before implementing repository)
- Standard Parts editor UX: MVP uses free-text part name without inventory autocomplete. If autocomplete is expected from screen designs, it would require an inventory search endpoint — verify during implementation
- Performance of `scan` with FilterExpression on `service_types` table at scale (>1000 items including stats). At that point, consider adding a `type` field to distinguish item types and a GSI on it.
- "More Filters" button behavior from screen designs is not specified — implement as expandable filter section with additional fields (warranty, interval range, date range)