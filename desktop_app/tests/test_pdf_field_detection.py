"""Tests for PDF signature field detection."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("pypdfium2")
pytest.importorskip("pikepdf")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QColor
from PySide6.QtWidgets import QApplication

from desktop_app.pdf.field_detection import SignatureFieldDetector
from desktop_app.pdf.viewer import PDFViewer


@pytest.fixture
def signature_field_pdf() -> str:
    """Create a PDF with obvious signature field cues."""
    temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp.close()

    pdf = canvas.Canvas(temp.name, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, height - 96, "Please sign below:")
    pdf.line(72, 160, 360, 160)
    pdf.drawString(72, 142, "Signature")
    pdf.rect(380, 132, 72, 28, stroke=1, fill=0)
    pdf.drawString(380, 120, "Initials")
    pdf.showPage()
    pdf.save()

    yield temp.name

    Path(temp.name).unlink(missing_ok=True)


@pytest.fixture
def native_form_benchmark_pdf() -> str:
    """Create a reusable AcroForm PDF with multiple native widget types."""
    temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp.close()

    pdf = canvas.Canvas(temp.name, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(72, height - 54, "Native Form Benchmark")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(72, height - 78, "This fixture exercises real AcroForm widgets.")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, height - 112, "Full Name")
    pdf.setFont("Helvetica", 11)
    pdf.acroForm.textfield(name="full_name", tooltip="Full Name", x=180, y=height - 124, width=240, height=20)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, height - 154, "Agree Terms")
    pdf.acroForm.checkbox(name="agree_terms", tooltip="Agree Terms", x=180, y=height - 166, buttonStyle="check", checked=False)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, height - 196, "Country")
    pdf.acroForm.choice(
        name="country",
        tooltip="Country",
        value="US",
        options=["US", "CA", "UK"],
        x=180,
        y=height - 208,
        width=120,
        height=20,
    )

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, height - 238, "Plan")
    pdf.acroForm.radio(name="plan", value="basic", selected=True, x=180, y=height - 250, tooltip="Plan")
    pdf.acroForm.radio(name="plan", value="pro", selected=False, x=260, y=height - 250, tooltip="Plan")
    pdf.showPage()
    pdf.save()

    yield temp.name
    Path(temp.name).unlink(missing_ok=True)


def test_detect_signature_fields(signature_field_pdf: str) -> None:
    """Detect obvious signature-like fields in a generated PDF."""
    detector = SignatureFieldDetector()
    candidates = detector.detect_page(signature_field_pdf, 0)

    assert candidates, "Expected at least one signature field candidate"

    field_types = {candidate.field_type for candidate in candidates}
    assert field_types & {"signature_line", "signature_box", "initials_box", "field_box", "signature"}

    assert any(candidate.confidence >= 0.5 for candidate in candidates)


def test_place_signature_on_detected_field(signature_field_pdf: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Snap a selected signature into a detected field area."""
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.warning", lambda *args, **kwargs: None)

    temp_sig = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_sig.close()

    pixmap = QPixmap(220, 80)
    pixmap.fill(Qt.GlobalColor.white)
    painter = QPainter(pixmap)
    painter.setPen(QColor(0, 0, 0))
    painter.drawText(10, 45, "Signature")
    painter.end()
    pixmap.save(temp_sig.name)

    viewer = PDFViewer()
    assert viewer.open_pdf(signature_field_pdf)
    viewer.set_signature_for_placement(pixmap, temp_sig.name)
    viewer.page_view.set_field_candidates(
        [
            {
                "x": 72,
                "y": 120,
                "width": 288,
                "height": 48,
                "field_type": "signature_line",
                "confidence": 0.9,
                "label": "signature line",
            }
        ]
    )

    placed = viewer.place_signature_on_detected_field()

    assert placed is True
    assert len(viewer.page_view.signatures) == 1
    sig = viewer.page_view.signatures[0]
    assert sig["sig_path"] == temp_sig.name
    assert sig["x"] >= 72
    assert sig["y"] >= 120
    assert sig["width"] <= 288
    assert sig["height"] <= 48

    viewer.close_pdf()
    Path(temp_sig.name).unlink(missing_ok=True)


