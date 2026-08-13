"""Local UI contract for human confirmation of auto-detect candidates."""

from pathlib import Path

from PySide6.QtGui import QImage

from desktop_app.processing.extractor import SignatureCandidate
from desktop_app.views.signature_candidate_dialog import SignatureCandidateDialog


EXTRACTION_SOURCE = (
    Path(__file__).parents[1] / "desktop_app" / "views" / "main_window_parts" / "extraction.py"
)


def test_candidate_dialog_exposes_ranked_choice_and_bounded_preview(qapp) -> None:
    image = QImage(120, 80, QImage.Format.Format_RGB32)
    image.fill(0xFFFFFFFF)
    candidates = [
        SignatureCandidate((5, 6, 40, 30), 0.91, "blue-ink"),
        SignatureCandidate((70, 40, 130, 100), 0.80, "grayscale-fallback"),
    ]

    dialog = SignatureCandidateDialog(candidates, image)

    assert dialog.candidate_combo.count() == 2
    assert "score 0.91" in dialog.candidate_combo.itemText(0)
    assert dialog.selected_candidate() == candidates[0]
    dialog.candidate_combo.setCurrentIndex(1)
    assert dialog.selected_candidate() == candidates[1]
    assert not dialog.preview.pixmap().isNull()
    dialog.close()


def test_auto_detect_action_requires_candidate_confirmation() -> None:
    source = EXTRACTION_SOURCE.read_text(encoding="utf-8")

    assert "auto_detect_signatures(" in source
    assert "SignatureCandidateDialog" in source
    assert "Candidate confirmed" in source
    assert "manual selection unchanged" in source
