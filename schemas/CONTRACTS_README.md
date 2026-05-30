# Agent I/O Data Contracts

**Version**: 1.0  
**Format**: Protobuf + YAML/Markdown  
**Updated**: 2026-05-23

---

## Overview

This document defines the **data contracts** between all agents in the SDLC system. Each agent produces output in **YAML + Markdown** format, validated against **Protobuf schemas**.

### Why Protobuf + YAML/Markdown?

**Protobuf** provides:
- ✅ Strong typing and schema validation
- ✅ Versioning support
- ✅ Cross-language compatibility
- ✅ Clear documentation of contracts

**YAML + Markdown** provides:
- ✅ Human-readable output
- ✅ Natural format for LLMs (Claude excels at Markdown)
- ✅ Rich formatting (headers, lists, code blocks, tables)
- ✅ Easy debugging (can read agent outputs directly)

**Best of both worlds**: Schema validation + human readability!

---

## Agent Data Flow

```
GitHub Issue
    ↓
┌─────────────────────────────────────────┐
│  GitHub Scanner Agent                   │
│  Output: GitHubScannerOutput            │
│  - Issue data (title, body, components) │
│  - Requirements extracted               │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Context Agent                          │
│  Input: Issue data (optional)           │
│  Output: ContextAgentOutput             │
│  - Backend context (tech stack, patterns)│
│  - Frontend context                      │
│  - File tree, API endpoints, imports    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Designer Agent                         │
│  Input: Requirements + Context          │
│  Output: DesignerOutput                 │
│  - Architecture design                   │
│  - Components breakdown                  │
│  - Risks and estimates                   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Planner Agent                          │
│  Input: Design                          │
│  Output: PlannerOutput                  │
│  - Task breakdown with dependencies     │
│  - Execution strategy (parallel/serial) │
│  - Dependency graph                      │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Coder Agent (per task)                 │
│  Input: Task specification              │
│  Output: CoderOutput                    │
│  - SEARCH/REPLACE blocks (Aider format)│
│  - New files to create                  │
│  - Implementation notes                 │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Reviewer Agent                         │
│  Input: Code changes                    │
│  Output: ReviewerOutput                 │
│  - Review decision (approve/reject)     │
│  - Issues found (security, quality)     │
│  - Quality assessment scores            │
└─────────────────────────────────────────┘
```

---

## Schema Files

### Location
```
schemas/
├── proto/                      # Protobuf schema definitions
│   ├── common.proto           # Shared types (Status, Severity, FileReference, etc.)
│   ├── github_scanner.proto   # GitHub Scanner output
│   ├── context_agent.proto    # Context Agent output
│   ├── designer.proto         # Designer output
│   ├── planner.proto          # Planner output
│   ├── coder.proto            # Coder output
│   └── reviewer.proto         # Reviewer output
├── examples/                   # Example outputs
│   ├── designer_example.md
│   ├── planner_example.md
│   └── ...
└── CONTRACTS_README.md         # This file
```

### Generated Python Code
```
src/schemas/                    # Auto-generated from .proto files
├── common_pb2.py
├── github_scanner_pb2.py
├── context_agent_pb2.py
├── designer_pb2.py
├── planner_pb2.py
├── coder_pb2.py
└── reviewer_pb2.py
```

---

## Common Types (from common.proto)

### Status Enum
```protobuf
enum Status {
  STATUS_UNSPECIFIED = 0;
  COMPLETE = 1;          // Agent finished successfully
  INCOMPLETE = 2;        // Agent couldn't complete
  IN_PROGRESS = 3;       // Agent still working
  FAILED = 4;            // Agent encountered error
  NEEDS_REVIEW = 5;      // Waiting for review
  APPROVED = 6;          // Reviewed and approved
  REJECTED = 7;          // Reviewed and rejected
}
```

### Severity Enum
```protobuf
enum Severity {
  SEVERITY_UNSPECIFIED = 0;
  LOW = 1;
  MEDIUM = 2;
  HIGH = 3;
  CRITICAL = 4;
}
```

### FileReference
```protobuf
message FileReference {
  string path = 1;                // e.g., "app/routes/dashboard.py"
  optional int32 start_line = 2;
  optional int32 end_line = 3;
  string description = 4;
}
```

### Component
```protobuf
message Component {
  string name = 1;
  string type = 2;                // "route", "service", "widget", etc.
  repeated FileReference files = 3;
  string description = 4;
  repeated string dependencies = 5; // Other components this depends on
}
```

---

## Agent Contracts

### 1. GitHub Scanner Agent

**Schema**: `github_scanner.proto`

