import logging
from typing import Optional, Tuple
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame, QApplication
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QRect, QByteArray, QBuffer, QIODevice, QMimeData
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QWheelEvent, QMouseEvent, QDrag

LOG = logging.getLogger(__name__)


class ImageView(QGraphicsView):
    """A widget for displaying and interacting with images (zoom, pan, select)."""

    selectionChanged = Signal(tuple)  # (x1, y1, x2, y2)
    fileDropped = Signal(str)         # file path
    zoomChanged = Signal(float)       # zoom level
    viewChanged = Signal()            # generic view-changed signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item: Optional[QGraphicsPixmapItem] = None
        self.selection_rect_item = None

        # State
        self._is_panning = False
        self._pan_start = QPointF()
        self._is_selecting = False
        self._selection_start = QPointF()
        self._selection_end = QPointF()
        self._zoom_level = 1.0
        self._selection_mode = True
        self._drag_source_enabled = False

        # Selection state used by tests and external helpers
        self._last_rect = QRect()
        self._last_rect_scene_bounds = QRectF()
        self._rotation = 0.0

        # Accept drops for file drag-and-drop
        self.setAcceptDrops(True)

        # UI Setup
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setBackgroundBrush(QColor("#1e1e1e"))

    # --- Image loading ---

    def load_image(self, path: str):
        """Load image from file path."""
        pixmap = QPixmap(path)
        self._set_pixmap(pixmap)

    def load_image_bytes(self, data: bytes):
        """Load image from bytes."""
        img = QImage.fromData(data)
        pixmap = QPixmap.fromImage(img)
        self._set_pixmap(pixmap)

    def set_image(self, image: QImage):
        """Set the displayed image from a QImage."""
        pixmap = QPixmap.fromImage(image)
        self._set_pixmap(pixmap)

    def set_pixmap(self, pixmap: QPixmap):
        """Set the displayed image from an already-built QPixmap.

        Prefer this over set_image() when the caller already converted the
        source QImage to a QPixmap (e.g. to cache it elsewhere) — it avoids
        a second, redundant QImage->QPixmap conversion of the same data.
        """
        self._set_pixmap(pixmap)

    def _set_pixmap(self, pixmap: QPixmap):
        self.scene.clear()
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.selection_rect_item = None
        self._zoom_level = 1.0
        self.zoomChanged.emit(self._zoom_level)

    def clear_image(self):
        self.scene.clear()
        self.pixmap_item = None
        self.selection_rect_item = None

    def clear_selection(self):
        """Remove the selection rectangle."""
        if self.selection_rect_item:
            self.scene.removeItem(self.selection_rect_item)
            self.selection_rect_item = None
        self._selection_start = QPointF()
        self._selection_end = QPointF()
        self._last_rect = QRect()
        self._last_rect_scene_bounds = QRectF()

    def has_image(self) -> bool:
        """Return True if an image is loaded."""
        return self.pixmap_item is not None

    def image(self) -> Optional[QImage]:
        """Return the current image as a QImage, or None."""
        if self.pixmap_item:
            return self.pixmap_item.pixmap().toImage()
        return None

    # --- Zoom ---

    def fit(self, margin_percent: float = 0.0):
        """Fit the image to the view with optional margin."""
        if not self.pixmap_item:
            return
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        if margin_percent > 0:
            factor = 1.0 - (margin_percent / 100.0)
            self.scale(factor, factor)
        self._zoom_level = self.transform().m11()
        self.zoomChanged.emit(self._zoom_level)
        self.viewChanged.emit()

    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.resetTransform()
        self._zoom_level = 1.0
        self.zoomChanged.emit(self._zoom_level)
        self.viewChanged.emit()

    def set_zoom_percent(self, percent: float):
        """Set zoom level as a percentage (100 = 1:1)."""
        self.resetTransform()
        factor = percent / 100.0
        self.scale(factor, factor)
        self._zoom_level = factor
        self.zoomChanged.emit(self._zoom_level)
        self.viewChanged.emit()

    def get_zoom_percent(self) -> float:
        """Return current zoom as a percentage (100 = 1:1)."""
        return self._zoom_level * 100.0

    def zoom_in(self):
        """Zoom in by 10%."""
        self.scale(1.1, 1.1)
        self._zoom_level *= 1.1
        self.zoomChanged.emit(self._zoom_level)
        self.viewChanged.emit()

    def zoom_out(self):
        """Zoom out by 10%."""
        self.scale(0.9, 0.9)
        self._zoom_level *= 0.9
        self.zoomChanged.emit(self._zoom_level)
        self.viewChanged.emit()

    def zoom_level(self) -> float:
        """Return the current zoom level (1.0 = 100%)."""
        return self._zoom_level

    @property
    def _zoom(self) -> float:
        """Alias for _zoom_level used by tests."""
        return self._zoom_level

    # --- Selection ---

    def set_selection_mode(self, enabled: bool):
        self._selection_mode = enabled
        if enabled:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            if not self._drag_source_enabled:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.setCursor(Qt.CursorShape.PointingHandCursor)

    def toggle_selection_mode(self, enabled: bool):
        """Alias for set_selection_mode used by extraction tab."""
        self.set_selection_mode(enabled)

    def set_drag_source(self, enabled: bool):
        """Enable dragging the image out of the view."""
        self._drag_source_enabled = enabled
        self.set_selection_mode(self._selection_mode)

    def get_selection(self) -> Optional[Tuple[int, int, int, int]]:
        """Get selection coordinates (x1, y1, x2, y2) relative to image."""
        if not self.selection_rect_item or not self.pixmap_item:
            return None

        rect = self.selection_rect_item.rect()
        img_rect = self.pixmap_item.boundingRect()
        x1 = max(0, int(rect.left()))
        y1 = max(0, int(rect.top()))
        x2 = min(int(img_rect.width()), int(rect.right()))
        y2 = min(int(img_rect.height()), int(rect.bottom()))

        if x2 <= x1 or y2 <= y1:
            return None

        return (x1, y1, x2, y2)

    def selected_rect_image_coords(self) -> Tuple[int, int, int, int]:
        """Get selection as (x1, y1, x2, y2) image coordinates. Returns (0,0,0,0) if no selection."""
        sel = self.get_selection()
        if sel:
            return sel
        # Fallback to programmatically-set bounds (used by tests)
        if self._last_rect_scene_bounds.isValid():
            r = self._last_rect_scene_bounds
            x1, y1 = int(r.left()), int(r.top())
            x2, y2 = int(r.right()), int(r.bottom())
            # Clamp to image bounds
            if self.pixmap_item:
                iw = int(self.pixmap_item.boundingRect().width())
                ih = int(self.pixmap_item.boundingRect().height())
                x1 = max(0, min(x1, iw))
                y1 = max(0, min(y1, ih))
                x2 = max(0, min(x2, iw))
                y2 = max(0, min(y2, ih))
            return (x1, y1, x2, y2)
        return (0, 0, 0, 0)

    def set_selection_from_coords(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Programmatically set the selection rectangle from image coordinates."""
        if not self.pixmap_item:
            return
        self._selection_start = QPointF(x1, y1)
        self._selection_end = QPointF(x2, y2)
        self._update_selection_rect()
        self._last_rect = QRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))
        self._last_rect_scene_bounds = QRectF(QPointF(x1, y1), QPointF(x2, y2))
        sel = self.get_selection()
        if sel:
            self.selectionChanged.emit(sel)

    def crop_selection(self) -> Optional[QImage]:
        """Crop the image to the current selection and return as QImage."""
        x1, y1, x2, y2 = self.selected_rect_image_coords()
        if x2 <= x1 or y2 <= y1 or not self.pixmap_item:
            return None
        img = self.pixmap_item.pixmap().toImage()
        return img.copy(x1, y1, x2 - x1, y2 - y1)

    # --- Drag and drop ---

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path:
                    self.fileDropped.emit(path)
                    break
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    # --- Rotation (stub — actual rotation handled by extraction mixin) ---

    def rotate(self, angle: float):
        """Rotate the view by *angle* degrees."""
        QGraphicsView.rotate(self, angle)

    def rotate_view(self, angle: float):
        """Rotate the view. Positive = CW (matches Qt convention)."""
        self._rotation = (self._rotation - angle) % 360
        QGraphicsView.rotate(self, angle)

    # --- Events ---

    def wheelEvent(self, event: QWheelEvent):
        zoom_in = event.angleDelta().y() > 0
        factor = 1.1 if zoom_in else 0.9
        self.scale(factor, factor)
        self._zoom_level *= factor
        self.zoomChanged.emit(self._zoom_level)
        self.viewChanged.emit()

    def mousePressEvent(self, event: QMouseEvent):
        if self._selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self._is_selecting = True
            pos = self.mapToScene(event.pos())
            self._selection_start = pos
            self._selection_end = pos
            self._update_selection_rect()
        elif self._drag_source_enabled and event.button() == Qt.MouseButton.LeftButton:
            self._pan_start = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_selecting:
            self._selection_end = self.mapToScene(event.pos())
            self._update_selection_rect()
        elif self._drag_source_enabled and event.buttons() & Qt.MouseButton.LeftButton:
            if (event.pos() - self._pan_start).manhattanLength() > 10:
                self._start_drag()
        else:
            super().mouseMoveEvent(event)

    def _start_drag(self):
        if not self.pixmap_item:
            return
        drag = QDrag(self)
        mime_data = QMimeData()
        pixmap = self.pixmap_item.pixmap()
        mime_data.setImageData(pixmap.toImage())
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        drag.setHotSpot(QPointF(50, 50).toPoint())
        drag.exec(Qt.DropAction.CopyAction)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_selecting:
            self._is_selecting = False
            self._selection_end = self.mapToScene(event.pos())
            self._update_selection_rect()

            sel = self.get_selection()
            if sel:
                x1, y1, x2, y2 = sel
                self._last_rect = QRect(x1, y1, x2 - x1, y2 - y1)
                self._last_rect_scene_bounds = QRectF(
                    QPointF(x1, y1), QPointF(x2, y2)
                )
                self.selectionChanged.emit(sel)
        else:
            super().mouseReleaseEvent(event)

    def _update_selection_rect(self):
        if not self.pixmap_item:
            return

        if not self.selection_rect_item:
            self.selection_rect_item = self.scene.addRect(
                QRectF(), QPen(QColor("#00ff00"), 2), QColor(0, 255, 0, 50)
            )
            self.selection_rect_item.setZValue(10)

        rect = QRectF(self._selection_start, self._selection_end).normalized()
        self.selection_rect_item.setRect(rect)
