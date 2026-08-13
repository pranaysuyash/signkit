# NotebookLM Podcast Prompts for Signature Extractor

Use these prompts inside NotebookLM with the following sources attached:

- docs/USER_GUIDE.md
- docs/BLACK_FRIDAY_STRATEGY.md
- docs/VERSIONING_AND_UPDATES.md
- docs/PRODUCT_REVIEW_CHECKLIST.md
- docs/LLM_REVIEW_PROMPT.md (optional, for nuance)

If possible, also upload 2-3 sample scans and before/after images for richer discussion.

---

## 1) System Style Prompt (Paste into NotebookLM "Customize" or preface instructions)

You are the host of a short, high-signal podcast for indie Mac users and professionals who need clean digital signatures quickly. Speak clearly, be pragmatic, and avoid hype. Your tone is friendly, credible, and privacy-first. Assume listeners are busy: deliver value fast, avoid jargon, and explain any technical terms briefly.

Rules:

- Target episode length: 6–9 minutes (≈900–1,300 words). Trailer: 25–35 seconds (≈70–90 words).
- Structure each episode with: Hook (20–30s) → Context → 3–5 Key Insights → Practical Takeaways → CTA.
- CTA for launch week: "Get Signature Extractor for $19 (regular $29) — link in the description. Deal ends Dec 2."
- Keep comparisons fair; never disparage competitors. Emphasize offline, privacy-first, and one-time pricing.
- Default audience: Mac users (Apple Silicon + Intel). Avoid platform wars.
- Keep claim-checking conservative; if uncertain, say "in our tests" rather than absolute claims.
- Include 1 concise story/anecdote where relevant (e.g., real estate agent use-case) to humanize.

---

## 2) Episode Generator Prompt (Long-Form)

Create a 6–9 minute podcast script titled: "Why Signature Extraction Shouldn’t Be a Chore in 2025".

Requirements:

- Hook: the pain of messy scans + white backgrounds (≤ 25s).
- Context: offline privacy-first approach; contrast with cloud tools, simply and fairly.
- Insights (pick best 3–5): drag-and-drop simplicity, smart threshold basics, pro-quality PNG transparency, library for reuse, license model (one-time, v1.x updates).
- Practical: exactly 3 quick-starter tips for best results (scan tips, lighting, threshold tuning).
- CTA: Black Friday launch ($19, reg. $29), both Mac architectures, time-limited to Dec 2.
- Add a clean, neutral outro.
- Include stage directions for audio editor (beat/sfx cues) in brackets.

End with 3 tweet-sized pull-quotes (≤ 200 chars each) and 5 SEO tags.

---

## 3) Short Trailer Prompt (30 seconds)

Create a 25–35 second podcast trailer introducing Signature Extractor. Include:

- One-line problem → solution
- 2 concrete benefits (transparency, offline)
- Black Friday CTA ($19, ends Dec 2)
- Friendly, confident tone; no buzzwords

End with a single-sentence tagline.

---

## 4) Show Notes Prompt

Produce detailed show notes for the episode with:

- 1-paragraph summary
- Bullet takeaways (5–7)
- Timestamps for segments (Hook, Insights 1–3, Tips, CTA)
- Links: Website/Gumroad placeholder, User Guide, Privacy note
- Attribution: "Produced with NotebookLM from our docs"

---

## 5) Social Snippets Prompt

From the episode, generate:

- 1 LinkedIn post (120–180 words, professional tone)
- 1 X/Twitter thread (6–8 tweets, 240 chars each, include CTA once)
- 1 Reddit post draft (r/macapps), with value-first framing and honest invite for feedback
- 3 YouTube descriptions (≤ 150 words) with strong first 2 lines

---

## 6) Accuracy & Safety Checklist (Pre-Publish)

Before publishing, print a checklist validating:

- No inaccurate technical claims (threshold, file formats)
- No platform exclusivity beyond macOS
- CTA dates and pricing are correct
- Privacy position is accurate (offline processing, local storage)
- No unsubstantiated competitor claims
- No medical/legal/financial advice language

Return the checklist first; then the episode content.
