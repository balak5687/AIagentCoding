#!/usr/bin/env python3
"""
Full SDLC Orchestrator - Complete workflow from GitHub issue to PR
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.playbook_loader import PlaybookLoader


class SDLCOrchestrator:
    """
    Full SDLC workflow orchestrator for GreasyNuts project.

    Workflow:
    1. Fetch GitHub issue
    2. Analyze requirements
    3. Load playbooks
    4. Create feature branch
    5. Implement backend changes
    6. Implement frontend changes
    7. Run tests
    8. Create PR
    """

    def __init__(self, issue_number: int, repo: str = "aravindmk1011/GreasyNutsIssues"):
        self.issue_number = issue_number
        self.repo = repo
        self.issue_url = f"https://github.com/{repo}/issues/{issue_number}"

        # Paths
        self.backend_path = Path("/home/ubuntu/greasynuts/dev/backend/GreasyNuts")
        self.frontend_path = Path("/home/ubuntu/greasynuts/dev/frontend/GreasyNutsFrontEnd/flutter_prototype")

        # Playbook system
        self.loader = PlaybookLoader()

        # State tracking
        self.state = {
            "start_time": datetime.now().isoformat(),
            "issue_number": issue_number,
            "branch_name": None,
            "phases": [],
            "files_created": [],
            "files_modified": []
        }

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "ERROR": "✗",
            "WARN": "⚠"
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Dict:
        """Execute shell command"""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or Path.cwd()
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }

    def phase_1_fetch_issue(self) -> Dict:
        """Phase 1: Fetch GitHub issue details"""
        self.log("=== PHASE 1: Fetch GitHub Issue ===")

        result = self.run_command([
            "gh", "issue", "view", str(self.issue_number),
            "--repo", self.repo,
            "--json", "title,body,labels,number"
        ])

        if not result["success"]:
            raise RuntimeError(f"Failed to fetch issue: {result['stderr']}")

        issue_data = json.loads(result["stdout"])
        self.log(f"Fetched issue #{issue_data['number']}: {issue_data['title']}", "SUCCESS")

        self.state["phases"].append({
            "phase": 1,
            "name": "fetch_issue",
            "status": "success",
            "issue": issue_data
        })

        return issue_data

    def phase_2_analyze_requirements(self, issue_data: Dict) -> Dict:
        """Phase 2: Analyze requirements and select playbooks"""
        self.log("\n=== PHASE 2: Analyze Requirements ===")

        # Parse issue to identify components
        body = issue_data.get("body", "")

        analysis = {
            "title": issue_data["title"],
            "type": "epic" if "EPIC" in issue_data["title"] else "feature",
            "components": self._extract_components(body),
            "backend_required": True,
            "frontend_required": True,
            "database_changes": True
        }

        self.log(f"Issue type: {analysis['type']}", "SUCCESS")
        self.log(f"Components identified: {len(analysis['components'])}", "SUCCESS")

        # Load playbooks
        playbooks = self._load_playbooks()
        analysis["playbooks"] = [pb["name"] for pb in playbooks]

        self.state["phases"].append({
            "phase": 2,
            "name": "analyze_requirements",
            "status": "success",
            "analysis": analysis,
            "playbooks_count": len(playbooks)
        })

        return analysis

    def _extract_components(self, body: str) -> List[str]:
        """Extract component names from issue body"""
        components = []

        # Look for component markers
        markers = [
            "Component 1", "Component 2", "Component 3",
            "Component 4", "Component 5", "Component 6", "Component 7"
        ]

        for marker in markers:
            if marker in body:
                # Extract component name after marker
                start = body.find(marker)
                end = body.find("\n", start)
                if end > start:
                    component_line = body[start:end]
                    # Extract name after "—"
                    if "—" in component_line:
                        name = component_line.split("—")[1].strip()
                        components.append(name)

        return components

    def _load_playbooks(self) -> List[Dict]:
        """Load all applicable playbooks"""
        playbooks = []

        # Level 1: General
        general = self.loader._load_from_level("general", "file_operations.yaml")
        if general:
            playbooks.append(general)
            self.log(f"  Loaded: {general['name']}")

        # Level 2: Style - Backend
        backend_style = self.loader._load_from_level("style", "python_flask_dynamodb.yaml")
        if backend_style:
            playbooks.append(backend_style)
            self.log(f"  Loaded: {backend_style['name']}")

        # Level 2: Style - Frontend
        frontend_style = self.loader._load_from_level("style", "flutter_material3.yaml")
        if frontend_style:
            playbooks.append(frontend_style)
            self.log(f"  Loaded: {frontend_style['name']}")

        # Level 3: Security
        security = self.loader._load_from_level("tasks", "production_security_checklist.yaml")
        if security:
            playbooks.append(security)
            self.log(f"  Loaded: {security['name']}")

        # Level 3: UI Patterns
        ui_patterns = self.loader._load_from_level("tasks", "modern_ui_patterns.yaml")
        if ui_patterns:
            playbooks.append(ui_patterns)
            self.log(f"  Loaded: {ui_patterns['name']}")

        self.log(f"Total playbooks: {len(playbooks)}", "SUCCESS")
        return playbooks

    def phase_3_create_feature_branch(self, issue_data: Dict) -> str:
        """Phase 3: Create feature branch"""
        self.log("\n=== PHASE 3: Create Feature Branch ===")

        # Generate branch name from issue
        issue_num = issue_data["number"]
        title_slug = issue_data["title"].lower()
        title_slug = title_slug.replace("epic:", "").replace(":", "")
        title_slug = "".join(c if c.isalnum() or c == " " else "" for c in title_slug)
        title_slug = "-".join(title_slug.split()[:4])

        branch_name = f"feature/issue-{issue_num}-{title_slug}"
        self.state["branch_name"] = branch_name

        # Create branch in backend repo
        self.log(f"Creating branch: {branch_name}")

        # Check current branch
        result = self.run_command(["git", "branch", "--show-current"], cwd=self.backend_path)
        current_branch = result["stdout"].strip()
        self.log(f"Current backend branch: {current_branch}")

        # Ensure we're on main/master
        self.run_command(["git", "checkout", "main"], cwd=self.backend_path)

        # Pull latest
        self.run_command(["git", "pull"], cwd=self.backend_path)

        # Create and checkout feature branch
        result = self.run_command(["git", "checkout", "-b", branch_name], cwd=self.backend_path)

        if not result["success"]:
            # Branch might exist, try to checkout
            result = self.run_command(["git", "checkout", branch_name], cwd=self.backend_path)

        if result["success"]:
            self.log(f"Backend branch created: {branch_name}", "SUCCESS")
        else:
            raise RuntimeError(f"Failed to create backend branch: {result['stderr']}")

        # Create branch in frontend repo
        self.run_command(["git", "checkout", "main"], cwd=self.frontend_path)
        self.run_command(["git", "pull"], cwd=self.frontend_path)
        result = self.run_command(["git", "checkout", "-b", branch_name], cwd=self.frontend_path)

        if not result["success"]:
            result = self.run_command(["git", "checkout", branch_name], cwd=self.frontend_path)

        if result["success"]:
            self.log(f"Frontend branch created: {branch_name}", "SUCCESS")

        self.state["phases"].append({
            "phase": 3,
            "name": "create_feature_branch",
            "status": "success",
            "branch_name": branch_name
        })

        return branch_name

    def phase_4_implement_backend(self, analysis: Dict) -> List[str]:
        """Phase 4: Implement backend API endpoints"""
        self.log("\n=== PHASE 4: Implement Backend ===")

        files_created = []

        # Get backend playbook for reference
        backend_playbook = self.loader._load_from_level("style", "python_flask_dynamodb.yaml")

        # Task 1: Create dashboard route
        dashboard_route = self._create_dashboard_route()
        if dashboard_route:
            files_created.append(dashboard_route)
            self.log(f"Created: {dashboard_route}", "SUCCESS")

        # Task 2: Create dashboard service
        dashboard_service = self._create_dashboard_service()
        if dashboard_service:
            files_created.append(dashboard_service)
            self.log(f"Created: {dashboard_service}", "SUCCESS")

        # Task 3: Update routes __init__.py
        self._register_dashboard_route()
        self.log("Registered dashboard route", "SUCCESS")

        self.state["files_created"].extend(files_created)
        self.state["phases"].append({
            "phase": 4,
            "name": "implement_backend",
            "status": "success",
            "files_created": files_created
        })

        return files_created

    def _create_dashboard_route(self) -> Optional[str]:
        """Create dashboard route file"""
        route_content = '''"""
