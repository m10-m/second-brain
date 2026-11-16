## Document Publishing Rules

These apply to any document under `docs/proposals/`, `docs/reports/`, or `docs/comms/` — anything shared beyond the user (with teammates or stakeholders, or published to a wiki / Notion / Confluence).

### Before writing, check every line for:

1. **No private-knowledge-base references.** Don't reference `MODEL.md`, `PLAN.md`, `INTEL.md`, `DECISIONS.md`, `QUESTIONS.md`, `PEOPLE.md`, or anything under `docs/` — readers don't have access. Instead: state decisions as facts, or link to the published version.

2. **No assignment of people to work.** Don't name who *should* implement something — that's leadership's call. Naming who *already owns* something (factual context) is fine; naming who *should do* it is not.

3. **No resourcing or capacity opinions.** Staffing, capacity constraints, team contention, "who does this work" — out of scope unless that is explicitly your role.

4. **No internal-system jargon.** Don't reference the session-start rules, the lint, REMSleep, or other concepts that only exist in this repo's `.claude/` configuration.

5. **Concise prose.** One idea per sentence. Cut filler ("essentially", "basically", "actually", "the only"). Use tables and bullets for enumerative content; prose is for genuinely flowing argument. Each paragraph must justify its existence.

6. **No stream-of-consciousness.** State decisions and facts; don't trace how you arrived at them. Avoid meta-commentary about the doc itself. When iterating on a draft, rewrite sections cleanly — don't layer corrections on top of earlier framing. A doc shown to others should read as a single coherent voice, not a transcript of the author's process.

7. **Diagrams in Mermaid, not ASCII.** Any diagram in a public-facing doc must be a ```mermaid fenced block, never hand-drawn ASCII / box-drawing art. Mermaid renders cleanly in Notion and GitHub, stays legible as it grows, and diffs sanely; ASCII art misaligns across fonts and rots the moment anyone edits it. Convert ASCII diagrams to Mermaid on the next pass that touches the doc.

8. **Human voice, no AI tells. No em-dashes.** A shared doc should read like a person wrote it, not a model. Hard rule: no em-dashes (`—`) anywhere; use a period, a comma, parentheses, or restructure the sentence. Hyphens in compounds (`read-only`) and literal UI/path arrows (`Security → API controls`) are fine; the banned character is the em-dash used as a clause separator. Strip the other primary AI hallmarks too: the "not just X, it's Y" / "not only… but…" construction, rule-of-three triads and over-balanced parallelism, "that said / on the other hand" both-sides cadence, tidy summarizing kickers ("At the end of the day…", "Ultimately…"), and filler ("essentially", "basically", "it's worth noting"). State things plainly and directly. This covers every doc that leaves the user: proposals, reports, comms, and anything sent to a named recipient.

### After publishing:

9. **Replace the local file with a pointer stub.** Once a doc is published, replace the local file content with a minimal stub: title, published URL, one-line description. Don't delete the file (preserves git history and relative links from other docs). Format:

```markdown
# [Title]

**Canonical location:** [URL]

_One-line description._
```
