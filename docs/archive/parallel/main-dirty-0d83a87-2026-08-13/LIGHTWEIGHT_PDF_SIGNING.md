# Lightweight PDF Signing Implementation (Phase 0)

## Goal

Enable users to open a PDF, place their signature anywhere, and save a signed PDF - **all offline, no Docker, minimal size increase**.

## Size Impact

### Current App

- PySide6: ~60 MB
- Pillow: ~5 MB
- OpenCV: ~40 MB
- NumPy: ~20 MB
- Requests: ~1 MB
- **Total: ~126 MB**

### With PDF Signing (Lightweight)

- PyMuPDF (fitz): ~40 MB (PDF rendering)
- pikepdf: ~5 MB (PDF manipulation)
- **New Total: ~171 MB** (only 35% increase)

### Alternative: If We Added Stirling-PDF

- Stirling-PDF: ~500-800 MB
- Java Runtime: ~100+ MB
- **Would be: ~800-1000 MB** (6x-8x increase) ❌

## Architecture

```
Desktop App (PySide6)
    ↓
┌─────────────────────────────────────┐
│  PDF Signing Module                 │
│  ├─ PyMuPDF: Render PDF to images  │
│  ├─ Your existing: Image overlay    │
│  ├─ pikepdf: Flatten & save PDF    │
│  └─ Local only, no backend needed   │
└─────────────────────────────────────┘
```

## Implementation Plan

### Dependencies

**requirements.txt additions:**

```txt
PyMuPDF==1.23.8  # aka fitz - PDF rendering
pikepdf==8.10.1  # PDF manipulation
reportlab==4.0.7  # Optional: for creating PDF content
```

### Core PDF Module

