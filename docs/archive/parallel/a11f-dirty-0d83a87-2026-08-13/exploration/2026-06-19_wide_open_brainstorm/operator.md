# Operator

This is the Operator pass for the `wide open brainstorm` room.

The operator view is simple: this product should feel like a local instrument for repeating a job without losing your place. The question is not "what features can we add?" It is "what does the user do 20 times a week, what slows them down, and what makes them trust the result enough to keep going?"

## Real Workflow

The working loop should look like this:

1. Open the source document or image.
2. Inspect the extracted signature or select the region that contains it.
3. Clean or normalize the signature if needed.
4. Store it in the local vault.
5. Choose or confirm the target document.
6. Place the signature on the page.
7. Nudge, rotate, or resize if necessary.
8. Preflight the output before export.
9. Export a new file.
10. Reopen or queue the next job without rebuilding state.

If the product is good, the user should not feel like they are starting over at step 1 every time. They should feel like they are moving through a repeatable machine.

## Five Micro-Decisions The Product Must Make Easier

1. Is this the right signature asset?
2. Is this the right page?
3. Is this the right place on the page?
4. Is the placement good enough to export?
5. Is this a one-off job or a repeatable pattern worth templating?

If those five decisions are hard, everything else becomes friction.

## Batch / Repeat / Template Patterns

The product should assume repeat work exists:

- reuse the last good signature by default when appropriate;
- remember the last successful placement on similar documents;
- support a "repeat this on the next file" action;
- group related documents into a batch lane;
- make templates adapt by document family, not just by pixel coordinates.

The most valuable template is not the most clever one. It is the one that gets the user from "same kind of document again" to "done" with minimal re-entry.

## Recovery, Preview, Undo, Confidence

The operator only trusts what can be recovered:

- show a real preflight preview before export;
- keep undo at the document-operation level, not just the mouse-drag level;
- restore the last stable session after a crash or quit;
- surface unresolved warnings instead of hiding them;
- make confidence visible before the file is written.

The export moment is the truth moment. If the preview and the export diverge, the app loses its operator.

## What Makes It Feel Like A Pro Tool

- remembers last-used signature, folder, and output settings;
- lets the user nudge placement with keyboard-first precision;
- makes batch runs resumable;
- gives the user a fast path to the next document;
- never hides failure behind a cheerful success state;
- makes support triage possible from the app itself.

## Three Strongest Concepts

### 1. Repeat Loop
The core action loop that turns one job into many without rework.

### 2. Safe Preflight
A visible review gate before export that catches the expensive mistakes.

### 3. Resume Lane
A recovery path that preserves the user's momentum after interruption.

## One Non-Obvious Insight

The product should optimize not for the first placement, but for the second identical placement.

That is where the time savings compound and where users decide the tool is worth keeping.

## Time Horizons

### 6 Months
- better keyboard control;
- clearer previews;
- easier reuse of last good placements;
- cleaner batch progress;
- visible confidence and warnings.

### 12 Months
- template inheritance;
- resumable batch lanes;
- richer preflight summaries;
- document-family memory;
- fewer manual confirmations on recurring documents.

### 24 Months
- the product behaves like a local production console;
- repeated document families become almost one-click;
- recovery is routine, not exceptional;
- operators trust the app enough to stop checking everything twice.

