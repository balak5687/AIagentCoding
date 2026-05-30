#!/usr/bin/env python3
"""
Test Dashboard Implementation - Issue #3
Tests the playbook system with a real GreasyNuts task
"""

import sys
import os
import yaml
import subprocess
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.playbook_loader import PlaybookLoader

class DashboardTestOrchestrator:
    """Orchestrates dashboard implementation using playbook system"""

    def __init__(self):
        self.loader = PlaybookLoader()
        self.issue_url = "https://github.com/aravindmk1011/GreasyNutsIssues/issues/3"
        self.issue_number = 3
        self.repo = "aravindmk1011/GreasyNutsIssues"
        self.greasynuts_path = Path("/home/ubuntu/greasynuts/dev")
        self.results = {
            "start_time": datetime.now().isoformat(),
            "phases": []
        }

    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def fetch_issue_details(self):
        """Fetch issue from GitHub"""
        self.log("=== PHASE 1: Fetch GitHub Issue ===")

        result = subprocess.run(
            ["gh", "issue", "view", str(self.issue_number),
             "--repo", self.repo,
             "--json", "title,body,labels"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch issue: {result.stderr}")

        import json
        issue_data = json.loads(result.stdout)

        self.log(f"✓ Fetched Issue: {issue_data['title']}")
        return issue_data

    def select_playbooks(self, issue_data):
        """Select applicable playbooks for this task"""
        self.log("\n=== PHASE 2: Select Playbooks ===")

        playbooks = []

        # Level 1: General operations
        general = self.loader._load_from_level("general", "file_operations.yaml")
        if general:
            playbooks.append(general)
            self.log(f"  Level 1 (general): {general['name']}")

        # Level 2: Style - Backend (Python Flask + DynamoDB)
        backend_style = self.loader._load_from_level("style", "python_flask_dynamodb.yaml")
        if backend_style:
            playbooks.append(backend_style)
            self.log(f"  Level 2 (style): {backend_style['name']}")

        # Level 2: Style - Frontend (Flutter Material3)
        frontend_style = self.loader._load_from_level("style", "flutter_material3.yaml")
        if frontend_style:
            playbooks.append(frontend_style)
            self.log(f"  Level 2 (style): {frontend_style['name']}")

        # Level 3: Task - Production Security
        security = self.loader._load_from_level("tasks", "production_security_checklist.yaml")
        if security:
            playbooks.append(security)
            self.log(f"  Level 3 (tasks): {security['name']}")

        # Level 3: Task - Modern UI Patterns
        ui_patterns = self.loader._load_from_level("tasks", "modern_ui_patterns.yaml")
        if ui_patterns:
            playbooks.append(ui_patterns)
            self.log(f"  Level 3 (tasks): {ui_patterns['name']}")

        self.log(f"\n✓ Total playbooks selected: {len(playbooks)}")

        return playbooks

    def analyze_codebase_structure(self):
        """Analyze existing codebase structure"""
        self.log("\n=== PHASE 3: Analyze Codebase ===")

        # Backend structure
        backend_path = self.greasynuts_path / "backend" / "GreasyNuts"
        frontend_path = self.greasynuts_path / "frontend" / "GreasyNutsFrontEnd"

        # Check backend modules
        backend_app = backend_path / "app"
        if backend_app.exists():
            routes_dir = backend_app / "routes"
            services_dir = backend_app / "services"
            repos_dir = backend_app / "repositories"

            self.log(f"✓ Backend structure found:")
            self.log(f"  Routes: {routes_dir.exists()}")
            self.log(f"  Services: {services_dir.exists()}")
            self.log(f"  Repositories: {repos_dir.exists()}")

            # List existing routes
            if routes_dir.exists():
                routes = list(routes_dir.glob("*.py"))
                self.log(f"  Existing routes: {len(routes)}")
                for route in routes[:5]:
                    self.log(f"    - {route.name}")

        # Check frontend structure
        if frontend_path.exists():
            flutter_app = frontend_path / "flutter_prototype"
            if flutter_app.exists():
                lib_dir = flutter_app / "lib"
                self.log(f"✓ Frontend structure found:")
                self.log(f"  Flutter app: {lib_dir.exists()}")

                if lib_dir.exists():
                    screens = lib_dir / "screens"
                    if screens.exists():
                        screen_list = list(screens.glob("*"))
                        self.log(f"  Existing screens: {len(screen_list)}")

        return {
            "backend_path": str(backend_path),
            "frontend_path": str(frontend_path),
            "has_3_layer_architecture": True
        }

    def create_implementation_plan(self, issue_data, playbooks, codebase_info):
        """Create detailed implementation plan using playbooks"""
        self.log("\n=== PHASE 4: Create Implementation Plan ===")

        plan = {
            "epic": issue_data["title"],
            "phases": []
        }

        # Phase 1: Backend API Endpoints
        backend_tasks = [
            {
                "id": "backend_1",
                "name": "Dashboard KPI Endpoints",
                "description": "Create /api/dashboard/kpis endpoint for jobs_today, pending_jobs, revenue_today, pending_payments",
                "playbooks": ["python_flask_dynamodb", "add_crud_endpoint"],
                "files_to_create": ["app/routes/dashboard.py", "app/services/dashboard_service.py"],
                "estimated_effort": "medium",
                "dependencies": []
            },
            {
                "id": "backend_2",
                "name": "Dashboard Alerts Endpoint",
                "description": "Create /api/dashboard/alerts for job_blocked, supplier_delay, low_stock alerts",
                "playbooks": ["python_flask_dynamodb"],
                "files_to_create": ["app/services/alert_service.py"],
                "estimated_effort": "medium",
                "dependencies": ["backend_1"]
            },
            {
                "id": "backend_3",
                "name": "Jobs Snapshot Endpoint",
                "description": "Create /api/dashboard/jobs-snapshot with job progress and delay tracking",
                "playbooks": ["python_flask_dynamodb"],
                "files_to_modify": ["app/routes/dashboard.py"],
                "estimated_effort": "medium",
                "dependencies": ["backend_1"]
            },
            {
                "id": "backend_4",
                "name": "Revenue Graph Endpoint",
                "description": "Create /api/dashboard/revenue with 7-day trend data",
                "playbooks": ["python_flask_dynamodb"],
                "files_to_modify": ["app/routes/dashboard.py"],
                "estimated_effort": "low",
                "dependencies": ["backend_1"]
            }
        ]

        # Phase 2: Frontend Dashboard UI
        frontend_tasks = [
            {
                "id": "frontend_1",
                "name": "Dashboard Screen Layout",
                "description": "Create dashboard_screen.dart with responsive layout structure",
                "playbooks": ["flutter_material3", "modern_ui_patterns"],
                "files_to_create": ["lib/screens/dashboard/dashboard_screen.dart"],
                "estimated_effort": "high",
                "dependencies": []
            },
            {
                "id": "frontend_2",
                "name": "KPI Cards Widget",
                "description": "Create stat_card.dart component for KPI display",
                "playbooks": ["flutter_material3", "modern_ui_patterns"],
                "files_to_create": ["lib/components/dashboard/stat_card.dart"],
                "estimated_effort": "low",
                "dependencies": ["frontend_1"]
            },
            {
                "id": "frontend_3",
                "name": "Alerts Panel Widget",
                "description": "Create alerts_panel.dart with severity-based styling",
                "playbooks": ["flutter_material3", "modern_ui_patterns"],
                "files_to_create": ["lib/components/dashboard/alerts_panel.dart"],
                "estimated_effort": "medium",
                "dependencies": ["frontend_1"]
            },
            {
                "id": "frontend_4",
                "name": "Jobs Snapshot Table",
                "description": "Create jobs_snapshot.dart with data table and status indicators",
                "playbooks": ["flutter_material3", "modern_ui_patterns"],
                "files_to_create": ["lib/components/dashboard/jobs_snapshot.dart"],
                "estimated_effort": "high",
                "dependencies": ["frontend_1"]
            },
            {
                "id": "frontend_5",
                "name": "Revenue Graph Widget",
                "description": "Create revenue_graph.dart using fl_chart package",
                "playbooks": ["flutter_material3"],
                "files_to_create": ["lib/components/dashboard/revenue_graph.dart"],
                "estimated_effort": "medium",
                "dependencies": ["frontend_1"]
            },
            {
                "id": "frontend_6",
                "name": "Dashboard Service",
                "description": "Create dashboard_service.dart for API integration",
                "playbooks": ["flutter_material3"],
                "files_to_create": ["lib/services/dashboard_service.dart"],
                "estimated_effort": "medium",
                "dependencies": []
            }
        ]

        plan["phases"] = [
            {
                "phase": 1,
                "name": "Backend API Development",
                "tasks": backend_tasks,
                "can_parallelize": True
            },
            {
                "phase": 2,
                "name": "Frontend UI Development",
                "tasks": frontend_tasks,
                "can_parallelize": True
            },
            {
                "phase": 3,
                "name": "Integration & Testing",
                "tasks": [
                    {
                        "id": "integration_1",
                        "name": "End-to-End Testing",
                        "description": "Test complete dashboard flow",
                        "estimated_effort": "medium"
                    }
                ]
            }
        ]

        self.log(f"✓ Created plan with {len(plan['phases'])} phases")
        for phase in plan["phases"]:
            self.log(f"  Phase {phase['phase']}: {phase['name']} ({len(phase['tasks'])} tasks)")

        return plan

    def validate_with_playbooks(self, plan, playbooks):
        """Validate plan against playbook best practices"""
        self.log("\n=== PHASE 5: Validate Against Playbooks ===")

        validation_results = []

        # Load security checklist
        security_playbook = None
        for pb in playbooks:
            if pb["name"] == "production_security_checklist":
                security_playbook = pb
                break

        if security_playbook:
            self.log("✓ Checking security requirements:")

            # Check if JWT auth is planned
            auth_mentioned = any(
                "auth" in task.get("description", "").lower()
                for phase in plan["phases"]
                for task in phase["tasks"]
            )

            if not auth_mentioned:
                validation_results.append({
                    "type": "security",
                    "severity": "high",
                    "message": "Plan should include authentication check on dashboard endpoints",
                    "playbook_reference": "production_security_checklist step 3"
                })
                self.log("  ⚠ Missing: Authentication validation")

            # Check if rate limiting is considered
            rate_limit_mentioned = any(
                "rate" in task.get("description", "").lower()
                for phase in plan["phases"]
                for task in phase["tasks"]
            )

            if not rate_limit_mentioned:
                validation_results.append({
                    "type": "security",
                    "severity": "medium",
                    "message": "Consider rate limiting on dashboard API endpoints",
                    "playbook_reference": "production_security_checklist step 8"
                })
                self.log("  ⚠ Consider: Rate limiting")

        # Check Flutter best practices
        flutter_playbook = None
        for pb in playbooks:
            if pb["name"] == "flutter_material3_style":
                flutter_playbook = pb
                break

        if flutter_playbook:
            self.log("✓ Checking Flutter best practices:")

            # Check if error handling is mentioned
            error_handling = any(
                "error" in task.get("description", "").lower()
                for phase in plan["phases"]
                for task in phase["tasks"]
            )

            if not error_handling:
                validation_results.append({
                    "type": "best_practice",
                    "severity": "medium",
                    "message": "Plan should include error handling for API calls",
                    "playbook_reference": "flutter_material3_style error_handling"
                })
                self.log("  ⚠ Consider: Error handling for async operations")

            # Check if loading states are mentioned
            loading_states = any(
                "loading" in task.get("description", "").lower()
                for phase in plan["phases"]
                for task in phase["tasks"]
            )

            if not loading_states:
                validation_results.append({
                    "type": "best_practice",
                    "severity": "low",
                    "message": "Plan should include loading state indicators",
                    "playbook_reference": "flutter_material3_style loading_states"
                })
                self.log("  ⚠ Consider: Loading state indicators")

        self.log(f"\n✓ Validation complete: {len(validation_results)} recommendations")

        return validation_results

    def generate_summary_report(self):
        """Generate test summary report"""
        self.log("\n=== PHASE 6: Generate Summary ===")

        self.results["end_time"] = datetime.now().isoformat()

        # Save results
        report_path = Path("/home/ubuntu/bala/AIagentCoding/test_results_dashboard.yaml")
        with open(report_path, "w") as f:
            yaml.dump(self.results, f, default_flow_style=False, sort_keys=False)

        self.log(f"✓ Test report saved: {report_path}")

        return report_path

    def run(self):
        """Execute complete test"""
        try:
            self.log("╔════════════════════════════════════════════════════════════╗")
            self.log("║  Testing Playbook System with Dashboard Implementation    ║")
            self.log("╚════════════════════════════════════════════════════════════╝")

            # Phase 1: Fetch issue
            issue_data = self.fetch_issue_details()
            self.results["phases"].append({
                "name": "fetch_issue",
                "status": "success",
                "data": issue_data
            })

            # Phase 2: Select playbooks
            playbooks = self.select_playbooks(issue_data)
            self.results["phases"].append({
                "name": "select_playbooks",
                "status": "success",
                "count": len(playbooks),
                "playbooks": [pb["name"] for pb in playbooks]
            })

            # Phase 3: Analyze codebase
            codebase_info = self.analyze_codebase_structure()
            self.results["phases"].append({
                "name": "analyze_codebase",
                "status": "success",
                "data": codebase_info
            })

            # Phase 4: Create plan
            plan = self.create_implementation_plan(issue_data, playbooks, codebase_info)
            self.results["phases"].append({
                "name": "create_plan",
                "status": "success",
                "data": plan
            })

            # Phase 5: Validate with playbooks
            validation = self.validate_with_playbooks(plan, playbooks)
            self.results["phases"].append({
                "name": "validate_plan",
                "status": "success",
                "recommendations": validation
            })

            # Phase 6: Summary
            report_path = self.generate_summary_report()

            self.log("\n╔════════════════════════════════════════════════════════════╗")
            self.log("║                    TEST SUMMARY                            ║")
            self.log("╚════════════════════════════════════════════════════════════╝")
            self.log(f"✓ Issue analyzed: {issue_data['title']}")
            self.log(f"✓ Playbooks loaded: {len(playbooks)}")
            self.log(f"✓ Implementation plan created: {sum(len(p['tasks']) for p in plan['phases'])} tasks")
            self.log(f"✓ Validation recommendations: {len(validation)}")
            self.log(f"✓ Report saved: {report_path}")

            self.log("\n🎉 Playbook system test SUCCESSFUL!")

            return True

        except Exception as e:
            self.log(f"\n❌ Test FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    orchestrator = DashboardTestOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)
