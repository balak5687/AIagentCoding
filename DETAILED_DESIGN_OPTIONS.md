# Multi-Agent SDLC System - Detailed Design Options

## PART 1: RESEARCH FACTS (Grounded in Reality)

### 1. How Agent Systems Actually Work (Research Findings)

#### A. Anthropic's Claude Code Agent Pattern
**FACT**: Claude Code uses a simple `Agent` tool that:
- Takes a `description` and `prompt` parameter
- Spawns a new Claude instance with the prompt
- Returns results when complete
- Runs in isolation (separate context window)

**FACT**: Claude Code's approach:
```python
# This is what Claude Code does internally (simplified)
result = Agent(
    description="Short task description",
    prompt="Detailed instructions for the agent"
)
```

**HOW IT WORKS**:
1. User calls Agent tool from within Claude Code
2. Claude Code API creates NEW Claude conversation
3. New conversation gets the `prompt` as system message
4. Agent executes independently
5. Results returned to parent conversation

**KEY INSIGHT**: No complex framework needed - just prompt + isolation

---

#### B. Aider's Diff-Based Editing
**FACT**: Success rates by editing approach:
- Diff format: 86-99% well-formed edits
- Whole file: 20-30% well-formed edits
- Unified diff: 76-95% well-formed

**FACT**: Aider's fuzzy matching algorithm:
1. Try exact string match first
2. If fail, normalize whitespace
3. If fail, use SequenceMatcher with 0.8 threshold
4. If fail, ask user or retry

**HOW IT WORKS**:
```python
# Aider's approach (factual)
def apply_edit(original, search_block, replace_block):
    # Step 1: Exact match
    if search_block in original:
        return original.replace(search_block, replace_block)
    
    # Step 2: Normalize indentation
    normalized_original = remove_leading_whitespace(original)
    normalized_search = remove_leading_whitespace(search_block)
    if normalized_search in normalized_original:
        # Apply with preserved indentation
        return smart_replace(original, search_block, replace_block)
    
    # Step 3: Fuzzy match
    ratio = SequenceMatcher(None, original, search_block).ratio()
    if ratio >= 0.8:
        return fuzzy_replace(original, search_block, replace_block)
    
    raise EditFailedException("Cannot find match")
```

---

#### C. Devin's Parallel/Serial Pattern
**FACT**: Devin's architecture:
- Each Devin instance = isolated VM
- Parallel tasks run on separate VMs
- Serial tasks run sequentially in same VM
- No shared state between parallel agents

**FACT**: Task decomposition strategy:
1. Analyze dependencies between tasks
2. Tasks with no shared files → parallel
3. Tasks with dependencies → serial
4. Create dependency graph (DAG)

**HOW IT WORKS**:
```python
# Dependency graph (factual pattern)
tasks = [
    Task(id=1, depends_on=[], files=["api.py"]),
    Task(id=2, depends_on=[], files=["frontend.js"]),  # Can run parallel with task 1
    Task(id=3, depends_on=[1], files=["api.py"]),      # Must wait for task 1
]

# Build graph
graph = build_dependency_graph(tasks)

# Identify parallel groups
parallel_groups = topological_sort(graph)
# Result: [[Task1, Task2], [Task3]]
```

---

#### D. MetaGPT's Role Specialization
**FACT**: MetaGPT uses SOP (Standard Operating Procedures):
- Each role has defined responsibilities
- Roles communicate via "environment" message bus
- Output of one role = input to next role
- Assembly-line pattern: PM → Architect → Engineer → QA

**FACT**: Role definition structure:
```python
# MetaGPT's actual pattern (simplified)
class Role:
    def __init__(self, profile, goal, constraints):
        self.profile = profile  # e.g., "Software Engineer"
        self.goal = goal        # e.g., "Write clean, tested code"
        self.constraints = constraints  # e.g., ["Follow PEP8", "Write unit tests"]
        self.memory = []
        self.watch = []  # Which actions trigger this role
    
    def observe(self, env):
        # Filter messages this role cares about
        return [msg for msg in env.messages if msg.action in self.watch]
    
    def react(self, observations):
        # Process and generate output
        pass
```

---

#### E. AutoGen's Manager Coordination
**FACT**: AutoGen patterns:
1. **Manager-Worker**: Manager delegates to specialist agents
2. **Group Chat**: All agents in shared conversation
3. **Two-Agent**: Simple back-and-forth

