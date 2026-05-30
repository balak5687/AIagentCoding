# Build Issue #4 — Job Module

You are building the complete Job Module for GarageHQ. You have full permissions to read, write, and execute.

## Your goal
Build all 36 tasks from the planner output. Work sequentially through dependency groups.

## First — read these files
1. /home/ubuntu/bala/AIagentCoding/planner_output_issue4.md — the full plan
2. /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/dashboard_service.py — service patterns
3. /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/repositories/work_order_repository.py — repo patterns
4. /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/dashboard.py — route patterns
5. /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/__init__.py — how to register blueprints
6. /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/work_order.py — existing work order model
7. /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/dashboardService.ts — frontend service pattern
8. /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useDashboard.ts — hook pattern
9. /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx — existing routes

## Skills to use
For each task type, use the matching playbook:
- Backend models: /home/ubuntu/bala/AIagentCoding/playbooks/tasks/add_database_model.yaml
- Backend CRUD routes: /home/ubuntu/bala/AIagentCoding/playbooks/tasks/add_crud_endpoint.yaml
- Backend service methods: /home/ubuntu/bala/AIagentCoding/playbooks/tasks/add_service_method.yaml
- React components: /home/ubuntu/bala/AIagentCoding/playbooks/react/react-dashboard-component.md
- React API service: /home/ubuntu/bala/AIagentCoding/playbooks/react/react-query-service.md
- React tables: /home/ubuntu/bala/AIagentCoding/playbooks/react/react-tanstack-table.md
- React charts: /home/ubuntu/bala/AIagentCoding/playbooks/react/react-recharts-chart.md

## Rules
- Both repos are on branch: testing/sdlc-issue-4
- Backend path: /home/ubuntu/greasynuts/dev/backend/GreasyNuts/
- React path: /home/ubuntu/greasynuts/dev/GreasyNutsReact/
- All new Pydantic fields MUST be Optional (backward compat with existing work_orders)
- DynamoDB max 5 GSIs per table
- After writing backend files: python3 -m py_compile <file> to verify syntax
- After writing React files: cd /home/ubuntu/greasynuts/dev/GreasyNutsReact && npx tsc --noEmit
- After all files written: restart backend with: cd /home/ubuntu/greasynuts/dev/backend/GreasyNuts && bash deploy_local.sh

## Build order (follow dependency groups from planner)
Group 1 (parallel — no deps): task_1, task_2, task_3, task_4, task_5, task_13
Group 2: task_6, task_9, task_14, task_15, task_21, task_29, task_30, task_31, task_32
Group 3: task_7, task_10, task_16
Group 4: task_8, task_11, task_17, task_18, task_19
Group 5: task_12, task_20
Group 6: task_28
Group 7: task_34
Group 8: task_35
Group 9: task_22, task_23, task_24, task_25, task_26, task_27
Group 10: task_33, task_36

## After completing all tasks
1. Run: cd /home/ubuntu/greasynuts/dev/backend/GreasyNuts && bash deploy_local.sh
2. Test: curl -s http://127.0.0.1:5000/api/jobs | python3 -m json.tool | head -20
3. Run: cd /home/ubuntu/greasynuts/dev/GreasyNutsReact && npm run build 2>&1 | tail -5
4. Report: what was built, any errors found and fixed, any tasks skipped

Start now. Read the planner output first, then build Group 1 tasks.
