"""
Repo Map — tree-sitter AST extraction of function/class signatures.
Replaces 1-file-1-chunk with function-level indexing.
Production pattern: Aider repo map (aider.chat/docs/repomap)
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

_PY_LANGUAGE = Language(tspython.language())
_PY_PARSER = Parser(_PY_LANGUAGE)


# ---------------------------------------------------------------------------
# Internal helpers — Python (tree-sitter)
# ---------------------------------------------------------------------------

def _node_text(node: Node, src: bytes) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _first_docstring(block_node: Node, src: bytes) -> Optional[str]:
    """Return the first line of a docstring inside a block node, if present."""
    for child in block_node.children:
        if child.type == "expression_statement":
            for sub in child.children:
                if sub.type == "string":
                    raw = _node_text(sub, src).strip("\"' \t\n")
                    return raw.split("\n")[0].strip()
    return None


def _build_py_signature(func_node: Node, src: bytes) -> str:
    """Build a human-readable signature from a function_definition node."""
    name = ""
    params = ""
    return_type = ""
    for child in func_node.children:
        if child.type == "identifier":
            name = _node_text(child, src)
        elif child.type == "parameters":
            params = _node_text(child, src)
        elif child.type == "type" and child.prev_sibling and child.prev_sibling.type == "->":
            return_type = _node_text(child, src)
    sig = f"def {name}{params}"
    if return_type:
        sig += f" -> {return_type}"
    return sig


def _extract_python(src: bytes) -> List[Dict[str, Any]]:
    """Walk the Python AST and extract symbols."""
    tree = _PY_PARSER.parse(src)
    symbols: List[Dict[str, Any]] = []

    def visit(node: Node, class_ctx: Optional[str] = None):
        if node.type == "class_definition":
            name = ""
            docstring = None
            for child in node.children:
                if child.type == "identifier":
                    name = _node_text(child, src)
                elif child.type == "block":
                    docstring = _first_docstring(child, src)
            symbols.append({
                "type": "class",
                "name": name,
                "signature": f"class {name}",
                "docstring": docstring,
                "line": node.start_point[0] + 1,
            })
            # recurse into class body
            for child in node.children:
                if child.type == "block":
                    for grandchild in child.children:
                        visit(grandchild, class_ctx=name)

        elif node.type == "function_definition":
            sig = _build_py_signature(node, src)
            func_name = ""
            docstring = None
            for child in node.children:
                if child.type == "identifier":
                    func_name = _node_text(child, src)
                elif child.type == "block":
                    docstring = _first_docstring(child, src)

            symbol_type = "method" if class_ctx else "function"
            entry: Dict[str, Any] = {
                "type": symbol_type,
                "name": func_name,
                "signature": sig,
                "docstring": docstring,
                "line": node.start_point[0] + 1,
            }
            if class_ctx:
                entry["class"] = class_ctx
            symbols.append(entry)

            # Don't recurse into nested functions from here; top-level walk
            # handles nested functions inside classes via the class block walk.

        elif node.type == "expression_statement" and class_ctx is None:
            # Top-level constants / important assignments
            for child in node.children:
                if child.type == "assignment":
                    lhs = child.children[0] if child.children else None
                    if lhs and lhs.type == "identifier":
                        var_name = _node_text(lhs, src)
                        # Only index ALL_CAPS constants or __dunder__ names
                        if var_name.isupper() or (var_name.startswith("__") and var_name.endswith("__")):
                            symbols.append({
                                "type": "constant",
                                "name": var_name,
                                "signature": _node_text(child, src).split("\n")[0][:120],
                                "docstring": None,
                                "line": node.start_point[0] + 1,
                            })

        elif node.type not in ("class_definition", "function_definition"):
            # Continue walking top-level nodes
            for child in node.children:
                if child.type in ("class_definition", "function_definition", "expression_statement"):
                    visit(child, class_ctx=class_ctx)

    for top_node in tree.root_node.children:
        visit(top_node)

    return symbols


# ---------------------------------------------------------------------------
# Internal helpers — Dart (regex fallback)
# ---------------------------------------------------------------------------

# Patterns for Dart
_DART_CLASS_RE = re.compile(
    r'^(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?(?:\s+with\s+[\w,\s]+)?\s*\{',
    re.MULTILINE,
)
_DART_METHOD_RE = re.compile(
    r'^\s{2,}(?:(?:static|async|@\w+\s*)*\s*)?'  # modifiers
    r'(?:([\w<>\[\]?,\s]+?)\s+)?'                  # return type (optional)
    r'(\w+)\s*\(([^)]*)\)',                        # name + params
    re.MULTILINE,
)
_DART_TOPLEVEL_FUNC_RE = re.compile(
    r'^(?:([\w<>\[\]?,\s]+?)\s+)?(\w+)\s*\(([^)]*)\)\s*(?:async\s*)?\{',
    re.MULTILINE,
)
_DART_CONST_RE = re.compile(
    r'^(?:const|final)\s+([\w<>]+)\s+([A-Z_][A-Z0-9_]*)\s*=',
    re.MULTILINE,
)


def _extract_dart(src: str) -> List[Dict[str, Any]]:
    """Regex-based Dart symbol extraction."""
    symbols: List[Dict[str, Any]] = []
    lines = src.splitlines()

    def _lineno(pos: int) -> int:
        return src[:pos].count("\n") + 1

    # Classes
    for m in _DART_CLASS_RE.finditer(src):
        symbols.append({
            "type": "class",
            "name": m.group(1),
            "signature": m.group(0).rstrip("{").strip(),
            "docstring": None,
            "line": _lineno(m.start()),
        })

    # Top-level functions (not indented)
    for m in _DART_TOPLEVEL_FUNC_RE.finditer(src):
        # Skip if line starts with spaces (it's a method)
        line_start = src.rfind("\n", 0, m.start()) + 1
        prefix = src[line_start:m.start()]
        if prefix.strip() == "" and not prefix.startswith(" "):
            name = m.group(2)
            ret = (m.group(1) or "").strip()
            params = m.group(3).strip()
            sig = f"{ret} {name}({params})".strip()
            symbols.append({
                "type": "function",
                "name": name,
                "signature": sig,
                "docstring": None,
                "line": _lineno(m.start()),
            })

    # Constants
    for m in _DART_CONST_RE.finditer(src):
        symbols.append({
            "type": "constant",
            "name": m.group(2),
            "signature": m.group(0)[:120],
            "docstring": None,
            "line": _lineno(m.start()),
        })

    return symbols


def _extract_typescript(src: str) -> List[Dict[str, Any]]:
    """Extract symbols from TypeScript/TSX files using regex."""
    symbols: List[Dict[str, Any]] = []
    lines = src.splitlines()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # React component: export default function Foo / export function Foo
        import re
        m = re.match(r'(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+(\w+)\s*[(<]', stripped)
        if m:
            name = m.group(1)
            symbols.append({"type": "function", "name": name,
                            "signature": stripped[:120], "docstring": "", "line": i})
            continue

        # Arrow function component: export const Foo = (
        m = re.match(r'(?:export\s+)?const\s+(\w+)\s*[=:]\s*(?:React\.memo\()?(?:async\s*)?\(', stripped)
        if m:
            name = m.group(1)
            kind = "component" if name[0].isupper() else "constant"
            symbols.append({"type": kind, "name": name,
                            "signature": stripped[:120], "docstring": "", "line": i})
            continue

        # Interface / type
        m = re.match(r'(?:export\s+)?interface\s+(\w+)', stripped)
        if m:
            symbols.append({"type": "interface", "name": m.group(1),
                            "signature": stripped[:80], "docstring": "", "line": i})
            continue

        m = re.match(r'(?:export\s+)?type\s+(\w+)\s*=', stripped)
        if m:
            symbols.append({"type": "type", "name": m.group(1),
                            "signature": stripped[:80], "docstring": "", "line": i})
            continue

    return symbols


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class RepoMap:
    """
    Build a structured symbol index for a set of source files.

    Usage::

        rm = RepoMap(["/path/to/foo.py", "/path/to/bar.dart"])
        index = rm.build()           # {file_path: [symbol, ...]}
        text  = rm.repo_map_string() # compact text for prompt injection
    """

    def __init__(self, file_paths: List[str]):
        self.file_paths = [str(p) for p in file_paths]
        self._index: Optional[Dict[str, List[Dict[str, Any]]]] = None

    # ------------------------------------------------------------------
    def build(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse all files and return::

            {
              "path/to/file.py": [
                {"type": "class|function|method|constant",
                 "name": "...",
                 "signature": "...",
                 "docstring": "...",   # first line, may be None
                 "line": 42},
                ...
              ],
              ...
            }
        """
        result: Dict[str, List[Dict[str, Any]]] = {}
        for fp in self.file_paths:
            path = Path(fp)
            if not path.exists():
                continue
            ext = path.suffix.lower()
            try:
                if ext == ".py":
                    src = path.read_bytes()
                    result[fp] = _extract_python(src)
                elif ext == ".dart":
                    src = path.read_text(encoding="utf-8", errors="replace")
                    result[fp] = _extract_dart(src)
                elif ext in (".tsx", ".ts", ".jsx", ".js"):
                    src = path.read_text(encoding="utf-8", errors="replace")
                    result[fp] = _extract_typescript(src)
                # silently skip unsupported extensions
            except Exception as exc:
                result[fp] = [{"type": "error", "name": str(exc), "signature": "", "line": 0}]

        self._index = result
        return result

    # ------------------------------------------------------------------
    def repo_map_string(self) -> str:
        """
        Compact text representation of the entire repo map.
        Suitable for injection into an agent prompt.

        Example output::

            src/brain/coding_brain.py
              class CodingBrain              (line 13)
                def __init__(self, kb_config, manifest)  (line 18)
                def index_codebase(self, backend_path, frontend_path) -> Tuple[int, int]  (line 29)
        """
        if self._index is None:
            self.build()

        lines: List[str] = []
        for fp, symbols in sorted(self._index.items()):
            if not symbols:
                continue
            lines.append(fp)
            for sym in symbols:
                indent = "    " if sym["type"] == "method" else "  "
                sig = sym["signature"]
                lineno = sym["line"]
                doc_suffix = f"  # {sym['docstring']}" if sym.get("docstring") else ""
                lines.append(f"{indent}{sig}  (line {lineno}){doc_suffix}")
            lines.append("")  # blank separator

        return "\n".join(lines)

    # ------------------------------------------------------------------
    def find_symbol(self, symbol_name: str) -> List[Dict[str, Any]]:
        """
        Return all entries whose name matches *symbol_name* (case-sensitive).
        Each entry is augmented with a ``"file"`` key.
        """
        if self._index is None:
            self.build()

        matches: List[Dict[str, Any]] = []
        for fp, symbols in self._index.items():
            for sym in symbols:
                if sym["name"] == symbol_name:
                    matches.append({**sym, "file": fp})
        return matches

    # ------------------------------------------------------------------
    @classmethod
    def from_directory(
        cls,
        root: str,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
    ) -> "RepoMap":
        """Convenience constructor: scan a directory tree."""
        if extensions is None:
            extensions = [".py", ".dart", ".tsx", ".ts", ".jsx"]
        if exclude_dirs is None:
            exclude_dirs = ["venv", "node_modules", ".git", "__pycache__", "build", "dist", ".dart_tool"]

        paths: List[str] = []
        root_path = Path(root)
        for ext in extensions:
            for fp in root_path.rglob(f"*{ext}"):
                if any(part in fp.parts for part in exclude_dirs):
                    continue
                paths.append(str(fp))
        return cls(paths)
