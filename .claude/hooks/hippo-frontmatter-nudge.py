#!/usr/bin/env python3
"""PostToolUse tripwire: a Hippocampus doc body changed — is its SUMMARY still true?

The frontmatter `summary:` is the ONLY thing a future session sees for most docs.
MODEL.md is dumped in full at session start; everything else is represented by its
summary line in the generated index, with the body loading on demand. So a warm doc
can be enormous at no cost, which is the design — but a summary that lags its body
is worse than a missing doc, because the index actively contradicts what the doc
knows and nobody opens it to find out.

The failure this is built from, A-Teams 2026-08-13. Over one session large parts of
`workstreams/hatchet-platform.md` were rewritten — an upgrade shipped, a chart-version
mechanism corrected, a node-roll trap discovered — and the summary was never touched.
It still read "Hatchet version upgrade remains required" and "the current 0.11.0"
four hours after the fleet moved to 0.14.0/v0.98.9. A session reading the index would
have concluded nothing had changed. Body current to 08-13, summary frozen at 08-07,
and a second agent edited the same body the same day without touching it either.

Why an edit trigger rather than the lint's calendar one: `hippo-lint.py` has a
STALE_SUMMARY_DAYS check, but 30 days is the wrong shape for a doc under active work.
The summary above was materially false within FOUR HOURS. The moment of damage is the
edit, so that is where the question belongs.

Scope. Fires on any `docs/**.md` edit, which covers both layouts in use across
instances (`docs/workstreams/` and `docs/architecture/`). Silent on the cold and
transient tiers, where the summary is not how a session navigates; on archives; on
MODEL.md, whose body is loaded in full every session so its summary is not the
interface; and on edits that rewrote the summary already.

NOTE on what this does NOT cover. It watches summary-vs-body drift. It does not
catch a hot doc whose BODY has gone stale against reality — that is a different
failure and needs a different trigger. Cetus 2026-08-20 is the worked example: a
whole session established the runtime topology while MODEL still called it unknown,
and nothing here would have fired, because MODEL was never edited.

Fires on every qualifying edit by deliberate choice (the principal, 2026-08-13: "every edit,
if it gets onerous we can change later"), so the message is kept short.
"""

import json
import os
import re
import sys

# Cold + transient tiers: their summaries are not what a session navigates by, and
# WORKLOG in particular is rewritten constantly by the prune hook. MODEL is exempt
# for the opposite reason — its whole body is in the session-start payload.
EXEMPT = {
    "WORKLOG.md",
    "DECISIONS.md",
    "INTEL.md",
    "MODEL.md",
}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in ("Edit", "Write", "NotebookEdit"):
        return 0

    path = (payload.get("tool_input") or {}).get("file_path") or ""
    norm = path.replace("\\", "/")
    if "/docs/" not in norm or not norm.endswith(".md"):
        return 0
    base = os.path.basename(norm)
    if base in EXEMPT or "/worklog-archive/" in norm or "/archive/" in norm:
        return 0

    # If the edit itself rewrote the summary, the author has already answered the
    # question; nagging then is the noise that gets a hook ignored.
    #
    # Match against the RAW string values, not json.dumps of the payload. The first
    # version did the latter and never fired: dumps escapes the inner quotes, so
    # `summary: "x"` arrives as `summary: \"x\"` and a `summary:\s*["']` pattern
    # cannot cross the backslash. Caught by the both-ways proof, which is the only
    # reason it is not still broken.
    SUMMARY_EDIT = re.compile(r"summary:\s*[\"']")
    for v in (payload.get("tool_input") or {}).values():
        if isinstance(v, str) and SUMMARY_EDIT.search(v):
            return 0

    # Report the doc's own drift when we can read it: a summary citing an older date
    # than the body is the concrete, checkable form of the problem.
    hint = ""
    try:
        text = open(path, encoding="utf-8").read()
        m = re.search(r'^summary:\s*"(.*?)"\s*$', text, re.M | re.S)
        if m:
            body = text.split("---", 2)[2] if text.startswith("---") else text
            dates = re.compile(r"\d{4}-\d{2}-\d{2}")
            s_dates = sorted(dates.findall(m.group(1)))
            b_dates = sorted(dates.findall(body))
            if s_dates and b_dates and b_dates[-1] > s_dates[-1]:
                hint = (
                    f" Right now its summary's newest date is {s_dates[-1]} "
                    f"while the body's is {b_dates[-1]}."
                )
        elif "type:" in text[:400]:
            hint = " This doc has frontmatter but no summary: the index cannot represent it."
    except OSError:
        pass  # unreadable file: a nudge must never break the edit, and a missing hint is not a failure

    print(
        f"🧭 You changed {base}. Its frontmatter `summary:` is the ONLY thing a "
        f"future session sees — the body loads on demand, the summary loads every "
        f"time.{hint}\n"
        f"If what you just wrote changed the doc's ESSENCE (a decision, a "
        f"capability now live, a claim retracted, a status moved), update the "
        f"summary in the same turn. A summary that lags its body is worse than a "
        f"missing doc: the index contradicts the knowledge and nobody opens it.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
