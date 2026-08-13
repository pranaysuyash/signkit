from pathlib import Path


WORKSPACE_APP = Path(__file__).parents[1] / "web" / "cloud_workspace" / "app.js"


def test_workspace_renders_passport_boundary_and_recovery_without_document_claims():
    source = WORKSPACE_APP.read_text(encoding="utf-8")

    assert "const passport = execution.passport || {};" in source
    assert "passport.data_boundary" in source
    assert "passport.source_of_truth" in source
    assert "passport.aggregate_status" in source
    assert "passport.recovery_action" in source
    assert "Passport unavailable from workspace API" in source
    assert "state.executions = merged;" in source
    assert "document bytes remain outside this surface" in source
    assert "New cloud execution" not in source
