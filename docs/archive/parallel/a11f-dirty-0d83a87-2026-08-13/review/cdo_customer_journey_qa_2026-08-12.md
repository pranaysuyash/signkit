# CDO customer-journey QA

Date: 2026-08-12
Surface: local canonical root at `http://127.0.0.1:8099/`
Owner: Solo operator with agent support

## Journey checked

Promise -> capability -> proof -> checkout intent -> support/refund
expectation -> policy links.

## Observed behavior

- The root page presents the qualified local-first promise, named workflow,
  pricing boundary, provider state, platform qualification, refund path, and
  support email in one continuous journey.
- Gumroad fallback checkout is actionable and records `checkout_intent` with
  provider, placement, entry path, and bounded UTM fields. The click was
  intercepted before navigation during QA.
- Dodo links are visibly unavailable when its product ID is empty, focusable,
  and route attention to the configuration note.
- All loaded image assets returned 200. No browser console messages were
  observed during the local load.
- The post-fix Lighthouse audit scored 100 for accessibility, 100 for SEO, and
  100 for agentic browsing on both mobile and desktop. Best Practices scored 77
  because of third-party analytics cookies and DevTools inspector issues, not
  product interaction failures.
- The canonical page had no horizontal overflow at the tested narrow viewport;
  the primary CTA is below the first mobile viewport but remains reachable in
  the normal scroll path.
- Legal policy links load as Markdown documents with `text/markdown`. They are
  reachable but are not a polished browser-document experience.

## Fixes made from this pass

- Added a main landmark.
- Added accessible names to the social icon links.
- Kept unavailable checkout anchors focusable with an explicit configuration
  fragment and button role while preserving the existing fallback behavior.
- Added static regression coverage for the accessibility primitives.
- Active-link review found no retired-route destinations in the canonical
  customer surface. Remaining references are limited to backups, historical
  landing assets, and test/deployment helpers.

## Remaining product/CX work

- Decide whether policy documents should have a browser-friendly presentation;
  this is a non-blocking usability improvement, not a certification task.
