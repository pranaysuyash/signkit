"""PDF signing utilities.

Primary implementation uses PyMuPDF when explicitly allowed for the session.
Otherwise, we use a deliberate pikepdf fallback.
"""

import io
import base64
import os
import tempfile
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, cast
from pathlib import Path

import pikepdf
from desktop_app.pdf.stack_profile import _is_fitz_allowed, record_signing_backend_telemetry
from PIL import Image as PILImage
from PIL import ImageEnhance

# Optional, preferred implementation
try:
    if _is_fitz_allowed():
        import fitz  # type: ignore  # PyMuPDF
        HAS_PYMUPDF = True
    else:
        HAS_PYMUPDF = False
        fitz = cast(Any, None)  # type: ignore
except Exception:
    HAS_PYMUPDF = False
    # Provide a dummy name to satisfy static analyzers when PyMuPDF is not installed
    fitz = cast(Any, None)  # type: ignore


_SIGNATURE_MANIFEST_KEY = "/SignKit-SignaturePlacements"
_SIGNATURE_MANIFEST_VERSION = 1
_MAX_SIGNATURE_MANIFEST_IMAGE_BYTES = 256_000


def _manifest_image_payload(sig_image_path: str) -> str:
    try:
        raw = Path(sig_image_path).read_bytes()
    except Exception:
        return ""

    if not raw:
        return ""
    if len(raw) > _MAX_SIGNATURE_MANIFEST_IMAGE_BYTES:
        return ""

    return base64.b64encode(raw).decode("ascii")


