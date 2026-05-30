# SDLC Agent System V2 — Design Document

## Current State (V1)
```
Designer → Planner → [Coder → Reviewer] × N tasks
```
Single Coder handles Python + Dart + routes + models. Reviewer does text review only, no compile check. No tester. No architect.

## V2 Pipeline

```
Designer
  → Architect (reviews design for feasibility before planning)
    → Planner
      → [per task, by type]:
          Backend Coder  → Compile Agent (py_compile)      → Tester → Reviewer
          Frontend Coder → Compile Agent (flutter analyze) → Tester → Reviewer
          [if rejected]  → Peer Guidance → Coder retries
            → Blackbox Tester (Playwright, post all-tasks-approved)
              → Git Agent (commit + PR)
                → Observability Report
```

## New Agents

### Backend Coder (`agents/backend_coder.md`)
- Python/Flask/DynamoDB specialist only
- Knows existing repository pattern (WorkOrderRepository, UserRepository etc.)
- Playbooks: `add_crud_endpoint.yaml`, `add_service_method.yaml`, `add_database_model.yaml`
- Never writes Flutter/Dart

### Frontend Coder (`agents/frontend_coder.md`)
- Flutter/Dart specialist only
- Uses flutter/skills playbooks (https://github.com/flutter/skills)
- Knows existing widget patterns (StatefulWidget + service, DashboardService, Dio)
- Never writes Python

### Architect (replaces Peer)
- Fires at TWO points — not just when stuck:
  1. **Pre-planning**: Reviews Designer output for feasibility. Catches missing repos, wrong patterns, undefined dependencies before Planner creates tasks.
  2. **Mid-task**: When Coder is stuck (iteration >= 2), provides targeted guidance.
- Has access to full codebase via Brain coding query
- Agent file: `agents/architect.md`

### Compile Agent (`agents/compile_agent.md`)
- Runs after every Coder output, before Reviewer
- Backend: `python -m py_compile <file>` + import check
- Frontend: `flutter analyze <file>`
- On failure: returns structured error list back to Coder as `compile_errors`
- On success: passes to Reviewer
- **Critical**: This agent was the biggest missing piece — would have prevented 80% of manual fixes

### Tester (`agents/tester.md`)
- Runs after Compile Agent passes, before Reviewer
- Writes unit tests for the implemented code
- Backend: pytest patterns
- Frontend: Flutter widget tests
- Uses `add_unit_tests.yaml` playbook
- Does NOT run tests (Compile Agent handles that)

### Blackbox Tester (`agents/blackbox_tester.md`)
- Runs after ALL tasks in an issue are approved
- Playwright-based end-to-end testing
- Tests the running app at feature environment URL
- Captures screenshots, reports pass/fail per user flow
- Feeds failures back as new fix tasks

### Git Agent (`agents/git_agent.md`)
- Runs after Blackbox Tester passes
- Creates/switches to correct branch
- Commits all approved changes with structured commit message
- Opens PR with summary of what was implemented
- Never touches main/dev/prod branches (branch guard)

### Observability Report Agent (`agents/report_agent.md`)
- Runs at end of each issue
- Generates structured report:
  - Per-task: attempts, iterations, peer help used, time taken
  - Overall: tasks approved first-attempt vs retried
  - Files changed, lines added/removed
  - Any skipped/timed-out tasks
- Saves to `reports/issue-{N}-run-{timestamp}.md`

## Missing Playbooks to Build

| Playbook | Purpose |
|---|---|
| `playbooks/tasks/add_service_method.yaml` | Add method to existing service class |
| `playbooks/flutter/responsive_layout.md` | From flutter/skills |
| `playbooks/flutter/stateful_widget.md` | From flutter/skills |
| `playbooks/flutter/json_serialization.md` | From flutter/skills |
| `playbooks/flutter/widget_test.md` | From flutter/skills |

## Flutter/Skills Integration

Install: `npx skills add flutter/skills`
Location: `playbooks/flutter/`
Usage: Frontend Coder pre-hook checks task description against flutter/skills index, injects matching skill as context

## Daemon Architecture (V2)

```
tmux session: sdlc-agents-v2
  pane 0: brain-server       (port 7433 — already running)
  pane 1: backend-coder      (watches .agent-bus/backend_coder/inbox)
  pane 2: frontend-coder     (watches .agent-bus/frontend_coder/inbox)
  pane 3: compile-agent      (watches .agent-bus/compile/inbox)
  pane 4: tester             (watches .agent-bus/tester/inbox)
  pane 5: reviewer           (watches .agent-bus/reviewer/inbox)
  pane 6: architect          (watches .agent-bus/architect/inbox)
  pane 7: blackbox-tester    (watches .agent-bus/blackbox_tester/inbox)
  pane 8: git-agent          (watches .agent-bus/git/inbox)
  pane 9: report-agent       (watches .agent-bus/report/inbox)
```

## Routing Logic (updated coder_daemon)

Post-coder hook decides which inbox to route to:
```
if task.type == 'backend':  → backend_coder/inbox
if task.type == 'frontend': → frontend_coder/inbox

post-coder:
  if request_peer OR iteration >= 2: → architect/inbox
  else: → compile/inbox

post-compile:
  if errors: → back to coder/inbox with compile_errors
  else: → tester/inbox

post-tester:
  → reviewer/inbox

post-reviewer:
  if approved: apply diff → ack orchestrator
  if rejected: → coder/inbox with feedback

post-all-tasks:
  → blackbox_tester/inbox
  → git/inbox
  → report/inbox
```

## Task Type Detection

Planner output already has `files` field. Add routing rule:
- file path contains `/backend/` or ends in `.py` → `type: backend`
- file path contains `/frontend/` or ends in `.dart` → `type: frontend`

## Build Priority Order

1. **Compile Agent** — highest impact, prevents post-approval fire-fighting
2. **Backend Coder + Frontend Coder** — split the single coder
3. **Flutter/skills playbooks** — load from github.com/flutter/skills
4. **Architect** — replaces current Peer, add pre-planning phase
5. **Blackbox Tester** — Playwright agent
6. **Git Agent** — automate commits/PRs
7. **Observability Report** — visibility into pipeline performance
8. **Tester** — unit test writer

## Decisions Made

- Architect ≠ Peer. Architect fires pre-planning AND mid-task. Peer was reactive only.
- Compile Agent runs BEFORE Reviewer. Reviewer should never see uncompilable code.
- Blackbox Tester uses Playwright (already installed, proven in Issue #3 testing).
- Brain ingest only on Reviewer approval — unreviewed code must not pollute brain. ✓ (already fixed)
- Branch guard in daemon base — never write to main/dev/prod. ✓ (already built)
