#!/usr/bin/env python3
"""
Build the full React dashboard for GarageHQ through the AI coding system.
10 tasks: service layer → layout → components → pages → wiring
"""
import sys
import asyncio
from pathlib import Path
from src.bus import FileMessageBus
from src.workflows.conversation import ConversationLoop
from src.brain import client as brain_client

BASE = "/home/ubuntu/greasynuts/feature/react-dashboard/src"

TASKS = [
    {
        "id": "r1",
        "name": "API service layer + types",
        "description": (
            "Create src/services/api.ts with Axios instance (baseURL from VITE_API_BASE, "
            "Bearer token from localStorage auth_token, 401 redirect to /login). "
            "Create src/services/dashboardService.ts with TypeScript interfaces: "
            "DashboardAlert, JobSnapshot, SupplyIssue, KpiCard, DashboardOverview. "
            "Export dashboardService object with: getOverview(), getKpis(preset='today'), "
            "getAlerts(), getJobsSnapshot(), getSupplyIssues(). "
            "Create src/hooks/useDashboard.ts with useQuery hooks for each endpoint, "
            "refetchInterval 60000. "
            "Follow react-query-service playbook exactly."
        ),
        "files": f"{BASE}/services/api.ts",
        "approach": "deterministic",
    },
    {
        "id": "r2",
        "name": "Auth service + login page",
        "description": (
            "Create src/services/authService.ts with login(email, password) that POSTs to "
            "/api/auth/login, stores token in localStorage as auth_token, returns user object. "
            "Create src/pages/LoginPage.tsx — clean centered card with GarageHQ logo text, "
            "email + password fields, Sign In button. "
            "On success navigate to /dashboard. On error show red error message inline. "
            "Style: white card on gradient background (indigo to purple), Tailwind only. "
            "Loading spinner on submit button. No layout shell — standalone page."
        ),
        "files": f"{BASE}/pages/LoginPage.tsx",
        "approach": "cognitive",
    },
    {
        "id": "r3",
        "name": "App layout shell with sidebar + top bar",
        "description": (
            "Create src/components/layout/AppLayout.tsx — the persistent shell. "
            "Dark navy sidebar (#1a2332) 260px wide with: GarageHQ logo at top, "
            "navigation items (Dashboard, Jobs, Customers, Inventory, Invoices, Suppliers, Reports, Settings) "
            "each with Lucide icon. Active item highlighted with white/15 background. "
            "Today's Overview section at bottom (live Jobs count + Revenue from useDashboardKpis). "
            "Quick Actions: New Job button, New Customer button. "
            "Top bar: white, search input (placeholder: Search jobs, customers, plates...), "
            "notification bell with count badge, refresh button, user avatar + name + role dropdown. "
            "Content area takes remaining width with gray-50 background. "
            "Mobile: sidebar hidden, hamburger menu. "
            "Props: children ReactNode, activeRoute string, onNavigate (route: string) => void."
        ),
        "files": f"{BASE}/components/layout/AppLayout.tsx",
        "approach": "cognitive",
    },
    {
        "id": "r4",
        "name": "KPI cards row",
        "description": (
            "Create src/components/dashboard/KpiCards.tsx. "
            "Fetches from useDashboardKpis(). Shows 4 cards in a responsive row (grid-cols-2 lg:grid-cols-4). "
            "Each card: colored icon background, title, large value, trend indicator (arrow + % + period). "
            "Colors: Jobs Today=blue, Pending Jobs=orange, Revenue Today=green, Expenses=red. "
            "Cards are clickable (onClick prop per card). "
            "Loading: 4 skeleton cards. "
            "Follow react-dashboard-component playbook."
        ),
        "files": f"{BASE}/components/dashboard/KpiCards.tsx",
        "approach": "deterministic",
    },
    {
        "id": "r5",
        "name": "Alerts panel",
        "description": (
            "Create src/components/dashboard/AlertsPanel.tsx. "
            "Card with Alerts header + View All button (onViewAll prop). "
            "Shows max 4 alerts from useDashboardOverview(). "
            "Each alert: colored severity dot (red=critical, orange=warning), message text, "
            "type badge, relative timestamp (e.g. '2 hours ago'). "
            "Empty state: green checkmark + No operational alerts text. "
            "Loading: skeleton list. "
            "Follow react-dashboard-component playbook."
        ),
        "files": f"{BASE}/components/dashboard/AlertsPanel.tsx",
        "approach": "deterministic",
    },
    {
        "id": "r6",
        "name": "Jobs snapshot table",
        "description": (
            "Create src/components/dashboard/JobsSnapshotTable.tsx. "
            "Card with Jobs Snapshot header + View All button. "
            "TanStack Table with columns: Vehicle (make+model+plate), Job ID (monospace truncated), "
            "Issue Type, Status (StatusBadge), Technician, Delivery Status (StatusBadge), Days. "
            "Default sort: days_elapsed descending (most urgent first). "
            "Status colors: in_progress=blue, new=gray, waiting_parts=yellow, completed=green. "
            "Delivery: delayed=red, at_risk=yellow, on_track=green. "
            "Days > 7 shown in red. Horizontal scroll on mobile. "
            "Empty state: No active jobs. "
            "Follow react-tanstack-table playbook."
        ),
        "files": f"{BASE}/components/dashboard/JobsSnapshotTable.tsx",
        "approach": "deterministic",
    },
    {
        "id": "r7",
        "name": "Revenue trend chart",
        "description": (
            "Create src/components/dashboard/RevenueTrendChart.tsx. "
            "Card with 7-Day Revenue Trend header + date range selector (Last 7 Days label). "
            "AreaChart from Recharts with gradient fill (blue #3b82f6 top, transparent bottom). "
            "X-axis: dates formatted as 'May 19' (not 2026-05-19). "
            "Y-axis: €prefix, no decimal. Tooltip: formatted currency. "
            "Below chart: Total Revenue + Daily Average summary row with border-top separator. "
            "Loading: skeleton chart height 200px. "
            "Follow react-recharts-chart playbook exactly."
        ),
        "files": f"{BASE}/components/dashboard/RevenueTrendChart.tsx",
        "approach": "deterministic",
    },
    {
        "id": "r8",
        "name": "Supply issues panel",
        "description": (
            "Create src/components/dashboard/SupplyIssuesPanel.tsx. "
            "Card with Supply Issues header + View All button. "
            "Table with columns: PO ID, Supplier, Status (red dot + delayed text), "
            "Affected Jobs (count badge), Days Overdue. "
            "Each row: red indicator dot, supplier name bold, days overdue in red if > 7. "
            "Empty state: green checkmark icon + No supply issues text. "
            "Loading: skeleton rows. "
            "Follow react-dashboard-component playbook."
        ),
        "files": f"{BASE}/components/dashboard/SupplyIssuesPanel.tsx",
        "approach": "deterministic",
    },
    {
        "id": "r9",
        "name": "Dashboard page assembly",
        "description": (
            "Create src/pages/DashboardPage.tsx — assembles all dashboard components. "
            "Layout: KpiCards full width at top. "
            "Middle row: AlertsPanel (flex 2) + JobsSnapshotTable (flex 3) side by side. "
            "Bottom row: RevenueTrendChart (flex 3) + SupplyIssuesPanel (flex 2) side by side. "
            "Mobile: single column stack. "
            "All panels use 16px gap. Page padding: p-6. "
            "Clicking View All on alerts → state change shows full alerts list inline. "
            "Auto-refresh indicator in top right showing last updated time."
        ),
        "files": f"{BASE}/pages/DashboardPage.tsx",
        "approach": "cognitive",
    },
    {
        "id": "r10",
        "name": "App routing + main entry",
        "description": (
            "Update src/App.tsx with React Router v6 routes: "
            "/ and /login → LoginPage (unauthenticated), "
            "/dashboard → DashboardPage wrapped in AppLayout (requires auth), "
            "/* → redirect to /dashboard if auth, /login if not. "
            "Create PrivateRoute component that checks localStorage auth_token. "
            "Update src/main.tsx to wrap App in QueryClientProvider (React Query) and BrowserRouter. "
            "Install react-router-dom if not already: add to package.json dependencies."
        ),
        "files": f"{BASE}/App.tsx",
        "approach": "deterministic",
    },
]


