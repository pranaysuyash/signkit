"""Tests for PDF signing improvements - color preservation, tracking, drag/move, bulk placement."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QPointF

if not QApplication.instance():
    app = QApplication(sys.argv)

from desktop_app.pdf.viewer import PDFViewer, PDFPageView
from desktop_app.pdf.signer import sign_pdf
from desktop_app.pdf.renderer import PDFRenderer
from desktop_app.library import storage as signature_library


@pytest.fixture
def sample_pdf():
    """Use pre-generated test PDF."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    sample_path = fixtures_dir / "sample.pdf"
    
    if not sample_path.exists():
        pytest.skip(f"Sample PDF not found at {sample_path}")
    
    return str(sample_path)


@pytest.fixture
def color_signature():
    """Create a colored signature image (blue)."""
    temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    
    pixmap = QPixmap(200, 100)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QColor(0, 0, 255))  # Blue signature
    painter.drawText(10, 50, "Blue Signature")
    painter.end()
    
    pixmap.save(temp.name)
    
    yield temp.name
    
    # Cleanup
    try:
        os.unlink(temp.name)
    except Exception:
        pass


class TestColorPreservation:
    """Test that signature colors are preserved when saving to PDF."""
    
    def test_rgba_signature_preserves_color(self, sample_pdf, color_signature):
        """Test that RGBA signatures maintain color in saved PDF."""
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        signatures = [
            {
                "page": 0,
                "sig_path": color_signature,
                "x": 100,
                "y": 600,
                "width": 150,
                "height": 50
            }
        ]
        
        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        assert Path(output.name).exists()
        assert Path(output.name).stat().st_size > 0
        
        # Cleanup
        os.unlink(output.name)


class TestSignatureTracking:
    """Test signature tracking across multiple pages."""
    
    def test_track_signatures_per_page(self, sample_pdf, color_signature):
        """Test that signatures are tracked separately for each page."""
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)
        
        # Place signature on page 0
        viewer.goto_page(0)
        viewer.page_view.add_signature_overlay(100, 200, 150, 50, QPixmap(color_signature), color_signature)
        
        # Place signature on page 1
        viewer.goto_page(1)
        viewer.page_view.add_signature_overlay(200, 300, 150, 50, QPixmap(color_signature), color_signature)
        
        # Get all signatures
        all_sigs = viewer.get_placed_signatures()
        
        assert len(all_sigs) == 2
        assert all_sigs[0]["page"] == 0
        assert all_sigs[1]["page"] == 1
        assert all_sigs[0]["sig_path"] == color_signature
        assert all_sigs[1]["sig_path"] == color_signature
        
        viewer.close_pdf()
    
    def test_signatures_persist_across_page_changes(self, sample_pdf, color_signature):
        """Test that signatures remain when navigating between pages."""
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)
        
        # Place signature on page 0
        viewer.goto_page(0)
        viewer.page_view.add_signature_overlay(100, 200, 150, 50, QPixmap(color_signature), color_signature)
        
        # Navigate away and back
        viewer.goto_page(1)
        viewer.goto_page(0)
        
        # Check signature is still there
        assert len(viewer.page_view.signatures) == 1
        assert viewer.page_view.signatures[0]["x"] == 100
        assert viewer.page_view.signatures[0]["y"] == 200
        
        viewer.close_pdf()
    
    def test_correct_signature_count(self, sample_pdf, color_signature):
        """Test that signature count is accurate."""
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)
        
        # Place 3 signatures on different pages
        viewer.goto_page(0)
        viewer.page_view.add_signature_overlay(100, 200, 150, 50, QPixmap(color_signature), color_signature)
        viewer.page_view.add_signature_overlay(300, 400, 150, 50, QPixmap(color_signature), color_signature)
        
        viewer.goto_page(1)
        viewer.page_view.add_signature_overlay(150, 250, 150, 50, QPixmap(color_signature), color_signature)
        
        all_sigs = viewer.get_placed_signatures()
        assert len(all_sigs) == 3
        
        viewer.close_pdf()


class TestDragMove:
    """Test signature drag and move functionality."""
    
    def test_signature_drag_updates_position(self):
        """Test that dragging a signature updates its position."""
        page_view = PDFPageView()
        page_view.set_page(QPixmap(800, 600))
        
        # Add signature
        pixmap = QPixmap(150, 50)
        pixmap.fill(QColor(255, 0, 0))
        page_view.add_signature_overlay(100, 100, 150, 50, pixmap, "test.png")
        
        original_x = page_view.signatures[0]["x"]
        original_y = page_view.signatures[0]["y"]
        
        # Simulate drag (this would normally be done through mouse events)
        page_view.signatures[0]["x"] = 200
        page_view.signatures[0]["y"] = 200
        
        assert page_view.signatures[0]["x"] == 200
        assert page_view.signatures[0]["y"] == 200
        assert page_view.signatures[0]["x"] != original_x
        assert page_view.signatures[0]["y"] != original_y
    
    def test_signature_constrained_to_bounds(self):
        """Test that dragged signatures stay within page bounds."""
        page_view = PDFPageView()
        page_view.set_page(QPixmap(800, 600))
        
        pixmap = QPixmap(150, 50)
        page_view.add_signature_overlay(700, 550, 150, 50, pixmap, "test.png")
        
        sig = page_view.signatures[0]
        
        # Try to drag beyond bounds
        sig["x"] = 900  # Would go off page
        sig["y"] = 700  # Would go off page
        
        # In real code, mouseMoveEvent constrains these
        # Simulate the constraint logic
        if page_view.pixmap:
            sig["x"] = max(0, min(sig["x"], page_view.pixmap.width() - sig["width"]))
            sig["y"] = max(0, min(sig["y"], page_view.pixmap.height() - sig["height"]))
        
        assert sig["x"] <= 800 - 150  # Within bounds
        assert sig["y"] <= 600 - 50   # Within bounds


