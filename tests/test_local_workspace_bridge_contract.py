from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_browser_workspace_owns_one_metadata_only_local_job_bridge() -> None:
    router = (ROOT / "backend" / "app" / "routers" / "workspace.py").read_text(encoding="utf-8")
    schema = (ROOT / "backend" / "app" / "schemas" / "workspace.py").read_text(encoding="utf-8")
    app = (ROOT / "web" / "cloud_workspace" / "app.js").read_text(encoding="utf-8")
    browser_proof = (ROOT / "tools" / "run_local_workspace_bridge_browser_proof.mjs").read_text(encoding="utf-8")

    assert '@router.get("/local-jobs"' in router
    assert '@router.get("/local-jobs/{job_id}"' in router
    assert '@router.post("/local-jobs/{job_id}/retry"' in router
    assert 'requested_action="inspect_job"' in router
    assert 'action_subject=subject' in router
    assert 'UUID is the canonical bridge identity' in router
    assert 'from desktop_app.workflows.engine import WorkflowEngine' in router
    assert '"passport": passport.to_payload()' in router
    assert 'alias="Idempotency-Key"' in router
    assert 'workflow_store.workflow_store_lock()' in router
    assert 'store.get_retry_receipt(job.job_id, retry_key)' in router
    assert 'store.save_retry_receipt(updated, retry_key)' in router
    assert "LocalWorkflowJobResponse" in schema
    assert 'api("/workspace/local-jobs")' in app
    assert 'execution.local_desktop' in app
    assert '/workspace/local-jobs/${execution.job_id}/retry' in app
    assert "retry_local_job" in app
    assert "local desktop workflow store" in app
    assert "SIGNKIT_DATA_DIR" in browser_proof
    assert "unauthenticated direct URL did not fail closed" in browser_proof
    assert "private source path leaked" in browser_proof
    assert "Retry local execution" in browser_proof
    assert "SIGNKIT_LOCAL_RECEIPT_REFERENCE" in browser_proof


def test_local_store_can_follow_the_isolated_local_product_data_root() -> None:
    source = (ROOT / "desktop_app" / "workflows" / "store.py").read_text(encoding="utf-8")

    assert 'os.environ.get("SIGNKIT_DATA_DIR")' in source
    assert 'os.environ.get("SIGNKIT_WORKFLOW_STORE_FILE")' in source
    assert 'else APP_DIR / "workflow_store.json"' in source
    assert "def workflow_store_lock()" in source
    assert '"retry_receipts"' in source
