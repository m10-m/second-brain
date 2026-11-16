---
name: join
description: Light initialisation for an additional agent session started after, or alongside, one that already ran `wake` today. Does the full context load (payload check, spine, index, On Deck) and a cheap repo check, then goes to the thread named in the arguments or asks which one. It skips the PR, review and tracker sweeps and the slate-wide catch-up, which `wake` already did. Use when the user says "join", "light init", "quick init", or starts a parallel agent. Usage `/join <thread>`.
---

# Join: context load without the sweeps

`wake` already swept PRs, review asks and the tracker today and caught the slate up. This session
loads the same context and skips that work.

## 1. Load the context

- **Payload:** if the hook splits its output into numbered parts, check every part is present and
  none shows as persisted or truncated. If anything is missing, read the payload file the banner
  names before anything else.
- The spine (MODEL.md), the index and On Deck are all in the payload. Read them there. Don't
  re-read whole docs the index already represents.
- **Stop at the index.** Open a `docs/workstreams/*` body only once the thread is known, and only
  that thread's.

## 2. Cheap repo check

```bash
date
git status --short
git branch --show-current
```

Plus branch and dirty count for each submodule in `.gitmodules`. If a submodule is on a feature
branch or dirty, another session probably has it. Say so before switching it.

## 3. Go to the thread

- **A thread named in the arguments:** match it to its On Deck entry and open that entry's warm
  doc. Check that thread's own PRs and tickets live, then start.
- **No thread named:** list the On Deck headings one line each and ask which.

This session keeps its own thread's On Deck entry current as the work moves, like any other
session. The slate-wide catch-up stays with `wake`.

## 4. Report

Three lines at most: payload OK, repo state, and the thread with where it stands.
