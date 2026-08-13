from __future__ import annotations

from types import SimpleNamespace

from desktop_app.pdf import preflight


def test_qpdf_preflight_reports_explicit_unavailability(monkeypatch, tmp_path):
    monkeypatch.setattr(preflight.shutil, "which", lambda _: None)

    result = preflight.run_qpdf_check(tmp_path / "document.pdf")

    assert result.available is False
    assert result.status == "unavailable"
    assert result.can_process is True


def test_qpdf_preflight_classifies_warning_and_error_exit_codes(monkeypatch, tmp_path):
    responses = iter(
        [
            SimpleNamespace(returncode=3, stdout="warning", stderr=""),
            SimpleNamespace(returncode=2, stdout="", stderr="error"),
        ]
    )
    monkeypatch.setattr(preflight.shutil, "which", lambda _: "/usr/bin/qpdf")
    monkeypatch.setattr(preflight.subprocess, "run", lambda *args, **kwargs: next(responses))

    warning = preflight.run_qpdf_check(tmp_path / "warning.pdf")
    error = preflight.run_qpdf_check(tmp_path / "error.pdf", suppress_recovery=True)

    assert warning.status == "warnings"
    assert warning.can_process is True
    assert error.status == "errors"
    assert error.can_process is False
