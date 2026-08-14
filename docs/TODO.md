# Launch TODOs and Roadmap (condensed)

This mirrors the working list we’ve been tracking in chat. Status will be kept up to date here.

Canonical backlog governance is now in:
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`

Update rule: any item with explicit acceptance or an unresolved risk stays explicitly in-progress/pending in
`Docs/LAUNCH_TOP_10_STATUS.md` and is reflected as "in-progress" or "pending" in this list.

Legend: [x] done • [~] in progress • [ ] pending

Full roadmap inventory: see `TODO_FULL.md`; current status is governed by the
Product Owner backlog and QA matrix.

## Top 10 launch gate

- [x] Auto-preview on selection/threshold changes (remove manual Preview)
- [x] Export/Save enablement tied to preview existence
- [x] Rotate CW/CCW with re-upload as new session
- [x] “My Signatures” local library (save/list/delete)
- [x] Library double-click opens into Source pane (re-uploads to backend)
- [x] Fit-to-view improved for transparent images
- [x] Left sidebar fixed width (avoid taking half the window)
- [x] Clearer icons + tooltips; de-dupe emoji vs system icons
- [~] Color swatch reflects current color consistently
- [x] Keyboard shortcuts for common actions (Cmd on macOS / Ctrl on others)

## Desktop UX polish

- [x] Lighter native look on macOS (minimal custom styles)
- [ ] Ensure right pane dominance and splitter behavior across window sizes
- [x] Clipboard: Copy result PNG with transparency
- [ ] Quick export presets (PNG w/transparent, JPG white bg)
- [x] JSON metadata export (bounds, threshold, color)
- [ ] Better status messages + unobtrusive errors

## Library behavior

- [x] Save extracted PNG with timestamped filename
- [x] Delete via context menu
- [x] Limit list to 50 recent
- [x] Show human-friendly names and times
- [x] Persist to ~/.signature_extractor/signatures
- [x] Opening loads into Source and resets preview

## Color/selection

- [~] Color picker swatch updates immediately and stays in sync
- [ ] Optional eyedropper/average color from selection (future)
- [ ] Threshold ramp preview (future)

## Backend

- [ ] Clean up commented/duplicate code
- [x] Confirm port 8001 across docs, tests, and desktop client
- [x] Local smoke tests: /health, authenticated upload, process/export/deletion round-trip (`QA-53`); hosted smoke remains a separate gate
- [x] Canonical root test collection covers `tests/`, `backend/tests/`, and `desktop_app/tests`; optional PDF and Qt event-loop skips remain explicit
- [x] Remove hardcoded backend database credential defaults, fail closed for incomplete production configuration, and protect local PII paths with owner-only permissions
- [x] Run authenticated extraction ownership smoke against disposable SQLite and the current Alembic head; retain target migration and hosted recovery as separate gates (`QA-53`)
- [x] Exercise local Alembic head downgrade and re-upgrade for the receipt-field migration; retain target backup restoration and hosted rollback as separate gates (`QA-54`)
- [x] Build and exercise the current macOS arm64 local package with isolated runtime and browser proof; retain signing, rollback, other-platform, hosted, provider, and remote CI gates (`QA-55`)
- [x] Keep the QA matrix executable and boundary-aware for negative paths, known limits, and hosted/provider non-claims (`QA-56`)
- [x] Make every canonical-root claim reviewable through a registry source commit and existing-commit test; retain provider, legal, and deployed gates (`QA-57`)
- [x] Keep strict-audit retained-page and historical-document warnings tied to explicit archive or redirect-only dispositions; retain deployed and legal gates (`QA-58`)
- [x] Keep optional landing analytics fail-silent when `gtag` is absent while preserving configured event forwarding; retain provider, consent, hosted, and observability gates (`QA-62`)

## Packaging and distribution

- [x] PyInstaller spec for the current macOS arm64 bundle (`QA-55`)
- [~] Local macOS arm64 DMG proof exists (`QA-55`); Gatekeeper guidance, signing, notarization, and other-platform bundles remain open
- [ ] Code signing + notarization (post-early access)
- [x] Manual update check in-app (“Check for Updates…”) using static updates.json

## Commerce (Gumroad first)

- [ ] Create Gumroad account + product (Standard license)
- [ ] Set GUMROAD_PRODUCT_URL in .env and wire Buy action (Buy menu opens env URL; fallback present)
- [ ] Product page copy (benefits, usage GIF, FAQ)
- [~] Deliverable bundle: current macOS arm64 app and DMG are locally proven; signed, notarized, cross-platform, and rollback-ready bundles remain open (`L0-05`, `L0-14`, `QA-55`)
- [ ] Plan later migration path (DoDoPayments)

## Docs and comms

- [ ] Update README with desktop-only instructions
- [ ] Add quickstart with screenshots
- [ ] Record short demo video (open → select → preview → export → library)
- [x] Local canonical product surface per `docs/LANDING_PAGE_PLAN.md` and the document-registration-studio direction; hosted publication remains a separate release gate
- [ ] Publish `updates.json` and stable downloads; add legal links (Privacy, Terms/EULA, Refund)

## Licensing & Evaluation

- [x] Local paid-feature gating uses one signed receipt boundary; legacy keys fail closed and the historical test key is explicit test mode. See `docs/decisions/ADR-0151-signed-local-entitlement-activation.md`.
- [ ] Provider adapter and controlled activation: configure product ID, verify receipt delivery, and exercise replay, timeout, refund, dispute, chargeback, offline grace, and support recovery (`L0-02`, `QA-15`)
- [x] Native-GUI proof archived for cancel/confirm, keyboard focus, preview rendering, and failure messaging; rerun after candidate-dialog or desktop-runtime changes (`RECON-23`)
- [~] Synthetic auto-detection baseline recorded; dataset research was refreshed without downloading new files; permissioned held-out evaluation, provenance, recall@k/IoU, failure classes, and an accuracy-bar decision remain open (`RECON-24`). See `docs/research/auto_detection_dataset_research_2026-08-14.md`.
- [x] Export gating uses the signed local entitlement boundary and Upgrade path (`L1-01`, `QA-23`)
- [x] Status bar note when unlicensed is bound to the evaluation-mode export lock (`L1-01`, `QA-23`)
- [ ] Optional watermark overlay in evaluation mode (off by default)

## Local product reconciliation addendum (2026-08-13)

The local product is now being advanced against the long-term document
registration-studio direction. The canonical task record is
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`; these entries keep the
condensed TODO list honest while the larger reconciliation remains active.

