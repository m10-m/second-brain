# Messages to people go through voice calibration

Standing order. **Before drafting or revising anything a named human will read as being from the principal** (a Slack message or DM, an email, a PR/MR review comment, a ticket comment, a short outward-facing note), load the `voice-calibration` skill and write to it.

This rule carries the trigger and nothing else. The method lives in the skill and the principal's actual voice lives in `.claude/voice/`, because style guidance needs examples and examples are too expensive to load every session.

**It applies on edits, not just first drafts.** The shape survives the first pass, when the rule is in view, and drifts on the second, when a good question gets answered at length. Treat a revision as a new draft.

**Two things it does not cover.** The internal knowledge base is deliberately a denser working voice, and session chat is a different medium. Per-audience calibration (register for a client deliverable, what never goes to a particular person, which internal identifiers are suppressed) belongs in this project's publishing rule.

_Prompted 2026-08-20: a drafted DM came back with nine separate voice corrections, and a corpus check then showed the assistant had been calibrating its drafts against its own earlier posts in the same channel rather than against anything hand-typed._

---

_**Layer L0.** Person-agnostic: the rule and the skill are the mechanism, and the principal is read from `.claude/user.yml`. The voice file itself is L1._
