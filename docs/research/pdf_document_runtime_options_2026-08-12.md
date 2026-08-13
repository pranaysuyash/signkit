# PDF Document Runtime Options

Date: 2026-08-12

## Decision

SignKit keeps PDFium as the canonical desktop rendering and field-detection
engine. The application-level correctness baseline is a process-wide PDFium
lock with explicit document cleanup. A disposable child-process boundary is
the availability and blast-radius boundary for unattended, arbitrary, or
hosted document processing.

The reusable seam is `desktop_app/pdf/document_runtime.py`, with the one-shot
worker in `desktop_app/pdf/document_worker.py`. The desktop viewer can select
`runtime_mode="isolated"` or set `SIGNKIT_PDF_DOCUMENT_RUNTIME=isolated`.
Interactive desktop behavior remains explicitly `in_process` by default until
the operator workflow is migrated and its recovery UX is verified.

## Option evaluation

| Option | Concurrency safety | Survives native crash | Hosted reuse | Decision |
| --- | --- | --- | --- | --- |
| Process-wide PDFium lock | Yes for application calls | No | Weak | Keep as baseline |
| Persistent PDF worker | Yes | Yes | Good | Not the first boundary; long-lived native state remains |
| Disposable worker per operation/job | Yes | Yes | Excellent | Canonical isolation seam |
| Process pool | Yes | Yes | Excellent throughput | Later, after job/idempotency metrics |
| qpdf `--check` preflight | Early structural signal | No | Good | Optional gate, not a sandbox |
| PDF.js worker | Browser preview isolation | Browser-side only | Preview only | Do not use for signing/extraction truth |
| MuPDF/PyMuPDF replacement | Changes engine | Not inherently | Possible | Rejected now; does not solve process safety |
| Transparent dual-engine fallback | Complicated | Depends on both engines | Difficult to audit | Rejected for canonical processing |

## Why the chosen boundary is durable

- Native PDFium state never crosses the parent/worker IPC boundary.
- A timeout, invalid result, or non-zero child exit becomes a structured
  `DocumentRuntimeError` in the parent.
- The worker is one-shot, so native state is discarded after the operation.
- The same request/result shape can be hosted in a disposable sandbox worker
  without coupling a future API route to Qt.
- The viewer retains one canonical detection pipeline rather than creating a
  second detector implementation.

## qpdf preflight policy

`desktop_app/pdf/preflight.py` exposes qpdf without making it a hard runtime
dependency. `--check` results are classified as `clean`, `warnings`, `errors`,
`timeout`, `failed`, or `unavailable`. Unavailability is explicit and
non-blocking for local desktop use. The unattended/API policy should require
an installed qpdf or an equivalent structural gate before accepting arbitrary
documents, then still process them in an isolated worker.

qpdf is not installed in the current `.venv` or host command path, so the
current evidence covers the adapter contract with mocked exit codes, not a
real qpdf binary. Installing qpdf is an environment/deployment decision, not a
Python dependency change.

## Research basis

- [pypdfium2 Python API and thread-safety guidance](https://pypdfium2.readthedocs.io/en/stable/python_api.html)
- [qpdf command-line checking and exit codes](https://qpdf.readthedocs.io/en/stable/cli.html)
- [PyMuPDF multiprocessing guidance](https://pymupdf.readthedocs.io/en/latest/faq.html)
- [PDF.js browser display and worker setup](https://mozilla.github.io/pdf.js/getting_started/?lang=en)

## Follow-up closure

The isolated boundary is implemented and the local-companion workspace route
now calls this seam by default for local PDF inspection, with bounded input,
artifact cleanup, audit metadata, and retry/idempotency rules. The remaining
product step is a future hosted or unattended job runner with cancellation,
durable asynchronous job state, deployment sandboxing, and production
observability. That remains intentionally separate from the Qt viewer default
so a silent change in desktop recovery behavior is not introduced.
