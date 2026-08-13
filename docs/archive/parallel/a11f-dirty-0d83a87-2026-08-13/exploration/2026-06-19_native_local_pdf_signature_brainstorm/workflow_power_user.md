# Native Local PDF + Signature App Brainstorm

Role: Power user / operator / support lens

Date: 2026-06-19

This is a brainstorm artifact, not a spec or roadmap.

## Role Point Of View

This app should feel like a local production instrument for people who do the same PDF work all day and cannot afford friction, ambiguity, or "let's see what happens" behavior. Power users do not want novelty; they want a tool that disappears under their hands. They care about whether the shortcut is faster than reaching for the mouse, whether the preview is trustworthy before export, whether a batch run can be resumed after interruption, and whether the app can explain exactly what it changed.

From this lens, the core product promise is not just "extract a signature." It is "do repetitive document work with confidence, at speed, with recovery." The app should make repeated actions feel mechanical in a good way: predictable placement, stable templates, visible state, recoverable failures, and enough audit trail that support does not have to reconstruct what happened from memory. A pro tool earns trust by making the operator faster without making them feel less in control.

## Top Workflow Pain Points A Native App Should Solve

1. **Too much mouse work for repetitive tasks**
   - If every document requires hunting for the same controls, users lose time and concentration.
   - Power users want keyboard-first flows, remembered positions, and one gesture that repeats the last action.

2. **No confidence before export**
   - A signature can look fine in the canvas and still export badly, shift on another page, or flatten incorrectly.
   - Users need preflight checks, page previews, and a clear "this is what will ship" state.

3. **Batch work is too fragile**
   - Repetitive PDF work often happens in runs of 10, 50, or 500 files, not one at a time.
   - If a batch fails halfway, users need to resume, skip, retry, and keep the good outputs.

4. **The app forgets too much**
   - Reopening a file should restore placement, zoom, selected page, template, and unresolved warnings.
   - If state disappears, operators lose trust and start using the app like a disposable viewer instead of a workspace.

5. **Recovery is not first-class**
   - Operators need undo, redo, revert-to-version, and "restore the last good export."
   - A support-friendly app should also expose what happened in a form that is easy to diagnose later.

6. **Templates are either too rigid or too manual**
   - Reusable document patterns should adapt to page size, page count, and minor layout drift.
   - If the operator has to rebuild placement every time, the template system is not actually saving work.

7. **Support cases are hard to explain**
   - When something goes wrong, the user should be able to point to an audit trail, a screenshot, or a saved session state.
   - The app should generate evidence that helps both the user and support staff understand the failure path.

## High-Leverage Workflow Features And Shortcuts

### Keyboard-first control surface

- `Cmd/Ctrl+O` open document
- `Cmd/Ctrl+Shift+O` open folder or batch set
- `Cmd/Ctrl+K` command palette for actions, templates, and recent documents
- `Space` or hold to pan the page
- Arrow keys to nudge a signature or selected field
- `Shift+Arrow` for larger nudges
- `Tab` cycle through candidate fields or next unresolved document
- `Enter` accept suggested placement
- `Esc` cancel the current drag, preview, or batch dialog
- `Cmd/Ctrl+Z` undo last visible action, not just one canvas event
- `Cmd/Ctrl+Shift+Z` redo

### Power-user action patterns

- **Repeat last action** with one keypress, including last signature, last template, last placement offset, or last export profile.
- **Apply to next** for recurring document sets, where the operator wants the same signature/template on the next file without reselecting settings.
- **Pin a favorite workflow** like "sign, flatten, export, next" to the top of the UI.
- **One-step safe mode** for users who want the app to do the obvious thing, but only after previewing the result.
- **Quick compare** between original, in-progress, and export-ready states.

### Preview-first interaction patterns

- Show a live before/after split view for every signature placement.
- Offer page-level thumbnails with visible markers for all edits and all signature placements.
- Provide a "preflight summary" before export:
  - pages touched
  - signatures placed
  - fields auto-detected
  - warnings
  - unresolved candidates
  - output filename
- Keep a persistent zoomed preview of the currently selected placement so users are never guessing about edge alignment.

## Batch / Repeat / Template Ideas

### Batch flows

- **Folder ingest**
  - Drag in a folder of PDFs and the app immediately groups them by document type, page count, and template compatibility.
- **Batch preview queue**
  - The queue should show filename, page count, matched template, confidence, and any warning before processing begins.
- **Resumable runs**
  - A batch should be restartable from the first failed item or from any selected checkpoint.
- **Skip / retry / quarantine**
  - Good files continue.
  - Broken files go to a review lane.
  - The operator can export only the successful subset if needed.
- **Dry run mode**
  - Simulate the batch, generate placements, and show the expected outputs before any files are written.

### Repeated-document patterns

- **Template by document family**
  - Save a placement recipe for contracts, HR forms, tax forms, real estate packets, or recurring vendor paperwork.
- **Relative anchors**
  - Templates should follow stable anchors such as text labels, boxes, page ratios, and page regions instead of brittle absolute coordinates only.
- **Template variants**
  - The same form family may have "one signer," "two signer," or "counter-signature" variants.
