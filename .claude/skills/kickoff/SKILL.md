---
name: kickoff
description: First-run project interview for a new Hippocampus instance. Finds out what the project is, what done looks like, who is involved, what is in flight and what material exists, then writes project.yml and first drafts of the hub docs. Use when the session-start payload says PROJECT NOT SET UP, when the docs are still empty skeletons, or when the user says "kickoff", "set this up" or "new project", or describes a new project in their first message.
---

# Kickoff: the first-run project interview

A new instance knows where things go and nothing about the project. This interview closes that gap before any other work, so the first real session starts from a mental model instead of empty files. It runs once per instance.

Identity comes first. If `.claude/user.yml` is missing, run the identity flow in `.claude/rules/role.md`, then come back here. The person setting up a new instance is its owner, so use their role as `owner_role` unless they say otherwise.

## 1. Start from what you have been told

People usually open a new instance by describing the project. Read their first message, and anything they pasted or pointed at, before asking anything. Note which topics below it already answers, ask only about the gaps, and play back what you understood so they can correct it.

If they have told you nothing, open with one plain question: "What is this project, and what are you trying to get done?"

## 2. Interview

Cover these a few questions per turn, as a conversation rather than a form. Follow their answers; the order is only a guide.

| Topic | What you are after | Lands in |
|---|---|---|
| The project | What it is, why it exists, where it stands now | `project.yml` description, MODEL |
| Done | What success looks like, deadlines, what is at stake | MODEL, PLAN |
| Their part | Their role in it, what they own, what they decide | MODEL, `owner_role` |
| People | Who is involved, what each knows or decides, who to ask about what | PEOPLE |
| In flight | Threads under way now and the next few things to do | PLAN, TASKS On Deck |
| Unknowns | What they don't know yet and need to find out | QUESTIONS |
| Material | Documents, repos, notes and systems this brain should read or connect to | follow-up debriefs |
| Words | The domain's own terms (a "matter" rather than a workstream, a "position" rather than a decision) | `project.yml` vocabulary |
| Boundaries | Anything confidential, or anything that must never leave this repo | MODEL, plus a rule if it is high-stakes |

Be opinionated as you go: reflect back the shape you are hearing, name tensions, and ask what you would need to know to be useful tomorrow. Stop when you can write a first model they would recognise. Completeness is not the goal, because debriefs fill in the rest. Two or three rounds is typical.

## 3. Write the first drafts

Show a short summary of what you will write, get a yes, then write:

- **`project.yml`**: `name`, `domain`, `description`, `owner_role`, a `persona` fitted to the work, and `vocabulary` overrides if the domain has its own terms.
- **`docs/MODEL.md`**: the first mental model. Replace the template comment and the `[date]` placeholder, and keep it short.
- **`docs/PLAN.md`**, **`docs/PEOPLE.md`**, **`docs/QUESTIONS.md`**: what the interview surfaced and nothing invented.
- **`docs/TASKS.md`**: the next session's slate under On Deck.
- **`docs/INTEL.md`**: the interview itself, under today's date, attributed to the user.
- Each touched doc's frontmatter `summary`, so the session-start index describes it.

Hold off on workstream docs unless a thread is clearly big enough to need one. Structure grows from the work (see `.claude/rules/hippocampus-updates.md`).

## 4. Hand off

Tell the user what you wrote, in a few lines. Then offer the next step: material they mentioned goes in through `/debrief` (paste notes, or point at documents and repos so you can read them), and any system they want connected gets set up next.
