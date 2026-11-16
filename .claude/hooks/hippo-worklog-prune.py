#!/usr/bin/env python3
"""Hippocampus worklog pruner + archiver.

Keeps docs/WORKLOG.md bounded to the KEEP_SECTIONS most-recent day-sections so
the rolling standup log never grows unbounded, and ARCHIVES what rolls off into
weekly files under docs/worklog-archive/ rather than discarding it. Runs at
session start (from session-start.sh). Silent on success; never breaks the hook.

Why archive rather than drop
----------------------------
The worklog is the only place that records what was actually *done* — ops
actions, investigations and their dead ends, comms sent — as opposed to what
was committed. That is precisely the input a timesheet or a monthly retainer
hours log needs, and it is unreconstructable from git after the fact. Dropping
it at the end of a 3-day window destroyed the one artifact that could
substantiate an invoice. Git technically held the deleted text, but "diff the
prune commits for the last month" is not a workflow anyone runs.

So: the rolling window still bounds what is *live*, and the drained sections
land in a weekly file that can be read on demand when filling out hours.

Design
------
- A day-section starts with a line matching `## YYYY-MM-DD`.
- Everything before the first day-section (frontmatter + title + explainer) is
  the PREAMBLE and is always preserved in WORKLOG.md.
- Day-sections are ranked by DATE (descending); the KEEP_SECTIONS newest stay
  live. Ranking is by date, not calendar-age, so a weekend or an idle stretch
  never wipes the last real work (Friday survives to Monday).
- Everything older is appended to docs/worklog-archive/<ISO-year>-W<week>.md,
  bucketed by ISO week (Mon-Sun), sections sorted ascending within the file so
  a week reads Monday-first.
- **Idempotent**: a date already present in its target archive file is not
  re-appended, so re-running is safe.
- **Fail-safe**: a section is only removed from WORKLOG.md after its archive
  write succeeded. If archiving fails, the section stays live rather than
  being lost.
- The archive directory is registered in hippo-index.py's ARTIFACT_DIRS, so it
  renders as a single per-dir count line rather than growing the index by one
  line per week.
"""

import datetime
import os
import re
import sys

KEEP_SECTIONS = 3  # rolling window: the N most-recent dated day-sections stay live

ROOT = os.environ.get("CLAUDE_PROJECT_DIR", ".")

# Knowledge-base root, relative to CLAUDE_PROJECT_DIR. The one thing that
# differs between instances — set it once here and everything else follows.
#   flat layout:   ("docs",)          nested layout: ("docs", "architecture")
KB_DIR = ("docs",)

WORKLOG = os.path.join(ROOT, *KB_DIR, "WORKLOG.md")
ARCHIVE_DIR = os.path.join(ROOT, *KB_DIR, "worklog-archive")

DATE_HDR = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")


def week_file(date_str):
    """Return (path, iso_year, iso_week, monday, sunday) for a YYYY-MM-DD date."""
    d = datetime.date(*map(int, date_str.split("-")))
    iso_year, iso_week, iso_weekday = d.isocalendar()
    monday = d - datetime.timedelta(days=iso_weekday - 1)
    sunday = monday + datetime.timedelta(days=6)
    path = os.path.join(ARCHIVE_DIR, f"{iso_year}-W{iso_week:02d}.md")
    return path, iso_year, iso_week, monday, sunday


def new_archive_preamble(iso_year, iso_week, monday, sunday):
    return (
        "---\n"
        "type: log\n"
        f'summary: "Worklog archive, ISO week {iso_year}-W{iso_week:02d} '
        f'({monday.isoformat()} to {sunday.isoformat()}). Day-by-day record of work done, '
        'drained from the rolling WORKLOG. Source for timesheets and monthly hours logs."\n'
        "status: archived\n"
        "---\n"
        "\n"
        f"# Worklog archive — {iso_year}-W{iso_week:02d}\n"
        "\n"
        f"_{monday.isoformat()} (Mon) to {sunday.isoformat()} (Sun). "
        "Drained from `docs/WORKLOG.md` by the session-start pruner. "
        "Day-sections ascending. Read on demand when filling out timesheets or the "
        "monthly retainer hours log._\n"
        "\n"
    )


def _norm(section_lines):
    """Whitespace-insensitive body compare, so a trailing-newline diff is not an edit."""
    return "\n".join(ln.rstrip() for ln in section_lines).strip()


def split_sections(lines):
    """Return (preamble_lines, [(date, [lines]), ...]) in document order."""
    starts = [i for i, ln in enumerate(lines) if DATE_HDR.match(ln)]
    if not starts:
        return lines, []
    preamble = lines[: starts[0]]
    out = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        out.append((DATE_HDR.match(lines[start]).group(1), lines[start:end]))
    return preamble, out


def archive_section(date, body):
    """Append one day-section to its weekly file. Returns True on success."""
    path, iso_year, iso_week, monday, sunday = week_file(date)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.readlines()
        preamble, sections = split_sections(existing)
        prior = next((s for d, s in sections if d == date), None)
        if prior is not None:
            if _norm(prior) == _norm(body):
                return True  # identical; idempotent no-op
            # Same date, different text: the section was edited after it was
            # archived (a detail remembered a day later). MERGE rather than
            # drop — silently losing a retroactive edit would defeat the point
            # of archiving for hours logs. Keep the archived text, append the
            # new content under a marker.
            merged = list(prior)
            if merged and not merged[-1].endswith("\n"):
                merged.append("\n")
            merged.append("\n_Appended on a later pass (section was edited after archiving):_\n\n")
            merged.extend(body[1:])  # skip the duplicate `## YYYY-MM-DD` heading
            sections = [(d, merged if d == date else s) for d, s in sections]
            body = None  # already merged in place
    else:
        preamble = new_archive_preamble(iso_year, iso_week, monday, sunday).splitlines(True)
        sections = []

    if body is not None:
        sections.append((date, body))
    sections.sort(key=lambda s: s[0])  # ascending within the week

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(preamble)
        for _d, sec in sections:
            f.writelines(sec)
            if sec and not sec[-1].endswith("\n"):
                f.write("\n")
    os.replace(tmp, path)
    return True


def main():
    if not os.path.exists(WORKLOG):
        return
    with open(WORKLOG, encoding="utf-8") as f:
        lines = f.readlines()

    preamble, sections = split_sections(lines)
    if len(sections) <= KEEP_SECTIONS:
        return  # within the window; nothing to drain

    keep_dates = set(sorted({d for d, _ in sections}, reverse=True)[:KEEP_SECTIONS])

    kept, drained_ok = [], set()
    for date, body in sections:
        if date in keep_dates:
            kept.append((date, body))
            continue
        try:
            if archive_section(date, body):
                drained_ok.add(date)
            else:
                kept.append((date, body))
        except Exception as e:
            # Archiving failed — keep the section live rather than lose it.
            print(f"(hippo-worklog-prune: archive failed for {date}: {e})", file=sys.stderr)
            kept.append((date, body))

    if not drained_ok:
        return

    out = list(preamble)
    for _d, body in kept:
        out.extend(body)
    if out != lines:
        with open(WORKLOG, "w", encoding="utf-8") as f:
            f.writelines(out)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never break the hook
        print(f"(hippo-worklog-prune error: {e})", file=sys.stderr)
        sys.exit(0)
