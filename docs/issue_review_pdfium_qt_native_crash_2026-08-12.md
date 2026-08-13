# PDFium and Qt Native Crash Review

Date: 2026-08-12
Status: Corrective fix implemented; residual native-runtime risk monitored
Severity: P1 desktop PDF reliability
Owner: Desktop/PDF Runtime

## Finding

A combined Qt workflow and PDF field-detection test invocation previously exited with a native `pypdfium2` segmentation fault during PDFium render/close activity. The failure was not a Python assertion and could terminate the whole desktop process. The two suites passed when run separately, which narrowed the issue to lifecycle/thread interaction but did not make the product safe.

## Root-cause assessment

The application used PDFium from multiple execution contexts:

- `PDFRenderer` rendered and closed a long-lived document on the Qt/UI path.
- `SignatureFieldDetector` opened, rendered, and closed separate documents on a `QThreadPool` worker.
- `PdfEngine` held another long-lived PDFium document without an explicit close method.

The upstream pypdfium2 contract states that PDFium is not thread-safe, recommends serialization with a mutex, warns that closing a parent closes child handles, and recommends explicit close and process isolation for parallel work. The observed stack was consistent with concurrent native use and teardown, but the original crash was not reproduced deterministically in every fresh process.

## Corrective implementation

Added `desktop_app/pdf/pdfium_runtime.py` with a process-wide reentrant `PDFIUM_LOCK` and `pdfium_operation()` context manager. All discovered PDFium operations now use it:

- renderer open, page count, page size, render, and close;
- rendered and OCR field detection open, page access, render, and close;
- legacy `PdfEngine` load, render, and explicit close/destructor.

The lock covers native bitmap conversion and cleanup, not only the initial call, so a parent document cannot be closed concurrently with child-page work. The application still keeps PDFium work off the UI thread for batch detection, but native calls are serialized.

## Evidence

- Prior combined crash: observed in the earlier Qt/PDFium investigation and recorded in the referenced task conversation.
- Three pre-fix fresh `faulthandler` runs later passed, confirming nondeterminism rather than disproving the risk.
- Five guarded post-fix fresh-process runs: `19 passed` each, including workflow smoke, PDF bulk detection, and PDFium runtime stress.
- `desktop_app/tests/test_pdfium_runtime.py`: `3 passed`, including concurrent detector/rendering and legacy-engine close lifecycle.
- PDF/runtime regression set: `33 passed`.
- Full `desktop_app/tests/test_pdf_features.py`: `24 passed`.
- Compilation and `.venv/bin/python -m pip check`: passed.

These are S1 targeted and repeated runtime checks. They are not production-like Tier 3 evidence, and a passing native test cannot prove that every PDFium input is safe.

## Residual risk and trigger

The fix addresses the application-level race and lifetime gap. PDFium remains native code, and malformed or adversarial PDFs could still expose upstream faults. If any future faulthandler/native crash occurs after this fix, the next response is not another retry: isolate rendering and field detection in a worker process with an IPC/result contract, capture the exact PDF fixture, pin or upgrade pypdfium2 only with compatibility evidence, and preserve the crash artifact for upstream triage.

## Research

- [pypdfium2 Python API: threading and memory management](https://pypdfium2.readthedocs.io/en/stable/python_api.html)
- [pypdfium2 project overview and known limitations](https://github.com/pypdfium2-team/pypdfium2)

## Addendum: worker boundary and option binding (2026-08-12)

The planned process-isolation response is now implemented as a reusable
boundary rather than a crash-specific script:

- `desktop_app/pdf/document_runtime.py` starts one child process per operation
  and converts timeout, invalid response, and child exit into a structured
  `DocumentRuntimeError`.
- `desktop_app/pdf/document_worker.py` owns the PDFium objects and emits only
  JSON metadata or base64 PNG bytes.
- `PDFViewer.detect_fields_for_pages()` accepts `runtime_mode="isolated"` and
  honors `SIGNKIT_PDF_DOCUMENT_RUNTIME=isolated`.
- `desktop_app/pdf/preflight.py` provides an optional qpdf structural check;
  qpdf is not installed in this environment, so its binary behavior remains
  deployment evidence to collect.

The full option comparison and hosted/API boundary decision are recorded in
`docs/research/pdf_document_runtime_options_2026-08-12.md`. This closes the
desktop isolation implementation task, but not the future ContractDesk job
runner integration, which still requires timeout, cancellation, cleanup,
audit metadata, and idempotent retry behavior. The local-companion route now
provides that bounded synchronous integration; hosted/unattended cancellation
and asynchronous job state remain separate work.
