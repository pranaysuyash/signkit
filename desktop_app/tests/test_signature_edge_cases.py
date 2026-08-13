"""Deterministic edge-case corpus checks for the local signature pipeline."""

import io
import json
from pathlib import Path

import pytest
from PIL import Image

from desktop_app.processing.extractor import SignatureExtractor


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "desktop_app/tests/fixtures/signature_edge_cases"
METADATA_PATH = FIXTURE_DIR / "metadata.json"


def _cases() -> list[dict]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return metadata["cases"]


def _assert_detected_bbox(extractor: SignatureExtractor, case: dict) -> tuple[str, tuple[int, int, int, int]]:
    image_path = ROOT / case["file"]
    session_id = extractor.create_session(str(image_path))
    detected = extractor.auto_detect_signature(session_id)
    assert detected is not None, f"expected a detection for {case['name']}"
    session = extractor.get_session(session_id)
    assert session is not None
    x1, y1, x2, y2 = detected
    assert 0 <= x1 < x2 <= session.width
    assert 0 <= y1 < y2 <= session.height
    assert x2 - x1 >= case["min_width"]
    assert y2 - y1 >= case["min_height"]
    return session_id, detected


def test_edge_case_inventory_is_versioned_and_privacy_safe():
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    assert metadata["schema_version"] == "1.0.0"
    assert metadata["seed"] == 20260812
    assert metadata["privacy"].startswith("synthetic only")
    assert {case["name"] for case in metadata["cases"]} == {
        "blank_canvas",
        "low_contrast",
        "rotated_tilted",
        "offset_noisy",
        "partial_occlusion",
        "multi_signature",
    }
    for case in metadata["cases"]:
        assert (ROOT / case["file"]).is_file()


@pytest.mark.parametrize("case", _cases(), ids=lambda case: case["name"])
def test_edge_case_auto_detection_contract(case):
    extractor = SignatureExtractor()
    image_path = ROOT / case["file"]
    session_id = extractor.create_session(str(image_path))
    detected = extractor.auto_detect_signature(session_id)
    if case["expected_detection"] == "none":
        assert detected is None
        return
    _assert_detected_bbox(extractor, case)


@pytest.mark.parametrize(
    "case",
    [case for case in _cases() if case["expected_detection"] == "present"],
    ids=lambda case: case["name"],
)
def test_edge_case_detection_flows_into_rgba_processing(case):
    extractor = SignatureExtractor()
    session_id, (x1, y1, x2, y2) = _assert_detected_bbox(extractor, case)
    output = extractor.process_selection(
        session_id=session_id,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        threshold=180,
        color="#111111",
        auto_clean=True,
    )
    image = Image.open(io.BytesIO(output))
    assert image.mode == "RGBA"
    assert image.size == (x2 - x1, y2 - y1)
    assert image.getchannel("A").getbbox() is not None


def test_edge_case_contract_rejects_a_mutated_detector(monkeypatch):
    """Dynamic mutation probe: the contract must fail if detection is disabled."""
    case = next(case for case in _cases() if case["expected_detection"] == "present")
    monkeypatch.setattr(SignatureExtractor, "auto_detect_signature", lambda self, session_id: None)
    extractor = SignatureExtractor()
    with pytest.raises(AssertionError, match="expected a detection"):
        _assert_detected_bbox(extractor, case)
