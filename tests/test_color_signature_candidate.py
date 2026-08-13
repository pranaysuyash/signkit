from __future__ import annotations

import cv2
import numpy as np

from desktop_app.processing.extractor import (
    SignatureExtractor,
    SignatureCandidate,
    _find_color_signature_candidate,
    _find_color_signature_candidates,
)


def test_color_candidate_prefers_blue_ink_over_grayscale_document_text() -> None:
    image = np.full((240, 320, 3), 235, dtype=np.uint8)
    cv2.putText(image, "PRINTED TEXT", (8, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)
    cv2.line(image, (95, 160), (150, 125), (190, 45, 20), 8)
    cv2.ellipse(image, (170, 150), (45, 22), -12, 0, 300, (190, 45, 20), 8)

    detected = _find_color_signature_candidate(image)

    assert detected is not None
    x1, y1, x2, y2 = detected
    assert x1 < 95 < x2
    assert y1 < 125 < y2
    assert x2 - x1 < 180


def test_color_candidates_return_multiple_ranked_regions() -> None:
    image = np.full((320, 480, 3), 235, dtype=np.uint8)
    cv2.ellipse(image, (130, 130), (55, 24), -10, 0, 300, (190, 45, 20), 8)
    cv2.ellipse(image, (350, 230), (55, 24), 8, 0, 300, (170, 40, 15), 8)

    candidates = _find_color_signature_candidates(image)

    assert len(candidates) >= 2
    assert candidates[0][1] >= candidates[1][1]
    assert _find_color_signature_candidate(image) == candidates[0][0]


def test_extractor_exposes_ranked_multi_candidate_api(tmp_path) -> None:
    image = np.full((320, 480, 3), 235, dtype=np.uint8)
    cv2.ellipse(image, (130, 130), (55, 24), -10, 0, 300, (190, 45, 20), 8)
    cv2.ellipse(image, (350, 230), (55, 24), 8, 0, 300, (170, 40, 15), 8)
    image_path = tmp_path / "two_signatures.jpg"
    assert cv2.imwrite(str(image_path), image)

    extractor = SignatureExtractor()
    session_id = extractor.create_session(str(image_path))
    candidates = extractor.auto_detect_signatures(session_id, max_candidates=2, min_confidence=0.75)

    assert len(candidates) == 2
    assert candidates[0].confidence >= candidates[1].confidence


def test_extractor_returns_explicit_grayscale_fallback_candidate(tmp_path, monkeypatch) -> None:
    image = np.full((120, 160, 3), 235, dtype=np.uint8)
    image_path = tmp_path / "grayscale_signature.jpg"
    assert cv2.imwrite(str(image_path), image)

    extractor = SignatureExtractor()
    session_id = extractor.create_session(str(image_path))
    monkeypatch.setattr(
        "desktop_app.processing.extractor._find_color_signature_candidates",
        lambda _image: [],
    )
    monkeypatch.setattr(
        SignatureExtractor,
        "auto_detect_signature",
        lambda _self, _session_id: (10, 20, 80, 60),
    )

    candidates = extractor.auto_detect_signatures(session_id)

    assert candidates == [
        SignatureCandidate(
            bbox=(10, 20, 80, 60),
            confidence=0.4,
            source="grayscale-fallback",
        )
    ]
