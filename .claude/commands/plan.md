# Plan Command

Generate a comprehensive implementation plan with sub-agent orchestration for complex features.

## What This Command Does

Invokes the `planning-agent` to create a detailed, executable plan that:

1. Decomposes the task into atomic work units
2. Assigns work to specialized agents (frontend-engineer, backend-engineer)
3. Maximizes parallel execution where possible
4. Includes mandatory quality checkpoints
5. Specifies opus model for all sub-agents

## Instructions

Invoke the `planning-agent` (model: opus) with:

> Create a comprehensive implementation plan for: $ARGUMENTS
>
> Requirements:
> 1. Break down into phases with clear deliverables
> 2. Assign tasks to appropriate specialized agents:
>    - frontend-engineer (opus) for UI/component work
>    - backend-engineer (opus) for API/database work
> 3. Identify parallelization opportunities
> 4. Include mandatory review checkpoints after each phase:
>    - principal-engineer-reviewer for code review
>    - completeness-checker before final completion
> 5. ALL sub-agents must use opus model
> 6. Document dependencies between tasks
> 7. Define clear success criteria
>
> Output a structured plan that can be executed autonomously with quality gates.

## Plan Structure Expected

The planning-agent will produce:

```
# Implementation Plan: [Feature Name]

## Overview
## Dependency Graph  
## Phase 1: [Foundation]
   - Parallel tasks with agent assignments
   - Checkpoint 1 (principal-engineer-reviewer)
## Phase 2: [Core Implementation]
   - Tasks with agent assignments
   - Checkpoint 2 (both reviewers)
## Phase 3: [Integration]
   - Final tasks
   - Final Review (mandatory)
## Success Criteria
```

## Usage

```
/plan [feature description]
```

## Examples

```
/plan user authentication with OAuth and MFA
/plan e-commerce checkout flow with payment integration
/plan real-time notification system with WebSocket support
/plan admin dashboard with role-based access control
```

## Execution Notes

After the plan is generated:

1. **Review the plan** for completeness and accuracy
2. **Execute phases** in order, respecting dependencies
3. **Run checkpoints** - these are MANDATORY, not optional
4. **Address issues** from reviews before proceeding
5. **Complete final review** before marking done

## Pro Tips

- Be specific in your feature description for better plans
- Include technical constraints if relevant
- Mention existing systems to integrate with
- The plan can be iterated - ask for adjustments if needed