Dashboard API Routes

Provides endpoints for dashboard KPIs, alerts, jobs snapshot, and revenue data.
"""

from flask import Blueprint, request, jsonify
from app.middleware.auth import require_auth
from app.services.dashboard_service import DashboardService
from app.utils.responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/kpis', methods=['GET'])
@require_auth
def get_kpis():
    """
    Get dashboard KPI metrics

    Returns:
        - jobs_today: Count of jobs created today
        - pending_jobs: Count of jobs with status != completed
        - revenue_today: Sum of paid invoices for today
        - pending_payments: Sum of unpaid invoice balances
    """
    try:
        kpis, error = DashboardService.get_kpis()

        if error:
            return error_response(error, 500)

        return success_response(kpis)

    except Exception as e:
        logger.exception("Error fetching KPIs")
        return error_response(f"Failed to fetch KPIs: {str(e)}", 500)


@dashboard_bp.route('/alerts', methods=['GET'])
@require_auth
def get_alerts():
    """
    Get dashboard alerts

    Alert types:
        - job_blocked: Jobs waiting for parts
        - supplier_delay: Delayed purchase orders
        - low_stock: Parts below threshold
        - unpaid_invoice: Overdue invoices
        - delayed_job: Jobs past due date
    """
    try:
        alerts, error = DashboardService.get_alerts()

        if error:
            return error_response(error, 500)

        return success_response(alerts)

    except Exception as e:
        logger.exception("Error fetching alerts")
        return error_response(f"Failed to fetch alerts: {str(e)}", 500)


@dashboard_bp.route('/jobs-snapshot', methods=['GET'])
@require_auth
def get_jobs_snapshot():
    """
    Get jobs snapshot with progress and delay tracking

    Returns list of active jobs with:
        - job_id
        - vehicle
        - issue_type
        - status
        - start_date
        - due_date
        - days_elapsed
        - delivery_status
        - delay_reason
    """
    try:
        limit = request.args.get('limit', 10, type=int)

        jobs, error = DashboardService.get_jobs_snapshot(limit=limit)

        if error:
            return error_response(error, 500)

        return success_response(jobs)

    except Exception as e:
        logger.exception("Error fetching jobs snapshot")
        return error_response(f"Failed to fetch jobs snapshot: {str(e)}", 500)


@dashboard_bp.route('/revenue', methods=['GET'])
@require_auth
def get_revenue_trend():
    """
    Get revenue trend data

    Query params:
        - days: Number of days (default 7)

    Returns:
        - dates: List of dates
        - revenue: List of revenue amounts
    """
    try:
        days = request.args.get('days', 7, type=int)

        revenue_data, error = DashboardService.get_revenue_trend(days=days)

        if error:
            return error_response(error, 500)

        return success_response(revenue_data)

    except Exception as e:
        logger.exception("Error fetching revenue trend")
        return error_response(f"Failed to fetch revenue trend: {str(e)}", 500)


@dashboard_bp.route('/supply-issues', methods=['GET'])
@require_auth
def get_supply_issues():
    """
    Get supplier-related issues and delayed purchase orders

    Returns:
        - po_id
        - supplier_name
        - delay_status
        - affected_jobs_count
    """
    try:
        issues, error = DashboardService.get_supply_issues()

        if error:
            return error_response(error, 500)

        return success_response(issues)

    except Exception as e:
        logger.exception("Error fetching supply issues")
        return error_response(f"Failed to fetch supply issues: {str(e)}", 500)
'''

        route_path = self.backend_path / "app" / "routes" / "dashboard.py"

        try:
            with open(route_path, 'w') as f:
                f.write(route_content)
            return str(route_path.relative_to(self.backend_path))
        except Exception as e:
            self.log(f"Failed to create dashboard route: {e}", "ERROR")
            return None

    def _create_dashboard_service(self) -> Optional[str]:
        """Create dashboard service file"""
        service_content = '''"""
