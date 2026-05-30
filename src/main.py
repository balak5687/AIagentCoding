import asyncio
import argparse
from pathlib import Path
import sys
from .core.config import Config
from .core.agent_runner import AgentRunner
from .core.orchestrator import SDLCOrchestrator


async def main_async(args):
    """Async main function"""
    # Load configuration
    config_path = args.config if Path(args.config).exists() else "config/config.yaml.example"

    try:
        config = Config.load(config_path)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        print("Please create a config.yaml file based on config/config.yaml.example")
        sys.exit(1)

    if args.debug:
        config.debug = True

    # Initialize runner
    runner = AgentRunner(mode=config.mode, config=vars(config))

    # Initialize orchestrator
    orchestrator = SDLCOrchestrator(runner, config)

    # Process GitHub issue
    print(f"Processing GitHub issue: {args.issue}")
    print(f"Mode: {config.mode}")
    print()

    try:
        result = await orchestrator.process_github_issue(args.issue)

        print(f"\n{'='*60}")
        print(f"RESULT")
        print(f"{'='*60}")
        print(f"Status: {result['status']}")

        if result['status'] == 'success':
            print(f"Tasks completed: {result.get('tasks_completed', 0)}")
            if 'pr_url' in result:
                print(f"PR URL: {result['pr_url']}")
            if 'deployment_url' in result:
                print(f"Deployment: {result['deployment_url']}")
        else:
            print(f"Reason: {result.get('reason', 'Unknown')}")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR")
        print(f"{'='*60}")
        print(f"{type(e).__name__}: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Agent SDLC System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--issue",
        required=True,
        help="GitHub issue URL or description"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Config file path (default: config.yaml)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    # Run async main
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
