"""
Coding Brain - BM25 keyword search for codebase.
Uses tree-sitter for code parsing and BM25 for fast keyword search.
Layer 1 enhancement: RepoMap provides function-level symbol indexing to
replace the truncated 1-file-1-chunk approach.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from rank_bm25 import BM25Okapi
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from .repo_map import RepoMap
from .symbol_store import SymbolStore


class CodingBrain:
    """
    Coding Brain provides fast keyword search over codebase using BM25.
    """

    def __init__(self, kb_config: Dict[str, Any], manifest):
        self.kb_config = kb_config
        self.manifest = manifest
        self.source_path = Path(kb_config["source"])
        self.storage_path = Path(kb_config["storagePath"])

        # BM25 index (loaded lazily)
        self._bm25_index = None
        self._documents = None
        self._metadata = None

        # RepoMap symbol index (built alongside BM25 index)
        self._repo_map: Optional[Dict[str, List[Dict[str, Any]]]] = None

        # Qdrant-backed persistent symbol store (initialized lazily / on load)
        self._symbol_store: Optional[SymbolStore] = None

    def index_codebase(
        self,
        backend_path: str,
        frontend_path: Optional[str] = None
    ) -> Tuple[int, int]:
        """
        Index the codebase using tree-sitter for parsing.

        Args:
            backend_path: Path to backend codebase
            frontend_path: Optional path to frontend codebase

        Returns:
            Tuple of (file_count, chunk_count)
        """
        print(f"🔍 Scanning codebase...")

        documents = []
        metadata = []

        # Scan Python backend
        if backend_path:
            backend_docs, backend_meta = self._scan_directory(
                Path(backend_path),
                language="python",
                extensions=[".py"]
            )
            documents.extend(backend_docs)
            metadata.extend(backend_meta)
            print(f"  ✓ Scanned {len(backend_docs)} Python files from backend")

        # Scan frontend (auto-detect React TSX/TS or Flutter Dart)
        if frontend_path:
            fp = Path(frontend_path)
            # Detect React by presence of package.json or tsconfig.json
            is_react = (fp / "package.json").exists() or (fp / "tsconfig.json").exists()
            if is_react:
                lang, exts = "typescript", [".tsx", ".ts"]
                label = "TypeScript/React"
            else:
                lang, exts = "dart", [".dart"]
                label = "Dart/Flutter"
            frontend_docs, frontend_meta = self._scan_directory(fp, language=lang, extensions=exts)
            documents.extend(frontend_docs)
            metadata.extend(frontend_meta)
            print(f"  ✓ Scanned {len(frontend_docs)} {label} files from frontend")

        # Generate structure.md summary
        self._generate_structure_md(metadata)

        # Build BM25 index
        print(f"🔨 Building BM25 index from {len(documents)} files...")
        tokenized_docs = [doc.lower().split() for doc in documents]
        self._bm25_index = BM25Okapi(tokenized_docs)
        self._documents = documents
        self._metadata = metadata

        # Build RepoMap symbol index alongside BM25
        all_paths = [meta["file"] for meta in metadata]
        self.build_repo_map(all_paths)

        # Save to disk
        self._save_index()

        file_count = len(documents)
        chunk_count = len(documents)  # For now, 1 chunk = 1 file

        # Update manifest
        self.manifest.update_kb_stats("codingBrain", file_count, chunk_count)
        self.manifest.update_index_timestamp()
        self.manifest.save()

        print(f"✅ Coding Brain indexed: {file_count} files, {chunk_count} chunks")

        return file_count, chunk_count

    def _scan_directory(
        self,
        root_path: Path,
        language: str,
        extensions: List[str]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Scan a directory and extract code content"""
        documents = []
        metadata = []

        # Recursively find files
        for ext in extensions:
            for file_path in root_path.rglob(f"*{ext}"):
                # Skip common ignored directories
                if any(part in file_path.parts for part in [
                    'venv', 'node_modules', '.git', '__pycache__',
                    'build', 'dist', '.dart_tool'
                ]):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')

                    # Extract just the code content for indexing
                    # In future: could use tree-sitter to extract just function/class names
                    documents.append(content)

                    metadata.append({
                        "file": str(file_path.relative_to(root_path.parent)),
                        "language": language,
                        "lines": content.count('\n') + 1,
                        "size": len(content)
                    })

                except Exception as e:
                    print(f"  ⚠ Skipped {file_path}: {e}")
                    continue

        return documents, metadata

    def _generate_structure_md(self, metadata: List[Dict[str, Any]]) -> None:
        """Generate structure.md summary of the codebase"""
        self.source_path.mkdir(parents=True, exist_ok=True)

        # Group by language
        by_language = {}
        total_files = 0
        total_lines = 0

        for meta in metadata:
            lang = meta["language"]
            if lang not in by_language:
                by_language[lang] = {"files": 0, "lines": 0}

            by_language[lang]["files"] += 1
            by_language[lang]["lines"] += meta["lines"]
            total_files += 1
            total_lines += meta["lines"]

        # Write structure.md
        structure_md = self.source_path / "structure.md"
        with open(structure_md, 'w') as f:
            f.write("# Codebase Structure\n\n")
            f.write(f"**Total Files**: {total_files}  \n")
            f.write(f"**Total Lines**: {total_lines:,}  \n\n")

            f.write("## By Language\n\n")
            for lang, stats in sorted(by_language.items()):
                f.write(f"- **{lang.title()}**: {stats['files']} files, {stats['lines']:,} lines\n")

            f.write("\n## File Tree\n\n")
            f.write("```\n")

            # Group by directory
            dirs = {}
            for meta in metadata:
                file_path = Path(meta["file"])
                dir_name = str(file_path.parent) if file_path.parent != Path('.') else "root"

                if dir_name not in dirs:
                    dirs[dir_name] = []
                dirs[dir_name].append(file_path.name)

            # Write tree
            for dir_name in sorted(dirs.keys())[:20]:  # First 20 directories
                f.write(f"{dir_name}/\n")
                for file_name in sorted(dirs[dir_name])[:5]:  # First 5 files per dir
                    f.write(f"  {file_name}\n")
                if len(dirs[dir_name]) > 5:
                    f.write(f"  ... and {len(dirs[dir_name]) - 5} more files\n")

            if len(dirs) > 20:
                f.write(f"... and {len(dirs) - 20} more directories\n")

            f.write("```\n")

        print(f"  ✓ Generated structure.md")

    def _save_index(self) -> None:
        """Save BM25 index and metadata to disk"""
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Save contexts.json (Kiro format)
        contexts_json = self.storage_path.parent / "contexts.json"
        contexts_data = {
            "contexts": [{
                "id": self.kb_config["id"],
                "name": self.kb_config["name"],
                "source": self.kb_config["source"],
                "indexType": "fast",
                "createdAt": self.manifest.data["createdAt"],
                "lastIndexed": self.manifest.data["lastIndexed"] or self.manifest.data["createdAt"],
                "fileCount": len(self._documents),
                "chunkCount": len(self._documents),
                "totalTokens": sum(len(doc.split()) for doc in self._documents)
            }]
        }

        with open(contexts_json, 'w') as f:
            json.dump(contexts_data, f, indent=2)

        # Save bm25_data.json
        bm25_data_path = self.storage_path / "bm25_data.json"
        bm25_data = {
            "documents": [
                {
                    "id": f"doc-{i:05d}",
                    "content": doc[:500],  # Truncate for storage
                    "tokens": doc.lower().split(),
                    "metadata": meta
                }
                for i, (doc, meta) in enumerate(zip(self._documents, self._metadata))
            ],
            "corpusStats": {
                "totalDocs": len(self._documents),
                "avgDocLength": sum(len(doc.split()) for doc in self._documents) / len(self._documents) if self._documents else 0
            }
        }

        with open(bm25_data_path, 'w') as f:
            json.dump(bm25_data, f, indent=2)

        print(f"  ✓ Saved BM25 index to {bm25_data_path}")

    def _load_index(self) -> None:
        """Load BM25 index from disk"""
        bm25_data_path = self.storage_path / "bm25_data.json"

        if not bm25_data_path.exists():
            raise FileNotFoundError(f"BM25 index not found: {bm25_data_path}")

        with open(bm25_data_path, 'r') as f:
            data = json.load(f)

        self._documents = []
        self._metadata = []
        tokenized_docs = []

        for doc_entry in data["documents"]:
            self._documents.append(doc_entry["content"])
            self._metadata.append(doc_entry["metadata"])
            tokenized_docs.append(doc_entry["tokens"])

        self._bm25_index = BM25Okapi(tokenized_docs)

        # Re-attach the symbol store (loads from disk automatically via Qdrant persistence)
        try:
            self._symbol_store = SymbolStore()
            sym_count = self._symbol_store.count()
            print(f"  ✓ SymbolStore loaded: {sym_count} symbols from disk")
        except Exception as e:
            print(f"  ⚠ SymbolStore unavailable (non-fatal): {e}")
            self._symbol_store = None

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the codebase using BM25 keyword matching.

        Args:
            query: Search query (keywords)
            top_k: Number of results to return

        Returns:
            List of results with file, content, and score
        """
        # Lazy load index if not loaded
        if self._bm25_index is None:
            self._load_index()

        # Tokenize query
        tokenized_query = query.lower().split()

        # Get BM25 scores
        scores = self._bm25_index.get_scores(tokenized_query)

        # Get top K
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only return results with non-zero scores
                file_path = self._metadata[idx]["file"]
                entry: Dict[str, Any] = {
                    "file": file_path,
                    "content": self._documents[idx][:500],  # First 500 chars
                    "score": float(scores[idx]),
                    "metadata": self._metadata[idx],
                }
                # Attach symbol-level index when repo map is available
                if self._repo_map is not None:
                    symbols = self._repo_map.get(file_path, [])
                    if symbols:
                        entry["symbols"] = symbols
                results.append(entry)

        return results

    def ingest(self, content: str, source: str = "runtime") -> None:
        """Add a document to the live BM25 index without restart."""
        if self._bm25_index is None:
            self._load_index()

        tokens = content.lower().split()
        metadata = {"file": source, "type": "runtime_ingested"}

        self._documents.append(content)
        self._metadata.append(metadata)
        # BM25Okapi requires full rebuild on new document
        all_tokens = [doc.lower().split() for doc in self._documents]
        self._bm25_index = BM25Okapi(all_tokens)

    def build_repo_map(self, paths: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build a RepoMap symbol index for the given file paths.

        Extracts class names, method/function signatures, return types,
        and top-level constants using tree-sitter (Python) or regex (Dart).

        Args:
            paths: List of file paths to index.  If None, uses the paths
                   already stored in ``self._metadata``.

        Returns:
            Dict mapping file path → list of symbol entries.
            Each entry has keys: type, name, signature, docstring, line.
        """
        if paths is None:
            if self._metadata is None:
                self._load_index()
            paths = [m["file"] for m in self._metadata]

        # Resolve relative paths to absolute using manifest base dirs
        mp = self.manifest.data.get("paths", {})
        bases = {
            "GreasyNuts": mp.get("backend", ""),
            "GreasyNutsReact": mp.get("react", ""),
            "GreasyNutsFrontEnd": mp.get("frontend", ""),
        }
        resolved = []
        for p in paths:
            pp = Path(p)
            if pp.is_absolute() and pp.exists():
                resolved.append(str(pp))
                continue
            found = False
            for prefix, base in bases.items():
                if base and p.startswith(prefix + "/"):
                    candidate = Path(base).parent / p
                    if candidate.exists():
                        resolved.append(str(candidate))
                        found = True
                        break
            if not found and pp.exists():
                resolved.append(str(pp))

        rm = RepoMap(resolved if resolved else paths)
        self._repo_map = rm.build()
        total_syms = sum(len(v) for v in self._repo_map.values())
        print(f"  ✓ RepoMap built: {total_syms} symbols across {len(self._repo_map)} files")

        # Persist symbols into Qdrant symbol store
        try:
            if self._symbol_store is None:
                self._symbol_store = SymbolStore()
            self._symbol_store.clear()
            indexed = self._symbol_store.index_symbols(self._repo_map)
            print(f"  ✓ SymbolStore indexed {indexed} symbols")
        except Exception as e:
            print(f"  ⚠ SymbolStore indexing failed (non-fatal): {e}")

        return self._repo_map

    def get_repo_map(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Return the symbol list for a single file.

        If the repo map hasn't been built yet, builds it on demand for
        just this one file.
        """
        if self._repo_map is None:
            self.build_repo_map()

        # Exact match first
        if file_path in self._repo_map:
            return self._repo_map[file_path]

        # Suffix match (handle relative vs absolute paths)
        for key in self._repo_map:
            if key.endswith(file_path) or file_path.endswith(key):
                return self._repo_map[key]

        # File not in index yet — parse it on-the-fly
        rm = RepoMap([file_path])
        symbols = rm.build().get(file_path, [])
        self._repo_map[file_path] = symbols
        return symbols

    def find_symbol(self, symbol_name: str) -> List[Dict[str, Any]]:
        """
        Search for a symbol name across all indexed files.

        Uses SymbolStore.find_exact() when the store is available (fast, no
        embedding needed).  Falls back to in-memory repo map scan otherwise.
        Returns a list of matches, each containing a ``"file"`` key.
        """
        # Prefer the Qdrant-backed store — already persisted across restarts
        if self._symbol_store is not None:
            try:
                return self._symbol_store.find_exact(symbol_name)
            except Exception:
                pass  # fall through to in-memory fallback

        # Fallback: in-memory repo map scan
        if self._repo_map is None:
            self.build_repo_map()

        rm = RepoMap([])
        rm._index = self._repo_map
        return rm.find_symbol(symbol_name)