def test_place_signature_on_detected_field_without_cached_candidates_runs_async(
    signature_field_pdf: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When no field candidates are cached yet, placement must detect first
    asynchronously (not block the caller) and deliver the result via
    on_complete once detection + placement finish."""
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.warning", lambda *args, **kwargs: None)

    temp_sig = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_sig.close()
    pixmap = QPixmap(220, 80)
    pixmap.fill(Qt.GlobalColor.white)
    pixmap.save(temp_sig.name)

    viewer = PDFViewer()
    assert viewer.open_pdf(signature_field_pdf)
    viewer.set_signature_for_placement(pixmap, temp_sig.name)
    assert viewer.page_view.field_candidates == []  # nothing cached yet

    results = []
    immediate_return = viewer.place_signature_on_detected_field(on_complete=results.append)

    # Must not block: no result yet, nothing placed synchronously.
    assert immediate_return is None
    assert results == []
    assert len(viewer.page_view.signatures) == 0

    _wait_for(lambda: len(results) == 1)

    assert results[0] is True
    assert len(viewer.page_view.signatures) == 1
    # Detection also populated the cache as a side effect, for next time.
    assert viewer.page_view.field_candidates

    viewer.close_pdf()
    Path(temp_sig.name).unlink(missing_ok=True)


def test_place_signature_on_detected_field_without_signature_returns_false_immediately(
    signature_field_pdf: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The 'no pending signature' guard must stay fully synchronous — it
    never needs detection, so it shouldn't touch the thread pool at all."""
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.information", lambda *args, **kwargs: None)

    viewer = PDFViewer()
    assert viewer.open_pdf(signature_field_pdf)

    results = []
    result = viewer.place_signature_on_detected_field(on_complete=results.append)

    assert result is False
    assert results == [False]

    viewer.close_pdf()


def _wait_for(predicate, timeout: float = 5.0) -> None:
    """Pump the Qt event loop until predicate() is true or timeout elapses."""
    deadline = time.time() + timeout
    while not predicate() and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)
    assert predicate(), "condition did not become true within timeout"


