# Hippocampus

**An AI-powered knowledge management system for professionals who deal in complex, evolving information.**

Hippocampus turns Claude Code or OpenAI Codex into a persistent memory and thinking partner. You feed it raw intel — meeting notes, phone calls, research findings, conversations — and it distills everything into a structured, living knowledge base that persists across sessions.

Named after the brain region responsible for converting short-term memory into long-term memory. That's exactly what this does.

## What it does

- **Ingests raw intel** from meetings, calls, conversations, documents
- **Distills into structured docs** — a mental model, plans, open questions, decisions, people map
- **Maintains context across sessions** — every new conversation starts with full knowledge of everything prior
- **Challenges and clarifies** — doesn't just transcribe, it interprets, finds tensions, asks questions
- **Tracks what you don't know** — open questions are first-class, not afterthoughts
- **Consolidates and connects** — periodic `/remsleep` cycles find cross-cutting patterns, contradictions, and staleness across the whole knowledge base

## Who it's for

Anyone who manages complex, multi-stakeholder domains where information comes in fragments and context is everything:

- **Lawyers** — case management, deposition notes, witness tracking, case theory
- **Architects / Engineers** — system design, technical intel, decision records
- **Consultants** — client engagements, stakeholder mapping, project tracking
- **Researchers** — literature notes, hypothesis tracking, methodology decisions
- **Product Managers** — user research, feature decisions, stakeholder alignment

## Getting started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or OpenAI Codex installed and authenticated
- Git

Codex and other `AGENTS.md`-aware agents use [`AGENTS.md`](AGENTS.md) as their
entry point. Claude Code continues to use `CLAUDE.md` and `.claude/settings.json`.

### Setup

1. **Create a new repo from this template:**

   On GitHub, click **"Use this template"** → **"Create a new repository"**. Or clone directly:

   ```bash
   git clone https://github.com/YOUR_ORG/hippocampus my-project
   cd my-project
   ```

2. **Launch your agent:**

   ```bash
   claude
   # or: codex
   ```

3. **The agent will guide you through setup.** It asks your name and role, then
   interviews you about the project: what it is, what done looks like, who is
   involved, what is in flight and what material exists. From that it writes
   `project.yml` and first drafts of the docs. If your first message already
   describes the project, it starts from that and asks only about the gaps.
   Codex users should review and trust the checked-in project hooks with `/hooks`.

4. **Start feeding it intel.** Type `/debrief` and paste your notes from a meeting, call, or research session. Your agent will:
   - React to what's new, surprising, or contradictory
   - Ask clarifying questions
   - Update the knowledge base once you're aligned

That's it. The docs build themselves as you work.

## The knowledge base

After setup, your `docs/` folder contains:

| Document | Purpose |
|----------|---------|
| **MODEL.md** | Your current mental model — the "state of the world" as you understand it |
| **PLAN.md** | Active plans, priorities, timelines, next actions |
| **INTEL.md** | Raw chronological log — who said what, when, with source attribution |
| **QUESTIONS.md** | Open questions you're tracking, with who might know the answer |
| **DECISIONS.md** | Decisions made, with rationale and alternatives considered |
| **PEOPLE.md** | Key people, what they know, what to ask them about |
| **TASKS.md** | Your personal action queue — discrete tasks separate from project workstreams |

As complexity grows, subdirectories appear:

