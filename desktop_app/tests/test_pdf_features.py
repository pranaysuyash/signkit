"""Unit tests for PDF features - rendering, signing, and audit logging."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

# Initialize Qt Application for tests that need GUI
from PySide6.QtWidgets import QApplication
if not QApplication.instance():
    app = QApplication(sys.argv)

# Test imports
from desktop_app.pdf.renderer import PDFRenderer
from desktop_app.pdf.signer import PDFSigner, sign_pdf, read_signature_manifest
from desktop_app.pdf.storage import AuditLogger, save_signed_pdf, get_audit_logs_for_pdf
from desktop_app.state.session import PDFState, SessionState


@pytest.fixture
def sample_pdf():
    """Use pre-generated test PDF."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    sample_path = fixtures_dir / "sample.pdf"
    
    if not sample_path.exists():
        pytest.skip(f"Sample PDF not found at {sample_path}")
    
    return str(sample_path)


@pytest.fixture
def sample_signature():
    """Create a simple test signature image."""
    from PySide6.QtGui import QPixmap, QPainter, QColor
    from PySide6.QtCore import Qt
    
    temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    
    pixmap = QPixmap(200, 100)
    pixmap.fill(Qt.GlobalColor.white)
    
    painter = QPainter(pixmap)
    painter.setPen(QColor(0, 0, 0))
    painter.drawText(10, 50, "Test Signature")
    painter.end()
    
    pixmap.save(temp.name)
    
    yield temp.name
    
    # Cleanup
    try:
        os.unlink(temp.name)
    except Exception:
        pass


class TestPDFRenderer:
    """Test PDF rendering functionality."""
    
    def test_open_pdf(self, sample_pdf):
        """Test opening a PDF file."""
        renderer = PDFRenderer(sample_pdf)
        assert renderer.page_count() == 2
        renderer.close()
    
    def test_pdf_not_found(self):
        """Test error handling for non-existent PDF."""
        with pytest.raises(FileNotFoundError):
            PDFRenderer("/nonexistent/file.pdf")
    
    def test_get_page_size(self, sample_pdf):
        """Test getting page dimensions."""
        renderer = PDFRenderer(sample_pdf)
        width, height = renderer.get_page_size(0)
        assert width > 0
        assert height > 0
        assert width == 612.0  # Letter size width in points
        assert height == 792.0  # Letter size height in points
        renderer.close()
    
    def test_render_page(self, sample_pdf):
        """Test rendering a PDF page to QPixmap."""
        renderer = PDFRenderer(sample_pdf)
        pixmap = renderer.render_page(0)
        assert pixmap is not None
        assert not pixmap.isNull()
        assert pixmap.width() > 0
        assert pixmap.height() > 0
        renderer.close()
    
    def test_render_invalid_page(self, sample_pdf):
        """Test rendering an invalid page number."""
        renderer = PDFRenderer(sample_pdf)
        pixmap = renderer.render_page(999)
        assert pixmap is None
        renderer.close()
    
    def test_render_with_zoom(self, sample_pdf):
        """Test rendering with different zoom levels."""
        renderer = PDFRenderer(sample_pdf)
        
        pixmap_100 = renderer.render_page(0, scale=1.0)
        pixmap_200 = renderer.render_page(0, scale=2.0)
        
        assert pixmap_200.width() > pixmap_100.width()
        assert pixmap_200.height() > pixmap_100.height()
        
        renderer.close()


