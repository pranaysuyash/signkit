# Document Understanding — Local (Add-On)

## Offer
- Name: Document Understanding — Local
- Packaging: Optional add-on for Lifetime; included in Pro
- Scope (Phase-0): Text-based PDFs only (no OCR), TL;DR, Q&A with citations, key terms (basic)
- Refund: 30-day money-back (same as core)

## Why Add-On
- Preserves core app’s simplicity and size
- Lets motivated users opt-in to model downloads and the heavier feature set
- Clear value communication separate from signature extraction

## UX Surfaces
- PDF right sidebar: “Understand” (Summary, Q&A)
- First-run: “Enable Enhanced Understanding” with model size, path, privacy note
- Status: model availability, indexing progress, cancel buttons
- Citations by page; “Not legal advice” note
- Unsupported docs: “This appears to be a scan — text OCR not yet supported.”

## Technical Components
- Retrieval: BM25 by default; optional embeddings + FAISS as enhancement
- LLM: 1–2B local instruct model; optional larger models as upgrades
- Storage: `~/.signature_extractor/rag/{doc_hash}` for index, cache, and summaries
- Integrity: signed manifest + SHA256 checks for model files

## In-App Purchase Flow
- Upgrade dialog surfaced from Sidebar/Export/Status when feature accessed without add-on
- Hosted checkout (provider TBD); on success, license payload toggles `feature_flags.document_understanding_local = true`
- App observes flag and unlocks immediately (no restart)

## Pricing (Draft)
- Add-on one-time: e.g., $19–$29
- Included in Pro Workspace
- Launch coupon may apply (LAUNCH20)

## Support Boundaries
- Best-effort performance targets listed in docs; CPU baselines noted
- Not legal advice; accuracy depends on document quality and model size
- Clear instructions for uninstalling/removing models to reclaim disk space

## Roadmap Hooks
- OCR for scanned PDFs (later)
- Red flags, structured key terms (phase 2)
- Larger models + acceleration (phase 3)