- **Remembered corrections**
  - If the user moves a signature once, the app should learn that correction for the next similar file.
- **Template inheritance**
  - A base template should be reusable with overrides instead of cloned into dozens of near-duplicates.

### Repeatability features

- Save last-used:
  - signature asset
  - template
  - output folder
  - flattening choice
  - naming pattern
  - export format
- Reopen recent jobs with their exact prior state.
- Allow a user to mark a workflow as "always ask" or "never ask again."

## Recovery, Preview, Undo, And Confidence Features

### Recovery

- **Session restore**
  - Restore open documents, scroll position, zoom, selected page, and unsaved edits after a crash or quit.
- **Checkpoint history**
  - Save safe restore points after major steps like import, placement, flattening, and export.
- **Local version history**
  - Keep previous export versions available for comparison and rollback.
- **Partial failure handling**
  - If page 7 of 20 fails, the app should not destroy the work already completed on pages 1 to 6.

### Preview

- **Layered preview**
  - Show original PDF, proposed changes, and final render as distinct views.
- **Field-level preview**
  - Hover or focus on a placement and see the anchor, confidence, and expected export behavior.
- **Export preview**
  - Show the flattened output exactly as the saved file should appear.
- **Support preview**
  - Generate a compact review bundle with thumbnails, change summary, and operation log for debugging.

### Undo

- Undo should work at the document-operation level, not just the UI gesture level.
- Undo should be safe after:
  - move
  - resize
  - rotate
  - template apply
  - batch apply
  - flatten preview
- A "revert document to last saved state" option should be obvious, not buried.

### Confidence

- Confidence should be visible, not implied.
- Show:
  - detection confidence
  - template match confidence
  - export confidence
  - unresolved warnings
  - whether the file was modified after preview
- Let the user mark a file as reviewed, approved, needs retry, or needs manual placement.
- Warn on risky transitions like flattening, overwriting, and irreversible redaction.

## What Would Make The App Feel Like A Pro Tool Instead Of A Toy

1. **It remembers what I did last time**
   - Professional tools reduce repeated setup.
   - A good default is not "empty canvas" every time; it is "continue from where I left off."

2. **It never makes me wonder what changed**
   - Every edit should be visible in a change summary.
   - The app should tell me what was auto-detected, what was inferred, and what I manually corrected.

3. **It respects batch reality**
   - Pro users operate on queues, not single documents.
   - The app should support the language of operations: jobs, retries, skips, failure reasons, and completion counts.

4. **It gives me real control over precision**
   - Nudge amounts, snap behavior, coordinate display, and page selection should be easy to tune.
   - Operators should not have to fight auto-placement when they already know the correct target.

5. **It behaves like a local instrument, not a web form**
   - Fast open.
   - Fast render.
   - No "please wait" theater when work is already on disk.
   - State should feel durable and private.

6. **It has a serious support story**
   - A pro tool should make it easy to answer:
     - what happened
     - when it happened
     - which file it touched
     - which template or signature was used
     - whether the export was verified

7. **It handles edge cases without drama**
   - Mixed page sizes, rotated pages, scanned PDFs, missing fonts, broken pages, duplicate names, and partially corrupted files should not feel catastrophic.

8. **It is predictable under stress**
   - When many files are queued or the machine is slow, the user should still see progress, cancellation, and a stable order of operations.

## Open Questions / Edge Cases / Failure Modes

### Open questions

- Should the default mode optimize for maximum automation or for maximum review before export?
- How much template learning should happen silently versus only after explicit approval?
- Should batch runs be allowed to continue after warnings, or should some warning classes hard-stop the job?
- Which actions deserve a separate "safe" confirmation because they are hard to reverse?
- How should the app distinguish between personal convenience templates and organization-approved templates?

### Edge cases

- Scanned PDFs with no searchable text.
- Rotated or mixed-orientation pages inside the same file.
- Documents where the signature area shifts between versions.
- PDFs with hidden layers, unusual forms, or broken structure.
- Multi-signature documents where one signer should not overwrite another's placement.
- Files that are password-protected, partially corrupted, or missing embedded fonts.
- Same filename across different folders or repeated runs.
- Very large batches where the UI must stay responsive while work continues in the background.

### Failure modes

- Auto-placement feels smart but is actually brittle, which erodes trust fast.
- Batch mode hides errors until the end instead of surfacing them early enough to act on.
- Undo only works for the visual layer, not the actual PDF output.
- Templates become stale because users cannot see when they were last validated.
- The app exports a file that looks correct in preview but differs after reopen.
- Recovery data exists but is too hard to read during support triage.

### Operator-facing safety checks

- Confirm the source document before any irreversible export.
- Show when the working copy diverges from the last saved version.
- Keep a clear distinction between draft, reviewed, and exported states.
- Make it obvious whether the current action applies to one page, the current file, or the entire batch.

## Bottom Line

The power-user version of this app should feel like a reliable local workstation for document operations. The winning experience is not "more features." It is: faster repetition, clearer previews, stronger recovery, and fewer surprises after export. If the tool can make repetitive PDF/signature work feel safe enough to trust and quick enough to prefer, it will earn a place in real operator workflows.
