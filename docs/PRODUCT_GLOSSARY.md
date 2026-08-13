# SignKit product glossary

Date: 2026-08-13
Status: Current working vocabulary; changes require product and evidence review

This glossary is the shared language for desktop, browser, public, support, and
legal surfaces. It distinguishes the current local product from planned hosted
coordination and prevents implementation terms from becoming customer promises.

| Term | Use this meaning | Do not imply |
| --- | --- | --- |
| Local processing by default | Core signature extraction, cleanup, local Vault work, PDF placement, and export execute on the user device by default | Absolute offline operation, zero network activity, or legal authenticity |
| Local companion service | The loopback service used by the desktop app for local API, workspace, or inspection coordination | Cloud processing or document upload to a remote service |
| Connected service | A provider or optional remote boundary used for checkout, updates, support, or a future explicitly enabled workflow | That document bytes are uploaded by default |
| Source | The user-selected image or document entering the workflow | A permanently retained server asset |
| Mark | The selected signature region or candidate the operator chooses | A verified identity or authentic signature |
| Clean | The local image cleanup operation applied to the selected mark | A guarantee that the result is legally valid or visually perfect |
| Review | The human decision point where the operator checks the candidate, placement, or output | Automatic approval |
| Saved | A local Vault or project record was written successfully | A remote backup or permanent retention guarantee |
| Placed | A signature image was positioned in a PDF document session | A cryptographic signature or notarization |
| Exported | The requested output file or archive was written and the receipt reports the result | That an external recipient accepted the document |
| Needs review | The system cannot safely finish without a human decision | A silent failure or an approved result |
| Retry | A repeat operation allowed by the workflow contract and idempotency rules | That every failed action is safe to repeat |
| Quarantine | A failed or ambiguous item is isolated from automatic progression for inspection | Deletion or loss of the source |
| Receipt | A structured record of an operation, result, source hash, state, and recovery information | Legal certification or provider fulfilment |
| Hosted extraction | The authenticated remote API boundary described by the backend contract | Production availability until target migration, deployment, smoke, and recovery are proven |
| Cloud workspace | The metadata-first coordination surface for current or planned topology | Browser-native document signing or hosted document-byte retention |
| Signing | Product shorthand for placing an extracted signature image on a PDF | Cryptographic signing, notarization, regulatory validity, or proof of identity |

## Copy gate

Customer-facing copy should use “local processing by default” unless the exact
stronger statement has an approved claim-registry row and matching evidence.
“Cloud” should describe a remote topology only. Use “local companion service”
for loopback desktop coordination.

Related state and recovery rules live in
`docs/STATE_CONTENT_MATRIX.md`. Customer-facing claim rules live in
`docs/launch_claims/registry.md`.
