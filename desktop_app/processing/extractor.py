"""Local signature extraction engine.

This module provides local image processing capabilities for signature extraction,
eliminating the need for backend API calls and enabling offline-first operation.

SECURITY ARCHITECTURE:
=====================
This module implements defense-in-depth security with multiple validation layers:

1. File Extension Check
   - First line of defense (weakest)
   - Blocks obvious non-image files (.exe, .pdf, .zip)
   - Easy to bypass by renaming files

2. Magic Number Validation (File Signature)
   - Second line of defense (strong)
   - Reads actual file binary headers
   - Cannot be bypassed by simple file renaming
   - See SecurityValidator.validate_image_file() for implementation details

3. File Size Limits
   - Prevents denial-of-service via huge files
   - 50MB max to balance security vs. usability
   - Protects against memory exhaustion attacks

4. Image Dimension Validation
   - Prevents memory exhaustion from maliciously crafted images
   - Max 10,000 x 10,000 pixels per dimension
   - Max 50 megapixels total
   - A 10000x10000 image at 24-bit color = ~286MB in memory

5. PIL/Pillow Verification
   - PIL.Image.verify() checks file structure integrity
   - Detects corrupted or malformed images
   - Prevents crashes from crafted files exploiting image library bugs

6. Path Sanitization
   - Prevents directory traversal attacks (../../../etc/passwd)
   - Blocks access to system directories (/etc, /bin, /sys, etc.)
   - See SecurityValidator.sanitize_path() for implementation

WHY THIS MATTERS:
================
User-uploaded files are the #1 attack vector in web and desktop applications:
- Malicious files can exploit bugs in image processing libraries (CVE history)
- Large files can exhaust system memory (DoS attack)
- Path traversal can expose sensitive system files
- File type spoofing can bypass naive validation

Real-world examples:
- ImageTragick (CVE-2016-3714): ImageMagick RCE via crafted image files
- LibPNG vulnerabilities: Buffer overflows from malformed PNG chunks
- JPEG parsing bugs: Crashes and potential code execution

This multi-layer approach ensures the app is production-ready and secure.
"""

from __future__ import annotations

import logging
import os
import tempfile
import time
import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

LOG = logging.getLogger(__name__)


@dataclass
class ProcessingParams:
    """Parameters for signature processing."""
    threshold: int
    color: str
    auto_clean: bool = False
    
    def __post_init__(self):
        """Validate parameters after initialization."""
        if not (0 <= self.threshold <= 255):
            raise ValueError(f"Threshold must be between 0 and 255, got {self.threshold}")
        
        # Validate color format
        if not self.color.startswith("#") or len(self.color) != 7:
            raise ValueError(f"Color must be in #RRGGBB format, got {self.color}")
        
        try:
            int(self.color[1:], 16)
        except ValueError:
            raise ValueError(f"Invalid hex color format: {self.color}")

from desktop_app.processing.watermark import WatermarkEngine

@dataclass
class ProcessingSession:
    """Represents an image processing session."""
    session_id: str
    original_image: np.ndarray
    processed_image: Optional[np.ndarray]
    created_at: float
    file_path: str
    dimensions: Tuple[int, int]
    processing_params: Optional[ProcessingParams] = None
    
    @property
    def width(self) -> int:
        """Get image width."""
        return self.dimensions[1]
    
    @property
    def height(self) -> int:
        """Get image height."""
        return self.dimensions[0]


