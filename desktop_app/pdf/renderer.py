"""PDF page rendering utilities using pypdfium2."""

from typing import Optional, Tuple
from pathlib import Path

import pypdfium2 as pdfium  # type: ignore[import-untyped]
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from desktop_app.pdf.pdfium_runtime import pdfium_operation


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
            with pdfium_operation():
                self.pdf = pdfium.PdfDocument(pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}")
        
        self.pdf_path = pdf_path
    
    def page_count(self) -> int:
        """Get total number of pages."""
        with pdfium_operation():
            return len(self.pdf)
    
    def get_page_size(self, page_num: int) -> Tuple[float, float]:
        """
        Get page dimensions in points (1/72 inch).
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            Tuple of (width, height) in points
        """
        with pdfium_operation():
            if page_num < 0 or page_num >= len(self.pdf):
                return (0.0, 0.0)

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
        with pdfium_operation():
            if page_num < 0 or page_num >= len(self.pdf):
                return None

            try:
                page = self.pdf[page_num]

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
                    QImage.Format.Format_RGB888
                )

                # Convert to QPixmap
                return QPixmap.fromImage(qimage)

            except Exception as e:
                print(f"Error rendering page {page_num}: {e}")
                return None
    
    def close(self) -> None:
        """Close the PDF document."""
        if hasattr(self, 'pdf') and self.pdf is not None:
            try:
                with pdfium_operation():
                    self.pdf.close()
                    self.pdf = None
            except Exception:
                pass
    
    def __del__(self):
        self.close()