def _coerce_manifest_text(value: Any, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        text = value.strip()
        return text if text else default
    return default


def _coerce_manifest_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _coerce_manifest_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _normalize_signature_for_manifest(sig: Dict[str, Any]) -> Dict[str, Any]:
    style = _coerce_signature_style(sig)
    sig_path = _coerce_manifest_text(sig.get("sig_path"), "")
    sig_image_data = _manifest_image_payload(sig_path)

    return {
        "version": _SIGNATURE_MANIFEST_VERSION,
        "page": _coerce_manifest_int(sig.get("page"), 0),
        "x": _coerce_manifest_int(sig.get("x"), 0),
        "y": _coerce_manifest_int(sig.get("y"), 0),
        "width": max(1, _coerce_manifest_int(sig.get("width"), 1)),
        "height": max(1, _coerce_manifest_int(sig.get("height"), 1)),
        "sig_path": sig_path,
        "sig_filename": Path(sig_path).name if sig_path else "",
        "rotation_deg": style.get("rotation_deg", 0.0),
        "brightness": style.get("brightness", 1.0),
        "contrast": style.get("contrast", 1.0),
        "saturation": style.get("saturation", 1.0),
        "units": "px",
        "dpi": _coerce_manifest_float(sig.get("dpi"), 150.0),
        "scale": _coerce_manifest_float(sig.get("scale"), 1.0),
        "style": style,
    } | ({"sig_image_data": sig_image_data} if sig_image_data else {})


def _build_signature_manifest(signatures: List[Dict[str, Any]]) -> str:
    placement_list = [_normalize_signature_for_manifest(sig) for sig in signatures if isinstance(sig, dict)]
    payload = {
        "kind": "signkit.signature_manifest",
        "version": _SIGNATURE_MANIFEST_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signatures": placement_list,
    }
    return json.dumps(payload, sort_keys=True)


def _apply_signature_manifest(output_pdf_path: str, signatures: List[Dict[str, Any]]) -> None:
    manifest_payload = _build_signature_manifest(signatures)
    output_path = Path(output_pdf_path)
    temp_file = tempfile.NamedTemporaryFile(prefix=output_path.name + ".", suffix=".pdf", delete=False)
    temp_output_pdf = temp_file.name
    temp_file.close()

    try:
        with pikepdf.open(output_pdf_path) as pdf:
            pdf.docinfo[_SIGNATURE_MANIFEST_KEY] = pikepdf.String(manifest_payload)
            pdf.save(temp_output_pdf)

        os.replace(temp_output_pdf, output_pdf_path)
    finally:
        if os.path.exists(temp_output_pdf):
            os.unlink(temp_output_pdf)


def _coerce_manifest_entry_float(entry: Dict[str, Any], key: str, default: float) -> float:
    try:
        return float(entry[key])
    except (TypeError, ValueError, KeyError):
        return default


def _coerce_manifest_entry_int(entry: Dict[str, Any], key: str, default: int) -> int:
    try:
        return int(entry[key])
    except (TypeError, ValueError, KeyError):
        return default


def _coerce_manifest_signature_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    style = _coerce_signature_style(entry.get("style"))
    return {
        "page": _coerce_manifest_entry_int(entry, "page", 0),
        "x": _coerce_manifest_entry_int(entry, "x", 0),
        "y": _coerce_manifest_entry_int(entry, "y", 0),
        "width": max(1, _coerce_manifest_entry_int(entry, "width", 1)),
        "height": max(1, _coerce_manifest_entry_int(entry, "height", 1)),
        "sig_path": _coerce_manifest_text(entry.get("sig_path"), ""),
        "rotation_deg": _coerce_manifest_entry_float(entry, "rotation_deg", 0.0),
        "brightness": _coerce_manifest_entry_float(entry, "brightness", 1.0),
        "contrast": _coerce_manifest_entry_float(entry, "contrast", 1.0),
        "saturation": _coerce_manifest_entry_float(entry, "saturation", 1.0),
        "style": style,
        "units": _coerce_manifest_text(entry.get("units"), "px"),
        "dpi": _coerce_manifest_entry_float(entry, "dpi", 150.0),
        "scale": _coerce_manifest_entry_float(entry, "scale", 1.0),
        "sig_image_data": _coerce_manifest_text(entry.get("sig_image_data"), ""),
    }


def read_signature_manifest(pdf_path: str) -> List[Dict[str, Any]]:
    """Read embedded SignKit signature placement metadata from an output PDF."""
    if not Path(pdf_path).exists():
        return []

    try:
        with pikepdf.open(pdf_path) as pdf:
            raw_manifest = pdf.docinfo.get(_SIGNATURE_MANIFEST_KEY)
    except Exception:
        return []

    if not raw_manifest:
        return []

    try:
        manifest = json.loads(str(raw_manifest))
    except Exception:
        return []

    if not isinstance(manifest, dict):
        return []
    if manifest.get("kind") != "signkit.signature_manifest":
        return []

    items = manifest.get("signatures")
    if not isinstance(items, list):
        return []

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized.append(_coerce_manifest_signature_entry(item))
    return normalized


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_signature_style(sig: Dict[str, Any]) -> Dict[str, float]:
    return {
        "rotation_deg": _coerce_float(sig.get("rotation_deg", 0.0), 0.0) % 360.0,
        "brightness": _coerce_float(sig.get("brightness", 1.0), 1.0),
        "contrast": _coerce_float(sig.get("contrast", 1.0), 1.0),
        "saturation": _coerce_float(sig.get("saturation", 1.0), 1.0),
    }


def _build_signature_image(
    sig_image_path: str,
    rotation_deg: float = 0.0,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
) -> PILImage.Image:
    """Build a style-adjusted signature image for PDF embedding."""
    sig_image = cast(PILImage.Image, PILImage.open(sig_image_path)).convert("RGBA")

    rotation_deg = float(rotation_deg) % 360.0
    if rotation_deg:
        # PIL rotate is CCW-positive; mirror with clockwise-positive control UI.
        sig_image = sig_image.rotate(-rotation_deg, expand=True, fillcolor=(0, 0, 0, 0))
        sig_image = sig_image.convert("RGBA")

    brightness_value = _coerce_float(brightness, 1.0)
    if brightness_value > 0:
        sig_image = ImageEnhance.Brightness(sig_image).enhance(brightness_value)

    contrast_value = _coerce_float(contrast, 1.0)
    if contrast_value > 0:
        sig_image = ImageEnhance.Contrast(sig_image).enhance(contrast_value)

    saturation_value = _coerce_float(saturation, 1.0)
    if saturation_value > 0:
        sig_image = ImageEnhance.Color(sig_image).enhance(saturation_value)

    return sig_image.convert("RGBA")


def _build_signature_tmp_image_file(
    sig_image_path: str,
    *,
    rotation_deg: float = 0.0,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
) -> str:
    styled_image = _build_signature_image(
        sig_image_path,
        rotation_deg=rotation_deg,
        brightness=brightness,
        contrast=contrast,
        saturation=saturation,
    )
    temp_file = tempfile.NamedTemporaryFile(prefix="signkit_sig_", suffix=".png", delete=False)
    temp_path = temp_file.name
    temp_file.close()
    styled_image.save(temp_path, format="PNG")
    return temp_path


def _cleanup_signature_temp_file(path: str) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass


class PDFSigner:
    """Embed signature images into PDF documents.

    Behavior:
    - When PyMuPDF is available, it is used to insert images via Page.insert_image,
      which is reliable and supported by PDF viewers (including Acrobat).
    - If PyMuPDF is unavailable, a deliberate pikepdf fallback is used
      as a fallback.
    """

    def __init__(self, input_pdf_path: str):
        """
        Initialize signer with input PDF.

        Args:
            input_pdf_path: Path to original PDF file

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF cannot be opened
        """
        if not Path(input_pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {input_pdf_path}")

        self.input_path = input_pdf_path
        self._using_fitz = False
        self._doc = None
        self._pdf = None

        # Prefer PyMuPDF document handle if enabled and available
        if HAS_PYMUPDF:
            try:
                self._doc = fitz.open(input_pdf_path)
                self._using_fitz = True
                record_signing_backend_telemetry(
                    backend="fitz",
                    source="PDFSigner.__init__",
                    reason="preferred_backend",
                )
            except Exception as e:
                record_signing_backend_telemetry(
                    backend="fitz",
                    source="PDFSigner.__init__",
                    reason=f"open_failed:{e}",
                )

        if not self._using_fitz:
            try:
                self._pdf = pikepdf.open(input_pdf_path)
                record_signing_backend_telemetry(
                    backend="pikepdf",
                    source="PDFSigner.__init__",
                    reason="fallback_or_configured",
                )
            except Exception as e:
                raise ValueError(f"Failed to open PDF (pikepdf): {e}")

    def add_signature(
        self,
        page_num: int,
        sig_image_path: str,
        x: float,
        y: float,
        width: float,
        height: float,
        rotation_deg: float = 0.0,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
    ) -> None:
        """
        Add a signature image to a specific page.

        Args:
            page_num: Page number (0-indexed)
            sig_image_path: Path to signature image file
            x, y: Position on page.
            width, height: Signature dimensions.
            rotation_deg: Signature image rotation in degrees.
            brightness: Brightness multiplier (1.0 means unchanged).
            contrast: Contrast multiplier (1.0 means unchanged).
            saturation: Saturation multiplier (1.0 means unchanged).

        Coordinates origin and units:
        - PyMuPDF path (preferred): expects top-left origin in PDF page space
          as used by PyMuPDF's Page.insert_image(). Units are PDF points.
        - Legacy pikepdf path: expects top-left origin as provided by the UI;
          the implementation converts to bottom-left internally. Units are PDF
          points.
        """
        # Preferred implementation: PyMuPDF
        if self._using_fitz and self._doc is not None:
            if page_num < 0 or page_num >= self._doc.page_count:
                raise ValueError(f"Invalid page number: {page_num}")

            page = self._doc[page_num]

            # PyMuPDF expects top-left origin in page space; units are points
            rect = fitz.Rect(float(x), float(y), float(x + width), float(y + height))

            # Insert image; preserve aspect ratio similar to viewer overlay
            # (image is scaled to fit into rect while maintaining aspect)
            try:
                image_file = _build_signature_tmp_image_file(
                    sig_image_path,
                    rotation_deg=rotation_deg,
                    brightness=brightness,
                    contrast=contrast,
                    saturation=saturation,
                )
                try:
                    page.insert_image(
                        rect,
                        filename=image_file,
                        keep_proportion=True,
                        overlay=True,
                    )
                finally:
                    _cleanup_signature_temp_file(image_file)
            except Exception as e:
                raise ValueError(f"Failed to insert image: {e}")
            return

        # Fallback: legacy pikepdf stream editing
        if self._pdf is None:
            raise RuntimeError("No PDF backend available for signing")

        if page_num < 0 or page_num >= len(self._pdf.pages):
            raise ValueError(f"Invalid page number: {page_num}")

        page = self._pdf.pages[page_num]

        # Load signature image; cast to concrete Image type for type checkers
        sig_image = _build_signature_image(
            sig_image_path,
            rotation_deg=rotation_deg,
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
        )

        # Preserve RGBA for transparency, convert others to RGB
        if sig_image.mode not in ("RGBA", "RGB", "L"):
            sig_image = sig_image.convert("RGBA")

        image_bytes = io.BytesIO()
        sig_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        raw_image = pikepdf.Stream(self._pdf, image_bytes.read())

        if sig_image.mode == "RGBA":
            color_space = pikepdf.Name("/DeviceRGB")
            alpha = sig_image.split()[3]
            alpha_bytes = io.BytesIO()
            alpha.save(alpha_bytes, format="PNG")
            alpha_bytes.seek(0)

            smask = pikepdf.Stream(self._pdf, alpha_bytes.read())
            smask.stream_dict = pikepdf.Dictionary(
                Type=pikepdf.Name("/XObject"),
                Subtype=pikepdf.Name("/Image"),
                Width=alpha.width,
                Height=alpha.height,
                ColorSpace=pikepdf.Name("/DeviceGray"),
                BitsPerComponent=8,
                Filter=pikepdf.Name("/FlateDecode"),
            )

            raw_image.stream_dict = pikepdf.Dictionary(
                Type=pikepdf.Name("/XObject"),
                Subtype=pikepdf.Name("/Image"),
                Width=sig_image.width,
                Height=sig_image.height,
                ColorSpace=color_space,
                BitsPerComponent=8,
                Filter=pikepdf.Name("/FlateDecode"),
                SMask=smask,
            )
        else:
            raw_image.stream_dict = pikepdf.Dictionary(
                Type=pikepdf.Name("/XObject"),
                Subtype=pikepdf.Name("/Image"),
                Width=sig_image.width,
                Height=sig_image.height,
                ColorSpace=pikepdf.Name("/DeviceRGB") if sig_image.mode == "RGB" else pikepdf.Name("/DeviceGray"),
                BitsPerComponent=8,
                Filter=pikepdf.Name("/FlateDecode"),
            )

        pdf_image = raw_image

        mediabox = page.MediaBox
        page_height = float(mediabox[3]) - float(mediabox[1])
        # Convert from top-left origin to bottom-left for PDF content stream
        y_pdf = page_height - y - height

        if "/Resources" not in page:
            page.Resources = pikepdf.Dictionary()
        if "/XObject" not in page.Resources:
            page.Resources.XObject = pikepdf.Dictionary()

        sig_name = f"/Sig{len(page.Resources.XObject)}"
        page.Resources.XObject[sig_name] = pdf_image

        drawing_commands = f"""
q
{width} 0 0 {height} {x} {y_pdf} cm
{sig_name} Do
Q
"""

        if "/Contents" in page:
            if isinstance(page.Contents, pikepdf.Array):
                existing_content = b""
                contents_array_any = cast(Any, page.Contents)
                for stream in contents_array_any:
                    existing_content += pikepdf.Stream(stream).read_bytes()
                new_content = existing_content + drawing_commands.encode("latin-1")
                page.Contents = pikepdf.Stream(self._pdf, new_content)
            else:
                existing_content = page.Contents.read_bytes()
                new_content = existing_content + drawing_commands.encode("latin-1")
                page.Contents = pikepdf.Stream(self._pdf, new_content)
        else:
            page.Contents = pikepdf.Stream(self._pdf, drawing_commands.encode("latin-1"))

    def save(self, output_path: str) -> None:
        """
        Save the signed PDF to a new file.

        Args:
            output_path: Path to save signed PDF
        """
        if HAS_PYMUPDF and self._doc is not None:
            # Use deflate to keep sizes reasonable if images are uncompressed
            self._doc.save(output_path, deflate=True)
        elif self._pdf is not None:
            self._pdf.save(output_path)
        else:
            raise RuntimeError("No PDF backend available for saving")

    def save_to_bytes(self) -> bytes:
        """
        Save the signed PDF to bytes.

        Returns:
            PDF file bytes
        """
        buffer = io.BytesIO()
        if HAS_PYMUPDF and self._doc is not None:
            self._doc.save(buffer, deflate=True)
            return buffer.getvalue()
        elif self._pdf is not None:
            self._pdf.save(buffer)
            return buffer.getvalue()
        else:
            raise RuntimeError("No PDF backend available for saving")

    def close(self) -> None:
        """Close the PDF."""
        try:
            if HAS_PYMUPDF and getattr(self, "_doc", None) is not None:
                self._doc.close()  # type: ignore[union-attr]
        except Exception:
            pass
        try:
            if getattr(self, "_pdf", None) is not None:
                self._pdf.close()  # type: ignore[union-attr]
        except Exception:
            pass

    def __del__(self):
        self.close()


def sign_pdf(input_pdf_path: str, output_pdf_path: str, 
             signatures: List[Dict[str, Any]]) -> bool:
    """
    Convenience function to sign a PDF in one call.
    
    Args:
        input_pdf_path: Path to original PDF
        output_pdf_path: Path to save signed PDF
        signatures: List of signature dicts with keys:
                   - page: int (page number, 0-indexed)
                   - sig_path: str (path to signature image)
                   - x, y: float (position in PDF coordinates)
                   - width, height: float (dimensions in PDF points)
                   - rotation_deg (optional): signature rotation in degrees
                   - brightness (optional): brightness multiplier
                   - contrast (optional): contrast multiplier
                   - saturation (optional): saturation multiplier
    
    Returns:
        True if successful, False otherwise
    """
    signer: PDFSigner | None = None
    try:
        signer = PDFSigner(input_pdf_path)
        
        for sig in signatures:
            # Support both point-based coordinates (legacy) and pixel-based
            # viewer coordinates (with dpi / scale metadata). If 'dpi' or
            # 'units' == 'px' is present, convert from pixels to PDF points.
            x = float(sig["x"])
            y = float(sig["y"])
            width = float(sig["width"])
            height = float(sig["height"])

            if sig.get("units") == "px" or ("dpi" in sig or "scale" in sig):
                dpi = float(sig.get("dpi", 150))
                scale = float(sig.get("scale", 1.0))
                if dpi <= 0:
                    dpi = 150.0
                if scale <= 0:
                    scale = 1.0
                px_to_pt = 72.0 / (dpi * scale)
                x *= px_to_pt
                y *= px_to_pt
                width *= px_to_pt
                height *= px_to_pt

            style = _coerce_signature_style(sig)
            signer.add_signature(
                page_num=int(sig["page"]),
                sig_image_path=str(sig["sig_path"]),
                x=x,
                y=y,
                width=width,
                height=height,
                rotation_deg=style["rotation_deg"],
                brightness=style["brightness"],
                contrast=style["contrast"],
                saturation=style["saturation"],
            )

        signer.save(output_pdf_path)
        try:
            _apply_signature_manifest(output_pdf_path, signatures)
        except Exception as exc:
            print(f"Warning: could not embed signature manifest metadata into output PDF. {exc}")
        return True
    except Exception as e:
        print(f"Error signing PDF: {e}")
        return False
    finally:
        if signer is not None:
            signer.close()


def sign_pdf_with_certificate(*args, **kwargs):
    """Proxy to the explicit certificate-backed PAdES signer.

    Kept beside the visual `sign_pdf` entry point so callers can choose the
    signing semantics deliberately without creating a second PDF pipeline.
    """

    from desktop_app.pdf.digital_signer import sign_pdf_with_certificate as _sign

    return _sign(*args, **kwargs)
