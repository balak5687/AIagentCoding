**Title**: Service Master Module
**Issue**: https://github.com/aravindmk1011/GreasyNutsIssues/issues/6
**Module**: Service Master

## Overview
The Service Master Module is a centralised library for managing all garage services, their pricing, procedures, parts, and performance metrics. It consists of four screens: Service Dashboard, Service Catalog, New Service form, and Service Kits.

## Screens

### Screen 1 — Service Dashboard
- **Sidebar sub-nav**: Service Dashboard, Service Catalog, Service Kits
- **Top bar**: Search with category dropdown (Service Code, Service Name, Category, Service Kit), filter dropdown (All/Active/Inactive, Maintenance, Repair, Electrical, AC, Engine, Transmission, Body Work)
- **KPI Cards** (4): Total Services, Active Categories, Most Used Service (name), Average Duration (hours)
- **Service Alerts Panel** (left): table of alerts, entire row clickable → opens Service Information Screen
- **Most Used Services Chart** (right): horizontal bar chart showing top services by usage count
- **Service Performance Table** (full width below): columns: Service Name, Category, Times Used, Avg Duration, Revenue Generated, Status

### Screen 2 — Service Information Screen
Opened by clicking any service row or alert.

**Section 1 — Service Header**: Service Code, Service Name, Category, Status badge, action buttons (Edit, Deactivate, Save)

**Section 2 — Service Summary**: Standard Price (AED), Estimated Duration (hours), Warranty Period, Service Interval (KM/months), Description. Editable by owner/manager.

**Section 3 — Standard Parts**: Table of parts auto-suggested when service is added to a job. Columns: Part Name, Part Number, Quantity, Unit, Notes. Editable.

**Section 4 — Service Procedure**: SOP / step-by-step instructions. Manager updates, technician views.

**Section 5 — Reference Materials**: Table of training resources. Columns: Title, Type (PDF Manual/Video Tutorial/OEM Procedure/Internal SOP), URL/Link. Entire row clickable. Opens PDF/video/website/internal doc.

**Section 6 — Service Usage History**: How often this service has been used. Columns: Job ID, Vehicle, Date, Technician, Duration, Notes.

**Action Bar** (top right): Edit Service, Deactivate Service, Save, Service Notes (garage-specific observations).

### Screen 3 — New Service / Create Service
Form to create a new service entry.

**Section 1 — Service Information**: Service Name, Service Code (auto-generated), Category (dropdown), Status (Active/Inactive), Description

**Section 2 — Pricing & Duration**: Standard Price (AED), Estimated Duration (hours), Warranty Period, Service Interval

**Section 3 — Standard Parts**: Add parts that auto-populate when service is added to a job

**Section 4 — Service Procedure**: Rich text / step-by-step SOP entry

**Section 5 — Service Notes**: Multi-line text, garage-specific instructions

**Section 6 — Action Buttons**: Save → creates service → adds to catalog → opens Service Information Screen. Do NOT show: Service Usage History, performance data until after creation.

### Screen 4 — Service Kits
Bundles of multiple services grouped together.

**Service Kit Table**: Kit Code, Kit Name, Included Services (count), Total Hours, Status, Actions dropdown (Open / Edit / Deactivate / Delete). Entire row clickable.

**Create Service Kit Screen**:
- Section 1 — Kit Information: Kit Name, Kit Code (auto), Description, Status
- Section 2 — Included Services: Search and select from Service Catalog. Auto-calculated: Total Services Count, Total Estimated Hours
- Section 3 — Kit Summary: auto-generated
- Action Buttons: Save, Cancel, Delete Kit

**Service Kit Information Screen**: same sections as Create but read-only with edit option.

## Service Categories
Maintenance, Repair, Electrical, AC, Engine, Transmission, Body Work

## Data Model Requirements
- `services` table: service_id (PK), service_code, service_name, category, status, standard_price, estimated_duration_hours, warranty_period, service_interval_km, service_interval_months, description, procedure_steps, notes, created_at, updated_at
- `service_parts` table: service_id (FK), part_id, quantity, unit, notes
- `service_references` table: service_id (FK), title, type, url
- `service_kits` table: kit_id (PK), kit_code, kit_name, description, status
- `service_kit_items` table: kit_id (FK), service_id (FK), order

## Business Rules
- Service Code auto-generated (e.g. SVC-001)
- Kit Code auto-generated (e.g. KIT-001)
- Standard Parts auto-suggest when service added to a job
- Usage History populated from jobs/work orders
- Total Kit Hours = sum of included service estimated durations
