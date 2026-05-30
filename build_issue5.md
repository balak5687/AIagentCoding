# Build Issue #5 — Invoice Module

You are building the complete Invoice Module for GarageHQ. You have full permissions.

## Read first
- /home/ubuntu/bala/AIagentCoding/planner_output_issue5.md — full 20-task plan
- /home/ubuntu/bala/AIagentCoding/.project-brain/sources/functionality-brain/specs/issue-5/requirements.md — full spec
- /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/models/invoice.py — existing invoice model to replace
- /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/routes/dashboard.py — route patterns
- /home/ubuntu/greasynuts/dev/backend/GreasyNuts/app/services/job_service.py — service patterns
- /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/services/jobService.ts — frontend service pattern
- /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/hooks/useJobs.ts — hook pattern
- /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/pages/JobsPage.tsx — page pattern
- /home/ubuntu/greasynuts/dev/GreasyNutsReact/src/App.tsx — routing pattern

## Rules
- Both repos on branch: testing/sdlc-issue-5
- Backend: /home/ubuntu/greasynuts/dev/backend/GreasyNuts/
- React: /home/ubuntu/greasynuts/dev/GreasyNutsReact/
- Customer invoice table must support English AND Arabic (bilingual)
- All new Pydantic fields Optional for backward compat
- DynamoDB max 5 GSIs per table
- After each backend file: python3 -m py_compile <file>
- After all React files: cd /home/ubuntu/greasynuts/dev/GreasyNutsReact && npx tsc --noEmit
- After completion: cd /home/ubuntu/greasynuts/dev/backend/GreasyNuts && bash deploy_local.sh

## Build all 20 tasks from the planner. Start now.
