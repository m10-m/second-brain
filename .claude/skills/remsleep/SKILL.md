---
name: remsleep
description: Holistic consolidation of the Hippocampus knowledge base. Use when you want to step back from targeted updates and let the AI brain form new connections, find contradictions, clean up staleness, and tighten cross-document coherence. Run periodically (e.g., end of week) or after a burst of debriefs.
---

# REMSleep — Hippocampus Consolidation

Named after REM sleep's role in memory consolidation and neural pathway formation. Debriefs process new intel into specific docs; REMSleep steps back, reads everything holistically, finds connections and contradictions, and tightens the knowledge base.

**This is not a debrief.** REMSleep consolidates and connects — it doesn't process new raw intel. If there's unprocessed intel in INTEL.md, flag it and suggest a debrief first.

## The Process

### Phase 1: Full Read

Discover all Hippocampus docs dynamically — glob `docs/**/*.md` to find everything. The knowledge base grows over time and REMSleep must pick up all files automatically.

Use subagents to read in parallel, grouped by category:

**Group A — Core docs (always deep-read):**
These are the structural backbone. REMSleep's primary job is keeping these coherent.
- `MODEL.md` — Current mental model
- `PLAN.md` — Plans with status and next actions
- `DECISIONS.md` — Decision record
- `QUESTIONS.md` — Open and resolved questions
- `PEOPLE.md` — People and context map
- `INTEL.md` — Raw intel chronolog
- `TASKS.md` — Current task tracking

**Group B — Workstreams + proposals:**
- `workstreams/*.md` — Active by default, but check: a completed/abandoned workstream should be flagged
- `proposals/*.md` — Triage by status. Active/DRAFT proposals get full read. Decided/rejected proposals get a skim — flag for archival if cluttering the active set

**Group C — Operational docs (if any):**
- Any other subdirectories (comms, reports, etc.) — Point-in-time artifacts. Skim only — check for unprocessed intel or untracked commitments. Don't maintain these, but flag issues.

Build a mental model of the current state: what's decided, what's open, what's in progress, who owns what, what has changed recently.

### Phase 2: Scan (7 Lenses)

Run through the knowledge base with each lens, collecting findings:

1. **Staleness** — Status fields that don't match reality. Effort estimates overtaken by events. Dates that have passed. "Next week" references that are now weeks ago. Target dates in the past with no update.

2. **Cross-pollination** — Connections between workstreams/decisions that exist but aren't documented. "This thing over here actually affects that thing over there." Dependencies that aren't called out. Shared blockers.

3. **Contradictions** — Places where two docs say conflicting things, often because one was updated and the other wasn't. Status fields, ownership assignments, technical descriptions that diverge.

4. **Intel graduation** — INTEL.md entries that have been fully processed into DECISIONS/PLAN/workstreams and can be marked as processed, vs entries sitting unprocessed. Flag unprocessed entries that look important.

5. **Question triage** — Open questions that can now be answered given recent intel or decisions. Questions that have become irrelevant. Questions that should be elevated to decisions. Resolved questions still sitting in the Open section.

6. **People drift** — Does PEOPLE.md still match reality? New ownership, shifted responsibilities, new context from recent meetings. People mentioned in intel who aren't in PEOPLE.md yet.

7. **Emergent patterns** — Themes or directions that aren't explicitly called out anywhere but are visible when you read everything together. The "aha" connections. Recurring blockers. Implicit priorities that should be made explicit.

**Bonus: Document lifecycle triage**
- Proposals that became decisions → flag: "archive proposal, decision is in DECISIONS.md"
- Completed/abandoned workstreams → flag for status update or archival
- Orphan files — exist but aren't referenced from any core doc

### Phase 3: Present Findings

Present ALL findings as a numbered checklist, grouped by lens. For each finding:

- **What** the issue is
- **Where** — which doc(s) are affected
- **Proposed change** — specific enough to execute
- **Confidence** — "certain" vs "I think this is right but check me"

