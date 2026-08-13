import os
import json
import hashlib
import tempfile
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from uuid import uuid4


APP_DIR = os.path.join(os.path.expanduser("~"), ".signature_extractor")
LIB_DIR = os.path.join(APP_DIR, "signatures")
DELETION_RECEIPT_DIRNAME = ".deletion_receipts"


def ensure_library_dir() -> str:
    os.makedirs(LIB_DIR, exist_ok=True)
    return LIB_DIR


def library_dir() -> str:
    return ensure_library_dir()


def auto_filename(prefix: str = "signature", ext: str = ".png") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}{ext}"


def save_png_to_library(png_bytes: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Save PNG to library with optional metadata sidecar file.
    
    Args:
        png_bytes: PNG image data
        metadata: Optional dict with extraction metadata (selection coords, color, threshold)
    
    Returns:
        Path to saved PNG file
    """
    ensure_library_dir()
    fname = auto_filename()
    path = os.path.join(LIB_DIR, fname)
    with open(path, "wb") as f:
        f.write(png_bytes)
    
    # Save metadata as JSON sidecar if provided
    if metadata:
        json_path = path.rsplit(".", 1)[0] + ".json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass  # Non-critical, continue even if metadata save fails
    
    return path


def save_image_to_library(
    image_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    custom_filename: Optional[str] = None
) -> str:
    """Copy an image file to the library with optional metadata.
    
    Args:
        image_path: Path to source image file
        metadata: Optional metadata dict (will be augmented with file info)
        custom_filename: Optional custom filename (otherwise auto-generated)
    
    Returns:
        Path to saved file in library
    
    Raises:
        ValueError: If image file is invalid or cannot be read
        IOError: If file operations fail
    """
    import shutil
    from PIL import Image
    
    # Validate that file exists
    if not os.path.exists(image_path):
        raise ValueError(f"Image file not found: {image_path}")
    
    # Validate that it's a readable image
    try:
        with Image.open(image_path) as img:
            img.verify()  # Verify it's a valid image
        
        # Re-open to get metadata (verify() closes the file)
        with Image.open(image_path) as img:
            width, height = img.size
            image_format = img.format
            image_mode = img.mode
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image file: {e}")
    
    # Ensure library directory exists
    ensure_library_dir()
    
    # Generate filename
    if custom_filename:
        fname = custom_filename
    else:
        # Use original extension
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            ext = '.png'  # Default to PNG
        fname = auto_filename(ext=ext)
    
    # Destination path
    dest_path = os.path.join(LIB_DIR, fname)
    
    # Copy file to library
    try:
        shutil.copy2(image_path, dest_path)
    except Exception as e:
        raise IOError(f"Failed to copy image to library: {e}")
    
    # Build metadata
    file_metadata = {
        "source": "loaded_file",
        "original_filename": os.path.basename(image_path),
        "original_path": os.path.abspath(image_path),
        "loaded_at": datetime.now().isoformat(),
        "image_size": {
            "width": width,
            "height": height
        },
        "image_format": image_format,
        "image_mode": image_mode,
        "file_size_bytes": os.path.getsize(image_path)
    }
    
    # Merge with provided metadata
    if metadata:
        file_metadata.update(metadata)
    
    # Save metadata as JSON sidecar
    json_path = dest_path.rsplit(".", 1)[0] + ".json"
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(file_metadata, f, indent=2)
    except Exception:
        pass  # Non-critical, continue even if metadata save fails
    
    return dest_path


@dataclass
class LibraryItem:
    path: str
    modified: float  # epoch seconds
    metadata: Optional[Dict[str, Any]] = None

    @property
    def display_name(self) -> str:
        return os.path.basename(self.path)

    @property
    def pretty_time(self) -> str:
        try:
            return datetime.fromtimestamp(self.modified).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return ""
    
    @property
    def tooltip_text(self) -> str:
        """Generate tooltip text with coordinate info and image dimensions.

        Dimensions are read from the metadata sidecar when available (written
        at save time by save_png_to_library/save_image_to_library) to avoid
        opening the image file with PIL for every item on every list refresh.
        Falls back to opening the file only for legacy items saved without
        an "image_size" sidecar field.
        """
        lines = [
            f"File: {self.display_name}",
            f"Modified: {self.pretty_time}"
        ]

        dims = (self.metadata or {}).get("image_size") or {}
        width, height = dims.get("width"), dims.get("height")
        mode = (self.metadata or {}).get("image_mode")
        if width and height:
            lines.append(f"Image Size: {width} × {height} px")
            if mode:
                lines.append(f"Mode: {mode}")
        else:
            # Legacy fallback: no cached dimensions in metadata, read from disk.
            try:
                from PIL import Image
                with Image.open(self.path) as img:
                    lines.append(f"Image Size: {img.width} × {img.height} px")
                    lines.append(f"Mode: {img.mode}")
            except Exception:
                pass
        
        # Add file size
        try:
            file_size = os.path.getsize(self.path)
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            lines.append(f"File Size: {size_str}")
        except Exception:
            pass
        
        # Add extraction metadata if available
        if self.metadata:
            lines.append("")  # Blank line separator
            lines.append("Extraction Info:")
            
            # Add selection coordinates if available
            if "selection" in self.metadata:
                sel = self.metadata["selection"]
                x1, y1 = sel.get("x1", 0), sel.get("y1", 0)
                x2, y2 = sel.get("x2", 0), sel.get("y2", 0)
                width, height = x2 - x1, y2 - y1
                lines.append(f"  Selection: ({x1}, {y1}) → ({x2}, {y2})")
                lines.append(f"  Selection Size: {width} × {height} px")
            
            # Add source image size if available
            if "image_size" in self.metadata:
                img_size = self.metadata["image_size"]
                w, h = img_size.get("width", 0), img_size.get("height", 0)
                if w and h:
                    lines.append(f"  Source Image: {w} × {h} px")
            
            # Add color info if available
            if "color" in self.metadata:
                lines.append(f"  Color: {self.metadata['color']}")
            
            # Add threshold if available
            if "threshold" in self.metadata:
                lines.append(f"  Threshold: {self.metadata['threshold']}")
            
            # Add session ID if available
            if "session_id" in self.metadata and self.metadata["session_id"]:
                session_id = self.metadata["session_id"]
                # Truncate long session IDs
                if len(session_id) > 20:
                    session_id = session_id[:17] + "..."
                lines.append(f"  Session: {session_id}")
        
        return "\n".join(lines)


@dataclass(frozen=True)
class DeletionResult:
    """Durable outcome for removing a library item and its sidecar."""

    status: str
    primary_deleted: bool
    cleanup_complete: bool
    reason: Optional[str] = None


def _library_path(path: str) -> Optional[str]:
    """Return a safe library path, rejecting traversal and symlink escapes."""

    try:
        root = os.path.realpath(LIB_DIR)
        candidate = os.path.realpath(os.path.abspath(os.path.expanduser(path)))
        if os.path.commonpath([candidate, root]) != root or candidate == root:
            return None
        return candidate
    except (OSError, TypeError, ValueError):
        return None


def _sha256_file(path: str) -> Optional[str]:
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _write_deletion_receipt(*, item_name: str, item_sha256: Optional[str], cleanup_status: str) -> None:
    receipt_dir = os.path.join(LIB_DIR, DELETION_RECEIPT_DIRNAME)
    os.makedirs(receipt_dir, exist_ok=True)
    destination = os.path.join(receipt_dir, f"{uuid4().hex}.json")
    payload = {
        "schema": "signkit.library_deletion_receipt.v1",
        "item_name": item_name,
        "sidecar_name": f"{os.path.splitext(item_name)[0]}.json",
        "item_sha256": item_sha256,
        "cleanup_status": cleanup_status,
        "recorded_at": datetime.now().astimezone().isoformat(),
    }
    _write_deletion_receipt_payload(destination, payload, receipt_dir=receipt_dir)


def _write_deletion_receipt_payload(destination: str, payload: Dict[str, Any], *, receipt_dir: str) -> None:
    """Atomically write a deletion receipt inside the local receipt directory."""

    descriptor, temporary_name = tempfile.mkstemp(prefix=".deletion-", suffix=".tmp", dir=receipt_dir)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _incomplete_deletion_receipt_paths() -> List[str]:
    receipt_dir = os.path.join(LIB_DIR, DELETION_RECEIPT_DIRNAME)
    if not os.path.isdir(receipt_dir):
        return []
    paths: List[str] = []
    for name in os.listdir(receipt_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(receipt_dir, name)
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError, TypeError):
            continue
        if isinstance(payload, dict) and payload.get("cleanup_status") == "incomplete":
            paths.append(path)
    return sorted(paths)


def incomplete_deletion_count() -> int:
    """Return the number of local cleanup receipts awaiting explicit repair."""

    return len(_incomplete_deletion_receipt_paths())


def recover_incomplete_deletions() -> Dict[str, int]:
    """Explicitly retry sidecar cleanup recorded as incomplete.

    Only sidecars derived from a receipt's basename are considered, and the
    resolved path must remain inside ``LIB_DIR``. Ambiguous, missing, directory,
    permission-denied, and receipt-write failures remain incomplete for a later
    explicit attempt.
    """

    receipt_paths = _incomplete_deletion_receipt_paths()
    recovered = 0
    for receipt_path in receipt_paths:
        receipt_dir = os.path.dirname(receipt_path)
        try:
            with open(receipt_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue

        item_name = payload.get("item_name")
        if not isinstance(item_name, str) or os.path.basename(item_name) != item_name or not item_name:
            continue
        sidecar_name = payload.get("sidecar_name") or f"{os.path.splitext(item_name)[0]}.json"
        if not isinstance(sidecar_name, str) or os.path.basename(sidecar_name) != sidecar_name:
            continue
        sidecar_path = _library_path(os.path.join(LIB_DIR, sidecar_name))
        if sidecar_path is None:
            continue

        try:
            if os.path.exists(sidecar_path):
                if os.path.isdir(sidecar_path):
                    continue
                os.remove(sidecar_path)
            payload["cleanup_status"] = "complete"
            payload["recovered_at"] = datetime.now().astimezone().isoformat()
            _write_deletion_receipt_payload(receipt_path, payload, receipt_dir=receipt_dir)
        except OSError:
            continue
        recovered += 1

    return {
        "scanned": len(receipt_paths),
        "recovered": recovered,
        "remaining": len(receipt_paths) - recovered,
    }


def list_items(limit: int = 50) -> List[LibraryItem]:
    """List the `limit` most recently modified library items.

    Two passes, deliberately: the first only stats each file (cheap,
    filesystem-metadata-only) to determine recency; the second opens and
    JSON-parses a sidecar only for the items that will actually be
    returned. The previous implementation parsed every sidecar for every
    file in the directory before sorting and truncating to `limit` — O(n)
    JSON-parse work to return O(limit) results, regardless of how large the
    library grows. This keeps the cost bounded by `limit` instead of by
    total library size, without introducing a separate manifest/index file
    (which would be a second, driftable source of truth for data the
    filesystem already owns correctly).
    """
    ensure_library_dir()
    stamped: List[Tuple[str, float]] = []
    for name in os.listdir(LIB_DIR):
        if not name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        p = os.path.join(LIB_DIR, name)
        try:
            stamped.append((p, os.path.getmtime(p)))
        except OSError:
            continue

    stamped.sort(key=lambda entry: entry[1], reverse=True)

    items: List[LibraryItem] = []
    for p, mtime in stamped[:limit]:
        metadata = None
        json_path = p.rsplit(".", 1)[0] + ".json"
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass  # Ignore metadata read errors
        items.append(LibraryItem(path=p, modified=mtime, metadata=metadata))

    return items


def delete_item_with_result(path: str) -> DeletionResult:
    """Remove a library image, sidecar, and metadata-only deletion receipt."""

    safe_path = _library_path(path)
    if safe_path is None or not os.path.isfile(safe_path):
        return DeletionResult("not_deleted", False, True, "path_not_in_library")

    item_name = os.path.basename(safe_path)
    item_sha256 = _sha256_file(safe_path)
    try:
        os.remove(safe_path)
    except OSError:
        return DeletionResult("not_deleted", False, True, "primary_delete_failed")

    cleanup_complete = True
    sidecar_path = os.path.splitext(safe_path)[0] + ".json"
    if os.path.exists(sidecar_path):
        try:
            os.remove(sidecar_path)
        except OSError:
            cleanup_complete = False

    status = "complete" if cleanup_complete else "incomplete"
    try:
        _write_deletion_receipt(item_name=item_name, item_sha256=item_sha256, cleanup_status=status)
    except OSError:
        cleanup_complete = False
        status = "incomplete"

    return DeletionResult(
        "deleted" if cleanup_complete else "cleanup_incomplete",
        True,
        cleanup_complete,
        None if cleanup_complete else "cleanup_incomplete",
    )


def delete_item(path: str) -> bool:
    """Backward-compatible boolean deletion API."""

    return delete_item_with_result(path).primary_deleted
