from pathlib import Path

from desktop_app.workflows import workflow_utils
from unittest.mock import Mock


def test_resolve_operator_subject_prefers_session_subject() -> None:
    """An explicit session subject should win over env and system fallback."""
    assert workflow_utils.resolve_operator_subject(session_subject="auditor@example.com") == "auditor@example.com"


def test_resolve_operator_subject_ignores_non_string_session_subject(monkeypatch) -> None:
    """Non-string subjects from mocks should be ignored in favor of env fallback."""
    monkeypatch.setenv("SIGNKIT_OPERATOR_SUBJECT", "env-operator@example.com")
    assert (
        workflow_utils.resolve_operator_subject(session_subject=Mock()) == "env-operator@example.com"
    )


def test_resolve_operator_subject_uses_environment_override(monkeypatch) -> None:
    """Environment variable must provide the operator subject when session subject is absent."""
    monkeypatch.setenv("SIGNKIT_OPERATOR_SUBJECT", "env-operator@example.com")
    monkeypatch.delenv("WORKFLOW_OPERATOR_SUBJECT", raising=False)
    monkeypatch.delenv("LOGNAME", raising=False)
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)

    assert workflow_utils.resolve_operator_subject() == "env-operator@example.com"


def test_resolve_operator_subject_falls_back_to_getuser(monkeypatch) -> None:
    """If no session/env subject is available, getuser() is the fallback."""
    monkeypatch.delenv("SIGNKIT_OPERATOR_SUBJECT", raising=False)
    monkeypatch.delenv("WORKFLOW_OPERATOR_SUBJECT", raising=False)
    monkeypatch.delenv("LOGNAME", raising=False)
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.setattr(workflow_utils.getpass, "getuser", lambda: "host-user")

    assert workflow_utils.resolve_operator_subject() == "host-user"


def test_resolve_operator_subject_fallback_if_getuser_fails(monkeypatch) -> None:
    """If getuser() crashes, we still return a safe local fallback value."""
    monkeypatch.delenv("SIGNKIT_OPERATOR_SUBJECT", raising=False)
    monkeypatch.delenv("WORKFLOW_OPERATOR_SUBJECT", raising=False)
    monkeypatch.delenv("LOGNAME", raising=False)
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.setattr(workflow_utils.getpass, "getuser", lambda: (_ for _ in ()).throw(RuntimeError("no user")))

    assert workflow_utils.resolve_operator_subject() == "desktop-operator"


def test_folder_id_from_path_is_deterministic(tmp_path: Path) -> None:
    """Stable path inputs must generate stable folder IDs for the same namespace."""
    input_dir = tmp_path / "input"
    review_dir = tmp_path / "review"
    sub_dir = tmp_path / "review" / "nested"
    input_dir.mkdir()
    review_dir.mkdir()
    sub_dir.mkdir(parents=True)

    input_id = workflow_utils.folder_id_from_path(str(input_dir), namespace="input")
    assert input_id == workflow_utils.folder_id_from_path(str(input_dir.resolve()), namespace="input")
    assert input_id == workflow_utils.folder_id_from_path(str(input_dir / "."), namespace="input")

    assert workflow_utils.folder_id_from_path(str(sub_dir), namespace="review") != workflow_utils.folder_id_from_path(
        str(review_dir), namespace="review"
    )
    assert workflow_utils.folder_id_from_path(str(input_dir), namespace="input") != workflow_utils.folder_id_from_path(
        str(input_dir), namespace="output"
    )
