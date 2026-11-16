# Ping me when a long runner finishes

Standing order, all projects: when background work that took a while completes, send a
`PushNotification`. Do not wait to be asked, and do not just print the result and move on —
the whole point of a long runner is that I started it and went to do something else, so the
result reaches nobody until something pulls me back.

**What counts as a long runner.** Anything where I plausibly walked away:

- A `Workflow` run (these are always long enough to qualify).
- A background `Bash` command, or any foreground one that ran past ~2 minutes.
- A full test suite, a build, a `docker pull`/`build`, a deploy, an `sst diff`, a migration.
- A remote or scheduled agent finishing.
- A long `/loop` iteration reaching a conclusion worth knowing.

**What does NOT.** A quick command, a file read, a lint pass, routine progress within a task
I am clearly watching, or a second notification about work I was already notified about. The
tool suppresses a ping when I am demonstrably at the terminal, so a "not sent" result is
fine and needs no retry or comment.

**Write the message as the outcome, not the event.** I need to decide whether to come back
now, and "task done" tells me nothing. Lead with the verdict and the number:

- Good: `code review back: 3 confirmed findings, 1 is an auth bypass in the api-proxy`
- Good: `ai-stacks suite green: 12,666 passed. ai-assemble 19 failures, all stale node_modules`
- Good: `sst diff failed: dockerfile path resolves relative to context, not repo root`
- Bad: `the review finished` / `tests complete` / `done, see above`

If the result is a failure or needs a decision from me before anything else can move, say so
in the first few words. Keep it one line, under 200 characters, no markdown.

**Also ping when a long runner needs me mid-flight**, not only at the end: it is blocked on an
interactive login, it wants a destructive-action confirmation, or it has been running long
enough that the estimate was clearly wrong.

_Prompted 2026-08-03: a high-effort workflow-backed code review was launched in the
background over four working trees and I asked to be pinged, then asked for it to become a
rule "especially for big long runners"._
