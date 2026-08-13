"""CI gate: the auto-detection system-of-record must not drift from its docs.

This enforces the "validate done/pending against code before touching the doc"
rule mechanically: if a detection module exists, the canonical auto-detection
doc must name it; and the field-detection module must keep its coordinate
transform and dedupe logic in a single shared helper (no forked copies).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "AUTO_DETECTION_ML.md"
FIELD_DETECTION = REPO_ROOT / "desktop_app" / "pdf" / "field_detection.py"
IMAGE_DETECTION = REPO_ROOT / "desktop_app" / "processing" / "extractor.py"


def test_auto_detection_doc_exists() -> None:
    assert DOC.exists(), f"Canonical auto-detection doc missing: {DOC}"


def test_all_detection_modules_are_documented() -> None:
    """No detection module may exist without a corresponding doc entry."""
    doc_text = DOC.read_text(encoding="utf-8")

    assert FIELD_DETECTION.exists(), f"Detection module missing: {FIELD_DETECTION}"
    assert IMAGE_DETECTION.exists(), f"Detection module missing: {IMAGE_DETECTION}"

    assert "field_detection" in doc_text, (
        "docs/AUTO_DETECTION_ML.md does not mention desktop_app/pdf/field_detection.py "
        "(PDF signature-field detection). Every detection module must be in the doc."
    )
    assert "extractor.py" in doc_text, (
        "docs/AUTO_DETECTION_ML.md does not mention desktop_app/processing/extractor.py "
        "(image signature detection)."
    )


def test_field_detection_keeps_single_coordinate_transform() -> None:
    """The image->PDF coordinate transform must live in exactly one helper,
    not be copy-pasted across the rendered-heuristic and OCR-hint paths."""
    source = FIELD_DETECTION.read_text(encoding="utf-8")

    assert "_image_rect_to_pdf" in source, (
        "field_detection.py should expose a single _image_rect_to_pdf helper; "
        "the inline image->PDF transform was forked across two methods."
    )
    # The old inline OCR form must be gone (single source of truth).
    assert "page_width_pt * (x / image.shape[1])" not in source, (
        "field_detection.py still has the duplicated inline OCR coordinate transform; "
        "use _image_rect_to_pdf instead."
    )


def test_field_detection_keeps_single_dedupe() -> None:
    """Both candidate representations must dedupe through one shared helper."""
    source = FIELD_DETECTION.read_text(encoding="utf-8")
    assert "_dedupe(" in source, (
        "field_detection.py should dedupe both dataclass and dict candidates through a "
        "single _dedupe helper; the two near-identical dedupe methods were forked."
    )
