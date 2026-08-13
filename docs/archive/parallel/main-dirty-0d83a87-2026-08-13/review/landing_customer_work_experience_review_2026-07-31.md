# Customer-facing SignKit concept review

Date: 2026-07-31  
Status: current parallel landing recommendation for founder review

## Redirect from the topology concept

Browser review correctly identified two category mistakes in the prior
topology-led concept:

1. It devoted too much physical space to abstract statements.
2. It exposed internal strategy language, including delivery topology, proof
   gates, and Legal/HR validation focus, to prospective customers.

Those facts remain important, but they belong in Wayfinder, strategy, product,
and sales decision artifacts. They are not front-door marketing copy. The
customer-facing site should make a visitor feel included in a clear, valuable
document job, not invited to evaluate SignKit's internal operating plan.

## New artifact

`web/concepts/2026-07-31-customer-work-experience/`

The prior concepts are retained unchanged:

- `web/concepts/2026-07-31-b2c-redesign/` is the rejected theatrical direction.
- `web/concepts/2026-07-31-workspace-experience/` is the first job-led pass.
- `web/concepts/2026-07-31-topology-experience/` is a useful strategy-expression
  experiment, not a customer-facing landing direction.

## Customer-facing rules used here

- Lead with the universal job: get the document right.
- Keep the page compact and evidence-dense. No full-viewport manifesto blocks.
- Show current product frames whole, with a caption explaining exactly what is
  real. Never use arbitrary UI crop decoration or reconstructed application UI.
- Give people broad, self-identifying contexts: contracts and approvals, people
  documents, records and forms, and personal paperwork. Do not advertise only
  the internal Legal/HR validation wedge.
- Explain local-first value in customer terms: keep sensitive work close, stay
  in control, and keep moving.
- Preserve Cloud, Hybrid, vertical validation, and horizontal-expansion detail
  in the product strategy record until it has customer-ready evidence and an
  approved public claim.

## Browser evidence

Opened and visually inspected:

`http://127.0.0.1:4176/web/concepts/2026-07-31-customer-work-experience/index.html`

- Tier 4: compact customer hero rendered with the current full desktop frame.
- Tier 4: the three-stage workflow switcher changed from current selection to
  current completed PDF workspace, including accessible selected state, image
  alt text, and caption.
- Browser console: clear after interaction.
- Static check: `node --check web/concepts/2026-07-31-customer-work-experience/app.js` passed.

## Webwright visual-evidence addendum

The browser review is preserved as a reusable Webwright run at:

`Docs/review/webwright/customer-work-experience/`

`plan.md` records the customer-facing language, compact visual hierarchy,
current-product proof, workflow interaction, and console checks. Clean
evidence is in `final_runs/run_4/`:

- `screenshots/final_execution_1_open_customer_hero.png`
- `screenshots/final_execution_2_pdf_workflow_selected.png`
- `final_script_log.txt`

Both screenshots were visually inspected after the run. That inspection found
an avoidable empty grid area above the workflow demo in the initial pass; the
workflow header grid was corrected before `run_4` was created. `run_4` then
verified the compact corrected stage, selected PDF state, and a clear console.

The project virtual environment invokes the evidence runner, while the
Webwright-required Firefox engine comes from the bundled browser-automation
runtime because Playwright is not installed in the project venv. Firefox was
installed once through the Webwright prerequisite command and is now available
for repeat evidence runs.

## Still required before any live replacement

- Founder approval of the information hierarchy and language.
- A deliberately prepared, authorized demo asset before public launch. The
  current fresh runtime frames prove current UI, but one includes a sample
  signature and should not be the permanent public marketing asset.
- A separate conversion decision for download, trial, or purchase CTA. This
  concept intentionally does not invent a commercial flow.

## Anything else?

Yes. The strategy-facing topology concept should remain a reference for the
internal experience system. Its content should surface publicly only when there
is a concrete customer benefit, a shipped capability, and evidence to support
the associated claim.