- [x] `RECON-13` Promote the selected registration-studio direction to the local canonical root.
- [x] `RECON-14` Add reusable real-browser proof for the root, workspace handoff, keyboard/pointer states, responsive widths, and reduced motion.
- [x] `RECON-16` Add one-command local stack startup with isolated data defaults and clean process shutdown.
- [x] `RECON-17` Add disposable local source-to-ready proof covering extraction, cleanup, vault, placement/export, forced failure, retry, passports, and artifact receipt, then join it to the browser proof through the local bridge.
- [x] `RECON-18` Implement one canonical metadata-only local companion bridge from the desktop workflow store to the browser workspace. See `docs/decisions/ADR-0147-local-desktop-passport-bridge-boundary.md`.
- [x] `RECON-19` Harden local bridge retry with store locking, durable idempotency receipts, deterministic default keys, and concurrent replay tests. See `docs/decisions/ADR-0147-local-desktop-passport-bridge-boundary.md`.
- [x] `RECON-20` Prove the local macOS ARM64 packaged runtime, prevent `.env` bundling, and package the canonical browser workspace. See `docs/review/local_packaging_runtime_proof_2026-08-13.md`.
- [x] `RECON-25` Consolidate PDF field-detection coordinate/dedupe helpers, add a labeled local AcroForm regression, and enforce auto-detection documentation coverage. See `docs/review/pdf_field_detection_contract_proof_2026-08-13.md` and QA-37.
- [x] `RECON-27` Add explicit local stale-workflow recovery: old transient jobs move to `Needs review` with a durable interruption event, no automatic retry, bounded operator copy, and invalid-timestamp fail-safe. See `docs/review/local_stale_workflow_recovery_proof_2026-08-13.md` and QA-40.
- [~] `RECON-28` Preserve and harden the parallel confidence-calibration harness without promoting synthetic results to product claims. One-to-one matching, PDF page validation, split-boundary warnings, dataset documentation, focused tests, and the synthetic self-test are now local evidence; held-out, privacy, accuracy-bar, and threshold-promotion gates remain open. See `docs/review/calibration_harness_proof_2026-08-14.md` and `docs/calibration_dataset_spec.md`.
- [x] `RECON-29` Add explicit local library cleanup recovery: incomplete deletion receipts expose a bounded `Repair Cleanup` action, repair only regular in-library sidecars after operator invocation, atomically update receipts, and preserve unresolved unsafe targets. See `docs/review/local_library_cleanup_recovery_proof_2026-08-14.md` and QA-44.
- [~] `L1-08` Advance the operator state/recovery contract with the local source-to-ready proof, canonical workflow/companion copy binding, non-retryable malformed-input review state, verified partial-export cleanup, structured library deletion cleanup with explicit receipt-backed `Repair Cleanup`, explicit local-service retry control, Tier 4 local companion restart proof, and the local canonical web accessibility semantics/browser contract; packaged/cross-platform stale-state, assistive-technology, and hosted evidence remain open. See `docs/review/local_operator_state_proof_2026-08-13.md`, `docs/review/local_library_cleanup_recovery_proof_2026-08-14.md`, `docs/review/local_companion_restart_proof_2026-08-13.md`, `docs/review/local_accessibility_audit_2026-08-13.md`, and QA-44.
- [x] `RECON-26` Repair the live `agent-start` doctrine source-selection/retention regression: fast refresh now retains the project-local `motto_v5.md`, does not delete tracked doctrine or rewrite context to workspace Doctrine 6.0, and passed two consecutive refreshes with a clean checkout. See `docs/review/agent_start_doctrine_contract_proof_2026-08-14.md` and QA-42. Shared retrieval/index health remains open under `RECON-06`.
- [x] `RECON-06` Rebuild the documented local workspace-memory runtime and prove real SignKit sync/index/search plus full and forced agent-start retrieval. Python `3.13.3`, `memsearch 0.4.17`, `588` synchronized files, `16042` direct chunks, `16047` project-collection chunks, truthful unavailable shared-collection status, and preserved legacy Milvus state are recorded in `docs/review/agent_start_retrieval_runtime_proof_2026-08-14.md` and QA-45. All-project retrieval quality, provider portability, hosted execution, and post-calibration context regeneration remain open.
- [x] `RECON-30` Resolve calibration artifact preservation: manifests, reports, and provenance notes are visible and tracked; generated PNG/PDF assets remain ignored and reproducible from recorded builder metadata; the artifact-policy plus calibration focused suite passes `10` checks; and all four 120-sample reports rerun successfully. See `docs/review/calibration_artifact_policy_proof_2026-08-14.md`. Clean-checkout CI, permissioned real data, privacy governance, the product accuracy bar, and threshold promotion remain open.
- [x] `RECON-31` Preserve and reconcile the concurrent commit-hook authority variant. The alternate `.githooks` scripts are archived under `docs/archive/parallel/agent-hook-operating-doctrine-2026-08-14/`; active SignKit hooks retain project-local `motto_v5.md` attestation and pass shell syntax checks. Reopen only through a documented doctrine-source decision with updated tests.

