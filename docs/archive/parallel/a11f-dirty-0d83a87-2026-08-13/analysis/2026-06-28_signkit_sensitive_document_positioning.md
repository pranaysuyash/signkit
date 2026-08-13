# SignKit Sensitive-Document Positioning and Truth Alignment

**Date:** 2026-06-28  
**Status:** Implemented in canonical marketing and onboarding surfaces

## Why This Pass Happened

An external GTM review correctly identified that SignKit's strongest wedge is not generic "signature extraction."

The stronger, code-grounded wedge is:

**a privacy-first local document workflow for people handling sensitive signed documents**

That matches the actual product surface already present in the repo:

- local signature extraction
- reusable signature storage
- built-in PDF signing
- local audit logging
- offline-first desktop operation

## Problems Found

### 1. Customer-facing truth drift

The public surfaces were not internally aligned.

- [purchase.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/purchase.html) said the product was macOS-only.
- [index.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/index.html) and [root.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/root.html) described multi-platform availability.
- [purchase.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/purchase.html) also carried unsupported social-proof numbers and timing claims.

That violated the motto_v3 customer-facing claims rule more than any missing feature did.

### 2. Wedge drift

Several surfaces still framed SignKit like a general signature tool or a broad PDF value proposition.

That undersold the real moat:

- local handling of sensitive documents
- one-app extraction to signing workflow
- repeatability for document-heavy professionals

### 3. Vertical signal was too weak

The app already fits legal, HR, finance, admin, and real-estate workflows, but the canonical surfaces were not consistently leading with those use cases.

### 4. External review mismatch

One external comment thread referenced a `main.py` cleanup item, but the current backend surface in this checkout already had the expected router/bootstrap shape and did not need a corresponding code change in this pass.

That is important for future review hygiene:

- code issues should be tied to the live file in this repo
- review feedback from another surface or snapshot should be translated, not blindly applied
- when no live defect exists, the right action is to record the mismatch and move on

## What Changed

### Public surfaces

Updated:

- [index.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/index.html)
- [root.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/root.html)
- [purchase.html](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/purchase.html)

Changes:

- repositioned the product around sensitive signed-document workflows
- replaced generic extraction-first hero copy with local-workflow messaging
- strengthened vertical relevance for legal, HR, finance, real-estate, and admin users
- removed unsupported social-proof metrics from the purchase page
- aligned platform wording to release-bundle truth instead of contradictory blanket claims

### Desktop onboarding

Updated:

- [desktop_app/views/onboarding_dialog.py](/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app/desktop_app/views/onboarding_dialog.py)

Changes:

- reframed first-run messaging around sensitive documents
- highlighted reusable signature storage and local PDF workflow
- updated quick-start guidance so it reflects real signed-document packets, not only generic image extraction

## Decision

For near-term GTM and product storytelling:

1. Lead with the vertical pain: sensitive signed documents that users do not want to upload.
2. Keep the horizontal story in support: extraction, library, PDF placement, audit visibility.
3. Avoid broad "PDF platform" positioning until more of the workflow stack is truly productized.
4. Avoid unsupported metrics or market claims unless they can be tied to current evidence.

## Highest-Value Next Product Opportunities

These remain the best implementation sequence after this messaging pass:

1. Signature and initials field detection on PDFs and scans.
2. Template reuse for repeat packets and recurring forms.
3. Local batch document workflows for document-heavy operators.
4. OCR cleanup for scanned packets that currently require manual rescue.

This sequence keeps the product on the strongest loop:

**extract signature -> find likely field -> place signature -> save PDF -> reuse on the next packet**
