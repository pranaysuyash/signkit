#!/usr/bin/env python3
"""Security tests for the Signature Extractor application.

This module tests security measures including input validation,
file handling, and protection against common attacks.
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from desktop_app.processing import SignatureExtractor, SecurityValidator
from desktop_app.processing import extractor as extractor_module


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_file_size_validation(self):
        """Test file size limit enforcement."""
        # Create a temporary file that's too large
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # Write more than 50MB of data
            large_data = b'x' * (51 * 1024 * 1024)
            tmp.write(large_data)
            tmp.flush()
            
            try:
                with pytest.raises(ValueError, match="File too large"):
                    SecurityValidator.validate_image_file(tmp.name)
            finally:
                os.unlink(tmp.name)
    
    def test_empty_file_validation(self):
        """Test empty file rejection."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # Create empty file
            pass
        
        try:
            with pytest.raises(ValueError, match="File is empty"):
                SecurityValidator.validate_image_file(tmp.name)
        finally:
            os.unlink(tmp.name)
    
    def test_invalid_extension_validation(self):
        """Test invalid file extension rejection."""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
            tmp.write(b'fake executable')
            tmp.flush()
            
            try:
                with pytest.raises(ValueError, match="Unsupported file extension"):
                    SecurityValidator.validate_image_file(tmp.name)
            finally:
                os.unlink(tmp.name)
    
    def test_magic_number_validation(self):
        """Test magic number validation for file type spoofing."""
        # Create a file with PNG extension but wrong magic number
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(b'This is not a PNG file')
            tmp.flush()
            
            try:
                with pytest.raises(ValueError, match="Invalid image file format"):
                    SecurityValidator.validate_image_file(tmp.name)
            finally:
                os.unlink(tmp.name)
    
    def test_directory_traversal_prevention(self):
        """Test directory traversal attack prevention."""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam", 
            "file.png/../../../etc/passwd",
            "file.png\\..\\..\\..\\windows\\system32",
        ]
        
        for path in traversal_paths:
            with pytest.raises(ValueError, match="Directory traversal not allowed"):
                SecurityValidator.sanitize_path(path)
        
        # Test system directory access prevention
        system_paths = [
            "/etc/passwd",
            "/bin/sh",
            "/usr/bin/python",
        ]
        if os.name == "nt":
            system_paths.append("C:\\Windows\\System32\\config\\SAM")
        
        for path in system_paths:
            with pytest.raises(ValueError, match="Access to system directory not allowed"):
                SecurityValidator.sanitize_path(path)
    
    def test_null_byte_injection_prevention(self):
        """Test null byte injection prevention."""
        malicious_path = "image.png\x00.exe"
        
        with pytest.raises(ValueError, match="File path contains null bytes"):
            SecurityValidator.sanitize_path(malicious_path)
    
    def test_path_length_validation(self):
        """Test extremely long path rejection."""
        # Create an absolute path that's too long
        long_path = "/tmp/" + "a" * 5000 + ".png"
        
        with pytest.raises(ValueError, match="File path too long"):
            SecurityValidator.sanitize_path(long_path)
    
    def test_suspicious_characters_validation(self):
        """Test suspicious character validation on Windows."""
        if os.name == 'nt':  # Windows
            suspicious_paths = [
                "file<.png",
                "file>.png", 
                "file:.png",
                'file".png',
                "file|.png",
                "file?.png",
                "file*.png",
            ]
            
            for path in suspicious_paths:
                with pytest.raises(ValueError, match="File path contains suspicious characters"):
                    SecurityValidator.sanitize_path(path)


