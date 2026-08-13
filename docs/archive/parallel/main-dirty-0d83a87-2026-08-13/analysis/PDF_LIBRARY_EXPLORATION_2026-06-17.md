# PDF Library Exploration

Date: `2026-06-17`

## Purpose

This note records a broader exploration of open-source PDF-related libraries for
the desktop app. It is intentionally wider than the current implementation in
`desktop_app/pdf/stack_profile.py` and `docs/PDF_SETUP.md`.

The goal was not to find one magical library for every job. The goal was to map
the library space by workflow and identify the best long-term fit for:

- rendering and preview
- structural editing and signing
- text/layout extraction
- OCR and scan preprocessing
- future searchable-PDF workflows

## Evidence Standard

This pass is based on:

- current repo structure and existing codepaths
- official project docs and PyPI metadata

This pass did not run runtime benchmarks or end-to-end tests. So this is a
documented research pass, not a verified performance study.

## Current Product Constraints

The repo already needs a split stack because the product has distinct behaviors:

- PDF viewing / rendering
- signature placement
- field detection
- scan/OCR-assisted hints
- future searchable-PDF support

Those behaviors do not collapse cleanly into one library without tradeoffs.

## Library Space By Role

### Rendering and viewer display

#### `pypdfium2`

- Official docs describe it as a PDFium binding focused on rendering and PDF
  operations.
- Latest release on PyPI was `2026-06-01`.
- It is a strong fit for desktop preview rendering and viewer navigation.
- It is the best default choice for this app’s rendering role.

Source links:

