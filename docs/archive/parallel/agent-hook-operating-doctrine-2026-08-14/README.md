# Preserved alternate agent hook variant

Date: 2026-08-14

This directory preserves the exact dirty hook variant found in the shared
checkout while a SignKit commit was being attempted. The archived scripts are
historical evidence only and are not executable hook sources.

The variant changed the active hook authority from the project-local
`motto_v5.md` to workspace `OPERATING_DOCTRINE.md` in all three scripts. That
conflicted with SignKit's more-specific project contract in
`docs/context/agent-start/AGENT_KICKOFF_PROMPT.txt`, the live
`tests/test_agent_start_doctrine_contract.py` assertions, and the existing
`docs/review/agent_start_doctrine_contract_proof_2026-08-14.md` evidence.

The full original files are preserved beside this record with these SHA-256
digests:

- `pre-commit`: `2e869a177b2228e8e0e62b28b26b12ad068a43349b2e80c5ae4749df9a0aed89`
- `commit-msg`: `bb80686fb719d91c7df44462e0f328ab59c775c05272e79121168e2f691ac133`
- `prepare-commit-msg`: `b0cae2aad346f5e0af3a1d285dcfc9d3ed8c31fae653f19c7f5a936e46f883dc`

The active hooks retain the workspace doctrine as the broader instruction
layer, but use the selected project-local `motto_v5.md` for SignKit's commit
attestation. Revisit this boundary only if the project doctrine source rule is
changed through a durable decision and corresponding tests.
