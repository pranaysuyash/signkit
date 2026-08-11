"""PDF viewer widget with page navigation, zoom, and field detection."""

import logging
from typing import Optional, List, Dict, Any, Tuple, Callable
from collections import OrderedDict
from pathlib import Path
import sys

from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QComboBox, QMessageBox, QMenu, QToolTip
)

from desktop_app.pdf.renderer import PDFRenderer
from desktop_app.pdf.field_detection import SignatureFieldDetector
from desktop_app.widgets.modern_mac_button import ModernMacButton
from desktop_app.widgets.async_utils import AsyncRunner, dispatch

LOG = logging.getLogger(__name__)


def _create_button(
    text: str = "",
    parent: Optional[QWidget] = None,
    *,
    use_modern_mac: Optional[bool] = None,
    primary: bool = False,
    color: str = 'blue',
    compact: bool = False  # Dialog buttons are typically not compact
) -> QPushButton:
    """Create a button, using ModernMacButton on macOS if available and requested.

    Args:
        text: Button text
        parent: Parent widget
        use_modern_mac: Force modern button (default: auto-detect macOS)
        primary: True for primary action buttons (colored)
        color: One of 'blue', 'purple', 'pink', 'red', 'orange', 'yellow', 'green', 'teal'
        compact: True for smaller buttons (sidebar/toolbar), False for larger (dialogs)
    """
    if use_modern_mac is None:
        use_modern_mac = sys.platform == "darwin"

    if use_modern_mac:
        try:
            btn = ModernMacButton(
                text, parent,
                primary=primary,
                color=color,
                glass=True,
                compact=compact
            )
            return btn
        except (NameError, TypeError):
            # Fallback if ModernMacButton not available or doesn't support compact
            pass

    # Default to standard QPushButton
    return QPushButton(text, parent)