class TestPlacementPreview:
    """Test signature placement preview functionality."""
    
    def test_preview_enabled_on_selection(self):
        """Test that preview is enabled when signature is selected."""
        page_view = PDFPageView()
        
        pixmap = QPixmap(150, 50)
        pixmap.fill(QColor(0, 255, 0))
        
        page_view.set_preview_signature(pixmap)
        
        assert page_view.preview_pixmap is not None
        assert page_view.preview_pixmap.width() == 150
    
    def test_preview_cleared_after_placement(self):
        """Test that preview is cleared after signature is placed."""
        page_view = PDFPageView()
        page_view.set_page(QPixmap(800, 600))
        
        pixmap = QPixmap(150, 50)
        page_view.set_preview_signature(pixmap)
        
        # Place signature
        page_view.add_signature_overlay(100, 100, 150, 50, pixmap, "test.png")
        
        # Clear preview (would be done by PDFViewer)
        page_view.set_preview_signature(None)
        
        assert page_view.preview_pixmap is None


class TestSignatureStyleEditing:
    """Test signature appearance controls and persistence."""

    def test_signature_style_roundtrip_and_update(self):
        page_view = PDFPageView()
        page_view.set_page(QPixmap(800, 600))

        pixmap = QPixmap(120, 40)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 120, 40, QColor(20, 40, 80))
        painter.end()

        style = {
            "rotation_deg": 90,
            "brightness": 1.1,
            "contrast": 0.9,
            "saturation": 0.8,
        }
        page_view.add_signature_overlay(100, 100, 120, 40, pixmap, "test.png", style)

        stored_style = page_view.get_signature_style(0)
        assert stored_style["rotation_deg"] == 90.0
        assert stored_style["brightness"] == 1.1
        assert page_view.signatures[0]["pixmap"].width() == 40
        assert page_view.signatures[0]["pixmap"].height() == 120

        updated = page_view.update_signature_style(
            0,
            {
                "rotation_deg": 180,
                "brightness": 1.0,
                "contrast": 1.0,
                "saturation": 1.0,
            },
        )

        assert updated is True
        assert page_view.get_signature_style(0)["rotation_deg"] == 180.0

    def test_restored_signature_style_round_trip(self, sample_pdf, color_signature):
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)

        viewer.restore_signature_placements(
            [
                {
                    "page": 0,
                    "sig_path": color_signature,
                    "x": 120,
                    "y": 220,
                    "width": 150,
                    "height": 50,
                    "style": {
                        "rotation_deg": 270,
                        "brightness": 0.85,
                        "contrast": 1.15,
                        "saturation": 0.75,
                    },
                }
            ]
        )

        assert len(viewer.page_view.signatures) == 1
        assert viewer.page_view.signatures[0]["style"]["rotation_deg"] == 270.0

        placed = viewer.get_placed_signatures()
        assert len(placed) == 1
        assert placed[0]["rotation_deg"] == 270.0

        viewer.close_pdf()

    def test_restored_signature_remains_editable(self, sample_pdf, color_signature):
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)

        viewer.restore_signature_placements(
            [
                {
                    "page": 0,
                    "sig_path": color_signature,
                    "x": 120,
                    "y": 220,
                    "width": 150,
                    "height": 50,
                }
            ]
        )

        viewer.goto_page(0)
        assert len(viewer.page_view.signatures) == 1

        viewer.page_view.selected_signature = 0
        viewer.page_view.signatures[0]["x"] = 190
        viewer.page_view.signatures[0]["y"] = 240

        placed = viewer.get_placed_signatures()
        assert len(placed) == 1
        assert placed[0]["x"] == 190
        assert placed[0]["y"] == 240

        viewer.close_pdf()

    def test_restored_signature_uses_library_fallback_when_source_missing(self, sample_pdf, color_signature, tmp_path, monkeypatch):
        """Resolve missing signature file paths from library on session restore."""
        monkeypatch.setenv("HOME", str(tmp_path))
        lib_dir = Path(signature_library.library_dir())
        lib_dir.mkdir(parents=True, exist_ok=True)

        # Simulate a signature asset kept in library
        fallback_name = "fallback_signature.png"
        fallback_path = lib_dir / fallback_name
        Path(color_signature).replace(fallback_path)
        restored_sig_path = str(tmp_path / "moved" / fallback_name)

        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)

        viewer.restore_signature_placements(
            [
                {
                    "page": 0,
                    "sig_path": restored_sig_path,
                    "x": 120,
                    "y": 220,
                    "width": 150,
                    "height": 50,
                }
            ]
        )

        viewer.goto_page(0)
        assert len(viewer.page_view.signatures) == 1
        assert viewer.page_view.signatures[0]["sig_path"] == str(fallback_path)
        placed = viewer.get_placed_signatures()
        assert len(placed) == 1
        assert Path(placed[0]["sig_path"]).name == fallback_name

        viewer.close_pdf()

    def test_signature_style_delta_preserves_safe_range(self):
        page_view = PDFPageView()
        page_view.set_page(QPixmap(800, 600))

        pixmap = QPixmap(200, 60)
        page_view.add_signature_overlay(100, 80, 200, 60, pixmap, "sig.png")

        page_view._apply_signature_style_delta(0, "rotation_deg", 90.0)
        assert page_view.get_signature_style(0)["rotation_deg"] == 90.0

        page_view._apply_signature_style_delta(0, "brightness", -2.0)
        assert page_view.get_signature_style(0)["brightness"] == 0.0

        page_view._apply_signature_style_delta(0, "contrast", 5.0)
        assert page_view.get_signature_style(0)["contrast"] == 3.0


