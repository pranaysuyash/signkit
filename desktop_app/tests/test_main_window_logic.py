import os
import io
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, QRect, QRectF, Qt, QSettings
from PySide6.QtGui import QImage, QColor
from PySide6.QtWidgets import QApplication, QListWidgetItem, QMessageBox

from desktop_app.views.main_window import MainWindow
from desktop_app.state.session import SessionState
from PIL import Image, ImageDraw


class DummyApiClient:
    def __init__(self):
        self.upload_calls = []

    def upload_image(self, path: str):
        self.upload_calls.append(path)
        return {"id": "rotated-session"}

    def process_image(self, **kwargs):
        raise NotImplementedError("process_image should be mocked per-test if needed")

    def health_check(self, timeout=2.0):
        return True, {"version": "test"}


class DummyBackendManager:
    """Stub backend manager that reports offline immediately."""
    def is_available(self):
        return False


class OnlineBackendManager:
    """Stub backend manager for the online status-bar path."""

    def is_available(self):
        return True


@pytest.fixture
def main_window(qapp):
    QSettings("SignKit", "DesktopApp").setValue("onboarding/show_on_startup", False)
    window = MainWindow(DummyApiClient(), SessionState(), backend_manager=DummyBackendManager())
    window._backend_check_timer.stop()
    return window


def _set_source_selection(window: MainWindow, tl_scene: QPointF, br_scene: QPointF) -> QRect:
    """Helper to seed source view selection state for tests."""
    rect_scene = QRectF(tl_scene, br_scene).normalized()
    tl_view = window.src_view.mapFromScene(rect_scene.topLeft())
    br_view = window.src_view.mapFromScene(rect_scene.bottomRight())
    rect_view = QRect(tl_view, br_view).normalized()
    window.src_view._last_rect = rect_view
    scene_points = [
        rect_scene.topLeft(),
        rect_scene.topRight(),
        rect_scene.bottomLeft(),
        rect_scene.bottomRight(),
    ]
    xs = [pt.x() for pt in scene_points]
    ys = [pt.y() for pt in scene_points]
    window.src_view._last_rect_scene_bounds = QRectF(QPointF(min(xs), min(ys)), QPointF(max(xs), max(ys)))
    return rect_view


def _make_image(width=100, height=100, color="#ffffff"):
    image = QImage(width, height, QImage.Format_RGB32)
    image.fill(QColor(color))
    return image


def test_active_pane_rotation_buttons(main_window):
    # Arrange: populate each pane with an image so controls can enable
    main_window.src_view.set_image(_make_image())
    main_window.preview_view.set_image(_make_image(40, 40))
    main_window.result_label.setVisible(True)
    main_window.res_view.setVisible(True)
    main_window.res_view.set_image(_make_image(30, 30))

    # Act: activate preview pane
    main_window._on_pane_clicked("preview")
    main_window._update_view_actions_enabled()

    # Assert
    assert main_window._active_pane == "preview"
    assert main_window.rotate_cw_btn.isEnabled()
    assert main_window.rotate_ccw_btn.isEnabled()

    # Act: switch to result pane
    main_window._on_pane_clicked("result")
    main_window._update_view_actions_enabled()

    assert main_window._active_pane == "result"
    assert main_window.rotate_cw_btn.isEnabled()
    assert main_window.rotate_ccw_btn.isEnabled()


def test_backend_health_updates_top_level_status_label(main_window):
    main_window.backend_manager = OnlineBackendManager()

    main_window._check_backend_health()

    assert main_window.backend_status_label.text() == "Local service: Online"


def test_typed_backend_timeout_uses_bounded_local_recovery_copy(main_window, monkeypatch):
    from desktop_app.api.errors import BackendUnavailable

    shown = []
    monkeypatch.setattr(QMessageBox, "critical", lambda *args: shown.append(args[2]))
    main_window._handle_backend_exception(BackendUnavailable("Backend timed out during upload"), context="Upload failed")

    assert len(shown) == 1
    assert "did not respond in time" in shown[0]
    assert "Backend timed out during upload" not in shown[0]


