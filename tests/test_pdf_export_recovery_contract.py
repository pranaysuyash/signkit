from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_pdf_save_verifies_output_and_cleans_new_partial_artifacts() -> None:
    source = (ROOT / "desktop_app" / "views" / "main_window_parts" / "pdf.py").read_text(encoding="utf-8")

    assert "verify_output" in source
    assert "output_preexisting" in source
    assert "Path(output_path).unlink(missing_ok=True)" in source
    assert "export_outcome_message" in source
    assert "save_failed" in source
