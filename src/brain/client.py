"""
Project Brain Client - Lightweight HTTP client for agents.
No model loading. Queries the persistent Brain Server.
"""
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional


BRAIN_SERVER_URL = "http://127.0.0.1:7433"


def _post(endpoint: str, data: dict) -> dict:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BRAIN_SERVER_URL}{endpoint}",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _get(endpoint: str) -> dict:
    with urllib.request.urlopen(f"{BRAIN_SERVER_URL}{endpoint}", timeout=5) as resp:
        return json.loads(resp.read())


def is_running() -> bool:
    try:
        _get("/health")
        return True
    except Exception:
        return False


def search_code(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """BM25 keyword search over codebase"""
    return _post("/query/code", {"query": query, "top_k": top_k})["results"]


def search_knowledge(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Semantic search over requirements/design"""
    return _post("/query/knowledge", {"query": query, "top_k": top_k})["results"]


def get_context(
    agent_name: str,
    code_query: Optional[str] = None,
    knowledge_query: Optional[str] = None,
    top_k: int = 3
) -> str:
    """Get formatted context string ready for prompt injection"""
    return _post("/query/context", {
        "agent": agent_name,
        "code_query": code_query,
        "knowledge_query": knowledge_query,
        "top_k": top_k
    })["context"]


def ingest(content: str, source: str = "runtime", brain: str = "functionality") -> bool:
    """Inject a document into the live brain index. Returns True on success."""
    try:
        _post("/ingest", {"content": content, "source": source, "brain": brain})
        return True
    except Exception:
        return False


def status() -> dict:
    return _get("/status")


def get_repo_map(file_path: str) -> dict:
    """
    Return the symbol map for a specific file.

    The response has the shape::

        {
          "file": "path/to/file.py",
          "symbols": [
            {"type": "class|function|method|constant",
             "name": "...",
             "signature": "...",
             "docstring": "...",
             "line": 42},
            ...
          ]
        }

    Returns an empty dict (with ``"symbols": []``) on error.
    """
    try:
        import urllib.parse
        encoded = urllib.parse.quote(file_path, safe="")
        return _get(f"/repo-map?file={encoded}")
    except Exception:
        return {"file": file_path, "symbols": []}


def find_symbol(symbol_name: str) -> dict:
    """
    Search all indexed files for a symbol with the given name.

    Returns::

        {
          "symbol": "get_supply_issues",
          "matches": [
            {"type": "function", "name": "get_supply_issues",
             "signature": "...", "line": 42, "file": "path/to/file.py"},
            ...
          ]
        }

    Returns ``{"symbol": ..., "matches": []}`` on error.
    """
    try:
        import urllib.parse
        encoded = urllib.parse.quote(symbol_name, safe="")
        return _get(f"/repo-map/search?symbol={encoded}")
    except Exception:
        return {"symbol": symbol_name, "matches": []}