class SecurityValidator:
    """Validates file inputs for security.
    
    This class performs multiple layers of validation to protect against:
    1. File type spoofing attacks (renaming malicious files to .jpg/.png)
    2. Path traversal attacks (accessing system files)
    3. Memory exhaustion attacks (processing huge images)
    4. Malformed file attacks (corrupted or crafted files that crash the app)
    
    Security is critical because:
    - Users can upload any file from their system
    - Malicious files could exploit image processing libraries (PIL, OpenCV)
    - Without validation, attackers could crash the app or potentially execute code
    """
    
    ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/jpg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
    
    # Magic number signatures for image validation
    # Note: These are kept for reference but validation uses prefix matching (see validate_image_file)
    IMAGE_SIGNATURES = {
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'\xff\xd8\xff\xe0': 'image/jpeg',  # JFIF
        b'\xff\xd8\xff\xe1': 'image/jpeg',  # EXIF
        b'\xff\xd8\xff\xe2': 'image/jpeg',  # Canon
        b'\xff\xd8\xff\xe3': 'image/jpeg',  # Samsung
        b'\xff\xd8\xff\xe8': 'image/jpeg',  # SPIFF
        b'\xff\xd8\xff\xdb': 'image/jpeg',  # Raw JPEG
        b'\xff\xd8\xff\xee': 'image/jpeg',  # Adobe JPEG
        b'\xff\xd8\xff\xfe': 'image/jpeg',  # JPEG with comment
    }
    
    # Maximum image dimensions to prevent memory exhaustion
    MAX_IMAGE_WIDTH = 10000
    MAX_IMAGE_HEIGHT = 10000
    MAX_PIXELS = 50_000_000  # 50 megapixels
    
    @classmethod
    def validate_image_file(cls, file_path: str) -> None:
        """Validate image file for security and format compliance.
        
        Args:
            file_path: Path to the image file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or unsafe
        """
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max {cls.MAX_FILE_SIZE})")
        
        if file_size == 0:
            raise ValueError("File is empty")
        
        # Check file extension
        if path.suffix.lower() not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {path.suffix}")
        
        # Validate magic numbers (file signatures)
        # CRITICAL SECURITY: Magic numbers prevent file type spoofing
        # 
        # WHY THIS IS NEEDED:
        # - File extensions (.jpg, .png) can be easily faked by renaming files
        # - A malicious .exe file renamed to .jpg would pass extension checks
        # - Magic numbers are the ACTUAL file format identifiers in the binary data
        # 
        # HOW IT WORKS:
        # - Every file format has a unique signature in its first few bytes
        # - PNG: Always starts with \x89PNG\r\n\x1a\n (8 bytes)
        # - JPEG: Always starts with \xff\xd8\xff (3 bytes) followed by marker
        # 
        # IMPLEMENTATION STRATEGY:
        # - PNG: Exact match required (signature is always the same)
        # - JPEG: Prefix match (\xff\xd8\xff) because the 4th byte varies:
        #   * \xe0 = JFIF (most common, from photo editing software)
        #   * \xe1 = EXIF (from digital cameras with metadata)
        #   * \xe2 = Canon cameras
        #   * \xfe = JPEG with comment
        #   * Many more variants exist
        # 
        # BUGFIX HISTORY:
        # - Original implementation checked only specific JPEG markers (e0, e1, db, ee)
        # - Failed for images from certain cameras/software with different markers
        # - Fixed by checking universal JPEG prefix (\xff\xd8\xff) instead
        # - This accepts ALL valid JPEG files while still preventing spoofed files
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                
            valid_signature = False
            
            # Check PNG signature (exact match required)
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                valid_signature = True
            # Check JPEG signature (universal prefix match)
            # Accepts any JPEG variant (JFIF, EXIF, Canon, Samsung, etc.)
            elif header.startswith(b'\xff\xd8\xff'):
                valid_signature = True
            
            if not valid_signature:
                raise ValueError("Invalid image file format (magic number check failed)")
                
        except (OSError, IOError) as e:
            raise ValueError(f"Cannot read file: {e}")
        
        # Additional PIL validation and dimension checking
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
                
            # Re-open for dimension checking (verify() closes the image)
            with Image.open(file_path) as img:
                width, height = img.size
                
                # Check image dimensions
                if width > cls.MAX_IMAGE_WIDTH or height > cls.MAX_IMAGE_HEIGHT:
                    raise ValueError(
                        f"Image too large: {width}x{height} pixels "
                        f"(max {cls.MAX_IMAGE_WIDTH}x{cls.MAX_IMAGE_HEIGHT})"
                    )
                
                # Check total pixel count
                total_pixels = width * height
                if total_pixels > cls.MAX_PIXELS:
                    raise ValueError(
                        f"Image has too many pixels: {total_pixels:,} "
                        f"(max {cls.MAX_PIXELS:,})"
                    )
                
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")
    
    @classmethod
    def sanitize_path(cls, file_path: str) -> str:
        """Sanitize file path to prevent directory traversal and other attacks.
        
        Args:
            file_path: Input file path
            
        Returns:
            Sanitized absolute path
            
        Raises:
            ValueError: If path is unsafe
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")
        
        # Check for null bytes (can cause issues on some systems)
        if '\x00' in file_path:
            raise ValueError("File path contains null bytes")
        
        # Check for directory traversal attempts
        if '..' in file_path:
            raise ValueError("Directory traversal not allowed")
        
        # Check for suspicious absolute paths (security risk)
        if os.path.isabs(file_path):
            # Block access to critical system directories (but allow temp dirs)
            dangerous_paths = ['/etc/', '/bin/', '/usr/bin/', '/sbin/', '/usr/sbin/', 
                             '/root/', '/sys/', '/proc/', '/dev/',
                             'C:\\Windows\\System32\\', 'C:\\Program Files\\']
            
            normalized_path = os.path.normpath(file_path).lower()
            for dangerous in dangerous_paths:
                if normalized_path.startswith(dangerous.lower()):
                    raise ValueError(f"Access to system directory not allowed: {file_path}")
            
            # Special check for /var but allow temp directories
            if normalized_path.startswith('/var/') and not any(temp_dir in normalized_path for temp_dir in ['/tmp/', '/temp/', '/folders/']):
                raise ValueError(f"Access to system directory not allowed: {file_path}")
            
            # Check path length for absolute paths
            if len(file_path) > 4096:
                raise ValueError("File path too long")
        
        # Convert to absolute path and resolve any symlinks/.. components
        try:
            abs_path = os.path.abspath(os.path.realpath(file_path))
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid file path: {e}")
        
        # Ensure the resolved path is what we expect
        if abs_path != os.path.normpath(abs_path):
            raise ValueError(f"Unsafe file path after normalization: {file_path}")
        
        # Check for suspicious characters (Windows-specific)
        if os.name == 'nt':
            suspicious_chars = '<>:"|?*'
            if any(char in file_path for char in suspicious_chars):
                raise ValueError(f"File path contains suspicious characters: {file_path}")
        
        return abs_path


@dataclass(frozen=True)
class SignatureCandidate:
    """A detected signature box and its ranking score."""

    bbox: Tuple[int, int, int, int]
    confidence: float
    source: str


def _find_color_signature_candidates(
    image: np.ndarray,
) -> list[tuple[Tuple[int, int, int, int], float]]:
    """Return blue-ink candidates sorted by deterministic ranking score."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blue_dominance = image[:, :, 0].astype(np.int16) - image[:, :, 2].astype(np.int16)
    color_mask = ((blue_dominance > 60) & (gray < 210)).astype(np.uint8) * 255
    color_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, color_kernel)
    color_mask = cv2.dilate(color_mask, color_kernel, iterations=2)
    color_contours, _ = cv2.findContours(
        color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    color_candidates = []
    image_area = image.shape[0] * image.shape[1]
    for contour in color_contours:
        area = cv2.contourArea(contour)
        x, y, width, height = cv2.boundingRect(contour)
        if area < 500 or area >= image_area * 0.5 or width <= 30 or height <= 15:
            continue
        dominance_score = float(
            blue_dominance[y : y + height, x : x + width].clip(min=0).sum()
        )
        color_candidates.append((dominance_score, x, y, width, height))
    if not color_candidates:
        return []
    max_score = max(candidate[0] for candidate in color_candidates) or 1.0
    ranked = sorted(color_candidates, reverse=True)
    selected: list[tuple[Tuple[int, int, int, int], float]] = []
    for score, x, y, width, height in ranked:
        candidate_box = (x, y, x + width, y + height)
        candidate_area = width * height
        duplicate = False
        for selected_box, _ in selected:
            ix1 = max(candidate_box[0], selected_box[0])
            iy1 = max(candidate_box[1], selected_box[1])
            ix2 = min(candidate_box[2], selected_box[2])
            iy2 = min(candidate_box[3], selected_box[3])
            intersection = max(0, ix2 - ix1) * max(0, iy2 - iy1)
            selected_area = (selected_box[2] - selected_box[0]) * (selected_box[3] - selected_box[1])
            union = candidate_area + selected_area - intersection
            if union and intersection / union >= 0.5:
                duplicate = True
                break
        if not duplicate:
            selected.append((candidate_box, min(1.0, score / max_score)))
    return selected


def _find_color_signature_candidate(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Return the strongest blue-ink candidate in a photographed document."""
    candidates = _find_color_signature_candidates(image)
    return candidates[0][0] if candidates else None


class SignatureExtractor:
    """Local image processing engine for signature extraction."""
    
    # Resource limits to prevent abuse
    MAX_SESSIONS = 100
    MAX_TEMP_FILES = 50
    
    def __init__(self):
        """Initialize the signature extractor."""
        self.sessions: Dict[str, ProcessingSession] = {}
        self._temp_files: set = set()
        self.watermarker = WatermarkEngine()
        
    def create_session(self, image_path: str) -> str:
        """Create new processing session with image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Session ID for the created session
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image file is invalid or unsafe
        """
        # Check resource limits
        if len(self.sessions) >= self.MAX_SESSIONS:
            # Clean up old sessions to make room
            self._cleanup_old_sessions()
            
        if len(self.sessions) >= self.MAX_SESSIONS:
            raise ValueError(f"Too many active sessions (max {self.MAX_SESSIONS})")
        
        # Validate and sanitize input
        sanitized_path = SecurityValidator.sanitize_path(image_path)
        SecurityValidator.validate_image_file(sanitized_path)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        try:
            # Load and validate image using OpenCV
            image = cv2.imread(sanitized_path, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError(f"Could not load image: {sanitized_path}")
            
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Create session
            session = ProcessingSession(
                session_id=session_id,
                original_image=image,
                processed_image=None,
                created_at=time.time(),
                file_path=sanitized_path,
                dimensions=(height, width)
            )
            
            self.sessions[session_id] = session
            
            LOG.info(f"Created session {session_id} for image {sanitized_path} ({width}x{height})")
            return session_id
            
        except Exception as e:
            LOG.error(f"Failed to create session for {sanitized_path}: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ProcessingSession]:
        """Get processing session by ID.

        Args:
            session_id: Session identifier

        Returns:
            ProcessingSession if found, None otherwise
        """
        return self.sessions.get(session_id)

    def auto_detect_signatures(
        self,
        session_id: str,
        *,
        max_candidates: int = 2,
        min_confidence: float = 0.75,
    ) -> list[SignatureCandidate]:
        """Detect zero or more scored signature candidates.

        Confidence is a deterministic per-image ranking score, not a calibrated
        probability. The color path can emit multiple boxes; the existing
        single-box detector remains the grayscale fallback.
        """
        if max_candidates < 1:
            raise ValueError("max_candidates must be at least 1")
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        session = self.get_session(session_id)
        if session is None:
            return []
        color_candidates = _find_color_signature_candidates(session.original_image)
        candidates = [
            SignatureCandidate(bbox=bbox, confidence=confidence, source="blue-ink")
            for bbox, confidence in color_candidates
            if confidence >= min_confidence
        ][:max_candidates]
        if candidates:
            return candidates
        fallback = self.auto_detect_signature(session_id)
        fallback_confidence = 0.4
        if fallback is None or fallback_confidence < min_confidence:
            return []
        return [
            SignatureCandidate(
                bbox=fallback,
                confidence=fallback_confidence,
                source="grayscale-fallback",
            )
        ]

    def auto_detect_signature(self, session_id: str) -> Optional[Tuple[int, int, int, int]]:
        """Detect the most likely signature region in the image.
        
        Uses contour detection to find the largest non-background region
        that looks like ink/marker on paper.
        
        Args:
            session_id: Processing session ID
            
        Returns:
            (x1, y1, x2, y2) bounding box of detected signature, or None if not found
        """
        session = self.get_session(session_id)
        if session is None:
            return None
        
        # Parameter rationale (heuristic defaults, not tuned against a
        # labeled signature dataset): use Otsu as a baseline and keep a
        # bounded offset so beige or shadowed paper does not become "ink".
        # The previous fixed threshold of 180 fragmented the real sample into
        # separate contours, then returned only the largest left-hand stroke.
        image = session.original_image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Photographed documents commonly use blue ink while the page text,
        # lines, and nearby objects are grayscale. Use that signal to create
        # a local candidate before falling back to the grayscale envelope.
        # These parameters were selected on the external corpus development
        # split only; the publisher's validation split was not used for tuning.
        color_candidate = _find_color_signature_candidate(image)
        if color_candidate is not None:
            detected = color_candidate
            LOG.info("Auto-detected color signature candidate: (%d,%d)-(%d,%d)", *detected)
            return detected

        otsu_threshold, _ = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        global_threshold = int(np.clip(otsu_threshold + 16, 140, 180))
        _, binary_global = cv2.threshold(
            gray, global_threshold, 255, cv2.THRESH_BINARY_INV
        )

        # Prefer the complete global ink envelope. Cursive signatures are
        # often made of many disconnected contours, so choosing one contour
        # cannot represent the user's full mark.
        ink_y, ink_x = np.where(binary_global > 0)
        if ink_x.size:
            x1, x2 = int(ink_x.min()), int(ink_x.max()) + 1
            y1, y2 = int(ink_y.min()), int(ink_y.max()) + 1
            width = x2 - x1
            height = y2 - y1
            image_area = image.shape[0] * image.shape[1]
            envelope_area = width * height
            aspect_ratio = width / height if height else 0
            if (
                width > 30
                and height > 15
                and 0.2 < aspect_ratio < 10
                and envelope_area < image_area * 0.9
            ):
                padding = max(10, min(20, round(min(width, height) * 0.05)))
                detected = (
                    max(0, x1 - padding),
                    max(0, y1 - padding),
                    min(image.shape[1], x2 + padding),
                    min(image.shape[0], y2 + padding),
                )
                LOG.info(
                    "Auto-detected signature envelope: (%d,%d)-(%d,%d) threshold=%d",
                    *detected,
                    global_threshold,
                )
                return detected

        # Adaptive threshold fallback for images where the global envelope is
        # too broad or does not satisfy the basic shape checks.
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 51, 10
        )
        combined = cv2.bitwise_or(binary, binary_global)

        # Morphological operations to clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Filter contours by area — too small = noise, too large = background
        img_area = image.shape[0] * image.shape[1]
        min_area = img_area * 0.001  # At least 0.1% of image
        max_area = img_area * 0.8    # Not more than 80% of image

        valid_contours = []
        for c in contours:
            area = cv2.contourArea(c)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = w / h if h > 0 else 0
                # Signatures are typically wider than tall, but not extreme
                if 0.2 < aspect_ratio < 10 and w > 30 and h > 15:
                    valid_contours.append((area, x, y, w, h))
        
        if not valid_contours:
            # Fallback: just use the largest contour
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return (x, y, x + w, y + h)
        
        # Merge nearby contours into a single bounding box
        valid_contours.sort(key=lambda t: t[0], reverse=True)
        # Take the largest valid contour region
        _, x, y, w, h = valid_contours[0]
        
        # Expand the bounding box slightly for better coverage
        padding = 10
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        LOG.info(f"Auto-detected signature region: ({x1},{y1})-({x2},{y2})")
        return (x1, y1, x2, y2)
    
    def process_selection(
        self,
        session_id: str,
        x1: int, y1: int, x2: int, y2: int,
        threshold: int,
        color: str,
        auto_clean: bool = False
    ) -> bytes:
        """Process selected region with given parameters.
        
        Args:
            session_id: Session identifier
            x1, y1, x2, y2: Selection coordinates
            threshold: Threshold value for binary processing
            color: Target color in #RRGGBB format
            
        Returns:
            PNG image bytes of processed signature
            
        Raises:
            ValueError: If session not found or parameters invalid
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Validate parameters
        params = ProcessingParams(threshold=threshold, color=color, auto_clean=auto_clean)
        self._validate_coordinates(x1, y1, x2, y2, session.width, session.height)
        
        try:
            # Ensure coordinates are within image bounds
            height, width = session.original_image.shape[:2]
            x1 = max(0, min(x1, width))
            x2 = max(0, min(x2, width))
            y1 = max(0, min(y1, height))
            y2 = max(0, min(y2, height))
            
            # Validate selection area
            if x2 <= x1 or y2 <= y1:
                raise ValueError("Invalid selection area")
            
            # Log processing info without sensitive data
            LOG.info(f"Processing selection {width}x{height} area with threshold={threshold}")
            
            # Crop the selected region
            cropped_image = session.original_image[y1:y2, x1:x2]
            
            # Convert to grayscale for thresholding
            gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            
            if auto_clean:
                # Auto-clean: Adaptive thresholding for shadow removal
                # Block size 21, C=10 are optimized for document signatures
                mask = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY_INV, 21, 10
                )
                # Morphological opening to remove small noise (salt noise)
                kernel = np.ones((2,2), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            else:
                # Standard: Apply global threshold to create binary mask
                _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
            
            # Convert color hex string (#RRGGBB) to BGR tuple for OpenCV
            hex_color = color.lstrip("#")
            r_val = int(hex_color[0:2], 16)
            g_val = int(hex_color[2:4], 16)
            b_val = int(hex_color[4:6], 16)
            color_bgr = (b_val, g_val, r_val)
            
            # Create colored image
            color_image = np.zeros_like(cropped_image, dtype=np.uint8)
            color_image[:, :] = color_bgr
            
            # Apply mask to create colored signature
            result_image = cv2.bitwise_and(color_image, color_image, mask=mask)
            
            # Convert BGR to RGB for PIL
            result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            
            # Add alpha channel for transparency
            r_channel, g_channel, b_channel = cv2.split(result_image_rgb)
            alpha = mask
            final_image = cv2.merge([r_channel, g_channel, b_channel, alpha])
            
            # Convert to PIL Image and save as PNG bytes
            final_image_pil = Image.fromarray(final_image, 'RGBA')
            
            # Save to bytes
            image_io = BytesIO()
            final_image_pil.save(image_io, format="PNG")
            image_bytes = image_io.getvalue()
            
            # Store processed image in session
            session.processed_image = final_image
            session.processing_params = params
            
            LOG.info(f"Successfully processed selection, output size: {len(image_bytes)} bytes")
            return image_bytes
            
        except Exception as e:
            LOG.error(f"Failed to process selection for session {session_id}: {e}")
            raise
    
    def process_selection_svg(
        self,
        session_id: str,
        x1: int, y1: int, x2: int, y2: int,
        threshold: int,
        color: str,
        auto_clean: bool = False
    ) -> str:
        """Process selected region and return SVG string.
        
        Args:
            session_id: Session identifier
            x1, y1, x2, y2: Selection coordinates
            threshold: Threshold value
            color: Target color in #RRGGBB format
            
        Returns:
            SVG XML string
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
            
        # Validate parameters
        self._validate_coordinates(x1, y1, x2, y2, session.width, session.height)
        
        try:
            # Crop the selected region
            cropped_image = session.original_image[y1:y2, x1:x2]
            
            # Convert to grayscale
            gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            
            if auto_clean:
                # Auto-clean: Adaptive thresholding
                mask = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY_INV, 21, 10
                )
                kernel = np.ones((2,2), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            else:
                # Standard threshold
                _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Generate SVG content
            height, width = mask.shape
            svg_parts = [
                f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
                f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
                f'<g fill="{color}">'
            ]
            
            for contour in contours:
                # Approximate contour to reduce points (smoother, smaller file)
                epsilon = 1.0  # Precision factor
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) < 3:
                    continue
                    
                # Build path data
                path_data = "M"
                for point in approx:
                    x, y = point[0]
                    path_data += f" {x},{y}"
                path_data += " Z"
                
                svg_parts.append(f'<path d="{path_data}" />')
                
            svg_parts.append('</g>')
            svg_parts.append('</svg>')
            
            return "\n".join(svg_parts)
            
        except Exception as e:
            LOG.error(f"Failed to generate SVG for session {session_id}: {e}")
            raise

    def process_selection_kmeans(
        self,
        session_id: str,
        x1: int, y1: int, x2: int, y2: int,
        k: int = 2
    ) -> bytes:
        """Process selected region using K-Means clustering (Forensic Mode).
        
        Args:
            session_id: Session identifier
            x1, y1, x2, y2: Selection coordinates
            k: Number of clusters (default 2: Ink vs Background)
            
        Returns:
            PNG bytes of the extracted signature
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
            
        # Validate parameters
        self._validate_coordinates(x1, y1, x2, y2, session.width, session.height)
        
        try:
            # Crop the selected region
            cropped_image = session.original_image[y1:y2, x1:x2]
            
            # Convert to LAB color space for better color separation
            lab_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2LAB)
            
            # Reshape to 2D array of pixels
            pixel_values = lab_image.reshape((-1, 3))
            pixel_values = np.float32(pixel_values)
            
            # Define criteria = ( type, max_iter = 100, epsilon = 1.0 )
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            
            # Apply KMeans
            _, labels, centers = cv2.kmeans(
                pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
            )
            
            # Convert back to 8 bit values
            centers = np.uint8(centers)
            
            # Determine which cluster is the "ink"
            # Usually ink is darker (lower L value in LAB)
            # L channel is index 0 in LAB
            #
            # Known limitation: this always picks the darkest of the k
            # clusters as "ink," which assumes dark-ink-on-light-background.
            # It will misidentify ink on light pen / dark paper (e.g. white
            # gel pen on black paper), and on documents with strong shadows
            # or multiple ink colors the darkest cluster may be a shadow or
            # printed text rather than the actual signature. There is no
            # confidence signal on this cluster-assignment step, so a
            # misidentification currently fails silently (produces a wrong
            # but plausible-looking extraction, not an error). Fixing this
            # properly (e.g. detecting background lightness and choosing
            # the cluster further from it, or surfacing a confidence score
            # to the user) is a real algorithmic improvement, not just a
            # parameter tweak -- flagged here rather than attempted without
            # test images covering these cases.
            l_values = centers[:, 0]
            ink_cluster_idx = np.argmin(l_values)
            
            # Create mask: 255 where label == ink_cluster_idx, else 0
            labels = labels.flatten()
            mask = np.zeros(labels.shape, dtype=np.uint8)
            mask[labels == ink_cluster_idx] = 255
            
            # Reshape mask back to image dimensions
            mask = mask.reshape(cropped_image.shape[:2])
            
            # Morphological cleanup (remove small noise)
            kernel = np.ones((2,2), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Apply mask to original image (or just return black ink on transparent)
            # For signature extraction, we usually want the original ink color or black
            # Let's keep original ink color but with alpha channel
            
            # Create RGBA image
            b, g, r = cv2.split(cropped_image)
            rgba = cv2.merge([b, g, r, mask])
            
            # Convert to bytes
            is_success, buffer = cv2.imencode(".png", rgba)
            if not is_success:
                raise RuntimeError("Failed to encode result image")
                
            png_bytes = buffer.tobytes()
            
            # Apply invisible watermark
            try:
                import time
                import hashlib
                from desktop_app.config import APP_VERSION

                meta = {
                    "app": "SignKit",
                    "version": APP_VERSION,
                    "timestamp": int(time.time()),
                    "source_hash": hashlib.md5(session.file_path.encode()).hexdigest() if session.file_path else "unknown",
                    "mode": "forensic"
                }
                png_bytes = self.watermarker.embed_watermark(png_bytes, meta)
            except Exception as e:
                LOG.error(f"Watermarking failed: {e}")
                
            return png_bytes
            
        except Exception as e:
            LOG.error(f"Failed to process selection (K-Means) for session {session_id}: {e}")
            raise

    def analyze_quality(
        self,
        session_id: str,
        x1: int, y1: int, x2: int, y2: int
    ) -> dict:
        """Analyze the quality of the selected region (Health Score).
        
        Args:
            session_id: Session identifier
            x1, y1, x2, y2: Selection coordinates
            
        Returns:
            Dictionary containing quality metrics:
            - score: Overall score (0-100)
            - rating: "Excellent", "Good", "Poor"
            - issues: List of specific issues (e.g., "Blurry", "Low Contrast")
            - metrics: Raw metrics (blur_var, contrast, resolution)
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
            
        # Validate parameters
        self._validate_coordinates(x1, y1, x2, y2, session.width, session.height)
        
        try:
            # Crop the selected region
            cropped_image = session.original_image[y1:y2, x1:x2]
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            
            # 1. Blur Detection (Laplacian Variance)
            # Higher variance = sharper image. < 100 is usually blurry.
            blur_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 2. Contrast Detection (RMS Contrast)
            # Standard deviation of pixel intensities
            contrast = gray.std()
            
            # 3. Resolution Check
            height, width = gray.shape
            min_dim = min(height, width)
            
            # Scoring Logic
            #
            # The blur/contrast/resolution cutoffs below (50/100, 20/40,
            # 100px/200px) and their point deductions are heuristic defaults
            # commonly used for Laplacian-variance blur detection and RMS
            # contrast, not values calibrated against a labeled set of real
            # signature scans in this codebase. They produce a relative,
            # directional signal (worse image -> lower score) rather than a
            # precisely calibrated absolute quality metric. If users report
            # the health badge disagreeing with visibly obvious blur/
            # contrast/resolution problems, these are the values to
            # recalibrate first, ideally against real user-submitted scans.
            issues = []
            score = 100

            # Blur Penalty
            if blur_var < 50:
                score -= 40
                issues.append("Very Blurry")
            elif blur_var < 100:
                score -= 20
                issues.append("Slightly Blurry")
                
            # Contrast Penalty
            if contrast < 20:
                score -= 30
                issues.append("Low Contrast")
            elif contrast < 40:
                score -= 10
                issues.append("Moderate Contrast")
                
            # Resolution Penalty
            if min_dim < 100:
                score -= 30
                issues.append("Low Resolution")
            elif min_dim < 200:
                score -= 10
                issues.append("Small Size")
                
            # Clamp score
            score = max(0, min(100, score))
            
            # Determine Rating
            if score >= 80:
                rating = "Excellent"
            elif score >= 50:
                rating = "Good"
            else:
                rating = "Poor"
                
            return {
                "score": score,
                "rating": rating,
                "issues": issues,
                "metrics": {
                    "blur_var": float(blur_var),
                    "contrast": float(contrast),
                    "min_dim": int(min_dim)
                }
            }
            
        except Exception as e:
            LOG.error(f"Failed to analyze quality for session {session_id}: {e}")
            # Return a safe default on error, but include the actual reason so
            # the UI (which surfaces `issues` directly in the health badge
            # tooltip) can show the user something more actionable than an
            # unexplained "Unknown" rating.
            return {
                "score": 0,
                "rating": "Unknown",
                "issues": [f"Analysis failed: {e}"],
                "metrics": {}
            }
    
    def rotate_image(self, session_id: str, angle: float) -> str:
        """Rotate image and create new session.
        
        Args:
            session_id: Original session identifier
            angle: Rotation angle in degrees (positive = clockwise)
            
        Returns:
            New session ID for rotated image
            
        Raises:
            ValueError: If session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        try:
            # Get image dimensions
            height, width = session.original_image.shape[:2]
            center = (width // 2, height // 2)
            
            # Create rotation matrix
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Calculate new dimensions to fit rotated image
            cos_val = abs(rotation_matrix[0, 0])
            sin_val = abs(rotation_matrix[0, 1])
            new_width = int((height * sin_val) + (width * cos_val))
            new_height = int((height * cos_val) + (width * sin_val))
            
            # Adjust rotation matrix for new center
            rotation_matrix[0, 2] += (new_width / 2) - center[0]
            rotation_matrix[1, 2] += (new_height / 2) - center[1]
            
            # Apply rotation
            rotated_image = cv2.warpAffine(
                session.original_image,
                rotation_matrix,
                (new_width, new_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(255, 255, 255)  # White background
            )
            
            # Save rotated image to temporary file with secure permissions
            temp_fd, temp_path = tempfile.mkstemp(suffix='.png', prefix='rotated_')
            self._temp_files.add(temp_path)
            
            try:
                os.close(temp_fd)  # Close file descriptor, keep the file
                
                # Set secure file permissions (owner read/write only)
                os.chmod(temp_path, 0o600)
                
                cv2.imwrite(temp_path, rotated_image)
                
                # Create new session with rotated image
                new_session_id = self.create_session(temp_path)
                
                LOG.info(f"Rotated image by {angle}° for session {session_id}, new session: {new_session_id}")
                return new_session_id
                
            except Exception:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                    self._temp_files.discard(temp_path)
                except OSError:
                    pass
                raise
                
        except Exception as e:
            LOG.error(f"Failed to rotate image for session {session_id}: {e}")
            raise
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session and associated resources.
        
        Args:
            session_id: Session identifier to clean up
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            LOG.debug(f"Cleaned up session {session_id}")
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old sessions to free resources."""
        if len(self.sessions) < self.MAX_SESSIONS:
            return  # No need to cleanup yet
        
        # Sort sessions by creation time and remove oldest ones
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest sessions to get below the limit
        # Remove enough to get to 75% of max capacity
        target_count = int(self.MAX_SESSIONS * 0.75)
        sessions_to_remove = len(sorted_sessions) - target_count
        
        if sessions_to_remove > 0:
            for session_id, _ in sorted_sessions[:sessions_to_remove]:
                self.cleanup_session(session_id)
            
            LOG.info(f"Cleaned up {sessions_to_remove} old sessions")

    def _validate_coordinates(self, x1: int, y1: int, x2: int, y2: int, 
                            max_width: int, max_height: int) -> None:
        """Validate coordinate bounds and ranges.
        
        Args:
            x1, y1, x2, y2: Coordinate values to validate
            max_width, max_height: Maximum allowed coordinate values
            
        Raises:
            ValueError: If coordinates are invalid or out of bounds
        """
        # Check coordinate types and ranges
        coords = [('x1', x1), ('y1', y1), ('x2', x2), ('y2', y2)]
        for name, value in coords:
            if not isinstance(value, int):
                raise ValueError(f"{name} must be an integer, got {type(value).__name__}")
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")
        
        # Check selection area first
        if x2 <= x1:
            raise ValueError(f"x2 must be > x1, got x1={x1}, x2={x2}")
        if y2 <= y1:
            raise ValueError(f"y2 must be > y1, got y1={y1}, y2={y2}")
        
        # Check selection size (prevent extremely large selections) before bounds
        width = x2 - x1
        height = y2 - y1
        max_selection_pixels = 25_000_000  # 25 megapixels
        
        if width * height > max_selection_pixels:
            raise ValueError(
                f"Selection too large: {width}x{height} pixels "
                f"(max {max_selection_pixels:,} pixels)"
            )
        
        # Check bounds after size validation
        if x1 >= max_width or x2 > max_width:
            raise ValueError(f"X coordinates must be <= {max_width} (x1 < {max_width}), got x1={x1}, x2={x2}")
        if y1 >= max_height or y2 > max_height:
            raise ValueError(f"Y coordinates must be <= {max_height} (y1 < {max_height}), got y1={y1}, y2={y2}")

    def cleanup_all(self) -> None:
        """Clean up all sessions and temporary files securely."""
        # Clear session data from memory
        for session in self.sessions.values():
            # Overwrite image data in memory (best effort)
            if session.original_image is not None:
                session.original_image.fill(0)
            if session.processed_image is not None:
                session.processed_image.fill(0)
        
        self.sessions.clear()
        
        # Securely clean up temporary files
        for temp_file in list(self._temp_files):
            try:
                if os.path.exists(temp_file):
                    # Overwrite file content before deletion (best effort)
                    try:
                        file_size = os.path.getsize(temp_file)
                        with open(temp_file, 'r+b') as f:
                            f.write(b'\x00' * file_size)
                            f.flush()
                            os.fsync(f.fileno())
                    except (OSError, IOError):
                        pass  # Continue with normal deletion if overwrite fails
                    
                    # Delete the file
                    os.unlink(temp_file)
                    LOG.debug(f"Securely cleaned up temp file: {os.path.basename(temp_file)}")
            except OSError as e:
                LOG.warning(f"Failed to clean up temp file {os.path.basename(temp_file)}: {e}")
        
        self._temp_files.clear()
        LOG.debug("Completed secure cleanup of all sessions and temporary files")
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cleanup_all()
        except Exception:
            pass  # Ignore errors during cleanup
