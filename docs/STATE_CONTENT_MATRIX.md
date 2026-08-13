# SignKit state and recovery content matrix

Date: 2026-08-13
Status: Current contract for implementation and QA

Every meaningful operator state must answer four questions: what happened,
whether output exists, what the operator can do next, and what the system
recorded. Technical identifiers may be available in details, but they are not
the primary message.

| State | User-visible meaning | Safe next action | Operator/receipt requirement |
| --- | --- | --- | --- |
| Source selected | An input was accepted for local processing | Select a mark or inspect the source | Record source name/hash and size limits |
| Mark selected | A candidate region was chosen | Clean or change the selection | Record coordinates and source relationship |
| Cleaned | A cleaned candidate is available for review | Review, save, or redo cleanup | Preserve input and candidate provenance |
| Needs review | Automatic processing stopped for a human decision | Inspect, adjust, approve, or quarantine | Record reason and whether retry is safe |
| Saved | A local Vault/project write completed | Place on PDF or reopen saved item | Record local path/reference and write result |
| Placed | A candidate was positioned in the document session | Review pages and appearance | Record page, coordinates, and document hash |
| Exported | Output was written successfully | Open, share, or start another task | Record output path/hash and export mode |
| Retry available | The previous operation may be repeated under its contract | Retry with the same or a new request key as specified | Record replay versus new attempt |
| Failed | The operation did not complete safely | Read reason, retry if allowed, or quarantine | Record error class, input impact, and recovery |
| Quarantined | The item is isolated from automatic progression | Inspect, repair input, or remove deliberately | Keep audit record and explain retention/deletion |
| Cancelled | The operator stopped progression | Resume only through an explicit action | Record partial work and cleanup status |
| Local companion online | Loopback coordination is available | Continue local workflow; inspect service details if needed | Do not describe this as cloud availability |
| Local companion offline | Core local work remains available, but coordination is unavailable | Continue local work or retry service startup | Show dependency impact and recovery action |
| Hosted request pending | A remote request was accepted but not complete | Inspect status or wait according to the contract | Record request key, owner, timestamp, and provider |
| Hosted request rejected | The remote boundary denied or could not safely process the request | Correct authorization/input or retry only if allowed | Record denial reason without leaking sensitive data |
| Deleted with cleanup complete | The requested logical asset is deleted and temporary artifacts were cleaned | Continue or verify audit receipt | Retain the minimum audit receipt required by policy |
| Deleted with cleanup incomplete | Logical deletion occurred but physical cleanup needs recovery | Follow operator cleanup runbook; do not silently retry | Surface cleanup state, age, and owner |

## Surface mapping

| Surface | Current responsibility | Required alignment |
| --- | --- | --- |
| Desktop extraction and PDF views | Source, mark, clean, review, save, place, export | Use the glossary terms and expose recovery before advanced controls |
| Desktop workflow console | Run, retry, cancel, quarantine, audit | Explain safe retry and partial-failure outcome |
| Desktop status and onboarding | Local companion health and product boundary | Never call a loopback service cloud; avoid absolute offline claims |
| Browser workspace | Metadata-first execution and local inspection proof | Keep document-byte and hosted-signing limits explicit |
| Public landing and checkout | Acquisition, product boundary, provider state | Bind claims to the registry and deployment probe |
| Support and legal documents | Recovery, refund, privacy, licensing, and limitations | Use one canonical vocabulary and dated policy source |

## Closure criteria

The matrix is implementation-complete when each state is mapped to an actual
control or message, a test or runtime observation proves the binding, and the
operator can recover from malformed input, timeout, duplicate request, partial
export, deletion cleanup failure, and local companion outage without guessing.

## Addendum (2026-08-13): desktop operator receipt binding

The desktop workflow console now renders a read-only metadata-only execution
passport for the selected job. It shows aggregate state, bounded recovery
action, attempt count, source of truth, data boundary, and ordered state-event
codes. It intentionally omits input/output paths, raw error messages, and
document bytes from this operator receipt view. The projection remains backed
by `desktop_app/workflows/passport.py` and the durable workflow store; the UI
does not create a second state machine.

Targeted evidence: `desktop_app/tests/test_workflow_screen_smoke.py` and
`tests/test_execution_passport_contract.py` passed together with the Qt
environment. Full source-to-export runtime observation and manual verification
of malformed-input, timeout, partial-export, cleanup, and local-companion
outage recovery messages remain open.

## Addendum (2026-08-13): disposable source-to-ready observation

`tools/run_local_source_to_ready_proof.py` has a fresh Tier 4 local result
recorded in `docs/review/local_operator_state_proof_2026-08-13.md`. It observes
source extraction, encrypted Vault round trip, a forced `ERR_SIGNING_FAILED`
transition to `retry`, canonical retry to `completed`, metadata-only passport
projection, and a verified visual placement artifact receipt. Hosted contact
and browser document-byte transfer were both false in the manifest.