class PDFPageView(QWidget):
    """Widget to display a single PDF page with signature overlays."""
    
    signature_clicked = Signal(int)  # Emits signature index
    page_clicked = Signal(QPointF)   # Emits click position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap: Optional[QPixmap] = None
        self.signatures: List[Dict[str, Any]] = []  # [{"x": 100, "y": 200, "width": 150, "height": 50, "pixmap": QPixmap, "sig_path": ""}, ...]
        self.field_candidates: List[Dict[str, Any]] = []
        self.selected_field_candidate_index: Optional[int] = None
        self._confidence_threshold: float = 0.8
        self.setMinimumSize(400, 500)
        
        # Drag/move state
        self.dragging_signature: Optional[int] = None
        self.drag_start_pos: Optional[QPointF] = None
        self.drag_offset_x: float = 0
        self.drag_offset_y: float = 0
        
        # Resize state
        self.resizing_signature: Optional[int] = None
        self.resize_handle: Optional[str] = None  # "nw", "ne", "sw", "se", "n", "s", "e", "w"
        self.resize_start_pos: Optional[QPointF] = None
        self.resize_orig_rect: Optional[Dict[str, float]] = None
        self.resize_aspect_ratio: Optional[float] = None
        self.selected_signature: Optional[int] = None  # Currently selected signature
        
        # Placement preview state
        self.preview_pixmap: Optional[QPixmap] = None
        self.preview_pos: Optional[QPointF] = None
        self.setMouseTracking(True)  # Enable mouse tracking for preview
        
        # Coordinate tooltip state
        self._coord_tooltips_enabled = False  # Off by default in PDF viewer
        self._last_tooltip_text = ""
    
    def set_page(self, pixmap: Optional[QPixmap]) -> None:
        """Set the PDF page to display."""
        self.pixmap = pixmap
        if pixmap:
            self.setFixedSize(pixmap.size())
        self.update()
    
    def set_preview_signature(self, sig_pixmap: Optional[QPixmap]) -> None:
        """Set signature for placement preview."""
        self.preview_pixmap = sig_pixmap
        self.update()
    
    def add_signature_overlay(self, x: int, y: int, width: int, height: int, 
                             sig_pixmap: QPixmap, sig_path: str = "") -> int:
        """
        Add a signature overlay at specified position.
        
        Args:
            sig_path: Path to signature image file (needed for PDF signing)
        
        Returns:
            Index of added signature
        """
        self.signatures.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "pixmap": sig_pixmap,
            "sig_path": sig_path  # Store path with each signature
        })
        self.update()
        return len(self.signatures) - 1
    
    def remove_signature(self, index: int) -> None:
        """Remove signature overlay by index."""
        if 0 <= index < len(self.signatures):
            self.signatures.pop(index)
            self.update()
    
    def clear_signatures(self) -> None:
        """Remove all signature overlays."""
        self.signatures.clear()
        self.update()

    def set_field_candidates(self, candidates: List[Dict[str, Any]]) -> None:
        """Set read-only field candidates to highlight on the page."""
        self.field_candidates = list(candidates)
        self.update()

    def clear_field_candidates(self) -> None:
        """Clear field candidate overlays."""
        self.field_candidates.clear()
        self.update()
    
    def paintEvent(self, event):
        """Draw PDF page and signature overlays."""
        painter = QPainter(self)
        
        # Draw PDF page
        if self.pixmap:
            painter.drawPixmap(0, 0, self.pixmap)
        
        # Draw signature overlays
        for i, sig in enumerate(self.signatures):
            # Draw signature image
            scaled_sig = sig["pixmap"].scaled(
                sig["width"], sig["height"],
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(sig["x"], sig["y"], scaled_sig)
            
            # Draw selection border
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(sig["x"], sig["y"], sig["width"], sig["height"])
            
            # Draw resize handles if this signature is selected
            if i == self.selected_signature:
                self._draw_resize_handles(painter, sig)

        # Draw candidate field overlays below signatures
        for idx, candidate in enumerate(self.field_candidates):
            rect = QRectF(candidate["x"], candidate["y"], candidate["width"], candidate["height"])
            confidence = candidate.get("confidence", 0.0)
            label = candidate.get("label") or candidate.get("field_type", "field").replace("_", " ")
            is_selected = idx == self.selected_field_candidate_index
            is_confident = float(confidence) >= self._confidence_threshold

            painter.setPen(QPen(QColor(0, 120, 215, 240) if is_selected else QColor(255, 153, 0, 220 if is_confident else 120), 3 if is_selected else 2, Qt.PenStyle.DashLine))
            painter.setBrush(QColor(0, 120, 215, 55) if is_selected else QColor(255, 193, 7, 42 if is_confident else 22))
            painter.drawRoundedRect(rect, 4, 4)

            badge_h = 18
            badge_w = max(72, min(int(rect.width()), 220))
            badge_x = int(rect.x())
            badge_y = max(0, int(rect.y()) - badge_h - 2)
            painter.fillRect(badge_x, badge_y, badge_w, badge_h, QColor(0, 120, 215, 220) if is_selected else QColor(255, 153, 0, 220))
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Helvetica", 8, QFont.Weight.Bold))
            badge_text = f"{label} {int(confidence * 100)}%"
            painter.drawText(badge_x + 5, badge_y + 13, badge_text[:40])
        
        # Draw placement preview if active
        if self.preview_pixmap and self.preview_pos:
            width, height = 150, 50
            x = int(self.preview_pos.x() - width / 2)
            y = int(self.preview_pos.y() - height / 2)
            
            # Draw semi-transparent preview
            painter.setOpacity(0.6)
            scaled_preview = self.preview_pixmap.scaled(
                width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(x, y, scaled_preview)
            
            # Draw preview border
            painter.setOpacity(1.0)
            painter.setPen(QPen(QColor(0, 200, 0), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(x, y, width, height)
    
    def mousePressEvent(self, event):
        """Handle mouse click (for signature selection or placement)."""
        pos = event.position()
        pos_point = pos.toPoint()
        
        # Check if clicked on existing signature
        for i, sig in enumerate(self.signatures):
            rect = QRectF(sig["x"], sig["y"], sig["width"], sig["height"])
            if rect.contains(pos_point):
                # Select this signature
                self.selected_signature = i
                self.update()
                
                # Right-click: show context menu
                if event.button() == Qt.MouseButton.RightButton:
                    self._show_signature_context_menu(i, event.globalPosition().toPoint())
                    return
                
                # Left-click: check if on resize handle first
                if event.button() == Qt.MouseButton.LeftButton:
                    handle = self._get_resize_handle_at(pos, sig)
                    if handle:
                        # Start resizing
                        self.resizing_signature = i
                        self.resize_handle = handle
                        self.resize_start_pos = pos
                        self.resize_orig_rect = {
                            "x": sig["x"],
                            "y": sig["y"],
                            "width": sig["width"],
                            "height": sig["height"]
                        }
                        self.resize_aspect_ratio = sig["width"] / sig["height"]
                        self.setCursor(self._get_cursor_for_handle(handle))
                        return
                    else:
                        # Start dragging
                        self.dragging_signature = i
                        self.drag_start_pos = pos
                        self.drag_offset_x = pos.x() - sig["x"]
                        self.drag_offset_y = pos.y() - sig["y"]
                        self.setCursor(Qt.CursorShape.ClosedHandCursor)
                return
        
        # Clicked on empty area - deselect
        self.selected_signature = None
        self.update()
        
        # Otherwise, emit page click for new signature placement
        if event.button() == Qt.MouseButton.LeftButton:
            self.page_clicked.emit(pos)
    
    def _show_signature_context_menu(self, index: int, global_pos: QPoint) -> None:
        """Show context menu for signature."""
        menu = QMenu(self)
        remove_action = menu.addAction("🗑️ Remove Signature")
        
        action = menu.exec(global_pos)
        if action == remove_action:
            self.remove_signature(index)
    
    def _draw_resize_handles(self, painter: QPainter, sig: Dict[str, Any]) -> None:
        """Draw resize handles on selected signature."""
        handle_size = 8
        x, y, w, h = sig["x"], sig["y"], sig["width"], sig["height"]
        
        # Handle positions: corners and edges
        handles = {
            "nw": (x, y),
            "ne": (x + w, y),
            "sw": (x, y + h),
            "se": (x + w, y + h),
            "n": (x + w/2, y),
            "s": (x + w/2, y + h),
            "e": (x + w, y + h/2),
            "w": (x, y + h/2)
        }
        
        painter.setPen(QPen(QColor(0, 120, 215), 1))
        painter.setBrush(QColor(255, 255, 255))
        
        for handle_pos in handles.values():
            hx, hy = handle_pos
            painter.drawRect(
                int(hx - handle_size/2),
                int(hy - handle_size/2),
                handle_size,
                handle_size
            )
    
    def _get_resize_handle_at(self, pos: QPointF, sig: Dict[str, Any]) -> Optional[str]:
        """Check if position is over a resize handle. Returns handle name or None."""
        handle_size = 8
        tolerance = handle_size / 2 + 2
        
        x, y, w, h = sig["x"], sig["y"], sig["width"], sig["height"]
        px, py = pos.x(), pos.y()
        
        # Check each handle
        handles = {
            "nw": (x, y),
            "ne": (x + w, y),
            "sw": (x, y + h),
            "se": (x + w, y + h),
            "n": (x + w/2, y),
            "s": (x + w/2, y + h),
            "e": (x + w, y + h/2),
            "w": (x, y + h/2)
        }
        
        for handle_name, (hx, hy) in handles.items():
            if abs(px - hx) <= tolerance and abs(py - hy) <= tolerance:
                return handle_name
        
        return None
    
    def _get_cursor_for_handle(self, handle: str) -> Qt.CursorShape:
        """Get cursor shape for resize handle."""
        cursors = {
            "nw": Qt.CursorShape.SizeFDiagCursor,
            "se": Qt.CursorShape.SizeFDiagCursor,
            "ne": Qt.CursorShape.SizeBDiagCursor,
            "sw": Qt.CursorShape.SizeBDiagCursor,
            "n": Qt.CursorShape.SizeVerCursor,
            "s": Qt.CursorShape.SizeVerCursor,
            "e": Qt.CursorShape.SizeHorCursor,
            "w": Qt.CursorShape.SizeHorCursor
        }
        return cursors.get(handle, Qt.CursorShape.ArrowCursor)
    
    def enable_coordinate_tooltips(self, enabled: bool) -> None:
        """Enable or disable coordinate tooltips for this page view."""
        self._coord_tooltips_enabled = bool(enabled)
    
    def _show_coordinate_tooltip(self, event) -> None:
        """Show coordinate tooltip at mouse position if enabled."""
        if not self._coord_tooltips_enabled or not self.pixmap:
            return
        
        pos = event.position()
        x = int(pos.x())
        y = int(pos.y())
        
        # Build tooltip text with PDF page coordinates
        coords = f"PDF: {x}, {y}"
        
        # Add signature info if hovering over one
        for i, sig in enumerate(self.signatures):
            rect = QRectF(sig["x"], sig["y"], sig["width"], sig["height"])
            if rect.contains(pos.toPoint()):
                coords += f"  •  Sig#{i+1}: {sig['width']}×{sig['height']}"
                if i == self.selected_signature:
                    coords += " [selected]"
                break
        
        # Show during resize/drag operations
        if self.resizing_signature is not None:
            sig = self.signatures[self.resizing_signature]
            coords += f"  •  Resizing: {sig['width']}×{sig['height']}"
        elif self.dragging_signature is not None:
            sig = self.signatures[self.dragging_signature]
            coords += f"  •  Moving: ({sig['x']}, {sig['y']})"
        elif self.preview_pixmap:
            coords += f"  •  Preview: {self.preview_pixmap.width()}×{self.preview_pixmap.height()}"
        
        # Use HTML with explicit black text on yellow background
        text = f'<span style="background-color: #ffffcc; color: #000000; padding: 4px; border: 1px solid #888;">{coords}</span>'
        
        # Avoid spamming identical tooltips
        if text == self._last_tooltip_text:
            return
        self._last_tooltip_text = text
        
        # Show tooltip near cursor
        global_pos = self.mapToGlobal(event.position().toPoint())
        QToolTip.showText(global_pos, text, self)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move (for dragging/resizing signatures or preview)."""
        pos = event.position()
        
        # Always update coordinate tooltip if enabled
        self._show_coordinate_tooltip(event)
        
        if self.resizing_signature is not None:
            # Resizing an existing signature
            sig = self.signatures[self.resizing_signature]
            orig = self.resize_orig_rect
            handle = self.resize_handle
            
            dx = pos.x() - self.resize_start_pos.x()
            dy = pos.y() - self.resize_start_pos.y()
            
            # Update dimensions based on handle
            new_x, new_y = orig["x"], orig["y"]
            new_width, new_height = orig["width"], orig["height"]
            
            if "w" in handle:  # West handles (left side)
                new_x = orig["x"] + dx
                new_width = orig["width"] - dx
            if "e" in handle:  # East handles (right side)
                new_width = orig["width"] + dx
            if "n" in handle:  # North handles (top side)
                new_y = orig["y"] + dy
                new_height = orig["height"] - dy
            if "s" in handle:  # South handles (bottom side)
                new_height = orig["height"] + dy
            
            # Preserve aspect ratio for corner handles
            if handle in ["nw", "ne", "sw", "se"]:
                # Use width as primary dimension
                new_height = new_width / self.resize_aspect_ratio
                if "n" in handle:
                    new_y = orig["y"] + orig["height"] - new_height
            
            # Enforce minimum size
            min_size = 20
            if new_width >= min_size and new_height >= min_size:
                sig["x"] = int(new_x)
                sig["y"] = int(new_y)
                sig["width"] = int(new_width)
                sig["height"] = int(new_height)
                
                # Constrain to page bounds
                if self.pixmap:
                    if sig["x"] < 0:
                        sig["width"] += sig["x"]
                        sig["x"] = 0
                    if sig["y"] < 0:
                        sig["height"] += sig["y"]
                        sig["y"] = 0
                    if sig["x"] + sig["width"] > self.pixmap.width():
                        sig["width"] = self.pixmap.width() - sig["x"]
                    if sig["y"] + sig["height"] > self.pixmap.height():
                        sig["height"] = self.pixmap.height() - sig["y"]
            
            self.update()
            
        elif self.dragging_signature is not None:
            # Dragging an existing signature
            sig = self.signatures[self.dragging_signature]
            
            # Update signature position
            sig["x"] = int(pos.x() - self.drag_offset_x)
            sig["y"] = int(pos.y() - self.drag_offset_y)
            
            # Constrain to page bounds
            if self.pixmap:
                sig["x"] = max(0, min(sig["x"], self.pixmap.width() - sig["width"]))
                sig["y"] = max(0, min(sig["y"], self.pixmap.height() - sig["height"]))
            
            self.update()
            
        elif self.preview_pixmap:
            # Show placement preview
            self.preview_pos = pos
            self.update()
            
        else:
            # Update cursor to show if hovering over a signature or resize handle
            pos_point = pos.toPoint()
            cursor_set = False
            
            for i, sig in enumerate(self.signatures):
                rect = QRectF(sig["x"], sig["y"], sig["width"], sig["height"])
                if rect.contains(pos_point):
                    # Check if over a resize handle (for selected signature)
                    if i == self.selected_signature:
                        handle = self._get_resize_handle_at(pos, sig)
                        if handle:
                            self.setCursor(self._get_cursor_for_handle(handle))
                            cursor_set = True
                            break
                    
                    # Otherwise show move cursor
                    if not cursor_set:
                        self.setCursor(Qt.CursorShape.OpenHandCursor)
                        cursor_set = True
                    break
            
            if not cursor_set:
                self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release (end dragging/resizing)."""
        if self.resizing_signature is not None:
            self.resizing_signature = None
            self.resize_handle = None
            self.resize_start_pos = None
            self.resize_orig_rect = None
            self.resize_aspect_ratio = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self.dragging_signature is not None:
            self.dragging_signature = None
            self.drag_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)


class PDFViewer(QWidget):
    """PDF viewer with navigation controls."""
    
    # Signals
    page_changed = Signal(int)  # Current page number
    signature_placed = Signal(int, int, int, int, int)  # page, x, y, width, height
    _DEFAULT_FIELD_CONFIDENCE_THRESHOLD = 0.8
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer: Optional[PDFRenderer] = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.pending_signature_pixmap: Optional[QPixmap] = None
        self.pending_signature_path: str = ""  # Track signature file path
        # Base DPI used for rendering; must be kept in sync with PDFRenderer.render_page default
        self.base_dpi: int = 150
        # Track all signatures across all pages: {page_num: [sig_dict, ...]}
        self.all_signatures: Dict[int, List[Dict[str, Any]]] = {}
        self.all_field_candidates: Dict[int, List[Dict[str, Any]]] = {}
        self.detector = SignatureFieldDetector()
        self.selected_field_candidate_index: Optional[int] = None
        self.field_auto_place_confidence = self._DEFAULT_FIELD_CONFIDENCE_THRESHOLD
        # Bounded LRU cache of rendered pages, keyed by (page_num, zoom, dpi).
        # Re-rendering a pdfium bitmap at 150 DPI is real, measurable CPU/IO
        # work; users routinely revisit the same page/zoom combination
        # (paging back and forth, toggling between two zoom levels) which
        # previously re-rendered from scratch every time. Cleared whenever a
        # new PDF is opened since entries are page-content-specific.
        self._page_render_cache: "OrderedDict[Tuple[int, float, int], QPixmap]" = OrderedDict()
        self._PAGE_RENDER_CACHE_MAX = 12
        # Holds the in-flight field-detection AsyncRunner; must be kept as an
        # instance attribute so it isn't garbage-collected before it emits.
        self._field_detect_runner: Optional[AsyncRunner] = None
        # Holds the in-flight batch (multi-page) detection AsyncRunner, used
        # by bulk/template signature placement; see detect_fields_for_pages().
        self._batch_detect_runner: Optional[AsyncRunner] = None
        self._setup_ui()
        self.page_view._confidence_threshold = self.field_auto_place_confidence
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Top toolbar
        toolbar = QHBoxLayout()
        
        self.prev_btn = _create_button("◀ Previous", self)
        self.prev_btn.clicked.connect(self.previous_page)
        toolbar.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Page 0 of 0")
        toolbar.addWidget(self.page_label)
        
        self.next_btn = _create_button("Next ▶", self)
        self.next_btn.clicked.connect(self.next_page)
        toolbar.addWidget(self.next_btn)
        
        toolbar.addStretch()
        
        # Zoom control
        toolbar.addWidget(QLabel("Zoom:"))
        self.zoom_combo = QComboBox()
        # Provide document-style options and common percentages
        self.zoom_combo.addItems(["Whole Page", "Page Width", "50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        toolbar.addWidget(self.zoom_combo)

        self.find_fields_btn = _create_button("Find Fields", self)
        self.find_fields_btn.clicked.connect(self.find_signature_fields)
        toolbar.addWidget(self.find_fields_btn)

        self.clear_fields_btn = _create_button("Clear Fields", self)
        self.clear_fields_btn.clicked.connect(self.clear_signature_fields)
        toolbar.addWidget(self.clear_fields_btn)
        
        layout.addLayout(toolbar)
        
        # Scroll area with page view
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.page_view = PDFPageView()
        self.page_view.page_clicked.connect(self._on_page_clicked)
        self.page_view.signature_clicked.connect(self._on_signature_clicked)
        
        self.scroll_area.setWidget(self.page_view)
        layout.addWidget(self.scroll_area)
        
        self._update_controls()
    
    def enable_coordinate_tooltips(self, enabled: bool) -> None:
        """Enable or disable coordinate tooltips in the PDF page view."""
        if self.page_view:
            self.page_view.enable_coordinate_tooltips(enabled)

    def set_field_auto_place_confidence(self, min_confidence: float) -> None:
        """Set the minimum confidence required for auto field placement."""
        self.field_auto_place_confidence = max(0.0, min(1.0, float(min_confidence)))
        self.page_view._confidence_threshold = self.field_auto_place_confidence

    def get_field_auto_place_confidence(self) -> float:
        """Get the current minimum field placement confidence."""
        return self.field_auto_place_confidence
    
    def open_pdf(self, pdf_path: str) -> bool:
        """
        Open a PDF file for viewing.
        
        Returns:
            True if opened successfully
        """
        try:
            # Close existing PDF
            if self.renderer:
                self.renderer.close()
            
            # Open new PDF
            self.renderer = PDFRenderer(pdf_path)
            self.current_page = 0
            self.all_field_candidates.clear()
            self._page_render_cache.clear()
            
            # Default to showing the whole page on open
            self.zoom_combo.setCurrentText("Whole Page")
            
            # Render first page
            self._render_current_page()
            self._update_controls()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF:\n{e}")
            return False
    
    def close_pdf(self) -> None:
        """Close the current PDF."""
        if self.renderer:
            self.renderer.close()
            self.renderer = None
        self.page_view.set_page(None)
        self.page_view.clear_signatures()
        self.page_view.clear_field_candidates()
        self.all_signatures.clear()  # Clear all tracked signatures
        self.all_field_candidates.clear()
        self._page_render_cache.clear()
        self._update_controls()
    
    def _render_current_page(self) -> None:
        """Render the current page, reusing a cached bitmap when available
        for this exact (page, zoom, dpi) combination."""
        if not self.renderer:
            return

        cache_key = (self.current_page, round(self.zoom_level, 4), self.base_dpi)
        pixmap = self._page_render_cache.get(cache_key)
        if pixmap is not None:
            self._page_render_cache.move_to_end(cache_key)
        else:
            pixmap = self.renderer.render_page(self.current_page, scale=self.zoom_level, dpi=self.base_dpi)
            if pixmap is not None:
                self._page_render_cache[cache_key] = pixmap
                if len(self._page_render_cache) > self._PAGE_RENDER_CACHE_MAX:
                    self._page_render_cache.popitem(last=False)

        self.page_view.set_page(pixmap)
        
        # Restore signatures for this page
        self._load_page_signatures()
        self._load_page_field_candidates()
        
        self.page_changed.emit(self.current_page)
    
    def _save_page_signatures(self) -> None:
        """Save current page's signatures before switching pages."""
        if self.current_page not in self.all_signatures:
            self.all_signatures[self.current_page] = []
        else:
            self.all_signatures[self.current_page].clear()
        
        # Copy signatures from page_view
        for sig in self.page_view.signatures:
            self.all_signatures[self.current_page].append(sig.copy())

    def _load_page_signatures(self) -> None:
        """Load signatures for current page from storage."""
        self.page_view.clear_signatures()
        
        if self.current_page in self.all_signatures:
            for sig in self.all_signatures[self.current_page]:
                self.page_view.signatures.append(sig.copy())
            self.page_view.update()

    def restore_signature_placements(self, signatures: List[Dict[str, Any]]) -> None:
        """Restore persisted signature placements into the in-memory viewer state."""
        self.all_signatures.clear()
        for sig in signatures:
            page_num = int(sig.get("page", 0))
            restored = dict(sig)
            if "pixmap" not in restored:
                sig_path = str(restored.get("sig_path", ""))
                restored["pixmap"] = QPixmap(sig_path) if sig_path else QPixmap()
            self.all_signatures.setdefault(page_num, []).append(restored)
        self._load_page_signatures()

    def _load_page_field_candidates(self) -> None:
        """Load stored field candidates for the current page and map them to view coords."""
        self.page_view.clear_field_candidates()
        if not self.renderer or not self.page_view.pixmap:
            return

        if self.current_page not in self.all_field_candidates:
            return

        page_width_pt, page_height_pt = self.renderer.get_page_size(self.current_page)
        pixmap_w = self.page_view.pixmap.width()
        pixmap_h = self.page_view.pixmap.height()
        if page_width_pt <= 0 or page_height_pt <= 0 or pixmap_w <= 0 or pixmap_h <= 0:
            return

        view_candidates: List[Dict[str, Any]] = []
        for candidate in self.all_field_candidates[self.current_page]:
            view_candidates.append(
                {
                    **candidate,
                    "x": int(candidate["x"] * pixmap_w / page_width_pt),
                    "y": int((page_height_pt - (candidate["y"] + candidate["height"])) * pixmap_h / page_height_pt),
                    "width": int(candidate["width"] * pixmap_w / page_width_pt),
                    "height": int(candidate["height"] * pixmap_h / page_height_pt),
                }
            )
        self.page_view.set_field_candidates(view_candidates)
    
    def previous_page(self) -> None:
        """Go to previous page."""
        if not self.renderer:
            return
        
        if self.current_page > 0:
            self._save_page_signatures()  # Save before switching
            self.current_page -= 1
            self._render_current_page()
            self._update_controls()

    def next_page(self) -> None:
        """Go to next page."""
        if not self.renderer:
            return

        if self.current_page < self.renderer.page_count() - 1:
            self._save_page_signatures()  # Save before switching
            self.current_page += 1
            self._render_current_page()
            self._update_controls()

    def goto_page(self, page_num: int) -> None:
        """Go to specific page."""
        if not self.renderer:
            return

        if 0 <= page_num < self.renderer.page_count():
            self._save_page_signatures()  # Save before switching
            self.current_page = page_num
            self._render_current_page()
            self._update_controls()
    
    def _on_zoom_changed(self, text: str) -> None:
        """Handle zoom level change."""
        if text in ("Whole Page", "Fit to Screen"):
            # Backward compatible: treat "Fit to Screen" as "Whole Page"
            self._fit_to_page()
            return
        if text == "Page Width":
            self._fit_to_width()
            return
        try:
            zoom_pct = int(text.rstrip('%'))
            self.zoom_level = zoom_pct / 100.0
            self._render_current_page()
        except ValueError:
            pass
    
    def _fit_to_page(self) -> None:
        """Fit the entire page within the viewport (like Word's "Whole Page")."""
        if not self.renderer:
            return

        page_width_pt, page_height_pt = self.renderer.get_page_size(self.current_page)
        if page_width_pt <= 0 or page_height_pt <= 0:
            return

        # Available area in pixels
        avail_w_px = max(1, self.scroll_area.viewport().width() - 20)
        avail_h_px = max(1, self.scroll_area.viewport().height() - 20)

        # Convert page size (points) to pixels at scale=1 using base DPI
        page_w_px_at_100 = page_width_pt * self.base_dpi / 72.0
        page_h_px_at_100 = page_height_pt * self.base_dpi / 72.0

        # Required scale so the rendered bitmap fits both dimensions
        s_w = avail_w_px / page_w_px_at_100
        s_h = avail_h_px / page_h_px_at_100
        self.zoom_level = max(0.1, min(min(s_w, s_h), 3.0))

        self._render_current_page()

        # Reflect custom mode in dropdown
        self._set_zoom_combo_mode("Whole Page")

    def _fit_to_width(self) -> None:
        """Fit page width to viewport (like Word's "Page Width")."""
        if not self.renderer:
            return

        page_width_pt, page_height_pt = self.renderer.get_page_size(self.current_page)
        if page_width_pt <= 0 or page_height_pt <= 0:
            return

        avail_w_px = max(1, self.scroll_area.viewport().width() - 20)
        page_w_px_at_100 = page_width_pt * self.base_dpi / 72.0
        s_w = avail_w_px / page_w_px_at_100
        self.zoom_level = max(0.1, min(s_w, 3.0))

        self._render_current_page()

        self._set_zoom_combo_mode("Page Width")

    def _set_zoom_combo_mode(self, label: str) -> None:
        """Helper to set the zoom combo without triggering handlers."""
        self.zoom_combo.blockSignals(True)
        idx = self.zoom_combo.findText(label)
        if idx >= 0:
            self.zoom_combo.setCurrentIndex(idx)
        else:
            # Fallback: set closest percentage text
            pct = int(self.zoom_level * 100)
            for i in range(self.zoom_combo.count()):
                t = self.zoom_combo.itemText(i)
                if t.endswith('%') and t.rstrip('%').isdigit() and int(t.rstrip('%')) == pct:
                    self.zoom_combo.setCurrentIndex(i)
                    break
        self.zoom_combo.blockSignals(False)

    def find_signature_fields(
        self,
        *,
        silent: bool = False,
        on_complete: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
    ) -> None:
        """Detect signature-like fields on the current page, asynchronously.

        detect_page() renders the page (pdfium, scale=2.0) and runs OpenCV
        contour heuristics on it — real CPU/IO work. This method dispatches
        it to the global QThreadPool (via the shared AsyncRunner/dispatch
        helpers in desktop_app/widgets/async_utils.py) and returns
        immediately; the button is disabled and shows a wait cursor for the
        duration, restored when the worker completes.

        Args:
            silent: suppress the informational QMessageBox summaries
                ("Fields Detected" / "No Fields Found"). Used by
                place_signature_on_detected_field(), which needs the
                candidates populated but shouldn't interrupt the placement
                flow with a detection-summary dialog.
            on_complete: invoked on the UI thread once detection finishes
                (or fails), with the field-candidate dicts for the current
                page (empty list on failure or "no fields found").
        """
        if not self.renderer:
            QMessageBox.information(self, "No PDF", "Open a PDF first.")
            if on_complete:
                on_complete([])
            return

        self.find_fields_btn.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

        detector = self.detector
        pdf_path = self.renderer.pdf_path
        page_index = self.current_page

        def _do_detect():
            return detector.detect_page(pdf_path, page_index)

        self._field_detect_runner = AsyncRunner(_do_detect)
        self._field_detect_runner.finished.connect(
            lambda candidates: self._on_field_detect_finished(candidates, page_index, silent, on_complete)
        )
        self._field_detect_runner.error.connect(
            lambda exc: self._on_field_detect_error(exc, silent, on_complete)
        )
        dispatch(self._field_detect_runner)

    def _on_field_detect_finished(
        self,
        candidates: List[Any],
        detected_page_index: int,
        silent: bool,
        on_complete: Optional[Callable[[List[Dict[str, Any]]], None]],
    ) -> None:
        self.unsetCursor()
        self.find_fields_btn.setEnabled(True)

        if detected_page_index != self.current_page:
            # The user navigated away from the page this detection was for
            # while it was running; the result is stale for the page now
            # showing. Store it under its own page (still useful once the
            # user returns there) but don't touch the currently-visible
            # page's candidates or fire on_complete for the wrong page.
            self.all_field_candidates[detected_page_index] = [
                c.as_dict() for c in candidates if c.page_index == detected_page_index
            ]
            if on_complete:
                on_complete([])
            return

        candidate_dicts = [c.as_dict() for c in candidates if c.page_index == self.current_page]
        self.all_field_candidates[self.current_page] = candidate_dicts
        self._load_page_field_candidates()
        self.set_selected_field_candidate_index(None)

        if not silent:
            if not candidates:
                QMessageBox.information(self, "No Fields Found", "No likely signature fields were detected on this page.")
            else:
                thresholded = [c for c in candidates if c.confidence >= self.field_auto_place_confidence]
                shown_count = len(candidates)
                shown_above = len(thresholded)
                if shown_count and shown_above < shown_count:
                    label = f"\n\n{shown_above}/{shown_count} candidate(s) above auto-placement threshold ({self.field_auto_place_confidence:.0%})."
                else:
                    label = ""

                label_counts = {}
                for candidate in candidates:
                    label_counts[candidate.field_type] = label_counts.get(candidate.field_type, 0) + 1

                summary = ", ".join(f"{name.replace('_', ' ')} x{count}" for name, count in sorted(label_counts.items()))
                QMessageBox.information(
                    self,
                    "Fields Detected",
                    f"Detected {len(candidates)} likely field(s) on page {self.current_page + 1}.\n\n{summary}{label}",
                )

        if on_complete:
            on_complete(self.page_view.field_candidates)

    def _on_field_detect_error(
        self,
        exc: Exception,
        silent: bool,
        on_complete: Optional[Callable[[List[Dict[str, Any]]], None]],
    ) -> None:
        self.unsetCursor()
        self.find_fields_btn.setEnabled(True)
        if not silent:
            QMessageBox.warning(self, "Field Detection Failed", f"Unable to detect fields:\n{exc}")
        if on_complete:
            on_complete([])

    def place_signature_on_detected_field(
        self, on_complete: Optional[Callable[[bool], None]] = None
    ) -> Optional[bool]:
        """Place the pending signature into the best detected field on the current page.

        Returns True/False synchronously when field candidates are already
        available for the current page (the common case: the user already
        ran "Find Fields", or a previous detection/navigation cached them).
        If no candidates are cached yet, detection has to run first — this
        dispatches it asynchronously (see find_signature_fields) and returns
        None immediately; the actual placement result is delivered via
        `on_complete` once detection finishes. `on_complete` is also called
        in the synchronous-result case, so callers can use a single code
        path regardless of which branch was taken.
        """
        if not self.pending_signature_pixmap:
            QMessageBox.information(self, "No Signature Selected", "Select a signature first.")
            if on_complete:
                on_complete(False)
            return False

        if self.page_view.field_candidates:
            result = self._place_on_best_field_candidate()
            if on_complete:
                on_complete(result)
            return result

        def _after_detect(_candidates: List[Dict[str, Any]]) -> None:
            result = self._place_on_best_field_candidate() if self.page_view.field_candidates else False
            if on_complete:
                on_complete(result)

        self.find_signature_fields(silent=True, on_complete=_after_detect)
        return None

    def _place_on_best_field_candidate(self) -> bool:
        """Place the pending signature into the best already-detected candidate.

        Precondition: self.page_view.field_candidates is non-empty. Split
        out of place_signature_on_detected_field so both the synchronous
        (already-cached) and asynchronous (detect-then-place) paths share
        one placement implementation.
        """
        field = self._choose_field_candidate()
        if field is None:
            QMessageBox.warning(
                self,
                "Confidence Too Low",
                "No field meets the minimum confidence threshold for auto placement.\n\n"
                "Move the signature manually on this page, or place a selected field from the list first.",
            )
            return False

        return self._place_signature_in_rect(field)

    def place_signature_on_field(self, field: Dict[str, Any]) -> bool:
        """Place the pending signature into a specific detected field."""
        if not self.pending_signature_pixmap:
            QMessageBox.information(self, "No Signature Selected", "Select a signature first.")
            return False
        return self._place_signature_in_rect(field)

    def set_selected_field_candidate_index(self, index: Optional[int]) -> None:
        """Remember which detected field the user selected in the review panel."""
        self.selected_field_candidate_index = index
        self.page_view.selected_field_candidate_index = index
        self.page_view.update()

    def get_selected_field_candidate(self) -> Optional[Dict[str, Any]]:
        """Return currently selected field candidate if valid."""
        if self.selected_field_candidate_index is None:
            return None
        if 0 <= self.selected_field_candidate_index < len(self.page_view.field_candidates):
            return self.page_view.field_candidates[self.selected_field_candidate_index]
        return None

    def _choose_field_candidate(self) -> Optional[Dict[str, Any]]:
        """Choose the best detected field or the user-selected one."""
        selected = self.get_selected_field_candidate()
        if selected is not None:
            return selected

        field_priority = {"signature_box": 0, "signature_line": 1, "field_box": 2, "initials_box": 3}
        candidates = sorted(
            self.page_view.field_candidates,
            key=lambda item: (
                field_priority.get(item.get("field_type", ""), 99),
                -float(item.get("confidence", 0.0)),
                -float(item.get("width", 0.0)) * float(item.get("height", 0.0)),
            ),
        )
        if not candidates:
            return None

        candidate = candidates[0]
        if float(candidate.get("confidence", 0.0)) < self.field_auto_place_confidence:
            return None

        return candidate

    def _compute_signature_rect_in_field(self, field: Dict[str, Any], sig_w: int, sig_h: int) -> Tuple[int, int, int, int]:
        """Compute placement rect for a signature inside a detected field."""
        aspect = sig_w / max(sig_h, 1)
        field_x = float(field["x"])
        field_y = float(field["y"])
        field_w = float(field["width"])
        field_h = float(field["height"])

        if field_w / max(field_h, 1.0) >= aspect:
            height = max(20, int(field_h))
            width = max(20, int(height * aspect))
        else:
            width = max(40, int(field_w))
            height = max(20, int(width / aspect))

        if field_w >= 20:
            width = min(width, int(field_w))
        if field_h >= 20:
            height = min(height, int(field_h))
        if width <= 0 or height <= 0:
            width = max(40, int(field_w))
            height = max(20, int(field_h))

        x = int(field_x + max(0.0, (field_w - width) / 2.0))
        y = int(field_y + max(0.0, (field_h - height) / 2.0))
        return x, y, width, height

    def _detect_signature_fields_silent(self) -> List[Dict[str, Any]]:
        """Detect fields on the current page without showing UI messages."""
        if not self.renderer:
            return []

        try:
            candidates = self.detector.detect_page(self.renderer.pdf_path, self.current_page)
        except Exception:
            self.all_field_candidates[self.current_page] = []
            self.page_view.clear_field_candidates()
            return []

        self.all_field_candidates[self.current_page] = [c.as_dict() for c in candidates if c.page_index == self.current_page]
        self._load_page_field_candidates()
        self.set_selected_field_candidate_index(None)
        return self.page_view.field_candidates

    def detect_fields_for_pages(
        self,
        page_indices: List[int],
        on_complete: Callable[[Dict[int, List[Dict[str, Any]]]], None],
    ) -> None:
        """Detect signature fields for multiple pages in a single background pass.

        Bulk/template signature placement in "adaptive" mode previously
        called `_detect_signature_fields_silent()` once per target page
        inside a synchronous UI-thread `for` loop (see
        `desktop_app/views/main_window_parts/pdf.py`'s
        `_on_pdf_template_apply_to_pages` and the bulk branch of
        `_on_pdf_signature_placed`) — for N pages, that's N sequential
        blocking pdfium-render + OpenCV calls, worse than the single-page
        "Find Fields" button case. This dispatches all N detections on one
        QThreadPool worker instead, so the UI thread is only blocked once
        (not N times) for the whole batch.

        Per-page failures are isolated (logged, empty result for that page)
        and never abort the batch — one unreadable/corrupt page must not
        prevent placement on the others.

        `on_complete` is invoked on the UI thread with
        `self.all_field_candidates` (already updated in place) once the
        batch finishes, or with `{}` immediately if there's no open PDF.
        """
        if not self.renderer:
            on_complete({})
            return

        detector = self.detector
        pdf_path = self.renderer.pdf_path
        # De-duplicate while preserving order: a caller may legitimately
        # pass the same page twice (e.g. a page selected by both a
        # user-defined range and a "current page" default).
        unique_pages = list(dict.fromkeys(page_indices))

        def _do_batch_detect() -> Dict[int, List[Any]]:
            results: Dict[int, List[Any]] = {}
            for page_index in unique_pages:
                try:
                    results[page_index] = detector.detect_page(pdf_path, page_index)
                except Exception as exc:
                    LOG.warning("Batch field detection failed for page %s: %s", page_index, exc)
                    results[page_index] = []
            return results

        def _on_batch_finished(results: Dict[int, List[Any]]) -> None:
            for page_index, candidates in results.items():
                self.all_field_candidates[page_index] = [
                    c.as_dict() for c in candidates if c.page_index == page_index
                ]
            if self.current_page in results:
                self._load_page_field_candidates()
            on_complete(dict(self.all_field_candidates))

        def _on_batch_error(exc: Exception) -> None:
            LOG.error("Batch field detection harness failed: %s", exc)
            on_complete({})

        self._batch_detect_runner = AsyncRunner(_do_batch_detect)
        self._batch_detect_runner.finished.connect(_on_batch_finished)
        self._batch_detect_runner.error.connect(_on_batch_error)
        dispatch(self._batch_detect_runner)

    def build_scaled_signature_rect(
        self,
        x_ratio: float,
        y_ratio: float,
        width_ratio: float,
        height_ratio: float,
    ) -> Optional[Tuple[int, int, int, int]]:
        """Build a signature rect based on normalized coordinates for the current page."""
        if not self.page_view.pixmap:
            return None

        page_width = self.page_view.pixmap.width()
        page_height = self.page_view.pixmap.height()

        width_ratio = min(1.0, max(0.0, width_ratio))
        height_ratio = min(1.0, max(0.0, height_ratio))
        x_ratio = min(1.0, max(0.0, x_ratio))
        y_ratio = min(1.0, max(0.0, y_ratio))

        x = int(round(x_ratio * page_width))
        y = int(round(y_ratio * page_height))
        width = max(1, int(round(width_ratio * page_width)))
        height = max(1, int(round(height_ratio * page_height)))

        x = max(0, min(x, page_width - width))
        y = max(0, min(y, page_height - height))
        return x, y, width, height

    def _place_signature_in_rect(self, field: Dict[str, Any]) -> bool:
        sig_w = max(1, int(self.pending_signature_pixmap.width()))  # type: ignore[union-attr]
        sig_h = max(1, int(self.pending_signature_pixmap.height()))  # type: ignore[union-attr]
        x, y, width, height = self._compute_signature_rect_in_field(field, sig_w, sig_h)

        self.page_view.add_signature_overlay(
            x,
            y,
            width,
            height,
            self.pending_signature_pixmap,  # type: ignore[arg-type]
            self.pending_signature_path,
        )
        self.signature_placed.emit(self.current_page, x, y, width, height)
        self.pending_signature_pixmap = None
        self.pending_signature_path = ""
        self.page_view.set_preview_signature(None)
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        return True

    def place_signature_in_rect(self, x: int, y: int, width: int, height: int) -> bool:
        """Place pending signature into an explicit rectangle and emit placement signal."""
        if not self.pending_signature_pixmap:
            return False

        if self.page_view.pixmap:
            x = max(0, min(x, self.page_view.pixmap.width() - width))
            y = max(0, min(y, self.page_view.pixmap.height() - height))
        width = max(1, width)
        height = max(1, height)

        self.page_view.add_signature_overlay(
            x,
            y,
            width,
            height,
            self.pending_signature_pixmap,  # type: ignore[arg-type]
            self.pending_signature_path,
        )
        self.signature_placed.emit(self.current_page, x, y, width, height)
        self.pending_signature_pixmap = None
        self.pending_signature_path = ""
        self.page_view.set_preview_signature(None)
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        return True

    def build_field_anchor_signature_rect(self, field: Dict[str, Any], x_ratio: float, y_ratio: float) -> Optional[Tuple[int, int, int, int]]:
        """Build a field-constrained placement rect anchored near a normalized point."""
        if not self.page_view.pixmap:
            return None

        # Keep backward compatibility for callers that pass an explicit field:
        # prefer the provided field when available, otherwise snap to the
        # nearest detected field around the normalized anchor.
        if field:
            try:
                field_rect = self._scale_rect_for_signature(field)
                if field_rect is not None:
                    return field_rect
            except Exception:
                pass

        return self.build_field_anchor_signature_rect_from_ratio(x_ratio, y_ratio)

    def build_field_anchor_signature_rect_from_ratio(
        self,
        x_ratio: float,
        y_ratio: float,
        sig_pixmap: Optional[QPixmap] = None,
    ) -> Optional[Tuple[int, int, int, int]]:
        """Build the best field-constrained rect from a normalized anchor."""
        if not self.page_view.pixmap:
            return None

        if not self.page_view.field_candidates:
            return None

        if not sig_pixmap and not self.pending_signature_pixmap:
            return None

        candidates = self.page_view.field_candidates
        target_w = float(self.page_view.pixmap.width())
        target_h = float(self.page_view.pixmap.height())
        anchor_x = x_ratio * target_w
        anchor_y = y_ratio * target_h

        best_distance = None
        best_field: Optional[Dict[str, Any]] = None

        for candidate in candidates:
            conf = float(candidate.get("confidence", 0.0))
            if conf < self.field_auto_place_confidence:
                continue
            cx = candidate.get("x", 0.0) + candidate.get("width", 0.0) / 2
            cy = candidate.get("y", 0.0) + candidate.get("height", 0.0) / 2
            dist = (cx - anchor_x) ** 2 + (cy - anchor_y) ** 2
            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_field = candidate

        if not best_field:
            return None

        sig_source = sig_pixmap or self.pending_signature_pixmap
        if not sig_source:
            return None
        sig_w = max(1, int(sig_source.width()))
        sig_h = max(1, int(sig_source.height()))
        return self._compute_signature_rect_in_field(best_field, sig_w, sig_h)

    def _scale_rect_for_signature(self, field: Dict[str, Any]) -> Optional[Tuple[int, int, int, int]]:
        """Scale a candidate field by pending signature size and keep it centered."""
        if not self.pending_signature_pixmap:
            return None
        sig_w = max(1, int(self.pending_signature_pixmap.width()))
        sig_h = max(1, int(self.pending_signature_pixmap.height()))
        return self._compute_signature_rect_in_field(field, sig_w, sig_h)

    def clear_signature_fields(self) -> None:
        """Clear detected field overlays for the current document."""
        self.page_view.clear_field_candidates()
        self.all_field_candidates.clear()
        if self.renderer:
            self._render_current_page()
    
    def _update_controls(self) -> None:
        """Update navigation controls state."""
        if not self.renderer:
            self.page_label.setText("No PDF loaded")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
        
        total = self.renderer.page_count()
        self.page_label.setText(f"Page {self.current_page + 1} of {total}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total - 1)
    
    def set_signature_for_placement(self, sig_pixmap: QPixmap, sig_path: str = "") -> None:
        """
        Set a signature for placement (user will click on PDF to place).
        
        Args:
            sig_pixmap: Signature image to place
            sig_path: Path to signature image file (for PDF embedding)
        """
        self.pending_signature_pixmap = sig_pixmap
        self.pending_signature_path = sig_path
        self.page_view.set_preview_signature(sig_pixmap)  # Enable preview
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
    
    def _on_page_clicked(self, pos: QPointF) -> None:
        """Handle click on PDF page."""
        if not self.pending_signature_pixmap:
            return

        if self.page_view.field_candidates:
            if self.place_signature_on_detected_field():
                return
        
        # Place signature at clicked position
        # Default size: 150x50 pixels (typical signature size)
        width, height = 150, 50
        x = int(pos.x() - width / 2)  # Center on click
        y = int(pos.y() - height / 2)
        
        # Add signature overlay to current page with path
        self.page_view.add_signature_overlay(
            x, y, width, height, 
            self.pending_signature_pixmap,
            self.pending_signature_path
        )
        
        # Emit signal for tracking
        self.signature_placed.emit(self.current_page, x, y, width, height)
        
        # Clear pending signature and preview
        self.pending_signature_pixmap = None
        self.pending_signature_path = ""
        self.page_view.set_preview_signature(None)  # Disable preview
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def _on_signature_clicked(self, index: int) -> None:
        """Handle click on existing signature (for removal/editing)."""
        # This is now handled in PDFPageView's mousePressEvent for dragging
        # Only called for actual removal requests
        pass
    
    def get_placed_signatures(self) -> List[Dict[str, Any]]:
        """
        Get all placed signatures across all pages.
        
        Returns:
            List of signature dicts with page, position, size, and image path
        """
        # Save current page signatures first
        self._save_page_signatures()
        
        # Collect all signatures from all pages
        all_sigs = []
        for page_num, sigs in self.all_signatures.items():
            for sig in sigs:
                all_sigs.append({
                    "page": page_num,
                    "x": sig["x"],
                    "y": sig["y"],
                    "width": sig["width"],
                    "height": sig["height"],
                    "sig_path": sig.get("sig_path", ""),
                    # Provide metadata so signer can convert from pixels to points
                    "units": "px",
                    "dpi": self.base_dpi,
                    "scale": self.zoom_level,
                })
        
        return all_sigs