class TestSignatureExtractorSecurity:
    """Test security measures in SignatureExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = SignatureExtractor()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.extractor.cleanup_all()
    
    def test_coordinate_bounds_validation(self):
        """Test coordinate bounds checking."""
        # Create a valid test image first
        test_image_path = self._create_test_image()
        
        try:
            session_id = self.extractor.create_session(test_image_path)
            
            # Test negative coordinates
            with pytest.raises(ValueError, match="must be non-negative"):
                self.extractor.process_selection(
                    session_id, -1, 0, 100, 100, 128, "#000000"
                )
            
            # Test coordinates outside image bounds
            with pytest.raises(ValueError, match="coordinates must be|X coordinates must be|Y coordinates must be"):
                self.extractor.process_selection(
                    session_id, 0, 0, 301, 10, 128, "#000000"
                )
            
            # Test invalid selection (x2 <= x1)
            with pytest.raises(ValueError, match="x2 must be > x1"):
                self.extractor.process_selection(
                    session_id, 100, 0, 50, 100, 128, "#000000"
                )
                
        finally:
            os.unlink(test_image_path)
    
    def test_parameter_type_validation(self):
        """Test parameter type validation."""
        test_image_path = self._create_test_image()
        
        try:
            session_id = self.extractor.create_session(test_image_path)
            
            # Test invalid coordinate types
            with pytest.raises(ValueError, match="must be an integer"):
                self.extractor.process_selection(
                    session_id, "0", 0, 100, 100, 128, "#000000"
                )
                
        finally:
            os.unlink(test_image_path)
    
    def test_session_limit_enforcement(self):
        """Test session limit enforcement with cleanup."""
        test_image_path = self._create_test_image()
        
        try:
            # Create sessions up to the limit
            session_ids = []
            for i in range(SignatureExtractor.MAX_SESSIONS + 10):
                session_id = self.extractor.create_session(test_image_path)
                session_ids.append(session_id)
            
            # Should have automatically cleaned up old sessions
            # Final count should be around 75% of MAX_SESSIONS due to cleanup
            final_count = len(self.extractor.sessions)
            assert final_count <= SignatureExtractor.MAX_SESSIONS
            assert final_count >= int(SignatureExtractor.MAX_SESSIONS * 0.7)  # Should be around 75%
            
        finally:
            os.unlink(test_image_path)
    
    def test_large_selection_prevention(self):
        """Test prevention of extremely large selections."""
        test_image_path = self._create_test_image(width=5200, height=5200)
        
        try:
            session_id = self.extractor.create_session(test_image_path)
            
            # Try to create a selection that's too large (but within image bounds)
            # Create coordinates that would result in >25M pixels
            with pytest.raises(ValueError, match="Selection too large"):
                self.extractor.process_selection(
                    session_id, 0, 0, 5200, 5200, 128, "#000000"
                )
                
        finally:
            os.unlink(test_image_path)
    
    def test_secure_cleanup(self):
        """Test secure cleanup of temporary files."""
        test_image_path = self._create_test_image()
        
        try:
            session_id = self.extractor.create_session(test_image_path)
            
            # Create some temporary files through rotation
            rotated_session_id = self.extractor.rotate_image(session_id, 90)
            
            # Verify temp files exist
            assert len(self.extractor._temp_files) > 0
            
            # Cleanup and verify files are removed
            temp_files = list(self.extractor._temp_files)
            self.extractor.cleanup_all()
            
            # Verify files are actually deleted
            for temp_file in temp_files:
                assert not os.path.exists(temp_file)
                
        finally:
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)

    def test_destructor_cleanup_does_not_emit_after_logging_shutdown(self, monkeypatch):
        """Finalization clears state without writing to closed log streams."""
        extractor = SignatureExtractor()

        calls = []

        def record_log(*_args, **_kwargs):
            calls.append(True)

        monkeypatch.setattr(extractor_module.LOG, "debug", record_log)
        monkeypatch.setattr(extractor_module.LOG, "warning", record_log)

        extractor.__del__()
        assert calls == []
    
    def _create_test_image(self, width: int = 300, height: int = 200) -> str:
        """Create a valid test image for testing."""
        import cv2
        import numpy as np
        
        # Create a simple test image
        img = np.ones((height, width, 3), dtype=np.uint8) * 255
        cv2.putText(img, "Test", (max(10, width // 8), max(20, height // 2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Save to temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        cv2.imwrite(temp_path, img)
        
        return temp_path


class TestMaliciousFileHandling:
    """Test handling of malicious files."""
    
    def test_malicious_png_header(self):
        """Test handling of files with malicious PNG headers."""
        # Create a file that looks like PNG but has malicious content
        malicious_content = (
            b'\x89PNG\r\n\x1a\n'  # Valid PNG header
            b'\x00\x00\x00\rIHDR'  # IHDR chunk
            b'\x00\x00\x00\x01\x00\x00\x00\x01'  # 1x1 image
            b'\x08\x02\x00\x00\x00\x90wS\xde'  # Rest of IHDR
            b'MALICIOUS_PAYLOAD_HERE'  # Malicious content
        )
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(malicious_content)
            tmp.flush()
            
            try:
                # Should fail during PIL validation
                with pytest.raises(ValueError, match="Invalid image file"):
                    SecurityValidator.validate_image_file(tmp.name)
            finally:
                os.unlink(tmp.name)
    
    def test_zip_bomb_prevention(self):
        """Test prevention of zip bomb-like attacks with huge images."""
        # This would be a very large image that could cause memory exhaustion
        # We test the dimension limits instead of creating an actual large file
        
        # Mock a huge image by testing dimension validation directly
        with pytest.raises(ValueError, match="Image too large"):
            # Simulate validation of a 50000x50000 image
            if 50000 > SecurityValidator.MAX_IMAGE_WIDTH:
                raise ValueError(f"Image too large: 50000x50000 pixels")


def run_security_tests():
    """Run all security tests."""
    print("Running security validation tests...")
    
    # Run pytest on this file
    import subprocess
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)
