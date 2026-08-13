from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from tools.import_ultralytics_signature_corpus import convert


def _write_case(root: Path, split: str, name: str, label: str) -> None:
    image_dir = root / "images" / split
    label_dir = root / "labels" / split
    image_dir.mkdir(parents=True)
    label_dir.mkdir(parents=True)
    Image.new("RGB", (100, 80), "white").save(image_dir / f"{name}.jpg")
    (label_dir / f"{name}.txt").write_text(label)


def test_convert_maps_yolo_boxes_and_preserves_external_relative_paths(tmp_path: Path) -> None:
    _write_case(tmp_path, "train", "train_1", "0 0.5 0.5 0.4 0.5\n")
    _write_case(tmp_path, "val", "val_1", "0 0.25 0.5 0.2 0.25\n")

    metadata = convert(tmp_path, "a" * 64, "2026-08-12", "https://example.test/signature.zip")

    assert len(metadata["cases"]) == 2
    assert metadata["cases"][0]["file"] == "images/train/train_1.jpg"
    assert metadata["cases"][0]["split"] == "development"
    assert metadata["cases"][0]["ground_truth"] == [[30, 20, 70, 60]]
    assert metadata["cases"][1]["split"] == "validation"
    assert metadata["source"]["independent_test_split"] is False


def test_convert_rejects_unknown_class_id(tmp_path: Path) -> None:
    _write_case(tmp_path, "train", "train_1", "1 0.5 0.5 0.4 0.5\n")
    _write_case(tmp_path, "val", "val_1", "0 0.5 0.5 0.4 0.5\n")

    with pytest.raises(ValueError, match="unexpected class id"):
        convert(tmp_path, "b" * 64, "2026-08-12", "https://example.test/signature.zip")
