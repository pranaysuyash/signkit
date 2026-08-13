# Cartographer

This cartographer pass for the `wide open brainstorm` room treats Signature Extractor as a navigable atlas, not a feature list.

## Core Map Thesis

The product should make the user feel like they can always answer three questions at a glance:

1. What signatures do I have?
2. Where have I used them?
3. What needs attention right now?

If the user can answer those without drilling into a maze of screens, the product feels legible. If they have to remember where they were, the product feels like a folder tree with anxiety.

## Three Altitudes

### 10,000 Feet: The Whole Territory

At the highest altitude, the product is a single surface for:

- signature assets,
- documents that need action,
- placement history,
- trust and provenance,
- export and recovery.

This is where the user should see the system as a complete landscape. The important move is not to show every detail; it is to show the shape of the workflow. The user should instantly understand whether they are in capture mode, reuse mode, or review mode.

The best 10,000-foot metaphor is a **signature atlas**: a map of the territory where signatures live, move, and get reused.

### 1,000 Feet: Workstreams and Regions

At the middle altitude, the product should group things by meaningful regions:

- by signature identity,
- by document family,
- by workflow state,
- by trust level,
- by recency and frequency of use.

This is where clusters matter. A user should not have to think in raw file names. They should think in neighborhoods:

- "my primary signature,"
- "tax forms,"
- "contracts pending placement,"
- "verified exports,"
- "needs review."

The right grouping pattern here is not one giant list with filters. It is a map with clear regions, each region telling the user what kind of attention it deserves.

### Ground Level: Exact Actions

At the lowest altitude, the product should always make the next move obvious:

- open the signature,
- compare against the source,
- place on the page,
- nudge into position,
- confirm,
- export,
- or back out safely.

Ground level is where navigation becomes trust. Every action should have a visible escape hatch, a visible state, and a visible reason for being there.

## Views

### 1. Atlas Home

The main home view should feel like a control map:

- recent signatures,
- active documents,
- unresolved placements,
- trust warnings,
- last-used export paths.

This is the "see everything at once" view. It should not try to do the work itself. It should orient the user before they commit to a path.

### 2. Signature Library

A gallery-style view for all signature assets, but grouped by use pattern rather than only by chronology.

Good grouping patterns:

- primary vs alternate signature,
- by signer identity,
- by document family,
- by confidence / cleanup quality,
- by last used.

This view should support fast scanning from afar and precise inspection when zoomed in.

### 3. Placement Map

A document page view with overlays, anchors, and a visible placement trail.

The user should be able to see:

- where the signature landed,
- what anchor was used,
- how much adjustment happened,
- whether the placement was reused or manually placed,
- and what would happen if they repeated the action.

This is the "terrain" view. It makes the page feel like a map with coordinates instead of a blank canvas.

### 4. Trust Ledger

A provenance view that answers:

- where did this signature come from,
- how was it cleaned or normalized,
- how many times was it reused,
- and what changed between versions.

This is the back-of-house map that lets the user trust the front-of-house views.

## Zoom Levels

### Zoomed Out

Show the overall structure:

- assets,
- active work,
- completed work,
- exceptions,
- trust signals.

The point of zoomed out mode is to reduce cognitive load. The user should feel like they can survey the whole estate without opening every door.

### Mid Zoom

Show grouped regions and work queues.

This is where the user chooses a lane:

- clean up a signature,
- place it in a document,
- review a prior placement,
- or resolve a mismatch.

Mid zoom is the best place for bulk decisions and smart defaults.

### Close Zoom

Show the exact placement, cleanup, and export details.

Close zoom should expose enough detail to make the user confident, but not so much detail that they feel trapped in technical minutiae.

## Navigation Metaphors

### Primary Metaphor: Signature Atlas

This is the clearest structure for the product because it combines:

- overview,
- regions,
- routes,
- landmarks,
- and re-entry points.

The atlas metaphor makes the product feel explorable without being chaotic.

### Secondary Metaphor: Trail Markers

Every important action should leave a visible trail:

- captured here,
- reused there,
- placed on this page,
- adjusted by this much,
- exported from this path.

Trail markers help the user recover context and avoid "where did that go?" moments.

### Tertiary Metaphor: Compass + Breadcrumbs

The user should always know:

- where they are,
- how they got there,
- what the current scope is,
- and how to go back to the broader map.

The product should not rely on hidden navigation. If the user is in a subview, they need a constant sense of location.

## How the User Sees Everything at Once

The product should use a persistent overview rail or summary zone that keeps the main state visible:

- current signature,
- current document,
- current placement status,
- recent activity,
- unresolved issues.

This does not need to be a giant dashboard. It needs to be a stable orientation layer. The user should never lose the thread while moving through deeper views.

The rule is simple: the deeper the user goes, the stronger the orientation cues must get.

## How the User Navigates Without Getting Lost

1. Keep the active scope visible at all times.
2. Make the back path obvious and semantically meaningful.
3. Use grouped regions instead of endless lists.
4. Preserve a clear distinction between overview, work queue, and detail view.
5. Let the user jump back to the atlas from any local view.

The product should behave like a well-marked museum, not a warehouse.

## Three Strongest Concepts

### 1. Signature Atlas

The master map of the whole product.

Why it matters:

- makes the system legible at a glance,
- supports multiple zoom levels,
- turns folders into regions,
- and gives the user a durable mental model.

### 2. Placement Trail

A visible path of how a signature moved from capture to placement to export.

Why it matters:

- supports recovery,
- reduces anxiety,
- and makes repeat behavior feel intentional rather than mysterious.

### 3. Trust Compass

A persistent orientation layer that tells the user what is current, what is uncertain, and what needs review.

Why it matters:

- keeps the user from getting lost,
- exposes confidence and provenance,
- and prevents the interface from becoming visually busy without being clear.

## 6 / 12 / 24 Month Horizon Ideas

### 6 Months

Make the current surface map-like:

- clearer home overview,
- stronger grouping,
- better breadcrumbs,
- visible placement status,
- and quick jump-back paths.

The goal is legibility first, not more screens.

### 12 Months

Turn the map into a working system:

- smarter clustering of signature families,
- reusable placement routes,
- document-family views,
- stronger recovery flows,
- and more reliable trust/provenance overlays.

At this horizon, users should feel that the product understands where things belong.

### 24 Months

Make the product feel like a navigational operating system for signature work:

- policy-aware regions,
- shared conventions for teams,
- cross-document path memory,
- predictive placement routes,
- and context-sensitive shortcuts that get better with use.

At this point, the map is not just a view. It is the product's organizing intelligence.

## One Non-Obvious Insight

The best navigation system here is not faster search. It is better spatial memory.

People remember where a signature lives, where they last placed it, and what kind of document they were working on. If the interface reinforces that memory with stable regions, landmarks, and trails, the user feels intelligent instead of dependent on the UI.

## What the Structure Should Feel Like

It should feel:

- spatial,
- calm,
- annotated,
- always re-enterable,
- and impossible to fully lose.

The structure is legible when users can move from overview to detail and back again without losing confidence.

