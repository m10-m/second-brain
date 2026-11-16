#!/usr/bin/env python3
"""Hippocampus lint -- the mechanical nag that replaces willpower.

Surfaces, at session start, the failure modes the index/load-on-demand design is
meant to prevent:
  1. A hub lobe over the line cap (state doc bloating).
  2. A hub that has turned log-shaped (many dated entries = it's becoming a log).
  3. The INTEL drain backlog (RAW entries pooling with no exit pressure).
  4. A hub whose frontmatter summary has frozen behind the body (the index line --
     the only thing read at session start -- no longer describes current state).
  5. A DECISIONS entry that supersedes a published contract without reconciling it.

Prints a compact block ONLY when there is something to nag about; silent when clean.
stdlib only.
"""
import os
import re
import datetime

ARCH = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), "docs")
HUB_LINE_CAP = 700
LOG_SHAPE_THRESHOLD = 6  # dated headings in a hub body before it reads as a log
# A hub's summary reads as stale when the body has dated activity this many days
# newer than the newest date the summary itself cites. A margin (not >0) so a
# same-week consolidation edit doesn't nag; only a summary months behind fires.
# Partial by design: only catches summaries that cite a date at all (a dateless
# summary can't be compared and never flags) -- one signal, not a full detector.
STALE_SUMMARY_DAYS = 30
# A DECISIONS entry that supersedes a published contract must reconcile that
# contract (e.g. a proposals/ doc + its published canonical), not just record the
# decision -- otherwise someone keeps building the superseded shape. Lint flags a
# supersession entry that cites a contract but carries no `Reconciled:` marker;
# adding the marker (once the contract is updated) clears it, so this is
# self-silencing, not a standing nag. Grandfathered: only entries on/after the
# convention start are in scope. SET THIS to the date your instance adopted the
# marker convention (default: epoch = applies to all entries).
RECONCILE_CONVENTION_START = datetime.date(1970, 1, 1)
SUPERSEDE = re.compile(r"supersede|superseded|supersedes|revers(?:e|es|ed|al)", re.I)
# Adjust CONTRACT_REF to match how your instance links published contracts
# (a proposals/ path and/or your publishing host, e.g. Notion/Confluence URLs).
CONTRACT_REF = re.compile(r"proposals/|app\.notion\.com|notion\.so", re.I)
RECONCILED_MARKER = re.compile(r"reconciled", re.I)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# A hub reads as a log when it accumulates dated entries: either dated headings
# (## 2026-..) or dated bold-lead paragraphs (**Status note (2026-..)**, **Update (..)**).
DATED = re.compile(
    r"(?m)^(?:#{2,4}\s+\d{4}-\d{2}-\d{2}"
    r"|\*\*(?:Status note|Update|Correction|Note|Done)\b[^\n]{0,30}\d{4}-\d{2}-\d{2})"
)


def _frontmatter_field(text, key):
    if not text.startswith("---"):
        return ""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return ""
    for line in m.group(1).splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def frontmatter_type(text):
    return _frontmatter_field(text, "type")


def _newest_date(strings):
    out = []
    for s in strings:
        for d in DATE.findall(s):
            try:
                out.append(datetime.date(*map(int, d.split("-"))))
            except ValueError:
                pass
    return max(out) if out else None


def lint():
    issues = []

    # 1 + 2 + 4: hub caps, log-shape, frozen summary
    for fn in sorted(os.listdir(ARCH)):
        path = os.path.join(ARCH, fn)
        if not (fn.endswith(".md") and os.path.isfile(path)):
            continue
        text = open(path, encoding="utf-8").read()
        if frontmatter_type(text) != "hub":
            continue
        nlines = text.count("\n") + 1
        if nlines > HUB_LINE_CAP:
            issues.append(f"hub over cap: {fn} {nlines} lines (cap {HUB_LINE_CAP}) — compact / split to a workstream")
        dated = DATED.findall(text)
        if len(dated) > LOG_SHAPE_THRESHOLD:
            issues.append(f"hub looks log-shaped: {fn} has {len(dated)} dated entries — move history to cold/archive, keep present-tense state")
        s_new = _newest_date([_frontmatter_field(text, "summary")])
        b_new = _newest_date(dated)
        if s_new and b_new and (b_new - s_new).days > STALE_SUMMARY_DAYS:
            issues.append(
                f"summary may be stale: {fn} summary cites {s_new} but body has dated activity through "
                f"{b_new} ({(b_new - s_new).days}d newer) — refresh the frontmatter summary (it's the index line)"
            )

    # 3: INTEL drain backlog
    intel = os.path.join(ARCH, "INTEL.md")
    if os.path.exists(intel):
        text = open(intel, encoding="utf-8").read()
        entries = re.split(r"(?m)(?=^## )", text)[1:]
        raw = [e for e in entries if "✅ PROCESSED" not in e and "✅ RESOLVED" not in e]
        dates = []
        for e in raw:
            dm = re.match(r"## (\d{4})-(\d{2})-(\d{2})", e.lstrip("# ").strip()) or re.search(
                r"(\d{4})-(\d{2})-(\d{2})", e.splitlines()[0]
            )
            if dm:
                try:
                    dates.append(datetime.date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))))
                except ValueError:
                    pass
        if raw:
            oldest = min(dates) if dates else None
            age = (datetime.date.today() - oldest).days if oldest else "?"
            tail = f", oldest {oldest} ({age}d)" if oldest else ""
            issues.append(f"INTEL backlog: {len(raw)} RAW entries un-routed{tail} — route at ingest; don't let it pool")

    # 5: a recent DECISIONS supersession left its published contract un-reconciled
    decisions = os.path.join(ARCH, "DECISIONS.md")
    if os.path.exists(decisions):
        text = open(decisions, encoding="utf-8").read()
        for entry in re.split(r"(?m)(?=^#{2,3}\s+\d{4}-\d{2}-\d{2})", text):
            head = entry.lstrip("# ").strip().splitlines()[0] if entry.strip() else ""
            dm = DATE.search(head)
            if not dm:
                continue
            try:
                edate = datetime.date(*map(int, dm.group(0).split("-")))
            except ValueError:
                continue
            if edate < RECONCILE_CONVENTION_START:
                continue
            if (
                SUPERSEDE.search(entry)
                and CONTRACT_REF.search(entry)
                and not RECONCILED_MARKER.search(entry)
            ):
                issues.append(
                    f"DECISIONS {edate}: supersedes a published contract but has no "
                    f"`Reconciled:` marker — update the published contract (engineers build "
                    f"from the contract, not DECISIONS), then add a `**Reconciled:** <docs>` "
                    f"line to the entry to clear this"
                )

    return issues


def main():
    issues = lint()
    if not issues:
        return
    print("--- HIPPOCAMPUS LINT (mechanical nag — fix or it compounds) ---")
    for i in issues:
        print(f"  ⚠ {i}")
    print("---")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"(hippo-lint error: {e})")
