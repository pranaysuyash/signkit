import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parents[1]
TOOL = ROOT / "tools" / "run_local_source_to_ready_proof.py"
README = ROOT / "tools" / "README.md"


def test_local_source_to_ready_proof_runs_real_extraction_retry_and_receipt(tmp_path: Path) -> None:
    output_dir = tmp_path / "source-to-ready"
    result = subprocess.run(
        [sys.executable, str(TOOL), "--output-dir", str(output_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads(result.stdout)
    assert manifest["status"] == "pass"
    assert manifest["hosted_service_contacted"] is False
    assert manifest["document_bytes_in_browser_workspace"] is False
    assert manifest["extraction"]["session_created"] is True
    assert manifest["extraction"]["encrypted_vault_round_trip"] is True
    assert manifest["workflow"]["forced_failure_state"] == "retry"
    assert manifest["workflow"]["forced_failure_attempt"] == 1
    assert manifest["workflow"]["completed_state"] == "completed"
    assert manifest["workflow"]["completed_attempt"] == 1
    assert manifest["workflow"]["attempt_count"] == 2
    assert "EVT_SIGNING_DONE" in manifest["workflow"]["event_codes"]
    assert manifest["workflow"]["failure_passport"]["recovery_action"] == "retry_local_job"
    assert manifest["workflow"]["final_passport"]["data_boundary"] == "metadata_only_no_document_bytes"
    assert manifest["artifact_receipt"]["verification_status"] == "verified"
    assert manifest["workflow"]["final_passport"]["output_reference"] == (
        f"local-receipt:{manifest['artifact_receipt']['artifact_id']}"
    )
    final_passport_json = json.dumps(manifest["workflow"]["final_passport"])
    assert "input_path_ref" not in final_passport_json
    assert "document_bytes" not in manifest["workflow"]["final_passport"]["data_boundary"].replace(
        "metadata_only_no_document_bytes", ""
    )

    for relative_path in manifest["paths"].values():
        assert (output_dir / relative_path).exists()


def test_local_source_to_ready_proof_is_explicitly_composed_from_canonical_owners() -> None:
    source = TOOL.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert "SignatureExtractor" in source
    assert "NotaryVault" in source
    assert "WorkflowEngine" in source
    assert "project_local_job" in source
    assert "build_artifact_receipt" in source
    assert "proof_forced_transient_failure" in source
    assert "hosted_service_contacted" in source
    assert "run_local_source_to_ready_proof.py" in readme
