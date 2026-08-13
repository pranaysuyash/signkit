# PDF Stack Setup and Selection Policy

Last updated: `2026-06-18`

## Why this exists

This project uses a multi-library PDF stack because each workflow has different
reliability, size, and API requirements. We keep one canonical policy in
`desktop_app/pdf/stack_profile.py` and map each workflow to one primary package.

Hard constraint from the architecture:

- one workflow → one primary package path
- `fitz` → `pikepdf` fallback for signing only
- runtime checks in one place (`stack_profile`) instead of scattered conditionals
- open-source-first default: `fitz` is opt-in

## Canonical role map (current implementation)

| Capability | Primary package | Fallback | Why it is used |
| --- | --- | --- | --- |
| Page rendering in PDF tab | `pypdfium2` | none | Fast rasterization and low-latency preview rendering |
| Signature placement / image stamping (`PDFSigner.add_signature`) | `PyMuPDF` (`fitz`) when enabled | `pikepdf` | PyMuPDF is strong for placement and widgets; `pikepdf` keeps signing available in OSS-default mode |
| Native form field inspection/edit (`PdfFormFieldEditor`) | `PyMuPDF` (`fitz`) when enabled | none | Widget APIs are needed for true form-field workflows |
| Structural edits + low-level fallback | `pikepdf` | none | Compact and deterministic fallback path for stream/object operations |
| Field heuristics (`SignatureFieldDetector`) | `pypdfium2 + cv2` | none | Mixed signal: rendered image + form metadata |
| OCR scan hints (`SIGNKIT_PDF_SCAN_PREPROCESS`) | `cv2 + pytesseract` | none | Optional text-aware hints for scanned forms |

### What each package maps to in code

- `pypdfium2`
  - `desktop_app/pdf/renderer.py` → `PDFRenderer.render_page`
  - `desktop_app/pdf/field_detection.py` → `_detect_rendered_page_candidates`
  - `desktop_app/pdf/stack_profile.py` → profile state for rendering availability
- `PyMuPDF` (`fitz`)
  - `desktop_app/pdf/signer.py` → `PDFSigner.add_signature` and save path
  - `desktop_app/pdf/form_fields.py` → `PdfFormFieldEditor.detect_pdf` / `fill_field`
  - `desktop_app/views/main_window_parts/pdf.py` → signing fallback status hints
- `pikepdf`
  - `desktop_app/pdf/signer.py` → fallback signing path in `PDFSigner.add_signature`
  - `desktop_app/pdf/field_detection.py` → `SignatureFieldDetector._detect_acroform_candidates`
  - `desktop_app/pdf/stack_profile.py` → signing fallback inventory
- `opencv-python` (`cv2`)
  - `desktop_app/pdf/field_detection.py` → `_detect_from_image`
- `pytesseract`
  - `desktop_app/pdf/field_detection.py` → `_detect_ocr_candidate_hints`

## Current package availability policy

Runtime policy is computed from:
- `desktop_app/pdf/stack_profile.py`
- `choose_signer_backend()` and `signing_backend_report()` for signing-chain visibility
- `stack_install_hint()` for operator-facing install guidance
- `SIGNKIT_ALLOW_PYMUPDF_SIGNING` and `SIGNKIT_PDF_SCAN_PREPROCESS` for optional modes

You can check policy output by running:

```bash
python - <<'PY'
from desktop_app.pdf.stack_profile import get_pdf_stack_profile, signing_backend_report
print(signing_backend_report())
print(get_pdf_stack_profile())
PY
```

## Installation

### Default OSS-first profile

```bash
python -m pip install pypdfium2 pikepdf
```

- `pypdfium2` is required for the PDF preview pipeline.
- `pikepdf` is required as the non-`fitz` signing path.
- `PyMuPDF` is intentionally opt-in to keep the base stack open-source-first.

### Capability profiles

- Preview only:
  - `python -m pip install pypdfium2`
- Signing (fallback-safe without `fitz`):
  - `python -m pip install pikepdf`
  - plus `python -m pip install pypdfium2` if PDF viewer is needed
- Full current feature set (non-default opt-in):
  - `python -m pip install pypdfium2 pikepdf`
  - `python -m pip install -r desktop_app/requirements-pymupdf-optional.txt`
  - `python -m pip install -r desktop_app/requirements-pdf-optional.txt`
  - set `SIGNKIT_ALLOW_PYMUPDF_SIGNING=1`

The optional files keep non-default capabilities explicit and discoverable:
- `requirements-pymupdf-optional.txt`: explicit `PyMuPDF` enablement
- `requirements-pdf-optional.txt`: optional `pypdf` (annotations), `pytesseract` (OCR hints), and `pyHanko` with its cryptographic dependencies for certificate-backed PAdES signing.
- Scan/OCR heuristics:
  - `python -m pip install opencv-python pytesseract`
  - install system Tesseract binary (required by pytesseract)
  - set `SIGNKIT_PDF_SCAN_PREPROCESS=true`

### Why these choices

