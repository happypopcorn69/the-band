# Create Agent Command

Dynamically create new specialized sub-agents using the meta-agent architect.

## What This Command Does

Invokes the `meta-agent` to generate a complete, production-ready sub-agent configuration file based on your description.

## Instructions

Invoke the `meta-agent` (model: opus) with:

> Create a new Claude Code sub-agent based on this description: $ARGUMENTS
>
> Requirements:
> 1. Generate a complete agent configuration file
> 2. Use kebab-case naming convention
> 3. Write an action-oriented description for auto-delegation
> 4. Select minimal required tools for the task
> 5. Default to opus model unless speed is critical
> 6. Include comprehensive instructions
> 7. Define clear output format
> 8. Save to .claude/agents/<agent-name>.md
>
> Confirm the agent was created and explain how to invoke it.

## Usage

```
/create-agent [description of the agent you need]
```

## Examples

```
/create-agent security auditor that scans for vulnerabilities and OWASP issues
/create-agent API documentation generator that creates OpenAPI specs
/create-agent database migration specialist for PostgreSQL
/create-agent performance profiler for React applications
/create-agent test coverage analyzer that identifies gaps
/create-agent accessibility auditor for WCAG compliance
```

## After Creation

Once the agent is created:

1. It's immediately available for use
2. Can be invoked directly or by the planning-agent
3. Can be referenced in other commands
4. Configuration is in `.claude/agents/<name>.md`

## Modifying Agents

To modify an existing agent:
- Edit the file directly in `.claude/agents/`
- Or run `/create-agent` with updated requirements

## Tips for Good Agent Descriptions

- Be specific about the domain and use case
- Mention key technologies or frameworks
- Describe expected outputs
- Note any integration requirements
- Specify if speed (haiku/sonnet) vs quality (opus) matters
