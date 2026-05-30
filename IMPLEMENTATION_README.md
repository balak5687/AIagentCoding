# Multi-Agent SDLC System - Implementation

A production-ready Multi-Agent SDLC system that automates software development from requirements through deployment.

## Architecture

Combines best practices from 6 leading frameworks:
- **Anthropic**: Markdown + YAML structured prompts
- **MetaGPT**: Role-based agents with clear SOPs
- **Aider**: Diff-based editing with fuzzy matching
- **Devin**: Dependency-aware parallel/serial orchestration
- **AutoGen**: Conversation loops for agent collaboration
- **Google**: Deterministic playbooks to reduce LLM hallucination

## Project Structure

```
AIagentCoding/
├── agents/                    # Agent definitions (Markdown files)
│   ├── designer.md           # Software architect
│   ├── planner.md            # Task breakdown & dependencies
│   ├── coder.md              # Implementation (with playbook support)
│   ├── peer.md               # Peer support
│   └── reviewer.md           # Code review
├── playbooks/                 # Deterministic code generation (Google's approach)
│   ├── add_crud_endpoint.yaml
│   ├── add_unit_tests.yaml
│   └── add_error_handling.yaml
├── src/
│   ├── core/
│   │   ├── config.py         # Configuration management
│   │   ├── agent_runner.py   # Execute agents via Claude Code CLI
│   │   ├── protocol.py       # Parse Markdown + YAML messages
│   │   └── orchestrator.py   # Main workflow coordination
│   ├── workflows/
│   │   ├── sequential.py     # Blocking execution
│   │   ├── parallel.py       # Parallel tasks with DAG
│   │   └── conversation.py   # Coder ↔ Peer ↔ Reviewer loops
│   ├── tools/
│   │   ├── diff_editor.py    # Aider-style fuzzy matching
│   │   └── playbook_loader.py # Google's deterministic approach
│   └── main.py               # CLI entry point
├── config/
│   └── config.yaml.example   # Configuration template
├── tests/
│   └── test_protocol.py      # Protocol tests
└── requirements.txt          # Python dependencies
```

## Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

```bash
cp config/config.yaml.example config.yaml
cp .env.example .env
```

Edit `config.yaml`:
```yaml
mode: claude-code          # or "api" for direct API calls
github_token: ${GITHUB_TOKEN}
github_repo: "owner/repo"
project_root: "/path/to/target/project"
```

Edit `.env`:
```bash
GITHUB_TOKEN=your_github_token
ANTHROPIC_API_KEY=your_api_key  # Only if mode=api
```

## Usage

### Run the System

```bash
python -m src.main --issue "https://github.com/owner/repo/issues/123"
```

### Debug Mode

```bash
python -m src.main --issue "Issue description" --debug
```

### Specify Custom Config

```bash
python -m src.main --issue "Issue description" --config my-config.yaml
```

## How It Works

### Phase 1: Analysis (Sequential)

```
GitHub Issue → Designer → Planner → Approval
```

1. **Designer**: Analyzes requirements, creates architecture
2. **Planner**: Breaks down into tasks with dependencies
3. **Approval**: (Future) Human review gate

### Phase 2: Implementation (Parallel + Conversation)

```
Task 1: Coder ↔ Peer ↔ Reviewer
Task 2: Coder ↔ Peer ↔ Reviewer  (runs in parallel)
Task 3: Coder ↔ Peer ↔ Reviewer
```

Each task runs a conversation loop:
1. **Coder** implements changes using SEARCH/REPLACE blocks
2. **Peer** provides guidance if coder is stuck (optional)
3. **Reviewer** validates code quality, security, correctness
4. Loop repeats until approved or max iterations

### Phase 3: Testing & Deployment (Sequential)

```
All Tasks → Tester → TestReviewer → DevOps → Done
```

(Future implementation)

## Playbook System (Google's Approach)

**Problem**: LLMs can hallucinate when using pure cognitive reasoning for common tasks.

**Solution**: Use **deterministic playbooks** for standard patterns (CRUD, testing, error handling).

### Cognitive vs Deterministic

| Approach | When to Use | Hallucination Risk |
|----------|-------------|-------------------|
| **Cognitive** | Novel algorithms, complex logic | Higher (15-20%) |
| **Deterministic** | CRUD, tests, boilerplate | Lower (2-5%) |

### How It Works

1. **Planner** detects task matches playbook pattern
2. **Orchestrator** loads playbook and enriches task
3. **Coder** follows step-by-step instructions
4. **Result**: Consistent, complete, validated code

### Available Playbooks

- `add_crud_endpoint.yaml` - REST API CRUD operations
- `add_unit_tests.yaml` - Unit test generation
- `add_error_handling.yaml` - Try/catch error handling
- `add_database_model.yaml` - Database models
- `refactor_extract_function.yaml` - Extract function
- `add_logging.yaml` - Logging statements
- `add_input_validation.yaml` - Input validation
- `fix_security_issue.yaml` - Security fixes

**See** `PLAYBOOK_SYSTEM.md` for detailed documentation.

## Agent Communication Protocol

Agents communicate via **Markdown + YAML frontmatter** (not JSON).

### Agent Output Format