RECON-30 evidence correction: the initial checklist line recorded the first
`9`-check artifact-policy run. QA-49 and the artifact proof supersede that
checkpoint with `10` checks after loader metadata validation was added.

QA-51 fresh local operator evidence is recorded in
`docs/review/local_product_operator_proof_2026-08-14.md`. It covers the
canonical landing and workspace, isolated local stack, source-to-ready retry
recovery, and authenticated metadata-only browser bridge. Hosted, provider,
packaged/cross-platform, assistive-technology, legal-signature, and real-user
gates remain separate.

The local closure claim is intentionally narrower than a hosted or packaged
release claim. Hosted deployment, provider activation, signed artifacts,
cross-platform installation, and external user research remain separate
backlog gates.

The local packaged-runtime claim is also deliberately narrow: QA-20 is closed
for macOS ARM64 only. Intel, Windows, Linux, notarization, clean installation,
rollback, hosted deployment, and provider activation remain open.

## Status synchronization addendum (2026-08-14)

`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md` is the canonical task
authority. This condensed TODO now reflects local closures proved by QA-23,
QA-53, and QA-55 while retaining unresolved hosted, provider, signing,
notarization, cross-platform, and rollback work as in-progress or pending.

The untracked root `TODO.md` is preserved separately as a parallel calibration
work record. It contains real-corpus, product-accuracy, and environment notes;
it is not silently merged into this launch TODO or treated as a competing
current status authority. Its items remain represented in the Product Owner
backlog as `RECON-24` and `RECON-28` where applicable.

Fresh local operator browser observation is recorded as `QA-61` in
`docs/review/local_operator_browser_observation_2026-08-14.md`. It advances
`L1-08` locally while packaged/cross-platform stale-state,
assistive-technology, hosted, and real-user gates remain open.

The local optional-analytics boundary is recorded as `QA-62` in
`docs/review/local_analytics_boundary_proof_2026-08-14.md`. Missing `gtag` is
silent, the canonical asset is explicitly versioned for cache invalidation,
configured event forwarding remains covered, and provider activation, consent,
hosted parity, and production observability remain separate gates.

---

Notes

- Pending items marked [~] have code in place; needs verification or minor follow-ups.
- If you want these grouped differently or tracked per-milestone, say the word and I’ll split into M1/M2 with dates.
