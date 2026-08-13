# Archivist

The Archivist is the room’s memory engineer: the role that turns a wide open brainstorm into durable product intelligence. This role does not just summarize ideas. It preserves meaning, keeps the best decisions legible, and makes sure the product can recover when a user, a session, or the model loses context.

## Core mandate

- Capture the few truths that should survive beyond the current session.
- Synthesize scattered ideas into reusable product knowledge.
- Protect long-term coherence across UI, workflows, naming, and recovery.
- Separate signal from residue so the product stays sharp instead of bloated.
- Make the system easier to resume after interruptions, failures, or context loss.

## What should be remembered

Remember the things that compound:

- the user’s stable goals and recurring jobs-to-be-done
- proven workflows that reliably lead to successful extraction, signing, export, or recovery
- user corrections, preferences, and repeated pain points
- canonical names for features, states, and objects
- decisions that affect later workstreams or other roles
- patterns that make support, onboarding, or troubleshooting faster next time
- recovery anchors such as last good state, last successful export, and last known working path

In a product like SignKit, the Archivist should especially remember:

- what kind of document the user was working on
- whether they were extracting, cleaning, placing, signing, or exporting
- which step failed, and what fixed it
- which signatures, templates, or settings are worth reusing
- the smallest context needed to resume without confusion

## What should be surfaced

Surface memory only when it helps the user move:

- “You already solved this once, here is the path that worked.”
- “This looks like the same failure mode as last time.”
- “You have a saved signature/template that matches this task.”
- “The last successful state was X, and here is the fastest recovery route.”
- “These two ideas keep recurring, so they probably belong to one product concept.”

Surface the smallest useful unit, not the whole history. The goal is a recovery ramp, not a dump of logs.

## What should be forgotten

Forget noise on purpose:

- one-off experiments that never repeated
- transient implementation details that do not affect future decisions
- debugging clutter that does not explain a failure pattern
- redundant idea variants once a clearer concept has been named
- obsolete assumptions that have already been superseded

The Archivist should help the room forget the wrong things, especially stale state that makes future work heavier than it needs to be.

## How the product gets smarter over time

The product gets smarter when every important interaction leaves behind a usable trace:

- successful extractions teach the system what “good” looks like
- failed attempts teach it where users get stuck
- repeated edits teach it which defaults are wrong
- saved outputs teach it which quality bar the user trusts
- recovery events teach it how to rebuild context with minimal friction

The learning loop should be explicit:

1. Capture the action.
2. Capture the outcome.
3. Capture the correction, if any.
4. Convert the correction into a reusable rule, preference, or recovery hint.
5. Promote repeated patterns into defaults.

Over time, the app should stop acting like a passive tool and start behaving like a memoryful assistant that recognizes the user’s working style.

## Recovery when context is lost

Recovery is a first-class product behavior, not an error state.

When context is lost, the user should be able to recover through a short chain:

- what was I doing
- what was the last good state
- what failed
- what is safe to retry
- what should I restore from memory

Good recovery flows include:

- a “resume work” entry point that opens the last meaningful task
- a compact session summary with the last successful operation
- visible recent artifacts: images, PDFs, exports, signatures, templates
- explicit rollback to the last stable extraction or placement state
- a “restore from memory” option that rebuilds the most likely next step
- a way to continue even if some details are missing, with clear uncertainty labels

For this room, recovery means the product can say: “Here is what I think you were doing, here is what I know for sure, and here is the safest way to continue.”

## Learning loops

The Archivist should close loops at three levels:

- session loop: what happened in this run
- workflow loop: what happened across a repeated task
- product loop: what should change in the app because the same friction keeps appearing

Each loop should record:

- trigger
- action
- result
- user correction
- durable lesson

This is how the product improves without needing the team to rediscover the same lessons every week.

## Three strongest concepts

### 1. Memory Spine
The core durable record of what the user did, what worked, and what must be recoverable later. It keeps the product’s history narrow, trustworthy, and easy to traverse.

### 2. Recovery Beacon
A visible “you are here” system for lost-context moments. It turns failure into orientation by showing the last known good path, the likely next action, and the safest way to continue.

### 3. Learning Ledger
The compounding layer that converts repeated corrections into smarter defaults, better prompts, and more reliable workflows. It is the product’s long-term memory of what actually helps.

## Time horizons

### 6 months
- reliable session summaries
- last-known-good recovery states
- basic preference memory for common extraction and export choices
- reusable templates and signatures with clearer provenance
- compact history that helps users resume without reorienting from scratch

### 12 months
- cross-session memory of recurring workflows
- smarter surfacing of likely next actions
- pattern detection for repeated failures and repeated wins
- more structured recovery from partial loss, failed exports, or interrupted work
- stronger defaults tuned by observed behavior rather than guesswork

### 24 months
- a true memory layer that understands task families, not just files
- automatic synthesis of user habits into workflow shortcuts
- context recovery that works across devices, sessions, and document types
- assistant behavior that can explain why it is recommending a step
- product intelligence that compounds from real usage instead of static rules

## Non-obvious insight

The thing most people miss about this wide open brainstorm is that memory should not try to preserve everything. It should preserve the shape of a successful recovery.

Users do not need the app to remember every detail forever. They need it to remember enough to re-enter the flow confidently when context is missing.

## Recovery and learning loops to keep alive

- When a task ends well, record the path that got there.
- When a task fails, record the smallest missing piece.
- When the user corrects the app, turn the correction into a reusable rule.
- When the same pattern repeats, elevate it into a default.
- When the product cannot be certain, show what it knows, what it infers, and how to continue safely.

## Archivist voice

The Archivist should be calm, precise, and quietly opinionated. It should favor long-term coherence over novelty, but it should not become a museum. Its job is to keep the product alive, resumable, and progressively smarter.

