"""Tests for batched bulk/template field detection.

Bulk-apply-to-pages and adaptive-mode bulk signing previously called
SignatureFieldDetector.detect_page() once per target page inside a
synchronous UI-thread `for` loop (via PDFViewer._detect_signature_fields_silent).
For N pages that meant N sequential blocking pdfium-render + OpenCV calls —
discovered while converting the single-page "Find Fields" button to async
(see docs/analysis/2026-07-01_performance_optimization_audit.md). This file
covers the fix: PDFViewer.detect_fields_for_pages() batches all N detections
into one QThreadPool worker, and the two bulk call sites in
desktop_app/views/main_window_parts/pdf.py now batch-detect once up front
instead of once per page.
"""

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
from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QApplication, QMessageBox

from desktop_app.pdf.viewer import PDFViewer
from desktop_app.pdf.template_store import SignaturePlacementTemplate
from desktop_app.views.main_window import MainWindow
from desktop_app.state.session import SessionState


def _wait_for(predicate, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while not predicate() and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)
    assert predicate(), "condition did not become true within timeout"


@pytest.fixture
def multi_page_pdf() -> str:
    """A 4-page PDF with a signature-line cue on every page."""
    temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp.close()

    pdf = canvas.Canvas(temp.name, pagesize=letter)
    width, height = letter
    for _ in range(4):
        pdf.setFont("Helvetica", 12)
        pdf.drawString(72, height - 96, "Please sign below:")
        pdf.line(72, 160, 360, 160)
        pdf.drawString(72, 142, "Signature")
        pdf.showPage()
    pdf.save()

    yield temp.name
    Path(temp.name).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# PDFViewer.detect_fields_for_pages
# ---------------------------------------------------------------------------

def test_detect_fields_for_pages_batches_all_pages_in_one_worker(multi_page_pdf, monkeypatch):
    viewer = PDFViewer()
    assert viewer.open_pdf(multi_page_pdf)

    calls = []
    real_detect_page = viewer.detector.detect_page

    def counting_detect_page(*args, **kwargs):
        calls.append(args)
        return real_detect_page(*args, **kwargs)

    monkeypatch.setattr(viewer.detector, "detect_page", counting_detect_page)

    results = []
    viewer.detect_fields_for_pages([0, 1, 2, 3], on_complete=results.append)

    # Dispatch must return immediately -- no detection has run synchronously yet.
    assert calls == []
    assert results == []

    _wait_for(lambda: len(results) == 1)

    assert len(calls) == 4  # one detect_page call per requested page
    assert set(viewer.all_field_candidates.keys()) >= {0, 1, 2, 3}
    for page_index in range(4):
        assert viewer.all_field_candidates[page_index]  # each page has a signature line

    viewer.close_pdf()


def test_detect_fields_for_pages_can_use_isolated_document_runtime(multi_page_pdf, monkeypatch):
    viewer = PDFViewer()
    assert viewer.open_pdf(multi_page_pdf)

    calls = []

    class FakeIsolatedRuntime:
        def detect_page(self, pdf_path, page_index):
            calls.append((pdf_path, page_index))
            return [{"page_index": page_index, "x": 10, "y": 20, "width": 100, "height": 30}]

    monkeypatch.setattr("desktop_app.pdf.viewer.IsolatedDocumentRuntime", FakeIsolatedRuntime)
    results = []
    viewer.detect_fields_for_pages(
        [0, 1],
        on_complete=results.append,
        runtime_mode="isolated",
    )
    _wait_for(lambda: len(results) == 1)

    assert [page_index for _, page_index in calls] == [0, 1]
    assert viewer.all_field_candidates[0][0]["page_index"] == 0
    assert viewer.all_field_candidates[1][0]["page_index"] == 1
    viewer.close_pdf()


def test_detect_fields_for_pages_isolates_per_page_failures(multi_page_pdf, monkeypatch):
    """One page's detection blowing up must not lose results for the others."""
    viewer = PDFViewer()
    assert viewer.open_pdf(multi_page_pdf)

    real_detect_page = viewer.detector.detect_page

    def flaky_detect_page(pdf_path, page_index):
        if page_index == 2:
            raise RuntimeError("corrupt page content stream")
        return real_detect_page(pdf_path, page_index)

    monkeypatch.setattr(viewer.detector, "detect_page", flaky_detect_page)

    results = []
    viewer.detect_fields_for_pages([0, 1, 2, 3], on_complete=results.append)
    _wait_for(lambda: len(results) == 1)

    assert viewer.all_field_candidates[2] == []  # isolated failure -> empty, not a crash
    assert viewer.all_field_candidates[0]        # unaffected pages still detected
    assert viewer.all_field_candidates[3]

    viewer.close_pdf()


