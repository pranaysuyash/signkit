import logging
import io
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

import pypdfium2 as pdfium
import pikepdf
from PIL import Image
from desktop_app.pdf.pdfium_runtime import pdfium_operation

LOG = logging.getLogger(__name__)

class PdfEngine:
    """Handles PDF operations: loading, rendering, and signing."""
    
    def __init__(self):
        self.current_pdf: Optional[pdfium.PdfDocument] = None
        self.pdf_path: Optional[str] = None
        self.page_count = 0
        
    def load_pdf(self, path: str) -> int:
        """Load a PDF document.
        
        Args:
            path: Path to the PDF file.
            
        Returns:
            Number of pages.
        """
        try:
            with pdfium_operation():
                if self.current_pdf is not None:
                    self.current_pdf.close()
                self.current_pdf = pdfium.PdfDocument(path)
                self.pdf_path = path
                self.page_count = len(self.current_pdf)
            LOG.info(f"Loaded PDF: {path} ({self.page_count} pages)")
            return self.page_count
        except Exception as e:
            LOG.error(f"Failed to load PDF {path}: {e}")
            raise

    def render_page(self, page_index: int, scale: float = 1.0) -> Image.Image:
        """Render a PDF page to a PIL Image.
        
        Args:
            page_index: 0-based page index.
            scale: Zoom scale factor.
            
        Returns:
            PIL Image of the rendered page.
        """
        if not self.current_pdf:
            raise ValueError("No PDF loaded")
            
        try:
            with pdfium_operation():
                page = self.current_pdf[page_index]
                bitmap = page.render(scale=scale, rotation=0)
                pil_image = bitmap.to_pil()
                return pil_image
        except Exception as e:
            LOG.error(f"Failed to render page {page_index}: {e}")
            raise

    def close(self) -> None:
        """Close the native PDFium document explicitly."""

        with pdfium_operation():
            if self.current_pdf is not None:
                self.current_pdf.close()
                self.current_pdf = None
            self.pdf_path = None
            self.page_count = 0

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def save_signed_pdf(
        self, 
        output_path: str, 
        signatures: List[Dict[str, Any]]
    ) -> None:
        """Save the PDF with signatures applied.
        
        Args:
            output_path: Where to save the signed PDF.
            signatures: List of signature dicts containing:
                - page_index: int
                - x: float (PDF points from left)
                - y: float (PDF points from bottom - standard PDF coord system)
                - width: float (width in points)
                - height: float (height in points)
                - image_bytes: bytes (PNG data)
        """
        if not self.pdf_path:
            raise ValueError("No PDF loaded")
            
        try:
            pdf = pikepdf.Pdf.open(self.pdf_path)
            
            for sig in signatures:
                page_idx = sig['page_index']
                if page_idx < 0 or page_idx >= len(pdf.pages):
                    continue
                    
                page = pdf.pages[page_idx]
                
                # Convert PNG to PDF using PIL
                img_stream = io.BytesIO(sig['image_bytes'])
                pil_img = Image.open(img_stream)
                
                # Create a temporary PDF in memory
                pdf_bytes = io.BytesIO()
                pil_img.save(pdf_bytes, format='PDF')
                pdf_bytes.seek(0)
                
                # Open as temporary PDF
                src_pdf = pikepdf.Pdf.open(pdf_bytes)
                src_page = src_pdf.pages[0]
                
                # Get page height for coordinate flip
                mediabox = page.MediaBox
                page_height = float(mediabox[3])
                
                x = sig['x']
                y_top = sig['y']
                width = sig['width']
                height = sig['height']
                
                # Convert Top-Left Y to Bottom-Left Y
                y_bottom = page_height - y_top - height
                
                # Overlay onto target page
                # pikepdf.Rectangle(x0, y0, x1, y1)
                rect = pikepdf.Rectangle(x, y_bottom, x + width, y_bottom + height)
                page.add_overlay(src_page, rect)
                
            pdf.save(output_path)
            LOG.info(f"Saved signed PDF to {output_path}")
            
        except Exception as e:
            LOG.error(f"Failed to save signed PDF: {e}")
            raise
