#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic",
# ]
# ///
"""
PermissionRequest Hook - Autonomous Decision Making

This hook intercepts permission requests and can auto-approve safe operations
or use an LLM to make intelligent decisions, reducing manual intervention.

Set ANTHROPIC_API_KEY environment variable for LLM-based decisions.

Exit codes:
- 0 with JSON output: Approve or block the request
- 0 without decision: Let user decide
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Log directory
LOG_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / ".claude" / "logs"

# Compliance level: "strict", "moderate", "permissive"
COMPLIANCE_LEVEL = os.environ.get("CLAUDE_COMPLIANCE_LEVEL", "moderate")

# Safe operations that can be auto-approved
SAFE_OPERATIONS = {
    "Read": True,  # Reading files is always safe
    "Glob": True,  # Finding files is safe
    "Grep": True,  # Searching is safe
    "LS": True,    # Listing directories is safe
}

# Operations that need review based on compliance level
MODERATE_APPROVE = {
    "Write": lambda inp: not is_critical_file(inp.get("file_path", "")),
    "Edit": lambda inp: not is_critical_file(inp.get("file_path", "")),
    "Bash": lambda inp: is_safe_bash_command(inp.get("command", "")),
}

# Critical files that always need manual approval
CRITICAL_FILES = [
    "package.json",
    "package-lock.json", 
    "yarn.lock",
    "Cargo.toml",
    "Cargo.lock",
    "requirements.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".github/",
    "Makefile",
    "tsconfig.json",
]

# Safe bash command patterns
SAFE_BASH_PATTERNS = [
    "ls", "cat", "head", "tail", "grep", "find", "echo",
    "pwd", "which", "type", "file", "wc", "sort", "uniq",
    "npm run", "npm test", "npm start", "npm build",
    "yarn run", "yarn test", "yarn start", "yarn build",
    "python -m pytest", "pytest", "python -m unittest",
    "cargo test", "cargo build", "cargo check",
    "git status", "git log", "git diff", "git branch",
]


def ensure_log_dir():
    """Create log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, data: dict):
    """Log permission events."""
    ensure_log_dir()
    log_file = LOG_DIR / "permission_request.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "compliance_level": COMPLIANCE_LEVEL,
        "data": data
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def is_critical_file(file_path: str) -> bool:
    """Check if a file is critical and needs manual review."""
    for pattern in CRITICAL_FILES:
        if pattern in file_path:
            return True
    return False


def is_safe_bash_command(command: str) -> bool:
    """Check if a bash command is safe to auto-approve."""
    command_lower = command.lower().strip()
    
    for safe_pattern in SAFE_BASH_PATTERNS:
        if command_lower.startswith(safe_pattern):
            return True
    
    return False


def evaluate_with_llm(tool_name: str, tool_input: dict) -> dict:
    """Use Claude to evaluate if permission should be granted."""
    try:
        import anthropic
        
        client = anthropic.Anthropic()
        
        prompt = f"""You are a security-conscious permission evaluator for a coding assistant.

Evaluate this tool request:
- Tool: {tool_name}
- Input: {json.dumps(tool_input, indent=2)}

Decide if this should be:
1. APPROVED - Safe operation, proceed automatically
2. BLOCKED - Dangerous operation, deny with explanation
3. REVIEW - Needs human review (uncertain or sensitive)

Consider:
- Could this cause data loss?
- Does it access sensitive files?
- Is it a destructive operation?
- Does it make external network calls?

Respond with JSON only:
{{"decision": "approve|block|review", "reason": "brief explanation"}}
"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Fast model for quick decisions
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text.strip()
        # Extract JSON from response
        if "{" in result_text:
            json_str = result_text[result_text.find("{"):result_text.rfind("}")+1]
            return json.loads(json_str)
        
        return {"decision": "review", "reason": "Could not parse LLM response"}
        
    except ImportError:
        return {"decision": "review", "reason": "Anthropic SDK not available"}
    except Exception as e:
        return {"decision": "review", "reason": f"LLM evaluation error: {str(e)}"}


def make_decision(tool_name: str, tool_input: dict) -> dict:
    """Make a permission decision based on compliance level."""
    
    # Always approve safe operations
    if tool_name in SAFE_OPERATIONS:
        return {
            "decision": "approve",
            "reason": f"Auto-approved: {tool_name} is a safe read-only operation"
        }
    
    # Strict mode: require manual approval for everything else
    if COMPLIANCE_LEVEL == "strict":
        return {"decision": None}  # Let user decide
    
    # Moderate mode: auto-approve known safe patterns
    if COMPLIANCE_LEVEL == "moderate":
        if tool_name in MODERATE_APPROVE:
            checker = MODERATE_APPROVE[tool_name]
            if checker(tool_input):
                return {
                    "decision": "approve", 
                    "reason": f"Auto-approved: {tool_name} matches safe pattern"
                }
    
    # Permissive mode: use LLM for uncertain cases
    if COMPLIANCE_LEVEL == "permissive":
        llm_result = evaluate_with_llm(tool_name, tool_input)
        if llm_result.get("decision") == "approve":
            return {
                "decision": "approve",
                "reason": f"LLM approved: {llm_result.get('reason', 'Safe operation')}"
            }
        elif llm_result.get("decision") == "block":
            return {
                "decision": "block",
                "reason": f"LLM blocked: {llm_result.get('reason', 'Potentially dangerous')}"
            }
    
    # Default: let user decide
    return {"decision": None}


def main():
    """Main hook handler."""
    try:
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        
        # Log the permission request
        log_event("permission_request", {
            "tool_name": tool_name,
            "tool_input": tool_input
        })
        
        # Make decision
        result = make_decision(tool_name, tool_input)
        
        # Log the decision
        log_event("decision", {
            "tool_name": tool_name,
            "decision": result.get("decision"),
            "reason": result.get("reason")
        })
        
        # Output decision if made
        if result.get("decision") is not None:
            print(json.dumps(result))
        
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