```markdown
---
agent: coder
status: complete
confidence: 85
request_peer: false
---

# Implementation Report

## Task
Implement user authentication

## Changes

### File: src/auth.py

<<<<<<< SEARCH
def login(username, password):
    pass
=======
def login(username, password):
    user = db.find_user(username)
    if user and verify_password(password, user.password_hash):
        return create_session(user)
    return None
>>>>>>> REPLACE

## Implementation Notes

Used bcrypt for password hashing. Session tokens stored in Redis.

## Confidence: 85%

High confidence, standard implementation.
```

## Agent Invocation

Agents are invoked via **subprocess to Claude Code CLI**:

```python
# Write prompt to temp file
with open(temp_file, 'w') as f:
    f.write(agent_definition + context)

# Execute
result = subprocess.run(
    ["claude", "--non-interactive", temp_file],
    capture_output=True
)

# Parse output
message = AgentMessage(result.stdout)
```

## Orchestration Patterns

### Sequential (Blocking)

Used when agents need complete output from previous agent:
```python
designer_result = runner.run("designer", context)
planner_result = runner.run("planner", designer_result)
```

### Parallel (Async)

Used for independent tasks with dependency graph:
```python
# Build dependency graph with NetworkX
graph = build_dependency_graph(tasks)

# Execute in topological order
for group in topological_generations(graph):
    await asyncio.gather(*[execute_task(t) for t in group])
```

### Conversation Loop

Used for collaborative work (coder ↔ peer ↔ reviewer):
```python
for iteration in range(max_iterations):
    coder_output = runner.run("coder", context)
    
    if coder_output.request_peer:
        peer_output = runner.run("peer", coder_output)
        continue
    
    reviewer_output = runner.run("reviewer", coder_output)
    
    if reviewer_output.status == "approved":
        break
```

## Testing

### Run Protocol Tests

```bash
python tests/test_protocol.py
```

Expected output:
```
✓ test_parse_simple_message passed
✓ test_extract_code_changes passed

All tests passed!
```

## Current Implementation Status

### ✅ Completed

- [x] Project structure
- [x] Configuration system
- [x] Agent communication protocol (Markdown + YAML)
- [x] Agent runner (subprocess to Claude Code CLI)
- [x] Core agent definitions (Designer, Planner, Coder, Peer, Reviewer)
- [x] Sequential orchestrator
- [x] Parallel executor with dependency graph
- [x] Conversation loop (Coder ↔ Peer ↔ Reviewer)
- [x] Main orchestrator
- [x] Diff editor with fuzzy matching
- [x] CLI entry point
- [x] Basic tests

### 🚧 TODO

- [ ] GitHub scanner agent
- [ ] Context agent (codebase analysis)
- [ ] Approval agent (human review)
- [ ] Tester agent
- [ ] TestReviewer agent
- [ ] DevOps agent
- [ ] Integration with actual GitHub API
- [ ] File change application (use DiffEditor)
- [ ] End-to-end testing
- [ ] Tmux debug mode
- [ ] Error recovery and retry logic enhancement

## Configuration Options

### Execution Mode

**claude-code** (default): Invokes agents via Claude Code CLI subprocess
```yaml
mode: claude-code
```

**api**: Direct API calls to Anthropic
```yaml
mode: api
anthropic_api_key: ${ANTHROPIC_API_KEY}
```

### Agent Settings

```yaml
max_retries: 3           # Retry failed agents
timeout_seconds: 600     # 10 minutes per agent
```

### Debug Mode

```yaml
debug: true              # Preserve temp files, verbose logging
use_tmux: false          # (Future) Watch agents in tmux panes
```

## Best Practices

### Agent Design

1. **Clear responsibilities**: Each agent has a specific role
2. **Entry/exit criteria**: Defined in agent MD files
3. **Structured output**: YAML frontmatter + Markdown sections
4. **Retry feedback**: Context includes previous attempt info

### Code Changes

1. **SEARCH/REPLACE blocks**: Never whole-file rewrites
2. **Exact matching**: Include enough context
3. **Fuzzy fallback**: 80% similarity threshold
4. **One change at a time**: Multiple blocks per file OK

### Orchestration

1. **Blocking for complete output**: Design, planning phases
2. **Parallel for independence**: Multiple features/bugs
3. **Conversation for quality**: Coder-reviewer loops
4. **Sync points**: Wait before testing/deployment

## Troubleshooting

### "Agent definition not found"

Ensure agent MD files exist in `agents/` directory.

### "Claude Code failed"

Check that `claude` CLI is installed and in PATH:
```bash
which claude
```

### "No tasks extracted from plan"

Planner output must include "Task Breakdown" section with proper format:
```markdown
### Task 1: Name
- **ID**: task_1
- **Dependencies**: []
```

### Import errors

Activate virtual environment:
```bash
source venv/bin/activate
```

## Contributing

When adding new agents:

1. Create agent MD file in `agents/`
2. Define role, responsibilities, output format
3. Use YAML frontmatter + Markdown sections
4. Add to orchestrator workflow if needed

## License

MIT

## References

- [Anthropic Claude](https://www.anthropic.com/claude)
- [MetaGPT](https://github.com/geekan/MetaGPT)
- [Aider](https://github.com/paul-gauthier/aider)
- [Devin AI](https://www.cognition-labs.com/introducing-devin)
- [AutoGen](https://github.com/microsoft/autogen)