def test_detect_fields_for_pages_dedupes_pages(multi_page_pdf, monkeypatch):
    viewer = PDFViewer()
    assert viewer.open_pdf(multi_page_pdf)

    calls = []
    real_detect_page = viewer.detector.detect_page
    monkeypatch.setattr(
        viewer.detector, "detect_page",
        lambda *a, **k: (calls.append(a) or real_detect_page(*a, **k)),
    )

    results = []
    viewer.detect_fields_for_pages([0, 0, 1, 0], on_complete=results.append)
    _wait_for(lambda: len(results) == 1)

    assert len(calls) == 2  # pages 0 and 1, not 4 calls for 4 (duplicated) entries

    viewer.close_pdf()


def test_detect_fields_for_pages_no_renderer_calls_back_with_empty(qapp=None):
    viewer = PDFViewer()  # no PDF opened
    results = []
    viewer.detect_fields_for_pages([0, 1], on_complete=results.append)
    assert results == [{}]  # synchronous, no worker dispatched


# ---------------------------------------------------------------------------
# MainWindow bulk-apply wiring
# ---------------------------------------------------------------------------

class DummyApiClient:
    def is_offline(self):
        return True


class DummyBackendManager:
    def is_available(self):
        return False


@pytest.fixture
def main_window(qapp):
    QSettings("SignKit", "DesktopApp").setValue("onboarding/show_on_startup", False)
    window = MainWindow(DummyApiClient(), SessionState(), backend_manager=DummyBackendManager())
    window._backend_check_timer.stop()
    return window


def _make_signature_png(path: str) -> None:
    pixmap = QPixmap(150, 50)
    pixmap.fill(QColor("white"))
    pixmap.save(path)


def test_run_after_bulk_field_detection_skips_dispatch_when_not_needed(main_window):
    """When needs_detection is False, then_fn must run synchronously with no
    thread-pool round trip and no cursor/status-bar side effects."""
    calls = []
    main_window._run_after_bulk_field_detection([0, 1, 2], False, lambda: calls.append(1))
    assert calls == [1]


def test_apply_template_to_pages_batches_detection_once_not_per_page(
    main_window, multi_page_pdf, monkeypatch
):
    """The core regression test: applying a field-anchored template to N
    pages must call detect_page exactly N times total, dispatched from a
    single detect_fields_for_pages() call -- not interleaved with N
    synchronous per-page _detect_signature_fields_silent() calls."""
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)

    assert main_window.pdf_viewer.open_pdf(multi_page_pdf)
    main_window._current_pdf_path = multi_page_pdf
    main_window.audit_logger = None

    sig_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    _make_signature_png(sig_path)

    template = SignaturePlacementTemplate(
        template_id="t1",
        name="Anchored",
        signature_path=sig_path,
        page_index=0,
        x_ratio=0.2, y_ratio=0.2, width_ratio=0.3, height_ratio=0.05,
        use_field_anchor=True,
        anchor_x_ratio=0.3, anchor_y_ratio=0.3,
    )

    detect_calls = []
    real_detect_page = main_window.pdf_viewer.detector.detect_page
    monkeypatch.setattr(
        main_window.pdf_viewer.detector, "detect_page",
        lambda *a, **k: (detect_calls.append(a) or real_detect_page(*a, **k)),
    )

    silent_calls = []
    real_silent = main_window.pdf_viewer._detect_signature_fields_silent
    monkeypatch.setattr(
        main_window.pdf_viewer, "_detect_signature_fields_silent",
        lambda: (silent_calls.append(1), real_silent())[1],
    )

    batch_dispatch_calls = []
    real_detect_for_pages = main_window.pdf_viewer.detect_fields_for_pages

    def counting_detect_for_pages(pages, on_complete):
        batch_dispatch_calls.append(list(pages))
        return real_detect_for_pages(pages, on_complete)

    monkeypatch.setattr(main_window.pdf_viewer, "detect_fields_for_pages", counting_detect_for_pages)

    target_pages = [0, 1, 2, 3]
    run_id = None

    def _run_loop():
        for page_num in target_pages:
            main_window._apply_template_to_target_page(
                page_num, template, run_id=run_id, skip_detection=True
            )

    main_window._run_after_bulk_field_detection(target_pages, True, _run_loop)

    _wait_for(lambda: len(main_window.pdf_viewer.page_view.signatures) >= 1 or batch_dispatch_calls)
    _wait_for(lambda: len(detect_calls) == len(target_pages))

    # Exactly one batched dispatch covering all 4 pages...
    assert batch_dispatch_calls == [target_pages]
    # ...and detect_page called once per page (not duplicated by a fallback
    # per-page synchronous call).
    assert len(detect_calls) == 4
    # The old per-page synchronous path must not have been used at all.
    assert silent_calls == []

    main_window.pdf_viewer.close_pdf()
    Path(sig_path).unlink(missing_ok=True)
