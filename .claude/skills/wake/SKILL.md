---
name: wake
description: Full session initialisation for the first session of the day, or the first after a gap of a few hours. Verifies the Hippocampus payload loaded, checks live state against the On Deck slate, sweeps your open PRs and review asks, reconciles the issue tracker, catches the slate up, then recommends one thread and stops. Use when the user says "wake", "good morning", "initialise fully", "init", "catch up", or starts the day. For an extra agent started alongside a session that already ran this, use `join` instead.
---

# Wake: full initialisation

This is the procedure `.claude/rules/session-start.md` describes, as one command. That rule is the
authority; where they disagree, the rule wins and this file is stale.

**It stops at the index.** No `docs/workstreams/*` body is opened here. Warm docs load after the
user picks a thread, and only that thread's.

Steps 3 and 4 depend on tooling your instance may not have (a GitHub CLI, a chat tool, an issue
tracker). Run what exists, skip what doesn't, and say which steps you skipped.

## 1. Did the payload load?

The session-start hook injects `project.yml`, On Deck, the generated index and MODEL.md. If your
instance splits the payload across several hook outputs (a banner like `[HIPPO PART k/N]`), check
that every part from 1 to N is present and that none shows as persisted or truncated output. If
anything is missing, read the payload file the banner names before doing anything else. A banner
saying "loaded" is no evidence that it did.

## 2. Live state (cheap, run in parallel)

```bash
date
git status --short
git branch --show-current
```

Then, for each submodule or companion repo listed in `.gitmodules` (or named in `project.yml`):
current branch, dirty file count, and commits behind its upstream default branch. Flag any
checkout parked on a merged branch or far behind. Leave it where it is. Don't run
`git submodule update`, which can reset a checkout another session is using.

**Every PR the slate names.** Pull the PR links out of `docs/TASKS.md` and look each one up:

```bash
grep -oE 'github.com/[^/]+/[^/]+/pull/[0-9]+' docs/TASKS.md | sort -u |
while read u; do o=$(echo $u | cut -d/ -f2); r=$(echo $u | cut -d/ -f3); n=${u##*/}
  gh pr view $n --repo $o/$r --json state,mergedAt,reviewDecision,updatedAt \
    --jq "\"$r#$n \(.state) \(.reviewDecision) upd=\(.updatedAt[0:10])\""; done
```

A slate entry that says "open" or "waiting" about a PR that has merged or closed is a delta. Adapt
the command to your forge if it isn't GitHub.

## 3. Your PRs and review asks

Skip this step if the project has no code review surface.

- **Your open PRs, scoped to the project's org or repos.** Your account may carry unrelated
  projects, so filter on the owner rather than taking an account-wide search. Any open PR the slate
  doesn't mention is a delta.
- **Bot and reviewer state on yours.** If your instance has a PR sweep script, run it on each PR
  updated since the last session and report anything it flags or fails to run. A clean exit means
  the threads it knew about were resolved. It doesn't mean a review bot is satisfied, so read the
  bot's own verdict line too. Without a script, read the reviews, inline comments and top-level PR
  comments, because a reviewer can leave findings on any of the three.
- **Review asks of the user.** If the team asks for reviews in chat rather than on the forge, search
  chat first, over the window since the last working day, then use the forge's review-requested
  search as a supplement. Set which surface is primary in `project.yml` or the instance rules. Use
  the search tool that covers private channels, since a public-only search returns nothing for
  them and that looks the same as an empty board.
- **Coverage test for each ask.** A PR is covered once anyone reviews it who is neither the author
  nor a bot, because an author replying to threads shows up as a review. The exception is a named
  half of the review ("you for the read"); that half stays the user's whoever else reviewed. The
  user's own stale change-request with a push since is also theirs.

## 4. Issue tracker

Skip this step if the project has no tracker, or the tracker isn't reachable from here.

If your instance has a script that reconciles the tracker against On Deck, run it and read its
output. Otherwise run two bounded queries, titles and status only: open items assigned to the user,
and open items the user created. Then report **mismatches, not the list**:

- a ticket in flight that no slate entry mentions
- a slate thread with no ticket
- a ticket marked done whose work isn't

For each slate ticket that is closed in the tracker, find what closed it. A reference in a commit
message closes the ticket, not the scope item, so a multi-item ticket cited from a partial PR reads
as finished when it isn't. Decide whether it was a real completion. If a check could not run, say
so. A failed look must never read as a clean one.

## 5. Catch the slate up

Edit `docs/TASKS.md` § On Deck for each delta that has been verified: a merged PR, a finished
ticket, or a "next" that has shipped. Delete completed blocks outright; don't relabel them as
history. Keep the section short. Use exact-string edits, never range replacements, and change only
lines a live check contradicted. Interpretation is the user's.

This slate-wide catch-up is `wake`'s job alone. `join` sessions keep only their own thread's entry
current.

## 6. Report, then stop

- One line confirming the payload and repo state, and whether anything is dirty or behind.
- **Deltas, not the enumeration:** what the slate had wrong (and that it is now fixed), owed review
  asks, your PRs needing attention, and tracker mismatches.
- **Recommend one thread**, and flag any with a deadline.
- Ask which thread. Don't pre-load anything.

Follow the project's rule for citing PR and ticket references (title and repo named) if it has one.
