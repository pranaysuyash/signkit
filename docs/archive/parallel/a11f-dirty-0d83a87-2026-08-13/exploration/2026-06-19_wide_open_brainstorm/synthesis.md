# Wide Open Brainstorm Synthesis

Date: 2026-06-19

This is the synthesis of the `wide open brainstorm` room, using the exact skill path:

- [`carl-tools:wide-open-brainstorm`](/Users/pranay/Projects/external-skills/carlkibler__agent-skills/skills/wide-open-brainstorm/SKILL.md)

This note is a brainstorm artifact, not a roadmap or implementation spec.

## North Star

The product should become a local-first document completion workspace for PDF and signature work.

The best version is not a generic PDF editor and not a cloud e-sign clone. It is a tool that makes this loop fast, private, and recoverable:

`extract -> recognize -> place -> review -> export -> reuse`

## Shared Answer Across Roles

The strongest convergence is around a single thesis:

the signature is not the product, the reusable and trustworthy signature asset is the product.

That means the product should center:

- local signature vaults;
- durable placement memory;
- visible confidence and preflight;
- recoverable session state;
- audit trails and export receipts;
- batch and repeat workflows;
- a navigation model that makes the whole system legible.

## Role Convergence

### Strategist + Champion

- The product wins by making signature capture and reuse feel like one trustworthy local workflow.
- The real moat is the reusable signature asset and the memory around it.
- The best differentiation is privacy plus repeatability, not feature breadth.

### Operator

- The core loop must be keyboard-friendly, resumable, and predictable.
- The product should optimize for the second and twentieth placement, not the first demo.

### Cartographer

- The product should feel like a signature atlas.
- Users need to answer at a glance: what signatures do I have, where were they used, what needs attention?

### Archivist

- The product should remember the shape of a successful recovery, not every detail forever.
- Memory should feed smarter defaults and safer restarts.

### Trickster

- The product becomes more legible when framed as a bridge, garden, detective board, or jazz session.
- Those metaphors reveal orientation, growth, evidence, and adaptive tempo.

### Skeptic

- The app should not become a bloated PDF platform.
- Most fancy extras are local maxima if the user still has to do the same correction dance.

### Executioner

- The broad idea does not deserve to be a standalone company as-is.
- If anything survives, it survives as a narrow local utility inside a larger document workflow.

## Strongest Feature Cluster

1. Signature field detection with confidence overlays
2. Provenance-rich signature vault
3. Template replay for repeat documents
4. Durable document session state
5. Preview-first export verification
6. Audit trail and export receipts
7. Batch signing and watch-folder automation
8. OCR / scan cleanup as an enhancer

These features reinforce one another. Together they create the local-first document completion workspace.

## Best Narrow Wedge

**Local-first signature placement for recurring PDFs, with field detection, reusable templates, and durable export/audit state.**

Why this wedge wins:

- it matches the repo's direction;
- it solves a repeated pain;
- it is differentiated by trust and repeatability;
- it expands naturally into adjacent workflow features.

## Tensions That Matter Most

### Breadth vs trust
The product should widen only in directions that strengthen the same workflow loop.

### Automation vs review
The system can suggest aggressively, but it should not silently mutate low-confidence documents.

### Visible signing vs digital signing
These are different trust classes and should not be blurred.

### Local privacy vs optional expansion
The default path must stay local and simple, even if opt-in capabilities exist later.

## 6 / 12 / 24 Month Direction

### 6 Months
- make the signing loop boringly fast;
- improve previews and confidence;
- reduce rework;
- strengthen session restore and export verification.

### 12 Months
- templates and reuse become a system;
- batch work feels natural;
- recovery is obvious;
- document-family memory starts to matter.

### 24 Months
- the app behaves like a local production instrument;
- recurring document families are nearly one-click;
- trust and recovery are table stakes;
- the product feels like a local authority for signature work.

## Kill Test Verdict

The Executioner lane was harsh for a reason, but the room still survived as a **narrow product thesis**.

The thing that survives is not "a broad signature company." It is:

- a local-first signature operations layer,
- focused on repeatable document completion,
- with memory, recovery, and export trust as the core value.

## What Most People Miss

The hardest part is not finding signatures. It is making the product calm and legible when it is almost sure, half sure, or wrong.

That is where trust is won.

## Parser Direction (Additional)

We now have a practical parser stance for this lane:

- default behavior stays local-first and deterministic;
- expand detector output classes before we add broad semantic extraction;
- treat `LiteParse` as the first optional layout-rich local parser enhancement;
- keep `LlamaParse` and other API-style document services as explicit opt-in adapters only (not the default path);
- defer GUI-vision systems (`OmniParser` family) to later experimentation, as they are not PDF form-field first-class tools.

This keeps the thesis aligned with the long-term contract:

- local privacy by default,
- transparent consent for any cloud path,
- recoverable action logs instead of opaque automation.