class TestPDFSigner:
    """Test PDF signing functionality."""
    
    def test_open_pdf(self, sample_pdf):
        """Test opening a PDF for signing."""
        signer = PDFSigner(sample_pdf)
        assert signer.input_path == sample_pdf
        signer.close()
    
    def test_pdf_not_found(self):
        """Test error handling for non-existent PDF."""
        with pytest.raises(FileNotFoundError):
            PDFSigner("/nonexistent/file.pdf")
    
    def test_add_signature(self, sample_pdf, sample_signature):
        """Test adding a signature to PDF."""
        signer = PDFSigner(sample_pdf)
        
        # Add signature to first page
        signer.add_signature(
            page_num=0,
            sig_image_path=sample_signature,
            x=100,
            y=600,
            width=150,
            height=50
        )
        
        # Save to temporary file
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        signer.save(output.name)
        signer.close()
        
        # Verify output exists and has content
        assert Path(output.name).exists()
        assert Path(output.name).stat().st_size > 0
        
        # Cleanup
        os.unlink(output.name)
    
    def test_add_signature_invalid_page(self, sample_pdf, sample_signature):
        """Test adding signature to invalid page."""
        signer = PDFSigner(sample_pdf)
        
        with pytest.raises(ValueError):
            signer.add_signature(
                page_num=999,
                sig_image_path=sample_signature,
                x=100,
                y=600,
                width=150,
                height=50
            )
        
        signer.close()
    
    def test_sign_pdf_convenience_function(self, sample_pdf, sample_signature):
        """Test the sign_pdf convenience function."""
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        signatures = [
            {
                "page": 0,
                "sig_path": sample_signature,
                "x": 100,
                "y": 600,
                "width": 150,
                "height": 50
            },
            {
                "page": 1,
                "sig_path": sample_signature,
                "x": 200,
                "y": 500,
                "width": 120,
                "height": 40
            }
        ]
        
        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        assert Path(output.name).exists()
        
        # Cleanup
        os.unlink(output.name)

    def test_sign_pdf_style_controls_applied(self, sample_pdf, sample_signature):
        """Test signature style metadata is accepted by the PDF signer."""
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

        signatures = [
            {
                "page": 0,
                "sig_path": sample_signature,
                "x": 100,
                "y": 600,
                "width": 150,
                "height": 50,
                "rotation_deg": 45,
                "brightness": 1.2,
                "contrast": 1.1,
                "saturation": 0.9,
            },
        ]

        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        assert Path(output.name).exists()
        assert Path(output.name).stat().st_size > 0

        os.unlink(output.name)

    def test_sign_pdf_manifest_is_embedded(self, sample_pdf, sample_signature):
        """Test that signed PDFs contain embedded signature placement metadata."""
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

        signatures = [
            {
                "page": 0,
                "sig_path": sample_signature,
                "x": 100,
                "y": 600,
                "width": 150,
                "height": 50,
                "rotation_deg": 15,
                "brightness": 1.2,
                "contrast": 1.1,
                "saturation": 0.9,
            },
        ]

        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success

        manifest = read_signature_manifest(output.name)
        assert isinstance(manifest, list)
        assert len(manifest) == 1
        assert manifest[0]["page"] == 0
        assert manifest[0]["x"] == 100
        assert manifest[0]["y"] == 600
        assert manifest[0]["width"] == 150
        assert manifest[0]["height"] == 50
        assert manifest[0]["rotation_deg"] == 15.0
        assert manifest[0]["sig_image_data"]

        os.unlink(output.name)

    def test_sign_pdf_handles_zero_x_coordinate(self, sample_pdf, sample_signature):
        """Test PDF signing still works when X coordinate is zero."""
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

        signatures = [
            {
                "page": 0,
                "sig_path": sample_signature,
                "x": 0,
                "y": 600,
                "width": 150,
                "height": 50,
            },
        ]

        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        assert Path(output.name).exists()
        assert Path(output.name).stat().st_size > 0

        os.unlink(output.name)


