#!/usr/bin/env python3
"""Hippocampus index harvester.

Walks docs/, reads each lobe's frontmatter, and emits one compact index:
summary + token estimate per lobe, grouped by type. This is the entire knowledge
payload at session start. Bodies are NOT dumped -- the agent Reads a lobe on
demand, budgeting by the token estimate shown here. This replaces cat-ing every
core doc in full (which grows unbounded) with a few-KB index.

Frontmatter schema (YAML-ish, top of file, between --- fences):
    ---
    type: hub | reference | log | stub        # default: unclassified
    summary: one-line current-state summary    # shown in the index
    aliases: [term, term]                       # recall triggers (optional)
    status: active | archived                   # default: active
    ---

Convention for the canonical lobes:
- hub:       MODEL / PLAN / QUESTIONS / PEOPLE and anything under workstreams/
             (current state; the agent reads the one its task touches).
- reference: TASKS, runbooks, catalogs (long; load only when relevant).
- log:       DECISIONS / INTEL (cold audit + evidence; read only to answer "why").

Design notes:
- stdlib only (no PyYAML); parses the flat keys we use, nothing fancier.
- A lobe with no frontmatter still appears, flagged, so nothing hides.
- type=log / status=archived render as COLD (never auto-loaded).
"""

import os
import re
import sys

ARCH_DIR = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), "docs")

# Directories whose contents are cold archive -- listed compactly, never detailed.
ARCHIVE_DIRS = {"archive", "ledger"}
# Artifact stores: supporting docs (resume notes, published-proposal stubs, dated
# audits, diagrams), NOT resident lobes. Summarized as a per-dir count, not
# enumerated -- discover by `ls`/grep when a task needs one. No frontmatter needed.
ARTIFACT_DIRS = {
    "comms", "proposals", "reports", "diagrams",
    # Weekly worklog archive drained from WORKLOG.md by hippo-worklog-prune.py.
    # One count line, never enumerated — otherwise it grows the index by a line
    # per week. Read a specific week on demand for timesheets / hours logs.
    "worklog-archive",
}
# Files to skip entirely (self-referential / scaffolding). Add instance-specific
# entries here (e.g. a standalone audit-plan a lobe shouldn't surface).
SKIP = set()


def parse_frontmatter(text):
    """Return (meta dict, body_without_frontmatter). meta empty if no fences."""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    meta = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        meta[key] = val
    return meta, body


# Bytes per token. NOT the usual chars/4 rule of thumb.
#
# Knowledge-base docs tokenize far worse than prose: they are dense with markdown
# links, ticket IDs, file paths, commit SHAs and URLs, all of which fragment into
# many tokens each. Measured on a real instance (2026-07-27): a 148,753-byte
# session-start payload came to ~60.3k tokens, i.e. ~2.47 bytes/token — chars/4
# under-reported it by ~40%.
#
# This matters more than it looks. The whole load-on-demand design tells the agent
# to budget its reads off the estimates printed in this index, so an estimator that
# is systematically low produces systematically bad budgeting decisions.
#
# To recalibrate for your own corpus: take a known payload, get its real token count
# from your tooling, and divide byte size by that.
BYTES_PER_TOKEN = 2.5


def est_tokens(text):
    return max(1, round(len(text) / BYTES_PER_TOKEN / 1000, 1))  # thousands of tokens