**FACT**: Tool-based delegation:
```python
# AutoGen's actual approach
manager = AssistantAgent("manager")
math_expert = AssistantAgent("math_expert")
code_expert = AssistantAgent("code_expert")

# Wrap specialists as tools
manager.register_tools([
    Tool(name="solve_math", agent=math_expert),
    Tool(name="write_code", agent=code_expert)
])

# Manager routes based on task
result = manager.chat("Calculate fibonacci and implement it")
# Manager decides which tool/agent to use
```

---

## PART 2: IMPLEMENTATION OPTIONS

### Option A: Pure Markdown Agents + Simple Orchestrator

**How Agents Are Invoked**:
```python
# orchestrator.py
import anthropic

client = anthropic.Anthropic(api_key="YOUR_KEY")

def invoke_agent(agent_md_file, context):
    # Load agent definition
    with open(f"agents/{agent_md_file}", "r") as f:
        agent_prompt = f.read()
    
    # Call Claude API directly
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=agent_prompt,  # Agent definition as system prompt
        messages=[{
            "role": "user",
            "content": context  # Task context
        }]
    )
    
    return response.content[0].text

# Usage
designer_output = invoke_agent("designer.md", github_issue)
planner_output = invoke_agent("planner.md", designer_output)
```

**Agent File Structure** (agents/designer.md):
```markdown
# Designer Agent

You are a software designer analyzing requirements.

## Entry Criteria
- GitHub issue provided with clear requirements
- Repository context available

## Exit Criteria
- Design document created with:
  - Architecture overview
  - Component breakdown
  - Implementation approach
  - Estimated complexity

## Instructions
Analyze the GitHub issue and create a detailed design...

## Output Format
Return JSON:
{
  "architecture": "...",
  "components": [...],
  "approach": "...",
  "complexity": "low|medium|high",
  "confidence": 0-100
}
```

**Pros**:
- ✅ Simple, transparent
- ✅ Easy to modify prompts
- ✅ Direct API control
- ✅ Requires Anthropic API key

**Cons**:
- ❌ Need API key (costs money)
- ❌ Manual orchestration logic
- ❌ No built-in parallel execution

---

### Option B: Hybrid with Claude Code Integration

**How Agents Are Invoked**:
```python
# Use Claude Code's capabilities from within
# This runs INSIDE Claude Code session

def invoke_agent_via_claude_code(agent_md, context):
    """
    This would be a Python script that Claude Code executes
    which then uses subprocess to call Claude Code CLI
    """
    import subprocess
    import json
    
    # Write agent prompt to temp file
    with open("/tmp/agent_prompt.txt", "w") as f:
        f.write(open(f"agents/{agent_md}").read())
        f.write("\n\n" + context)
    
    # Invoke Claude Code in non-interactive mode
    result = subprocess.run([
        "claude",
        "--non-interactive",
        "--input", "/tmp/agent_prompt.txt"
    ], capture_output=True, text=True)
    
    return result.stdout

# Usage in orchestrator
result = invoke_agent_via_claude_code("designer.md", github_issue)
```

**Pros**:
- ✅ Uses existing Claude Code installation
- ✅ No API key needed (uses your Claude Code license)
- ✅ Same interface as Option A

**Cons**:
- ❌ Depends on Claude Code CLI being available
- ❌ Subprocess overhead
- ❌ Not officially documented pattern

---

### Option C: Python Classes with MD Prompts (True Hybrid)

**How Agents Are Invoked**:
```python
# Base agent runner
class AgentRunner:
    def __init__(self, api_key=None):
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            # Use Claude Code Agent tool if available
            self.use_claude_code = True
    
    def run(self, agent_name, context):
        # Load MD prompt
        prompt = self.load_prompt(f"agents/{agent_name}.md")
        
        # Parse entry criteria from MD
        if not self.check_entry_criteria(prompt, context):
            raise ValueError(f"{agent_name}: Entry criteria not met")
        
        # Invoke agent
        if self.use_claude_code:
            output = self.invoke_via_claude_code(prompt, context)
        else:
            output = self.invoke_via_api(prompt, context)
        
        # Validate exit criteria
        if not self.check_exit_criteria(prompt, output):
            raise ValueError(f"{agent_name}: Exit criteria not met")
        
        return output
    
    def invoke_via_api(self, prompt, context):
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            system=prompt.instructions,
            messages=[{"role": "user", "content": context}]
        )
        return response.content[0].text
    
    def invoke_via_claude_code(self, prompt, context):
        # Call Agent tool (if running inside Claude Code)
        # This is pseudocode - actual implementation would use
        # the Agent tool that Claude Code provides
        result = Agent(
            description=f"Run {prompt.agent_name}",
            prompt=prompt.instructions + "\n\n" + context
        )
        return result

# Orchestrator
runner = AgentRunner()

# Sequential execution
designer_out = runner.run("designer", github_issue)
planner_out = runner.run("planner", designer_out)

# Parallel execution (Devin pattern)
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for task in tasks:
        if task.can_run_parallel:
            future = executor.submit(runner.run, "coder", task.context)
            futures.append(future)
    
    results = [f.result() for f in futures]
```

