#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Stop Hook - Task Completion Verification

This hook fires when Claude is about to stop responding.
Can be used to:
- Verify task completion
- Trigger final reviews
- Send notifications
- Generate completion summaries

Exit codes:
- 0: Allow Claude to stop
- 0 with {"decision": "block"}: Prevent stopping, provide feedback
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
LOG_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "logs"
COMPLETION_LOG = LOG_DIR / "completions.jsonl"

# Keywords that suggest incomplete work
INCOMPLETE_INDICATORS = [
    "TODO",
    "FIXME", 
    "not implemented",
    "placeholder",
    "will implement",
    "need to add",
    "coming soon",
    "later",
    "skip for now",
]


def ensure_log_dir():
    """Create log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_completion(session_id: str, reason: str, data: dict):
    """Log completion events."""
    ensure_log_dir()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "stop_reason": reason,
        "data": data
    }
    
    with open(COMPLETION_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def check_recent_files_for_incomplete() -> list[str]:
    """Check recently modified files for incomplete indicators."""
    issues = []
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    
    # Check files modified in the last hour (rough heuristic)
    try:
        import subprocess
        result = subprocess.run(
            ["find", str(project_dir), "-type", "f", "-mmin", "-60", 
             "-not", "-path", "*/.git/*", "-not", "-path", "*/node_modules/*"],
            capture_output=True, text=True
        )
        
        recent_files = result.stdout.strip().split("\n")
        
        for file_path in recent_files[:20]:  # Check up to 20 files
            if not file_path or not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                    
                for indicator in INCOMPLETE_INDICATORS:
                    if indicator.lower() in content.lower():
                        issues.append(f"{file_path}: contains '{indicator}'")
                        break
            except:
                pass
                
    except Exception as e:
        pass  # Don't block on errors
    
    return issues


def main():
    """Main hook handler."""
    try:
        input_data = json.loads(sys.stdin.read())
        
        session_id = input_data.get("session_id", "unknown")
        reason = input_data.get("reason", "unknown")
        
        # Log the stop event
        log_completion(session_id, reason, input_data)
        
        # Optional: Check for incomplete work
        # Uncomment to enable blocking on incomplete indicators
        """
        incomplete_issues = check_recent_files_for_incomplete()
        if incomplete_issues:
            result = {
                "decision": "block",
                "reason": f"Found potentially incomplete work:\\n" + 
                          "\\n".join(incomplete_issues[:5]) +
                          "\\n\\nPlease address these before completing."
            }
            print(json.dumps(result))
            sys.exit(0)
        """
        
        # Allow stop by default
        print(json.dumps({
            "continue": True,
            "suppressOutput": True
        }))
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
