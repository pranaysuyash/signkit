"""
Test coordinate mapping in ImageView under various transformations.
"""
import io
import math
import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRect, QRectF, QPoint, QPointF
from PySide6.QtGui import QImage
from PIL import Image as PILImage
from PIL import ImageDraw

from desktop_app.widgets.image_view import ImageView


@pytest.fixture(scope="module")
def qapp():
    """Ensure QApplication exists for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def image_view(qapp):
    """Create ImageView with a test image."""
    view = ImageView()
    view.setGeometry(0, 0, 800, 600)
    
    # Create a test image with known dimensions and a visible pattern
    pil_img = PILImage.new("RGB", (400, 300), color="white")
    draw = ImageDraw.Draw(pil_img)
    # Draw a blue rectangle that we'll select
    draw.rectangle([50, 50, 350, 250], fill="blue", outline="red", width=2)
    
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    
    qimage = QImage.fromData(img_bytes)
    view.set_image(qimage)
    
    return view


def _set_selection(view: ImageView, tl_scene: QPointF, br_scene: QPointF) -> None:
    """Helper to set both view and scene selection rectangles for tests."""
    rect_scene = QRectF(tl_scene, br_scene).normalized()
    tl_view = view.mapFromScene(rect_scene.topLeft())
    br_view = view.mapFromScene(rect_scene.bottomRight())
    view._last_rect = QRect(tl_view, br_view).normalized()
    scene_points = [
        rect_scene.topLeft(),
        rect_scene.topRight(),
        rect_scene.bottomLeft(),
        rect_scene.bottomRight(),
    ]
    xs = [pt.x() for pt in scene_points]
    ys = [pt.y() for pt in scene_points]
    view._last_rect_scene_bounds = QRectF(QPointF(min(xs), min(ys)), QPointF(max(xs), max(ys)))


def test_coordinate_mapping_at_fit(image_view):
    """Test that coordinate mapping works when view is fitted."""
    # View is fitted by default after set_image
    # Select a region in the middle
    _set_selection(image_view, QPointF(100, 100), QPointF(200, 200))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    
    # Should map back to approximately the scene coordinates (which are image pixels)
    assert 95 <= x1 <= 105, f"x1={x1}, expected ~100"
    assert 95 <= y1 <= 105, f"y1={y1}, expected ~100"
    assert 195 <= x2 <= 205, f"x2={x2}, expected ~200"
    assert 195 <= y2 <= 205, f"y2={y2}, expected ~200"


def test_coordinate_mapping_at_100_percent(image_view):
    """Test coordinate mapping at 100% zoom (1:1 pixel mapping)."""
    # Reset to 100% zoom
    image_view.reset_zoom()
    QApplication.processEvents()
    
    # Select a region
    _set_selection(image_view, QPointF(50, 50), QPointF(150, 150))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    
    # At 100%, should be very accurate
    assert 45 <= x1 <= 55, f"x1={x1}, expected ~50"
    assert 45 <= y1 <= 55, f"y1={y1}, expected ~50"
    assert 145 <= x2 <= 155, f"x2={x2}, expected ~150"
    assert 145 <= y2 <= 155, f"y2={y2}, expected ~150"


def test_coordinate_mapping_zoomed_in(image_view):
    """Test coordinate mapping when zoomed in."""
    # Zoom in 2x
    image_view.reset_zoom()
    image_view.zoom_in()
    image_view.zoom_in()
    QApplication.processEvents()
    
    # Select a region in scene coordinates
    _set_selection(image_view, QPointF(80, 80), QPointF(120, 120))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    
    # Should still map correctly to image pixels
    assert 75 <= x1 <= 85, f"x1={x1}, expected ~80"
    assert 75 <= y1 <= 85, f"y1={y1}, expected ~80"
    assert 115 <= x2 <= 125, f"x2={x2}, expected ~120"
    assert 115 <= y2 <= 125, f"y2={y2}, expected ~120"


def test_coordinate_mapping_zoomed_out(image_view):
    """Test coordinate mapping when zoomed out."""
    # Zoom out
    image_view.reset_zoom()
    image_view.zoom_out()
    image_view.zoom_out()
    QApplication.processEvents()
    
    # Select a larger region
    _set_selection(image_view, QPointF(20, 20), QPointF(180, 180))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    
    # Should still map correctly
    assert 15 <= x1 <= 25, f"x1={x1}, expected ~20"
    assert 15 <= y1 <= 25, f"y1={y1}, expected ~20"
    assert 175 <= x2 <= 185, f"x2={x2}, expected ~180"
    assert 175 <= y2 <= 185, f"y2={y2}, expected ~180"


def test_coordinate_mapping_subpixel_selection_keeps_nonzero_area(image_view):
    """A tiny sub-pixel drag still returns a valid 1x1 selection."""
    image_view.reset_zoom()

    _set_selection(image_view, QPointF(120.2, 100.2), QPointF(120.6, 100.6))

    x1, y1, x2, y2 = image_view.selected_rect_image_coords()

    assert x2 > x1, f"selection should not collapse to zero width ({x1},{x2})"
    assert y2 > y1, f"selection should not collapse to zero height ({y1},{y2})"
    assert x2 - x1 == 1
    assert y2 - y1 == 1


def test_coordinate_mapping_rotated_90(image_view):
    """Rotated views should still yield accurate coordinates."""
    image_view.reset_zoom()
    image_view.rotate_view(90)
    QApplication.processEvents()

    # After 90° rotation, attempt to make a selection
    _set_selection(image_view, QPointF(100, 100), QPointF(150, 150))

    x1, y1, x2, y2 = image_view.selected_rect_image_coords()

    assert 95 <= x1 <= 105
    assert 95 <= y1 <= 105
    assert 145 <= x2 <= 155
    assert 145 <= y2 <= 155


def test_coordinate_mapping_rotated_180(image_view):
    """Rotating 180° should still map correctly."""
    image_view.reset_zoom()
    image_view.rotate_view(180)
    QApplication.processEvents()
    
    _set_selection(image_view, QPointF(100, 100), QPointF(200, 200))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    
    assert 95 <= x1 <= 105
    assert 95 <= y1 <= 105
    assert 195 <= x2 <= 205
    assert 195 <= y2 <= 205


def test_coordinate_clamping(image_view):
    """Test that coordinates are properly clamped to image bounds."""
    image_view.reset_zoom()
    
    # Try to select beyond image bounds
    _set_selection(image_view, QPointF(-50, -50), QPointF(500, 400))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    
    # Should be clamped to [0, 400) x [0, 300)
    assert x1 >= 0
    assert y1 >= 0
    assert x2 <= 400
    assert y2 <= 300


def test_crop_matches_coordinates(image_view):
    """Test that crop_selection returns image matching the coordinates."""
    image_view.reset_zoom()
    
    # Select a specific region
    _set_selection(image_view, QPointF(100, 100), QPointF(200, 180))
    
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    cropped = image_view.crop_selection()
    
    assert cropped is not None
    # Cropped image dimensions should match coordinate span
    assert cropped.width() == x2 - x1
    assert cropped.height() == y2 - y1


def test_explicit_zoom_setting(image_view):
    """Explicit zoom percent should adjust scaling without breaking coordinates."""
    image_view.set_zoom_percent(150)
    QApplication.processEvents()
    assert math.isclose(image_view._zoom, 1.5, rel_tol=1e-2)

    # Selection should still map correctly after zoom change
    _set_selection(image_view, QPointF(120, 90), QPointF(220, 160))
    x1, y1, x2, y2 = image_view.selected_rect_image_coords()
    assert 115 <= x1 <= 125
    assert 85 <= y1 <= 95
    assert 215 <= x2 <= 225
    assert 155 <= y2 <= 165
