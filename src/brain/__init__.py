"""
Project Brain - Two-brain knowledge system for multi-agent SDLC.

Provides:
- Coding Brain: BM25 keyword search for codebase
- Functionality Brain: Semantic search for requirements/design
- LSP integration: Deep code intelligence
- Runtime query interface for agents
"""
from .base import ProjectBrain
from .manifest import BrainManifest

__all__ = ["ProjectBrain", "BrainManifest"]
