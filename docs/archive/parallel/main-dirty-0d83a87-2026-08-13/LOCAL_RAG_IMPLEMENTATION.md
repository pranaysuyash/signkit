# Fully Local RAG & Summaries — Design and Implementation Plan

## Goals
- Help users understand PDFs before signing: quick summaries, key terms, Q&A, and red‑flag detection.
- 100% local/on-device. No network calls, opt‑in model downloads, privacy‑by‑default.
- Integrate into the existing PDF workflow without degrading performance or app size excessively.
- Phase‑0 scope: TEXT‑BASED PDFs only (no OCR); skip image‑only/scanned PDFs for now.

## Primary Use Cases
- TL;DR: One-paragraph summary of a contract or long PDF.
- Key terms extraction: parties, dates, amounts, obligations, termination, renewal.
- Red flags: hidden fees, auto-renewal, unilateral changes, high penalties, arbitration clauses.
- Q&A: “What is the cancellation policy?” “Total fees per year?” “Who is responsible for X?”
- Explain selection: User highlights text; app explains in simpler language.

## Requirements
- Offline by default: model inference runs locally; no telemetry.
- Cross-platform: macOS, Windows, Linux (CPU baseline, optional GPU/Metal/CUDA when available).
- Reasonable footprint: keep default install <130–150 MB; allow optional model downloads post-install.
- Reproducible: deterministic chunking and indexing; stable results across runs.

## Packaging & SKU
- Offered as an optional add‑on (“Document Understanding — Local”).
- Lifetime users can purchase the add‑on; Pro includes it by default.
- Add‑on contains model download manager and RAG features; core app remains lightweight.

## Architecture Overview
- Extraction layer (PDF → text):
  - Prefer pypdfium2 text extraction per page when available.
  - Fallback: pdfminer.six for robust layout handling (MIT license).
- Chunking:
  - Split per page into overlapping chunks (e.g., ~1500 chars or ~512 tokens, 64 overlap) with page mapping.
- Retrieval (BM25‑first):
  - Default: BM25/Okapi with Whoosh or simple Lucene equivalent (fast, tiny footprint, zero model).
  - Optional: Embeddings + FAISS as “Enhanced Retrieval” after model download.
- Retriever:
  - KNN search (k=8–12) with Maximal Marginal Relevance (MMR) to improve diversity.
- Summarizer/Reasoner:
  - Small instruct LLM via llama.cpp (GGUF). Two-tier approach:
    - Default: 1–2B instruct for TL;DR + citations.
    - Optional high-quality 3B–7B as on-demand download.
- Orchestrator:
  - Local RAG pipeline wraps retrieval, prompt templating, and response post-processing.

## Model Selection (Licenses, Sizes, Quality)
- Embeddings:
  - nomic-embed-text v1.5 (Apache 2.0) — GGUF ~200–250 MB; quality suitable for contract Q&A.
  - Alternative (later): bge-small-en or all-MiniLM-L6-v2 (requires torch; larger footprint).
- LLM (Instruct):
  - Qwen2.5-1.5B/3B-Instruct (Apache 2.0): GGUF ~0.5–1.6 GB (Q4_K_M). Good multilingual support.
  - TinyLlama 1.1B (Apache 2.0): GGUF ~0.3–0.5 GB; fast but weaker reasoning.
  - Mistral 7B Instruct (Apache 2.0): GGUF ~3.8–4.5 GB; high quality; optional download.
- Recommendation:
  - Ship app without models and with BM25 retriever available immediately.
  - First run of add‑on offers “Enable Enhanced Understanding” → download small pack (~500–800 MB total: embed + 1.5B LLM).
  - Allow users to upgrade to better models via in-app download manager.

## Data Flow
// Text PDFs only — skip if PDF page yields no extractable text
- Indexing (per PDF):
  1) Extract text per page (pypdfium2 → pdfminer fallback). If page has no text, mark page as unsupported.
  2) Normalize (strip headers/footers heuristically, merge hyphenated words, preserve lists/tables as text).
  3) Chunk with overlap and attach page numbers.
  4) Embed chunks → store in FAISS index + metadata manifest `{chunk_id, page, offsets}`.
  5) Cache index under `~/.signature_extractor/rag/{hash_of_pdf}/`.
- Querying:
  1) Embed query.
  2) Retrieve top-k chunks with MMR.
  3) Compose a prompt with system instruction + selected contexts.
  4) Generate answer locally; include citations (page numbers) from chunk metadata.