- [pypdfium2 docs](https://pypdfium2.readthedocs.io/)
- [pypdfium2 PyPI](https://pypi.org/project/pypdfium2/)

#### `pdf.js`

- Browser-native PDF rendering engine with prebuilt distribution artifacts.
- Best fit when the product surface is a web app or embedded browser view.
- For this desktop app, it is interesting as a rendering reference and possible
  future hybrid viewer path, but not as the current primary engine because the
  app is already structured around local Python/Qt rendering.
- Worth exploring if we later want a web-based PDF viewer or shared browser
  rendering layer.

Source links:

- [pdf.js README](https://github.com/mozilla/pdf.js/blob/master/README.md)

#### `pdf2image`

- It wraps Poppler tools to convert PDF pages into images.
- It is MIT licensed.
- It is viable as a rendering fallback, but it introduces an external Poppler
  dependency and is more of a conversion wrapper than a core PDF viewer engine.
- I would not make it the primary viewer backend for this app.

Source links:

- [pdf2image GitHub](https://github.com/Belval/pdf2image)

#### `PyMuPDF`

- Strong rendering and manipulation package.
- Official docs say it is available under AGPL or commercial license terms.
- That makes it a poor default for this repo given the open-source-only
  requirement.
- It remains a useful opt-in advanced path if a future distribution explicitly
  accepts those terms.

Source links:

- [PyMuPDF docs](https://pymupdf.readthedocs.io/)
- [PyMuPDF license note](https://pymupdf.readthedocs.io/en/latest/about.html)

### Structural editing and signing

#### `pikepdf`

- Official docs position it as a library for creating, manipulating, parsing,
  repairing, and rewriting PDFs.
- Latest release on PyPI was `2026-06-08`.
- It is the best baseline fallback for structural edits and robust save paths.
- It fits the current repository well because it keeps the non-AGPL signing path
  available.

Source links:

- [pikepdf docs](https://pikepdf.readthedocs.io/)
- [pikepdf PyPI](https://pypi.org/project/pikepdf/)

#### `pypdf`

- Pure-Python, BSD-licensed, current, and actively maintained.
- Latest release on PyPI was `2026-06-17`.
- It is strong for splitting, merging, rotation, page transforms, text, and
  metadata operations.
- It is not a direct replacement for the current signing fallback path because
  it does not give the same low-level editing and placement leverage as qpdf /
  pikepdf.
- I would keep it in the candidate set for future utility operations, not as the
  primary signing backend.

Source links:

- [pypdf docs](https://pypdf.readthedocs.io/)
- [pypdf PyPI](https://pypi.org/project/pypdf/)

#### `PyMuPDF`

- Best-in-class ergonomics for some PDF manipulation jobs.
- Still not a default choice here because of the license posture.
- Good as an explicit opt-in advanced editing path, not the baseline path.

Source links:

- [PyMuPDF docs](https://pymupdf.readthedocs.io/)

### OCR and scan preprocessing

#### `pytesseract` + Tesseract

- `pytesseract` is a light Python wrapper around the Tesseract engine.
- It is good for keyword-level OCR hints and text extraction assistance.
- It is not a full OCR product on its own; it depends on the system Tesseract
  binary.
- This is a practical optional path for scan-mode hinting.

Source links:

- [pytesseract PyPI](https://pypi.org/project/pytesseract/)

#### `EasyOCR`

- Latest release on PyPI was `2024-09-24`.
- It is Apache-2.0 licensed and supports many scripts.
- It is attractive when we want higher-level OCR with less handwritten glue
  code.
- Its main drawback for this app is the larger runtime footprint through PyTorch
  and its broader deployment complexity.
- I would keep it as a future OCR candidate, not the default scan helper.

Source links:

- [EasyOCR PyPI](https://pypi.org/project/easyocr/)

#### `OCRmyPDF`

- Latest release on PyPI was `2026-06-12`.
- It is a strong tool for making scanned PDFs searchable and improving OCR
  quality.
- It is not a narrow signature-hint helper; it is more of a full document
  preprocessing pipeline.
- It becomes interesting if the roadmap includes searchable-PDF export or scan
  cleanup as a first-class feature.

Source links:

- [OCRmyPDF docs](https://ocrmypdf.readthedocs.io/)
- [OCRmyPDF PyPI](https://pypi.org/project/ocrmypdf/)

#### `docTR`

- MIT-licensed OCR stack with text detection and recognition.
- Strong candidate when we want deep-learning OCR without building a pipeline
  from primitives ourselves.
- More appropriate than a tiny wrapper if we want a dedicated OCR feature slice.
- It is still heavier than `pytesseract`, so it should be introduced only when
  the simpler OCR path is no longer enough.

Source links:

- [docTR README](https://github.com/mindee/doctr/blob/main/README.md)
- [docTR PyPI](https://pypi.org/project/doctr/)

#### `Docling`

- MIT-licensed codebase with separate model packages.
- Strong for document parsing and advanced PDF understanding.
- More of a document intelligence framework than a narrow rendering engine.
- Worth exploring if the product evolves toward structured document extraction,
  layout understanding, or LLM-ready document pipelines.

Source links:

- [Docling README](https://github.com/docling-project/docling/blob/main/README.md)
- [Docling PyPI](https://pypi.org/project/docling/)
- [Docling models PyPI](https://pypi.org/project/docling-ibm-models/)

### Layout and text extraction

#### `pdfplumber`

- Great for detailed access to text characters, rectangles, lines, tables, and
  visual debugging.
- It is best on machine-generated PDFs.
- It does not do modification or OCR.
- It is a strong future candidate for richer field discovery and layout-aware
  inspection.

Source links:

- [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)

## Feature Coverage By Capability

This section maps product behaviors to the libraries that best cover them.
It answers the practical question: do these options cover highlighting, edits,
comments, and logging?

| Feature | Best fit now | Notes |
| --- | --- | --- |
| Page rendering | `pypdfium2` | Best default desktop renderer for the current architecture |
| Browser rendering | `pdf.js` | Best if we later want a browser or hybrid viewer |
| Highlight / underline / strikeout | `PyMuPDF`, `pypdf`, `pikepdf` | All can work with annotations; `PyMuPDF` is most ergonomic, `pypdf` is strongest pure-Python option, `pikepdf` is lower-level |
| Sticky notes / comments | `PyMuPDF`, `pypdf`, `pikepdf` | Supported as PDF annotations, but the current app does not expose a full annotation editor UI yet |
| Text edits / object edits | `pikepdf`, `pypdf`, `PyMuPDF` | `pikepdf` is strongest for structural edits, `pypdf` for pure-Python transforms, `PyMuPDF` for convenience |
| Redaction / cleanup | `PyMuPDF`, `pikepdf` | Better as a dedicated editing workflow than as part of the extraction-first baseline |
| Form fill / flatten | `pdf-lib`, `pypdf`, `PyMuPDF` | `pdf-lib` is especially attractive in browser-safe export flows |
| Audit logging | Current repo code + JSONL logs | Already present in `desktop_app/pdf/storage.py`; this is an app capability, not a library feature |
| Review markup persistence | `PyMuPDF`, `pypdf`, `pikepdf`, `pdf-lib` | All can represent annotations, but fidelity depends on the target viewer and save path |
| Report generation | `pdfmake`, `PDFKit`, `pdf-lib` | `pdfmake` is most declarative, `PDFKit` most programmatic, `pdf-lib` most modification-oriented |

### Browser-side PDF export and report generation

This is a separate bucket from viewer rendering. It matters when we want a
client-side report builder, exported audit report, or browser-safe PDF output.

#### `pdf-lib`

- Pure JavaScript and works in browsers, Node, Deno, and React Native.
- Best fit when we want a browser-safe open-source PDF manipulation engine.
- Strong for create/modify, copying pages, forms, images, metadata, and page
  composition.
- This is the best match for a client-side export path if the goal is to keep
  PDF generation inside the browser or front-end runtime.
- The npm metadata shows the latest published version as `1.17.1`; the package
  appears mature rather than fast-moving.

Source links:

- [pdf-lib README](https://github.com/Hopding/pdf-lib/blob/master/README.md)
- [pdf-lib npm](https://www.npmjs.com/package/pdf-lib)

#### `pdfmake`

- Pure JavaScript document generation library for server-side and client-side
  use.
- Better than `pdf-lib` when we want declarative report layout with tables,
  headers, footers, and page sections.
- Heavier and more opinionated than `pdf-lib`, but better suited to formal
  report composition.
- The npm metadata shows a fresh `0.3.11` release and recent publishing.

Source links:

- [pdfmake README](https://github.com/bpampuch/pdfmake/blob/master/README.md?plain=1)
- [pdfmake npm](https://www.npmjs.com/package/pdfmake)

#### `PDFKit`

- MIT-licensed and available for Node and the browser.
- Powerful low-level generation API with chainable layout primitives.
- More Node-shaped than `pdf-lib` or `pdfmake`, but still browser-capable.
- Best when we want programmatic control over drawing/text/layout and are okay
  writing more layout code ourselves.
- The npm metadata shows a current `0.19.1` release.

Source links:

- [PDFKit README](https://github.com/foliojs/pdfkit)
- [PDFKit docs](https://pdfkit.org/)
- [PDFKit npm](https://www.npmjs.com/package/pdfkit)

## Recommendation Matrix

| Role | Best current fit | Reason |
| --- | --- | --- |
| Viewer rendering | `pypdfium2` | Strong rendering focus, current release, and a good desktop bundle fit |
| Signing fallback | `pikepdf` | Robust structural editing and non-AGPL default path |
| Advanced signing/editing | `PyMuPDF` opt-in | Excellent capability, but not default because of license posture |
| Simple OCR hints | `pytesseract` + Tesseract | Light enough for keyword hints and scan assistance |
| Richer OCR pipeline | `OCRmyPDF` or `EasyOCR` | More powerful, but heavier and better suited to a separate OCR feature slice |
| Layout exploration | `pdfplumber` | Strong for text/line/shape inspection when we need more field-detection signal |
| Browser-style rendering | `pdf.js` | Best fit for web delivery, future hybrid viewer, or renderer parity checks |
| Deep OCR | `docTR` | Better than wrappers when we want a model-based OCR pipeline |
| Document understanding | `Docling` | Better aligned to structured extraction and downstream document intelligence |
| Browser-safe PDF export | `pdf-lib` | Best fit for client-side manipulation / export path |
| Declarative PDF reports | `pdfmake` | Better for tables, headers, footers, and structured report layout |
| Programmatic browser PDF generation | `PDFKit` | Best for low-level control when we can tolerate more layout code |

## What I Would Build Next

If the team wants to expand beyond the current baseline, I would prioritize:

1. `pdfplumber`-assisted layout detection for field discovery.
2. `OCRmyPDF`-backed searchable PDF preprocessing as a separate workflow.
3. `pdf.js` only if we need browser-view parity or a future hybrid desktop/web viewer.
4. `docTR` if OCR quality needs a better model-based approach than Tesseract.
5. `Docling` if we move toward structured document understanding rather than just signature extraction.
6. `EasyOCR` only if Tesseract-based hints prove insufficient on real documents.
7. `pdf-lib` if we build a client-side export/report path.
8. `pdfmake` if we need declarative report layout with repeated sections and tables.
9. `PDFKit` if we want lower-level programmatic control in a browser/Node export path.
10. `pypdf` for utility transforms if we want more pure-Python manipulation paths.

## Current Repo Coverage

The current repository already covers some of this feature surface directly:

- audit logging via [desktop_app/pdf/storage.py](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/pdf/storage.py)
- signature placement and saving via [desktop_app/pdf/signer.py](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/pdf/signer.py)
- field detection via [desktop_app/pdf/field_detection.py](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/pdf/field_detection.py)

What is not yet fully covered in-product:

- a dedicated annotation editor for highlights and comments
- a review workflow for annotation lists or comment threads
- redaction UX
- a browser-side report builder

Those are valid future slices, but they are not yet implemented as a full product surface.

## What I Would Not Make Default

- `PyMuPDF` as a default dependency, because the repo asked for open-source-only
  and no commercial licensing surprises.
- `pdf2image` as the main rendering engine, because it is a wrapper around
  external Poppler tooling rather than a core in-process PDF stack.
- `OCRmyPDF` as the main signature-field detector, because it solves a broader
  scanned-PDF preprocessing problem than this app needs right now.
- `pdf.js` as the current primary engine, because the app is already built
  around a native desktop Python stack and would need a different delivery model
  to benefit most from it.
- `pdfmake` as the first choice for simple client-side export, because it is
  more declarative than `pdf-lib` and is better reserved for structured reports.

## Verification Status

- Static exploration completed.
- Official docs and PyPI metadata reviewed.
- No runtime benchmark or end-to-end test was executed in this pass.

## Commercial / License Posture

This is the key filter for the repo’s long-term direction:

- the default stack should remain commercially usable
- the stack should not force our own product to become GPL/AGPL
- weak copyleft is acceptable when it preserves commercial use and does not
  impose source publication obligations on our own code

### Practical classification

| Package | Practical classification | Commercial use | Notes |
| --- | --- | --- | --- |
| `pypdfium2` | permissive | yes | Apache-2.0 or BSD-3-Clause, good default rendering choice |
| `pikepdf` | weak copyleft | yes | MPL-2.0, commercial use allowed; source-level changes to pikepdf itself must be published |
| `pypdf` | permissive | yes | BSD-3-Clause, pure-Python utility/editing path |
| `pdf.js` | permissive | yes | Apache-2.0, best browser rendering reference |
| `pdf-lib` | permissive | yes | MIT, browser-safe export/manipulation path |
| `pdfmake` | permissive | yes | MIT, declarative reports |
| `PDFKit` | permissive | yes | MIT, browser/Node generation |
| `pdfplumber` | permissive | yes | MIT, layout extraction |
| `pdf2image` | permissive | yes | MIT wrapper around Poppler tooling |
| `docTR` | permissive | yes | MIT, model-based OCR path |
| `Docling` | permissive | yes | MIT, document understanding path |
| `OCRmyPDF` | weak copyleft | yes | MPL-2.0, commercial use allowed; source-level changes to OCRmyPDF itself must be published |
| `EasyOCR` | permissive | yes | Apache-2.0, commercial OCR path |
| `PyMuPDF` | restrictive for this repo’s default posture | not default | AGPL/commercial dual license, so keep opt-in only unless the business explicitly accepts it |

### What this means for us

- The current and proposed default stack does not require us to open-source our
  own application.
- We can still sell the product commercially using the permissive / weak-copyleft
  stack above.
- If we modify `pikepdf` or `OCRmyPDF` themselves, those upstream changes should
  be treated as source-level contributions that may need to be published under
  MPL-2.0 terms.
- `PyMuPDF` stays outside the default commercial-safe stack because of the
  AGPL/commercial dual-license posture.

## Cross-References

- [PDF Stack Setup](../PDF_SETUP.md)
- [PDF Platform Convergence](PDF_PLATFORM_CONVERGENCE_2026-06-17.md)
- [Implementation Epics](IMPLEMENTATION_EPICS_2026-06-17.md)