def test_find_signature_fields_restores_button_and_cursor(
    signature_field_pdf: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """find_signature_fields() now runs detection on a QThreadPool worker
    (see its docstring in desktop_app/pdf/viewer.py); it must disable the
    button and show a busy cursor while in flight, and always restore both
    once the worker completes, including on failure."""
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.warning", lambda *args, **kwargs: None)

    viewer = PDFViewer()
    assert viewer.open_pdf(signature_field_pdf)

    done = []
    viewer.find_signature_fields(on_complete=lambda candidates: done.append(candidates))

    # Busy feedback must be visible immediately, before the worker completes.
    assert not viewer.find_fields_btn.isEnabled()
    assert viewer.cursor().shape() == Qt.CursorShape.WaitCursor

    _wait_for(lambda: bool(done))

    assert viewer.find_fields_btn.isEnabled()
    assert viewer.cursor().shape() != Qt.CursorShape.WaitCursor

    viewer.close_pdf()


def test_find_signature_fields_restores_state_on_detector_failure(
    signature_field_pdf: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even if detect_page() raises (inside the worker thread), the
    button/cursor must not be left permanently disabled/busy."""
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.warning", lambda *args, **kwargs: None)

    viewer = PDFViewer()
    assert viewer.open_pdf(signature_field_pdf)

    def boom(*args, **kwargs):
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(viewer.detector, "detect_page", boom)

    done = []
    viewer.find_signature_fields(on_complete=lambda candidates: done.append(candidates))

    assert not viewer.find_fields_btn.isEnabled()

    _wait_for(lambda: len(done) == 1)

    assert done == [[]]  # error path calls on_complete([])
    assert viewer.find_fields_btn.isEnabled()
    assert viewer.cursor().shape() != Qt.CursorShape.WaitCursor

    viewer.close_pdf()


def test_field_candidate_positions_survive_page_navigation(
    signature_field_pdf: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Regression test for a coordinate-space corruption bug: navigating away
    from a page and back must not change that page's detected field-overlay
    positions.

    Root cause (fixed): PDFViewer._save_page_field_candidates() copied
    page_view.field_candidates (pixel/view-space, Y-flipped — the display
    projection built by _load_page_field_candidates) directly back into
    all_field_candidates[page] (which must stay in PDF-point-space) with no
    inverse transform, on every goto_page()/previous_page()/next_page()
    call. The next time that page loaded, the point->pixel transform ran a
    second time on already-pixel-space data, silently corrupting overlay
    positions. The method served no real purpose — field candidates are
    never mutated in the view layer (only read for selection), so there was
    never anything legitimate to save back — and was removed outright
    rather than patched with an inverse transform.
    """
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.information", lambda *a, **k: None)
    monkeypatch.setattr("desktop_app.pdf.viewer.QMessageBox.warning", lambda *a, **k: None)

    # Build a second page onto the existing single-page fixture PDF.
    import pikepdf
    two_page_path = tmp_path / "two_page.pdf"
    with pikepdf.open(signature_field_pdf) as pdf:
        pdf.pages.append(pdf.pages[0])
        pdf.save(str(two_page_path))

    viewer = PDFViewer()
    assert viewer.open_pdf(str(two_page_path))

    detected = []
    viewer.find_signature_fields(on_complete=detected.append)
    _wait_for(lambda: len(detected) == 1)
    assert detected[0], "expected at least one field candidate on page 0"

    positions_before = [
        (c["x"], c["y"], c["width"], c["height"]) for c in viewer.page_view.field_candidates
    ]

    # Navigate away and back.
    viewer.next_page()
    viewer.previous_page()

    positions_after = [
        (c["x"], c["y"], c["width"], c["height"]) for c in viewer.page_view.field_candidates
    ]

    assert positions_after == positions_before

    viewer.close_pdf()


def test_detect_native_widgets_and_limit_heuristics(native_form_benchmark_pdf: str) -> None:
    """Detect real widgets and keep heuristic noise bounded on a form-heavy PDF."""
    detector = SignatureFieldDetector()
    candidates = detector.detect_pdf(native_form_benchmark_pdf)

    acroform_types = {candidate.field_type.lower() for candidate in candidates if candidate.source == "acroform"}
    heuristic_candidates = [candidate for candidate in candidates if candidate.source != "acroform"]

    assert {"text", "checkbox", "choice"} <= acroform_types
    assert len(heuristic_candidates) <= 3
    assert len(candidates) <= 12


def test_build_scaled_signature_rect() -> None:
    """Build a scaled rect from normalized coordinates for the current page."""
    viewer = PDFViewer()
    viewer.page_view.set_page(QPixmap(200, 100))

    rect = viewer.build_scaled_signature_rect(0.25, 0.2, 0.5, 0.25)

    assert rect == (50, 20, 100, 25)


def test_build_field_anchor_signature_rect_from_ratio_prefers_best_field(signature_field_pdf: str) -> None:
    """Prefer the detected field closest to the anchor point."""
    temp_sig = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_sig.close()

    sigmap = QPixmap(100, 50)
    sigmap.fill(Qt.GlobalColor.blue)
    sigmap.save(temp_sig.name)

    viewer = PDFViewer()
    viewer.page_view.set_page(QPixmap(400, 200))
    viewer.page_view.set_field_candidates(
        [
            {
                "x": 10,
                "y": 20,
                "width": 80,
                "height": 30,
                "field_type": "field_box",
                "confidence": 0.81,
            },
            {
                "x": 300,
                "y": 140,
                "width": 80,
                "height": 30,
                "field_type": "signature_line",
                "confidence": 0.95,
            },
        ]
    )
    viewer.page_view._confidence_threshold = 0.5

    rect = viewer.build_field_anchor_signature_rect_from_ratio(0.82, 0.85, sigmap)

    assert rect is not None
    x, y, width, height = rect
    assert width <= 80
    assert height <= 30
    assert x >= 300
    assert x < 380
    assert y >= 140
    assert y < 170

    Path(temp_sig.name).unlink(missing_ok=True)