def test_companion_offline_state_exposes_retry_control(main_window):
    main_window._on_backend_offline("test outage")
    assert not main_window.retry_companion_button.isHidden()

    main_window._on_backend_online()
    assert main_window.retry_companion_button.isHidden()


def test_rotate_preview_updates_rotation_state(main_window):
    main_window.preview_view.set_image(_make_image())
    main_window._on_pane_clicked("preview")
    main_window._update_view_actions_enabled()

    starting_rotation = main_window.preview_view._rotation
    main_window.on_rotate(90)

    assert main_window.preview_view._rotation == (starting_rotation - 90) % 360


def test_selection_crop_updates_preview(main_window):
    source_image = _make_image(120, 80)
    main_window.src_view.set_image(source_image)

    # Simulate a selection by mapping scene coordinates to view coordinates
    rect = _set_source_selection(main_window, QPointF(10, 10), QPointF(40, 35))

    # Act
    main_window.on_selection_changed(rect)

    preview_image = main_window.preview_view.image()
    assert preview_image is not None
    x1, y1, x2, y2 = main_window.src_view.selected_rect_image_coords()
    assert preview_image.width() == x2 - x1
    assert preview_image.height() == y2 - y1

    # Ensure coordinates returned to backend align with preview dimensions
    x1, y1, x2, y2 = main_window.src_view.selected_rect_image_coords()
    assert (x2 - x1, y2 - y1) == (preview_image.width(), preview_image.height())


