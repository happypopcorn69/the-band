#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
SubagentStop Hook - Sub-agent Completion Monitoring

This hook fires when a sub-agent (Task tool) is about to finish.
Can be used to:
- Log sub-agent completions
- Verify sub-agent task completion
- Coordinate multi-agent workflows
- Prevent premature sub-agent stops

Exit codes:
- 0: Allow sub-agent to stop
- 2: Block sub-agent from stopping (shows error to sub-agent)
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
LOG_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "logs"
SUBAGENT_LOG = LOG_DIR / "subagent_completions.jsonl"


def ensure_log_dir():
    """Create log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_subagent_completion(session_id: str, data: dict):
    """Log sub-agent completion events."""
    ensure_log_dir()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "event": "subagent_stop",
        "data": data
    }
    
    with open(SUBAGENT_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def main():
    """Main hook handler."""
    try:
        input_data = json.loads(sys.stdin.read())
        
        session_id = input_data.get("session_id", "unknown")
        
        # Log the sub-agent completion
        log_subagent_completion(session_id, input_data)
        
        # Allow sub-agent to complete
        # To block: print error to stderr and sys.exit(2)
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