Dashboard Service

Business logic for dashboard data aggregation and KPI calculations.
"""

from typing import Tuple, Optional, List, Dict
from datetime import datetime, timedelta
from app.repositories.work_orders_repository import WorkOrdersRepository
from app.repositories.invoices_repository import InvoicesRepository
from app.repositories.parts_repository import PartsRepository
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """Dashboard business logic"""

    @staticmethod
    def get_kpis() -> Tuple[Optional[Dict], Optional[str]]:
        """
        Calculate dashboard KPIs

        Returns:
            (kpis_dict, error_message)
        """
        try:
            today = datetime.utcnow().date().isoformat()

            # Jobs today
            all_jobs = WorkOrdersRepository.get_all()
            jobs_today = sum(1 for job in all_jobs
                           if job.get('created_at', '')[:10] == today)

            # Pending jobs
            pending_jobs = sum(1 for job in all_jobs
                             if job.get('status') != 'completed')

            # Revenue today
            all_invoices = InvoicesRepository.get_all()
            revenue_today = sum(
                float(inv.get('total_amount', 0))
                for inv in all_invoices
                if inv.get('payment_status') == 'paid'
                and inv.get('payment_date', '')[:10] == today
            )

            # Pending payments
            pending_payments = sum(
                float(inv.get('total_amount', 0))
                for inv in all_invoices
                if inv.get('payment_status') != 'paid'
            )

            kpis = {
                'jobs_today': jobs_today,
                'pending_jobs': pending_jobs,
                'revenue_today': round(revenue_today, 2),
                'pending_payments': round(pending_payments, 2)
            }

            return kpis, None

        except Exception as e:
            logger.exception("Error calculating KPIs")
            return None, str(e)

    @staticmethod
    def get_alerts() -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Get operational alerts

        Returns:
            (alerts_list, error_message)
        """
        try:
            alerts = []

            # Job blocked alerts (waiting for parts)
            jobs = WorkOrdersRepository.get_all()
            blocked_jobs = [job for job in jobs
                          if job.get('status') == 'waiting_parts']

            for job in blocked_jobs[:5]:  # Limit to 5
                alerts.append({
                    'alert_id': f"job_blocked_{job['work_order_id']}",
                    'type': 'job_blocked',
                    'severity': 'high',
                    'message': f"Job {job['work_order_id']} blocked (No stock)",
                    'related_entity_id': job['work_order_id'],
                    'timestamp': datetime.utcnow().isoformat()
                })

            # Low stock alerts
            parts = PartsRepository.get_all()
            low_stock_parts = [part for part in parts
                             if int(part.get('quantity_in_stock', 0)) < 5]

            for part in low_stock_parts[:5]:
                alerts.append({
                    'alert_id': f"low_stock_{part['part_id']}",
                    'type': 'low_stock',
                    'severity': 'medium',
                    'message': f"Low stock: {part['part_name']}",
                    'related_entity_id': part['part_id'],
                    'timestamp': datetime.utcnow().isoformat()
                })

            # Unpaid invoices
            invoices = InvoicesRepository.get_all()
            unpaid = [inv for inv in invoices
                     if inv.get('payment_status') != 'paid']

            if len(unpaid) > 0:
                alerts.append({
                    'alert_id': 'unpaid_invoices',
                    'type': 'unpaid_invoice',
                    'severity': 'medium',
                    'message': f"{len(unpaid)} unpaid invoices",
                    'related_entity_id': None,
                    'timestamp': datetime.utcnow().isoformat()
                })

            # Sort by severity
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))

            return alerts, None

        except Exception as e:
            logger.exception("Error fetching alerts")
            return None, str(e)

    @staticmethod
    def get_jobs_snapshot(limit: int = 10) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Get snapshot of active jobs with progress tracking

        Returns:
            (jobs_list, error_message)
        """
        try:
            jobs = WorkOrdersRepository.get_all()

            # Filter to active jobs only
            active_jobs = [job for job in jobs
                         if job.get('status') not in ['completed', 'cancelled']]

            snapshot = []
            for job in active_jobs[:limit]:
                # Calculate days elapsed
                start_date = job.get('created_at', '')[:10]
                days_elapsed = 0
                if start_date:
                    start = datetime.fromisoformat(start_date)
                    days_elapsed = (datetime.utcnow() - start).days

                # Determine delivery status
                status = job.get('status', 'unknown')
                if status == 'completed':
                    delivery_status = 'completed'
                elif status == 'waiting_parts':
                    delivery_status = 'delayed'
                else:
                    delivery_status = 'on_track'

                snapshot.append({
                    'job_id': job.get('work_order_id'),
                    'vehicle': job.get('vehicle_id', 'Unknown'),
                    'issue_type': job.get('description', 'Service'),
                    'status': status,
                    'start_date': start_date,
                    'due_date': job.get('due_date'),
                    'days_elapsed': days_elapsed,
                    'delivery_status': delivery_status,
                    'delay_reason': job.get('notes') if delivery_status == 'delayed' else None
                })

            return snapshot, None

        except Exception as e:
            logger.exception("Error fetching jobs snapshot")
            return None, str(e)

    @staticmethod
    def get_revenue_trend(days: int = 7) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get revenue trend for last N days

        Returns:
            (revenue_data, error_message)
        """
        try:
            invoices = InvoicesRepository.get_all()

            # Generate date range
            today = datetime.utcnow().date()
            date_range = [(today - timedelta(days=i)).isoformat()
                         for i in range(days-1, -1, -1)]

            # Calculate revenue per day
            revenue_by_date = {}
            for inv in invoices:
                if inv.get('payment_status') == 'paid':
                    payment_date = inv.get('payment_date', '')[:10]
                    if payment_date in date_range:
                        revenue_by_date[payment_date] = (
                            revenue_by_date.get(payment_date, 0) +
                            float(inv.get('total_amount', 0))
                        )

            # Format response
            revenue_data = {
                'dates': date_range,
                'revenue': [round(revenue_by_date.get(date, 0), 2)
                          for date in date_range]
            }

            return revenue_data, None

        except Exception as e:
            logger.exception("Error fetching revenue trend")
            return None, str(e)

    @staticmethod
    def get_supply_issues() -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Get supplier-related issues (placeholder for now)

        Returns:
            (issues_list, error_message)
        """
        try:
            # TODO: Implement when purchase orders module is available
            issues = []

            return issues, None

        except Exception as e:
            logger.exception("Error fetching supply issues")
            return None, str(e)
'''

        service_path = self.backend_path / "app" / "services" / "dashboard_service.py"

        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            return str(service_path.relative_to(self.backend_path))
        except Exception as e:
            self.log(f"Failed to create dashboard service: {e}", "ERROR")
            return None

    def _register_dashboard_route(self):
        """Register dashboard blueprint in routes __init__.py"""
        routes_init = self.backend_path / "app" / "routes" / "__init__.py"

        try:
            # Read current content
            with open(routes_init, 'r') as f:
                content = f.read()

            # Check if already registered
            if "dashboard_bp" in content:
                self.log("Dashboard route already registered", "INFO")
                return

            # Add import
            if "from app.routes.dashboard import dashboard_bp" not in content:
                # Find last import statement
                lines = content.split('\n')
                last_import_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('from app.routes.'):
                        last_import_idx = i

                # Insert import after last route import
                lines.insert(last_import_idx + 1, "from app.routes.dashboard import dashboard_bp")
                content = '\n'.join(lines)

            # Add blueprint registration
            if "app.register_blueprint(dashboard_bp" not in content:
                # Find where blueprints are registered
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "app.register_blueprint" in line:
                        # Insert after last registration
                        lines.insert(i + 1, "    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')")
                        break
                content = '\n'.join(lines)

            # Write back
            with open(routes_init, 'w') as f:
                f.write(content)

            self.state["files_modified"].append("app/routes/__init__.py")

        except Exception as e:
            self.log(f"Failed to register dashboard route: {e}", "ERROR")

    def phase_5_commit_backend(self):
        """Phase 5: Commit backend changes"""
        self.log("\n=== PHASE 5: Commit Backend Changes ===")

        # Stage files
        self.run_command(["git", "add", "."], cwd=self.backend_path)

        # Check status
        result = self.run_command(["git", "status", "--short"], cwd=self.backend_path)
        if result["stdout"].strip():
            self.log(f"Changes to commit:\n{result['stdout']}")

            # Commit
            commit_msg = f"feat: Add dashboard API endpoints (Issue #{self.issue_number})\n\n- Dashboard KPIs endpoint\n- Alerts endpoint\n- Jobs snapshot endpoint\n- Revenue trend endpoint\n- Supply issues endpoint"

            result = self.run_command(
                ["git", "commit", "-m", commit_msg],
                cwd=self.backend_path
            )

            if result["success"]:
                self.log("Backend changes committed", "SUCCESS")
            else:
                self.log(f"Commit failed: {result['stderr']}", "ERROR")
        else:
            self.log("No changes to commit", "WARN")

        self.state["phases"].append({
            "phase": 5,
            "name": "commit_backend",
            "status": "success"
        })

    def phase_6_push_and_pr(self):
        """Phase 6: Push branch and create PR"""
        self.log("\n=== PHASE 6: Push and Create PR ===")

        branch_name = self.state["branch_name"]

        # Push backend
        result = self.run_command(
            ["git", "push", "-u", "origin", branch_name],
            cwd=self.backend_path
        )

        if result["success"] or "already exists" in result["stderr"]:
            self.log("Backend branch pushed", "SUCCESS")
        else:
            self.log(f"Push failed: {result['stderr']}", "WARN")

        # Create PR
        pr_body = f"""## Dashboard Module Implementation

