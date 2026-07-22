"""Tests for the local signature processing engine (desktop_app/processing/extractor.py).

Covers session lifecycle and the forensic (K-Means) watermarking path, which
previously failed silently: a duplicate `class SignatureExtractor` definition
shadowed the live class's `__init__`, so `self.watermarker` / `self.original_path`
never existed and every forensic-mode watermark attempt raised AttributeError
(swallowed by a broad except and logged as "Watermarking failed").
"""

import io
import json
import struct

import pytest
from PIL import Image, ImageDraw

from desktop_app.processing.extractor import SignatureExtractor


def _make_signature_image(path: str, size=(200, 100)) -> None:
    """Write a simple synthetic "signature on paper" PNG to disk."""
    img = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line([(20, 80), (60, 20), (100, 80), (140, 20), (180, 80)], fill=(10, 10, 10), width=4)
    img.save(path, format="PNG")


@pytest.fixture
def sample_image_path(tmp_path):
    path = tmp_path / "sample_signature.png"
    _make_signature_image(str(path))
    return str(path)


@pytest.fixture
def extractor():
    return SignatureExtractor()


def test_create_session_tracks_file_path(extractor, sample_image_path):
    session_id = extractor.create_session(sample_image_path)
    session = extractor.get_session(session_id)
    assert session is not None
    assert session.file_path == sample_image_path
    assert session.width == 200
    assert session.height == 100


def test_process_selection_returns_valid_rgba_png(extractor, sample_image_path):
    session_id = extractor.create_session(sample_image_path)
    png_bytes = extractor.process_selection(
        session_id=session_id, x1=0, y1=0, x2=200, y2=100,
        threshold=180, color="#000000",
    )
    img = Image.open(io.BytesIO(png_bytes))
    assert img.mode == "RGBA"
    assert img.size == (200, 100)


def test_analyze_quality_returns_score_and_rating(extractor, sample_image_path):
    session_id = extractor.create_session(sample_image_path)
    quality = extractor.analyze_quality(session_id=session_id, x1=0, y1=0, x2=200, y2=100)
    assert 0 <= quality["score"] <= 100
    assert quality["rating"] in {"Excellent", "Good", "Poor"}


def test_analyze_quality_failure_reports_the_actual_reason(extractor, sample_image_path, monkeypatch):
    """The fallback on unexpected failure must surface *why* it failed, not
    just an unexplained "Unknown" rating with no actionable detail (the UI
    displays `issues` directly in the health-badge tooltip)."""
    session_id = extractor.create_session(sample_image_path)

    def boom(*args, **kwargs):
        raise RuntimeError("simulated cv2 failure")

    monkeypatch.setattr("cv2.Laplacian", boom)

    quality = extractor.analyze_quality(session_id=session_id, x1=0, y1=0, x2=200, y2=100)

    assert quality["rating"] == "Unknown"
    assert quality["score"] == 0
    assert any("simulated cv2 failure" in issue for issue in quality["issues"])


def test_kmeans_forensic_mode_embeds_watermark_without_error(extractor, sample_image_path, caplog):
    """Regression test: forensic mode must actually watermark, not silently no-op.

    Before the fix, `self.watermarker` and `self.original_path` did not exist on
    the live SignatureExtractor instance, so embed_watermark() always raised
    AttributeError, was swallowed, and every forensic export shipped unwatermarked.
    """
    session_id = extractor.create_session(sample_image_path)

    png_bytes = extractor.process_selection_kmeans(
        session_id=session_id, x1=0, y1=0, x2=200, y2=100, k=2
    )

    assert "Watermarking failed" not in caplog.text

    # Decode the LSB-embedded metadata header to confirm a real payload was written.
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    bits = []
    for y in range(height):
        for x in range(width):
            if len(bits) >= 32:
                break
            r, g, b, a = pixels[x, y]
            bits.append(b & 1)
        if len(bits) >= 32:
            break

    length_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit
        length_bytes.append(byte)
    payload_len = struct.unpack(">I", bytes(length_bytes))[0]

    assert 0 < payload_len < (width * height)


def test_kmeans_watermark_metadata_contains_source_hash(extractor, sample_image_path):
    """The embedded metadata must reference the session's source file, not a
    non-existent `self.original_path` attribute."""
    session_id = extractor.create_session(sample_image_path)
    png_bytes = extractor.process_selection_kmeans(
        session_id=session_id, x1=0, y1=0, x2=200, y2=100, k=2
    )

    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    bits = []
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            bits.append(b & 1)

    length_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit
        length_bytes.append(byte)
    payload_len = struct.unpack(">I", bytes(length_bytes))[0]

    payload_bits = bits[32:32 + payload_len * 8]
    payload_bytes = bytearray()
    for i in range(0, len(payload_bits), 8):
        byte = 0
        for bit in payload_bits[i:i + 8]:
            byte = (byte << 1) | bit
        payload_bytes.append(byte)

    meta = json.loads(bytes(payload_bytes).decode("utf-8"))
    assert meta["mode"] == "forensic"
    assert meta["source_hash"] != "unknown"
