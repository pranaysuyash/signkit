from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from backend.app.services import extraction as extraction_service
from backend.app.services.extraction import (
    _read_image_cached,
    build_selection_metadata,
    normalize_crop_bounds,
    persist_selection_metadata,
    render_signature_png,
    resolve_upload_path,
)


@pytest.fixture(autouse=True)
def _clear_image_cache():
    """Each test starts with an empty module-level image cache."""
    extraction_service._IMAGE_CACHE.clear()
    yield
    extraction_service._IMAGE_CACHE.clear()


def _write_test_image(path: Path, *, width: int = 24, height: int = 18) -> None:
    image = np.full((height, width, 3), 80, dtype=np.uint8)
    image[4:12, 5:15] = 255
    cv2.imwrite(str(path), image)


def test_normalize_crop_bounds_clamps_and_rejects_zero_area():
    assert normalize_crop_bounds(100, 80, -5, 10, 20, 90) == (0, 10, 20, 80)

    with pytest.raises(ValueError, match="area is zero"):
        normalize_crop_bounds(10, 10, 4, 4, 4, 8)


def test_resolve_upload_path_prefers_direct_png(tmp_path):
    session_id = "12345678-1234-5678-1234-567812345678"
    image_path = tmp_path / f"{session_id}.png"
    _write_test_image(image_path)

    assert resolve_upload_path(session_id, tmp_path) == image_path


def test_resolve_upload_path_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_upload_path("12345678-1234-5678-1234-567812345678", tmp_path)


def test_persist_selection_metadata_round_trips(tmp_path):
    payload = build_selection_metadata(
        "12345678-1234-5678-1234-567812345678",
        width=20,
        height=10,
        x1=1,
        y1=2,
        x2=8,
        y2=9,
        threshold=128,
        color="#000000",
    )

    metadata_path = persist_selection_metadata(tmp_path, "session-abc", payload)
    assert metadata_path.exists()
    assert json.loads(metadata_path.read_text(encoding="utf-8")) == payload


def test_render_signature_png_produces_png_bytes(tmp_path):
    image_path = tmp_path / "source.png"
    _write_test_image(image_path)

    output = render_signature_png(
        image_path,
        x1=4,
        y1=3,
        x2=16,
        y2=13,
        color="#112233",
        threshold=100,
    )

    assert isinstance(output, BytesIO)
    assert output.getvalue().startswith(b"\x89PNG\r\n\x1a\n")

    output.seek(0)
    rendered = Image.open(output)
    assert rendered.size == (12, 10)
    assert rendered.mode == "RGBA"


def test_read_image_cached_avoids_second_disk_read(tmp_path, monkeypatch):
    """Interactive threshold tuning re-invokes render_signature_png for the
    same uploaded file repeatedly; the second+ read must hit the cache."""
    image_path = tmp_path / "source.png"
    _write_test_image(image_path)

    calls = []
    real_imread = extraction_service.cv2.imread
    monkeypatch.setattr(
        extraction_service.cv2, "imread",
        lambda *a, **k: (calls.append(1) or real_imread(*a, **k)),
    )

    first = _read_image_cached(image_path)
    second = _read_image_cached(image_path)

    assert len(calls) == 1
    assert first is second


def test_read_image_cached_invalidates_on_mtime_change(tmp_path, monkeypatch):
    """A re-uploaded file at the same path (new mtime) must not silently
    serve stale cached image data — that would be a correctness bug, not
    just a missed optimization."""
    image_path = tmp_path / "source.png"
    _write_test_image(image_path, width=24, height=18)

    calls = []
    real_imread = extraction_service.cv2.imread
    monkeypatch.setattr(
        extraction_service.cv2, "imread",
        lambda *a, **k: (calls.append(1) or real_imread(*a, **k)),
    )

    first = _read_image_cached(image_path)

    # Overwrite with visibly different content (not just a re-save of the
    # same pixels) so a stale cache hit is distinguishable from a fresh read.
    different_image = np.full((18, 24, 3), 200, dtype=np.uint8)
    cv2.imwrite(str(image_path), different_image)
    # Some filesystems have coarse mtime resolution; force a distinct mtime
    # so this test is deterministic rather than occasionally flaky.
    bumped = image_path.stat().st_mtime + 1.0
    os.utime(image_path, (bumped, bumped))

    second = _read_image_cached(image_path)

    assert len(calls) == 2
    assert not np.array_equal(first, second)


def test_read_image_cached_array_is_read_only(tmp_path):
    image_path = tmp_path / "source.png"
    _write_test_image(image_path)
    image = _read_image_cached(image_path)
    assert image.flags.writeable is False


def test_render_signature_png_reuses_cache_across_threshold_tweaks(tmp_path, monkeypatch):
    image_path = tmp_path / "source.png"
    _write_test_image(image_path)

    calls = []
    real_imread = extraction_service.cv2.imread
    monkeypatch.setattr(
        extraction_service.cv2, "imread",
        lambda *a, **k: (calls.append(1) or real_imread(*a, **k)),
    )

    for threshold in (80, 120, 160, 200):
        render_signature_png(
            image_path, x1=4, y1=3, x2=16, y2=13, color="#112233", threshold=threshold
        )

    assert len(calls) == 1, "four threshold tweaks on the same file must only read from disk once"