- Summarization:
  - Map-reduce: chunk summaries → combine. For small docs (<20 pages), use single-pass with longer context.
- Red flags & key terms:
  - Rules-first pass (regex/keyword patterns) + LLM classification/extraction.
  - Extract structured JSON: `{parties, dates, amounts, renewal, termination, jurisdiction, notices, penalties, fees}`.

## UI Integration (PDF Tab)
- New right sidebar: “Understand” with tabs
  - Overview (TL;DR summary)
  - Q&A (ask a question, show answers with citations by page)
  - Key Terms (structured fields)
  - Risks/Red Flags (list with short rationales and links to pages)
- Selection action: context menu “Explain selection” → short paraphrase.
- Status indicators: model availability (downloaded vs not), indexing progress, offline badge.
- Unsupported notice: If a PDF is image‑only (no text), show “This document appears to be a scan. Document Understanding supports text‑based PDFs only for now.”

## Performance Targets (CPU Baseline)
- Indexing: 100–150 pages in <60s on modern CPU (text extraction + embeddings).
- Query latency: <2s for embedding + retrieval; <6–10s for 1.5B LLM answer.
- Summarization: <90s for 50 pages using map-reduce; cancelable.
- Memory: keep working set <3 GB for 1.5B; <6 GB for 3B.

## Storage & Caching
- Per-PDF cache folder keyed by SHA256 of bytes.
- Artifacts: `manifest.json`, `faiss.index`, `chunks.jsonl` (for debugging), optional `summary.md` cache.
- Auto-prune LRU caches beyond configurable disk cap (e.g., 2–5 GB).

## Bundling & Distribution
- Dependencies:
  - `llama-cpp-python` for LLM + embeddings (single runtime; no torch required).
  - `faiss-cpu` for vector index (wheel available for major platforms).
  - `pdfminer.six` as fallback text extractor.
- Model downloads:
  - Serve via HTTPS from your CDN; signed SHA256 manifest for integrity.
  - In-app download manager with resume + checksum verification.
- App size:
  - Baseline app unchanged; BM25 works without model downloads. Enhanced retrieval/LLM models are optional downloads.

## Privacy & Security
- No network usage unless user explicitly downloads models.
- Local-only inference; no cloud calls.
- Clear “Private by default” copy and local paths in settings.
- Signed manifests for model files; verify checksums before activation.

## Licensing Notes
- Use Apache/MIT models to avoid copyleft obligations.
- Provide third-party notices for llama.cpp, FAISS, pdfminer.six.
- Avoid AGPL libraries (e.g., PyMuPDF) in this feature path.

## Telemetry (Optional, Opt-In)
- Minimal: index started/completed, query latency, errors. All local by default; only if user opts in, send anonymized counters.

## API Sketch (Internal)
- Indexer:
  - `build_index(pdf_path) -> IndexHandle`
  - `load_index(doc_hash) -> IndexHandle`
- RAG:
  - `answer_query(index, question, top_k=8) -> {answer, citations}`
- Summarization:
  - `summarize(index) -> markdown`
- Red flags/Key terms:
  - `extract_terms(index) -> dict`
  - `detect_red_flags(index) -> list[dict]`

## Roadmap
- Phase 1 (MVP, 1–2 weeks)
  - Text extraction, chunking, BM25 index (no model download).
  - TL;DR summary using 1–2B model (optional download); basic Q&A if model installed.
  - UI: Understand panel with Summary + Q&A; model download manager.
- Phase 2 (2–3 weeks)
  - Key terms structured extraction; citations; explain selection.
  - Red flags: hybrid rules + LLM judge; configurable sensitivity.
  - Caching + LRU pruning; cancelable jobs; progress UI.
- Phase 3 (post-MVP)
  - Better models (3B/7B) with optional GPU/Metal acceleration.
  - Multi-document compare; revision diffs; glossary generation.
  - Multilingual and OCR pipeline for image‑based PDFs (Tesseract or PaddleOCR locally).

## Risks & Mitigations
- Model size and performance: default to 1–2B; make larger models optional.
- Inference accuracy on legalese: craft domain prompts and few-shot examples; allow user feedback.
- Packaging complexity: keep heavy deps minimal (llama.cpp + faiss; avoid torch initially).
- PDF text quality: use pdfminer fallback; add OCR-only path later for scans.

## Open Questions
- Which models to host by default (licensing, quality, size)?
- Do we ship any model with the app, or require first-run download?
- Minimum CPU/memory target for acceptable UX?
