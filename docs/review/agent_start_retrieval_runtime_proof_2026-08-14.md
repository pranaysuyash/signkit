# Agent-start retrieval runtime proof

Date: 2026-08-14
Checkout: `/Users/pranay/Projects/Data_Science/computer_vision/proj6/signature-extractor-app`
Branch: `main`
Evidence tier: Tier 3 local shared-tooling runtime, with generated-context provenance

## Result

The documented workspace-memory setup path now produces a real local Python
environment and a usable `memsearch` CLI. A real SignKit sync, index, semantic
search, full `agent-start` retrieval refresh, and bounded forced-retrieval
refresh completed successfully. The generated context records the local
provider, model, collection, source selection, and retrieval boundary.

This closes the local runtime portion of RECON-06. It does not prove provider
portability, hosted retrieval, shared-collection availability, retrieval
quality for every project, or production deployment.

## Commands and observed evidence

The documented setup command was run from `/Users/pranay/Projects/workspace_memory`:

```text
scripts/projects_memsearch.sh setup --local
Python 3.13.3
memsearch 0.4.17
```

The existing 4.1 GB `/Users/pranay/.memsearch/milvus.db` file was not deleted.
It was preserved as `/Users/pranay/.memsearch/milvus.db.legacy-20260814` before
the current Milvus Lite database was initialized.

The direct project index used the local provider and model:

```text
MEMSEARCH_PROVIDER=local
MEMSEARCH_MODEL=BAAI/bge-base-en-v1.5
MEMSEARCH_COLLECTION=signkit_recon06_local
scripts/projects_memsearch.sh index \
  --only-project Data_Science/computer_vision/proj6/signature-extractor-app
```

Observed result: `588` files synchronized and `16042` chunks indexed. Direct
semantic search returned current SignKit sources including
`docs/BRAND_NARRATIVE_CONTRACT.md`,
`docs/PRODUCT_OWNER_BACKLOG_AUDIT_2026-08-12.md`, and
`docs/RECONCILIATION_STATUS_2026-08-13.md`.

The full wrapper refresh was then run with the real local runtime:

```text
timeout 600 env MEMSEARCH_PROVIDER=local \
  MEMSEARCH_MODEL=BAAI/bge-base-en-v1.5 \
  AGENT_START_INSTALL_PRECOMMIT_HOOKS=0 \
  /Users/pranay/Projects/agent-start \
  --project Data_Science/computer_vision/proj6/signature-extractor-app \
  --quiet
```

Observed result: exit `0`; project collection
`projects_proj_data_science_computer_vision_proj6_signature_extractor_app`;
`16047` total indexed chunks; semantic search returned the reconciliation
status and other current SignKit sources.

A bounded forced-retrieval refresh also returned exit `0`:

```text
timeout 90 env MEMSEARCH_PROVIDER=local \
  MEMSEARCH_MODEL=BAAI/bge-base-en-v1.5 \
  AGENT_START_SKIP_INDEX_RETRIEVE=1 \
  AGENT_START_INSTALL_PRECOMMIT_HOOKS=0 \
  /Users/pranay/Projects/agent-start \
  --project Data_Science/computer_vision/proj6/signature-extractor-app \
  --skip-index --quiet
```

The generated context files record the local retrieval provenance:

- `docs/context/agent-start/SESSION_CONTEXT.md`
- `docs/context/agent-start/STEP1_ENV.sh`
- `.agent/SESSION_CONTEXT.md`
- `.agent/STEP1_ENV.sh`

The selected project `motto_v5.md` and `/Users/pranay/Downloads/motto_v5.md`
both retained SHA-256
`f1ade186d46bf2e20e9eebd56ceca3a733711671471198284828482659524840`.
The generated context truthfully reports that the shared collection is not
available yet where that collection was not populated.

## Boundaries and follow-up

The local model emits a nonfatal FutureWarning during embedding. That warning
was retained in generated output and is not treated as proof of clean provider
compatibility. The generated context was produced while a separate calibration
slice was dirty in the shared checkout. It must be regenerated after that
slice is reconciled before the generated snapshots are treated as the final
canonical source state. The active pre-commit hook stages the `.agent`
compatibility mirror when it exists; the lower-case `docs/context/agent-start`
snapshots remain separately reviewable and are not silently treated as source
authority.

Remaining gates are full all-project retrieval health, shared-collection
population, provider portability, hosted execution, and evidence that retrieval
results are sufficiently useful for every operator workflow.

## Commit-gate authority reconciliation

During the first commit attempt, another worker's dirty hook variant changed
all three `.githooks` scripts from the project-local `motto_v5.md` authority to
workspace `OPERATING_DOCTRINE.md`. The attempt failed before creating a commit
when that variant was being replaced concurrently. The exact three scripts are
preserved as historical files under
`docs/archive/parallel/agent-hook-operating-doctrine-2026-08-14/`, with their
SHA-256 digests in that directory's README.

The active hook sources were reconciled to the existing SignKit contract after
comparison with `docs/context/agent-start/AGENT_KICKOFF_PROMPT.txt`,
`tests/test_agent_start_doctrine_contract.py`, and
`docs/review/agent_start_doctrine_contract_proof_2026-08-14.md`. The broader
workspace Doctrine remains an instruction layer, but it does not replace the
more-specific project motto for SignKit commit attestation. `bash -n` passes
for all three active hooks. This is a local source and syntax proof; the full
commit and push gate remains to be rerun after this reconciliation.
