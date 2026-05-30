# Kiro CLI Knowledge Base - Internal Structure

**Source**: Direct observation from working with Kiro CLI  
**Date**: 2026-05-24

---

## Filesystem Structure

```
~/.kiro/knowledge-bases/
├── q_cli_default/                    ← default agent KB
│   ├── contexts.json                 ← manifest of all KBs for this agent
│   └── context-id-1/                 ← specific KB instance
│       ├── data.json                 ← embeddings/chunks (semantic index)
│       └── bm25_data.json            ← BM25 tokens (keyword index)
│
└── my-agent-abc123/                  ← custom agent KB
    ├── contexts.json
    └── context-id-2/
        └── data.json
```

---

## Two Index Types

### 1. `indexType: "best"` — Semantic Search
**Model**: `all-minilm-l6-v2` (sentence transformers)  
**Best for**: 
- Documents / research papers
- Natural language queries
- Conceptual searches
- NLP tasks

**Storage**: `data.json` contains:
- File chunks
- Embedding vectors (384 dimensions for all-minilm-l6-v2)
- Metadata (file path, chunk index, timestamp)

**Query method**: Cosine similarity against stored chunks

---

### 2. `indexType: "fast"` — BM25 Keyword Search
**Algorithm**: BM25 (Best Match 25) text ranking  
**Best for**:
- Logs
- Config files
- Large codebases
- Exact lookups
- Keyword matching

**Storage**: `bm25_data.json` contains:
- Tokenized text
- Term frequencies
- Inverse document frequencies
- Document lengths

**Query method**: BM25 scoring for keyword relevance

---

## Indexing Process

1. **Chunking**: Files split into logical chunks (paragraph, function, class)
2. **Vectorization**:
   - **Semantic**: Each chunk → embedding vector (all-minilm-l6-v2)
   - **BM25**: Each chunk → tokenized + TF-IDF stats
3. **Storage**: Chunks written to JSON per knowledge base
4. **Limits**: Max 10,000 files per knowledge base

---

## Key Properties

| Property | Details |
|----------|---------|
| **Isolation** | Each agent has isolated KBs (can't access other agents) |
| **Persistence** | Stored on disk, persists across sessions |
| **Supported Formats** | Code, Markdown, CSV, Text |
| **Background Indexing** | Large directories indexed asynchronously |
| **Auto-sync** | Watches agent `resources` for changes if `autoUpdate: true` |

---

## Agent Configuration

In `.kiro/agents/<agent-name>.json`:

```json
{
  "resources": [
    {
      "type": "knowledgeBase",
      "source": "file://./docs",
      "name": "ProjectDocs",
      "indexType": "best",        ← or "fast"
      "autoUpdate": true
    }
  ]
}
```

---

## contexts.json Structure (inferred)

```json
{
  "contexts": [
    {
      "id": "context-id-1",
      "name": "ProjectDocs",
      "source": "/path/to/docs",
      "indexType": "best",
      "createdAt": "2026-05-24T10:00:00Z",
      "lastIndexed": "2026-05-24T10:05:00Z",
      "fileCount": 142,
      "chunkCount": 1523
    }
  ]
}
```

---

## data.json Structure (inferred)

### For Semantic Index (`indexType: "best"`):
```json
{
  "chunks": [
    {
      "id": "chunk-001",
      "file": "docs/architecture.md",
      "content": "The system uses a microservices architecture...",
      "embedding": [0.123, -0.456, 0.789, ...],  // 384 dimensions
      "metadata": {
        "chunkIndex": 0,
        "startLine": 1,
        "endLine": 15
      }
    }
  ],
  "indexMetadata": {
    "model": "all-minilm-l6-v2",
    "dimension": 384,
    "totalChunks": 1523
  }
}
```

### For BM25 Index (`indexType: "fast"`):
```json
{
  "documents": [
    {
      "id": "doc-001",
      "file": "src/main.py",
      "tokens": ["def", "main", "args", "config"],
      "termFrequencies": {"def": 5, "main": 2, "args": 3},
      "docLength": 150
    }
  ],
  "corpusStats": {
    "totalDocs": 142,
    "avgDocLength": 120,
    "idf": {
      "def": 0.5,
      "main": 1.2
    }
  }
}
```

---

## bm25_data.json Structure

Separate file specifically for BM25 index data:
- Tokenized corpus
- Term frequencies per document
- IDF scores
- Document statistics

---

## Query Execution

### Semantic Query (indexType: "best"):
1. User query → embedding via all-minilm-l6-v2
2. Cosine similarity against all stored chunk embeddings
3. Top K results returned (ranked by similarity score)

### Keyword Query (indexType: "fast"):
1. User query → tokenized
2. BM25 scoring against all documents
3. Top K results returned (ranked by BM25 score)

---

## References

- **Sentence Transformers**: https://www.sbert.net/docs/pretrained_models.html#sentence-embedding-models
- **all-minilm-l6-v2**: 384-dimensional embeddings, trained on 1B+ pairs
- **BM25 Algorithm**: Okapi BM25 probabilistic retrieval function
- **Kiro Docs**: https://kiro.dev/docs/cli/custom-agents/configuration-reference/
