"""Signature field detection helpers for PDF pages.

This module combines two practical signal sources:

1. AcroForm/widget inspection for real PDF form fields.
2. OpenCV layout heuristics for scanned or flattened documents.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import logging
import re
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence

import pikepdf
import pypdfium2 as pdfium
import numpy as np
from desktop_app.pdf.stack_profile import is_scan_preprocess_enabled
from desktop_app.pdf.pdfium_runtime import pdfium_operation

LOG = logging.getLogger(__name__)
MAX_HEURISTIC_CANDIDATES_PER_PAGE = 3
MAX_TOTAL_CANDIDATES_PER_PAGE = 12


@dataclass(frozen=True)
class SignatureFieldCandidate:
    """A likely signature-related field or placement area."""

    page_index: int
    field_type: str
    x: float
    y: float
    width: float
    height: float
    confidence: float
    source: str
    reason: str
    label: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "page_index": self.page_index,
            "field_type": self.field_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "source": self.source,
            "reason": self.reason,
            "label": self.label,
        }


class SignatureFieldDetector:
    """Detect likely signature fields in PDF documents."""

    def detect_pdf(self, pdf_path: str, page_index: Optional[int] = None) -> List[SignatureFieldCandidate]:
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        candidates: list[SignatureFieldCandidate] = []
        with pikepdf.open(pdf_path) as pdf:
            page_indexes = [page_index] if page_index is not None else list(range(len(pdf.pages)))
            for idx in page_indexes:
                if idx < 0 or idx >= len(pdf.pages):
                    continue
                candidates.extend(self._detect_acroform_candidates(pdf, idx))

        if page_index is not None:
            pages_for_heuristics = [page_index]
        else:
            pages_for_heuristics = page_indexes[:3]

        # Rendered heuristics and OCR hints run only in scan-preprocess mode.
        for idx in pages_for_heuristics:
            try:
                candidates.extend(self._detect_rendered_page_candidates(pdf_path, idx))
            except Exception as exc:
                LOG.debug("Rendered candidate detection failed for page %s: %s", idx, exc)

        if is_scan_preprocess_enabled():
            for idx in pages_for_heuristics:
                try:
                    candidates.extend(self._detect_ocr_candidate_hints(pdf_path, idx))
                except Exception as exc:
                    LOG.debug("OCR candidate detection failed for page %s: %s", idx, exc)

        return self._limit_candidates_per_page(self._dedupe_candidates(candidates))

    def detect_page(self, pdf_path: str, page_index: int) -> List[SignatureFieldCandidate]:
        return self.detect_pdf(pdf_path, page_index=page_index)

    def _detect_acroform_candidates(
        self,
        pdf: pikepdf.Pdf,
        page_index: int,
    ) -> List[SignatureFieldCandidate]:
        candidates: list[SignatureFieldCandidate] = []
        page = pdf.pages[page_index]
        annotations = page.get("/Annots", [])

        for annot_ref in annotations:
            try:
                annot = annot_ref.get_object()
            except Exception:
                annot = annot_ref

            if str(annot.get("/Subtype", "")) != "/Widget":
                continue

            rect = annot.get("/Rect")
            if not rect or len(rect) != 4:
                continue

            x0, y0, x1, y1 = [float(v) for v in rect]
            width = max(0.0, x1 - x0)
            height = max(0.0, y1 - y0)
            if width <= 0 or height <= 0:
                continue

            field_type, confidence, reason = self._infer_form_field_type(annot)
            label = self._extract_field_label(annot)
            if field_type == "unknown" and not label:
                continue

            candidates.append(
                SignatureFieldCandidate(
                    page_index=page_index,
                    field_type=field_type,
                    x=x0,
                    y=y0,
                    width=width,
                    height=height,
                    confidence=confidence,
                    source="acroform",
                    reason=reason,
                    label=label,
                )
            )

        return candidates

    def _infer_form_field_type(self, annot: Any) -> tuple[str, float, str]:
        # Confidence values below are a hand-ranked ordering, not a
        # calibrated probability: real /Sig widgets are most trustworthy
        # (0.99), progressively less-specific text/label matches score
        # lower, and "present but unrecognized" widgets get a middling 0.5
        # rather than 0. They haven't been validated against a labeled set
        # of real-world PDFs -- if auto-placement (which filters on
        # `field_auto_place_confidence`) is too eager or too conservative in
        # practice, these are the values to revisit, ideally with labeled
        # examples of correct vs. incorrect auto-placements.
        field_type = self._pdf_text(annot.get("/FT"))
        field_name = self._extract_field_label(annot).lower()
        tooltip = self._pdf_text(annot.get("/TU")).lower()
        combined = f"{field_name} {tooltip}".strip()

        if field_type == "/Sig" or any(k in combined for k in ("signature", "sign here")):
            return "signature", 0.99 if field_type == "/Sig" else 0.93, "AcroForm signature widget"
        if any(k in combined for k in ("initial", "initials")):
            return "initials", 0.91, "Widget label suggests initials"
        if "date" in combined:
            return "date", 0.88, "Widget label suggests date field"
        if field_type == "/Btn":
            return "checkbox", 0.84, "AcroForm button widget"
        if field_type == "/Ch":
            return "choice", 0.78, "AcroForm choice widget"
        if field_type == "/Tx":
            return "text", 0.72, "AcroForm text widget"
        return "unknown", 0.5, "Widget present without clear signature semantics"

    def _extract_field_label(self, annot: Any) -> str:
        parts: list[str] = []
        for key in ("/T", "/TU", "/TM"):
            value = self._pdf_text(annot.get(key))
            if value:
                parts.append(value)
        return " ".join(parts).strip()

    def _detect_rendered_page_candidates(
        self,
        pdf_path: str,
        page_index: int,
    ) -> List[SignatureFieldCandidate]:
        with pdfium_operation():
            pdf = pdfium.PdfDocument(pdf_path)
        try:
            cv2_module = self._require_cv2()
            if cv2_module is None:
                LOG.debug("OpenCV not available; skipping rendered heuristic candidate detection")
                return []

            with pdfium_operation():
                page = pdf[page_index]
                page_width_pt = float(page.get_width())
                page_height_pt = float(page.get_height())
                bitmap = page.render(scale=2.0, rotation=0)
                image = np.array(bitmap.to_pil().convert("RGB"))
            heuristics = self._detect_from_image(image, cv2_module)

            candidates: list[SignatureFieldCandidate] = []
            for item in heuristics:
                candidates.append(
                    SignatureFieldCandidate(
                        page_index=page_index,
                        field_type=item["field_type"],
                        x=item["x"] * page_width_pt / image.shape[1],
                        y=page_height_pt - (item["y"] + item["height"]) * page_height_pt / image.shape[0],
                        width=item["width"] * page_width_pt / image.shape[1],
                        height=item["height"] * page_height_pt / image.shape[0],
                        confidence=item["confidence"],
                        source="heuristic",
                        reason=item["reason"],
                        label=item["label"],
                    )
                )
            return candidates
        finally:
            with pdfium_operation():
                pdf.close()

    def _detect_ocr_candidate_hints(
        self,
        pdf_path: str,
        page_index: int,
    ) -> List[SignatureFieldCandidate]:
        with pdfium_operation():
            pdf = pdfium.PdfDocument(pdf_path)
        try:
            cv2_module, pytesseract_module = self._require_scan_ocr_stack()
            if cv2_module is None or pytesseract_module is None:
                return []

            with pdfium_operation():
                page = pdf[page_index]
                page_width_pt = float(page.get_width())
                page_height_pt = float(page.get_height())
                bitmap = page.render(scale=2.0, rotation=0)
                image = np.array(bitmap.to_pil().convert("RGB"))

            gray = cv2_module.cvtColor(image, cv2_module.COLOR_RGB2GRAY)
            _, threshold = cv2_module.threshold(gray, 0, 255, cv2_module.THRESH_BINARY + cv2_module.THRESH_OTSU)
            data = pytesseract_module.image_to_data(threshold, output_type=pytesseract_module.Output.DICT, lang="eng")

            tokens = data.get("text", [])
            confidences = data.get("conf", [])
            lefts = data.get("left", [])
            tops = data.get("top", [])
            widths = data.get("width", [])
            heights = data.get("height", [])
            candidates: list[SignatureFieldCandidate] = []

            for idx, raw_text in enumerate(tokens):
                text = str(raw_text or "").strip()
                if not text:
                    continue

                if not self._looks_like_signature_ocr_text(text):
                    continue

                conf = self._parse_tesseract_confidence(confidences, idx)
                # 0.35 is an unvalidated cutoff on Tesseract's raw
                # word-confidence score, chosen to filter obvious OCR noise
                # while still keeping hints from lower-quality scans (where
                # even correct reads often score lower). Not configurable
                # and not exposed to the user, so a document with generally
                # poor OCR quality silently loses all keyword hints below
                # this line rather than surfacing why. Revisit with labeled
                # low-quality-scan examples if OCR hints are found to be
                # too sparse or too noisy in practice.
                if conf < 0.35:
                    continue

                x = float(lefts[idx]) if idx < len(lefts) else 0.0
                y = float(tops[idx]) if idx < len(tops) else 0.0
                width = float(widths[idx]) if idx < len(widths) else 0.0
                height = float(heights[idx]) if idx < len(heights) else 0.0

                if width <= 6 or height <= 6:
                    continue

                candidates.append(
                    SignatureFieldCandidate(
                        page_index=page_index,
                        field_type="ocr_keyword_hint",
                        x=page_width_pt * (x / image.shape[1]),
                        y=page_height_pt - ((y + height) * page_height_pt / image.shape[0]),
                        width=page_width_pt * (width / image.shape[1]),
                        height=page_height_pt * (height / image.shape[0]),
                        # Maps Tesseract's 0-1 confidence into a 0.6-0.94
                        # band: OCR hints are deliberately capped below the
                        # 0.99/0.93 AcroForm-widget scores in
                        # _infer_form_field_type above (OCR text matches are
                        # inherently less reliable evidence of an actual
                        # signature field than a real form widget), while a
                        # floor of 0.6 keeps them above the "unknown widget"
                        # 0.5 score. Not empirically calibrated.
                        confidence=round(0.6 + min(0.34, conf * 0.35), 3),
                        source="ocr",
                        reason=f"OCR keyword hint: {text}",
                        label=text[:48],
                    )
                )

            return candidates
        finally:
            with pdfium_operation():
                pdf.close()

    def _looks_like_signature_ocr_text(self, text: str) -> bool:
        normalized = text.lower().strip()
        if len(normalized) < 3:
            return False

        signature_terms = (
            "sign",
            "signature",
            "sign here",
            "sig",
            "initial",
            "initials",
            "acknowledge",
            "date",
        )
        return any(token in normalized for token in signature_terms)

    def _parse_tesseract_confidence(self, confidences: Sequence[Any], index: int) -> float:
        if index >= len(confidences):
            return 0.0

        try:
            raw_conf = float(confidences[index])
        except (TypeError, ValueError):
            return 0.0

        if raw_conf <= 1:
            return max(0.0, raw_conf)
        return max(0.0, min(1.0, raw_conf / 100.0))

    def _detect_from_image(self, image: np.ndarray, cv2_module: Any) -> List[dict[str, Any]]:
        gray = cv2_module.cvtColor(image, cv2_module.COLOR_RGB2GRAY)
        blur = cv2_module.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2_module.threshold(blur, 0, 255, cv2_module.THRESH_BINARY_INV + cv2_module.THRESH_OTSU)

        height, width = gray.shape[:2]
        candidates: list[dict[str, Any]] = []

        horizontal_kernel = cv2_module.getStructuringElement(cv2_module.MORPH_RECT, (max(20, width // 12), 1))
        horizontal = cv2_module.morphologyEx(binary, cv2_module.MORPH_OPEN, horizontal_kernel)
        for contour in self._contours(horizontal, cv2_module):
            x, y, w, h = cv2_module.boundingRect(contour)
            if self._looks_like_signature_line(w, h, width):
                candidates.append(
                    {
                        "field_type": "signature_line",
                        "x": float(x),
                        "y": float(y),
                        "width": float(w),
                        "height": float(max(h, 4)),
                        "confidence": self._score_line_candidate(x, y, w, h, width, height),
                        "reason": "Long horizontal rule near document text",
                        "label": "signature line",
                    }
                )

        rect_kernel = cv2_module.getStructuringElement(cv2_module.MORPH_RECT, (5, 5))
        closed = cv2_module.morphologyEx(binary, cv2_module.MORPH_CLOSE, rect_kernel, iterations=2)
        for contour in self._contours(closed, cv2_module):
            x, y, w, h = cv2_module.boundingRect(contour)
            if self._looks_like_field_box(w, h, width, height):
                field_type = self._classify_box(w, h)
                candidates.append(
                    {
                        "field_type": field_type,
                        "x": float(x),
                        "y": float(y),
                        "width": float(w),
                        "height": float(h),
                        "confidence": self._score_box_candidate(x, y, w, h, width, height),
                        "reason": "Rectangular field-like region detected",
                        "label": field_type.replace("_", " "),
                    }
                )

        return self._dedupe_candidate_dicts(candidates)

    def _looks_like_signature_line(self, w: int, h: int, page_width: int) -> bool:
        return w >= max(90, int(page_width * 0.12)) and h <= 16 and (w / max(h, 1)) >= 7

    def _looks_like_field_box(self, w: int, h: int, page_width: int, page_height: int) -> bool:
        if w < 70 or h < 18:
            return False
        if w > page_width * 0.75:
            return False
        if h > max(160, int(page_height * 0.18)):
            return False
        return (w / max(h, 1)) >= 1.2

    def _classify_box(self, w: int, h: int) -> str:
        ratio = w / max(h, 1)
        if ratio >= 4.5 and h <= 50:
            return "signature_box"
        if ratio >= 2.0 and h <= 35:
            return "signature_box"
        if w <= 90 and h <= 50:
            return "initials_box"
        return "field_box"

    def _score_line_candidate(self, x: int, y: int, w: int, h: int, page_width: int, page_height: int) -> float:
        length_score = min(1.0, w / max(page_width * 0.45, 1))
        thin_score = 1.0 - min(1.0, h / 16.0)
        bottom_bonus = 0.12 if y > page_height * 0.45 else 0.0
        return round(min(0.99, 0.45 + 0.4 * length_score + 0.2 * thin_score + bottom_bonus), 3)

    def _score_box_candidate(self, x: int, y: int, w: int, h: int, page_width: int, page_height: int) -> float:
        size_score = min(1.0, (w * h) / max((page_width * page_height) * 0.01, 1))
        aspect_score = min(1.0, max(w / max(h, 1), h / max(w, 1)))
        bottom_bonus = 0.1 if y > page_height * 0.45 else 0.0
        return round(min(0.95, 0.35 + 0.4 * size_score + 0.15 * aspect_score + bottom_bonus), 3)

    def _contours(self, image: np.ndarray, cv2_module: Any) -> Iterable[np.ndarray]:
        found = cv2_module.findContours(image, cv2_module.RETR_EXTERNAL, cv2_module.CHAIN_APPROX_SIMPLE)
        if len(found) == 3:
            _, contours, _ = found
        else:
            contours, _ = found
        return contours

    def _require_cv2(self) -> Any:
        try:
            return importlib.import_module("cv2")
        except Exception:
            return None

    def _require_scan_ocr_stack(self) -> tuple[Any, Any]:
        try:
            cv2_module = importlib.import_module("cv2")
        except Exception:
            return None, None

        try:
            pytesseract_module = importlib.import_module("pytesseract")
        except Exception:
            return cv2_module, None

        return cv2_module, pytesseract_module

    def _dedupe_candidates(self, candidates: Sequence[SignatureFieldCandidate]) -> List[SignatureFieldCandidate]:
        ordered = sorted(candidates, key=lambda c: c.confidence, reverse=True)
        output: list[SignatureFieldCandidate] = []
        for candidate in ordered:
            if any(self._rect_overlap((candidate.x, candidate.y, candidate.width, candidate.height), (existing.x, existing.y, existing.width, existing.height)) > 0.55 for existing in output):
                continue
            output.append(candidate)
        return sorted(output, key=lambda c: (c.page_index, -c.confidence, c.y, c.x))

    def _dedupe_candidate_dicts(self, candidates: Sequence[dict[str, Any]]) -> List[dict[str, Any]]:
        ordered = sorted(candidates, key=lambda c: c["confidence"], reverse=True)
        output: list[dict[str, Any]] = []
        for candidate in ordered:
            if any(self._rect_overlap((candidate["x"], candidate["y"], candidate["width"], candidate["height"]), (existing["x"], existing["y"], existing["width"], existing["height"])) > 0.55 for existing in output):
                continue
            output.append(candidate)
        return output

    def _limit_candidates_per_page(self, candidates: Sequence[SignatureFieldCandidate]) -> List[SignatureFieldCandidate]:
        by_page: dict[int, list[SignatureFieldCandidate]] = {}
        for candidate in candidates:
            by_page.setdefault(candidate.page_index, []).append(candidate)

        output: list[SignatureFieldCandidate] = []
        for page_index in sorted(by_page):
            page_candidates = by_page[page_index]
            acroform = [candidate for candidate in page_candidates if candidate.source == "acroform"]
            heuristic = [candidate for candidate in page_candidates if candidate.source != "acroform"]

            heuristic.sort(key=lambda c: (-c.confidence, c.y, c.x, c.field_type))
            heuristic = heuristic[:MAX_HEURISTIC_CANDIDATES_PER_PAGE]

            page_output = sorted(
                acroform + heuristic,
                key=lambda c: (-c.confidence, c.source != "acroform", c.y, c.x, c.field_type),
            )
            output.extend(page_output[:MAX_TOTAL_CANDIDATES_PER_PAGE])

        return output

    def _rect_overlap(
        self,
        a: tuple[float, float, float, float],
        b: tuple[float, float, float, float],
    ) -> float:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        a1 = (ax, ay, ax + aw, ay + ah)
        b1 = (bx, by, bx + bw, by + bh)

        ix0 = max(a1[0], b1[0])
        iy0 = max(a1[1], b1[1])
        ix1 = min(a1[2], b1[2])
        iy1 = min(a1[3], b1[3])
        if ix1 <= ix0 or iy1 <= iy0:
            return 0.0

        inter = (ix1 - ix0) * (iy1 - iy0)
        a_area = aw * ah
        b_area = bw * bh
        return inter / max((a_area + b_area - inter), 1.0)

    def _pdf_text(self, value: Any) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
        return re.sub(r"\s+", " ", text)