- Rendering is split from signing because one library is not best-in-class for both.
- Signing keeps a robust fallback (`pikepdf`) so the app remains operational when `fitz` is disabled.
- Certificate-backed PAdES signing is explicit through `sign_pdf_with_certificate()` and requires a PKCS#12 credential; it is separate from visual image placement. The desktop Save Signed PDF action asks the operator to choose visual placement or certificate-backed PAdES semantics, and certificate mode reports the verified artifact receipt. `desktop_app/pdf/credentials.py` provides a provider boundary and macOS Keychain passphrase adapter. It remains opt-in until signer authorization, key custody, and trust policy are configured.
- Timestamping is also explicit: pass `timestamp_url` for an HTTP RFC 3161 provider or inject a `timestamper`; baseline local signing does not contact a TSA. External TSA, revocation, DSS/VRI, and long-term validation requirements remain separate production gates.
- PDFium rendering and field detection are serialized through `desktop_app/pdf/pdfium_runtime.py` because the native PDFium library is not thread-safe. Long-lived PDFium documents are explicitly closed; if a native crash recurs, the documented escalation is process isolation rather than relying on repeated in-process retries.
- For unattended or arbitrary-document work, use `SIGNKIT_PDF_DOCUMENT_RUNTIME=isolated` or pass `runtime_mode="isolated"` to `PDFViewer.detect_fields_for_pages()`. This runs each operation in the disposable `desktop_app/pdf/document_worker.py` process through `desktop_app/pdf/document_runtime.py`.
- `desktop_app/pdf/preflight.py` exposes optional qpdf `--check` structural inspection. qpdf is an early signal, not a sandbox; the isolated worker remains required for untrusted documents. qpdf is not installed in the current local environment, so deployment must make its availability policy explicit.
- The local-companion workspace route `POST /workspace/executions/{execution_id}/document-inspections` accepts only explicit `local` topology, runs transient PDF inspection through the isolated worker, persists hash/result metadata, and does not retain source bytes. Hosted/cloud document execution remains gated separately.
- OCR/scan preprocessing is explicitly opt-in because it adds runtime and dependency overhead.
- This follows the long-term rule that each workflow may combine multiple engines, but each engine gets one explicit role.

## Environment toggles

- `SIGNKIT_ALLOW_PYMUPDF_SIGNING`
  - values: `0`, `false`, `no`, `off` (default off), `1`, `true`, `yes`, `on`
  - when enabled, `PDFSigner` attempts `fitz` first then falls back to `pikepdf`
- `SIGNKIT_PDF_SCAN_PREPROCESS`
  - values: `0`, `false`, `no`, `off` (default off), `1`, `true`, `yes`, `on`, `scan`
  - when enabled and dependencies exist, adds rendered-image heuristics and OCR keyword hints
- `SIGNKIT_DISABLE_PDF_BACKEND_TELEMETRY=1` disables backend telemetry capture
- `SIGNKIT_PDF_BACKEND_TELEMETRY_PATH=/custom/path/pdf_backends.jsonl` custom telemetry file path

## Why this is not a redundant stack

- Rendering, signing, and field workflows optimize different tradeoffs.
- We keep one primary path per job type and one fallback path for signing only.
- This is not duplicate work; it avoids forcing a single library to own all roles it is weaker at.

## Commercial-safe license posture

The default stack is intentionally chosen so the app can remain commercially
usable under open-source licenses.

| Package | License posture | Commercial use | Notes |
| --- | --- | --- | --- |
| `pypdfium2` | Apache-2.0 or BSD-3-Clause | Yes | Strong default renderer for commercial products |
| `pikepdf` | MPL-2.0 | Yes | Commercial use is allowed; source-level changes to pikepdf itself must be published |
| `pypdf` | BSD-3-Clause | Yes | Safe pure-Python utility/editing path |
| `pdf.js` | Apache-2.0 | Yes | Strong for browser rendering and hybrid web delivery |
| `pdf-lib` | MIT | Yes | Very safe for browser-side export/manipulation |
| `pdfmake` | MIT | Yes | Very safe for declarative report generation |
| `PDFKit` | MIT | Yes | Very safe for programmatic PDF generation |
| `pdfplumber` | MIT | Yes | Safe for layout extraction and debugging |
| `pdf2image` | MIT | Yes | Safe as a Poppler wrapper; external tool packaging still matters |
| `docTR` | MIT | Yes | Safe for commercial OCR / document understanding work |
| `Docling` | MIT | Yes | Safe for commercial document understanding work |
| `OCRmyPDF` | MPL-2.0 | Yes | Commercial use is allowed; source-level changes to OCRmyPDF itself must be published |
| `EasyOCR` | Apache-2.0 | Yes | Safe for commercial OCR work |
| `PyMuPDF` | AGPL/commercial dual license | Not default | Keep opt-in only unless the team explicitly accepts the AGPL/commercial tradeoff |

In short:

- safe baseline commercial stack: `pypdfium2`, `pikepdf`, `pypdf`, `pdf.js`,
  `pdf-lib`, `pdfmake`, `PDFKit`, `pdfplumber`, `pdf2image`, `docTR`,
  `Docling`, `OCRmyPDF`, `EasyOCR`
- not default: `PyMuPDF`
- optional only if the project explicitly wants it: `PyMuPDF`

## Next build/improvement candidates (from current state)

1. Add a small policy page in docs for legal/commercial packaging choices around opt-in libraries.
2. Add lightweight tests for `desktop_app/pdf/stack_profile.py` profile behavior under env toggles.
3. Add `pytesseract` as an optional docs dependency for scanner environments.
4. Add a small UI hint for users when scan/OCR mode is disabled and no hint candidates will be returned.
5. See the broader library survey in `docs/analysis/PDF_LIBRARY_EXPLORATION_2026-06-17.md`.
6. See the preserved long-form architecture memo in `docs/analysis/LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md`.

## Durable document sessions

- Signature placements are persisted per PDF so reopening the same document can restore the export recipe later.
- The signature vault stores the image assets, while the document session store keeps placement geometry and page association.
- If the source PDF changes materially, the saved placements may be skipped rather than applied blindly.

## Cross-References

- [Long-Term PDF Workspace Architecture](analysis/LONG_TERM_PDF_WORKSPACE_ARCHITECTURE_2026-06-18.md)
- [PDF Library Exploration](analysis/PDF_LIBRARY_EXPLORATION_2026-06-17.md)
- [PDF Platform Convergence](analysis/PDF_PLATFORM_CONVERGENCE_2026-06-17.md)