**Output Format**:
```yaml
agent: github_scanner
status: COMPLETE
confidence: 90

issue:
  number: 3
  title: "EPIC: Dashboard Module Rev2"
  url: "https://github.com/aravindmk1011/GreasyNutsIssues/issues/3"
  issue_type: "epic"
  components:
    - name: "Sidebar Navigation"
      backend_required: false
      frontend_required: true
    - name: "KPI Cards"
      backend_required: true
      frontend_required: true
  requirements:
    functional:
      - "Display real-time KPIs (jobs today, pending jobs, revenue, payments)"
      - "Show operational alerts (blocked jobs, low stock, supplier delays)"
    data_sources:
      - "Jobs"
      - "Invoices"
      - "Suppliers"
```

**Key Fields**:
- `issue.number`, `issue.title`, `issue.url` - Issue metadata
- `issue.components[]` - Parsed components from EPIC
- `issue.requirements` - Extracted requirements

---

### 2. Context Agent

**Schema**: `context_agent.proto`

**Output Format**:
```yaml
agent: context_agent
status: COMPLETE
confidence: 95

backend:
  name: "GreasyNuts Backend"
  path: "/home/ubuntu/greasynuts/dev/backend/GreasyNuts"
  type: "backend"
  tech_stack:
    language: "Python"
    framework: "Flask"
    database: "DynamoDB"
  architecture:
    pattern: "3-layer"
    layers: ["routes", "services", "repositories"]
  patterns:
    - name: "JWT Authentication"
      description: "@require_auth decorator on all protected routes"
      examples: ["app/routes/auth.py", "app/routes/customers.py"]
  api_endpoints:
    - method: "GET"
      path: "/api/customers"
      handler_file: "app/routes/customers.py"
      requires_auth: true
  stats:
    total_files: 2215
    lines_of_code: 327000
    routes_count: 15
    services_count: 12
```

**Key Fields**:
- `backend/frontend.tech_stack` - Technology detected
- `architecture.pattern` - Architecture type identified
- `patterns[]` - Existing code patterns found
- `api_endpoints[]` - Discovered API endpoints

---

### 3. Designer Agent

**Schema**: `designer.proto`

**Output Format**:
```yaml
agent: designer
status: COMPLETE
confidence: 88

design:
  title: "Dashboard Module Implementation"
  architecture:
    pattern: "3-layer"
    data_flow: "Routes → Services → Repositories"
  components:
    - name: "Dashboard Routes"
      type: "route"
      files:
        - path: "app/routes/dashboard.py"
      dependencies: ["dashboard_service"]
  approach:
    strategy: "incremental"
    success_criteria:
      - "All 5 API endpoints return valid data"
  risks:
    - id: "performance-001"
      severity: MEDIUM
      description: "Dashboard may be slow with large datasets"
      mitigation: "Add caching layer"
  estimates:
    complexity_score: 6
    estimated_loc: 800
    time_estimate: "7-9 hours"
```

**Key Fields**:
- `design.components[]` - What needs to be built
- `design.approach` - How to implement
- `design.risks[]` - Potential issues
- `design.estimates` - Complexity and time

---

### 4. Planner Agent

**Schema**: `planner.proto`

**Output Format**:
```yaml
agent: planner
status: COMPLETE
confidence: 85

plan:
  title: "Dashboard Implementation Plan"
  tasks:
    - id: "task_1"
      name: "Create dashboard routes"
      description: "Implement 5 REST endpoints"
      files:
        - path: "app/routes/dashboard.py"
      depends_on: []
      approach: "cognitive"
      agent: "coder"
      complexity: 6
    - id: "task_2"
      name: "Create dashboard service"
      depends_on: ["task_1"]
      approach: "deterministic"
      playbook: "flask_service_pattern"
  strategy:
    type: "hybrid"
    phases:
      - order: 1
        name: "Backend Implementation"
        task_ids: ["task_1", "task_2"]
        execution_mode: "sequential"
```

**Key Fields**:
- `plan.tasks[]` - All tasks with dependencies
- `plan.strategy` - Execution approach
- `plan.dependencies` - Dependency graph

---

### 5. Coder Agent

**Schema**: `coder.proto`

**Output Format**:
```yaml
agent: coder
status: COMPLETE
confidence: 82

implementation:
  task_id: "task_1"
  summary: "Created dashboard routes with 5 endpoints"
  changes:
    - file_path: "app/routes/__init__.py"
      type: MODIFY
      search_block: |
        from app.routes.auth import auth_bp
        from app.routes.customers import customers_bp
      replace_block: |
        from app.routes.auth import auth_bp
        from app.routes.customers import customers_bp
        from app.routes.dashboard import dashboard_bp
      reason: "Register dashboard blueprint"
  new_files:
    - file_path: "app/routes/dashboard.py"
      content: |
        from flask import Blueprint
        ...
      purpose: "Dashboard API endpoints"
  request_peer: false
```

