#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
PostToolUse Hook - Tool Result Logging

This hook fires after a tool successfully completes.
Uses for:
- Logging tool results
- Monitoring file changes
- Triggering follow-up actions
- Extracting chat transcripts

Exit codes:
- 0: Continue normally
- 2: Provide feedback to Claude (won't block, but Claude sees it)
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
LOG_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "logs"
TOOL_LOG = LOG_DIR / "tool_usage.jsonl"


def ensure_log_dir():
    """Create log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_tool_use(tool_name: str, tool_input: dict, tool_response: str, session_id: str):
    """Log tool usage to JSONL file."""
    ensure_log_dir()
    
    # Truncate large responses for logging
    response_preview = tool_response[:500] if len(tool_response) > 500 else tool_response
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "response_length": len(tool_response),
        "response_preview": response_preview
    }
    
    with open(TOOL_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def track_file_changes(tool_name: str, tool_input: dict):
    """Track file modifications for review purposes."""
    if tool_name in ["Write", "Edit", "MultiEdit"]:
        ensure_log_dir()
        changes_file = LOG_DIR / "file_changes.jsonl"
        
        file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": tool_name,
            "file": file_path
        }
        
        with open(changes_file, "a") as f:
            f.write(json.dumps(change_entry) + "\n")


def main():
    """Main hook handler."""
    try:
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", "")
        session_id = input_data.get("session_id", "unknown")
        
        # Log the tool usage
        log_tool_use(tool_name, tool_input, tool_response, session_id)
        
        # Track file changes
        track_file_changes(tool_name, tool_input)
        
        # Continue normally
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
