---
title: Product Museum experience architecture for SignKit
date: 2026-07-31
status: accepted for parallel concept exploration, not approved for production replacement
owners:
  - product
  - design
related:
  - ../review/signkit_experience_system_direction_2026-07-31.md
  - ../review/landing_inspiration_research_2026-07-31.md
  - ../wayfinder/SIGNKIT_SCALING_EXPANSION_WAYFINDER_MAP.md
  - ../../web/concepts/2026-07-31-workbench-experience/
---

# Product Museum experience architecture

## Decision

SignKit's long-term landing experience should be organised as a **Product
Museum**, not a conventional stack of marketing sections, screenshots, and
feature cards.

The page's information architecture must make a visitor understand, before
they consciously read the supporting copy:

1. what SignKit helps them finish,
2. what operating it feels like,
3. how the work moves from source material to a ready PDF, and
4. why that way of working feels more capable than fighting documents in
   disconnected tools.

The launch message remains job-led. The emotional promise is **the relief of
finishing paperwork without a fight**. Local execution is valuable proof of
trust and control, but it is not the hero's emotional or informational centre.

## Decision input

This decision incorporates the user-provided ChatGPT discussion
`Linear vs Raycast Design` (`6a6c9c53-cee8-83ee-9d3f-44c44e693b60`), recorded
here as design reasoning rather than treated as a source of product facts.

The central insight is information architecture, not borrowed visual style:

- Linear lets product state do most of the persuasion. Copy identifies what
  the visitor is already seeing.
- Raycast sells an operating feeling. The interface's speed and responsiveness
  communicate the benefit before a feature explanation does.
- SignKit therefore needs to sell the feeling of getting a consequential
  document over the line, not merely the fact that files stay local.

## Why the previous framing was insufficient

The earlier workbench direction improved visual craft but still treated the
main illustration as a product screenshot with explanatory tabs. That is a
useful art-direction study, but it is not yet a living product demonstration.

Static screenshots, decorative fades, and a three-item feature list make a
visitor watch marketing. The intended experience makes the visitor operate a
small, understandable slice of the product. A selection visibly becomes a
clean mark, then becomes a placed mark, then makes export feel inevitable.

The workbench concept in `web/concepts/2026-07-31-workbench-experience/` is
therefore preserved as a visual-direction artefact. It does **not** close the
Product Museum decision by itself.

## Experience architecture

The eventual visitor path is a sequence of product chapters, not a list of
feature buckets:

| Chapter | Visitor question | Experience character | Evidence status |
| --- | --- | --- | --- |
| Entrance | What does this help me finish? | Direct, warm, personal document arrival | Current product story only |
| Capture | Can I get the useful mark out of this file? | Paper, ink, selection, considered motion | Demonstrate current capability when used publicly |
| Workbench | Can I make a precise decision rather than hope? | Dense desktop tooling, split views, visible controls | Current and illustrative direction must be distinctly labelled |
| Vault | Can I keep and reuse what I have prepared? | Calm, archival, owned, searchable | Only show shipped vault behaviour as current |
| PDF editing | Can I place it properly in the final document? | Technical, zoomed, aligned, deliberate | Demonstrate current capability when used publicly |
| Automation | Can repeated work move without becoming opaque? | Queues, folders, recovery, progress, visible state | Only shipped work is public proof; emerging work remains an exploration |
| Future lab | Where could the workspace grow? | Experimental, spatial, assisted, intentionally separate | Research, never a purchase promise |

These chapters may change palette, density, motion, and interaction grammar.
They share SignKit's typography roles, spacing rhythm, accessibility behaviour,
and plain-language copy. The brand is coherent because the underlying job and
interaction standards are coherent, not because every capability is forced
into a single neomorphic, glass, or workbench treatment.

## The one interaction that matters

The public landing needs one memorable, product-specific interaction. It must
be brief enough to understand in about ten seconds and legible without an
explanation:

```text
source document → select mark → refine result → place in PDF → ready to export
```

