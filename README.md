# Multi-Agent SDLC System

A comprehensive AI-powered Software Development Life Cycle (SDLC) system with specialized agents for each phase of development.

## Overview

This system implements a full-blown SDLC team using AI agents with clear separation of concerns, entry/exit criteria, and quality gates at each stage.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                           │
│              (Workflow Management & Coordination)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
┌─────────▼────────┐              ┌────────▼─────────┐
│  GITHUB SCANNER  │              │  CONTEXT AGENT   │
│   (Issue Scan)   │              │  (Code Context)  │
└─────────┬────────┘              └────────┬─────────┘
          │                                 │
          └────────────┬────────────────────┘
                       │
          ┌────────────▼────────────┐
          │   DESIGNER/ARCHITECT    │
          │ (Requirement Analysis)  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │    PLANNER AGENT        │
          │  (Task Decomposition)   │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   APPROVAL AGENT        │
          │  (GitHub Notification)  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   TASK EXECUTION LOOP   │
          │   (For Each Task)       │
          └────────────┬────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
┌─────────▼────────┐   ┌───────────▼──────────┐   ┌──────────────┐
│   CODER AGENT    │   │   REVIEWER AGENT     │   │  PEER AGENT  │
│ (Implementation) │◄──┤  (Code Review)       │◄──┤ (Assistance) │
└─────────┬────────┘   └───────────┬──────────┘   └──────────────┘
          │                        │
          └────────────┬───────────┘
                       │
          ┌────────────▼────────────┐
          │    TESTER AGENT         │
          │  (Test Pack Creation)   │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │ TEST REVIEWER AGENT     │
          │ (Test Validation)       │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │  DEVOPS AGENT           │
          │ (Deploy & Monitor)      │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │    QUALITY GATE         │
          │  (Final Validation)     │
          └─────────────────────────┘
```

## Agent Roles & Responsibilities

### 1. **Orchestrator Agent**
- **Responsibility**: Workflow management and coordination
- **Entry Criteria**: System start or new GitHub issue detected
- **Exit Criteria**: Full SDLC cycle completed or failure threshold reached
- **Context**: Full system state, agent status, quality metrics

### 2. **GitHub Scanner Agent**
- **Responsibility**: Monitor GitHub for issues, parse requirements
- **Entry Criteria**: Scheduled check or webhook trigger
- **Exit Criteria**: Issue parsed and validated
- **Context**: GitHub API access, issue templates

### 3. **Context Agent**
- **Responsibility**: Repository analysis, semantic search, context retrieval
- **Entry Criteria**: New task or context request from other agents
- **Exit Criteria**: Relevant code/docs retrieved
- **Context**: Indexed codebase, vector embeddings

### 4. **Designer/Architect Agent**
- **Responsibility**: Analyze requirements, produce detailed implementation design
- **Entry Criteria**: Issue parsed and validated
- **Exit Criteria**: Design document approved with confidence >80%
- **Context**: Requirements, codebase architecture, design patterns

### 5. **Planner Agent**
- **Responsibility**: Create execution plan with task DAG and dependencies
- **Entry Criteria**: Design document approved
- **Exit Criteria**: Plan created with deterministic/AI/search strategies
- **Context**: Design doc, resource availability, complexity estimates

### 6. **Approval Agent**
- **Responsibility**: Send plan to GitHub for approval
- **Entry Criteria**: Plan created
- **Exit Criteria**: Approval received or rejection handled
- **Context**: Plan document, GitHub API access

### 7. **Coder Agent**
- **Responsibility**: Implement code changes using diff-based editing
- **Entry Criteria**: Task assigned, context available, tests defined
- **Exit Criteria**: Code complete, self-review passed, no syntax errors
- **Context**: Task specification, relevant code, design patterns

### 8. **Peer Agent**
- **Responsibility**: Assist coder, suggest improvements, prevent loops
- **Entry Criteria**: Coder requests help or stuck detection
- **Exit Criteria**: Coder unblocked or escalation needed
- **Context**: Current code state, error logs, coder's attempts

### 9. **Reviewer Agent**
- **Responsibility**: Review code quality, find issues, prevent merges of bad code
- **Entry Criteria**: Code implementation complete
- **Exit Criteria**: Review complete (approve/reject with reasons)
- **Context**: Code diff, design spec, coding standards

### 10. **Tester Agent**
- **Responsibility**: Create comprehensive test packs and execute tests
- **Entry Criteria**: Code reviewed and approved
- **Exit Criteria**: All tests executed, results documented
- **Context**: Code changes, existing tests, test strategies

### 11. **Test Reviewer Agent**
- **Responsibility**: Find issues with test pack creation and execution
- **Entry Criteria**: Tests created and executed
- **Exit Criteria**: Test quality validated or issues identified
- **Context**: Test code, coverage reports, test results

### 12. **DevOps Agent**
- **Responsibility**: Deploy to dev/feature/prod, capture screenshots, monitor
- **Entry Criteria**: All tests passed and validated
- **Exit Criteria**: Deployment successful with health checks passing
- **Context**: Infrastructure config, deployment scripts, monitoring tools

## Quality Gates

1. **Design Gate**: Architecture review, feasibility check
2. **Plan Gate**: Task breakdown validation, dependency verification
3. **Code Gate**: Syntax check, linting, security scan
4. **Review Gate**: Code quality, design adherence, best practices
5. **Test Gate**: Coverage threshold, all tests passing
6. **Test Quality Gate**: Test comprehensiveness, edge case coverage
7. **Deployment Gate**: Health checks, rollback readiness
8. **Production Gate**: Final validation, monitoring active

## Key Principles

### Separation of Context
- Each agent has its own context scope
- No agent can modify another agent's context
- Context is passed explicitly through handoffs

### Entry/Exit Criteria
- Clear, measurable criteria for each agent
- Automatic validation at each boundary
- Failure triggers appropriate escalation

### Agent Autonomy
- Agents make decisions within their domain
- Can request help but must articulate the problem
- Cannot proceed beyond exit criteria without approval

### Feedback Loops
- Iterative refinement within agent boundaries
- Maximum retry limits to prevent infinite loops
- Escalation when stuck or confidence drops

### Single-Threaded Writes
- Only one agent modifies files at a time
- Parallel analysis and context gathering
- Serial code changes to prevent conflicts

## Technology Stack

- **Language**: Python 3.11+
- **Orchestration**: LangGraph (stateful, resumable execution)
- **LLM**: Anthropic Claude (Opus 4.7 for planning, Sonnet 4.5 for execution)
- **Vector Store**: FAISS + sentence-transformers
- **Git**: GitPython for repository operations
- **CI/CD**: GitHub Actions integration
- **Testing**: pytest, coverage.py
- **Container**: Docker for isolated execution

## Installation

```bash
# Clone repository
git clone <repo-url>
cd AIagentCoding

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

