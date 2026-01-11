# Review Command

Spawn two review agents in sequence to perform comprehensive quality assurance on the current implementation.

## What This Command Does

This command triggers a two-stage review process:

1. **Principal Engineer Review** - Architectural and code quality analysis
2. **Completeness Check** - Detection of placeholders, mocks, and gaps

## Instructions

Execute the following two-agent review pipeline:

### Stage 1: Principal Engineer Review

Invoke the `principal-engineer-reviewer` agent (model: opus) with:

> Review all code changes related to: $ARGUMENTS
>
> Focus on:
> - Architecture and design patterns
> - Code quality and consistency
> - Performance implications
> - Security considerations
> - Test coverage
>
> Provide a structured review with severity-categorized findings.

Wait for the review to complete. If there are CRITICAL issues, they should be addressed before proceeding.

### Stage 2: Completeness Check

Invoke the `completeness-checker` agent (model: opus) with:

> Scan the implementation for: $ARGUMENTS
>
> Look for:
> - TODO/FIXME/HACK comments
> - Mock or placeholder data
> - Incomplete implementations
> - Missing error handling
> - Hardcoded values that should be configurable
> - Skipped or empty tests
>
> Provide a detailed completeness report.

### Final Summary

After both agents complete, provide:

1. **Combined Status**: PASS / NEEDS WORK / BLOCKED
2. **Critical Actions**: Numbered list of must-fix items
3. **Recommendations**: Suggested improvements

## Usage

```
/review [feature-name or description of what to review]
```

## Examples

```
/review user authentication flow
/review the new dashboard components
/review recent API changes
```

## Important Notes

- Both review stages MUST complete for a full review
- CRITICAL issues from Stage 1 should be addressed before production
- Completeness check catches things code review might miss
- Use this after every feature implementation
