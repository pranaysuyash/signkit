# PDF Feature Implementation Plan

## Overview

This document details the step-by-step implementation plan for adding PDF viewing, signature placement, and audit logging to the Signature Extractor desktop app **without affecting existing functionality**.

---

## Goals

1. **Preserve existing features**: Image extraction, signature library, all current workflows remain unchanged
2. **Add PDF viewer**: Users can open and view PDF documents
3. **Enable signature placement**: Users can drag/drop saved signatures from library onto PDF pages
4. **Save signed PDFs**: Generate new PDF with signatures embedded
5. **Audit logging**: Track all PDF operations (open, sign, save) for compliance

---

## Architecture Overview

```
Desktop App (PySide6)
├─ Existing: Signature Extraction Workflow (UNCHANGED)
│   ├─ Open Image → Upload → Select Region → Extract → Save to Library
│   └─ Library Management (view, delete, export)
│
└─ NEW: PDF Signing Workflow
    ├─ Open PDF → View Pages
    ├─ Select Signature from Library
    ├─ Place Signature on PDF (click/drag)
    ├─ Save Signed PDF
    └─ Audit Log (all operations tracked)
```

---

## Phase 1: Foundation & Infrastructure

### 1.1 Install PDF Dependencies

**Action**: Add pypdfium2 and pikepdf to requirements

**File**: `desktop_app/requirements.txt`

```diff
PySide6>=6.5.0
requests>=2.31.0
python-dotenv>=1.0.0
Pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0
+pypdfium2>=4.26.0
+pikepdf>=8.10.0
```

**Verification**:

```bash
pip install -r desktop_app/requirements.txt
python -c "import pypdfium2; import pikepdf; print('✓ PDF libraries installed')"
```

**Impact**: None on existing features (lazy loading)

---

### 1.2 Create PDF Module Structure

**Action**: Create new module for PDF operations

**Files to create**:

```
desktop_app/pdf/
├─ __init__.py
├─ viewer.py          # PDF viewing widget
├─ signer.py          # PDF signature embedding
├─ renderer.py        # Page rendering utilities
└─ audit.py           # Audit logging for PDF operations
```

**Why separate module**: Keeps PDF code isolated, easy to maintain/test

---

### 1.3 Extend Session State

**Action**: Add PDF-specific state without breaking existing state

**File**: `desktop_app/state/session.py`

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class PDFState:
    """State for PDF viewing and signing operations."""
    current_pdf_path: Optional[str] = None
    current_page: int = 0
    total_pages: int = 0
    zoom_level: float = 1.0
    placed_signatures: List[Dict[str, Any]] = field(default_factory=list)
    # placed_signatures format: [{"page": 0, "sig_path": "...", "x": 100, "y": 200, "width": 150, "height": 50}, ...]


@dataclass
class SessionState:
    # EXISTING FIELDS (UNCHANGED)
    access_token: Optional[str] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None  # image id returned by upload
    last_request: Dict[str, Any] = field(default_factory=dict)

    # NEW: PDF state (initialized to None, created on-demand)
    pdf_state: Optional[PDFState] = None

    def auth_header(self) -> Dict[str, str]:
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    # NEW: PDF state management
    def init_pdf_state(self) -> None:
        """Initialize PDF state if not already present."""
        if self.pdf_state is None:
            self.pdf_state = PDFState()

    def clear_pdf_state(self) -> None:
        """Clear PDF state (when closing PDF)."""
        self.pdf_state = None
```

**Impact**: Zero impact on existing code (new optional field)

---

### 1.4 Create PDF Storage Directory

**Action**: Extend library storage to handle PDFs

**File**: `desktop_app/pdf/storage.py`

```python
"""Storage management for PDF documents and audit logs."""

import os
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
from pathlib import Path


# Use existing app directory structure
APP_DIR = os.path.join(os.path.expanduser("~"), ".signature_extractor")
PDF_DIR = os.path.join(APP_DIR, "pdfs")
AUDIT_DIR = os.path.join(APP_DIR, "audit_logs")


def ensure_pdf_dir() -> str:
    """Ensure PDF output directory exists."""
    os.makedirs(PDF_DIR, exist_ok=True)
    return PDF_DIR


def ensure_audit_dir() -> str:
    """Ensure audit log directory exists."""
    os.makedirs(AUDIT_DIR, exist_ok=True)
    return AUDIT_DIR