@pytest.mark.skip(reason="Requires event loop for QTimer.singleShot chain in on_rotate -> _on_rotate_upload_finished")
def test_source_rotation_reuploads_and_clears_selection(main_window):
    # Prepare current image bytes
    pil_image = Image.new("RGBA", (20, 10), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(pil_image)
    draw.rectangle([2, 2, 17, 7], fill=(255, 0, 0, 255))
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    main_window._current_image_data = png_bytes
    main_window.src_view.set_image(QImage.fromData(png_bytes))

    # Create a real session in the local extractor so rotation can find it
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(png_bytes)
    tmp.flush()
    tmp.close()
    original_session_id = main_window.local_extractor.create_session(tmp.name)
    main_window.session.set_extraction_session(original_session_id)
    main_window._last_local_path = tmp.name

    _set_source_selection(main_window, QPointF(2, 2), QPointF(8, 8))

    main_window._on_pane_clicked("source")
    main_window._update_view_actions_enabled()

    main_window.on_rotate(90)

    assert main_window.session.session_id != original_session_id
    assert main_window.src_view.selected_rect_image_coords() == (0, 0, 0, 0)
    assert not main_window.preview_view.has_image()

    import os
    os.unlink(tmp.name)

    rotated_image = QImage.fromData(main_window._current_image_data)
    assert rotated_image.pixelColor(0, 0).alpha() == 0


def test_rotate_result_pane_changes_only_view(main_window):
    main_window.res_view.set_image(_make_image())
    main_window._on_pane_clicked("result")
    main_window._update_view_actions_enabled()

    start_rotation = main_window.res_view._rotation
    main_window.on_rotate(90)

    assert main_window.res_view._rotation == (start_rotation - 90) % 360
    # Source selection should remain untouched
    assert main_window.src_view.selected_rect_image_coords() == (0, 0, 0, 0)


def test_controls_disabled_when_active_pane_empty(main_window):
    main_window._on_pane_clicked("result")
    main_window._update_view_actions_enabled()

    assert not main_window.rotate_cw_btn.isEnabled()
    assert not main_window.rotate_ccw_btn.isEnabled()
    assert not main_window.fit_btn.isEnabled()


def test_clear_selection_hides_preview(main_window):
    main_window.preview_view.set_image(_make_image())
    main_window.preview_container.setVisible(True)
    main_window.result_label.setVisible(True)
    main_window.res_view.setVisible(True)

    main_window.on_clear_selection()

    assert not main_window.preview_container.isVisible()
    assert not main_window.res_view.isVisible()


def test_escape_clears_source_selection(main_window):
    main_window.src_view.set_image(_make_image(120, 80))
    _set_source_selection(main_window, QPointF(8, 8), QPointF(44, 40))

    assert main_window.src_view.has_selection()

    main_window._handle_escape_cancel()

    assert not main_window.src_view.has_selection()
    assert main_window.sel_info.text() == "Selection: –"


def test_schedule_preview_blocks_zero_selection(main_window):
    main_window.src_view.set_image(_make_image(120, 80))
    main_window.session.set_extraction_session("demo-session")

    # No selection
    main_window.schedule_preview()

    assert not main_window._preview_timer.isActive()


def test_source_selection_guard_raises_on_empty(main_window):
    main_window.src_view.set_image(_make_image(120, 80))

    with pytest.raises(ValueError, match="No selection"):
        main_window._get_source_selection()


def test_clean_session_resets_views(main_window):
    main_window.session.set_extraction_session("active-session")
    main_window._last_result_png = b"pngbytes"
    main_window.src_view.set_image(_make_image())
    main_window.preview_view.set_image(_make_image(40, 30))
    main_window.preview_label.setVisible(True)
    main_window.preview_view.setVisible(True)
    main_window.preview_container.setVisible(True)
    main_window.res_view.set_image(_make_image(20, 20))
    main_window.res_view.setVisible(True)
    main_window.result_label.setVisible(True)

    main_window.on_clean_session()

    assert main_window.session.session_id is None
    assert not main_window.src_view.has_image()
    assert not main_window.preview_view.has_image()
    assert not main_window.res_view.has_image()
    assert main_window._last_result_png is None
    assert main_window.clean_session_btn.isEnabled() is False


@pytest.mark.skip(reason="Requires event loop for QTimer.singleShot callbacks in _refresh_library_list")
def test_save_to_library_uses_storage(monkeypatch, main_window):
    captured = {}

    def fake_save(png_bytes):
        captured["bytes"] = png_bytes
        return "/tmp/fake.png"

    def fake_list_items(limit=50):
        captured["refresh_called"] = True
        return []

    monkeypatch.setattr("desktop_app.library.storage.save_png_to_library", fake_save)
    monkeypatch.setattr("desktop_app.library.storage.list_items", fake_list_items)

    main_window._last_result_png = b"pngbytes"
    main_window.on_save_to_library()

    assert captured["bytes"] == b"pngbytes"
    assert captured.get("refresh_called")


def test_library_delete_button_enables_with_selection(main_window):
    # Simulate library items
    item = QListWidgetItem("sig")
    item.setData(Qt.ItemDataRole.UserRole, "/tmp/sig.png")
    main_window.library_list.addItem(item)
    main_window._update_library_controls()
    assert not main_window.delete_from_library_btn.isEnabled()

    item.setSelected(True)
    main_window._update_library_controls()
    assert main_window.delete_from_library_btn.isEnabled()


def test_main_window_uses_single_canonical_pdf_tab(main_window):
    pdf_tabs = [
        main_window.tab_widget.tabText(i)
        for i in range(main_window.tab_widget.count())
        if "PDF" in main_window.tab_widget.tabText(i)
    ]

    assert pdf_tabs == ["📄 PDF Signing"]


def test_pdf_open_loads_visible_viewer_and_close_clears_state(monkeypatch, main_window):
    pdf_path = str(
        Path(__file__).resolve().parent / "fixtures" / "sample.pdf"
    )
    if not Path(pdf_path).exists() or not getattr(main_window, "pdf_viewer", None):
        pytest.skip("PDF viewer dependencies or fixture are unavailable")

    monkeypatch.setattr(main_window, "_native_open_file", lambda *args, **kwargs: pdf_path)
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)

    main_window.on_pdf_open()

    assert main_window._current_pdf_path == pdf_path
    assert main_window.session.pdf_state is not None
    assert main_window.pdf_viewer.renderer is not None
    assert main_window.pdf_viewer.page_label.text().startswith("Page 1 of")

    main_window.on_pdf_close()

    assert main_window._current_pdf_path is None
    assert main_window.session.pdf_state is None
    assert main_window.pdf_viewer.renderer is None


def test_workflow_review_action_locked_state_routes_to_upgrade(monkeypatch, main_window):
    upgrade_calls = []
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(main_window, "_open_workflow_upgrade", lambda: upgrade_calls.append(True))

    main_window.workflow_review_action.trigger()

    assert upgrade_calls == [True]


