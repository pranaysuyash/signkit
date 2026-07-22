"""Tests for the background signature-preview pipeline.

Extraction pipelines are a high-risk path (motto_v3 0.5): before this change,
`on_preview` ran cv2 thresholding/K-Means, a backend HTTP sync, and quality
analysis synchronously on the Qt UI thread, freezing the app for large
selections. This suite covers both layers of the fix:

1. `run_signature_preview` — the pure, Qt-free worker function — success,
   extraction-failure, and quality-analysis-failure paths.
2. `MainWindow._on_preview_worker_finished` — the UI-thread result handler,
   including the stale-result guard that discards a superseded request.
3. An end-to-end run through the real QThreadPool via `on_preview()`.
"""

import time

import pytest
from PIL import Image, ImageDraw

pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtWidgets import QApplication

from desktop_app.processing.extractor import SignatureExtractor
from desktop_app.views.main_window_parts.extraction_utils import run_signature_preview


def _make_signature_image(path: str, size=(200, 100)) -> None:
    img = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line([(20, 80), (60, 20), (100, 80), (140, 20), (180, 80)], fill=(10, 10, 10), width=4)
    img.save(path, format="PNG")


@pytest.fixture
def sample_image_path(tmp_path):
    path = tmp_path / "sig.png"
    _make_signature_image(str(path))
    return str(path)


# ---------------------------------------------------------------------------
# run_signature_preview: pure function, no Qt involved
# ---------------------------------------------------------------------------

def test_run_signature_preview_success(sample_image_path):
    extractor = SignatureExtractor()
    session_id = extractor.create_session(sample_image_path)
    persisted = []

    result = run_signature_preview(
        extractor=extractor,
        is_forensic=False,
        session_id=session_id,
        x1=0, y1=0, x2=200, y2=100,
        threshold_value=180,
        color_hex="#000000",
        auto_clean=False,
        persist_fn=lambda: persisted.append(True),
        request_id=1,
        start_time=time.time(),
    )

    assert result["ok"] is True
    assert result["request_id"] == 1
    assert isinstance(result["png_bytes"], (bytes, bytearray))
    assert result["quality"]["rating"] in {"Excellent", "Good", "Poor"}
    assert persisted == [True]


def test_run_signature_preview_extraction_failure_is_captured(sample_image_path):
    """An invalid session must produce ok=False, not raise into the caller."""
    extractor = SignatureExtractor()

    result = run_signature_preview(
        extractor=extractor,
        is_forensic=False,
        session_id="does-not-exist",
        x1=0, y1=0, x2=10, y2=10,
        threshold_value=180,
        color_hex="#000000",
        auto_clean=False,
        persist_fn=lambda: None,
        request_id=7,
        start_time=time.time(),
    )

    assert result["ok"] is False
    assert result["request_id"] == 7
    assert isinstance(result["error"], Exception)


def test_run_signature_preview_persist_failure_does_not_fail_preview(sample_image_path):
    """persist_fn (backend sync) is best-effort; its failure must not affect
    the local extraction result."""
    extractor = SignatureExtractor()
    session_id = extractor.create_session(sample_image_path)

    def failing_persist():
        raise RuntimeError("backend unreachable")

    result = run_signature_preview(
        extractor=extractor,
        is_forensic=False,
        session_id=session_id,
        x1=0, y1=0, x2=200, y2=100,
        threshold_value=180,
        color_hex="#000000",
        auto_clean=False,
        persist_fn=failing_persist,
        request_id=2,
        start_time=time.time(),
    )

    assert result["ok"] is True
    assert isinstance(result["png_bytes"], (bytes, bytearray))


