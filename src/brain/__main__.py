"""
Project Brain CLI - Initialize and manage the Project Brain system.

Usage:
    python -m src.brain init --project GreasyNuts --issue 3
    python -m src.brain status
    python -m src.brain query "dashboard requirements"
"""
import argparse
import sys
from pathlib import Path
from .base import ProjectBrain
from .query_interface import BrainQueryInterface


def cmd_init(args):
    """Initialize Project Brain"""
    print("🧠 Initializing Project Brain...\n")

    # Get paths from config or use defaults
    if args.config:
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        backend_path = config['projects']['backend']['path']
        frontend_path = config['projects']['frontend']['path']
        branch = config['projects']['backend']['branch']
    else:
        backend_path = args.backend
        frontend_path = args.frontend
        branch = args.branch or "main"

    # Create Project Brain
    brain_root = Path(args.brain_root or ".project-brain")

    if brain_root.exists() and not args.force:
        print(f"❌ Brain already exists at {brain_root}")
        print(f"   Use --force to reinitialize")
        return 1

    brain = ProjectBrain.create_new(
        brain_root=brain_root,
        project_name=args.project,
        backend_path=backend_path,
        frontend_path=frontend_path,
        branch=branch,
        test_issue=args.issue
    )

    print(f"✅ Project Brain created at {brain_root}\n")

    # Index Coding Brain
    print("=" * 80)
    print("PHASE 1: Indexing Coding Brain (BM25)")
    print("=" * 80)

    file_count, chunk_count = brain.coding.index_codebase(
        backend_path=backend_path,
        frontend_path=frontend_path if args.include_frontend else None
    )

    print(f"\n✅ Coding Brain: {file_count} files, {chunk_count} chunks indexed\n")

    # Index Functionality Brain
    print("=" * 80)
    print("PHASE 2: Indexing Functionality Brain (Semantic)")
    print("=" * 80)

    file_count, chunk_count = brain.functionality.index_knowledge(
        repo_name=args.repo if args.repo else None,
        issue_number=args.issue
    )

    print(f"\n✅ Functionality Brain: {file_count} files, {chunk_count} chunks indexed\n")

    # Summary
    print("=" * 80)
    print("✅ PROJECT BRAIN INITIALIZED")
    print("=" * 80)
    print(f"Location: {brain_root}")
    print(f"Manifest: {brain_root / 'manifest.yaml'}")
    print(f"\nTo query the brain:")
    print(f"  python -m src.brain query \"your question\"")
    print(f"\nTo check status:")
    print(f"  python -m src.brain status")

    return 0


def cmd_status(args):
    """Show Project Brain status"""
    brain_root = Path(args.brain_root or ".project-brain")
    manifest_path = brain_root / "manifest.yaml"

    if not manifest_path.exists():
        print(f"❌ No brain found at {brain_root}")
        print(f"   Run: python -m src.brain init")
        return 1

    brain = ProjectBrain.load(str(manifest_path))

    print("🧠 Project Brain Status\n")
    print("=" * 80)

    # Basic info
    manifest = brain.manifest.data
    print(f"Project: {manifest['project']}")
    print(f"Issue: #{manifest['testIssue']}")
    print(f"Created: {manifest['createdAt']}")
    print(f"Last Indexed: {manifest['lastIndexed']}")

    print("\n" + "=" * 80)
    print("Knowledge Bases:")
    print("=" * 80)

    for kb_name, kb_config in manifest['knowledgeBases'].items():
        print(f"\n{kb_config['name']}:")
        print(f"  Type: {kb_config['indexType']}")
        print(f"  Files: {kb_config['fileCount']}")
        print(f"  Chunks: {kb_config['chunkCount']}")
        print(f"  Source: {kb_config['source']}")

    print("\n" + "=" * 80)
    print("Agents:")
    print("=" * 80)

    for agent_name, agent_config in manifest['agents'].items():
        print(f"\n{agent_name}:")
        print(f"  Knowledge Bases: {', '.join(agent_config['knowledgeBases'])}")

    return 0


def cmd_query(args):
    """Query the Project Brain"""
    brain_root = Path(args.brain_root or ".project-brain")
    manifest_path = brain_root / "manifest.yaml"

    if not manifest_path.exists():
        print(f"❌ No brain found at {brain_root}")
        return 1

    interface = BrainQueryInterface.for_agent(
        str(manifest_path),
        args.agent or "designer"
    )

    print(f"🔍 Querying as '{args.agent or 'designer'}' agent:\n")
    print(f"Query: \"{args.query}\"\n")
    print("=" * 80)

    if args.type == "code":
        results = interface.search_code(args.query, top_k=args.top_k)
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['file']} (score: {r['score']:.2f})")
            print(f"   {r['content'][:200]}...")

    elif args.type == "knowledge":
        results = interface.search_knowledge(args.query, top_k=args.top_k)
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['metadata']['file']} (similarity: {r['similarity']:.3f})")
            print(f"   {r['content'][:200]}...")

    else:  # auto
        results = interface.auto_query(args.query, top_k=args.top_k)
        for i, r in enumerate(results, 1):
            if 'file' in r:  # Code result
                print(f"\n{i}. [CODE] {r['file']} (score: {r.get('score', 0):.2f})")
            else:  # Knowledge result
                print(f"\n{i}. [KNOWLEDGE] {r['metadata']['file']} (similarity: {r.get('similarity', 0):.3f})")
            content = r.get('content', '')
            print(f"   {content[:200]}...")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Project Brain - Knowledge management for multi-agent SDLC"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize Project Brain')
    init_parser.add_argument('--project', required=True, help='Project name')
    init_parser.add_argument('--backend', help='Backend path')
    init_parser.add_argument('--frontend', help='Frontend path')
    init_parser.add_argument('--branch', help='Git branch (default: main)')
    init_parser.add_argument('--issue', type=int, required=True, help='GitHub issue number')
    init_parser.add_argument('--repo', help='GitHub repo (owner/repo)')
    init_parser.add_argument('--config', help='Path to config.yaml')
    init_parser.add_argument('--brain-root', help='Brain root directory (default: .project-brain)')
    init_parser.add_argument('--force', action='store_true', help='Force reinitialize')
    init_parser.add_argument('--include-frontend', action='store_true', default=True, help='Include frontend in indexing')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show Project Brain status')
    status_parser.add_argument('--brain-root', help='Brain root directory')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the Project Brain')
    query_parser.add_argument('query', help='Query string')
    query_parser.add_argument('--agent', default='designer', help='Agent name (default: designer)')
    query_parser.add_argument('--type', choices=['code', 'knowledge', 'auto'], default='auto', help='Query type')
    query_parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    query_parser.add_argument('--brain-root', help='Brain root directory')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'init':
        return cmd_init(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'query':
        return cmd_query(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