def test_workflow_review_action_fallback_uses_attributed_content_free_url(monkeypatch, main_window):
    opened_urls = []
    monkeypatch.setattr(main_window, "_open_url", opened_urls.append)
    main_window.workflow_premium_enabled = True
    del main_window.workflow_console_tab
    del main_window._workflow_console_tab_index

    main_window.workflow_review_action.trigger()

    assert opened_urls == [
        "https://pranaysuyash.com/contact"
        "?source=signkit&entry=desktop-app&intent=document-workflow"
    ]
    assert all(term not in opened_urls[0] for term in ("file=", "document=", "path=", "result="))


def test_batch_queue_actions_remain_readable_in_sidebar(main_window):
    main_window.resize(1000, 700)
    main_window.show()
    QApplication.processEvents()

    buttons = (
        main_window.batch_add_btn,
        main_window.batch_process_selected_btn,
        main_window.batch_process_next_btn,
        main_window.batch_process_all_btn,
        main_window.batch_remove_btn,
        main_window.batch_clear_btn,
    )

    assert all(button.width() >= 100 for button in buttons)


def test_on_delete_selected_library(monkeypatch, main_window):
    items_deleted = []

    def fake_delete(path):
        from desktop_app.library.storage import DeletionResult

        items_deleted.append(path)
        return DeletionResult("deleted", True, True)

    monkeypatch.setattr("desktop_app.library.storage.delete_item_with_result", fake_delete)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)

    item = QListWidgetItem("sig")
    item.setData(Qt.ItemDataRole.UserRole, "/tmp/sig.png")
    main_window.library_list.addItem(item)
    item.setSelected(True)

    main_window.on_delete_selected_library()

    assert "/tmp/sig.png" in items_deleted
    # List refreshed, so selection cleared and button disabled
    assert not main_window.delete_from_library_btn.isEnabled()


def test_library_open_delegates_to_canonical_loader(monkeypatch, main_window, tmp_path):
    image_path = tmp_path / "library.png"
    Image.new("RGB", (16, 16), color="blue").save(image_path, format="PNG")

    calls = []

    def fake_load(path, *, auto_select=True):
        calls.append((path, auto_select))
        return "session-123"

    monkeypatch.setattr(main_window, "_load_image_from_path", fake_load)

    item = QListWidgetItem("sig")
    item.setData(Qt.ItemDataRole.UserRole, str(image_path))

    main_window.on_library_item_open(item)

    assert calls == [(str(image_path), False)]
    assert main_window.status_bar.currentMessage() == "Loaded into Source from library"


@pytest.mark.skip(reason="Requires event loop for QTimer.singleShot callbacks in on_library_item_open")
def test_library_open_sets_source_active(main_window):
    # Create a fake library PNG file
    pil_image = Image.new("RGB", (32, 32), color="blue")
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        pil_image.save(temp_file, format="PNG")
        temp_file.flush()
        temp_file.close()

        item = QListWidgetItem("sig")
        item.setData(Qt.ItemDataRole.UserRole, temp_file.name)

        main_window.on_library_item_open(item)

        assert main_window._active_pane == "source"
        assert main_window.rotate_cw_btn.isEnabled()
    finally:
        os.unlink(temp_file.name)


def test_auto_threshold_toggle(main_window):
    # Create an image with distinct dark/light regions
    pil_image = Image.new("L", (40, 20), color=20)
    draw = ImageDraw.Draw(pil_image)
    draw.rectangle([20, 0, 39, 19], fill=230)
    buffer = io.BytesIO()
    pil_image.convert("RGB").save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    main_window.src_view.set_image(QImage.fromData(img_bytes))
    _set_source_selection(main_window, QPointF(0, 0), QPointF(40, 20))

    main_window.threshold.setValue(5)
    main_window.auto_threshold_cb.setChecked(True)

    QApplication.processEvents()

    assert main_window._auto_threshold_enabled is True
    assert not main_window.threshold.isEnabled()
    auto_value = main_window.threshold.value()
    assert 0 <= auto_value <= 255

    main_window.auto_threshold_cb.setChecked(False)
    QApplication.processEvents()
    assert main_window._auto_threshold_enabled is False
    assert main_window.threshold.isEnabled()
