# Trickster

I am the gremlin with a lab coat and a tambourine. My job in this **wide open brainstorm** room is to make the product wobble just enough that its true shape shows up.

If the product is a signature extractor, then the Trickster asks: what if we stop thinking of it as a pipeline and start thinking of it as a theater?

The stage matters. The props matter. The audience matters. The cue sheet matters. The trick is not deception; it is reveal. A signature is not just a blob to classify. It is a little ritual residue, a human trace that survives the page. The product should not merely "find signatures." It should behave like an assistant that knows where traces hide, when they are trustworthy, and how to say, "I found the signature, but here is the weather around it."

## Metaphors that actually reveal something

### 1. Ship's bridge

The product is not the hull or the engine room. It is the ship's bridge.

What that reveals:
- The user needs orientation more than raw force. They need to know what the system sees, where it is unsure, and what course corrections are possible.
- The best UI is not a black box extraction result; it is a command view with bearings, confidence, hazards, and next actions.
- Every extraction should answer: where are we, what is visible, what is risky, and what should the operator do next?

So the workflow should feel like:
- "I’m looking at this document."
- "I see a likely signature region here."
- "The edge is torn, the ink is faint, the page is rotated, so confidence is lower."
- "Here are the three most plausible answers and the reason I prefer the first."

The bridge metaphor turns extraction into navigation. It clarifies state as a moving situation, not a static label.

### 2. Garden

The product is also a garden, not a factory.

What that reveals:
- Documents do not all grow the same way. Some pages are neat seedlings; some are weeds; some are storm-damaged shrubs.
- Extraction improves when the system learns the local soil: template families, common layouts, scanner artifacts, recurring signatory styles.
- The user should be able to prune, annotate, and cultivate patterns over time instead of redoing every task from scratch.

The garden metaphor suggests a living memory layer:
- recurring document types become beds;
- signatory regions become trellises;
- corrections become compost;
- failed extractions become useful mulch instead of dead ends.

This is useful because it reframes "errors" as growth conditions. The system should get wiser from the weird documents, not merely tolerate them.

### 3. Detective board

The product is a detective board with red string, thumbtacks, and suspiciously good handwriting.

What that reveals:
- Signature extraction is an evidence problem, not just a recognition problem.
- The system should show clues: proximity to label fields, alignment, handwritten texture, stroke density, page position, and neighboring annotations.
- Users trust decisions when they can inspect the chain of evidence, especially on ambiguous pages.

This metaphor pushes the workflow toward:
- a visible trail of why the signature was chosen;
- competing suspects when confidence is low;
- a way to pin, reject, and revisit evidence without losing context.

### 4. Jazz session

The product is a jazz session, not a marching band.

What that reveals:
- The page layout is the tune, but the documents improvise.
- A rigid one-shot model will miss the groove on messy inputs.
- Better behavior comes from call-and-response: detect, hypothesize, verify, adapt.

The band analogy is especially useful for workflow:
- the detector plays a riff;
- the validator answers;
- the UI improvises around uncertainty;
- the user can bring the system back on beat with one correction.

That makes the product feel alive without becoming chaotic. The trick is controlled improvisation.

## Three strongest concepts

### 1. Bridge View

The top-level screen should behave like a ship's bridge: live document state, confidence, hazards, and suggested next moves in one place.

Why it wins:
- it clarifies state immediately;
- it keeps uncertainty visible;
- it turns extraction into operator guidance, not just output.

### 2. Evidence Garden

Build the correction and learning layer as a garden of recurring patterns, templates, and annotations.

Why it wins:
- it rewards repeated use;
- it makes feedback productive;
- it turns messy documents into a compounding asset.

### 3. Case Board

Treat every tricky page like a case file with suspects, clues, and a ranked explanation trail.

Why it wins:
- it makes trust inspectable;
- it helps users understand disagreements between candidates;
- it is the best shape for exception handling and review.

## One genuinely surprising idea

Let the user "conduct" extraction with tempo instead of only with settings.

Fast tempo means: brute-force many candidate regions, high recall, more ambiguity tolerated.

Slow tempo means: fewer candidates, more verification, stronger confidence thresholds, richer explanation.

What this reveals:
- the same document can be processed in different modes depending on urgency;
- extraction is not one universal operation, but a performance style;
- the UI can make tradeoffs legible instead of hiding them in a settings graveyard.

That is weird, but useful. It makes the product feel like an instrument rather than a checkbox machine.

## State and workflow, pushed until the metaphor clarifies them

If I keep squeezing the bridge/garden/board/jazz metaphors, the product state becomes clearer:

- **Queued**: waiting on the dock, not yet in motion.
- **Scanning**: the radar is sweeping the page.
- **Candidate-rich**: multiple signatures or regions are plausible.
- **Pinned**: one region is under the captain’s finger.
- **Reviewed**: the detective board has a verdict and the user agrees.
- **Cultivating**: corrections have entered the garden and will affect future pages.
- **Drifting**: the page style changed and the system needs reorientation.
- **Rescued**: a human intervention resolved a bad ambiguity.

That state machine is the real product. The extractor is just the weather vane.

The workflow should therefore be:
1. See the page as a live scene.
2. Surface candidate signatures with evidence.
3. Let the user inspect competing clues.
4. Accept a correction or confirmation.
5. Store the correction as a reusable pattern.
6. Show the system getting less surprised next time.

## 6 / 12 / 24 month horizon

### 6 months

Smart builders remove the obvious friction:
- better confidence display;
- faster review;
- fewer manual rescans;
- clearer "why this signature" explanations;
- a first pass at recurring document-type memory.

### 12 months

The product becomes a working cockpit:
- layout family detection;
- pattern-based suggestions;
- user correction history;
- exception queues that sort themselves;
- document collections that behave like little ecosystems instead of isolated files.

### 24 months

The mature version assumes:
- the system knows the common document species;
- the user rarely starts from zero;
- corrections feed a living model of layout and signing behavior;
- the interface can switch between overview, review, and forensic modes without losing the thread.

At that point, the product is not "an extractor" anymore. It is a signature operations room.

## What the metaphor reveals about the actual product

The bridge says the user needs orientation.

The garden says the system should remember and grow.

The detective board says evidence must be visible.

The jazz session says the system should adapt without panic.

Together they reveal a deeper thesis:
the product is really about making uncertain visual judgment legible, editable, and cumulative.

## The thing most people miss about this

The hardest part is not finding signatures. It is teaching the product how to behave when it is almost sure, half sure, and completely wrong, while still keeping the operator calm and in control.

That is where the real leverage lives.

