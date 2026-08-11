# Mac Premium Readiness Checklist (PySide-first)

## Goal
Deliver premium-level macOS experience and trust cues without splitting the runtime into a separate native app.

## Scope (v1)
- macOS app packaging quality
- native-feeling onboarding and window treatment
- security and consent UX clarity
- workflow polish and visibility
- premium messaging and pricing fitment artifacts

## App-store-style quality gates (without native rebuild)

### Packaging and signing
- [ ] `.app` bundle naming and iconography are production-ready.
- [ ] App is signed with developer cert (or enterprise-scope equivalent for staging).
- [ ] Notarization path is defined for distribution build.
- [ ] Update channel and auto-update behavior are documented.

### Installer and permissions
- [ ] First-run permission request copy explains why each permission is needed.
- [ ] Folder-selection permission prompts are minimized and clear.
- [ ] Keychain/secure-store errors surface readable remediation steps.
- [ ] Recovery path when secure-store backend is missing.

### Workflow UX (premium feel)
- [ ] Dashboard uses a clean, stable visual hierarchy.
- [ ] Lock/unlock and grant status are obvious from first screen.
- [ ] Failures use clear language and next-step suggestions.
- [ ] One-click export for receipts/compliance pack.
- [ ] Queue states are color-augmented with text labels (no color-only status).

### Trust and language
- [ ] Repeated legal boundary phrasing is consistent across screens.
- [ ] No “legally binding” claims for visual signatures.
- [ ] Explicit visibility for reviewer/auditor actions and actor identity.

### Performance perception
- [ ] Folder scan and first completion latency are within acceptable startup expectations.
- [ ] Progress and ETA messaging exists for larger batches.
- [ ] Cancel/recover actions are immediate and reversible in UI.

## Evidence required before pricing bump

- 2-week private pilot on macOS with documented operator feedback scores.
- At least one workflow in recurring use for legal/HR/admin packet flow.
- Reduced manual clicks/time in end-to-end task compared with current v0.
- Zero critical unauthorized execution incidents in pilot.

## Trigger for native mac runtime reconsideration

Open ticket for native mac split only if at least one condition is true:

- `W16` review identifies a security requirement not solvable in shared stack.
- macOS distribution constraints require native lifecycle hooks unavailable in PySide path.
- Customer NPS/retention data shows premium perception blocked by UI runtime mismatch.

When any condition triggers, compute the W16 matrix and file evidence:
- [w16_go_no_go_matrix.md](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/docs/exploration/2026-07-24_authorized_template_folder_signing_workflow/w16_go_no_go_matrix.md)

## Ticket linkage

- `W16` should close only when this checklist has 90%+ completion and evidence links are attached.
