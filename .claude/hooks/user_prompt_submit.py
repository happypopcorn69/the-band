#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
UserPromptSubmit Hook - Prompt Logging and Enhancement

This hook fires when a user submits a prompt, before Claude processes it.
Uses for:
- Logging all prompts for analysis
- Storing the last prompt for reference
- Validating prompt content
- Injecting context

Exit codes:
- 0: Continue processing
- 2: Block the prompt (with error message)
"""

import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
LOG_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "logs"
LAST_PROMPT_FILE = LOG_DIR / "last_prompt.txt"
PROMPT_LOG_FILE = LOG_DIR / "prompts.jsonl"


def ensure_log_dir():
    """Create log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_prompt(prompt: str, session_id: str):
    """Log the prompt to a JSONL file."""
    ensure_log_dir()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "prompt": prompt,
        "length": len(prompt)
    }
    
    with open(PROMPT_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def store_last_prompt(prompt: str):
    """Store the last prompt for reference."""
    ensure_log_dir()
    
    with open(LAST_PROMPT_FILE, "w") as f:
        f.write(prompt)


def detect_agent_invocation(prompt: str) -> str | None:
    """Detect if prompt is invoking a specific agent."""
    prompt_lower = prompt.lower()
    
    agent_triggers = {
        "frontend-engineer": ["frontend", "react", "vue", "component", "css", "ui"],
        "backend-engineer": ["backend", "api", "database", "endpoint", "server"],
        "principal-engineer-reviewer": ["review", "code review"],
        "completeness-checker": ["check complete", "find placeholders", "find todos"],
        "planning-agent": ["plan", "implement feature", "build"],
    }
    
    for agent, triggers in agent_triggers.items():
        for trigger in triggers:
            if trigger in prompt_lower:
                return agent
    
    return None


def validate_prompt(prompt: str) -> tuple[bool, str]:
    """Validate prompt content."""
    
    # Check for empty prompts
    if not prompt or not prompt.strip():
        return False, "Empty prompt received"
    
    # Check for extremely long prompts (potential abuse)
    if len(prompt) > 100000:
        return False, "Prompt exceeds maximum length (100k characters)"
    
    return True, ""


def main():
    """Main hook handler."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-only", action="store_true", help="Only log, don't modify")
    parser.add_argument("--store-last-prompt", action="store_true", help="Store last prompt")
    parser.add_argument("--name-agent", action="store_true", help="Detect and name agent")
    args = parser.parse_args()
    
    try:
        input_data = json.loads(sys.stdin.read())
        
        prompt = input_data.get("prompt", "")
        session_id = input_data.get("session_id", "unknown")
        
        # Validate prompt
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            print(error_msg, file=sys.stderr)
            sys.exit(2)  # Block invalid prompts
        
        # Log the prompt
        log_prompt(prompt, session_id)
        
        # Store last prompt if requested
        if args.store_last_prompt:
            store_last_prompt(prompt)
        
        # Detect agent invocation if requested
        if args.name_agent:
            detected_agent = detect_agent_invocation(prompt)
            if detected_agent:
                # Log which agent was detected
                ensure_log_dir()
                with open(LOG_DIR / "agent_invocations.jsonl", "a") as f:
                    f.write(json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "session_id": session_id,
                        "detected_agent": detected_agent,
                        "prompt_preview": prompt[:100]
                    }) + "\n")
        
        # Continue processing
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
