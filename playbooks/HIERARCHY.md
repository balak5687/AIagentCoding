# Playbook Hierarchy

**Based on**: Google's TensorFlow→JAX migration system (arXiv:2603.27296)

## Google's Four-Level Hierarchy

```
Level 1: General Instruction Playbook
         ↓
Level 2: Style Playbook
         ↓
Level 3: Task-Specific Playbook
         ↓
Level 4: Client-Specific Playbook
```

### Update Cadence (from Google's paper)

| Level | Update Frequency | Trigger |
|-------|-----------------|---------|
| General Instruction | Rarely | New tools/capabilities added |
| Style | Rarely | Manual, when style violations detected |
| Task-Specific | Regularly | New patterns discovered |
| Client-Specific | Frequently | After each execution iteration |

---

## Our Implementation

### Level 1: General Instruction Playbooks

**Purpose**: Fundamental capabilities for interacting with codebase
**Location**: `playbooks/general/`

**Examples**:
- `file_operations.yaml` - Read, write, search files
- `git_operations.yaml` - Commit, branch, merge
- `build_operations.yaml` - Build, test, run
- `dependency_operations.yaml` - Install, update packages

**Update**: Only when new tools added to system

---

### Level 2: Style Playbooks

**Purpose**: Language and project-specific coding standards
**Location**: `playbooks/style/`

**Examples**:
- `python_style.yaml` - PEP 8, type hints, docstrings
- `javascript_style.yaml` - ESLint, Prettier
- `java_style.yaml` - Google Java Style Guide
- `react_style.yaml` - Component patterns, hooks usage
- `fastapi_style.yaml` - Route structure, dependency injection

**Update**: Manually when style violations detected

---

### Level 3: Task-Specific Playbooks

**Purpose**: Common development tasks across projects
**Location**: `playbooks/tasks/`

**Examples**:
- `add_crud_endpoint.yaml` - REST API CRUD
- `add_unit_tests.yaml` - Test generation
- `add_error_handling.yaml` - Error handling patterns
- `add_database_model.yaml` - ORM models
- `add_authentication.yaml` - Auth patterns
- `add_logging.yaml` - Logging setup
- `refactor_extract_function.yaml` - Code extraction
- `optimize_query.yaml` - Database optimization

**Update**: Whenever new generally applicable patterns discovered

---

### Level 4: Project-Specific Playbooks

**Purpose**: Patterns specific to current project/client
**Location**: `playbooks/projects/{project_name}/`

**Examples** (for a hypothetical e-commerce project):
- `add_payment_gateway.yaml` - Stripe integration patterns
- `add_product_feature.yaml` - Product model extensions
- `add_checkout_step.yaml` - Checkout flow patterns
- `add_admin_panel.yaml` - Admin CRUD patterns

**Update**: Iteratively after each execution

---

## Playbook Selection Process

```python
def select_playbooks(task, project_context):
    playbooks = []
    
    # 1. Always include general instruction playbook
    playbooks.append(load_playbook("general/file_operations.yaml"))
    
    # 2. Add style playbook for detected language/framework
    if task.language == "python":
        playbooks.append(load_playbook("style/python_style.yaml"))
    if task.framework == "fastapi":
        playbooks.append(load_playbook("style/fastapi_style.yaml"))
    
    # 3. Add task-specific playbook if matched
    task_playbook = match_task_playbook(task.description)
    if task_playbook:
        playbooks.append(task_playbook)
    
    # 4. Add project-specific playbook if exists
    project_playbook = find_project_playbook(project_context.name, task)
    if project_playbook:
        playbooks.append(project_playbook)
    
    return playbooks
```

---

## Human Supervision Gates

**Based on Google's approach**: Playbooks are AI-generated then human-supervised

### Gate 1: Playbook Generation
- **When**: Creating new playbook from examples
- **Human Reviews**: 
  - Pattern correctness
  - Example quality
  - Completeness
- **Approval Required**: YES

### Gate 2: Playbook Updates
- **When**: Modifying existing playbook
- **Human Reviews**:
  - Changes don't break existing patterns
  - New patterns are beneficial
- **Approval Required**: YES for style/task-specific, NO for project-specific

### Gate 3: Playbook Application
- **When**: Agent uses playbook for code generation
- **Human Reviews**:
  - Generated code follows playbook correctly
  - Playbook was appropriate choice
- **Approval Required**: NO (post-review only)

### Gate 4: Production Readiness
- **When**: Code ready for production
- **Human Reviews**:
  - Security review
  - Performance review
  - Best practices followed
- **Approval Required**: YES

---

## Playbook File Format

### Standard Structure

```yaml
# Metadata
metadata:
  level: general|style|task|project
  version: "1.0.0"
  created_by: ai|human
  supervised_by: "engineer_name"
  approved_date: "2026-05-23"
  last_updated: "2026-05-23"
  
# Pattern information
name: playbook_name
description: "What this playbook does"
category: api|testing|database|security|performance
language: python|javascript|java|go|any
framework: fastapi|react|spring|express|any

# AI generation info (if applicable)
generation:
  ai_model: "claude-sonnet-4"
  training_examples: ["example1.py", "example2.py"]
  human_supervisor: "engineer_name"
  approval_status: pending|approved|rejected
  
# Pattern matching
pattern:
  keywords: ["list", "of", "keywords"]
  entities_required: ["entity1", "entity2"]
  
# Deterministic steps with AI guidance
steps:
  - step: 1
    action: "What to do"
    ai_guidance: "How LLM should approach this"
    deterministic: true|false
    template: "template_name"
    validation: ["check1", "check2"]
    
# Code templates
templates:
  template_name:
    python: |
      # Python implementation
    javascript: |
      // JavaScript implementation
      
# Validation
validation:
  - "Validation check 1"
  - "Validation check 2"
  
# Examples (from successful executions)
examples:
  - input: "Example task description"
    output: "Example code generated"
    success: true
    notes: "Why this worked well"
```

---

## Migration Path

### Current State
- ✅ 3 task-specific playbooks (hand-written)
- ❌ No general instruction playbooks
- ❌ No style playbooks
- ❌ No project-specific playbooks
- ❌ No AI generation
- ❌ No human supervision gates

### Phase 1: Infrastructure (Week 1)
- [ ] Create playbook hierarchy directories
- [ ] Implement playbook selection logic
- [ ] Add metadata fields to existing playbooks
- [ ] Create human supervision workflow

### Phase 2: General & Style Playbooks (Week 2)
- [ ] Generate general instruction playbooks
- [ ] Create style playbooks for Python, JavaScript, Java
- [ ] Human review and approval
- [ ] Test with existing tasks

### Phase 3: AI-Generated Playbooks (Week 3)
- [ ] Implement playbook generation from examples
- [ ] Create learning system from successful executions
- [ ] Add human supervision UI/workflow
- [ ] Generate project-specific playbooks

### Phase 4: Production Readiness (Week 4)
- [ ] Add production readiness checks
- [ ] Security review playbooks
- [ ] Performance optimization playbooks
- [ ] Best practices playbooks
- [ ] End-to-end testing

---

## References

1. **Google Research Paper**:
   - "A Multi-agent AI System for Deep Learning Model Migration from TensorFlow to JAX"
   - arXiv:2603.27296, March 2026
   - https://arxiv.org/abs/2603.27296

2. **Key Insights from Paper**:
   - Hierarchical playbook structure (4 levels)
   - AI-generated playbooks with human supervision
   - Different update cadences per level
   - 6.4x-8x speedup results
   - File-based memory bank for agent communication
