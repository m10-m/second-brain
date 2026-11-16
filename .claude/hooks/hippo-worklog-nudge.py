#!/usr/bin/env python3
"""PostToolUse tripwire: milestone nudge — WORKLOG + warm-tier fidelity.

Fires the "update WORKLOG inline, not at session end" rule at the MOMENT a
loggable milestone lands, instead of depending on recall before a /clear.
Advisory work (a review, a reply, a decision) has no deploy-shaped signal, so it
is the class that most often slips; pinning the reminder to the event is what
keeps the log current so a /clear never loses an owed entry.

Same trigger also carries a WARM-TIER self-check. The milestone that earns a
WORKLOG line is often the same moment durable state moves (a cold proposal/comms
doc changing status, a decision locked, the model or plan shifting), and that
half drifts more easily because WORKLOG has this hook backstop and the warm tier
does not. The check is a QUESTION, not a mandate: most milestones need only the
WORKLOG line, so it stays a self-check to avoid the sprawl broad triggers would
otherwise cause.

Pairs with hippo-worklog-precompact.py (the PreCompact backstop) and the WORKLOG
"definition of done" in .claude/rules/hippocampus-updates.md.

Self-filters: exits silent on a non-milestone tool call. Contract mirrors the
other tripwires: exit 0 + {"hookSpecificOutput": {"hookEventName": "PostToolUse",
"additionalContext": "..."}}.

────────────────────────────────────────────────────────────────────────────
CUSTOMISE PER INSTANCE: the BASH_MILESTONES deploy verbs and the TRACKER_TOOLS
names below are sensible defaults. Add your instance's deploy commands (e.g.
`pulumi up`, `sst deploy`, `helmfile`) and your tracker's MCP tool names. Keep
the matcher in .claude/settings.json in sync with TRACKER_TOOLS.
────────────────────────────────────────────────────────────────────────────
"""
import json
import re
import sys

# Bash command patterns that mark a loggable milestone, mapped to a label.
# Generic core + a customise slot for instance-specific deploy verbs.
BASH_MILESTONES = [
    (r"\bgit\s+commit\b", "a commit landed"),
    (r"\bgh\s+pr\s+(create|merge|ready)\b", "a PR was opened/merged"),
    (r"\bgh\s+workflow\s+run\b", "a CI/deploy workflow was dispatched"),
    # ── instance deploy verbs (uncomment / edit per project) ──
    # (r"\bpulumi\s+up\b", "an infra deploy ran"),
    # (r"\bsst\s+deploy\b", "an app deploy ran"),
    # (r"\b(terraform|tofu)\s+apply\b", "an infra apply ran"),
    # (r"\bhelmfile\b|\bdeploy-helm\b", "a Helm deploy ran"),
]

# Shared, outbound deliverables (Hippocampus-standard dirs).
DELIVERABLE_DIRS = ("/docs/comms/", "/docs/proposals/")

# Tracker "a comment/issue was saved" tool names. Default = Linear MCP; swap for
# your tracker's tool names and mirror them in settings.json's PostToolUse matcher.
TRACKER_TOOLS = {"mcp__linear__save_comment", "mcp__linear__save_issue"}


def detect(tool_name, tool_input):
    if tool_name == "Bash":
        cmd = (tool_input or {}).get("command", "")
        for pat, label in BASH_MILESTONES:
            if re.search(pat, cmd):
                return label
        return None
    if tool_name in ("Write", "Edit"):
        path = (tool_input or {}).get("file_path", "")
        if any(d in path for d in DELIVERABLE_DIRS):
            return "a shared deliverable (comms/proposal) was written"
        return None
    if tool_name in TRACKER_TOOLS:
        return "a tracker comment/issue was saved"
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    label = detect(data.get("tool_name", ""), data.get("tool_input") or {})
    if not label:
        sys.exit(0)

    msg = (
        f"📓 Milestone check — a loggable milestone just landed ({label}).\n"
        f"1) WORKLOG: if not already captured, UPSERT it into today's day-section in "
        f"docs/WORKLOG.md now — fold into the existing entry for this "
        f"work-thread, don't append a new fragment (one coherent block per day, "
        f"newest on top). Capture what git and the tracker don't: the why, dead-ends, "
        f"comms sent. A milestone isn't done until its WORKLOG line exists.\n"
        f"2) WARM/HOT tier: did this move DURABLE state, not just produce an "
        f"artifact? A cold proposal/comms doc changing status (it goes invisible next "
        f"session without a warm pointer), a decision locked, the mental model or a "
        f"plan shifting, an externally-sourced fact — those route to the "
        f"workstream/MODEL/PLAN/DECISIONS/INTEL, not only WORKLOG. If the hot/warm "
        f"tier isn't now true, fix it THIS turn. (A check, not a mandate — most "
        f"milestones need only the WORKLOG line.)\n"
        f"See .claude/rules/hippocampus-updates.md."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
