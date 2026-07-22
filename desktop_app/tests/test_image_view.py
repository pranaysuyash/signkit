"""Tests for desktop_app/widgets/image_view.py.

Focus: ImageView.set_pixmap() lets a caller that already converted a QImage
to a QPixmap (e.g. to cache it) display that same QPixmap without triggering
a second, redundant QImage->QPixmap conversion via set_image().
"""

import pytest

pytest.importorskip("PySide6")

from PySide6.QtGui import QImage, QColor, QPixmap
from PySide6.QtWidgets import QApplication

from desktop_app.widgets.image_view import ImageView


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def _make_qimage(w=64, h=48, color="blue") -> QImage:
    img = QImage(w, h, QImage.Format.Format_RGB32)
    img.fill(QColor(color))
    return img


def test_set_pixmap_displays_given_pixmap_without_reconverting(qapp, monkeypatch):
    view = ImageView()
    qimage = _make_qimage()

    conversions = []
    original_from_image = QPixmap.fromImage

    def counting_from_image(*args, **kwargs):
        conversions.append(1)
        return original_from_image(*args, **kwargs)

    monkeypatch.setattr(QPixmap, "fromImage", staticmethod(counting_from_image))

    pixmap = QPixmap.fromImage(qimage)  # the one conversion the caller does
    assert len(conversions) == 1

    view.set_pixmap(pixmap)

    assert len(conversions) == 1, "set_pixmap must not perform another QImage->QPixmap conversion"
    assert view.has_image()
    assert view.pixmap_item.pixmap().toImage() == pixmap.toImage()


def test_set_image_still_converts_from_qimage(qapp):
    """set_image() remains the entry point for callers that only have a
    QImage (no separately-cached QPixmap)."""
    view = ImageView()
    qimage = _make_qimage(color="red")

    view.set_image(qimage)

    assert view.has_image()
    assert view.pixmap_item.pixmap().toImage() == qimage