**Pros**:
- ✅ Best of both: MD prompts + Python validation
- ✅ Supports both API and Claude Code modes
- ✅ Built-in parallel execution
- ✅ Entry/exit criteria enforced in code

**Cons**:
- ❌ More complex than pure MD
- ❌ Still need API key OR Claude Code

---

### Option D: LangGraph Workflow with MD Agents

**How Agents Are Invoked**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class SDLCState(TypedDict):
    github_issue: str
    design: dict
    plan: dict
    tasks: list
    code_changes: list

def designer_node(state: SDLCState):
    runner = AgentRunner()
    design = runner.run("designer", state["github_issue"])
    return {"design": json.loads(design)}

def planner_node(state: SDLCState):
    runner = AgentRunner()
    plan = runner.run("planner", json.dumps(state["design"]))
    return {"plan": json.loads(plan)}

def coder_node(state: SDLCState):
    runner = AgentRunner()
    results = []
    for task in state["tasks"]:
        code = runner.run("coder", json.dumps(task))
        results.append(code)
    return {"code_changes": results}

# Build workflow
workflow = StateGraph(SDLCState)
workflow.add_node("designer", designer_node)
workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)

workflow.add_edge("designer", "planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", END)

workflow.set_entry_point("designer")

app = workflow.compile()

# Execute
result = app.invoke({
    "github_issue": issue_text
})
```

**Pros**:
- ✅ Stateful, resumable workflows
- ✅ Visual graph representation
- ✅ Built-in checkpointing
- ✅ Agents still defined in MD

**Cons**:
- ❌ Adds LangGraph dependency
- ❌ Learning curve for LangGraph
- ❌ More moving parts

---

## PART 3: DETAILED DESIGN (RECOMMENDED APPROACH)

### Chosen: Option C (Python Classes + MD Prompts)

**Why**: Best balance of simplicity, flexibility, and power

### Architecture

```
AIagentCoding/
├── agents/                     # Agent definitions (MD)
│   ├── github_scanner.md
│   ├── context_agent.md
│   ├── designer.md
│   ├── planner.md
│   ├── approval.md
│   ├── coder.md
│   ├── peer.md
│   ├── reviewer.md
│   ├── tester.md
│   ├── test_reviewer.md
│   └── devops.md
│
├── src/
│   ├── agent_runner.py         # Core agent execution
│   ├── orchestrator.py         # Workflow management
│   ├── criteria_validator.py  # Entry/exit validation
│   ├── diff_editor.py          # Aider-style editing
│   ├── github_client.py        # GitHub API
│   └── parallel_executor.py    # Devin-style parallel
│
├── config.yaml                 # Configuration
├── orchestrator_main.py        # Entry point
└── README.md
```

### Agent Invocation Flow

```
orchestrator_main.py
    ↓
1. Load config (GitHub repo, API key/Claude Code mode)
    ↓
2. GitHubScanner agent → scans for issues
    ↓
3. ContextAgent → retrieves relevant code
    ↓
4. Designer agent → analyzes requirements
    ↓
5. Planner agent → creates task breakdown
    ↓
6. Approval agent → posts to GitHub, waits
    ↓
7. FOR EACH TASK (parallel if independent):
    ├─ Coder agent → implements code
    ├─ Peer agent → assists if stuck
    └─ Reviewer agent → reviews code
    ↓
8. Tester agent → creates tests
    ↓
9. TestReviewer agent → validates tests
    ↓
10. DevOps agent → deploys & screenshots
    ↓
11. Create PR, notify GitHub
```

### Key Implementation Details

#### 1. Agent Definition Format (MD)
```markdown
---
name: coder
model: claude-sonnet-4-5-20250929
max_tokens: 8192
temperature: 0.7
---

# Coder Agent

## Role
Implement code changes using diff-based editing (Aider pattern).

## Entry Criteria
```yaml
task_specification: required
relevant_files: required
design_document: required
blocking_dependencies: none
```

## Exit Criteria
```yaml
code_complete: true
syntax_valid: true
linting_passed: true
confidence: ">= 70"
```

## Context Scope
**You receive**:
- Task specification (what to build)
- Relevant file contents (from ContextAgent)
- Design document excerpt
- Coding standards

