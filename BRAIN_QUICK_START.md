# Project Brain - Quick Start Guide

**Status**: ✅ Fully Operational  
**Version**: 1.0

---

## What Is Project Brain?

A two-brain knowledge system that gives AI agents runtime access to:
1. **Coding Brain** (BM25): Fast keyword search over 2,313 codebase files
2. **Functionality Brain** (Semantic): Concept search over requirements, design, specs

---

## Quick Commands

```bash
# Check status
python -m src.brain status

# Query knowledge
python -m src.brain query "dashboard requirements"

# Query code
python -m src.brain query "purchase order function" --type code

# Query as specific agent
python -m src.brain query "authentication" --agent coder
```

---

## For Agent Developers

### 1. Import the Interface

```python
from src.brain.query_interface import BrainQueryInterface

# Initialize for your agent
interface = BrainQueryInterface.for_agent(
    manifest_path=".project-brain/manifest.yaml",
    agent_name="designer"  # or coder, planner, reviewer
)
```

### 2. Search Code (BM25 - Fast)

```python
# Find functions, classes, files
results = interface.search_code("purchase_order create", top_k=5)

for result in results:
    print(f"File: {result['file']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}")
```

### 3. Search Knowledge (Semantic)

```python
# Find requirements, design, domain knowledge
results = interface.search_knowledge("dashboard requirements", top_k=5)

for result in results:
    print(f"File: {result['metadata']['file']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Content: {result['content']}")
```

### 4. Format for Prompt Injection

```python
# Get context to inject into your agent prompt
context = interface.format_context_for_prompt(
    code_query="dashboard controller",
    knowledge_query="dashboard requirements",
    top_k=3
)

# Now inject into your prompt
prompt = f"""
<context>
{context}
</context>

Your task: Design the dashboard module architecture.
"""
```

---

## Agent Access Levels

| Agent | Coding Brain | Functionality Brain |
|-------|-------------|-------------------|
| **Designer** | ✅ Yes | ✅ Yes |
| **Context Agent** | ✅ Yes | ❌ No |
| **Planner** | ❌ No | ✅ Yes |
| **Coder** | ✅ Yes | ❌ No |
| **Reviewer** | ✅ Yes | ❌ No |

---

## What's Indexed

### Coding Brain (BM25)
- **2,313 files** (2,218 Python + 95 Dart)
- **908,707 lines** of code
- Backend: GreasyNuts Python/FastAPI
- Frontend: Flutter/Dart
- Query time: <100ms

### Functionality Brain (Semantic)
- **76 semantic chunks**
- GitHub Issue #3 (Dashboard Module Rev2)
- Product overview (from README)
- Requirements, design placeholders
- Query time: ~1-2s

---

## Example Queries

### Good Code Queries (BM25)
- ✅ "purchase order create function"
- ✅ "authentication login"
- ✅ "dashboard controller"
- ✅ "invoice generate"

### Good Knowledge Queries (Semantic)
- ✅ "What are the dashboard requirements?"
- ✅ "How does real-time sync work?"
- ✅ "What features does the garage system have?"
- ✅ "Mobile responsiveness requirements"

---

## Directory Structure

```
.project-brain/
├── manifest.yaml              ← Configuration
├── sources/                   ← Version controlled
│   ├── coding-brain/
│   │   └── structure.md       ← Generated summary
│   └── functionality-brain/
│       ├── product.md
│       └── specs/issue-3/
│           └── requirements.md
└── knowledge-bases/           ← Generated (gitignored)
    ├── coding-brain/
    │   └── bm25_data.json
    └── functionality-brain/
        └── data.json          ← Embeddings
```

---

## Troubleshooting

### Brain not found?
```bash
# Check if brain exists
python -m src.brain status

# If not, it was already initialized earlier
ls -la .project-brain/
```

### Slow semantic queries?
- First query loads the model (~1-2s)
- Subsequent queries are faster
- Model: all-minilm-l6-v2 (384 dims)

### No results found?
- Try broader keywords
- BM25 needs exact keyword matches
- Semantic search needs conceptual similarity

---

## Integration Points

### Where to add brain queries in your agent:

```python
# In src/core/agent_runner.py or agent code:

from src.brain.query_interface import BrainQueryInterface

def run_agent(agent_name, task):
    # 1. Initialize brain interface
    brain = BrainQueryInterface.for_agent(
        ".project-brain/manifest.yaml",
        agent_name
    )

    # 2. Get relevant context
    code_context = brain.search_code(task["keywords"])
    knowledge_context = brain.search_knowledge(task["description"])

    # 3. Format for prompt
    context_str = brain.format_context_for_prompt(
        code_query=task["keywords"],
        knowledge_query=task["description"]
    )

    # 4. Inject into agent prompt
    prompt = build_agent_prompt(agent_name, task, context_str)

    # 5. Run agent with context
    result = execute_agent(prompt)

    return result
```

---

## Performance Tips

1. **Cache queries** if asking same question multiple times
2. **Use top_k wisely** - more results = more prompt tokens
3. **Code queries first** - BM25 is faster than semantic
4. **Batch related queries** - load model once for multiple semantic queries

---

## Files to Read

- `src/brain/query_interface.py` - Full API documentation
- `src/brain/base.py` - ProjectBrain class
- `PROJECT_BRAIN_COMPLETE.md` - Complete implementation details
- `.project-brain/manifest.yaml` - Current configuration

---

## Support

- Check status: `python -m src.brain status`
- View manifest: `cat .project-brain/manifest.yaml`
- Test queries: `python -m src.brain query "your query"`

---

**Ready to use!** Just import `BrainQueryInterface` and start querying.