The proof advances the local source-to-export state contract but does not close
the remaining malformed-input, timeout, partial-export, deletion-cleanup, or
local-companion-outage states.

## Addendum (2026-08-13): canonical operator copy binding

`desktop_app/workflows/operator_content.py` now owns the primary desktop
labels for persisted workflow states and bounded outcome messages. The
workflow console uses those labels instead of raw enum values or stored
exception text. Technical receipt events remain available through the existing
metadata-only passport and workflow store, while paths and raw exceptions are
not presented as the primary failure message.

## Addendum (2026-08-13): local companion outage copy binding

`desktop_app/workflows/operator_content.py` now also owns the bounded copy for
the local companion lifecycle: checking, starting, online, and offline. The
desktop extraction surface, main-window health monitor, and onboarding dialog
use this layer. An outage tells the operator that core local document work
remains available and that retry or continued local work is possible; raw
endpoint, timeout, or exception details are reserved for logs and are not the
primary message.

Targeted evidence: `tests/test_operator_content.py` and
`tests/test_topology_experience_contract.py` passed as QA-30. This binds the
copy contract but does not prove process restart, stale companion recovery,
assistive-technology behavior, or packaged-runtime outage observation.

## Addendum (2026-08-13): malformed-input recovery binding

The workflow matcher and engine now classify missing, non-PDF, unreadable, and
invalid-geometry inputs as `NEEDS_REVIEW` with the typed code
`ERR_INPUT_INVALID`. The transition does not consume a retry attempt because
the safe next action is to choose or repair the source, not to repeat the same
invalid request. Parser details remain bounded technical evidence, while the
primary operator copy tells the user to choose a readable PDF or review the
source.

Targeted evidence: `desktop_app/tests/test_workflow_engine.py` and
`tests/test_operator_content.py` passed as QA-31.

## Addendum (2026-08-13): partial-export recovery binding

The PDF save surface now treats an export as ready only after
`desktop_app/workflows/verifier.py` confirms that the output exists, is
non-empty, and differs from the source. If the destination did not exist
before the attempt and export or verification fails, the newly created output
is removed before the operator is notified. The primary message is bounded
and explicitly says that no incomplete output was kept; technical error class
is retained only for the audit path.

Targeted evidence: `tests/test_pdf_export_recovery_contract.py`,
`tests/test_operator_content.py`, `desktop_app/tests/test_export_mode_dispatch.py`,
and `tests/test_artifact_receipt.py` passed as QA-32. This does not establish
packaged, device, certificate-provider, or assistive-technology observation.

## Addendum (2026-08-13): local library deletion cleanup binding

Local library deletion now validates the resolved path remains inside the
library root, removes the image and JSON sidecar as one operator action, and
writes a metadata-only deletion receipt. The result distinguishes
`deleted`, `cleanup_incomplete`, and `not_deleted`; the UI explains the
cleanup-incomplete state without exposing the path. The boolean `delete_item`
compatibility wrapper remains for older callers, while the desktop surface
uses the structured result.

Targeted evidence: `tests/test_library_deletion_contract.py`,
`desktop_app/tests/test_main_window_logic.py`, and
`tests/test_operator_content.py` passed as QA-33. Permission-denied,
cross-device, and restart/recovery observations remain open.

## Addendum (2026-08-13): local companion retry binding

The desktop status surface now exposes an explicit `Retry local service`
control when the companion is offline. The retry runs `BackendManager.restart`
off the UI thread, returns to Online only after the existing health proof
passes, and keeps the control visible when restart does not reach a healthy
state. Typed timeout failures use bounded local recovery copy. The control
does not imply hosted availability or cryptographic document signing.

Targeted evidence: `desktop_app/tests/test_main_window_logic.py`,
`tests/test_topology_experience_contract.py`, and
`tests/test_operator_content.py` passed as QA-34. A real process restart,
stale-state recovery, packaged-runtime observation, and assistive-technology
observation remain open.

## Addendum (2026-08-13): local companion process recovery observation

The real local runtime now has Tier 4 evidence for start, health readiness,
restart, second health readiness, and clean shutdown through
`BackendManager`. The desktop Retry local service control delegates to this
existing lifecycle rather than introducing a second process owner. The proof
is isolated to a disposable local data directory and does not establish
packaged, cross-platform, hosted, or assistive-technology behavior.

Evidence: `docs/review/local_companion_restart_proof_2026-08-13.md` and QA-35.

## Addendum (2026-08-13): canonical web accessibility semantics

The canonical root and backend-mounted workspace now share a stable
`main#main-content` landmark and visible-on-focus skip link across login and
authenticated states. The dynamically rendered local PDF file control has an
explicit label association. Focused semantic contracts and the real local
Chrome proof passed as QA-36. This closes only the local semantic and
browser-observable sub-gate; VoiceOver/screen-reader, manual zoom/reflow,
device, packaged, cross-platform, hosted, and formal WCAG evidence remain
open.