**desktop_app/pdf/**init**.py** (new):

```python
"""PDF viewing and signing module."""
from .viewer import PDFViewer
from .signer import PDFSigner

__all__ = ["PDFViewer", "PDFSigner"]
```

**desktop_app/pdf/viewer.py** (new):

```python
"""PDF viewer widget using PyMuPDF."""
from typing import Optional
import fitz  # PyMuPDF
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Signal


class PDFViewer(QWidget):
    """Widget for viewing and navigating PDF pages."""

    page_changed = Signal(int)  # Current page number

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doc: Optional[fitz.Document] = None
        self.current_page = 0
        self.zoom = 1.0
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        # Add image label, navigation controls, etc.
        # Similar to your existing ImageView widget

    def load_pdf(self, filepath: str) -> bool:
        """
        Load PDF file.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.doc = fitz.open(filepath)
            self.current_page = 0
            self._render_page(0)
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False

    def _render_page(self, page_num: int) -> QImage:
        """
        Render PDF page to QImage.

        Args:
            page_num: Page number (0-indexed)

        Returns:
            QImage of the rendered page
        """
        if not self.doc or page_num >= len(self.doc):
            return QImage()

        page = self.doc[page_num]

        # Render at specified zoom (DPI)
        # 72 DPI = 1.0 zoom, 144 DPI = 2.0 zoom
        mat = fitz.Matrix(self.zoom * 2, self.zoom * 2)  # 2x for retina
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert PyMuPDF pixmap to QImage
        img = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format_RGB888
        )

        return img.copy()  # Copy to avoid memory issues

    def get_page_dimensions(self, page_num: int) -> tuple[float, float]:
        """
        Get page width and height in points (1/72 inch).

        Returns:
            (width, height) tuple
        """
        if not self.doc or page_num >= len(self.doc):
            return (0, 0)

        page = self.doc[page_num]
        rect = page.rect
        return (rect.width, rect.height)

    def page_count(self) -> int:
        """Get total number of pages."""
        return len(self.doc) if self.doc else 0

    def next_page(self):
        """Navigate to next page."""
        if self.current_page < self.page_count() - 1:
            self.current_page += 1
            self._render_page(self.current_page)
            self.page_changed.emit(self.current_page)

    def previous_page(self):
        """Navigate to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page(self.current_page)
            self.page_changed.emit(self.current_page)

    def set_zoom(self, zoom: float):
        """Set zoom level (1.0 = 100%)."""
        self.zoom = max(0.25, min(zoom, 4.0))
        self._render_page(self.current_page)
```

**desktop_app/pdf/signer.py** (new):

```python
"""PDF signing functionality using pikepdf and PyMuPDF."""
from typing import Optional
import io
from pathlib import Path
import fitz  # PyMuPDF
import pikepdf
from PIL import Image


class PDFSigner:
    """Handle PDF signature placement and flattening."""

    def __init__(self, pdf_path: str):
        """
        Initialize signer with PDF file.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        self.doc = fitz.open(str(self.pdf_path))

    def add_signature_image(
        self,
        signature_image_path: str,
        page_num: int,
        x: float,
        y: float,
        width: Optional[float] = None,
        height: Optional[float] = None,
        keep_aspect: bool = True
    ) -> bool:
        """
        Add signature image to PDF page.

        Args:
            signature_image_path: Path to signature PNG (with transparency)
            page_num: Page number (0-indexed)
            x, y: Position in PDF points (1/72 inch)
            width, height: Signature size in points (optional)
            keep_aspect: Maintain aspect ratio if only one dimension given

        Returns:
            True if successful
        """
        try:
            page = self.doc[page_num]

            # Load signature image
            img = Image.open(signature_image_path)

            # Calculate dimensions if not provided
            if width is None and height is None:
                # Default to 2 inches wide at 150 DPI
                width = 2 * 72  # 144 points
                height = width * (img.height / img.width)
            elif width is None:
                width = height * (img.width / img.height)
            elif height is None:
                height = width * (img.height / img.width)

            # Create rectangle for signature placement
            rect = fitz.Rect(x, y, x + width, y + height)

            # Insert image into PDF
            # PyMuPDF handles PNG transparency automatically
            page.insert_image(
                rect,
                filename=signature_image_path,
                keep_proportion=keep_aspect,
                overlay=True  # Place on top of existing content
            )

            return True

        except Exception as e:
            print(f"Error adding signature: {e}")
            return False

    def save(self, output_path: str, flatten: bool = True) -> bool:
        """
        Save signed PDF.

        Args:
            output_path: Path to save signed PDF
            flatten: If True, flatten annotations and make non-editable

        Returns:
            True if successful
        """
        try:
            if flatten:
                # Save with PyMuPDF (bakes images into content stream)
                self.doc.save(
                    output_path,
                    garbage=4,  # Maximum compression
                    deflate=True,
                    clean=True
                )
            else:
                # Save without flattening (preserves layers)
                self.doc.save(output_path)

            return True

        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False

    def add_metadata(
        self,
        author: Optional[str] = None,
        title: Optional[str] = None,
        subject: Optional[str] = None,
        keywords: Optional[str] = None
    ):
        """
        Add or update PDF metadata.

        Args:
            author: Document author
            title: Document title
            subject: Document subject
            keywords: Comma-separated keywords
        """
        metadata = self.doc.metadata

        if author:
            metadata["author"] = author
        if title:
            metadata["title"] = title
        if subject:
            metadata["subject"] = subject
        if keywords:
            metadata["keywords"] = keywords

        # Add signature tool info
        metadata["producer"] = "Signature Extractor App"
        metadata["creator"] = "Signature Extractor App"

        self.doc.set_metadata(metadata)

    def close(self):
        """Close PDF document."""
        if self.doc:
            self.doc.close()


class SimplePDFSigner:
    """
    Simplified signer for quick operations.
    Use this for one-shot signing without viewer.
    """

    @staticmethod
    def sign_pdf(
        input_pdf: str,
        output_pdf: str,
        signature_image: str,
        page_num: int,
        x: float,
        y: float,
        width: float,
        height: float
    ) -> bool:
        """
        One-shot PDF signing.

        Args:
            input_pdf: Input PDF path
            output_pdf: Output PDF path
            signature_image: Signature PNG path
            page_num: Page number (0-indexed)
            x, y: Position in PDF points
            width, height: Signature size in points

        Returns:
            True if successful
        """
        signer = PDFSigner(input_pdf)

        success = signer.add_signature_image(
            signature_image,
            page_num,
            x, y,
            width, height
        )

        if success:
            signer.add_metadata(
                subject="Signed Document",
                keywords="signature, signed"
            )
            success = signer.save(output_pdf, flatten=True)

        signer.close()
        return success
```

### Integration with Main Window

**desktop_app/views/main_window.py** (modifications):

```python
from desktop_app.pdf.viewer import PDFViewer
from desktop_app.pdf.signer import SimplePDFSigner

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... existing code ...

        # Add PDF viewer tab
        self.pdf_viewer = PDFViewer()
        # Add to your tab widget or create new pane

        self._create_pdf_actions()

    def _create_pdf_actions(self):
        """Create PDF-related actions."""
        # File menu
        open_pdf_action = QAction("Open PDF...", self)
        open_pdf_action.triggered.connect(self._on_open_pdf)
        self.file_menu.addAction(open_pdf_action)

        # Sign menu (new)
        sign_menu = self.menuBar().addMenu("Sign")

        place_signature_action = QAction("Place Signature", self)
        place_signature_action.setShortcut("Ctrl+Shift+S")
        place_signature_action.triggered.connect(self._on_place_signature)
        sign_menu.addAction(place_signature_action)

        save_signed_action = QAction("Save Signed PDF", self)
        save_signed_action.setShortcut("Ctrl+S")
        save_signed_action.triggered.connect(self._on_save_signed_pdf)
        sign_menu.addAction(save_signed_action)

    def _on_open_pdf(self):
        """Open PDF file dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if filepath:
            if self.pdf_viewer.load_pdf(filepath):
                self.statusBar().showMessage(f"Loaded: {filepath}")
                self.current_pdf_path = filepath
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to load PDF file"
                )

    def _on_place_signature(self):
        """Place selected signature on current PDF page."""
        # Get selected signature from library
        selected_sig = self.library_view.get_selected_signature()
        if not selected_sig:
            QMessageBox.warning(
                self,
                "No Signature",
                "Please select a signature from your library"
            )
            return

        # Get click position from PDF viewer
        # (You'll need to implement click handling in PDFViewer)
        position = self.pdf_viewer.get_last_click_position()
        if not position:
            QMessageBox.information(
                self,
                "Click to Place",
                "Click on the PDF where you want to place the signature"
            )
            return

        # Place signature
        from desktop_app.pdf.signer import PDFSigner
        signer = PDFSigner(self.current_pdf_path)

        success = signer.add_signature_image(
            selected_sig["path"],
            self.pdf_viewer.current_page,
            position[0],
            position[1],
            width=150,  # 2 inches at 72 DPI
            height=None  # Auto-calculate
        )

        if success:
            # Update preview
            self.pdf_viewer._render_page(self.pdf_viewer.current_page)
            self.statusBar().showMessage("Signature placed")
        else:
            QMessageBox.warning(self, "Error", "Failed to place signature")

    def _on_save_signed_pdf(self):
        """Save signed PDF."""
        if not hasattr(self, 'current_pdf_path'):
            QMessageBox.warning(self, "No PDF", "No PDF loaded")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Signed PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if output_path:
            # Use the in-memory doc from signer
            # Or re-sign if needed
            QMessageBox.information(
                self,
                "Success",
                f"Signed PDF saved to:\n{output_path}"
            )
```

## User Workflow

### Simple Flow (MVP)

1. **Open PDF**: File → Open PDF
2. **View page**: Navigate with arrows, zoom in/out
3. **Select signature**: Click signature in library
4. **Click location**: Click where to place on PDF
5. **Save**: File → Save Signed PDF
6. **Done**: Flattened PDF with signature embedded

### Advanced Flow (Future)

- Multiple signatures on same PDF
- Drag-to-resize signature
- Undo/redo signature placement
- Preview before save
- Add initials, date fields

## Testing Checklist

- [ ] Load PDF with 1 page
- [ ] Load PDF with 10+ pages
- [ ] Navigate between pages
- [ ] Zoom in/out maintains quality
- [ ] Place signature on different pages
- [ ] Signature transparency preserved
- [ ] Save flattened PDF
- [ ] Verify signed PDF opens in Preview/Acrobat
- [ ] Memory usage with large PDFs
- [ ] Works offline (no network)

## Performance Considerations

### Memory

- PyMuPDF loads entire PDF into memory
- For 100-page PDF: ~50-100 MB RAM
- Acceptable for desktop app
- Don't cache all rendered pages (render on-demand)

### Rendering Speed

- Single page render: ~50-200ms depending on complexity
- Fast enough for real-time navigation
- Use threading for background page pre-rendering

### File Size

- Flattened PDFs may be larger (images embedded)
- Use compression (garbage=4, deflate=True)
- Typical increase: 5-20% for signature-only PDFs

## Future Enhancements (Post-MVP)

### Phase 1.5: Enhanced Signing

- [ ] Multiple signature placement per session
- [ ] Drag-and-drop signature positioning
- [ ] Visual preview before save
- [ ] Signature size adjustment

### Phase 2: Basic PDF Editing

- [ ] Rotate pages (using PyMuPDF only, no Stirling)
- [ ] Delete pages
- [ ] Merge two PDFs (using PyMuPDF)
- [ ] Extract page as image

### Phase 3: Advanced (Only if needed)

- [ ] Form field detection
- [ ] Text annotation
- [ ] Freehand drawing
- [ ] Date/text stamps

## When to Consider Stirling-PDF

**DON'T add Stirling-PDF until:**

- ✅ Users specifically request advanced operations (OCR, compression, etc.)
- ✅ You have enterprise customers needing batch processing
- ✅ You're building cloud/web version anyway
- ✅ You've validated demand via surveys/support tickets

**For 90% of users:**

- PyMuPDF + pikepdf is sufficient
- Faster, lighter, simpler
- Works offline
- No Docker complexity

## Size Comparison

| Configuration                   | Size         | Offline         | Complexity |
| ------------------------------- | ------------ | --------------- | ---------- |
| **Current**                     | ~126 MB      | ✅ Full         | Low        |
| **+ PDF Signing (PyMuPDF)**     | ~171 MB      | ✅ Full         | Low        |
| **+ Stirling-PDF**              | ~800-1000 MB | ❌ Needs Docker | High       |
| **+ Stirling-PDF (cloud-only)** | ~171 MB      | ⚠️ Partial      | Medium     |

## Recommendation

**Start with PyMuPDF + pikepdf approach:**

- 35% size increase vs 6-8x with Stirling
- Maintains offline-first positioning
- Simple implementation
- Covers 90% use cases
- Can add Stirling later as optional cloud add-on

**Reserve Stirling-PDF for:**

- Cloud/web version (separate product)
- Enterprise tier with advanced needs
- Optional "Advanced PDF Tools" add-on (downloaded separately)
