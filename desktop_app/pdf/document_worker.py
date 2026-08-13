"""One-shot child process for isolated PDFium operations."""

from __future__ import annotations

import base64
from io import BytesIO
import json
import sys
from typing import Any


def _render_page(pdf_path: str, page_index: int, scale: float) -> str:
    import pypdfium2 as pdfium

    from desktop_app.pdf.pdfium_runtime import pdfium_operation

    with pdfium_operation():
        pdf = pdfium.PdfDocument(pdf_path)
        try:
            page = pdf[page_index]
            bitmap = page.render(scale=scale, rotation=0)
            image = bitmap.to_pil()
            output = BytesIO()
            image.save(output, format="PNG")
            return base64.b64encode(output.getvalue()).decode("ascii")
        finally:
            pdf.close()


def _handle(request: dict[str, Any]) -> dict[str, Any]:
    operation = request.get("operation")
    pdf_path = request.get("pdf_path")
    page_index = request.get("page_index")
    if not isinstance(operation, str) or not isinstance(pdf_path, str) or not isinstance(page_index, int):
        return {"ok": False, "error": "invalid_request"}

    if operation == "detect_page":
        from desktop_app.pdf.field_detection import SignatureFieldDetector

        candidates = SignatureFieldDetector().detect_page(pdf_path, page_index)
        return {"ok": True, "candidates": [candidate.as_dict() for candidate in candidates]}

    if operation == "render_page":
        scale = request.get("scale", 1.0)
        if not isinstance(scale, (int, float)) or scale <= 0:
            return {"ok": False, "error": "invalid_scale"}
        return {"ok": True, "png_base64": _render_page(pdf_path, page_index, float(scale))}

    return {"ok": False, "error": "unsupported_operation"}


def main() -> int:
    try:
        request = json.load(sys.stdin)
        response = _handle(request)
    except Exception as exc:
        response = {"ok": False, "error": type(exc).__name__}
    sys.stdout.write(json.dumps(response, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