The interaction must be a semantic, keyboard-operable DOM experience, not a
video, a decorative animation, or a static mockup with changing captions.
The selected region, cleanup result, PDF position, and ready state should all
visibly change. Copy labels the consequences of the interaction instead of
substituting for it.

## Product truth and illustrative direction

There are two valid visual evidence roles. They must never be conflated.

| Role | Permitted material | Required labelling |
| --- | --- | --- |
| Current-product proof | Current runtime captures or live, safe demo components driven by current behaviour | No special label needed if it is demonstrably current; do not omit limitation or scope facts |
| Future-interface direction | Generated art, prototypes, aspirational components, and interaction studies | `Illustrative`, `Concept`, or equivalent visible label. Never call it a current screen or use it to imply a shipped capability |

The existing generated asset at
`web/concepts/2026-07-31-workbench-experience/assets/signkit-future-workspace-concept.png`
is in the second role. It communicates finish and composition, not runtime
truth. It must be replaced by the living UI when a production-facing page is
built.

## Options considered

1. **Traditional SaaS landing page**: headline, mockup, cards, testimonials,
   feature grid. Rejected because SignKit's sequence of work is the
   differentiation and this pattern makes it generic.
2. **Literal current-screenshot tour**: safest from an evidence perspective,
   but insufficient as a future design target. Retained as product proof,
   not as the entire experience.
3. **One uniform visual language for every capability**: rejected because
   capture, vault, placement, automation, and research have different mental
   models and need different density and interaction grammars.
4. **Product Museum**: selected. It preserves a single job-led story while
   giving every genuine capability its own appropriate experience chapter.

## Guardrails

- Do not lead with "local", privacy, topology, or an internal validation
  wedge. Use those as substantiating proof after the job is understood.
- Do not turn Legal, HR, or any other internal vertical into an exclusionary
  public persona label.
- Do not use generated UI as a hidden claim about current functionality.
- Do not show Cloud, Hybrid, certificate signing, AI autonomy, or automation
  as currently available until their delivery and claim gates are closed.
- Do not add sound by default. Any future sound or haptic cue must be optional,
  muted by default, and subordinate to accessibility preferences.
- No generic hover-fade theatre. Motion must reveal state, causality, or an
  available next action.

## Implementation contract for the next concept

The next Product Museum prototype must include:

1. an entrance that explains the job in one glance;
2. a DOM-based source-to-PDF interaction with visible causal state changes;
3. at least two chapter-specific visual grammars beyond the entrance;
4. a clearly separated illustrative or research chapter, if future capability
   is shown at all;
5. reduced-motion, keyboard, focus, and responsive behaviours; and
6. Browser visual verification at desktop and touch-mobile widths.

It must preserve the existing parallel concepts. No production landing
replacement follows from this decision without user approval.

## Evidence, confidence, and revisit trigger

- Design-reasoning evidence: Tier 1 from the supplied design discussion and
  existing product documentation.
- Visual-reference evidence: Tier 4 from prior Browser inspection of Linear,
  Raycast, and the parallel SignKit concepts.
- Current product capability claims: governed separately by runtime evidence
  and the launch-claim registry, not by this decision record.

Revisit this decision when a production public landing is approved, when the
interactive demo's performance or accessibility budget is established, or when
new shipped capability changes the chapter map.

## Anything else?

Yes. The Product Museum is a public experience architecture, not permission to
broaden SignKit's product claims. The strategy and topology material remains
useful for product planning, but it does not belong as internal language on a
customer-facing landing page.

## Update log

- 2026-07-31: created after the `Linear vs Raycast Design` discussion exposed
  that previous documentation captured visual references but missed the
  information-architecture and living-UI implications.
- 2026-07-31: the requested wide-open multi-persona review was recorded in
  `Docs/exploration/2026-07-31_product_museum_wide_open_brainstorm.md`.
  Its red-team conclusion narrowed the approved parallel experiment to a
  compact, explicitly simulated proof interaction. The resulting DOM concept
  is at `web/concepts/2026-07-31-product-museum-living-ui/`; the illustrated
  workbench remains preserved at `web/concepts/2026-07-31-workbench-experience/`.
