## First Action Every Session

The session-start hook (`session-start.sh`) has already loaded your context: `.claude/user.yml` + `project.yml`, the **On Deck** slate (from `docs/TASKS.md`), a **generated index** of the knowledge base (one summary + token estimate per doc, via `hippo-index.py`), and **MODEL.md in full** — the spine. It also runs `hippo-lint.py`, which nags about bloating/log-shaped hubs and un-routed intel.

Load on demand, not up front. Do NOT re-read whole docs the index already represents:

1. **MODEL.md** is already in context (the spine) — that is the mental model.
2. Scan the **index** to see what each doc holds. Then `Read` the specific doc(s) the task you have committed to touches, budgeting by the token estimates shown. Before that commitment there is no such doc — see *Initialization stops at the index* below.
3. **Vocabulary:** the **lobes** are the all-caps top-level hubs (MODEL, PLAN, QUESTIONS, PEOPLE); `docs/workstreams/*` are the **workstreams**; together they are the **hubs** tier and hold current state. **DECISIONS.md / INTEL.md are COLD** (audit/evidence) — read them only to answer "why is the state this way," not as routine session-start reading.

If `.claude/user.yml` doesn't exist, stop and follow the identity creation flow in `role.md` first. If the payload says **PROJECT NOT SET UP**, or the docs are still empty skeletons, run the kickoff interview (`.claude/skills/kickoff/SKILL.md`) before any other work. If the user's first message already describes the project, start from it and ask only about the gaps. Material they mention goes in through `/debrief` afterwards.

**For task-specific sessions** (the user says "let's work on X"), go straight to the relevant doc. Workstream details live in `docs/workstreams/`, proposals in `docs/proposals/`.

### Initialization stops at the index

**On Deck lists several threads; a session works one of them.** Its warm-doc pointers are *addresses*, not a reading list — the reason each entry carries one line on where you left off is so the slate is legible without opening anything. Reading every candidate thread's workstream doc up front pays for N threads to work one, and it is the single most expensive mistake available at session start. Measured on a live instance: three workstream bodies (roughly 18k + 25k + 10k tokens) opened before a thread was chosen, on top of a ~25k session-start payload. That is more than double the cost of the payload the load-on-demand design exists to shrink, spent on context that is discarded at the user's first reply.

So: **do not open a `docs/workstreams/*` body during initialization.** Open it the moment the session commits to a thread, and open only that thread's doc.

**"Initialise fully" / "init" / "catch up" does not license reading warm docs.** Fully initialised means all of this and nothing more:

1. The spine (MODEL.md) is in context and the index has been scanned — both arrive free in the hook payload.
2. On Deck has been read (also free in the payload).
3. **Cheap live-state verification has run.** This half is valuable and stays: `date`, VCS status and branch, a targeted `grep`, a ticket or PR lookup. These cost hundreds of tokens each, and they are exactly where a stale hub claim gets caught — the knowledge base is a snapshot and the world moves between sessions (see *Staleness check*). On the instance measured above, this pass found a closed ticket the slate still said to close, a merged change recorded as open, an idle piece of the user's own work on no slate at all, and a code checkout parked on a long-merged branch.
4. A recommended thread is named, with any deadline-bearing one flagged.

Then **stop and ask which thread**. Do not pre-load "so we're ready either way" — being ready for N threads costs N times being ready for one, and all but one gets thrown away.

**Corollary — grep, don't Read, for a single fact.** When initialization needs one specific thing (is this question still open, what does that table say for this deliverable), `grep -n` for it. A warm doc's body is for the session that owns that thread.

### Staleness check

If the project involves code repositories, external data, or other sources of truth that change between sessions, verify currency before making claims. The knowledge base records what was true when it was written — the world may have moved. When in doubt, check the primary source before asserting something from memory.

### Representation vs reality

When auditing or proposing changes, **what's in your representations (IaC, config files, docs, past notes) and what's actually deployed can differ**. Resources get configured outside of IaC; docs get written once and drift; tools report metadata that's accurate-but-partial. Before writing up a finding or ticket that claims "X is not configured" based only on grepping the codebase, verify against the live source of truth — the API, the running system, the actual endpoint. Grep of the IaC tells you what you manage; only the live state tells you what exists.

This is the same principle as the global rule "trust user reality over tool metadata" — the running system is authoritative, the representation can lag. If you make a claim that turns out to be wrong because you trusted the representation over reality, record it in INTEL.md so the next session learns the pattern.

### Packaged as two skills

`/wake` runs the initialisation above as one command, for the first session of the day or the first after a gap: payload check, live-state verification of the slate's PR links, your open PRs and review asks, tracker reconciliation reported as deltas, a slate catch-up limited to verified changes, then one recommended thread. `/join <thread>` is for an extra agent alongside one that already woke: the same context load (payload, spine, index, On Deck), then straight to the named thread. It skips the sweeps and the slate-wide catch-up, and keeps only its own thread's On Deck entry current. This rule stays the authority; when it changes, update `.claude/skills/wake/SKILL.md` to match.