```bash
# Required environment variables
ANTHROPIC_API_KEY=<your-key>
GITHUB_TOKEN=<your-token>
GITHUB_REPO=owner/repo
PROJECT_ROOT=/path/to/target/project
```

## Usage

### Start the System
```bash
python src/main.py --mode monitor
```

### Process Specific Issue
```bash
python src/main.py --issue 123
```

### Resume Failed Task
```bash
python src/main.py --resume <task-id>
```

## Project Structure

```
AIagentCoding/
├── src/
│   ├── agents/              # Individual agent implementations
│   │   ├── orchestrator.py
│   │   ├── github_scanner.py
│   │   ├── context_agent.py
│   │   ├── designer.py
│   │   ├── planner.py
│   │   ├── coder.py
│   │   ├── reviewer.py
│   │   ├── peer.py
│   │   ├── tester.py
│   │   ├── test_reviewer.py
│   │   └── devops.py
│   ├── prompts/             # Agent system prompts
│   │   ├── orchestrator_prompt.md
│   │   ├── github_scanner_prompt.md
│   │   ├── context_agent_prompt.md
│   │   ├── designer_prompt.md
│   │   ├── planner_prompt.md
│   │   ├── coder_prompt.md
│   │   ├── reviewer_prompt.md
│   │   ├── peer_prompt.md
│   │   ├── tester_prompt.md
│   │   ├── test_reviewer_prompt.md
│   │   └── devops_prompt.md
│   ├── tools/               # Shared tools for agents
│   │   ├── git_tools.py
│   │   ├── github_tools.py
│   │   ├── search_tools.py
│   │   ├── edit_tools.py
│   │   └── test_tools.py
│   ├── workflows/           # LangGraph workflow definitions
│   │   ├── sdlc_workflow.py
│   │   └── task_execution_workflow.py
│   ├── quality_gates/       # Quality validation logic
│   │   ├── design_gate.py
│   │   ├── code_gate.py
│   │   ├── test_gate.py
│   │   └── deployment_gate.py
│   ├── memory/              # Agent memory management
│   │   ├── vector_store.py
│   │   └── context_manager.py
│   └── main.py              # Entry point
├── prompts/                 # Detailed prompt templates
├── tests/                   # System tests
├── config/                  # Configuration files
├── docs/                    # Documentation
├── requirements.txt
├── .env.example
└── README.md
```

## Metrics & Monitoring

- Task completion rate
- Average time per SDLC phase
- Agent success/failure rates
- Code quality metrics
- Test coverage trends
- Deployment success rate
- Cost per task (LLM tokens)

## License

MIT License
