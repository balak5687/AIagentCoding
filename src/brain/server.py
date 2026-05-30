"""
Project Brain Server - Runs as a persistent background process.
Agents query it via HTTP on localhost. No model reloading between queries.
"""
import json
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from .base import ProjectBrain


class BrainRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress default HTTP logs unless debug
        if self.server.debug:
            print(f"[Brain Server] {format % args}")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/health":
            self._respond(200, {"status": "ok", "project": self.server.brain.manifest.data["project"]})

        elif path == "/status":
            manifest = self.server.brain.manifest.data
            brain = self.server.brain
            # Use live in-memory counts if available, else fall back to manifest
            coding_files = len(brain.coding._documents) if brain.coding._documents else manifest["knowledgeBases"]["codingBrain"]["fileCount"]
            func_chunks = len(brain.functionality._chunks) if brain.functionality._chunks is not None else manifest["knowledgeBases"]["functionalityBrain"]["chunkCount"]
            self._respond(200, {
                "project": manifest["project"],
                "issue": manifest["testIssue"],
                "coding_files": coding_files,
                "coding_chunks": coding_files,
                "functionality_chunks": func_chunks,
                "last_indexed": manifest["lastIndexed"]
            })

        elif path == "/repo-map":
            # GET /repo-map?file=path/to/file.py
            file_param = params.get("file", [None])[0]
            if not file_param:
                self._respond(400, {"error": "Missing 'file' query parameter"})
                return
            symbols = self.server.brain.coding.get_repo_map(file_param)
            self._respond(200, {"file": file_param, "symbols": symbols})

        elif path == "/repo-map/search":
            # GET /repo-map/search?symbol=get_supply_issues
            symbol_param = params.get("symbol", [None])[0]
            if not symbol_param:
                self._respond(400, {"error": "Missing 'symbol' query parameter"})
                return
            coding = self.server.brain.coding
            # Prefer SymbolStore exact lookup when available (persisted across restarts)
            if coding._symbol_store is not None:
                try:
                    matches = coding._symbol_store.find_exact(symbol_param)
                    self._respond(200, {"symbol": symbol_param, "matches": matches, "source": "symbol_store"})
                    return
                except Exception:
                    pass  # fall through to in-memory search
            matches = coding.find_symbol(symbol_param)
            self._respond(200, {"symbol": symbol_param, "matches": matches, "source": "repo_map"})

        else:
            self._respond(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if self.path == "/query/code":
            # BM25 keyword search over codebase
            query = body.get("query", "")
            top_k = body.get("top_k", 5)
            results = self.server.brain.coding.search(query, top_k=top_k)
            self._respond(200, {"results": results})

        elif self.path == "/query/knowledge":
            # Semantic search over requirements/design
            query = body.get("query", "")
            top_k = body.get("top_k", 5)
            results = self.server.brain.functionality.search(query, top_k=top_k)
            self._respond(200, {"results": results})

        elif self.path == "/query/context":
            # Auto-enriched context formatted for agent prompt injection
            agent_name = body.get("agent", "designer")
            code_query = body.get("code_query")
            knowledge_query = body.get("knowledge_query")
            top_k = body.get("top_k", 3)

            from .query_interface import BrainQueryInterface
            interface = BrainQueryInterface(self.server.brain, agent_name)
            context_str = interface.format_context_for_prompt(
                code_query=code_query,
                knowledge_query=knowledge_query,
                top_k=top_k
            )
            self._respond(200, {"context": context_str})

        elif self.path == "/ingest":
            content = body.get("content", "")
            source = body.get("source", "runtime")
            brain_target = body.get("brain", "functionality")

            if not content:
                self._respond(400, {"error": "content required"})
                return

            if brain_target == "coding":
                self.server.brain.coding.ingest(content, source)
            else:
                self.server.brain.functionality.ingest(content, source)

            self._respond(200, {"status": "ingested", "source": source, "brain": brain_target})

        else:
            self._respond(404, {"error": "Unknown endpoint"})

    def _respond(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


class BrainServer:
    def __init__(self, manifest_path: str, host: str = "127.0.0.1", port: int = 7433, debug: bool = False):
        self.manifest_path = manifest_path
        self.host = host
        self.port = port
        self.debug = debug
        self.httpd: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        print(f"🧠 Loading Project Brain from {self.manifest_path}...")
        brain = ProjectBrain.load(self.manifest_path)

        # Pre-load both indexes into memory now (once)
        print("  Loading Coding Brain (BM25)...")
        brain.coding._load_index()

        print("  Loading Functionality Brain (embeddings)...")
        brain.functionality._load_index()
        brain.functionality._load_model()

        print(f"  ✅ Both brains loaded and ready")

        # Start HTTP server
        self.httpd = ThreadingHTTPServer((self.host, self.port), BrainRequestHandler)
        self.httpd.brain = brain
        self.httpd.debug = self.debug

        print(f"🚀 Brain Server running at http://{self.host}:{self.port}")
        print(f"   Endpoints:")
        print(f"     GET  /health")
        print(f"     GET  /status")
        print(f"     GET  /repo-map?file=<path>")
        print(f"     GET  /repo-map/search?symbol=<name>")
        print(f"     POST /query/code       {{query, top_k}}")
        print(f"     POST /query/knowledge  {{query, top_k}}")
        print(f"     POST /query/context    {{agent, code_query, knowledge_query, top_k}}")
        print()
        self.httpd.serve_forever()

    def start_background(self):
        """Start the server in a background thread"""
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()


def run_server(manifest_path: str, port: int = 7433, debug: bool = False):
    server = BrainServer(manifest_path, port=port, debug=debug)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Brain Server stopped")
