# AGENTS.md

## Code Quality

- Write clear, self-documenting code with meaningful names
- Keep functions small and focused on a single responsibility
- Add comments only when explaining *why*, not *what*
- Follow existing patterns and conventions in the codebase
- Remove dead code rather than commenting it out

## Making Changes

- Read and understand existing code before modifying
- Make minimal, targeted changes that solve the specific problem
- Preserve existing formatting and style conventions
- Update tests when changing functionality
- Run linters and tests before considering work complete
- Always use type hinting when applicable

## Testing

- Write tests that verify behavior, not implementation details
- Cover edge cases and error conditions
- Keep tests independent and deterministic
- Maintain existing test coverage levels

## Security

- Never hardcode secrets, credentials, or API keys
- Use environment variables for configuration
- Validate and sanitize all inputs
- Follow the principle of least privilege

## Problem Solving

- Identify root causes before implementing fixes
- Prefer simple solutions over clever ones
- Ask clarifying questions when requirements are ambiguous
- Document assumptions and decisions

## Agent skills

### Issue tracker

Issues and PRDs are always created in GitHub Issues for this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default mattpocock/skills triage label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This is a multi-context monorepo with a root `CONTEXT-MAP.md` pointing to subsystem context files. See `docs/agents/domain.md`.
