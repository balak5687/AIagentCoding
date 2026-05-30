#!/usr/bin/env python3
"""
Extract and analyze conversation history from Claude Code history.jsonl
"""
import json
from pathlib import Path
from datetime import datetime

def extract_conversation(history_file, project_path):
    """Extract all conversations for a specific project"""
    conversations = []

    with open(history_file, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('project') == project_path:
                    timestamp = entry.get('timestamp', 0)
                    dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else None
                    conversations.append({
                        'timestamp': dt,
                        'message': entry.get('display', ''),
                        'session_id': entry.get('sessionId', ''),
                        'pasted': entry.get('pastedContents', {})
                    })
            except json.JSONDecodeError:
                continue

    return sorted(conversations, key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)

def main():
    history_file = Path.home() / '.claude' / 'history.jsonl'
    project_path = '/home/ubuntu/bala/AIagentCoding'

    print("="*80)
    print(f"CONVERSATION HISTORY FOR: {project_path}")
    print("="*80)
    print()

    conversations = extract_conversation(history_file, project_path)

    print(f"Total Messages: {len(conversations)}\n")
    print("-"*80)

    for idx, conv in enumerate(conversations, 1):
        timestamp = conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if conv['timestamp'] else 'Unknown'
        print(f"\n[{idx}] {timestamp}")
        print(f"Session: {conv['session_id'][:8]}...")
        print(f"Message: {conv['message']}")
        if conv['pasted']:
            print(f"Pasted Content: {list(conv['pasted'].keys())}")
        print("-"*80)

    # Summary analysis
    print("\n" + "="*80)
    print("CONVERSATION ANALYSIS")
    print("="*80)

    # Extract key themes
    messages = [c['message'] for c in conversations]

    keywords = {
        'playbook': sum(1 for m in messages if 'playbook' in m.lower()),
        'designer': sum(1 for m in messages if 'designer' in m.lower()),
        'agent': sum(1 for m in messages if 'agent' in m.lower()),
        'task': sum(1 for m in messages if 'task' in m.lower()),
        'test': sum(1 for m in messages if 'test' in m.lower()),
        'schema': sum(1 for m in messages if 'schema' in m.lower()),
        'github': sum(1 for m in messages if 'github' in m.lower()),
        'greasynuts': sum(1 for m in messages if 'greasynuts' in m.lower()),
        'brain': sum(1 for m in messages if 'brain' in m.lower()),
        'context': sum(1 for m in messages if 'context' in m.lower()),
    }

    print("\nKey Topics (mentions):")
    for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {keyword}: {count}")

    # Extract task-related messages
    print("\n" + "="*80)
    print("TASK-RELATED MESSAGES")
    print("="*80)
    task_messages = [c for c in conversations if 'task' in c['message'].lower() or 'implement' in c['message'].lower()]
    for conv in task_messages:
        timestamp = conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if conv['timestamp'] else 'Unknown'
        print(f"\n[{timestamp}] {conv['message']}")

    print("\n" + "="*80)

if __name__ == '__main__':
    main()
