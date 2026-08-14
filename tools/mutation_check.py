#!/usr/bin/env python3
"""Run the repository's small, curated S3 test-sensitivity manifest.

Each mutant is a type-valid edit to a real source expression that breaks one
named invariant. The declared tests must fail against the mutant. A parse or
collection error is reported as BROKEN, not counted as a kill.
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKUP_SUFFIX = ".mutation-backup"


@dataclass(frozen=True)
class Mutant:
    id: str
    file: str
    find: str
    replace: str
    tests: tuple[str, ...]
    reason: str


MUTANTS = (
    Mutant(
        id="extractor-bounded-candidates",
        file="desktop_app/processing/extractor.py",
        find="        ][:max_candidates]",
        replace="        ][:1]",
        tests=("tests/test_color_signature_candidate.py",),
        reason="The public detector must honor max_candidates for two ranked signatures.",
    ),
    Mutant(
        id="workspace-replay-key-matching",
        file="backend/app/services/workspace.py",
        find="WorkspaceExecutionEvent.idem_key == idem_key",
        replace="WorkspaceExecutionEvent.idem_key != idem_key",
        tests=("backend/tests/test_workspace_service.py",),
        reason="A repeated transition with the same idempotency key must not append an event.",
    ),
    Mutant(
        id="extractor-grayscale-fallback",
        file="desktop_app/processing/extractor.py",
        find="        if fallback is None or fallback_confidence < min_confidence:",
        replace="        if fallback is None:",
        tests=("tests/test_color_signature_candidate.py",),
        reason="The grayscale fallback must obey the same min_confidence threshold as color candidates.",
    ),
    Mutant(
        id="workspace-owner-filter",
        file="backend/app/routers/workspace.py",
        find=(
            "            WorkspaceExecution.id == execution_id,\n"
            "            WorkspaceExecution.owner_user_id == current_user.id,\n"
        ),
        replace=(
            "            WorkspaceExecution.id == execution_id,\n"
            "            # owner filter removed by mutation\n"
        ),
        tests=("backend/tests/test_workspace_router.py",),
        reason="A workspace execution must be invisible to a user who does not own it.",
    ),
    Mutant(
        id="passport-metadata-boundary-validation",
        file="contracts/execution_passport.py",
        find="        if self.data_boundary != DATA_BOUNDARY_METADATA_ONLY:",
        replace="        if False:",
        tests=("tests/test_execution_passport_contract.py",),
        reason="The cross-surface passport must reject any boundary that could carry document bytes.",
    ),
    Mutant(
        id="runtime-hosted-route-exclusion",
        file="backend/app/main.py",
        find="if is_local_companion():",
        replace="if True:",
        tests=("backend/tests/test_runtime_profile.py",),
        reason="A hosted runtime must not register the local document-inspection route.",
    ),
    Mutant(
        id="inspection-candidate-confidence-bound",
        file="backend/app/schemas/workspace.py",
        find="confidence: float = Field(..., ge=0, le=1)",
        replace="confidence: float = Field(..., ge=0, le=2)",
        tests=("backend/tests/test_workspace_router.py",),
        reason="Worker confidence values outside 0..1 must be rejected at the API boundary.",
    ),
    Mutant(
        id="local-source-to-ready-retry",
        file="tools/run_local_source_to_ready_proof.py",
        find="            if attempt_count == 1:\n",
        replace="            if False:  # mutation removes the forced transient failure\n",
        tests=("tests/test_local_source_to_ready_proof_tool.py",),
        reason="The local source-to-ready proof must exercise and prove the canonical retry recovery path.",
    ),
    Mutant(
        id="extraction-smoke-health-gate",
        file="tools/run_extraction_hosted_smoke.py",
        find='            _assert_status(health, 200, "health")\n',
        replace='            _assert_status(health, 500, "health")\n',
        tests=("tests/test_extraction_hosted_smoke_tool.py",),
        reason="The local extraction smoke must fail when the health endpoint is not healthy.",
    ),
    Mutant(
        id="migration-recovery-rollback-target",
        file="tools/run_local_migration_recovery_proof.py",
        find='        command.downgrade(alembic_config, ROLLBACK_TARGET)\n',
        replace='        command.downgrade(alembic_config, "head")\n',
        tests=("tests/test_local_migration_recovery_proof_tool.py",),
        reason="The local migration proof must actually exercise the intended rollback revision.",
    ),
    Mutant(
        id="local-retry-attempt-accounting",
        file="desktop_app/workflows/engine.py",
        find=(
            "            models.WorkflowState.RETRY,\n"
            "            models.WorkflowState.FAILED,\n"
        ),
        replace="            models.WorkflowState.FAILED,\n",
        tests=("tests/test_local_source_to_ready_proof_tool.py",),
        reason="A retryable source-to-ready failure must consume one attempt in the durable job and passport.",
    ),
    Mutant(
        id="local-bridge-owner-binding",
        file="desktop_app/workflows/authorization.py",
        find="    if grant.approver_subject == subject:\n        return True",
        replace="    if grant.approver_subject != subject:\n        return True",
        tests=("backend/tests/test_local_workflow_bridge.py",),
        reason="The local browser bridge must expose only jobs explicitly bound to the authenticated user.",
    ),
    Mutant(
        id="local-bridge-passport-projection",
        file="backend/app/routers/workspace.py",
        find='            "passport": passport.to_payload(),',
        replace='            "passport": {"data_boundary": "metadata_only_no_document_bytes"},',
        tests=("backend/tests/test_local_workflow_bridge.py",),
        reason="The bridge must return the complete canonical metadata passport, not a weakened or ad hoc shape.",
    ),
    Mutant(
        id="local-retry-idempotency-replay",
        file="backend/app/routers/workspace.py",
        find="        replay = store.get_retry_receipt(job.job_id, retry_key)",
        replace="        replay = None  # mutation removes durable retry replay",
        tests=("backend/tests/test_local_workflow_bridge.py",),
        reason="Repeated or concurrent local retry requests must return the durable first result without a second engine execution.",
    ),
    Mutant(
        id="local-inprocess-backend-environment",
        file="desktop_app/backend_manager.py",
        find="            if value:\n                os.environ[key] = value",
        replace="            if False:  # mutation removes the in-process environment contract\n                os.environ[key] = value",
        tests=("desktop_app/tests/test_backend_manager.py",),
        reason="Frozen local startup must apply the generated database and JWT settings before backend import.",
    ),
    Mutant(
        id="release-ledger-source-identity",
        file="tools/release_artifact_ledger.py",
        find="    if not SOURCE_SHA_PATTERN.fullmatch(source_sha.strip()):\n",
        replace="    if False:  # mutation accepts an invalid source identifier\n",
        tests=("tests/test_release_artifact_ledger.py",),
        reason="A release ledger must reject a source value that is not a Git commit identifier.",
    ),
    Mutant(
        id="release-ledger-duplicate-name-identity",
        file="tools/release_artifact_ledger.py",
        find="            if name in seen_names:\n",
        replace="            if False:  # mutation permits duplicate artifact names\n",
        tests=("tests/test_release_artifact_ledger.py",),
        reason="A ready release ledger must not contain two artifact records with the same name.",
    ),
    Mutant(
        id="release-ledger-duplicate-path-identity",
        file="tools/release_artifact_ledger.py",
        find="            if path in seen_paths:\n",
        replace="            if False:  # mutation permits duplicate artifact paths\n",
        tests=("tests/test_release_artifact_ledger.py",),
        reason="A ready release ledger must not contain two artifact records with the same path.",
    ),
)


def _restore_orphaned_backups() -> None:
    for mutant in MUTANTS:
        source = ROOT / mutant.file
        backup = Path(f"{source}{BACKUP_SUFFIX}")
        if backup.exists():
            source.write_bytes(backup.read_bytes())
            backup.unlink()
            print(f"Recovered {source.relative_to(ROOT)} from an interrupted run.")


def _install_signal_handlers() -> None:
    def recover_and_exit(signum: int, _frame: object) -> None:
        _restore_orphaned_backups()
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGINT, recover_and_exit)
    signal.signal(signal.SIGTERM, recover_and_exit)


def _run_tests(tests: tuple[str, ...]) -> tuple[str, str]:
    test_env = os.environ.copy()
    # Backend mutants import the application settings at collection time. Keep
    # the sensitivity gate self-contained instead of requiring an ambient
    # developer .env or a running database.
    test_env.setdefault("JWT_SECRET", "s3-sensitivity-gate-secret-that-is-at-least-32-bytes")
    test_env.setdefault("DATABASE_URL", "sqlite:///:memory:")
    process = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *tests],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=test_env,
    )
    output = f"{process.stdout}\n{process.stderr}".strip()
    if process.returncode == 0:
        return "SURVIVED", "the declared tests passed against broken code"
    if re.search(r"(?m)^FAILED ", output):
        return "killed", ""
    tail = "\n".join(output.splitlines()[-12:])
    return "BROKEN", f"the run failed without a test failure; mutant may be invalid\n{tail}"


def _apply_and_run(mutant: Mutant) -> tuple[str, str]:
    source = ROOT / mutant.file
    original = source.read_bytes()
    needle = mutant.find.encode()
    replacement = mutant.replace.encode()
    occurrences = original.count(needle)
    if occurrences == 0:
        return "NOT FOUND", "the manifest find string is no longer present"
    if occurrences > 1:
        return "AMBIGUOUS", f"the find string occurs {occurrences} times"

    backup = Path(f"{source}{BACKUP_SUFFIX}")
    backup.write_bytes(original)
    try:
        source.write_bytes(original.replace(needle, replacement, 1))
        return _run_tests(mutant.tests)
    finally:
        source.write_bytes(original)
        if backup.exists():
            backup.unlink()
        if source.read_bytes() != original:
            raise RuntimeError(f"FATAL: failed to restore {source}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list mutants without running them")
    parser.add_argument("--only", help="run one mutant by id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _restore_orphaned_backups()
    _install_signal_handlers()

    if args.list:
        for mutant in MUTANTS:
            print(f"{mutant.id}\n  {mutant.file}\n  {mutant.reason}\n")
        return 0

    selected = tuple(mutant for mutant in MUTANTS if not args.only or mutant.id == args.only)
    if not selected:
        print(f'No mutant with id "{args.only}". Use --list to see the manifest.', file=sys.stderr)
        return 2

    results: list[tuple[Mutant, str, str]] = []
    print(f"Test-sensitivity gate: {len(selected)} mutant(s)")
    for mutant in selected:
        verdict, detail = _apply_and_run(mutant)
        results.append((mutant, verdict, detail))
        print(f"{verdict:<10} {mutant.id}")

    failures = [(mutant, verdict, detail) for mutant, verdict, detail in results if verdict != "killed"]
    print(f"\n{len(results) - len(failures)}/{len(results)} mutants killed.")
    if not failures:
        print("Result: every listed test is sensitive to its named invariant.")
        return 0

    print("\nUnenforced or invalid mutants:")
    for mutant, verdict, detail in failures:
        print(f"\n  {verdict} {mutant.id}")
        print(f"    {mutant.file}: {mutant.reason}")
        print(f"    tests: {', '.join(mutant.tests)}")
        if detail:
            print(f"    {detail}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