Example format:
```
### 1. Staleness (N findings)
- [ ] **S1:** PLAN.md lists workstream X as "in progress" but DECISIONS.md records it as decided on 2026-03-06. Update PLAN.md status. [certain]
- [ ] **S2:** workstreams/alpha.md references "next week" target — that was 3 weeks ago. Update or remove timeline. [certain]

### 2. Cross-pollination (N findings)
- [ ] **X1:** The auth decision directly affects the API migration workstream — neither doc references the other. Add cross-references. [certain]
```

**Do NOT write anything yet.** Wait for the user to review and approve/reject each finding.

### Phase 4: Apply

Apply approved changes. For each change:
- State which doc is being updated
- Make the edit
- Brief confirmation

Work through the approved list systematically. If applying one change reveals that another approved change needs adjustment, flag it before proceeding.

### Phase 4b: Verify

After all changes are applied, run a verification pass. Use a subagent to read every modified file and confirm each approved change landed correctly in the final state. Report results as PASS/FAIL per item. If any FAIL, fix immediately before proceeding to the summary.

This step exists because changes can silently fail (wrong match string, concurrent edits). The cost of verification is low; the cost of believing a change landed when it didn't compounds across sessions.

### Phase 4c: Mark Consolidated Intel

For each INTEL.md entry whose content has been consolidated into structural docs during this REMSleep pass (or in a previous pass that missed the marking step), update the entry heading with a marker and add pointer lines below it. The session-start hook reads the marker and elides the entry body when loading INTEL.md, keeping the chronolog complete on disk while reducing context bloat at session start.

**Marker convention:**

- Fully consolidated → ` ✅ PROCESSED` appended to the heading
- Partially consolidated → ` ✅ PARTIALLY PROCESSED` appended to the heading
- Not consolidated → leave heading unchanged

**Pointer lines (mandatory for marked entries):**

Immediately under the heading (after one blank line), add italic pointer lines summarizing where the intel landed. The hook keeps the heading + pointer lines visible at session start; everything else in the entry body is elided until the next `## ` heading.

```
## 2026-03-30 ✅ PROCESSED — Topic title

_Processed into: MODEL.md (section X), DECISIONS.md (decision Y on 2026-03-30), workstreams/foo.md._

### Original body heading
... body retained verbatim — git history is the audit trail ...
```

For partial:

```
## 2026-03-31 ✅ PARTIALLY PROCESSED — Topic title

_Processed into: PLAN.md (workstream Z), reports/some-report.md._
_Pending: Open question about A. Action items for B not yet communicated._
```

**Rules:**

- Body stays in the file. Never delete the body when marking — git history is the audit trail and the body may be needed for future reference. The hook is the only thing that elides it.
- Pointer line format: italic markdown (`_..._`), one line per pointer category. The hook recognizes lines starting with `_` as pointer lines. Anything else is treated as body and gets elided.
- When in doubt, prefer `PARTIALLY PROCESSED` with a `_Pending:_` line over `PROCESSED`. The pointer line is what loads at session start; underspecifying it loses the breadcrumb.
- Don't mark if you're unsure where the intel was consolidated. The marker is a claim about provenance and must be accurate.
- Mark in the same REMSleep pass as the consolidation. The connection between intel and where it landed is freshest at the moment of consolidation.

### Phase 5: Summary

After all changes applied:
- **Count of changes by type** (staleness fix, new connection, contradiction resolved, etc.)
- **Rejected findings** that might warrant revisiting later
- **Unprocessed intel** flagged during the scan (suggest debrief if significant)
- **Document lifecycle actions** taken or recommended (archival, restructuring)
- **Suggested timing for next REMSleep** based on the rate of change observed

## Key Principles

- **Read everything before writing anything.** The value is in the holistic view.
- **Present before committing.** Every change gets user approval. This isn't autopilot.
- **Connections are the highest-value output.** Staleness fixes are maintenance; cross-pollination is insight.
- **Don't duplicate debrief work.** REMSleep consolidates and connects — it doesn't process new raw intel.
- **Preserve coherence.** Changes should make the docs more coherent, not just more current. If a staleness fix would create a contradiction elsewhere, flag the whole chain.
- **Dynamic discovery.** Never hardcode file lists. Glob for everything. The Hippocampus grows.
- **Triage before deep-reading.** Not every doc needs the same attention. Core docs always get deep reads; operational docs get skimmed and triaged.