def auto_pdf_filename(original_name: str = "document") -> str:
    """Generate timestamped filename for saved PDF."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(original_name).stem
    return f"{base}_signed_{ts}.pdf"


def save_signed_pdf(pdf_bytes: bytes, original_name: str = "document.pdf") -> str:
    """
    Save signed PDF to library.

    Args:
        pdf_bytes: PDF file bytes
        original_name: Original PDF filename (for naming)

    Returns:
        Full path to saved PDF
    """
    ensure_pdf_dir()
    fname = auto_pdf_filename(original_name)
    path = os.path.join(PDF_DIR, fname)
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    return path


@dataclass
class AuditLogEntry:
    """Single audit log entry."""
    timestamp: str  # ISO format
    operation: str  # "open_pdf", "place_signature", "save_pdf", "delete_signature"
    pdf_path: str
    details: dict  # Operation-specific details
    user_email: Optional[str] = None


class AuditLogger:
    """Audit logger for PDF operations."""

    def __init__(self, pdf_path: str, user_email: Optional[str] = None):
        self.pdf_path = pdf_path
        self.user_email = user_email
        ensure_audit_dir()

        # Create log file per PDF
        pdf_name = Path(pdf_path).stem
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(AUDIT_DIR, f"{pdf_name}_{ts}.jsonl")

    def log(self, operation: str, details: dict) -> None:
        """
        Log an operation.

        Args:
            operation: Operation type (e.g., "open_pdf", "place_signature")
            details: Operation-specific details
        """
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            pdf_path=self.pdf_path,
            details=details,
            user_email=self.user_email
        )

        # Append to JSONL file (one JSON object per line)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def log_open(self) -> None:
        """Log PDF opened."""
        self.log("open_pdf", {
            "action": "User opened PDF for viewing/signing"
        })

    def log_place_signature(self, page: int, sig_path: str, x: int, y: int,
                           width: int, height: int) -> None:
        """Log signature placement."""
        self.log("place_signature", {
            "page": page,
            "signature_file": Path(sig_path).name,
            "position": {"x": x, "y": y},
            "size": {"width": width, "height": height}
        })

    def log_remove_signature(self, page: int, index: int) -> None:
        """Log signature removal."""
        self.log("remove_signature", {
            "page": page,
            "signature_index": index
        })

    def log_save(self, output_path: str, signature_count: int) -> None:
        """Log PDF saved."""
        self.log("save_pdf", {
            "output_path": output_path,
            "signature_count": signature_count,
            "output_size_bytes": os.path.getsize(output_path)
        })

    def log_error(self, error_type: str, error_msg: str) -> None:
        """Log an error."""
        self.log("error", {
            "error_type": error_type,
            "error_message": error_msg
        })


def get_audit_logs_for_pdf(pdf_path: str) -> List[AuditLogEntry]:
    """
    Retrieve audit logs for a specific PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of audit log entries
    """
    ensure_audit_dir()
    pdf_name = Path(pdf_path).stem

    # Find all log files for this PDF
    logs = []
    for fname in os.listdir(AUDIT_DIR):
        if fname.startswith(pdf_name) and fname.endswith(".jsonl"):
            log_path = os.path.join(AUDIT_DIR, fname)
            with open(log_path, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        logs.append(AuditLogEntry(**data))
                    except Exception:
                        continue

    return sorted(logs, key=lambda x: x.timestamp)


def export_audit_logs(pdf_path: str, output_path: str) -> None:
    """
    Export audit logs to JSON file.

    Args:
        pdf_path: Path to PDF file
        output_path: Path to save exported logs
    """
    logs = get_audit_logs_for_pdf(pdf_path)
    with open(output_path, "w") as f:
        json.dumps([asdict(log) for log in logs], indent=2)
```

**Impact**: None on existing signature library (separate directory)

---

## Phase 2: PDF Viewer Widget

### 2.1 Create PDF Renderer

**Action**: Create utility to render PDF pages to QPixmap

**File**: `desktop_app/pdf/renderer.py`

```python
"""PDF page rendering utilities using pypdfium2."""

from typing import Optional, Tuple
from pathlib import Path

import pypdfium2 as pdfium
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


class PDFRenderer:
    """Render PDF pages to QPixmap for display."""

    def __init__(self, pdf_path: str):
        """
        Initialize renderer with PDF file.

        Args:
            pdf_path: Path to PDF file

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF cannot be opened
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            self.pdf = pdfium.PdfDocument(pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}")

        self.pdf_path = pdf_path

    def page_count(self) -> int:
        """Get total number of pages."""
        return len(self.pdf)

    def get_page_size(self, page_num: int) -> Tuple[float, float]:
        """
        Get page dimensions in points (1/72 inch).

        Args:
            page_num: Page number (0-indexed)

        Returns:
            Tuple of (width, height) in points
        """
        page = self.pdf[page_num]
        width = page.get_width()
        height = page.get_height()
        return (width, height)

    def render_page(self, page_num: int, scale: float = 1.0,
                    dpi: int = 150) -> Optional[QPixmap]:
        """
        Render a PDF page to QPixmap.

        Args:
            page_num: Page number (0-indexed)
            scale: Zoom scale (1.0 = 100%)
            dpi: Rendering DPI (higher = better quality, slower)

        Returns:
            QPixmap or None if rendering fails
        """
        if page_num < 0 or page_num >= len(self.pdf):
            return None

        try:
            page = self.pdf[page_num]

            # Calculate render size
            width_pt, height_pt = page.get_width(), page.get_height()
            width_px = int(width_pt * dpi / 72 * scale)
            height_px = int(height_pt * dpi / 72 * scale)

            # Render to bitmap
            bitmap = page.render(
                scale=scale * dpi / 72,
                rotation=0,
                crop=(0, 0, 0, 0),
            )

            # Convert to PIL Image then QImage
            pil_image = bitmap.to_pil()

            # Convert PIL to QImage
            data = pil_image.tobytes("raw", "RGB")
            qimage = QImage(
                data,
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format_RGB888
            )

            # Convert to QPixmap
            return QPixmap.fromImage(qimage)

        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return None

    def close(self) -> None:
        """Close the PDF document."""
        if hasattr(self, 'pdf'):
            try:
                self.pdf.close()
            except Exception:
                pass

    def __del__(self):
        self.close()
```

**Impact**: None (new module, not imported anywhere yet)

---

### 2.2 Create PDF Viewer Widget

**Action**: Create scrollable PDF viewer widget

**File**: `desktop_app/pdf/viewer.py`

```python
"""PDF viewer widget with page navigation and zoom."""

from typing import Optional, List, Dict, Any
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QTransform
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QComboBox, QMessageBox, QSizePolicy
)

from desktop_app.pdf.renderer import PDFRenderer


