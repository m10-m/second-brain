#!/usr/bin/env bash
# Hippocampus session-start hook.
# Loads the knowledge base into context once per session, so the active agent
# cannot skip the session-start read -- it is already there.
#
# Claude Code invokes this on UserPromptSubmit; Codex invokes it on
# SessionStart. It uses session_id from hook input (JSON on stdin) so concurrent
# sessions do not interfere.
#
# Load-on-demand design: instead of cat-ing every core doc in full (which grows
# unbounded), emit a GENERATED INDEX (one line + token estimate per lobe, from
# each doc's frontmatter) plus MODEL.md in full (the spine). The agent Reads any
# other lobe on demand, budgeting by the token estimates. See hippo-index.py.
#
# Always exit 0; surface errors for the agent to fix rather than blocking the turn.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Read hook input from stdin, extract session_id
INPUT="$(cat)"
SESSION_ID="$(echo "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)"

if [[ -z "$SESSION_ID" ]]; then
  exit 0
fi

MARKER="/tmp/.hippocampus-session-${SESSION_ID}"

# Only run once per session
if [[ -f "$MARKER" ]]; then
  exit 0
fi
touch "$MARKER"

echo "=== SESSION START: Hippocampus context loaded ==="
echo ""

# Hippocampus lint -- mechanical nag (bloating hubs / log-shaped hubs / un-routed
# INTEL backlog / stale summaries / un-reconciled supersessions). Prints only when
# there's something to fix; silent when clean.
if command -v python3 &>/dev/null; then
  LINT_OUT="$(python3 "$REPO_ROOT/.claude/hooks/hippo-lint.py" 2>/dev/null)"
  [[ -n "$LINT_OUT" ]] && { echo "$LINT_OUT"; echo ""; }
fi

# Worklog prune -- keep docs/WORKLOG.md bounded to its rolling window. Silent; the
# worklog is read-on-demand (standup source), never dumped at session start.
if command -v python3 &>/dev/null; then
  python3 "$REPO_ROOT/.claude/hooks/hippo-worklog-prune.py" 2>/dev/null || true
fi

# User identity
echo "--- .claude/user.yml ---"
cat "$REPO_ROOT/.claude/user.yml" 2>/dev/null || echo "(not found -- ask user for name and role)"
echo ""

# Project configuration
echo "--- project.yml ---"
cat "$REPO_ROOT/project.yml" 2>/dev/null || echo "(not found)"
echo ""

# Kickoff check -- a new instance that has not been told what the project is.
# Either signal is enough: project.yml still carries the template's default name,
# or MODEL.md still carries the skeleton's "[date]" placeholder.
if grep -q '^name: "My Project"' "$REPO_ROOT/project.yml" 2>/dev/null \
   || grep -q 'Last updated: \[date\]' "$REPO_ROOT/docs/MODEL.md" 2>/dev/null; then
  echo "--- PROJECT NOT SET UP ---"
  echo "project.yml is still the template default, or MODEL.md is still the empty skeleton."
  echo "After identity, run the kickoff interview (.claude/skills/kickoff/SKILL.md) before other work."
  echo "If the user's first message already describes the project, start from it and ask only about the gaps."
  echo ""
fi

# On-deck slate -- the morning queue. Surfaced FIRST (before the index dump) so it
# lands in the visible session-start preview. Source of truth is the "## On Deck"
# section at the top of docs/TASKS.md; edit it at the end of a session.
TASKS_PATH="$REPO_ROOT/docs/TASKS.md"
if [[ -f "$TASKS_PATH" ]]; then
  ONDECK=$(awk '/^## On Deck/{f=1; next} /^## /{f=0} f' "$TASKS_PATH")
  if [[ -n "${ONDECK//[[:space:]]/}" ]]; then
    echo "--- ON DECK (next-session slate, from docs/TASKS.md) ---"
    echo "$ONDECK"
    echo "---"
    echo ""
  fi
fi

# Knowledge payload: a GENERATED INDEX (one line + token estimate per lobe), not
# full bodies. The agent Reads a lobe on demand, budgeting by the estimates. This
# replaces cat-ing MODEL/PLAN/QUESTIONS/INTEL/... in full. See hippo-index.py.
if command -v python3 &>/dev/null; then
  python3 "$REPO_ROOT/.claude/hooks/hippo-index.py" 2>/dev/null \
    || echo "(hippo-index harvester failed — Read docs/ manually)"
else
  echo "(hippo-index needs python3 — Read docs/MODEL.md + docs/PLAN.md manually)"
fi
echo ""

# MODEL.md is the one body dumped in full -- it is the spine read every session.
echo "--- docs/MODEL.md (the spine — full text) ---"
cat "$REPO_ROOT/docs/MODEL.md" 2>/dev/null || echo "(not found)"
echo ""

echo "=== END SESSION CONTEXT ==="
