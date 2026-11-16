---
name: voice-calibration
description: Write any message that goes to a named human recipient in the principal's own voice rather than in assistant prose. Use before drafting or revising a Slack message, DM, email, PR/MR review comment, ticket comment, or any short outward-facing note. Activates on "draft a message", "reply to", "put it in the composer", "send them", "write to", "draft a Slack", "comment on the PR", or any request to compose something a person will read as being from the principal. Also load it when editing a draft that has already been reviewed, since the failure mode is drift on the second pass.
---

# Voice calibration

Assistant prose and a human's prose differ in a consistent, correctable way, and the gap is invisible from inside a draft. This skill is the **method**. The principal's actual voice is **data**, and it lives outside this file.

Scope: **messages to named recipients only.** Slack, DM, email, PR and ticket comments. Not the internal knowledge base, which is deliberately a denser working voice. Not session chat.

## Load the principal's voice file first

1. Read `.claude/user.yml` for the principal.
2. Read `.claude/voice/<principal-slug>.md`. That file holds the corpus samples and the evidence-tagged rules.
3. If it does not exist, say so rather than guessing, and offer to start one. **An invented voice is worse than plain prose**, because it reads as deliberate.

Per-audience calibration is not here and not in the voice file. It lives in the project's own publishing rule: who the audiences are, register for client deliverables, what must never be surfaced to a given person, which internal identifiers are suppressed. **The test: would this still be true if the principal changed clients?** If no, it belongs to the project.

## Length and structure come before any line-level tweak

The most common failure is not word choice. It is that the draft arrives as a document when the medium wanted a message: multi-paragraph, bold headers, tables, bullet lists, where the principal writes two sentences and no formatting.

So **check the shape against the corpus before checking the wording.** If the corpus median is short and unformatted, write the short version and offer the long one rather than defaulting to it. A long structured post is a deliberate exception for a rollout or an announcement, not the house style.

## Answer the question, then stop announcing things

Two assistant habits get cut from drafts more reliably than any word choice.

**Answer the question that was actually asked, in a sentence, before anything else.** Asked "how difficult will this be to add?", a draft returned a landscape of the pieces and a question about prioritisation, and never said how difficult. The principal added the answer themselves as a **separate short message**: "long story short; the actual work is easy, especially in the age of LLMs, it's a very light lift. Sourcing the data is the only challenge and it's not a technical one." Analysis supports a verdict, it does not replace one. **If the ask has a one-line answer, lead with it or send it on its own.**

**Do not announce the move you are about to make.** "Worth being precise about what this gives us though, because it's less than it looks" became "But maybe that's not that critical." "The one piece with no clean route is the connection list" became "The murky bit is the connection list." The framing sentence adds nothing the next sentence does not already carry, and colloquial beats precise-and-stiff.

The family to watch is "worth saying / worth noting / worth stating / worth knowing / worth flagging". Counted across one session's written output: **42 instances**. Each one is a sentence whose whole job is to tell the reader the next thing matters.

**And cut your own verdicts and instructions.** "I'd leave that alone" was deleted. So was a closing paragraph arguing where a feature belonged. State what is true and let the recipient draw the conclusion, or ask them for it.

**What survives edits verbatim: facts, file references, and explicit uncertainty.** A paragraph naming the exact tiers, saying "counts, not names", and admitting "may be able to, and we'd have to check" was kept word for word. So precision on checkable things is wanted. It is the connective furniture around them that is not.

## AI tells are a density problem, not a banned-word list

**Almost every item on a tells list is ordinary English that humans write.** "It's not X, it's Y" happens naturally. So does "load-bearing", a three-item list, a both-sides sentence. **What marks the prose is frequency, not occurrence.** One instance in a message reads as a person making a point. Five in one document reads as a signature.

So the check is a count, not a search. Before anything goes out, grep the tells and look at the **rate**: roughly one instance of any single tell per document is unremarkable, and the same phrase three or more times in one piece is the thing to fix. Fix it by cutting the repeats, not by hunting the construction to extinction.

**Over-correcting is its own tell.** Prose with every natural emphasis surgically removed reads stilted, and stilted is more obviously machine-written than an occasional "not just X, it's Y". A voice file that bans a construction the principal themselves uses is calibrating against a style guide rather than against a person.

Measured example, 2026-08-20: across one session's written output, "genuinely" appeared **12** times, "not just" **5**, "load-bearing" **2**. The one worth acting on was the first. Two instances of a distinctive phrase across a day of work is not a problem; twelve of a filler adverb is.

**The one exception is absolute: no em-dashes.** That is a character rather than a construction, the principal has stated it as a hard rule repeatedly, and it is independently written into four separate project rule files. Zero, not "sparingly".

## Evidence discipline

Every rule in a voice file carries its evidence, and the tiers are load-bearing:

- **Hypothesis.** Seen once, in one message, to one recipient. Apply lightly. Do not build a formula from it.
- **Voice.** Three or more instances across at least two audiences.

Promote only on new evidence. If a hypothesis is contradicted, delete the row rather than hedging it, and record the contradiction. This exists because a single edited draft yields a dozen plausible-looking rules and most of them are that-message-specific.

## Harvesting a corpus without contaminating it

**The trap: a large share of the principal's sent messages were drafted by an assistant and sent by them.** They carry no attribution. Mining them teaches the assistant its own style back with the principal's signature on it, which is worse than no corpus because it reads as validation. This has already happened once: Slack drafts were being calibrated against the assistant's own earlier posts in the same channel.

Discriminators, best first:

1. **A draft that survives an edit is the highest-signal item available.** Deletions show what the principal removes, and sent messages never can. Capture the before and after as a pair every time it happens.
2. **Orthographic noise proves a human typed it.** Typos, lowercase sentence starts, doubled spaces after a period. Assistants do not produce these.
3. **Length and absence of markdown.** Short, conversational, unformatted: almost certainly theirs.
4. **A programmatic-send marker** in the rendered message (for example `Sent using <name>'s Slack Bot`) means assistant-authored. Often visible when reading a channel but not searchable.
5. **Multi-paragraph with bold headers, tables or per-person sections: treat as assistant-authored** unless a diff proves otherwise.

Exclude 4 and 5, weight 1 and 2 highest, and **record which discriminator qualified each sample** so a later pass can re-judge rather than inherit.

**Harvest per workspace, from inside the project that reaches it.** A chat connection reaches one workspace. A workspace where the engagement is young and much of the volume is assistant-drafted is a small and contaminated corpus; prefer one with a long human history.
