# AGENTS.md

Entry point for non-Claude coding agents (OpenAI Codex CLI and any other
`AGENTS.md`-aware agent). Codex auto-loads only this file, so it has to carry
the operating model on its own. Claude Code uses `CLAUDE.md` + `.claude/rules/*`
+ a session-start hook instead; both drive the same knowledge base, so this file
points at the shared rules rather than duplicating them, to avoid drift.

If you are Claude Code, ignore this file and use `CLAUDE.md`.

---

## What this repo is

A **Hippocampus** knowledge base: you ingest raw intel (meeting notes, calls,
research, conversations) and distill it into a structured set of living
documents that persist across sessions. The documents ARE the memory. If it is
not in the docs, it did not happen.

Read `README.md` for the full concept and `project.yml` for this instance's
domain, persona, and vocabulary. Read `project.yml` first, every session, before
anything else — it sets who this is for and how concepts are named.

---

## Every session, before responding

The checked-in Codex hook normally loads this context for you. If project hooks
have not been trusted or did not run, do this yourself at the start of the
session:

1. **Read `project.yml`** — domain, persona, owner role, vocabulary overrides.
2. **Read `.claude/user.yml`** — the current user's name and role. It is
   gitignored (per-user). If it is missing, stop and follow the identity flow in
   `.claude/rules/role.md` before doing anything else: ask the user's name and
   role, then create the file.
3. **Read `docs/TASKS.md`** — the `## On Deck` block at the top is the next
   session's slate. Start there.
4. **Read `docs/MODEL.md` in full** — this is the spine, the current mental
   model. It is short by design.
5. **Scan, do not read in full, the rest of the knowledge base.** Open the
   specific doc your task touches; do not pull everything up front:
   - **Hubs (current state):** `MODEL.md`, `PLAN.md`, `QUESTIONS.md`,
     `PEOPLE.md`, and anything under `docs/workstreams/`.
   - **Cold (audit / evidence):** `DECISIONS.md`, `INTEL.md`. Read these only to
     answer "why is the state this way," not as routine session-start reading.

Full rationale is in `.claude/rules/session-start.md`. Load on demand. Do not
re-read whole docs you already have a summary of.

### Before asserting anything

The knowledge base records what was true when it was written. If the domain
touches sources that change between sessions (code repos, live systems, external
data), verify the primary source before making a claim. What is written in a doc
or config and what is actually true can drift. See
`.claude/rules/session-start.md` ("Representation vs reality").

---

## The operating rules

These live in `.claude/rules/`. They are auto-loaded for Claude Code; for you
they are reference files — read the one relevant to what you are doing:

| File | When it applies |
|---|---|
| `role.md` | Identity and per-role write access. Owner has full write; contributors add intel/questions freely but structural changes are confirmed; viewers are read-only. Enforce the tier matching `user.yml`. |
| `session-start.md` | The load-on-demand model above, plus the verify-live-state discipline. |
| `hippocampus-updates.md` | **When to update which doc, inline as work happens** — not batched at session end. Read this before writing to any doc. |
| `doc-publishing.md` | How to write anything shared beyond the owner: concise, human voice, no AI tells, diagrams in Mermaid. |
| `working-method.md` | Standing working guidance for this instance. |
| `key-context.md` | Pointers to the source-of-truth docs. |

The one discipline to internalize: **record as you go.** A decision goes to
`DECISIONS.md` when it is made; a model shift to `MODEL.md`; a new externally
sourced fact to `INTEL.md` with its source; a workstream move to `PLAN.md`.
Sessions end and context clears before a "now update the docs" step happens, so
do it on the same turn the thing occurs. `hippocampus-updates.md` has the full
decision tree for what belongs where.

---

## The workflows

Both are defined as skills in `.claude/skills/<name>/SKILL.md`. Each `SKILL.md`
is a prompt you can follow directly, whether or not your agent has a native skill
system.

- **kickoff** (`.claude/skills/kickoff/SKILL.md`) — first-run interview about
  the project. Run it once, after the identity flow, while `project.yml` is still
  the template default or `docs/MODEL.md` is still the empty skeleton. Start from
  whatever the user already said about the project and ask only about the gaps.
- **debrief** (`.claude/skills/debrief/SKILL.md`) — process raw notes/intel into
  the knowledge base. React to what is new or contradictory, ask clarifying
  questions, then update the docs surgically once aligned.
- **remsleep** (`.claude/skills/remsleep/SKILL.md`) — periodic holistic
  consolidation. Read everything, scan for staleness, contradictions, and
  cross-cutting patterns, propose a numbered checklist of changes, apply on
  approval.

Trigger them when the user says "debrief" / "new intel" / pastes notes, or asks
to consolidate / "remsleep."

---

## Codex setup

The knowledge base is tool-agnostic. Codex integration is checked into this
template alongside Claude Code's configuration. MCP remains per-user because
the servers and credentials depend on the domain.

### MCP servers

Register any servers the domain needs in `~/.codex/config.toml`:

```toml
[mcp_servers.<name>]
command = "npx"
args = ["-y", "<server-package>"]
# env = { API_KEY = "..." }
```

Edit `config.toml` then reload without restarting via the `config/mcpServer/reload`
app-server method, or just restart Codex.

### Lifecycle hooks

Codex uses `.codex/hooks.json`; Claude Code continues to use
`.claude/settings.json`. Both runtimes call the shared scripts under
`.claude/hooks/` for session initialization and milestone WORKLOG nudges.

Codex does not accept model-visible `additionalContext` from `PreCompact`, so
its equivalent reminder runs from `SessionStart(source=compact)` through the
Codex-only `.codex/hippo-worklog-after-compact.py` adapter. Claude retains its
native `PreCompact` hook unchanged.

Codex project hooks start untrusted. On the first Codex session after cloning or
after a hook change, open `/hooks`, review the project-local definitions, and
trust them. If hooks are unavailable, use the manual initialization steps
above.

### Skills

Codex loads user skills from `$HOME/.agents/skills/<name>/SKILL.md`. To use
`debrief` / `remsleep` as native Codex skills, symlink them so edits remain
immediately visible to both runtimes:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$(pwd)/.claude/skills/kickoff"  "$HOME/.agents/skills/kickoff"
ln -s "$(pwd)/.claude/skills/debrief"  "$HOME/.agents/skills/debrief"
ln -s "$(pwd)/.claude/skills/remsleep" "$HOME/.agents/skills/remsleep"
```

Or skip this and follow the `SKILL.md` prompts directly when asked.

---

## What is Claude-Code-specific

- **Auto-loading of `CLAUDE.md` + `.claude/rules/*`** — Claude Code pulls these
  into every session automatically. Codex only auto-loads this `AGENTS.md`, which
  is why the rules are referenced here for you to read on demand. The shared
  session loader, generated index, lint, and WORKLOG reminders still run in
  both runtimes through their respective checked-in hook configurations.
- **Auto-memory** (`~/.claude/projects/.../memory/`) — machine-local to Claude
  Code, does not travel. Anything durable should already be in the git-tracked
  docs.
