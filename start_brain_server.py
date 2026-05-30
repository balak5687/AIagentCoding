#!/usr/bin/env python3
"""
Start the Project Brain Server as a background process.
Loads indexes once, then serves agents via HTTP on :7433.

Usage:
    python start_brain_server.py              # foreground
    python start_brain_server.py --daemon     # background (nohup)
"""
import sys
import os
import argparse
from pathlib import Path

MANIFEST = ".project-brain/manifest.yaml"
PID_FILE = ".project-brain/brain_server.pid"
LOG_FILE = ".project-brain/brain_server.log"
PORT = 7433


def start_foreground(debug=False):
    from src.brain.server import run_server
    run_server(MANIFEST, port=PORT, debug=debug)


def start_daemon():
    """Start as background daemon process"""
    pid = os.fork()
    if pid > 0:
        # Parent — write PID and exit
        Path(PID_FILE).write_text(str(pid))
        print(f"🧠 Brain Server started (PID {pid})")
        print(f"   URL:  http://127.0.0.1:{PORT}")
        print(f"   Log:  {LOG_FILE}")
        print(f"   PID:  {PID_FILE}")
        print(f"\n   Stop: python start_brain_server.py --stop")
        sys.exit(0)

    # Child — redirect stdout/stderr to log file
    with open(LOG_FILE, 'w') as log:
        os.dup2(log.fileno(), sys.stdout.fileno())
        os.dup2(log.fileno(), sys.stderr.fileno())

    from src.brain.server import run_server
    run_server(MANIFEST, port=PORT, debug=False)


def stop_daemon():
    if not Path(PID_FILE).exists():
        print("Brain Server is not running (no PID file)")
        return

    pid = int(Path(PID_FILE).read_text().strip())
    try:
        os.kill(pid, 15)  # SIGTERM
        Path(PID_FILE).unlink()
        print(f"🛑 Brain Server stopped (PID {pid})")
    except ProcessLookupError:
        print(f"Process {pid} not found — already stopped")
        Path(PID_FILE).unlink(missing_ok=True)


def check_status():
    from src.brain import client as brain_client
    if brain_client.is_running():
        s = brain_client.status()
        print(f"✅ Brain Server is running on port {PORT}")
        print(f"   Project: {s.get('project')}")
        print(f"   Coding Brain: {s.get('coding_files')} files")
        print(f"   Functionality Brain: {s.get('functionality_chunks')} chunks")
        print(f"   Last Indexed: {s.get('last_indexed')}")
    else:
        print(f"❌ Brain Server is not running on port {PORT}")
        print(f"   Start with: python start_brain_server.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project Brain Server")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--stop", action="store_true", help="Stop background daemon")
    parser.add_argument("--status", action="store_true", help="Check server status")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.stop:
        stop_daemon()
    elif args.status:
        check_status()
    elif args.daemon:
        start_daemon()
    else:
        start_foreground(debug=args.debug)