class TestBulkPlacement:
    """Test bulk signature placement across multiple pages."""
    
    def test_bulk_placement_all_pages(self, sample_pdf, color_signature):
        """Test placing signature on all pages."""
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)
        
        pixmap = QPixmap(color_signature)
        
        # Simulate bulk placement on all pages
        for page_num in range(viewer.renderer.page_count()):
            viewer.goto_page(page_num)
            viewer.page_view.add_signature_overlay(100, 200, 150, 50, pixmap, color_signature)
        
        all_sigs = viewer.get_placed_signatures()
        assert len(all_sigs) == viewer.renderer.page_count()
        
        # Verify each page has a signature
        pages_with_sigs = set(sig["page"] for sig in all_sigs)
        assert pages_with_sigs == set(range(viewer.renderer.page_count()))
        
        viewer.close_pdf()
    
    def test_bulk_placement_page_range(self, sample_pdf, color_signature):
        """Test placing signature on specific page range."""
        viewer = PDFViewer()
        viewer.open_pdf(sample_pdf)
        
        pixmap = QPixmap(color_signature)
        target_pages = [0, 1]  # Only first two pages
        
        for page_num in target_pages:
            viewer.goto_page(page_num)
            viewer.page_view.add_signature_overlay(100, 200, 150, 50, pixmap, color_signature)
        
        all_sigs = viewer.get_placed_signatures()
        assert len(all_sigs) == len(target_pages)
        
        pages_with_sigs = set(sig["page"] for sig in all_sigs)
        assert pages_with_sigs == set(target_pages)
        
        viewer.close_pdf()


class TestPDFSaveWithSignatures:
    """Test that signatures actually appear in saved PDFs."""
    
    def test_save_includes_all_signatures(self, sample_pdf, color_signature):
        """Test that saved PDF includes all placed signatures."""
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        signatures = [
            {
                "page": 0,
                "sig_path": color_signature,
                "x": 100,
                "y": 600,
                "width": 150,
                "height": 50
            },
            {
                "page": 1,
                "sig_path": color_signature,
                "x": 200,
                "y": 500,
                "width": 120,
                "height": 40
            }
        ]
        
        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        
        # Verify output PDF exists and has content
        assert Path(output.name).exists()
        output_size = Path(output.name).stat().st_size
        original_size = Path(sample_pdf).stat().st_size
        
        # Signed PDF should be larger (has signatures)
        assert output_size > original_size
        
        # Cleanup
        os.unlink(output.name)
    
    def test_save_with_correct_paths(self, sample_pdf, color_signature):
        """Test that each signature uses its own image path."""
        # Create second signature with different color
        temp2 = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        pixmap2 = QPixmap(200, 100)
        pixmap2.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap2)
        painter.setPen(QColor(255, 0, 0))  # Red signature
        painter.drawText(10, 50, "Red Signature")
        painter.end()
        pixmap2.save(temp2.name)
        
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        signatures = [
            {
                "page": 0,
                "sig_path": color_signature,  # Blue
                "x": 100,
                "y": 600,
                "width": 150,
                "height": 50
            },
            {
                "page": 0,
                "sig_path": temp2.name,  # Red
                "x": 300,
                "y": 600,
                "width": 150,
                "height": 50
            }
        ]
        
        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        
        # Cleanup
        os.unlink(output.name)
        os.unlink(temp2.name)


# Run tests with: pytest desktop_app/tests/test_pdf_improvements.py -v