**You do NOT receive**:
- Other tasks (isolated)
- Test results (until you finish)
- Reviewer feedback (until you submit)

## Instructions

You are an expert software engineer implementing code changes.

### Editing Approach (Aider Pattern)
Use SEARCH/REPLACE blocks for surgical edits:

```
<<<<<<< SEARCH
def old_function():
    return "old"
=======
def new_function():
    return "new"
>>>>>>> REPLACE
```

### Guidelines
1. Make minimal changes (diff-based)
2. Preserve existing code style
3. Add comments for non-obvious logic
4. Self-review before submitting

### When Stuck
If you encounter:
- Unclear requirements → Request clarification
- Technical blocker → Request peer agent
- Repeated failures (3x) → Escalate to designer

## Output Format
```json
{
  "status": "complete|need_help|blocked",
  "changes": [
    {
      "file": "path/to/file.py",
      "search": "code to find",
      "replace": "new code"
    }
  ],
  "confidence": 85,
  "notes": "Implementation notes",
  "request_peer": false
}
```
```

#### 2. Agent Runner Implementation
```python
# src/agent_runner.py
import anthropic
import yaml
import json
from pathlib import Path

class AgentRunner:
    def __init__(self, mode="api", api_key=None):
        self.mode = mode  # "api" or "claude-code"
        if mode == "api":
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def run(self, agent_name, context, max_retries=3):
        """Run an agent with retry logic"""
        agent_def = self.load_agent(agent_name)
        
        for attempt in range(max_retries):
            try:
                # Validate entry criteria
                self.validate_entry(agent_def, context)
                
                # Invoke agent
                output = self.invoke(agent_def, context)
                
                # Validate exit criteria
                self.validate_exit(agent_def, output)
                
                return output
            except ExitCriteriaFailed as e:
                if attempt < max_retries - 1:
                    context = self.add_feedback(context, e.message)
                    continue
                raise
        
        raise MaxRetriesExceeded(f"{agent_name} failed after {max_retries} attempts")
    
    def load_agent(self, agent_name):
        """Load agent definition from MD file"""
        path = Path(f"agents/{agent_name}.md")
        content = path.read_text()
        
        # Parse frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            metadata = yaml.safe_load(parts[1])
            instructions = parts[2]
        else:
            metadata = {}
            instructions = content
        
        return {
            "name": agent_name,
            "metadata": metadata,
            "instructions": instructions,
            "entry_criteria": self.parse_criteria(instructions, "Entry Criteria"),
            "exit_criteria": self.parse_criteria(instructions, "Exit Criteria")
        }
    
    def invoke(self, agent_def, context):
        """Invoke agent based on mode"""
        if self.mode == "api":
            return self.invoke_api(agent_def, context)
        elif self.mode == "claude-code":
            return self.invoke_claude_code(agent_def, context)
    
    def invoke_api(self, agent_def, context):
        """Invoke via Anthropic API"""
        response = self.client.messages.create(
            model=agent_def["metadata"].get("model", "claude-sonnet-4-5-20250929"),
            max_tokens=agent_def["metadata"].get("max_tokens", 4096),
            temperature=agent_def["metadata"].get("temperature", 0.7),
            system=agent_def["instructions"],
            messages=[{
                "role": "user",
                "content": json.dumps(context) if isinstance(context, dict) else context
            }]
        )
        return response.content[0].text
    
    def invoke_claude_code(self, agent_def, context):
        """Invoke via Claude Code subprocess"""
        # Write prompt to temp file
        import tempfile, subprocess
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(agent_def["instructions"])
            f.write("\n\n## Task Context\n")
            f.write(json.dumps(context, indent=2) if isinstance(context, dict) else context)
            prompt_file = f.name
        
        # Call Claude Code CLI
        result = subprocess.run(
            ["claude", "--non-interactive", prompt_file],
            capture_output=True,
            text=True
        )
        
        return result.stdout
```

#### 3. Orchestrator Implementation
```python
# src/orchestrator.py
from agent_runner import AgentRunner
from parallel_executor import ParallelExecutor
import json