| Directory | Purpose |
|-----------|---------|
| **workstreams/** | Detailed tracking for major initiatives — phases, owners, dependencies, status |
| **proposals/** | Technical proposals, research docs, evaluation frameworks |

These are living documents. Your agent updates them as new intel comes in. Each fact lives in one canonical location — no duplication.

## Key commands

| Command | What it does |
|---------|-------------|
| `/kickoff` | First-run interview about the project; writes `project.yml` and the first drafts (runs automatically on a new instance) |
| `/debrief` | Process raw meeting notes or intel into the knowledge base |
| `/remsleep` | Holistic consolidation — find connections, contradictions, staleness across all docs |
| `/wake` | Full session initialisation: verify the payload, check the slate against live state, sweep PRs and the tracker, recommend one thread |
| `/join <thread>` | Light initialisation for an extra agent alongside one that already woke |
| Ask anything | Your agent loads the knowledge base every session — just ask |

## How it works

### The debrief cycle

1. **You paste raw notes** — bullet points, stream of consciousness, voice memo transcripts, whatever
2. **Your agent absorbs and reacts** — what changed, what's surprising, what connects to existing knowledge
3. **Your agent asks questions** — ambiguities, missing context, new open questions to track
4. **You clarify and iterate** — back and forth until you're aligned on what the intel means
5. **Your agent records to the knowledge base** — each doc updated surgically, only what changed

### The consolidation cycle (REMSleep)

After a burst of debriefs, or periodically (end of week):

1. **Your agent reads everything** — every doc in the knowledge base, holistically
2. **Scans with 7 lenses** — staleness, cross-pollination, contradictions, intel graduation, question triage, people drift, emergent patterns
3. **Presents findings** — numbered checklist with proposed changes, grouped by type
4. **You approve/reject** — each change gets explicit approval before writing
5. **Claude applies and verifies** — changes land, verification pass confirms they stuck

This is how the knowledge base stays coherent over time. Debriefs add new intel; REMSleep connects it.

### Multi-user support

Multiple people can use the same Hippocampus repo. Each user gets a local identity file (`.claude/user.yml`, gitignored) that determines their access level:

- **Owner** (configured in `project.yml`) — full read/write to all docs
- **Contributor** — can add intel and questions freely; structural changes are confirmed first
- **Viewer** — read access; input recorded as intel for the owner to review

### Session continuity

Every session starts by loading the knowledge base. Claude Code invokes the
loader on the first `UserPromptSubmit`; Codex invokes the same loader on
`SessionStart`. Both use `session_id` for isolation, so concurrent sessions do
not interfere. The loader emits the **On Deck** slate, a **generated index**
(one summary + token estimate per doc, from each doc's frontmatter), and
**MODEL.md in full** (the spine), then runs a lint for bloating or log-shaped
docs. The agent reads any other doc on demand, budgeting by the token estimates.
This keeps the session-start payload small as the knowledge base grows.

Your agent doesn't need you to re-explain — it picks up where you left off. The docs ARE the memory.

## Customization

The kickoff interview writes `project.yml` for you. Edit it afterwards to adjust:

```yaml
name: "My Project"
domain: legal  # Adjusts vocabulary and Claude's persona
description: "Brief description of what this knowledge base tracks"

owner_role: "Lead Attorney"

persona: >
  You are a legal research and case management partner.
  Help organize case intel, track open issues, and maintain
  the case theory.
```

See `project.yml` for all available options and domain presets.

## Philosophy

- **If it's not in the docs, it didn't happen.** Every debrief ends with docs updated.
- **Interpret, don't transcribe.** Raw notes go in INTEL.md. Everything else is processed and connected.
- **Source attribution matters.** "The client said X" is different from "I inferred X from the filing."
- **Track what you don't know.** Open questions are as important as answers.
- **One fact, one location.** No duplication. Other docs point to the canonical source.
- **Connections compound.** Individual facts are useful; the relationships between them are powerful. REMSleep finds these.

## License

Copyright 2026 Nubelo Engineering, S.L. Licensed under the [Elastic License 2.0](LICENSE).

You can use, copy and change Hippocampus, at work and for paying clients included. You can't offer it to other people as a hosted or managed service.

What you put into a brain made from this template is yours: your documents, notes and worklogs, and any new files you write yourself. The license covers the template's own files and your changes to them. If you pass a copy on to someone else, keep the LICENSE file and say what you changed.

---

Built for [Claude Code](https://claude.ai/claude-code) and OpenAI Codex.