class PDFPageView(QWidget):
    """Widget to display a single PDF page with signature overlays."""

    signature_clicked = Signal(int)  # Emits signature index
    page_clicked = Signal(QPointF)   # Emits click position

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap: Optional[QPixmap] = None
        self.signatures: List[Dict[str, Any]] = []  # [{"x": 100, "y": 200, "width": 150, "height": 50, "pixmap": QPixmap}, ...]
        self.setMinimumSize(400, 500)

    def set_page(self, pixmap: Optional[QPixmap]) -> None:
        """Set the PDF page to display."""
        self.pixmap = pixmap
        if pixmap:
            self.setFixedSize(pixmap.size())
        self.update()

    def add_signature_overlay(self, x: int, y: int, width: int, height: int,
                             sig_pixmap: QPixmap) -> int:
        """
        Add a signature overlay at specified position.

        Returns:
            Index of added signature
        """
        self.signatures.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "pixmap": sig_pixmap
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

    def paintEvent(self, event):
        """Draw PDF page and signature overlays."""
        painter = QPainter(self)

        # Draw PDF page
        if self.pixmap:
            painter.drawPixmap(0, 0, self.pixmap)

        # Draw signature overlays
        for sig in self.signatures:
            # Draw signature image
            scaled_sig = sig["pixmap"].scaled(
                sig["width"], sig["height"],
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            painter.drawPixmap(sig["x"], sig["y"], scaled_sig)

            # Draw selection border
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(sig["x"], sig["y"], sig["width"], sig["height"])

    def mousePressEvent(self, event):
        """Handle mouse click (for signature selection or placement)."""
        pos = event.position().toPoint()

        # Check if clicked on existing signature
        for i, sig in enumerate(self.signatures):
            rect = QRectF(sig["x"], sig["y"], sig["width"], sig["height"])
            if rect.contains(pos):
                self.signature_clicked.emit(i)
                return

        # Otherwise, emit page click for new signature placement
        self.page_clicked.emit(event.position())


class PDFViewer(QWidget):
    """PDF viewer with navigation controls."""

    # Signals
    page_changed = Signal(int)  # Current page number
    signature_placed = Signal(int, int, int, int, int)  # page, x, y, width, height

    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer: Optional[PDFRenderer] = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.pending_signature_pixmap: Optional[QPixmap] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Top toolbar
        toolbar = QHBoxLayout()

        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.previous_page)
        toolbar.addWidget(self.prev_btn)

        self.page_label = QLabel("Page 0 of 0")
        toolbar.addWidget(self.page_label)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_page)
        toolbar.addWidget(self.next_btn)

        toolbar.addStretch()

        # Zoom control
        toolbar.addWidget(QLabel("Zoom:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        toolbar.addWidget(self.zoom_combo)

        layout.addLayout(toolbar)

        # Scroll area with page view
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.page_view = PDFPageView()
        self.page_view.page_clicked.connect(self._on_page_clicked)
        self.page_view.signature_clicked.connect(self._on_signature_clicked)

        self.scroll_area.setWidget(self.page_view)
        layout.addWidget(self.scroll_area)

        self._update_controls()

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
        self._update_controls()

    def _render_current_page(self) -> None:
        """Render the current page."""
        if not self.renderer:
            return

        pixmap = self.renderer.render_page(self.current_page, scale=self.zoom_level)
        self.page_view.set_page(pixmap)
        self.page_changed.emit(self.current_page)

    def previous_page(self) -> None:
        """Go to previous page."""
        if not self.renderer:
            return

        if self.current_page > 0:
            self.current_page -= 1
            self._render_current_page()
            self._update_controls()

    def next_page(self) -> None:
        """Go to next page."""
        if not self.renderer:
            return

        if self.current_page < self.renderer.page_count() - 1:
            self.current_page += 1
            self._render_current_page()
            self._update_controls()

    def goto_page(self, page_num: int) -> None:
        """Go to specific page."""
        if not self.renderer:
            return

        if 0 <= page_num < self.renderer.page_count():
            self.current_page = page_num
            self._render_current_page()
            self._update_controls()

    def _on_zoom_changed(self, text: str) -> None:
        """Handle zoom level change."""
        try:
            zoom_pct = int(text.rstrip('%'))
            self.zoom_level = zoom_pct / 100.0
            self._render_current_page()
        except ValueError:
            pass

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

    def set_signature_for_placement(self, sig_pixmap: QPixmap) -> None:
        """
        Set a signature for placement (user will click on PDF to place).

        Args:
            sig_pixmap: Signature image to place
        """
        self.pending_signature_pixmap = sig_pixmap
        self.setCursor(Qt.CrossCursor)

    def _on_page_clicked(self, pos: QPointF) -> None:
        """Handle click on PDF page."""
        if not self.pending_signature_pixmap:
            return

        # Place signature at clicked position
        # Default size: 150x50 pixels (typical signature size)
        width, height = 150, 50
        x = int(pos.x() - width / 2)  # Center on click
        y = int(pos.y() - height / 2)

        # Add signature overlay to current page
        self.page_view.add_signature_overlay(x, y, width, height, self.pending_signature_pixmap)

        # Emit signal for tracking
        self.signature_placed.emit(self.current_page, x, y, width, height)

        # Clear pending signature
        self.pending_signature_pixmap = None
        self.setCursor(Qt.ArrowCursor)

    def _on_signature_clicked(self, index: int) -> None:
        """Handle click on existing signature (for removal/editing)."""
        reply = QMessageBox.question(
            self, "Remove Signature",
            "Do you want to remove this signature?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.page_view.remove_signature(index)

    def get_placed_signatures(self) -> List[Dict[str, Any]]:
        """
        Get all placed signatures on current page.

        Returns:
            List of signature dicts with position and size
        """
        return [
            {
                "page": self.current_page,
                "x": sig["x"],
                "y": sig["y"],
                "width": sig["width"],
                "height": sig["height"]
            }
            for sig in self.page_view.signatures
        ]
```

**Impact**: None (new widget, not integrated into main window yet)

---

## Phase 3: PDF Signer (Save Functionality)

### 3.1 Create PDF Signer

**Action**: Create utility to embed signatures into PDF

**File**: `desktop_app/pdf/signer.py`

```python
"""PDF signing utilities using pikepdf."""

import io
from typing import List, Dict, Any
from pathlib import Path

import pikepdf
from PIL import Image as PILImage
from PySide6.QtGui import QPixmap


class PDFSigner:
    """Embed signature images into PDF documents."""

    def __init__(self, input_pdf_path: str):
        """
        Initialize signer with input PDF.

        Args:
            input_pdf_path: Path to original PDF file

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF cannot be opened
        """
        if not Path(input_pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {input_pdf_path}")

        try:
            self.pdf = pikepdf.open(input_pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}")

        self.input_path = input_pdf_path

    def add_signature(self, page_num: int, sig_image_path: str,
                     x: float, y: float, width: float, height: float) -> None:
        """
        Add a signature image to a specific page.

        Args:
            page_num: Page number (0-indexed)
            sig_image_path: Path to signature image file
            x, y: Position in PDF coordinates (bottom-left origin)
            width, height: Signature dimensions in PDF points

        Note: PDF coordinate system has origin at bottom-left,
              while Qt has origin at top-left. Caller must convert.
        """
        if page_num < 0 or page_num >= len(self.pdf.pages):
            raise ValueError(f"Invalid page number: {page_num}")

        page = self.pdf.pages[page_num]

        # Load signature image
        sig_image = PILImage.open(sig_image_path)

        # Convert to RGB if necessary
        if sig_image.mode != 'RGB':
            sig_image = sig_image.convert('RGB')

        # Create image object in PDF
        sig_pdf_image = pikepdf.PdfImage(sig_image)

        # Get page dimensions
        mediabox = page.MediaBox
        page_height = float(mediabox[3] - mediabox[1])

        # Create form XObject for the signature
        # PDF uses bottom-left origin, so we need to flip Y coordinate
        y_pdf = page_height - y - height

        # Add image to page resources
        if '/Resources' not in page:
            page.Resources = pikepdf.Dictionary()
        if '/XObject' not in page.Resources:
            page.Resources.XObject = pikepdf.Dictionary()

        # Generate unique name for signature
        sig_name = f"/Sig{len(page.Resources.XObject)}"
        page.Resources.XObject[sig_name] = sig_pdf_image

        # Add drawing commands to page content stream
        drawing_commands = f"""
        q
        {width} 0 0 {height} {x} {y_pdf} cm
        {sig_name} Do
        Q
        """

        # Append to existing content stream
        if '/Contents' in page:
            existing_content = page.Contents.read_bytes()
            new_content = existing_content + drawing_commands.encode('latin-1')
            page.Contents = pikepdf.Stream(self.pdf, new_content)
        else:
            page.Contents = pikepdf.Stream(self.pdf, drawing_commands.encode('latin-1'))

    def save(self, output_path: str) -> None:
        """
        Save the signed PDF to a new file.

        Args:
            output_path: Path to save signed PDF
        """
        self.pdf.save(output_path)

    def save_to_bytes(self) -> bytes:
        """
        Save the signed PDF to bytes.

        Returns:
            PDF file bytes
        """
        buffer = io.BytesIO()
        self.pdf.save(buffer)
        return buffer.getvalue()

    def close(self) -> None:
        """Close the PDF."""
        if hasattr(self, 'pdf'):
            try:
                self.pdf.close()
            except Exception:
                pass

    def __del__(self):
        self.close()


def sign_pdf(input_pdf_path: str, output_pdf_path: str,
             signatures: List[Dict[str, Any]]) -> bool:
    """
    Convenience function to sign a PDF in one call.

    Args:
        input_pdf_path: Path to original PDF
        output_pdf_path: Path to save signed PDF
        signatures: List of signature dicts with keys:
                   - page: int (page number, 0-indexed)
                   - sig_path: str (path to signature image)
                   - x, y: float (position in PDF coordinates)
                   - width, height: float (dimensions in PDF points)

    Returns:
        True if successful, False otherwise
    """
    try:
        signer = PDFSigner(input_pdf_path)

        for sig in signatures:
            signer.add_signature(
                page_num=sig["page"],
                sig_image_path=sig["sig_path"],
                x=sig["x"],
                y=sig["y"],
                width=sig["width"],
                height=sig["height"]
            )

        signer.save(output_pdf_path)
        signer.close()
        return True

    except Exception as e:
        print(f"Error signing PDF: {e}")
        return False
```

**Impact**: None (not called anywhere yet)

---

## Phase 4: Main Window Integration

### 4.1 Add PDF Tab to Main Window

**Action**: Extend MainWindow with new PDF tab (alongside existing image extraction tab)

**File**: `desktop_app/views/main_window.py`

**Changes**:

1. **Import PDF modules** (at top of file):

```python
# EXISTING IMPORTS (unchanged)
from desktop_app.api.client import ApiClient
from desktop_app.state.session import SessionState
from desktop_app.widgets.image_view import ImageView
# ... existing imports ...

# NEW: PDF imports (lazy load to avoid breaking if not installed)
try:
    from desktop_app.pdf.viewer import PDFViewer
    from desktop_app.pdf.signer import sign_pdf
    from desktop_app.pdf.storage import AuditLogger, save_signed_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠ PDF features not available (install pypdfium2 and pikepdf)")
```

2. **Add Tab Widget** (in `__init__` method):

```python
def __init__(self, api_client, session_state, parent=None):
    super().__init__(parent)
    self.api_client = api_client
    self.session = session_state

    # NEW: Initialize PDF state
    self.audit_logger: Optional[AuditLogger] = None

    self.setWindowTitle("Signature Extractor (Desktop)")

    # ... existing window setup ...

    # CHANGE: Replace single central widget with tab widget
    from PySide6.QtWidgets import QTabWidget

    self.tabs = QTabWidget(self)
    self.setCentralWidget(self.tabs)

    # Tab 1: Existing signature extraction (UNCHANGED)
    extraction_tab = QWidget()
    self._setup_extraction_tab(extraction_tab)
    self.tabs.addTab(extraction_tab, "Extract Signatures")

    # Tab 2: NEW PDF signing
    if PDF_AVAILABLE:
        pdf_tab = QWidget()
        self._setup_pdf_tab(pdf_tab)
        self.tabs.addTab(pdf_tab, "Sign PDFs")
```

3. **Move existing UI to extraction tab**:

```python
def _setup_extraction_tab(self, tab_widget: QWidget) -> None:
    """Setup existing signature extraction UI (UNCHANGED FUNCTIONALITY)."""
    root = QHBoxLayout(tab_widget)

    # Left panel (controls)
    left_panel = QWidget()
    left_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    left_panel.setFixedWidth(320)
    controls = QVBoxLayout(left_panel)

    # ... ALL EXISTING UI CODE GOES HERE ...
    # (just move it from __init__ into this method)
    # - open_btn
    # - threshold slider
    # - color picker
    # - zoom controls
    # - library list
    # - etc.

    # Right panel (image view)
    right_panel = QWidget()
    main_view = QVBoxLayout(right_panel)

    # ... existing image view setup ...

    root.addWidget(left_panel)
    root.addWidget(right_panel, 1)
```

4. **Create new PDF tab**:

```python
def _setup_pdf_tab(self, tab_widget: QWidget) -> None:
    """Setup PDF signing UI."""
    root = QHBoxLayout(tab_widget)

    # Left panel: PDF controls + signature library
    left_panel = QWidget()
    left_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    left_panel.setFixedWidth(320)
    controls = QVBoxLayout(left_panel)

    # PDF file controls
    controls.addWidget(QLabel("<b>PDF Document</b>"))

    self.pdf_open_btn = QPushButton("📄 Open PDF")
    self.pdf_open_btn.clicked.connect(self.on_pdf_open)
    controls.addWidget(self.pdf_open_btn)

    self.pdf_close_btn = QPushButton("Close PDF")
    self.pdf_close_btn.clicked.connect(self.on_pdf_close)
    self.pdf_close_btn.setEnabled(False)
    controls.addWidget(self.pdf_close_btn)

    controls.addSpacing(20)

    # Signature library (read-only for selection)
    controls.addWidget(QLabel("<b>Signature Library</b>"))
    controls.addWidget(QLabel("Click a signature, then click on PDF to place it:"))

    self.pdf_sig_list = QListWidget()
    self.pdf_sig_list.setMaximumHeight(300)
    self.pdf_sig_list.itemClicked.connect(self.on_pdf_sig_selected)
    controls.addWidget(self.pdf_sig_list)

    self.pdf_refresh_lib_btn = QPushButton("🔄 Refresh Library")
    self.pdf_refresh_lib_btn.clicked.connect(self.refresh_pdf_library)
    controls.addWidget(self.pdf_refresh_lib_btn)

    controls.addSpacing(20)

    # Save controls
    controls.addWidget(QLabel("<b>Save Signed PDF</b>"))

    self.pdf_save_btn = QPushButton("💾 Save Signed PDF")
    self.pdf_save_btn.clicked.connect(self.on_pdf_save)
    self.pdf_save_btn.setEnabled(False)
    controls.addWidget(self.pdf_save_btn)

    self.pdf_view_logs_btn = QPushButton("📋 View Audit Logs")
    self.pdf_view_logs_btn.clicked.connect(self.on_pdf_view_audit_logs)
    self.pdf_view_logs_btn.setEnabled(False)
    controls.addWidget(self.pdf_view_logs_btn)

    controls.addStretch()

    # Right panel: PDF viewer
    right_panel = QWidget()
    pdf_view_layout = QVBoxLayout(right_panel)

    self.pdf_viewer = PDFViewer()
    self.pdf_viewer.signature_placed.connect(self.on_signature_placed_on_pdf)
    pdf_view_layout.addWidget(self.pdf_viewer)

    root.addWidget(left_panel)
    root.addWidget(right_panel, 1)

    # Load signature library
    self.refresh_pdf_library()
```

5. **PDF action handlers**:

```python
def on_pdf_open(self) -> None:
    """Open a PDF file for signing."""
    path, _ = QFileDialog.getOpenFileName(
        self, "Open PDF", "", "PDF Files (*.pdf)"
    )
    if not path:
        return

    # Initialize PDF state in session
    self.session.init_pdf_state()
    self.session.pdf_state.current_pdf_path = path

    # Open PDF in viewer
    if self.pdf_viewer.open_pdf(path):
        # Initialize audit logger
        self.audit_logger = AuditLogger(path, self.session.user_email)
        self.audit_logger.log_open()

        # Update UI
        self.pdf_close_btn.setEnabled(True)
        self.pdf_save_btn.setEnabled(True)
        self.pdf_view_logs_btn.setEnabled(True)
        self.statusBar().showMessage(f"Opened: {Path(path).name}")
    else:
        self.session.clear_pdf_state()


def on_pdf_close(self) -> None:
    """Close the current PDF."""
    self.pdf_viewer.close_pdf()
    self.session.clear_pdf_state()
    self.audit_logger = None

    # Update UI
    self.pdf_close_btn.setEnabled(False)
    self.pdf_save_btn.setEnabled(False)
    self.pdf_view_logs_btn.setEnabled(False)
    self.statusBar().showMessage("PDF closed")


def on_pdf_sig_selected(self, item: QListWidgetItem) -> None:
    """Handle signature selection from library."""
    sig_path = item.data(Qt.UserRole)
    if not sig_path or not Path(sig_path).exists():
        return

    # Load signature image
    sig_pixmap = QPixmap(sig_path)
    if sig_pixmap.isNull():
        QMessageBox.warning(self, "Error", "Failed to load signature image")
        return

    # Set for placement on PDF
    self.pdf_viewer.set_signature_for_placement(sig_pixmap)
    self.statusBar().showMessage("Click on PDF to place signature")

    # Store path for later use
    self._pending_sig_path = sig_path


def on_signature_placed_on_pdf(self, page: int, x: int, y: int,
                                width: int, height: int) -> None:
    """Handle signature placement on PDF page."""
    if not hasattr(self, '_pending_sig_path'):
        return

    # Log the placement
    if self.audit_logger:
        self.audit_logger.log_place_signature(
            page, self._pending_sig_path, x, y, width, height
        )

    # Store in session state
    if self.session.pdf_state:
        self.session.pdf_state.placed_signatures.append({
            "page": page,
            "sig_path": self._pending_sig_path,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        })

    self.statusBar().showMessage(f"Signature placed on page {page + 1}")
    del self._pending_sig_path


def on_pdf_save(self) -> None:
    """Save the signed PDF."""
    if not self.session.pdf_state or not self.session.pdf_state.current_pdf_path:
        return

    placed_sigs = self.session.pdf_state.placed_signatures
    if not placed_sigs:
        reply = QMessageBox.question(
            self, "No Signatures",
            "No signatures have been placed. Save anyway?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

    # Ask for output path
    original_name = Path(self.session.pdf_state.current_pdf_path).name
    default_name = f"{Path(original_name).stem}_signed.pdf"

    output_path, _ = QFileDialog.getSaveFileName(
        self, "Save Signed PDF", default_name, "PDF Files (*.pdf)"
    )
    if not output_path:
        return

    # Sign PDF
    try:
        # Convert Qt coordinates to PDF coordinates
        # (pikepdf expects bottom-left origin, Qt uses top-left)
        pdf_signatures = []
        for sig in placed_sigs:
            # Get page height for coordinate conversion
            # (This is simplified - actual implementation needs page dimensions)
            pdf_signatures.append({
                "page": sig["page"],
                "sig_path": sig["sig_path"],
                "x": sig["x"],
                "y": sig["y"],  # Will be converted in signer
                "width": sig["width"],
                "height": sig["height"]
            })

        # Sign PDF
        success = sign_pdf(
            self.session.pdf_state.current_pdf_path,
            output_path,
            pdf_signatures
        )

        if success:
            # Log save operation
            if self.audit_logger:
                self.audit_logger.log_save(output_path, len(placed_sigs))

            QMessageBox.information(
                self, "Success",
                f"Signed PDF saved to:\n{output_path}"
            )
            self.statusBar().showMessage(f"Saved: {Path(output_path).name}")
        else:
            raise Exception("PDF signing failed")

    except Exception as e:
        if self.audit_logger:
            self.audit_logger.log_error("save_failed", str(e))
        QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{e}")


def on_pdf_view_audit_logs(self) -> None:
    """View audit logs for current PDF."""
    if not self.session.pdf_state or not self.session.pdf_state.current_pdf_path:
        return

    from desktop_app.pdf.storage import get_audit_logs_for_pdf

    logs = get_audit_logs_for_pdf(self.session.pdf_state.current_pdf_path)

    if not logs:
        QMessageBox.information(self, "Audit Logs", "No audit logs found for this PDF")
        return

    # Display logs in a simple dialog
    log_text = "\n\n".join([
        f"[{log.timestamp}] {log.operation}\n{log.details}"
        for log in logs
    ])

    # Create simple text display dialog
    from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox

    dialog = QDialog(self)
    dialog.setWindowTitle("Audit Logs")
    dialog.resize(600, 400)

    layout = QVBoxLayout(dialog)

    text_edit = QTextEdit()
    text_edit.setReadOnly(True)
    text_edit.setPlainText(log_text)
    layout.addWidget(text_edit)

    buttons = QDialogButtonBox(QDialogButtonBox.Ok)
    buttons.accepted.connect(dialog.accept)
    layout.addLayout(buttons)

    dialog.exec()


def refresh_pdf_library(self) -> None:
    """Refresh signature library in PDF tab."""
    self.pdf_sig_list.clear()

    # Load from library
    from desktop_app.library import storage as lib
    items = lib.list_items(limit=100)

    for lib_item in items:
        pixmap = QPixmap(lib_item.path)
        if pixmap.isNull():
            continue

        # Create thumbnail
        thumb = pixmap.scaled(80, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create list item
        list_item = QListWidgetItem(lib_item.display_name)
        list_item.setIcon(thumb)
        list_item.setData(Qt.UserRole, lib_item.path)

        self.pdf_sig_list.addItem(list_item)
```

**Impact**:

- **Existing functionality**: 100% preserved in "Extract Signatures" tab
- **New functionality**: Completely separate in "Sign PDFs" tab
- **Shared**: Signature library (read-only in PDF tab)

---

## Phase 5: Testing & Validation

### 5.1 Unit Tests

**File**: `desktop_app/tests/test_pdf_features.py`

```python
"""Unit tests for PDF features."""

import os
import tempfile
from pathlib import Path

import pytest
from PySide6.QtGui import QPixmap

from desktop_app.pdf.renderer import PDFRenderer
from desktop_app.pdf.signer import PDFSigner, sign_pdf
from desktop_app.pdf.storage import AuditLogger, save_signed_pdf


@pytest.fixture
def sample_pdf():
    """Create a simple test PDF."""
    # Create a minimal PDF for testing
    from reportlab.pdfgen import canvas

    temp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    c = canvas.Canvas(temp.name)
    c.drawString(100, 750, "Test PDF Document")
    c.showPage()
    c.save()

    yield temp.name
    os.unlink(temp.name)


@pytest.fixture
def sample_signature():
    """Create a simple test signature image."""
    temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)

    pixmap = QPixmap(200, 100)
    pixmap.fill(Qt.white)
    pixmap.save(temp.name)

    yield temp.name
    os.unlink(temp.name)


def test_pdf_renderer_open(sample_pdf):
    """Test opening a PDF."""
    renderer = PDFRenderer(sample_pdf)
    assert renderer.page_count() == 1
    renderer.close()


def test_pdf_renderer_render_page(sample_pdf):
    """Test rendering a PDF page."""
    renderer = PDFRenderer(sample_pdf)
    pixmap = renderer.render_page(0)
    assert pixmap is not None
    assert not pixmap.isNull()
    renderer.close()


def test_pdf_signer_add_signature(sample_pdf, sample_signature):
    """Test adding a signature to PDF."""
    signer = PDFSigner(sample_pdf)
    signer.add_signature(0, sample_signature, 100, 100, 150, 50)

    output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    signer.save(output.name)
    signer.close()

    # Verify output exists and has content
    assert Path(output.name).exists()
    assert Path(output.name).stat().st_size > 0

    os.unlink(output.name)


def test_audit_logger():
    """Test audit logging."""
    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

    logger = AuditLogger(temp_pdf.name, "test@example.com")
    logger.log_open()
    logger.log_place_signature(0, "sig.png", 100, 200, 150, 50)
    logger.log_save("/output.pdf", 1)

    # Verify log file was created
    assert Path(logger.log_file).exists()

    # Clean up
    os.unlink(logger.log_file)
    os.unlink(temp_pdf.name)


def test_sign_pdf_workflow(sample_pdf, sample_signature):
    """Test complete PDF signing workflow."""
    output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

    signatures = [
        {
            "page": 0,
            "sig_path": sample_signature,
            "x": 100,
            "y": 600,
            "width": 150,
            "height": 50
        }
    ]

    success = sign_pdf(sample_pdf, output.name, signatures)
    assert success
    assert Path(output.name).exists()

    os.unlink(output.name)
```

**Run tests**:

```bash
pytest desktop_app/tests/test_pdf_features.py -v
```

---

### 5.2 Integration Testing Checklist

**Manual Testing Plan**:

1. **Existing Features (Must Not Break)**:

   - [ ] Open image → Upload → Extract → Preview works
   - [ ] Threshold slider works
   - [ ] Color picker works
   - [ ] Zoom controls work
   - [ ] Save to library works
   - [ ] Library view/delete works
   - [ ] Export PNG works
   - [ ] Export JSON works

2. **New PDF Features**:

   - [ ] Open PDF displays correctly
   - [ ] Page navigation works (prev/next)
   - [ ] Zoom controls work in PDF viewer
   - [ ] Select signature from library enables placement
   - [ ] Click on PDF places signature at correct position
   - [ ] Multiple signatures can be placed
   - [ ] Click on placed signature offers removal
   - [ ] Save signed PDF creates valid file
   - [ ] Saved PDF opens in external viewer with signatures
   - [ ] Audit log captures all operations
   - [ ] View audit logs displays correctly

3. **Cross-Tab Functionality**:
   - [ ] Switching tabs doesn't lose state
   - [ ] Signatures extracted in tab 1 appear in tab 2 library
   - [ ] Both tabs can coexist without conflicts

---

## Phase 6: Documentation & Deployment

### 6.1 Update User Documentation

**File**: `docs/HELP.md` (add section)

```markdown
## PDF Signing Workflow

### Opening a PDF

1. Click the **"Sign PDFs"** tab
2. Click **"📄 Open PDF"**
3. Select a PDF file from your computer
4. The first page will display in the viewer

### Placing Signatures

1. In the **Signature Library** panel, click on a saved signature
2. Your cursor will change to a crosshair (†)
3. Click anywhere on the PDF to place the signature
4. The signature will appear at the clicked position
5. Repeat to place multiple signatures

### Removing Signatures

- Click on any placed signature
- Choose **"Yes"** to remove it

### Saving the Signed PDF

1. Click **"💾 Save Signed PDF"**
2. Choose where to save the file
3. The original PDF remains unchanged
4. A new signed PDF is created

### Viewing Audit Logs

- Click **"📋 View Audit Logs"** to see all operations:
  - When the PDF was opened
  - Every signature placement (timestamp, position, page)
  - When the PDF was saved
- Audit logs are stored in `~/.signature_extractor/audit_logs/`

### Keyboard Shortcuts

- **Prev Page**: Left Arrow
- **Next Page**: Right Arrow
- **Zoom In**: Ctrl/Cmd + (on PDF tab)
- **Zoom Out**: Ctrl/Cmd - (on PDF tab)
```

---

### 6.2 Update README

**File**: `README.md` (add section)

```markdown
## Features

### Signature Extraction

- Open any image with signatures
- Select signature regions with mouse
- Automatic background removal
- Adjustable threshold and color
- Save to personal library

### PDF Signing (New!)

- Open PDF documents
- Place saved signatures anywhere on any page
- Multiple signatures per document
- Save signed PDFs (original unchanged)
- Complete audit trail for compliance

### Library Management

- View all saved signatures
- One-click deletion
- Export as PNG or JSON
- Reuse across documents
```

---

### 6.3 Migration Guide

**File**: `docs/PDF_MIGRATION.md`

````markdown
# Migrating to PDF-Enabled Version

## For Existing Users

**Good news**: All your existing signatures are automatically available in the PDF signing feature!

### What's Changed

1. **New Tab Layout**:

   - Your existing workflow is now in the "Extract Signatures" tab
   - New "Sign PDFs" tab for PDF operations
   - Everything else works exactly the same

2. **Shared Library**:
   - Signatures you've saved are available in both tabs
   - Extract in tab 1, use in tab 2

### What Hasn't Changed

- Image extraction workflow (identical)
- Signature library storage location
- Export functionality
- All keyboard shortcuts

### New Dependencies

If you're building from source:

```bash
pip install pypdfium2>=4.26.0 pikepdf>=8.10.0
```
````

If PDF libraries aren't installed, the app will work normally but the "Sign PDFs" tab won't appear.

## For Developers

### Bundling Changes

- App size increases by ~20 MB (PDF libraries)
- See `docs/BUNDLING_ANALYSIS.md` for details

### API Changes

- `SessionState` has new `pdf_state` field (optional, backwards compatible)
- New modules under `desktop_app/pdf/` (isolated, no breaking changes)

```

---

## Phase 7: Rollout Plan

### 7.1 Development Timeline

**Week 1: Foundation**
- Day 1-2: Install dependencies, create module structure
- Day 3-4: Implement PDF renderer and viewer widget
- Day 5: Testing and bug fixes

**Week 2: Integration**
- Day 1-2: Implement PDF signer
- Day 3-4: Integrate into main window (tab structure)
- Day 5: Testing existing features (regression check)

**Week 3: Polish**
- Day 1-2: Audit logging implementation
- Day 3-4: UI refinements, error handling
- Day 5: Integration testing

**Week 4: Documentation & Release**
- Day 1-2: Write documentation
- Day 3: Build and test installers
- Day 4: Beta testing
- Day 5: Release

---

### 7.2 Risk Mitigation

**Risk 1: Breaking Existing Features**
- **Mitigation**: Tab-based UI keeps workflows separate
- **Verification**: Comprehensive regression testing checklist

**Risk 2: PDF Library Compatibility**
- **Mitigation**: Lazy loading, graceful degradation if not installed
- **Verification**: Test on clean machines without PDF libs

**Risk 3: Large File Sizes**
- **Mitigation**: Use pypdfium2 (smaller than PyMuPDF)
- **Verification**: Bundle size testing (target: <150 MB)

**Risk 4: Coordinate System Confusion**
- **Mitigation**: Clear documentation, helper functions for Qt↔PDF conversion
- **Verification**: Visual verification of signature placement

---

## Appendix: Code Structure Summary

```

desktop_app/
├─ main.py # UNCHANGED (entry point)
├─ config.py # UNCHANGED
├─ state/
│ └─ session.py # MODIFIED (added pdf_state field)
├─ library/
│ └─ storage.py # UNCHANGED (shared by both workflows)
├─ views/
│ ├─ main_window.py # MODIFIED (added tabs, PDF handlers)
│ ├─ login_dialog.py # UNCHANGED
│ ├─ export_dialog.py # UNCHANGED
│ └─ license_dialog.py # UNCHANGED
├─ widgets/
│ └─ image_view.py # UNCHANGED
├─ pdf/ # NEW MODULE
│ ├─ **init**.py
│ ├─ renderer.py # PDF → QPixmap rendering
│ ├─ viewer.py # PDF viewer widget
│ ├─ signer.py # Signature embedding
│ ├─ storage.py # PDF storage + audit logging
│ └─ audit.py # Audit log utilities
└─ tests/
├─ test_main_window_logic.py # UNCHANGED
└─ test_pdf_features.py # NEW

backend/ # UNCHANGED (no backend changes needed)

````

---

## Success Criteria

✅ **Preservation**: All existing features work identically

✅ **Integration**: PDF signing uses existing signature library

✅ **Audit**: All PDF operations are logged with timestamps

✅ **UX**: Intuitive tab-based workflow, clear visual feedback

✅ **Quality**: Signed PDFs open correctly in all PDF viewers

✅ **Performance**: PDF rendering <2 seconds per page

✅ **Size**: Final bundle <150 MB (including PDF libraries)

✅ **Documentation**: Complete user guide and developer docs

---

## Next Steps

1. **Install dependencies**:
   ```bash
   pip install pypdfium2>=4.26.0 pikepdf>=8.10.0
````

2. **Create PDF module** (Phase 1.2)

3. **Run existing tests** to establish baseline:

   ```bash
   pytest desktop_app/tests/ -v
   ```

4. **Implement in order**: Renderer → Viewer → Signer → Integration

5. **Test after each phase** to catch issues early

Ready to begin! 🚀
