# Customer-claim and reference audit

Date: 2026-08-12
Owner: Solo operator with agent support
Status: Repo audit complete; production closure remains open

## Findings

### Canonical repository surface

The current `index.html` uses the governed claim markers, qualified local
processing language, provider-neutral checkout language, one-time pricing, and
the documented refund/update boundaries. The strict public-surface audit passes
with 13 governed claim families.

### Retained HTML

Six retained HTML surfaces still contain direct checkout references, and
several contain high-risk or obsolete language such as absolute offline claims,
unqualified lifetime language, placeholder product IDs, unsupported social
proof, or old provider framing. These files are now non-public by route policy,
but their content remains a trust hazard if deployment redirects drift.

They are intentionally preserved for historical review. The release gate must
continue to require route redirects and must not treat these files as approved
copy.

### Historical documentation

The route/reference scan found 30 historical documents that mention retired
paths. The dated addendum in
`docs/landing/CANONICAL_SURFACE_ADDENDUM_2026-08-12.md` is the current truth;
historical files should not be silently rewritten because they preserve prior
decisions and failure modes.

### Policy truth and solo-operator review

The public root is qualified, but policy documents and older pricing material
still contain provider-primary, offline, or lifetime terminology that requires
an owner decision. The solo operator and agents should narrow public copy to
the evidence available and record the decision. External legal review is not a
default task; open it only when a specific customer, payment provider,
platform, or regulatory requirement makes it necessary.

## External evidence

The live site was inspected during this audit and still exposed the retired
root narrative and direct Gumroad checkout. The live route probe also found
legacy paths returning 200 or 308 instead of the repository's required 301
redirects. Cloudflare Pages showed the production project `signkit-landing`
with stale `landing-page` deployments approximately eight months old.

## Closure criteria

- Live root contains the current public-surface marker and governed copy.
- Every retired landing path returns 301 to `/` while preserving attribution
  query parameters.
- Deployed checkout JavaScript contains `checkout_intent`, `entry_path`, and
  bounded UTM attribution.
- Solo operator records a policy decision on provider and privacy wording;
  external review is optional unless specifically required.
- Analytics owner confirms source attribution can be joined to purchase events
  without personal data in event labels.
- Any outbound campaign, email, PDF, or affiliate link points to `/` or an
  approved provider destination, never to a retired landing route.
