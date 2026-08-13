from __future__ import annotations

import pytest

from desktop_app.workflows import engine


def test_visual_export_mode_delegates_to_existing_visual_producer(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, list[dict[str, object]]]] = []

    def fake_visual(input_path: str, output_path: str, signatures: list[dict[str, object]]) -> bool:
        calls.append((input_path, output_path, signatures))
        return True

    monkeypatch.setattr(engine, "sign_pdf", fake_visual)
    signatures = [{"page": 0, "x": 10, "y": 20}]

    result = engine.export_pdf_artifact(
        "input.pdf",
        "output.pdf",
        signing_mode="visual",
        signatures=signatures,
    )

    assert result is True
    assert calls == [("input.pdf", "output.pdf", signatures)]


def test_certificate_export_mode_delegates_to_certificate_producer(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, str, dict[str, object]]] = []

    def fake_certificate(input_path: str, output_path: str, pfx_path: str, **options: object) -> str:
        calls.append((input_path, output_path, pfx_path, options))
        return "certificate-result"

    monkeypatch.setattr(engine, "sign_pdf_with_certificate", fake_certificate)

    result = engine.export_pdf_artifact(
        "input.pdf",
        "output.pdf",
        signing_mode="certificate",
        pfx_path="signer.p12",
        passphrase="secret",
    )

    assert result == "certificate-result"
    assert calls == [("input.pdf", "output.pdf", "signer.p12", {"passphrase": "secret"})]


def test_export_mode_rejects_ambiguous_configuration() -> None:
    with pytest.raises(ValueError, match="does not accept visual signatures"):
        engine.export_pdf_artifact(
            "input.pdf",
            "output.pdf",
            signing_mode="certificate",
            pfx_path="signer.p12",
            signatures=[],
        )