def test_run_signature_preview_quality_failure_still_returns_png(sample_image_path, monkeypatch):
    """A quality-analysis exception must not discard the successfully
    extracted PNG — only the quality fields should reflect the failure."""
    extractor = SignatureExtractor()
    session_id = extractor.create_session(sample_image_path)

    def boom(*args, **kwargs):
        raise RuntimeError("quality analysis exploded")

    monkeypatch.setattr(extractor, "analyze_quality", boom)

    result = run_signature_preview(
        extractor=extractor,
        is_forensic=False,
        session_id=session_id,
        x1=0, y1=0, x2=200, y2=100,
        threshold_value=180,
        color_hex="#000000",
        auto_clean=False,
        persist_fn=lambda: None,
        request_id=3,
        start_time=time.time(),
    )

    assert result["ok"] is True
    assert result["quality"] is None
    assert isinstance(result["quality_error"], RuntimeError)


# ---------------------------------------------------------------------------
# MainWindow integration: stale-result guard + real QThreadPool round trip
# ---------------------------------------------------------------------------

from desktop_app.views.main_window import MainWindow
from desktop_app.state.session import SessionState
from PySide6.QtCore import QSettings, QRect


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


def _seed_session_and_selection(window: MainWindow, image_path: str):
    session_id = window.local_extractor.create_session(image_path)
    window.session.session_id = session_id

    from PySide6.QtGui import QImage, QColor
    qimg = QImage(200, 100, QImage.Format_RGB32)
    qimg.fill(QColor("white"))
    window.src_view.set_image(qimg)

    rect_scene = QRectF(QPointF(0, 0), QPointF(200, 100)).normalized()
    tl_view = window.src_view.mapFromScene(rect_scene.topLeft())
    br_view = window.src_view.mapFromScene(rect_scene.bottomRight())
    window.src_view._last_rect = QRect(tl_view, br_view).normalized()
    window.src_view._last_rect_scene_bounds = rect_scene
    return session_id


def test_stale_preview_result_is_ignored(main_window, sample_image_path):
    """A result tagged with an older request id must not overwrite the UI
    state established by a newer, already-applied result."""
    _seed_session_and_selection(main_window, sample_image_path)

    main_window._preview_request_id = 5
    stale_result = {
        "ok": True,
        "request_id": 4,  # older than current
        "start_time": time.time(),
        "png_bytes": b"should-not-be-applied",
        "quality": {"score": 100, "rating": "Excellent", "issues": []},
        "quality_error": None,
    }

    calls = []
    main_window._on_process_finished = lambda *a, **k: calls.append(a)

    main_window._on_preview_worker_finished(stale_result)

    assert calls == []  # stale result must never reach _on_process_finished


def test_fresh_preview_result_is_applied(main_window, sample_image_path):
    _seed_session_and_selection(main_window, sample_image_path)

    main_window._preview_request_id = 5
    fresh_result = {
        "ok": True,
        "request_id": 5,
        "start_time": time.time(),
        "png_bytes": b"applied",
        "quality": {"score": 90, "rating": "Excellent", "issues": []},
        "quality_error": None,
    }

    calls = []
    main_window._on_process_finished = lambda *a, **k: calls.append(a)

    main_window._on_preview_worker_finished(fresh_result)

    assert len(calls) == 1
    assert calls[0][0] == b"applied"
    # main_window is never shown in tests, so isVisible() is always False
    # regardless of setVisible(); isHidden() reflects the widget's own
    # explicit show/hide state independent of the (unshown) top-level window.
    assert not main_window.health_badge.isHidden()


def test_on_preview_runs_end_to_end_via_threadpool(main_window, sample_image_path):
    """Full round trip through the real QThreadPool: on_preview() dispatches
    a worker and the UI is updated once it completes, without blocking the
    calling thread synchronously."""
    _seed_session_and_selection(main_window, sample_image_path)

    finished = []
    original = main_window._on_preview_worker_finished

    def spy(result):
        finished.append(result)
        return original(result)

    main_window._on_preview_worker_finished = spy

    main_window.on_preview()

    deadline = time.time() + 5.0
    while not finished and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)

    assert finished, "preview worker did not complete within timeout"
    assert finished[0]["ok"] is True
    assert isinstance(finished[0]["png_bytes"], (bytes, bytearray))