class SDLCOrchestrator:
    def __init__(self, config):
        self.runner = AgentRunner(
            mode=config.get("mode", "api"),
            api_key=config.get("api_key")
        )
        self.parallel = ParallelExecutor(self.runner)
    
    def process_github_issue(self, issue_url):
        """Main workflow"""
        
        # Phase 1: Scanning & Context
        issue_data = self.runner.run("github_scanner", {"url": issue_url})
        context = self.runner.run("context_agent", issue_data)
        
        # Phase 2: Design
        design = self.runner.run("designer", {
            "issue": issue_data,
            "context": context
        })
        
        # Phase 3: Planning
        plan = self.runner.run("planner", {
            "design": design,
            "context": context
        })
        
        # Phase 4: Approval
        approval = self.runner.run("approval", {
            "plan": plan,
            "github_issue": issue_url
        })
        
        if not approval["approved"]:
            return {"status": "rejected", "reason": approval["reason"]}
        
        # Phase 5: Task Execution (parallel/serial)
        tasks = json.loads(plan)["tasks"]
        task_results = self.execute_tasks(tasks)
        
        # Phase 6: Testing
        test_results = self.runner.run("tester", {
            "code_changes": task_results
        })
        
        test_validation = self.runner.run("test_reviewer", test_results)
        
        # Phase 7: Deployment
        deployment = self.runner.run("devops", {
            "code_changes": task_results,
            "test_results": test_validation
        })
        
        return {
            "status": "success",
            "pr_url": deployment["pr_url"],
            "deployment_url": deployment["feature_url"]
        }
    
    def execute_tasks(self, tasks):
        """Execute tasks with parallel/serial logic (Devin pattern)"""
        
        # Build dependency graph
        dep_graph = self.build_dependency_graph(tasks)
        
        # Get execution order
        execution_order = self.topological_sort(dep_graph)
        
        all_results = []
        
        for task_group in execution_order:
            if len(task_group) == 1:
                # Serial execution
                result = self.execute_single_task(task_group[0])
                all_results.append(result)
            else:
                # Parallel execution
                results = self.parallel.execute_parallel([
                    (task, self.execute_single_task)
                    for task in task_group
                ])
                all_results.extend(results)
        
        return all_results
    
    def execute_single_task(self, task):
        """Execute single task with coder → peer → reviewer"""
        
        # Coder attempts
        coder_output = self.runner.run("coder", task)
        
        # Check if peer needed
        if json.loads(coder_output).get("request_peer"):
            peer_output = self.runner.run("peer", {
                "task": task,
                "coder_attempts": coder_output
            })
            coder_output = peer_output
        
        # Reviewer validates
        review = self.runner.run("reviewer", {
            "task": task,
            "code": coder_output
        })
        
        if review["status"] != "approved":
            # Retry with feedback
            coder_output = self.runner.run("coder", {
                **task,
                "review_feedback": review["feedback"]
            })
        
        return coder_output
```

---

## PART 4: INTEGRATION OF BEST PRACTICES

### How Each Pattern Is Applied:

1. **Anthropic's Simple Prompts**
   - Agents = MD files with clear instructions
   - XML-style sections (## Role, ## Entry Criteria)
   - Minimal scaffolding in Python

2. **MetaGPT's Role Specialization**
   - Each agent has specific role definition
   - Entry/exit criteria enforce boundaries
   - Assembly-line handoffs (Designer → Planner → Coder)

3. **Aider's Diff-Based Editing**
   - Coder agent uses SEARCH/REPLACE blocks
   - DiffEditor class with fuzzy matching
   - Minimal, surgical code changes

4. **Devin's Parallel/Serial Pattern**
   - Dependency graph analysis
   - ParallelExecutor for independent tasks
   - Isolated execution per task

5. **AutoGen's Manager Coordination**
   - Orchestrator = manager
   - Agents = specialist workers
   - Dynamic routing based on task needs

---

## PART 5: NEXT STEPS

### Implementation Tasks:

1. **Create agent MD files** (12 agents)
2. **Implement AgentRunner** (core execution)
3. **Implement CriteriaValidator** (entry/exit checks)
4. **Implement DiffEditor** (Aider-style)
5. **Implement ParallelExecutor** (Devin-style)
6. **Implement Orchestrator** (workflow)
7. **Create config system**
8. **Test with sample GitHub issue**
9. **Add monitoring/logging**
10. **Documentation**

---

## QUESTIONS FOR YOU:

1. **Which mode do you want to start with?**
   - Option A: Pure API (need Anthropic API key)
   - Option B: Claude Code integration (use your license)
   - Option C: Both (switchable)

2. **Do you have an Anthropic API key?**
   - If yes → can use API mode immediately
   - If no → need to use Claude Code mode or get key

3. **Start with MVP or full system?**
   - MVP: Just Designer → Planner → Approval (3 agents)
   - Full: All 12 agents with complete workflow

4. **Prototype target?**
   - Real GitHub issue from your projects?
   - Synthetic test issue?

Let me know and I'll create the implementation tasks!
