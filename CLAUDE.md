# CLAUDE.md

This is a **Hippocampus** knowledge base — an AI-powered system for ingesting raw intel and distilling it into structured, persistent knowledge.

## How this works

- **`project.yml`** — Project configuration (domain, persona, vocabulary). Read this first to understand context.
- **`docs/`** — The knowledge base. Living documents that Claude maintains across sessions.
  - Core docs: `MODEL.md`, `PLAN.md`, `INTEL.md`, `QUESTIONS.md`, `DECISIONS.md`, `PEOPLE.md`, `TASKS.md`
  - `workstreams/` — Detailed tracking for major initiatives (created as complexity grows)
  - `proposals/` — Technical proposals and research docs (created as needed)
- **`.claude/rules/`** — Behavioral rules for Claude. These make the system work — don't modify unless you know what you're doing.
- **`.claude/hooks/`** — Session-start hook that loads the knowledge base into context automatically. Ensures Claude can't skip the initialization read.
- **`.claude/skills/`** — Skills like `/debrief` and `/remsleep` that provide structured workflows.
- **`.claude/user.yml`** — Per-user identity file (gitignored). Created on first session.

## Key principle

The docs ARE the memory. If it's not in the docs, it didn't happen. Every debrief session ends with docs updated.

## Commands

- `/kickoff` — First-run interview about the project. Runs automatically while `project.yml` is still the template default.
- `/debrief` — Process raw meeting notes or intel into the knowledge base
- `/remsleep` — Holistic consolidation: find connections, contradictions, staleness, and tighten coherence across all docs. Run periodically or after a burst of debriefs.
- `/wake` — Full session initialisation: verify the payload, check the slate against live state, sweep PRs and the tracker, recommend one thread
- `/join <thread>` — Light initialisation for an extra agent alongside one that already woke
- Just ask questions — Claude reads the full knowledge base every session