def collect():
    lobes = []
    artifacts = {}  # dir -> [count, total_tokens]
    for root, _dirs, files in os.walk(ARCH_DIR):
        rel_root = os.path.relpath(root, ARCH_DIR)
        parts = rel_root.split(os.sep)
        in_archive = any(p in ARCHIVE_DIRS for p in parts)
        artifact_dir = parts[0] if parts[0] in ARTIFACT_DIRS else None
        for fn in sorted(files):
            if not fn.endswith(".md") or fn in SKIP:
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, ARCH_DIR)
            if artifact_dir:
                try:
                    sz = os.path.getsize(path)
                except OSError:
                    sz = 0
                entry = artifacts.setdefault(artifact_dir, [0, 0.0])
                entry[0] += 1
                entry[1] += round(sz / BYTES_PER_TOKEN / 1000, 1)
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except OSError:
                continue
            meta, _body = parse_frontmatter(text)
            ltype = meta.get("type", "")
            status = meta.get("status", "active")
            if in_archive:
                ltype, status = "log", "archived"
            lobes.append(
                {
                    "rel": rel,
                    "type": ltype,
                    "summary": meta.get("summary", ""),
                    "status": status,
                    "tok": est_tokens(text),
                    "has_fm": bool(meta),
                }
            )
    return lobes, artifacts


def fmt(lobe):
    flag = "" if lobe["has_fm"] else "  ⚠ no-frontmatter"
    summ = lobe["summary"] or "(no summary)"
    return f"  {lobe['rel']:<42} ~{lobe['tok']}k  {summ}{flag}"


def main():
    lobes, artifacts = collect()
    if not lobes:
        print("(no lobes found under docs/)")
        return

    # Hubs (type: hub) split into LOBES -- top-level brain regions (MODEL/PLAN/
    # QUESTIONS/PEOPLE) -- and WORKSTREAMS -- per-stream detail under workstreams/.
    # Together they are the "hubs" tier. References (incl. runbooks + stubs that
    # live under workstreams/) and cold logs are separate tiers.
    active_hub = lambda l: l["type"] == "hub" and l["status"] == "active"
    lobes_top = [l for l in lobes if active_hub(l) and not l["rel"].startswith("workstreams/")]
    streams = [l for l in lobes if active_hub(l) and l["rel"].startswith("workstreams/")]
    refs = [l for l in lobes if l["type"] == "reference" and l["status"] == "active"]
    cold = [l for l in lobes if l["type"] == "log" or l["status"] == "archived"]
    classified = {id(l) for l in lobes_top + streams + refs + cold}
    other = [l for l in lobes if id(l) not in classified]

    print("=== HIPPOCAMPUS INDEX — lobe map. Read a body on demand; budget by ~tokens. ===")
    print("MODEL.md (the spine) is dumped in full below. Everything else loads on demand.\n")

    if lobes_top or streams:
        print("HUBS — the durable state (lobes + workstreams):")
    if lobes_top:
        print(" LOBES — top-level brain regions:")
        for l in sorted(lobes_top, key=lambda x: x["rel"]):
            print(fmt(l))
    if streams:
        print(" WORKSTREAMS — per-stream detail (read the one your task touches):")
        for l in sorted(streams, key=lambda x: x["rel"]):
            print(fmt(l))
    if lobes_top or streams:
        print()
    if refs:
        print("REFERENCE — runbooks / catalogs (long; load only when relevant):")
        for l in sorted(refs, key=lambda x: x["rel"]):
            print(fmt(l))
        print()
    if cold:
        print("COLD — audit/evidence/archive. DO NOT auto-load; read only to answer 'why':")
        for l in sorted(cold, key=lambda x: x["rel"]):
            print(f"  {l['rel']:<42} ~{l['tok']}k  {l['summary'] or '(audit log)'}")
        print()
    if artifacts:
        print("ARTIFACT STORES — supporting docs, not lobes. `ls`/grep the dir when a task needs one:")
        for d in sorted(artifacts):
            cnt, tok = artifacts[d]
            print(f"  {d}/{'':<40} {cnt} docs (~{round(tok)}k total)")
        print()
    if other:
        print("⚠ UNCLASSIFIED — needs frontmatter (type/summary):")
        for l in sorted(other, key=lambda x: x["rel"]):
            print(fmt(l))
        print()

    print("=== END INDEX ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never break the hook
        print(f"(hippo-index harvester error: {e})", file=sys.stderr)
        sys.exit(0)
