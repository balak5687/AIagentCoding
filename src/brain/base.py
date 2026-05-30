"""
Base Project Brain class that provides unified access to both coding and functionality brains.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from .manifest import BrainManifest


class ProjectBrain:
    """
    Main interface to the Project Brain system.
    Provides access to both Coding Brain (BM25) and Functionality Brain (semantic).
    """

    def __init__(self, manifest: BrainManifest):
        self.manifest = manifest
        self.brain_root = Path(manifest.manifest_path).parent

        # Will be initialized lazily
        self._coding_brain = None
        self._functionality_brain = None
        self._lsp_manager = None

    @classmethod
    def load(cls, manifest_path: str) -> 'ProjectBrain':
        """Load Project Brain from manifest file"""
        manifest = BrainManifest.load(Path(manifest_path))
        return cls(manifest)

    @classmethod
    def create_new(
        cls,
        brain_root: Path,
        project_name: str,
        backend_path: str,
        frontend_path: str,
        branch: str,
        test_issue: int
    ) -> 'ProjectBrain':
        """Create a new Project Brain"""
        manifest = BrainManifest.create_new(
            brain_root=brain_root,
            project_name=project_name,
            backend_path=backend_path,
            frontend_path=frontend_path,
            branch=branch,
            test_issue=test_issue
        )
        manifest.save()

        brain = cls(manifest)

        # Create necessary directories
        for kb_name, kb_config in manifest.data["knowledgeBases"].items():
            Path(kb_config["source"]).mkdir(parents=True, exist_ok=True)
            Path(kb_config["storagePath"]).mkdir(parents=True, exist_ok=True)

        return brain

    @property
    def coding(self):
        """Get Coding Brain instance (lazy loading)"""
        if self._coding_brain is None:
            from .coding_brain import CodingBrain
            kb_config = self.manifest.get_kb_config("codingBrain")
            self._coding_brain = CodingBrain(kb_config, self.manifest)
        return self._coding_brain

    @property
    def functionality(self):
        """Get Functionality Brain instance (lazy loading)"""
        if self._functionality_brain is None:
            from .functionality_brain import FunctionalityBrain
            kb_config = self.manifest.get_kb_config("functionalityBrain")
            self._functionality_brain = FunctionalityBrain(kb_config, self.manifest)
        return self._functionality_brain

    @property
    def lsp(self):
        """Get LSP Manager instance (lazy loading)"""
        if self._lsp_manager is None:
            from .lsp_manager import LSPManager
            self._lsp_manager = LSPManager(self.manifest)
        return self._lsp_manager

    def get_agent_context(self, agent_name: str) -> Dict[str, Any]:
        """
        Get complete context for an agent based on its configured knowledge bases.
        This is called by agents at runtime to get relevant context.
        """
        kb_names = self.manifest.get_agent_kbs(agent_name)
        context = {
            "agent": agent_name,
            "knowledgeBases": {},
            "availableQueries": []
        }

        for kb_name in kb_names:
            if kb_name == "codingBrain":
                context["knowledgeBases"]["coding"] = {
                    "type": "BM25",
                    "indexType": "fast",
                    "description": "Keyword search for functions, classes, files in codebase"
                }
                context["availableQueries"].append("brain.coding.search(query)")

            elif kb_name == "functionalityBrain":
                context["knowledgeBases"]["functionality"] = {
                    "type": "Semantic",
                    "indexType": "best",
                    "description": "Semantic search for requirements, design, domain knowledge"
                }
                context["availableQueries"].append("brain.functionality.search(query, top_k=5)")

        # Add LSP capabilities if enabled
        lsp_python = self.manifest.get_lsp_config("python")
        if lsp_python and lsp_python.get("enabled"):
            context["availableQueries"].extend([
                "brain.lsp.goto_definition(symbol, file)",
                "brain.lsp.find_references(symbol)",
                "brain.lsp.get_diagnostics(file)"
            ])

        return context

    def query_for_agent(
        self,
        agent_name: str,
        query: str,
        query_type: str = "auto",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Universal query interface for agents.
        Automatically routes to appropriate brain based on agent's KB access.

        Args:
            agent_name: Name of the requesting agent
            query: Query string
            query_type: "coding", "functionality", or "auto" (auto-detect)
            top_k: Number of results to return

        Returns:
            List of results with content, metadata, and scores
        """
        kb_names = self.manifest.get_agent_kbs(agent_name)

        if query_type == "auto":
            # Simple heuristic: code-like queries go to coding brain
            code_indicators = ["function", "class", "method", "import", "def ", "def("]
            if any(indicator in query.lower() for indicator in code_indicators):
                query_type = "coding"
            else:
                query_type = "functionality"

        results = []

        if query_type == "coding" and "codingBrain" in kb_names:
            results = self.coding.search(query, top_k=top_k)

        elif query_type == "functionality" and "functionalityBrain" in kb_names:
            results = self.functionality.search(query, top_k=top_k)

        return results

    def save(self) -> None:
        """Save manifest and any updated indexes"""
        self.manifest.save()
