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
