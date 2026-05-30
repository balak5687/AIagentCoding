"""
Functionality Brain - Semantic search for domain knowledge, requirements, design.
Uses sentence-transformers (all-minilm-l6-v2) for embeddings.
"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
from github import Github
import os


class FunctionalityBrain:
    """
    Functionality Brain provides semantic search over requirements, design, and domain knowledge.
    """

    def __init__(self, kb_config: Dict[str, Any], manifest):
        self.kb_config = kb_config
        self.manifest = manifest
        self.source_path = Path(kb_config["source"])
        self.storage_path = Path(kb_config["storagePath"])

        # Embedding model (loaded lazily)
        self._model = None
        self._embeddings = None
        self._chunks = None
        self._metadata = None

    def index_knowledge(
        self,
        github_issue_url: Optional[str] = None,
        issue_number: Optional[int] = None,
        repo_name: Optional[str] = None
    ) -> Tuple[int, int]:
        """
        Index domain knowledge including GitHub issue, product docs, specs.

        Args:
            github_issue_url: Full URL to GitHub issue
            issue_number: Issue number (if repo_name provided)
            repo_name: Repo name like "owner/repo"

        Returns:
            Tuple of (file_count, chunk_count)
        """
        print(f"🔍 Building Functionality Brain...")

        # Ensure source directory exists
        self.source_path.mkdir(parents=True, exist_ok=True)

        # Fetch GitHub issue if provided
        if github_issue_url or (issue_number and repo_name):
            self._fetch_github_issue(github_issue_url, issue_number, repo_name)

        # Generate product.md from README if exists
        backend_path = self.manifest.get_project_paths().get("backend")
        if backend_path:
            self._generate_product_md(backend_path)

        # Collect all markdown files to index
        chunks, metadata = self._collect_and_chunk_documents()

        # Generate embeddings
        print(f"🔨 Generating embeddings for {len(chunks)} chunks...")
        self._load_model()
        embeddings = self._model.encode(chunks, show_progress_bar=True)

        self._embeddings = embeddings
        self._chunks = chunks
        self._metadata = metadata

        # Save to disk
        self._save_index()

        file_count = len(set(m["file"] for m in metadata))
        chunk_count = len(chunks)

        # Update manifest
        self.manifest.update_kb_stats("functionalityBrain", file_count, chunk_count)
        self.manifest.update_index_timestamp()
        self.manifest.save()

        print(f"✅ Functionality Brain indexed: {file_count} files, {chunk_count} chunks")

        return file_count, chunk_count

    def _fetch_github_issue(
        self,
        issue_url: Optional[str] = None,
        issue_number: Optional[int] = None,
        repo_name: Optional[str] = None
    ) -> None:
        """Fetch GitHub issue and save as requirements.md"""
        try:
            # Get GitHub token from environment
            github_token = os.getenv('GITHUB_TOKEN')
            if not github_token:
                print("  ⚠ No GITHUB_TOKEN found, skipping issue fetch")
                return

            g = Github(github_token)

            # Parse issue URL or use provided params
            if issue_url:
                # Extract repo and issue from URL
                # Format: https://github.com/owner/repo/issues/123
                parts = issue_url.replace('https://github.com/', '').split('/')
                repo_name = f"{parts[0]}/{parts[1]}"
                issue_number = int(parts[3])

            if not (repo_name and issue_number):
                print("  ⚠ Invalid issue parameters")
                return

            print(f"  📥 Fetching issue #{issue_number} from {repo_name}...")

            repo = g.get_repo(repo_name)
            issue = repo.get_issue(issue_number)

            # Create specs directory
            specs_dir = self.source_path / "specs" / f"issue-{issue_number}"
            specs_dir.mkdir(parents=True, exist_ok=True)

            # Write requirements.md
            requirements_path = specs_dir / "requirements.md"
            with open(requirements_path, 'w') as f:
                f.write(f"# Requirements - Issue #{issue_number}\n\n")
                f.write(f"**Title**: {issue.title}\n\n")
                f.write(f"**Status**: {issue.state}\n")
                f.write(f"**Created**: {issue.created_at}\n")
                f.write(f"**Updated**: {issue.updated_at}\n\n")

                if issue.labels:
                    f.write(f"**Labels**: {', '.join([l.name for l in issue.labels])}\n\n")

                f.write("## Description\n\n")
                f.write(issue.body or "No description provided")
                f.write("\n\n")

                # Include comments as additional context
                comments = issue.get_comments()
                if comments.totalCount > 0:
                    f.write("## Discussion\n\n")
                    for comment in comments:
                        f.write(f"### Comment by {comment.user.login} ({comment.created_at})\n\n")
                        f.write(comment.body)
                        f.write("\n\n")

            print(f"  ✓ Saved requirements to {requirements_path.relative_to(self.source_path.parent)}")

            # Create placeholder design.md and tasks.md
            (specs_dir / "design.md").write_text(
                f"# Design - Issue #{issue_number}\n\n"
                f"**Status**: To be generated by Designer agent\n\n"
                f"This file will be populated by the Designer agent after analyzing requirements.\n"
            )

            (specs_dir / "tasks.md").write_text(
                f"# Tasks - Issue #{issue_number}\n\n"
                f"**Status**: To be generated by Planner agent\n\n"
                f"This file will be populated by the Planner agent after reviewing the design.\n"
            )

        except Exception as e:
            print(f"  ⚠ Failed to fetch GitHub issue: {e}")

    def _generate_product_md(self, backend_path: str) -> None:
        """Generate product.md from README if it exists"""
        readme_path = Path(backend_path) / "README.md"

        if not readme_path.exists():
            # Create a basic product.md
            product_md = self.source_path / "product.md"
            product_md.write_text(
                "# Product Overview\n\n"
                f"**Project**: {self.manifest.data['project']}\n\n"
                "This file should contain:\n"
                "- What the product does\n"
                "- Target users\n"
                "- Key features\n"
                "- Business objectives\n"
            )
            print(f"  ✓ Created placeholder product.md")
            return

        # Copy README content to product.md
        product_md = self.source_path / "product.md"
        content = readme_path.read_text()

        with open(product_md, 'w') as f:
            f.write("# Product Overview\n\n")
            f.write(content)

        print(f"  ✓ Generated product.md from README")

    def _collect_and_chunk_documents(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Collect all markdown files and chunk them"""
        chunks = []
        metadata = []

        # Recursively find all markdown files
        for md_file in self.source_path.rglob("*.md"):
            try:
                content = md_file.read_text()

                # Simple chunking: split by double newline (paragraphs)
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

                for i, para in enumerate(paragraphs):
                    if len(para) > 50:  # Only chunks with substantial content
                        chunks.append(para)
                        metadata.append({
                            "file": str(md_file.relative_to(self.source_path)),
                            "chunkIndex": i,
                            "chunkLength": len(para)
                        })

            except Exception as e:
                print(f"  ⚠ Skipped {md_file}: {e}")

        print(f"  ✓ Collected {len(chunks)} chunks from {len(set(m['file'] for m in metadata))} files")

        return chunks, metadata

    def _load_model(self) -> None:
        """Load sentence transformer model"""
        if self._model is None:
            print(f"  📦 Loading embedding model: all-minilm-l6-v2...")
            self._model = SentenceTransformer('all-minilm-l6-v2')

    def _save_index(self) -> None:
        """Save embeddings and metadata to disk"""
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Save contexts.json (Kiro format)
        contexts_json = self.storage_path.parent / "contexts.json"
        contexts_data = {
            "contexts": [{
                "id": self.kb_config["id"],
                "name": self.kb_config["name"],
                "source": self.kb_config["source"],
                "indexType": "best",
                "createdAt": self.manifest.data["createdAt"],
                "lastIndexed": self.manifest.data["lastIndexed"] or self.manifest.data["createdAt"],
                "fileCount": len(set(m["file"] for m in self._metadata)),
                "chunkCount": len(self._chunks),
                "embeddingModel": "all-minilm-l6-v2",
                "embeddingDimension": 384
            }]
        }

        with open(contexts_json, 'w') as f:
            json.dump(contexts_data, f, indent=2)

        # Save data.json with embeddings
        data_json_path = self.storage_path / "data.json"
        data = {
            "chunks": [
                {
                    "id": f"chunk-{i:05d}",
                    "content": chunk,
                    "embedding": embedding.tolist(),
                    "metadata": meta
                }
                for i, (chunk, embedding, meta) in enumerate(
                    zip(self._chunks, self._embeddings, self._metadata)
                )
            ],
            "indexMetadata": {
                "model": "all-minilm-l6-v2",
                "dimension": 384,
                "totalChunks": len(self._chunks)
            }
        }

        with open(data_json_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"  ✓ Saved embeddings to {data_json_path}")

    def _load_index(self) -> None:
        """Load embeddings from disk"""
        data_json_path = self.storage_path / "data.json"

        if not data_json_path.exists():
            raise FileNotFoundError(f"Embeddings not found: {data_json_path}")

        with open(data_json_path, 'r') as f:
            data = json.load(f)

        self._chunks = []
        self._embeddings = []
        self._metadata = []

        for chunk_entry in data["chunks"]:
            self._chunks.append(chunk_entry["content"])
            self._embeddings.append(np.array(chunk_entry["embedding"]))
            self._metadata.append(chunk_entry["metadata"])

        self._embeddings = np.array(self._embeddings)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search domain knowledge using semantic similarity.

        Args:
            query: Natural language query
            top_k: Number of results to return

        Returns:
            List of results with content, metadata, and similarity score
        """
        # Lazy load index and model
        if self._embeddings is None:
            self._load_index()

        if self._model is None:
            self._load_model()

        # Encode query
        query_embedding = self._model.encode([query])[0]

        # Compute cosine similarities
        similarities = np.dot(self._embeddings, query_embedding) / (
            np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top K
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                results.append({
                    "content": self._chunks[idx],
                    "similarity": float(similarities[idx]),
                    "metadata": self._metadata[idx]
                })

        return results

    def ingest(self, content: str, source: str = "runtime") -> None:
        """Add a document to the live index without restart."""
        if self._embeddings is None:
            self._load_index()
        if self._model is None:
            self._load_model()

        embedding = self._model.encode([content])[0]
        metadata = {"file": source, "type": "runtime_ingested"}

        self._chunks.append(content)
        self._metadata.append(metadata)
        self._embeddings = np.vstack([self._embeddings, embedding])
