from __future__ import annotations

import os
import threading
from collections import OrderedDict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Tuple

import cv2
import json
import numpy as np
from PIL import Image

from backend.app.security import UploadSecurity

# Bounded, mtime-keyed cache of decoded source images. Interactive threshold
# tuning re-invokes render_signature_png repeatedly for the same uploaded
# file; without this, every request re-reads and re-decodes the image from
# disk. Keying on (path, mtime) means a re-upload that reuses the same path
# (e.g. a session id) naturally invalidates the stale entry instead of
# silently serving old image data.
_IMAGE_CACHE_LOCK = threading.Lock()
_IMAGE_CACHE: "OrderedDict[Tuple[str, float], np.ndarray]" = OrderedDict()
_IMAGE_CACHE_MAX = 32


def _read_image_cached(file_path: Path) -> np.ndarray:
    """Read an image via cv2.imread, cached by (resolved path, mtime).

    The returned array must be treated as read-only by callers: it may be
    shared across concurrent requests for the same file.
    """
    resolved = str(file_path.resolve())
    mtime = file_path.stat().st_mtime
    key = (resolved, mtime)

    with _IMAGE_CACHE_LOCK:
        cached = _IMAGE_CACHE.get(key)
        if cached is not None:
            _IMAGE_CACHE.move_to_end(key)
            return cached

    image = cv2.imread(resolved)
    if image is None:
        raise ValueError("Failed to read image file")
    image.setflags(write=False)  # Enforce the read-only sharing contract.

    with _IMAGE_CACHE_LOCK:
        _IMAGE_CACHE[key] = image
        if len(_IMAGE_CACHE) > _IMAGE_CACHE_MAX:
            _IMAGE_CACHE.popitem(last=False)

    return image


def resolve_upload_path(session_id: str, uploads_dir: Path) -> Path:
    """Resolve an uploaded image path from a validated session id."""
    canonical_session_id = UploadSecurity.validate_session_id(session_id)

    direct_png = uploads_dir / f"{canonical_session_id}.png"
    if direct_png.exists():
        return direct_png

    for extension in sorted(UploadSecurity.ALLOWED_EXTENSIONS):
        candidate = uploads_dir / f"{canonical_session_id}{extension}"
        if candidate.exists():
            return candidate

    raise FileNotFoundError("Image file not found.")


def normalize_crop_bounds(
    width: int,
    height: int,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> Tuple[int, int, int, int]:
    """Clamp crop coordinates to image bounds and ensure a non-empty area."""
    start_x, end_x = sorted((x1, x2))
    start_y, end_y = sorted((y1, y2))
    start_x = max(0, min(start_x, width))
    end_x = max(0, min(end_x, width))
    start_y = max(0, min(start_y, height))
    end_y = max(0, min(end_y, height))

    if start_x == end_x or start_y == end_y:
        raise ValueError("Invalid crop dimensions: area is zero")

    return start_x, start_y, end_x, end_y


def build_selection_metadata(
    session_id: str,
    *,
    width: int,
    height: int,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    threshold: int,
    color: str,
) -> dict:
    """Build a durable record of a region selection."""
    threshold = UploadSecurity.validate_threshold(threshold)
    color = UploadSecurity.validate_hex_color(color)
    normalized_x1, normalized_y1, normalized_x2, normalized_y2 = normalize_crop_bounds(
        width=width,
        height=height,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )

    return {
        "session_id": session_id,
        "selected_at": datetime.now(timezone.utc).isoformat(),
        "selection": {
            "x1": normalized_x1,
            "y1": normalized_y1,
            "x2": normalized_x2,
            "y2": normalized_y2,
            "threshold": threshold,
            "color": color,
        },
        "image_bounds": {"width": width, "height": height},
    }


def persist_selection_metadata(metadata_dir: Path, session_id: str, payload: dict) -> Path:
    """Persist region selection metadata to a JSON sidecar."""
    metadata_dir.mkdir(parents=True, exist_ok=True)
    # Restrict the metadata directory (holds selection sidecars, local PII).
    if os.name == "posix":
        try:
            os.chmod(metadata_dir, 0o700)
        except OSError:
            pass
    metadata_path = metadata_dir / f"{session_id}.json"
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # Selection metadata is bound to the owner's document; restrict the sidecar
    # to the owner only.
    if os.name == "posix":
        try:
            os.chmod(metadata_path, 0o600)
        except OSError:
            pass
    return metadata_path


def render_signature_png(
    file_path: Path,
    *,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str,
    threshold: int,
) -> BytesIO:
    """Render a cropped, colorized signature region as PNG bytes."""
    threshold = UploadSecurity.validate_threshold(threshold)
    color = UploadSecurity.validate_hex_color(color)
    image = _read_image_cached(file_path)

    height, width = image.shape[:2]
    start_x, start_y, end_x, end_y = normalize_crop_bounds(
        width=width,
        height=height,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )

    cropped_image = image[start_y:end_y, start_x:end_x]
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    hex_color = color.lstrip("#")
    r_val = int(hex_color[0:2], 16)
    g_val = int(hex_color[2:4], 16)
    b_val = int(hex_color[4:6], 16)
    color_bgr = (b_val, g_val, r_val)

    color_image = np.zeros_like(cropped_image, dtype=np.uint8)
    color_image[:, :] = color_bgr
    result_image = cv2.bitwise_and(color_image, color_image, mask=mask)

    b_channel, g_channel, r_channel = cv2.split(result_image)
    final_image = cv2.merge([b_channel, g_channel, r_channel, mask])

    final_image_pil = Image.fromarray(final_image)
    final_image_io = BytesIO()
    final_image_pil.save(final_image_io, format="PNG")
    final_image_io.seek(0)
    return final_image_io
