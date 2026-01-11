# Claude Code Multi-Agent System

A comprehensive multi-agent orchestration system for Claude Code, featuring specialized domain agents, automated code review, intelligent planning, and autonomous decision-making hooks.

## 🎯 Overview

This system implements the principles from [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery), providing:

- **Specialized Agents**: Frontend and backend engineers for domain-specific tasks
- **Review Pipeline**: Principal engineer + completeness checker for quality gates
- **Planning Agent**: Orchestrates sub-agents with parallelization and checkpoints
- **Autonomous Hooks**: Reduces manual intervention through intelligent auto-approval
- **Slash Commands**: Easy invocation of review and planning workflows

## 📁 Structure

```
.claude/
├── agents/
│   ├── frontend-engineer.md      # React/Vue/TypeScript specialist
│   ├── backend-engineer.md       # API/Database/Auth specialist
│   ├── principal-engineer-reviewer.md  # Code review expert
│   ├── completeness-checker.md   # Finds placeholders, TODOs, gaps
│   ├── planning-agent.md         # Orchestration & planning
│   └── meta-agent.md             # Creates new agents dynamically
├── commands/
│   ├── review.md                 # /review - Two-stage quality check
│   ├── plan.md                   # /plan - Generate implementation plans
│   └── create-agent.md           # /create-agent - Dynamic agent creation
├── hooks/
│   ├── user_prompt_submit.py     # Prompt logging & validation
│   ├── pre_tool_use.py           # Security filtering
│   ├── post_tool_use.py          # Tool result logging
│   ├── permission_request.py     # Autonomous approval decisions
│   ├── stop.py                   # Completion verification
│   └── subagent_stop.py          # Sub-agent monitoring
├── logs/                         # Auto-generated logs
└── settings.json                 # Hook configuration
```

## 🚀 Quick Start

### 1. Copy to Your Project

```bash
# Clone or copy the .claude directory to your project root
cp -r .claude /path/to/your/project/
```

### 2. Install Dependencies

```bash
# Install uv for Python script execution
curl -LsSf https://astral.sh/uv/install.sh | sh

# Optional: For LLM-based permission decisions
pip install anthropic
```

### 3. Set Environment Variables (Optional)

```bash
# For autonomous permission decisions
export ANTHROPIC_API_KEY="your-key-here"

# Compliance level: strict | moderate | permissive
export CLAUDE_COMPLIANCE_LEVEL="moderate"
```

### 4. Start Using

```bash
# Navigate to your project
cd /path/to/your/project

# Start Claude Code
claude

# Use the commands
/plan user authentication with OAuth
/review authentication implementation
/create-agent API rate limiter specialist
```

## 🤖 Agents

### Domain Specialists

| Agent | Model | Use For |
|-------|-------|---------|
| `frontend-engineer` | opus | React, Vue, TypeScript, CSS, components |
| `backend-engineer` | opus | APIs, databases, authentication, servers |

### Quality Assurance

| Agent | Model | Use For |
|-------|-------|---------|
| `principal-engineer-reviewer` | opus | Code review, architecture, patterns |
| `completeness-checker` | opus | Finding TODOs, placeholders, gaps |

### Orchestration

| Agent | Model | Use For |
|-------|-------|---------|
| `planning-agent` | opus | Complex task planning, sub-agent coordination |
| `meta-agent` | opus | Creating new agents dynamically |

## 📜 Slash Commands

### `/review [feature]`

Triggers a two-stage review:
1. **Principal Engineer Review**: Architecture, code quality, security
2. **Completeness Check**: Placeholders, mocks, TODOs, gaps

```bash
/review user authentication flow
/review the new dashboard components
```

### `/plan [feature]`

Generates a comprehensive implementation plan:
- Breaks down into phases
- Assigns to specialized agents
- Maximizes parallelization
- Includes mandatory review checkpoints

```bash
/plan e-commerce checkout with payments
/plan real-time notification system
```

### `/create-agent [description]`

Dynamically creates new specialized agents:

```bash
/create-agent security auditor for OWASP vulnerabilities
/create-agent API documentation generator
```

## 🔧 Hooks

### Hook Lifecycle

1. **UserPromptSubmit**: Logs prompts, validates input
2. **PreToolUse**: Blocks dangerous commands
3. **PostToolUse**: Logs tool results, tracks changes
4. **PermissionRequest**: Auto-approves safe operations
5. **Stop**: Verifies task completion
6. **SubagentStop**: Monitors sub-agent completion

### Compliance Levels

Set via `CLAUDE_COMPLIANCE_LEVEL`:

| Level | Behavior |
|-------|----------|
| `strict` | Manual approval for most operations |
| `moderate` | Auto-approve safe patterns (default) |
| `permissive` | Use LLM for uncertain decisions |

### Security Features

The `pre_tool_use.py` hook blocks:
- Destructive commands (`rm -rf /`, fork bombs)
- Access to sensitive files (`.env`, credentials)
- Dangerous shell patterns

## 📊 Logs

All hooks log to `.claude/logs/`:

- `prompts.jsonl` - All user prompts
- `tool_usage.jsonl` - Tool execution details
- `permission_request.jsonl` - Permission decisions
- `completions.jsonl` - Session completions
- `file_changes.jsonl` - File modification tracking
- `agent_invocations.jsonl` - Agent usage patterns

## 🔄 Workflow Example

### Feature Implementation Workflow

```bash
# 1. Plan the feature
/plan user profile with avatar upload

# Claude generates plan with phases, agent assignments, checkpoints

# 2. Execute the plan
# Planning agent orchestrates:
# - frontend-engineer creates components
# - backend-engineer creates API endpoints
# - Both run in parallel where possible

# 3. Checkpoint review
# After each phase:
# - principal-engineer-reviewer checks code
# - Address any critical issues

# 4. Final review
/review user profile feature
# - Principal engineer does final review
# - Completeness checker finds any gaps
```

## ⚙️ Customization

### Adding New Agents

1. Create `.claude/agents/<name>.md`
2. Use frontmatter format:
```yaml
---
name: your-agent
description: Use proactively for...
tools: Read, Write, Edit
model: opus
color: blue
---

# Purpose
...
```

Or use: `/create-agent [description]`

### Modifying Hooks

Edit files in `.claude/hooks/`:
- Change security patterns in `pre_tool_use.py`
- Adjust auto-approval logic in `permission_request.py`
- Add custom logging in `post_tool_use.py`

### Adjusting Permissions

Edit `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": ["pattern:*"],
    "deny": ["dangerous:*"]
  }
}
```

## 🎓 Best Practices

1. **Always use `/review` after features** - Catches issues early
2. **Use `/plan` for complex tasks** - Better coordination and parallelization
3. **Start with `moderate` compliance** - Balance autonomy and control
4. **Monitor logs** - Understand patterns and improve workflows
5. **Create domain agents** - Specialized agents produce better results
6. **All sub-agents use opus** - Quality over speed for sub-tasks

## 🔐 Security Considerations

- Hooks run with your environment credentials
- Review hook code before enabling
- Sensitive files are protected by default
- Use `strict` mode for sensitive projects
- Check logs for suspicious activity

## 📚 Resources

- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
- [Sub-Agents Documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Original Inspiration](https://github.com/disler/claude-code-hooks-mastery)

## 📝 License

MIT - Use freely, modify as needed.
