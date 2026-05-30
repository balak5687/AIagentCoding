"""
Manifest management for Project Brain.
Handles reading/writing the central manifest.yaml that references all knowledge bases.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class BrainManifest:
    """Manages the Project Brain manifest.yaml file"""

    def __init__(self, manifest_path: Path):
        self.manifest_path = Path(manifest_path)
        self.data: Dict[str, Any] = {}

    @classmethod
    def create_new(
        cls,
        brain_root: Path,
        project_name: str,
        backend_path: str,
        frontend_path: str,
        branch: str,
        test_issue: int
    ) -> 'BrainManifest':
        """Create a new manifest with default structure"""
        manifest_path = brain_root / "manifest.yaml"
        manifest = cls(manifest_path)

        manifest.data = {
            "version": "1.0",
            "project": project_name,
            "testIssue": test_issue,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "lastIndexed": None,

            "paths": {
                "backend": backend_path,
                "frontend": frontend_path,
                "branch": branch
            },

            "knowledgeBases": {
                "codingBrain": {
                    "id": f"{project_name.lower()}-codebase",
                    "name": f"{project_name} Codebase",
                    "indexType": "fast",
                    "source": str(brain_root / "sources/coding-brain/"),
                    "storagePath": str(brain_root / "knowledge-bases/coding-brain" / f"{project_name.lower()}-codebase/"),
                    "fileCount": 0,
                    "chunkCount": 0,
                    "autoUpdate": True,
                    "formats": ["py", "dart", "yaml", "json", "md"]
                },

                "functionalityBrain": {
                    "id": f"{project_name.lower()}-domain",
                    "name": f"{project_name} Domain Knowledge",
                    "indexType": "best",
                    "source": str(brain_root / "sources/functionality-brain/"),
                    "storagePath": str(brain_root / "knowledge-bases/functionality-brain" / f"{project_name.lower()}-domain/"),
                    "fileCount": 0,
                    "chunkCount": 0,
                    "autoUpdate": True,
                    "embeddingModel": "all-minilm-l6-v2",
                    "embeddingDimension": 384
                }
            },

            "agents": {
                "designer": {
                    "config": str(brain_root / "agents/designer.json"),
                    "knowledgeBases": ["functionalityBrain", "codingBrain"]
                },
                "contextAgent": {
                    "config": str(brain_root / "agents/context-agent.json"),
                    "knowledgeBases": ["codingBrain"]
                },
                "planner": {
                    "config": str(brain_root / "agents/planner.json"),
                    "knowledgeBases": ["functionalityBrain"]
                },
                "coder": {
                    "config": str(brain_root / "agents/coder.json"),
                    "knowledgeBases": ["codingBrain"]
                },
                "reviewer": {
                    "config": str(brain_root / "agents/reviewer.json"),
                    "knowledgeBases": ["codingBrain"]
                }
            },

            "lsp": {
                "python": {
                    "server": "pyright",
                    "command": "pyright-langserver",
                    "args": ["--stdio"],
                    "enabled": True
                },
                "dart": {
                    "server": "dart-analysis-server",
                    "command": "dart",
                    "args": ["language-server", "--protocol=lsp"],
                    "enabled": False  # Optional, requires Flutter SDK
                }
            }
        }

        return manifest

    @classmethod
    def load(cls, manifest_path: Path) -> 'BrainManifest':
        """Load existing manifest from disk"""
        manifest = cls(manifest_path)

        if not manifest.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest.manifest_path, 'r') as f:
            manifest.data = yaml.safe_load(f)

        return manifest

    def save(self) -> None:
        """Save manifest to disk"""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.manifest_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)

    def update_index_timestamp(self) -> None:
        """Update the lastIndexed timestamp"""
        self.data["lastIndexed"] = datetime.utcnow().isoformat() + "Z"

    def update_kb_stats(self, kb_name: str, file_count: int, chunk_count: int) -> None:
        """Update file and chunk counts for a knowledge base"""
        if kb_name in self.data["knowledgeBases"]:
            self.data["knowledgeBases"][kb_name]["fileCount"] = file_count
            self.data["knowledgeBases"][kb_name]["chunkCount"] = chunk_count

    def get_kb_config(self, kb_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific knowledge base"""
        return self.data["knowledgeBases"].get(kb_name)

    def get_agent_kbs(self, agent_name: str) -> List[str]:
        """Get list of knowledge bases accessible to an agent"""
        agent_config = self.data["agents"].get(agent_name)
        return agent_config.get("knowledgeBases", []) if agent_config else []

    def get_project_paths(self) -> Dict[str, str]:
        """Get backend/frontend paths"""
        return self.data.get("paths", {})

    def get_lsp_config(self, language: str) -> Optional[Dict[str, Any]]:
        """Get LSP server configuration for a language"""
        return self.data.get("lsp", {}).get(language)
