"""Detector adapters bridging real detectors to the calibration harness.

The real detector modules are imported **lazily** inside ``detect`` so that
importing this package (and running the self-test) never pulls in the desktop
app, OpenCV, PyQt, or PDF libraries. Only the adapter you actually use is
imported.
"""

from __future__ import annotations

from typing import List

from .types import Candidate, Sample


class PdfFieldAdapter:
    """Runs desktop_app/pdf/field_detection.py against each PDF sample."""

    name = "pdf"

    def __init__(self) -> None:
        self._detector = None

    def _get(self):
        if self._detector is None:
            from desktop_app.pdf.field_detection import SignatureFieldDetector

            self._detector = SignatureFieldDetector()
        return self._detector

    def detect(self, sample: Sample) -> List[Candidate]:
        if not sample.asset_path:
            return []
        candidates = self._get().detect_pdf(sample.asset_path)
        return [
            Candidate(
                sample_id=sample.sample_id,
                confidence=float(c.confidence),
                bbox=(c.x, c.y, c.width, c.height),
                page_index=c.page_index,
                source=c.source,
            )
            for c in candidates
        ]


class ImageSignatureAdapter:
    """Runs desktop_app/processing/extractor.py against each image sample."""

    name = "image"

    def __init__(self) -> None:
        self._extractor = None

    def _get(self):
        if self._extractor is None:
            from desktop_app.processing.extractor import SignatureExtractor

            self._extractor = SignatureExtractor()
        return self._extractor

    def detect(self, sample: Sample) -> List[Candidate]:
        if not sample.asset_path:
            return []
        extractor = self._get()
        session_id = extractor.create_session(sample.asset_path)
        raw = extractor.auto_detect_signatures(
            session_id, max_candidates=10, min_confidence=0.0
        )
        out: List[Candidate] = []
        for c in raw:
            x1, y1, x2, y2 = c.bbox
            out.append(
                Candidate(
                    sample_id=sample.sample_id,
                    confidence=float(c.confidence),
                    bbox=(float(x1), float(y1), float(x2 - x1), float(y2 - y1)),
                    source=c.source,
                )
            )
        return out


class SyntheticAdapter:
    """Returns precomputed candidates stored on the sample (self-test only)."""

    name = "synthetic"

    def detect(self, sample: Sample) -> List[Candidate]:
        return list(sample.synthetic_candidates or [])