**Key Fields**:
- `implementation.changes[]` - SEARCH/REPLACE blocks
- `implementation.new_files[]` - Files to create
- `request_peer` - If true, needs peer help

---

### 6. Reviewer Agent

**Schema**: `reviewer.proto`

**Output Format**:
```yaml
agent: reviewer
status: APPROVED
confidence: 90

review:
  task_id: "task_1"
  decision: APPROVED
  issues:
    - id: "style-001"
      category: STYLE
      severity: LOW
      description: "Missing docstring on get_kpis function"
      file_path: "app/routes/dashboard.py"
      line_number: 15
      suggestion: "Add docstring describing return values"
      blocking: false
  strengths:
    - "Follows 3-layer architecture correctly"
    - "Proper error handling with try-except"
    - "JWT authentication on all endpoints"
  quality:
    code_quality_score: 85
    security_score: 95
    follows_patterns: true
```

**Key Fields**:
- `review.decision` - APPROVED | NEEDS_MINOR_FIXES | REJECTED
- `review.issues[]` - Problems found
- `review.quality` - Quality scores

---

## Validation

### Python Usage

```python
from src.core.schema_validator import validate_agent_output

# Agent produces YAML + Markdown output
raw_output = """
---
agent: designer
status: COMPLETE
confidence: 88
...
---

# Design Document
...
"""

# Validate against schema
is_valid, proto_msg, yaml_data, markdown = validate_agent_output(
    "designer",
    raw_output,
    strict=True  # Raise exception on error
)

if is_valid:
    # Access validated data
    print(f"Components: {len(proto_msg.design.components)}")
    print(f"Complexity: {proto_msg.design.estimates.complexity_score}/10")
    
    # Convert to dict if needed
    from google.protobuf import json_format
    design_dict = json_format.MessageToDict(proto_msg)
```

### Business Rules Validation

Beyond schema structure, we validate:
- **Confidence scores**: Must be 0-100
- **Designer**: If COMPLETE, must have components and confidence >60
- **Planner**: If COMPLETE, must have tasks and no circular dependencies
- **Coder**: If COMPLETE, must have changes or new files
- **Reviewer**: If APPROVED, no blocking HIGH/CRITICAL issues

---

## Regenerating Python Code

If you modify `.proto` files:

```bash
# Install tools (one time)
pip install protobuf grpcio-tools

# Regenerate Python code
python -m grpc_tools.protoc \
  -I=schemas/proto \
  --python_out=src/schemas \
  --pyi_out=src/schemas \
  schemas/proto/*.proto
```

---

## Best Practices

### For Agent Developers

1. **Follow the schema strictly** - Required fields must be present
2. **Validate locally** - Test your agent output against schema before committing
3. **Use enums correctly** - Status, Severity use specific enum values
4. **Provide rich markdown** - Schemas capture structure, markdown captures details
5. **Include metadata** - Always set confidence scores

### For Schema Maintainers

1. **Version carefully** - Protobuf supports backwards compatibility
2. **Use optional fields** - For non-critical data
3. **Document changes** - Update this README when schemas change
4. **Add examples** - Create example output for new schemas
5. **Test validation** - Ensure validation catches real errors

---

## Schema Evolution

### Adding New Fields

**Safe** (backwards compatible):
```protobuf
message DesignerOutput {
  // Existing fields...
  optional string new_field = 10;  // Optional, won't break old agents
}
```

**Breaking** (not backwards compatible):
```protobuf
message DesignerOutput {
  // Existing fields...
  string required_field = 10;  // Required, breaks old agents
}
```

### Deprecating Fields

```protobuf
message DesignerOutput {
  string old_field = 5 [deprecated = true];  // Mark as deprecated
}
```

---

## Troubleshooting

### "ParseError: Failed to parse"
- Check YAML syntax (indentation, quotes)
- Ensure enum values match exactly (COMPLETE not "complete")
- Verify required fields are present

### "Unknown field"
- Field name in YAML doesn't match protobuf schema
- Typo in field name
- Using snake_case instead of camelCase (use snake_case)

### "Circular dependency detected"
- Planner created task graph with cycle
- Check `depends_on` relationships
- Use topological sort to find cycle

---

## References

- **Protobuf Documentation**: https://protobuf.dev
- **YAML Specification**: https://yaml.org/spec/1.2.2/
- **Markdown Spec (CommonMark)**: https://commonmark.org
- **Aider SEARCH/REPLACE format**: https://aider.chat/docs/repomap.html

---

**Contract Version**: 1.0  
**Last Updated**: 2026-05-23  
**Maintainer**: SDLC System Team
