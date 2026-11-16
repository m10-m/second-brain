#!/usr/bin/env python3
"""PreCompact backstop: flush WORKLOG before context is summarised.

Second layer under hippo-worklog-nudge.py. The PostToolUse nudge keeps WORKLOG
current at each milestone; this catches whatever had no tool signature (a pure
reasoning/decision turn) right before /compact or an auto-compact collapses the
detail. Fires on both manual and auto compaction.

Caveat that shapes the design: /clear fires SessionEnd, NOT PreCompact, and
SessionEnd output does not return to the model (the session is ending), so a hard
/clear can't be rescued by a last-second reminder. That is why the PostToolUse
nudge is primary — for /clear you rely on the log already being current.

Contract: exit 0 + {"hookSpecificOutput": {"hookEventName": "PreCompact",
"additionalContext": "..."}}.
"""
import json
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    trigger = data.get("trigger", "")  # "manual" | "auto"
    when = "before this /compact" if trigger == "manual" else "before this auto-compaction"

    msg = (
        f"📓 WORKLOG flush {when}: the detailed context is about to be summarised. "
        f"Before it is, make sure today's work is captured in docs/WORKLOG.md "
        f"— PRs, deploys, decisions still in flight, dead-ends, comms sent — the "
        f"connective tissue that won't survive the summary. Upsert into today's "
        f"day-section (don't sprawl new fragments). See .claude/rules/hippocampus-updates.md."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "PreCompact", "additionalContext": msg}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
