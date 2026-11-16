---
name: debrief
description: Process raw meeting notes or intel into the Hippocampus knowledge base. Use when the user pastes meeting notes, shares new intel, or says "debrief", "new intel", "meeting notes", or "process these notes". Also use when the user returns from a call and wants to capture what they learned.
---

# Debrief — Intel Processing

The user will paste raw notes or intel. Your job is to process this through a structured conversation that ends with the knowledge base docs being updated.

Before starting, read `project.yml` to understand the domain and any vocabulary overrides. Use the project's vocabulary throughout (e.g., "matter" instead of "workstream" if configured).

## The Process

### Phase 1: Absorb and React

Read the pasted notes carefully. Then tell the user:

1. **How your understanding changed** — what's new, what shifted, what got confirmed or contradicted vs what's already in the docs
2. **Surprises or tensions** — anything that conflicts with existing decisions, plans, or assumptions in the knowledge base
3. **Connections** — how this intel connects to existing plans, open questions, or decisions

Be opinionated. Don't just summarize — interpret. Say what you think this means.

### Phase 2: Clarify

Ask clarifying questions in two categories:

1. **Questions you need answered now** — ambiguities in the notes, missing context that changes the interpretation, things that sound important but are unclear
2. **New open questions this raises** — things that should be tracked in QUESTIONS.md, with suggested targets for who might know. Present these and ask the user if they can answer any of them right now.

If something in the notes could be clarified by reading code or checking a primary source, say so and offer to investigate. Don't silently assume — propose the investigation and let the user decide.

### Phase 3: Iterate

The user will answer your questions, correct misunderstandings, and add context. This may trigger:
- New questions from you
- Investigations against primary sources
- Revised interpretations

Keep going until you and the user agree on what the intel means. Don't rush to recording — understanding comes first.

### Phase 4: Record to Hippocampus

Once aligned, update the docs. Tell the user exactly what you plan to update before doing it:

- **INTEL.md** — Append raw intel under today's date with source attribution
- **QUESTIONS.md** — Add new open questions, update/resolve existing ones
- **DECISIONS.md** — Log any decisions that were made or confirmed
- **PLAN.md** — Update status, next actions, blockers
- **TASKS.md** — Add personal action items that arose from this debrief
- **PEOPLE.md** — Add new people, update what they know / what to ask them
- **MODEL.md** — Update if the mental model shifted
- **Detail docs** — Update relevant docs in `docs/workstreams/`, `docs/proposals/`, etc.

Not every debrief touches every file. Only update what actually changed.

## Key Principles

- **The docs are the memory.** If it doesn't get written there, it didn't happen. Every debrief must end with docs updated.
- **Don't duplicate.** Each fact lives in ONE canonical location. Other docs point to it. The `.claude/rules/` files point at Hippocampus — never store intel there.
- **Interpret, don't transcribe.** Raw notes go in INTEL.md. Everything else should be processed, organized, and connected to existing knowledge.
- **Source attribution matters.** Always note who said what and when. "The client said X" is different from "I concluded X."
- **Ask before assuming.** If the notes are ambiguous, ask. Don't fill gaps with guesses.

## Attribution Convention

In raw notes and INTEL.md, use prefix tags to distinguish who said/flagged what:
- Use first-initial tags: `[A]` for Alice, `[B]` for Bala, etc. (names from `PEOPLE.md`)
- Unattributed lines default to the person named in the section header
- `(code-confirmed)` or `(doc-confirmed)` = verified against primary sources
- `(Name)` or `(Name observation)` = inline attribution when prefix doesn't fit

This matters because different sources carry different authority, and people can be wrong about others' work.

## Validation

When processing technical or factual claims from intel, consider whether they can be verified against primary sources (code, documents, data, live systems). Two levels:

1. **Propose investigation** for any concrete claim that can be verified (e.g., "X uses Y," "Z is deployed," "we have N of something"). Say: "I can verify this — want me to check?"
2. **Default to checking** if the claim affects decisions or would change the mental model. Don't wait to be asked.

Record any delta between what was claimed and what was found — both are valuable. The person's mental model reveals intent and direction; the primary source reveals ground truth.

If the project involves code: check PRs and branches, not just the main branch. Work may exist in unmerged PRs. "Not in main" doesn't mean "doesn't exist."
