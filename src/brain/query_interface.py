"""
Runtime Query Interface for Agents.
Provides a simple API for agents to query the Project Brain during execution.
"""
from typing import List, Dict, Any, Optional
from .base import ProjectBrain


class BrainQueryInterface:
    """
    Simple query interface that agents can use at runtime.
    Wraps ProjectBrain with convenience methods.
    """

    def __init__(self, brain: ProjectBrain, agent_name: str):
        self.brain = brain
        self.agent_name = agent_name

    @classmethod
    def for_agent(cls, manifest_path: str, agent_name: str) -> 'BrainQueryInterface':
        """
        Create a query interface for a specific agent.

        Args:
            manifest_path: Path to manifest.yaml
            agent_name: Name of the agent (designer, coder, etc.)

        Returns:
            BrainQueryInterface instance
        """
        brain = ProjectBrain.load(manifest_path)
        return cls(brain, agent_name)

    def get_context(self) -> Dict[str, Any]:
        """
        Get available knowledge bases and query methods for this agent.

        Returns:
            Dict with knowledgeBases and availableQueries
        """
        return self.brain.get_agent_context(self.agent_name)

    def search_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search codebase using BM25 keyword matching.
        Only works if agent has access to codingBrain.

        Args:
            query: Keywords to search for
            top_k: Number of results

        Returns:
            List of {file, content, score, metadata}

        Example:
            results = interface.search_code("purchase_order create function")
            for r in results:
                print(f"{r['file']}: {r['score']}")
        """
        kb_names = self.brain.manifest.get_agent_kbs(self.agent_name)

        if "codingBrain" not in kb_names:
            return []

        return self.brain.coding.search(query, top_k=top_k)

    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search domain knowledge using semantic similarity.
        Only works if agent has access to functionalityBrain.

        Args:
            query: Natural language query
            top_k: Number of results

        Returns:
            List of {content, similarity, metadata}

        Example:
            results = interface.search_knowledge("What are dashboard requirements?")
            for r in results:
                print(f"Similarity: {r['similarity']:.2f}")
                print(r['content'])
        """
        kb_names = self.brain.manifest.get_agent_kbs(self.agent_name)

        if "functionalityBrain" not in kb_names:
            return []

        return self.brain.functionality.search(query, top_k=top_k)

    def auto_query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Automatically route query to appropriate brain.
        Uses heuristics to detect if query is code-related or domain-related.

        Args:
            query: Any query string
            top_k: Number of results

        Returns:
            Results from appropriate brain

        Example:
            # Auto-detects this is code query
            results = interface.auto_query("find authentication function")

            # Auto-detects this is domain query
            results = interface.auto_query("what are the dashboard requirements")
        """
        return self.brain.query_for_agent(
            agent_name=self.agent_name,
            query=query,
            query_type="auto",
            top_k=top_k
        )

    def format_context_for_prompt(
        self,
        code_query: Optional[str] = None,
        knowledge_query: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """
        Format relevant context as a string that can be injected into agent prompts.

        Args:
            code_query: Optional query for codebase
            knowledge_query: Optional query for domain knowledge
            top_k: Number of results per query

        Returns:
            Formatted string with context

        Example:
            context = interface.format_context_for_prompt(
                code_query="purchase_order",
                knowledge_query="dashboard requirements"
            )

            # Then inject into agent prompt:
            prompt = f"<context>\n{context}\n</context>\n\nYour task: ..."
        """
        sections = []

        # Add code context
        if code_query:
            results = self.search_code(code_query, top_k=top_k)
            if results:
                sections.append("## Relevant Code\n")
                for i, r in enumerate(results, 1):
                    sections.append(f"### {i}. {r['file']} (score: {r['score']:.2f})\n")
                    sections.append(f"```\n{r['content'][:500]}\n```\n")

        # Add knowledge context
        if knowledge_query:
            results = self.search_knowledge(knowledge_query, top_k=top_k)
            if results:
                sections.append("\n## Relevant Requirements & Design\n")
                for i, r in enumerate(results, 1):
                    sections.append(f"### {i}. {r['metadata']['file']} (similarity: {r['similarity']:.2f})\n")
                    sections.append(f"{r['content']}\n\n")

        return "\n".join(sections) if sections else "No relevant context found."

    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get full content of a specific file from the coding brain.

        Args:
            file_path: Relative path to file

        Returns:
            File content or None if not found
        """
        # Search for exact file path
        results = self.search_code(file_path, top_k=1)

        if results and file_path in results[0]['file']:
            return results[0]['content']

        return None
