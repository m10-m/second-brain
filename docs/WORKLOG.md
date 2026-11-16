---
type: log
summary: "Rolling ~3-day worklog: what you actually did (ops actions, investigations + dead-ends, comms sent, decisions-in-flight) — the connective tissue git and your tracker don't capture. Read on demand to draft standup/status notes. Older days are archived to weekly files in worklog-archive/, the source for timesheets and monthly hours logs. Never auto-loaded."
status: active
---

# WORKLOG

_Rolling worklog for standup / status notes. **Read on demand only** — deliberately NOT loaded at session start (that is what makes a naive oplog explode context). Kept to the **3 most-recent day-sections** by `.claude/hooks/hippo-worklog-prune.py` at session start (ranked by date, so a weekend or idle stretch never wipes the last real work). **What rolls off is archived, not discarded** — it lands in `worklog-archive/<ISO-year>-W<week>.md`, bucketed by ISO week, sections ascending so a week reads Monday-first. That archive is the source for **timesheets and monthly hours logs**: it is the only record of what was actually done, as opposed to what was committed, and it is unreconstructable from git after the fact. Append terse, outcome-focused lines as work completes, capturing what git commits and tracker tickets DON'T: ops actions, investigations and their dead-ends, comms sent, decisions still in flight. Newest day on top._

<!-- Append day-sections below, newest first. Format:

## YYYY-MM-DD

**Theme / workstream.**
- Terse outcome-focused line: what you did + the result, not the play-by-play.

-->
