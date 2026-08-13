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


def test_document_session_falls_back_to_matching_filename(tmp_path, monkeypatch):
    original_dir = tmp_path / "original"
    moved_dir = tmp_path / "renamed"
    original_dir.mkdir()
    moved_dir.mkdir()

    original_pdf = original_dir / "contract.pdf"
    moved_pdf = moved_dir / "contract.pdf"
    original_pdf.write_bytes(b"%PDF-1.4 original")
    moved_pdf.write_bytes(b"%PDF-1.4 renamed")

    monkeypatch.setenv("HOME", str(tmp_path))

    placements = [{"page": 0, "x": 12, "y": 18, "width": 30, "height": 40, "sig_path": "sig.png"}]
    save_document_session(str(original_pdf), placements)

    loaded = load_document_session(str(moved_pdf))
    assert loaded == placements


def test_document_session_exact_path_preferred_over_filename_match(tmp_path, monkeypatch):
    dir_one = tmp_path / "one"
    dir_two = tmp_path / "two"
    dir_one.mkdir()
    dir_two.mkdir()

    pdf_one = dir_one / "contract.pdf"
    pdf_two = dir_two / "contract.pdf"
    pdf_one.write_bytes(b"%PDF-1.4 one")
    pdf_two.write_bytes(b"%PDF-1.4 two")

    monkeypatch.setenv("HOME", str(tmp_path))

    save_document_session(str(pdf_one), [{"page": 0, "x": 1, "y": 2, "width": 3, "height": 4, "sig_path": "old.png"}])
    save_document_session(str(pdf_two), [{"page": 0, "x": 11, "y": 22, "width": 33, "height": 44, "sig_path": "new.png"}])

    loaded = load_document_session(str(pdf_two))
    assert any(item.get("x") == 11 for item in loaded)
    assert any(item.get("x") == 1 for item in loaded) is False
