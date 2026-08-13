from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from reportlab.pdfgen import canvas

from desktop_app.pdf.field_detection import SignatureFieldDetector
from desktop_app.pdf.renderer import PDFRenderer
from desktop_app.pdf.pdfium_runtime import PDFIUM_LOCK
from desktop_app.processing.pdf_engine import PdfEngine


def _make_pdf(path: Path, page_count: int = 3) -> None:
    pdf = canvas.Canvas(str(path))
    for page_index in range(page_count):
        pdf.drawString(72, 720, f"Page {page_index + 1}")
        pdf.line(72, 680, 260, 680)
        pdf.showPage()
    pdf.save()


def test_pdfium_lock_is_reentrant() -> None:
    with PDFIUM_LOCK:
        with PDFIUM_LOCK:
            assert PDFIUM_LOCK._is_owned()


def test_concurrent_detection_and_rendering_complete_without_native_race(tmp_path: Path) -> None:
    pdf_path = tmp_path / "concurrent.pdf"
    _make_pdf(pdf_path)
    detector = SignatureFieldDetector()
    renderer = PDFRenderer(str(pdf_path))

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            detection = pool.submit(
                lambda: [detector.detect_page(str(pdf_path), index % 3) for index in range(12)]
            )
            rendered = []
            for _ in range(12):
                pixmap = renderer.render_page(0, scale=0.5, dpi=72)
                rendered.append(pixmap is not None and not pixmap.isNull())

            detected = detection.result(timeout=30)

        assert len(detected) == 12
        assert all(rendered)
    finally:
        renderer.close()


def test_legacy_pdf_engine_closes_native_document(tmp_path: Path) -> None:
    pdf_path = tmp_path / "legacy-engine.pdf"
    _make_pdf(pdf_path, page_count=1)
    engine = PdfEngine()

    assert engine.load_pdf(str(pdf_path)) == 1
    assert engine.render_page(0, scale=0.5).size[0] > 0
    engine.close()

    assert engine.current_pdf is None
    assert engine.pdf_path is None
    assert engine.page_count == 0
