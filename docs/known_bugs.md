# Known Bugs & Issues

## AI Coding System

### CRITICAL

**BUG-001: V2 coders (backend_coder, frontend_coder, react_coder) get zero brain context**
- File: `src/core/agent_runner.py` `_fetch_brain_context()`
- Status: PARTIALLY FIXED — backend_coder/frontend_coder added, react_coder added
- Root: switch statement only covered old `coder` agent name
- Remaining: verify context actually flows through in debug output

**BUG-002: react_coder daemon watches wrong inbox**
- File: `run_daemon.py`
- Status: FIXED — `_make_named_daemon()` added
- Root: `make_backend_coder_daemon()` hardcoded `agent_name='backend_coder'` regardless of caller

**BUG-003: ConversationLoop routes .tsx files to `coder` not `react_coder`**
- File: `src/workflows/conversation.py` `_route_coder()`
- Status: FIXED
- Root: `.tsx`/`.ts` not in routing conditions before fix

### HIGH

**BUG-004: BM25 full rebuild on every ingest — O(n) per approved task**
- File: `src/brain/coding_brain.py` `ingest()`
- Status: OPEN
- Fix: batch ingests, rebuild once per run end

**BUG-005: Brain status endpoint shows stale chunk count**
- File: `src/brain/server.py` `/status` handler
- Status: OPEN
- Fix: count from live brain object not manifest file

**BUG-006: BrainServer uses single-threaded HTTPServer — blocks parallel daemon queries**
- File: `src/brain/server.py`
- Status: OPEN
- Fix: `from http.server import ThreadingHTTPServer` — one line

**BUG-007: Retry feedback only keeps metadata, loses full coder output**
- File: `src/core/agent_runner.py` `_add_retry_feedback()`
- Status: OPEN
- Fix: store `message.content` not just `message.metadata`

**BUG-008: Agent outputs (designer, planner) still fed into functionality brain on every run**
- File: `src/core/agent_runner.py` `_feed_back_to_brain()`
- Status: PARTIALLY FIXED — coder/peer blocked, but reviewer output feeds in regardless of quality
- Remaining: only feed after reviewer approval with diff_applied > 0

**BUG-009: Orchestrator timeout (15min) races with reviewer daemon**
- File: `run_issue3.py` / `run_react_dashboard.py`
- Status: PARTIALLY FIXED — `wait_for_task()` uses task-specific file
- Remaining: tasks in same parallel group can still starve if single coder processes sequentially

**BUG-010: Planner outputs relative paths (backend/models/) not absolute paths**
- File: `run_pipeline.py` context constraints
- Status: OPEN — constraint added but untested on full run
- Impact: Coder writes to wrong location (AIagentCoding dir instead of greasynuts)

### MEDIUM

**BUG-011: Supply issues `affected_jobs_count` always 0**
- File: `app/services/dashboard_service.py` `get_supply_issues()`
- Status: OPEN
- Root: Cross-references `work_order.parts_used` field but seed data uses `parts` key in POs
- Fix: Update `get_supply_issues()` to check both field names OR fix seed data

**BUG-012: Flutter dashboard — `testing/sdlc-issue-3` branch has uncommitted changes**
- Repo: `/home/ubuntu/greasynuts/dev/backend/GreasyNuts`
- Status: OPEN — changes applied but never committed
- Files: `app/__init__.py`, `app/models/dashboard.py`, `app/routes/dashboard.py`, `app/services/dashboard_service.py`
- Fix: Commit to branch before starting Issue #4

**BUG-013: Revenue Today / Expenses Today always €0 in KPI cards**
- File: `app/services/dashboard_service.py` `_get_executive_kpis()`
- Status: OPEN
- Root: `today_start` boundary uses UTC midnight but invoices created with `days_ago(0)` timestamp earlier in the day
- Fix: Widen today window or use date comparison not datetime

**BUG-014: Jobs Snapshot — `issue_type` field empty for most jobs**  
- File: `app/services/dashboard_service.py` `get_jobs_snapshot()`
- Status: PARTIALLY FIXED — falls back to `issue_description[:30]`
- Remaining: seed data uses `issue_type` directly, live data may differ

---

## React Dashboard (port 8091)

**BUG-015: Supply Issues `affected_jobs` always shows "0 jobs"**
- Same root as BUG-011

**BUG-016: Revenue chart x-axis labels — only show if bottom margin >= 20px**
- File: `RevenueTrendChart.tsx`
- Status: FIXED

**BUG-017: Jobs Snapshot table — Technician column cut off on smaller screens**
- Status: Shows "Unassigned" now, but Delivery Status column still partially hidden
- Fix: Add column visibility toggle or reduce column count

---

## Issues Pending (GitHub)

| Issue | Title | Branch | Status |
|---|---|---|---|
| #3 | Dashboard Module Rev2 | `testing/sdlc-issue-3` | Code complete, not committed, not merged |
| #4 | Job Module | No branch yet | Designer + Planner done (relative paths issue) |
| TBD | Inventory Module | Not started | |
| TBD | Invoice Module | Not started | |

---

## AI Coding System — Architecture Debt

Tracked separately in `docs/sdlc_agent_system_v2.md`:
- Brain: 500-char truncation, 1-file-1-chunk, wrong embedding model (all-minilm-l6-v2 → voyage-code-2)
- Layer 1 (Repo Map): BUILT — tree-sitter symbol extraction
- Layer 2 (Hybrid search + Qdrant): NOT BUILT
- Blackbox Tester: NOT BUILT
- Git Agent: NOT BUILT
- Observability Report: NOT BUILT
