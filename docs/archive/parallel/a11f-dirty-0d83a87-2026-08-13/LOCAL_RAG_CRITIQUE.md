# Local Document Understanding (RAG) — Critique and Positioning

## Summary
Local RAG is valuable but shifts the product from “signature extraction + PDF placement” toward “contract intelligence.” Done right—as an add‑on—it can deepen our vertical integration without bloating the core.

## Critiques
- Strategic drift: Expands scope beyond core promise; must be packaged to avoid confusing value prop.
- Trust & accuracy: Hallucinations and vague answers can undermine legal confidence; citations and disclaimers are mandatory.
- Footprint & performance: Even small models are large; CPU‑only latency can frustrate low‑spec users.
- Packaging complexity: Cross‑platform native deps (llama.cpp, FAISS) increase build/test surface and support burden.
- OCR dependency: Image‑only PDFs need OCR; skipping them initially may disappoint some users.

## Decisions (Current Direction)
- Scope: Support text‑based PDFs only in Phase‑0; show a clear notice for scanned/image‑only PDFs.
- Packaging: Ship as an optional add‑on; Pro includes it, Lifetime can purchase separately.
- Retrieval: Default to BM25 to keep zero‑download baseline; offer embeddings as an enhancement.
- UI: “Understand” sidebar with page citations and “not legal advice” disclaimer; non‑blocking, cancelable jobs.
- Kill switches: If install friction, latency, or accuracy degrade UX materially, roll back to a minimal TL;DR only or pause feature.

## Pricing & Copy Guidance
- Add‑on: “Document Understanding — Local” (one‑time) or included in Pro.
- Copy: “Private by default. Runs on your device. Text‑based PDFs only (for now).”
- Refund stance: honor standard 30‑day refund even for add‑on.

## Metrics to Watch
- Model download completion rate; first success to first query time.
- TL;DR usage vs Q&A usage; average latency; cancel rates.
- Support volume: install issues, performance complaints, accuracy disputes.

## Risks & Mitigations
- Accuracy concerns → require citations, keep answers scoped, prefer extract‑then‑summarize.
- Heavy downloads → show sizes up‑front, allow background/resume, keep BM25 path functional without models.
- Platform variance → publish tested CPU baselines; expose settings for max tokens/threads.

## When to Expand Scope
- Add OCR for scanned PDFs once text‑PDF experience is strong and we have clear UI for “OCR in progress” with costs disclosed.
- Consider larger models only after confirming engagement; accelerate on Metal/CUDA where available.

