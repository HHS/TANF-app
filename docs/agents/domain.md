# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root for repo-wide product and system language.
- **`CONTEXT-MAP.md`** at the repo root to find subsystem-specific context files.
- **Subsystem `CONTEXT.md` files** for each area involved in the change.
- **`docs/Technical-Documentation/`** if it exists for system-wide decisions.
- **`<subsystem>/docs/adr/`** if it exists for context-specific decisions.

If any ADR directory does not exist, proceed silently. Do not flag its absence or suggest creating one upfront. The producer skill (`/grill-with-docs`) creates ADRs lazily when decisions actually get resolved.

## File structure

This repo uses a multi-context layout:

```text
/
├── CONTEXT.md
├── CONTEXT-MAP.md
├── docs/agents/
├── tdrs-backend/
│   ├── CONTEXT.md
│   ├── keycloak/CONTEXT.md
│   └── plg/CONTEXT.md
├── tdrs-services/
│   └── parser/CONTEXT.md
└── tdrs-frontend/
    └── CONTEXT.md
```

## Use the glossary's vocabulary

When your output names a domain concept in an issue title, refactor proposal, hypothesis, or test name, use the term as defined in the relevant `CONTEXT.md`. Do not drift to synonyms the glossary explicitly avoids.

If the concept you need is not in the glossary yet, that is a signal: either you are inventing language the project does not use, or there is a real gap to note for `/grill-with-docs`.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding it.