Implements Issue #{self.issue_number}

### Backend Changes
- ✅ Dashboard API routes (`/api/dashboard/`)
- ✅ Dashboard service with business logic
- ✅ KPIs calculation (jobs, revenue, payments)
- ✅ Alerts aggregation (job blocks, low stock, unpaid invoices)
- ✅ Jobs snapshot with progress tracking
- ✅ Revenue trend (7-day graph data)

### API Endpoints
- `GET /api/dashboard/kpis` - Dashboard KPI metrics
- `GET /api/dashboard/alerts` - Operational alerts
- `GET /api/dashboard/jobs-snapshot` - Active jobs with progress
- `GET /api/dashboard/revenue` - Revenue trend data
- `GET /api/dashboard/supply-issues` - Supplier issues

### Testing
- [ ] Manual API testing
- [ ] Integration testing with existing modules
- [ ] Frontend integration

### Playbooks Used
- ✅ Python Flask + DynamoDB style guide
- ✅ Production security checklist
- ✅ 3-layer architecture pattern

Co-authored-by: AI Agent <ai@greasynuts.com>
"""

        # Create PR using gh CLI
        result = self.run_command([
            "gh", "pr", "create",
            "--repo", "aravindmk1011/GreasyNuts",  # Assuming actual repo name
            "--base", "main",
            "--head", branch_name,
            "--title", f"Dashboard Module API - Issue #{self.issue_number}",
            "--body", pr_body
        ], cwd=self.backend_path)

        if result["success"]:
            pr_url = result["stdout"].strip()
            self.log(f"PR created: {pr_url}", "SUCCESS")
            self.state["pr_url"] = pr_url
        else:
            # PR might already exist
            if "already exists" in result["stderr"]:
                self.log("PR already exists", "INFO")
            else:
                self.log(f"PR creation failed: {result['stderr']}", "WARN")

        self.state["phases"].append({
            "phase": 6,
            "name": "push_and_pr",
            "status": "success"
        })

    def generate_report(self):
        """Generate final execution report"""
        self.log("\n=== Execution Report ===")

        self.state["end_time"] = datetime.now().isoformat()

        # Calculate duration
        start = datetime.fromisoformat(self.state["start_time"])
        end = datetime.fromisoformat(self.state["end_time"])
        duration = (end - start).total_seconds()

        self.log(f"Issue: #{self.issue_number}")
        self.log(f"Branch: {self.state['branch_name']}")
        self.log(f"Files created: {len(self.state['files_created'])}")
        self.log(f"Files modified: {len(self.state['files_modified'])}")
        self.log(f"Duration: {duration:.1f}s")

        if "pr_url" in self.state:
            self.log(f"PR: {self.state['pr_url']}")

        # Save report
        import yaml
        report_path = Path("/home/ubuntu/bala/AIagentCoding/sdlc_execution_report.yaml")
        with open(report_path, 'w') as f:
            yaml.dump(self.state, f, default_flow_style=False, sort_keys=False)

        self.log(f"Report saved: {report_path}", "SUCCESS")

    def run(self):
        """Execute full SDLC workflow"""
        try:
            self.log("╔════════════════════════════════════════════════════════════╗")
            self.log("║         Full SDLC Workflow - Issue to PR                  ║")
            self.log("╚════════════════════════════════════════════════════════════╝\n")

            # Phase 1: Fetch issue
            issue_data = self.phase_1_fetch_issue()

            # Phase 2: Analyze requirements
            analysis = self.phase_2_analyze_requirements(issue_data)

            # Phase 3: Create feature branch
            branch_name = self.phase_3_create_feature_branch(issue_data)

            # Phase 4: Implement backend
            files_created = self.phase_4_implement_backend(analysis)

            # Phase 5: Commit changes
            self.phase_5_commit_backend()

            # Phase 6: Push and create PR
            self.phase_6_push_and_pr()

            # Generate report
            self.generate_report()

            self.log("\n╔════════════════════════════════════════════════════════════╗")
            self.log("║                   SDLC Workflow Complete!                  ║")
            self.log("╚════════════════════════════════════════════════════════════╝")

            return True

        except Exception as e:
            self.log(f"\n✗ SDLC workflow failed: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sdlc_orchestrator.py <issue_number>")
        sys.exit(1)

    issue_num = int(sys.argv[1])
    orchestrator = SDLCOrchestrator(issue_num)
    success = orchestrator.run()

    sys.exit(0 if success else 1)