async def run_task(bus: FileMessageBus, task: dict) -> dict:
    task_id = task["id"]
    coder = "react_coder"
    bus.send(coder, task_id, {"task": task, "iteration": 1}, from_agent="orchestrator")

    import time
    start = time.time()
    while time.time() - start < 900:
        await asyncio.sleep(3)
        result = bus.wait_for_task("reviewer", task_id)
        if result:
            r = result.get("result", result)
            return r
    return {"status": "timeout", "task_id": task_id}


async def main():
    print("=" * 70)
    print("REACT DASHBOARD — Full Build via AI Coding System")
    print("=" * 70)

    if not brain_client.is_running():
        print("❌ Brain not running")
        return 1

    s = brain_client.status()
    print(f"✓ Brain — {s.get('coding_files')} files, {s.get('functionality_chunks')} chunks")
    print(f"✓ Target: /home/ubuntu/greasynuts/feature/react-dashboard/")
    print(f"Watch: tmux attach -t sdlc-agents")
    print()

    bus = FileMessageBus()
    approved = 0
    failed = 0

    # Tasks run sequentially (each builds on previous)
    for task in TASKS:
        print(f"[{task['id']}] {task['name']}...")
        result = await run_task(bus, task)
        status = result.get("status", "unknown")
        applied = result.get("diffs_applied", 0)
        symbol = "✅" if status == "approved" else "❌"
        print(f"  {symbol} {status} — {applied} diffs applied")
        if status == "approved":
            approved += 1
        else:
            failed += 1
            print(f"  Continuing despite failure...")

    print()
    print("=" * 70)
    print(f"COMPLETE — {approved} approved, {failed} failed")
    print("=" * 70)

    # Install react-router-dom and start dev server
    if approved > 0:
        import subprocess
        print("\nInstalling react-router-dom...")
        subprocess.run(
            ["npm", "install", "react-router-dom"],
            cwd="/home/ubuntu/greasynuts/feature/react-dashboard",
            capture_output=True
        )
        print("Starting dev server on port 3001...")
        subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "0.0.0.0"],
            cwd="/home/ubuntu/greasynuts/feature/react-dashboard",
            stdout=open("/tmp/react_dev.log", "w"),
            stderr=subprocess.STDOUT
        )
        print("✓ Dev server starting at http://localhost:3001")
        print("  Logs: tail -f /tmp/react_dev.log")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
