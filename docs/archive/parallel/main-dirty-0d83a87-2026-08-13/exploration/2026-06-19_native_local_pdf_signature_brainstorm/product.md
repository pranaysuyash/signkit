# Native Local PDF + Signature App Brainstorm

Role: Product Strategist / PM

Date: 2026-06-19

This is a brainstorm artifact, not a roadmap or spec.

## Role Point Of View

This app should not try to win by being a smaller Acrobat or a generic e-sign clone. The real opportunity is to become the best local-first document completion workspace for people who already live inside PDFs and need to move fast without giving their files, signatures, or workflow telemetry to a cloud service. The repo already points in that direction: signature extraction, reusable signature assets, PDF signing, field detection, template reuse, audit logging, and document/session state are not separate ideas here. They are one workflow.

That means the product lens should be: how do we make "find the right place, place the right mark, verify it, and export it" feel obvious, trustworthy, and repeatable on a laptop with no cloud dependency. The winning product is probably not the one with the most features. It is the one that makes the signing/document-completion loop feel fast enough that users stop looking for an external service.

## Top 10 Feature Ideas

1. **Signature field detection with confidence overlays**
   - Detect likely signature lines, initials boxes, date fields, and "sign here" regions.
   - Show a confidence-ranked overlay in the viewer so the user can accept or reject suggestions.
   - This is the most obvious bridge from extraction into actual PDF utility.

2. **Reusable signature library with provenance**
   - Store extracted signatures, initials, and variants in a local vault.
   - Track where each asset came from, when it was last used, and which document types it fits.
   - The library should feel like a real asset manager, not just a folder of PNGs.

3. **Template replay for repeat documents**
   - Save placement geometry and field anchors so a recurring contract can be signed in one click the next time.
   - Support relative placement so templates survive page size changes and minor layout drift.
   - This is where the app starts creating compounding value instead of one-off convenience.

4. **Document session state that survives reopen**
   - Persist the current document's placement, edits, export state, and review state.
   - A signature that looks correct in-session but disappears or exports differently after reopen breaks trust immediately.
   - This should be treated as core product behavior, not a backend detail.

5. **Targeted PDF edit actions, not a full editor**
   - Rotate, reorder, split, merge, crop, flatten, and stamp.
   - Add simple text/date annotations and form fills where the document already has structure.
   - These are high-frequency, high-leverage tasks that expand the app without turning it into a sprawling clone.

6. **Annotation, approval, and review layer**
   - Add highlights, notes, approval marks, and redaction candidates as first-class app objects.
   - Keep the app-owned review state separate from the exported PDF serialization so the workflow remains auditable.
   - This turns the app from "signing utility" into "document completion workspace."

7. **Batch signing and watch-folder automation**
   - Apply a signature/template to a batch of incoming PDFs.
   - Add a watch-folder mode for recurring operational workflows.
   - This is a strong power-user feature because it converts repeated manual labor into a local production line.

8. **Searchable scan cleanup and quality scoring**
   - Detect blur, skew, low contrast, and bad crops before the user commits to signing.
   - Offer a "make this easier to work with" pass for ugly scans.
   - The surprise value is not OCR itself; it is preventing bad document inputs from creating bad signature outputs.

9. **Export receipts and audit trail**
   - Generate a local operation log that says what was changed, where, when, and with which signature/template.
   - Exports should be explainable later, especially for users who reuse the app in compliance-sensitive contexts.
   - Trust is a feature here, not just a compliance checkbox.

10. **Smart local suggestions based on document type**
    - Learn from prior corrections to suggest likely signing spots, preferred signatures, and page targets.
    - Start with deterministic heuristics before any ML-heavy ambition.
    - The surprise is a "this looks like the same form as last time" experience without sending documents to a server.

## Best Narrow Wedge

The strongest wedge is: **local-first signature placement for recurring PDFs, with field detection, reusable templates, and durable export/audit state**.

Why this wedge:

- It is close to what the repo already does well and can plausibly own end-to-end.
- It solves a painful, repeated job that people actually pay to make easier: "take this PDF, put the right signature in the right place, and make sure it survives export."
- It is differentiated by workflow trust, not by feature count.
- It naturally expands into adjacent high-value tools like form fill, annotations, batch signing, and scan cleanup without changing the core identity.

In product terms, the wedge is not "signature extraction" alone. Extraction is the asset acquisition step. The wedge is the whole loop:

`extract -> recognize -> place -> review -> export -> reuse`

That loop is defensible because it combines local privacy, deterministic behavior, and repeatability. Most cloud e-sign tools are good at sending documents around. Most PDF utilities are good at editing files. Very few do both in a way that feels purpose-built for the same user and stays offline by default.

## What Not To Build

- **Do not build a generic Acrobat replacement.** The surface area explodes and the product loses identity.
- **Do not start with cloud-first collaboration.** The repo's strongest position is local-first privacy and low-friction document work.
- **Do not market visible image stamping as cryptographic signing.** Those are different trust classes and should stay distinct.
- **Do not chase broad AI document intelligence before the core signing loop is trusted.** Fancy extraction is not a substitute for reliable placement/export.
- **Do not add parallel PDF stacks just because a library looks powerful.** The product needs one canonical path per role.
- **Do not make every PDF feature a first-class feature.** Some things belong as opt-in capabilities or later expansion, not day-one promises.
- **Do not turn redaction into a black-rectangle drawing tool.** If redaction exists, it has to be real content removal, not visual theater.
- **Do not build a pricing story before the workflow story is clear.** Users will pay for the boring, repeatable, trustworthy path before they pay for novelty.

## Product Questions Still Open

1. Is the product primarily for individuals, freelancers, and small businesses, or should it eventually support compliance-heavy teams as a second market?
2. How much of the workflow should be framed as "signing" versus "document completion" versus "PDF workspace"?
3. Where is the line between visible signature placement and legal-grade digital signatures in the product promise?
4. Which adjacent task should be added first after signing: annotations, form filling, scan cleanup, or batch automation?
5. Should the local vault be optimized for personal convenience, team reuse, or export portability first?
6. How aggressive should default automation be before the user confirms placement?
7. Which document types are the best first beachhead: contracts, HR forms, tax docs, real estate packets, or internal approvals?

## Biggest Tradeoff

The biggest tension is **breadth versus trust**.

If the app tries to become a general document platform too early, it loses the sharpness that makes it easy to understand and easy to love. But if it stays too narrow, it risks becoming a clever extraction tool that never graduates into a durable workflow product.

The practical answer is to widen in the direction of **adjacent trust-building actions**:

- from extraction to placement
- from placement to review
- from review to export
- from export to reuse
- from reuse to batch and automation

That path keeps the product coherent. It also keeps the core promise believable: private, local, repeatable PDF/signature work that gets better each time you use it.

