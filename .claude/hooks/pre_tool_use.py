#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
PreToolUse Hook - Security and Safety Filter

This hook runs before any tool execution and can block dangerous commands.
Exit codes:
- 0: Allow the tool to proceed
- 2: Block the tool and provide feedback to Claude
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Dangerous patterns to block
DANGEROUS_BASH_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf /*",
    "> /dev/sda",
    "mkfs.",
    "dd if=/dev/zero",
    ":(){:|:&};:",  # Fork bomb
    "chmod -R 777 /",
    "curl | sh",
    "wget | sh",
    "curl | bash",
    "wget | bash",
]

# Sensitive files to protect
PROTECTED_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "secrets.json",
    "credentials.json",
    ".aws/credentials",
    ".ssh/",
    "id_rsa",
    "id_ed25519",
]

# Log directory
LOG_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "logs"


def ensure_log_dir():
    """Create log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, data: dict):
    """Log hook events for debugging."""
    ensure_log_dir()
    log_file = LOG_DIR / "pre_tool_use.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def is_dangerous_bash(command: str) -> tuple[bool, str]:
    """Check if a bash command is dangerous."""
    command_lower = command.lower()
    
    for pattern in DANGEROUS_BASH_PATTERNS:
        if pattern.lower() in command_lower:
            return True, f"Blocked dangerous pattern: {pattern}"
    
    return False, ""


def is_sensitive_file(file_path: str) -> tuple[bool, str]:
    """Check if accessing a sensitive file."""
    for protected in PROTECTED_FILES:
        if protected in file_path:
            return True, f"Attempted access to sensitive file: {protected}"
    
    return False, ""


def evaluate_tool(tool_name: str, tool_input: dict) -> dict:
    """Evaluate if a tool call should be allowed."""
    
    # Check Bash commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        is_dangerous, reason = is_dangerous_bash(command)
        if is_dangerous:
            return {
                "decision": "block",
                "reason": f"🚫 Security: {reason}. Please use a safer alternative."
            }
    
    # Check file access
    if tool_name in ["Read", "Write", "Edit"]:
        file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        is_sensitive, reason = is_sensitive_file(file_path)
        if is_sensitive:
            return {
                "decision": "block", 
                "reason": f"🔒 Security: {reason}. This file contains sensitive data."
            }
    
    # Allow by default
    return {"decision": "allow"}


def main():
    """Main hook handler."""
    try:
        # Read hook input from stdin
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        
        # Log the event
        log_event("pre_tool_use", {
            "tool_name": tool_name,
            "tool_input": tool_input
        })
        
        # Evaluate the tool call
        result = evaluate_tool(tool_name, tool_input)
        
        if result.get("decision") == "block":
            log_event("blocked", {
                "tool_name": tool_name,
                "reason": result.get("reason")
            })
            # Print reason to stderr (shown to Claude)
            print(result.get("reason"), file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks the tool
        
        # Allow the tool to proceed
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on parse errors
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on unexpected errors


if __name__ == "__main__":
    main()
