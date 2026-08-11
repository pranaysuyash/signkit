"""Tests for durable PDF placement sessions."""

from pathlib import Path

from desktop_app.pdf.document_session_store import load_document_session, save_document_session


def test_document_session_roundtrip(tmp_path, monkeypatch):
    pdf_path = tmp_path / "contract.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setenv("HOME", str(tmp_path))

    placements = [
        {
            "page": 0,
            "x": 120,
            "y": 180,
            "width": 150,
            "height": 48,
            "sig_path": "/tmp/signature.png",
            "units": "px",
            "dpi": 150,
            "scale": 1.0,
        }
    ]

    save_document_session(str(pdf_path), placements)
    loaded = load_document_session(str(pdf_path))

    assert loaded == placements


def test_document_session_restores_after_pdf_changes(tmp_path, monkeypatch):
    pdf_path = tmp_path / "contract.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setenv("HOME", str(tmp_path))

    placements = [{"page": 0, "x": 1, "y": 2, "width": 3, "height": 4, "sig_path": "x"}]
    save_document_session(str(pdf_path), placements)

    pdf_path.write_bytes(b"%PDF-1.4 changed")
    assert load_document_session(str(pdf_path)) == placements
