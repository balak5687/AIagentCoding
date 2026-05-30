# Playbooks - Deterministic Code Generation

**Inspired by**: Google's deterministic approach to reduce LLM hallucination

## Philosophy

**Cognitive vs Deterministic**:
- **Cognitive**: LLM reasons about novel problems (more creative, higher hallucination risk)
- **Deterministic**: Follow step-by-step playbooks (less creative, lower hallucination)

**When to Use Each**:
- Use **playbooks** for: CRUD operations, standard patterns, boilerplate, refactoring
- Use **cognitive** for: Novel algorithms, complex business logic, architectural decisions

## How Playbooks Work

1. **Planner** detects task matches a playbook pattern
2. **Planner** includes playbook reference in task
3. **Coder** loads playbook and follows steps deterministically
4. **Result**: More consistent, less hallucination

## Playbook Structure

Each playbook is a YAML file with:
- **pattern**: Task pattern to match
- **steps**: Deterministic steps to execute
- **templates**: Code templates with placeholders
- **validation**: Checks to verify correctness

## Available Playbooks

1. `add_crud_endpoint.yaml` - Add REST API CRUD endpoint
2. `add_database_model.yaml` - Add database model/table
3. `add_unit_tests.yaml` - Add unit tests for function/class
4. `refactor_extract_function.yaml` - Extract code into function
5. `add_error_handling.yaml` - Add try/catch error handling
6. `add_logging.yaml` - Add logging statements
7. `add_input_validation.yaml` - Add input validation
8. `fix_security_issue.yaml` - Fix common security issues

## Example Usage

**Task**: "Add CRUD endpoint for User model"

**Without Playbook** (Cognitive):
- LLM reasons about how to implement
- May forget edge cases
- Inconsistent patterns
- Higher hallucination risk

**With Playbook** (Deterministic):
- Load `add_crud_endpoint.yaml`
- Follow steps 1-10 exactly
- Fill in templates with User-specific values
- Validate against checklist
- Lower hallucination risk

## Creating New Playbooks

See `playbook_template.yaml` for structure.

Key principles:
1. **Atomic steps** - Each step is clear and unambiguous
2. **Templates** - Provide exact code patterns with placeholders
3. **Validation** - Include checks to verify correctness
4. **Examples** - Show concrete examples
