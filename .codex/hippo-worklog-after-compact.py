#!/usr/bin/env python3
"""Restore Hippocampus continuity after Codex compacts its context.

Claude Code keeps using hippo-worklog-precompact.py through its native
PreCompact hook. Codex does not add model context from PreCompact, but it emits
SessionStart with source=compact immediately afterwards. This Codex-only
adapter uses that model-visible event without changing Claude's hook contract.
"""

import json


MESSAGE = (
    "Hippocampus continuity after compaction: verify that today's work is "
    "captured in docs/WORKLOG.md, including decisions in flight, dead ends, "
    "communications, commits, and deploys. Upsert into the existing thread "
    "for today rather than adding fragments. Also verify that any durable "
    "state or understanding change is reflected in the relevant hot or warm "
    "document. See .claude/rules/hippocampus-updates.md."
)

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": MESSAGE,
            }
        }
    )
)