class TestAuditLogging:
    """Test audit logging functionality."""
    
    def test_create_audit_logger(self, sample_pdf):
        """Test creating an audit logger."""
        logger = AuditLogger(sample_pdf, "test@example.com")
        assert logger.pdf_path == sample_pdf
        assert logger.user_email == "test@example.com"
        assert Path(logger.log_file).parent.exists()
        
        # Cleanup
        if Path(logger.log_file).exists():
            os.unlink(logger.log_file)
    
    def test_log_open(self, sample_pdf):
        """Test logging PDF open operation."""
        logger = AuditLogger(sample_pdf, "test@example.com")
        logger.log_open()
        
        # Verify log file exists
        assert Path(logger.log_file).exists()
        
        # Read and verify log content
        with open(logger.log_file, "r") as f:
            content = f.read()
            assert "open_pdf" in content
            assert sample_pdf in content
        
        # Cleanup
        os.unlink(logger.log_file)
    
    def test_log_place_signature(self, sample_pdf):
        """Test logging signature placement."""
        logger = AuditLogger(sample_pdf)
        logger.log_place_signature(0, "signature.png", 100, 200, 150, 50)
        
        # Verify log content
        with open(logger.log_file, "r") as f:
            content = f.read()
            assert "place_signature" in content
            assert "signature.png" in content
            assert "100" in content
            assert "200" in content
        
        # Cleanup
        os.unlink(logger.log_file)
    
    def test_log_save(self, sample_pdf):
        """Test logging PDF save operation."""
        logger = AuditLogger(sample_pdf)
        
        # Create a dummy output file
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        output.write(b"test content")
        output.close()
        
        logger.log_save(output.name, 2)
        
        # Verify log content
        with open(logger.log_file, "r") as f:
            content = f.read()
            assert "save_pdf" in content
            assert output.name in content
            assert "signature_count" in content
        
        # Cleanup
        os.unlink(logger.log_file)
        os.unlink(output.name)
    
    def test_log_error(self, sample_pdf):
        """Test logging errors."""
        logger = AuditLogger(sample_pdf)
        logger.log_error("test_error", "Test error message")
        
        # Verify log content
        with open(logger.log_file, "r") as f:
            content = f.read()
            assert "error" in content
            assert "test_error" in content
            assert "Test error message" in content
        
        # Cleanup
        os.unlink(logger.log_file)
    
    def test_get_audit_logs(self, sample_pdf):
        """Test retrieving audit logs."""
        logger = AuditLogger(sample_pdf)
        logger.log_open()
        logger.log_place_signature(0, "sig.png", 100, 200, 150, 50)
        logger.log_save("/output.pdf", 1)
        
        # Retrieve logs — filter to entries created by this test
        all_logs = get_audit_logs_for_pdf(sample_pdf)
        test_logs = [l for l in all_logs if l.user_email is None]
        assert len(test_logs) >= 3
        assert test_logs[-3].operation == "open_pdf"
        assert test_logs[-2].operation == "place_signature"
        assert test_logs[-1].operation == "save_pdf"
        
        # Cleanup
        os.unlink(logger.log_file)


class TestPDFState:
    """Test PDF state management."""
    
    def test_create_pdf_state(self):
        """Test creating PDF state."""
        state = PDFState()
        assert state.current_pdf_path is None
        assert state.current_page == 0
        assert state.total_pages == 0
        assert state.zoom_level == 1.0
        assert len(state.placed_signatures) == 0
    
    def test_session_state_pdf_integration(self):
        """Test PDF state integration with SessionState."""
        session = SessionState()
        assert session.pdf_state is None
        
        # Initialize PDF state
        session.init_pdf_state()
        assert session.pdf_state is not None
        assert isinstance(session.pdf_state, PDFState)
        
        # Clear PDF state
        session.clear_pdf_state()
        assert session.pdf_state is None
    
    def test_placed_signatures_tracking(self):
        """Test tracking placed signatures."""
        state = PDFState()
        
        # Add signatures
        state.placed_signatures.append({
            "page": 0,
            "sig_path": "signature1.png",
            "x": 100,
            "y": 200,
            "width": 150,
            "height": 50
        })
        
        state.placed_signatures.append({
            "page": 1,
            "sig_path": "signature2.png",
            "x": 200,
            "y": 300,
            "width": 120,
            "height": 40
        })
        
        assert len(state.placed_signatures) == 2
        assert state.placed_signatures[0]["page"] == 0
        assert state.placed_signatures[1]["page"] == 1


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_signing_workflow(self, sample_pdf, sample_signature):
        """Test complete PDF signing workflow with audit logging."""
        # Initialize audit logger
        logger = AuditLogger(sample_pdf, "test@example.com")
        logger.log_open()
        
        # Place signatures
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
        
        # Log placement
        for sig in signatures:
            logger.log_place_signature(
                sig["page"], sig["sig_path"],
                sig["x"], sig["y"],
                sig["width"], sig["height"]
            )
        
        # Sign PDF
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        success = sign_pdf(sample_pdf, output.name, signatures)
        assert success
        
        # Log save
        logger.log_save(output.name, len(signatures))
        
        # Verify audit trail
        logs = get_audit_logs_for_pdf(sample_pdf)
        assert len(logs) >= 3  # open, place, save
        
        # Verify output
        assert Path(output.name).exists()
        assert Path(output.name).stat().st_size > 0
        
        # Cleanup
        os.unlink(logger.log_file)
        os.unlink(output.name)


# Run tests with: pytest desktop_app/tests/test_pdf_features.py -v
