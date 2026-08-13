#!/usr/bin/env python3
"""Evaluate SignverOD directly from protected Parquet shards.

Only signature-class boxes are treated as ground truth. Images are decoded in
memory and never copied into the repository.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import uuid
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from desktop_app.processing.extractor import ProcessingSession, SignatureExtractor
from tools.evaluate_signature_corpus import average_precision, evaluate_case


def _signature_boxes(objects: dict, width: float, height: float) -> list[tuple[float, float, float, float]]:
    boxes: list[tuple[float, float, float, float]] = []
    for category, box in zip(objects.get("category", []), objects.get("bbox", [])):
        if int(category) != 1:
            continue
        x, y, box_width, box_height = (float(value) for value in box)
        boxes.append((x, y, x + box_width, y + box_height))
    return boxes


def _decode_image(image_value: dict) -> np.ndarray:
    image_bytes = image_value.get("bytes")
    if not image_bytes:
        raise ValueError("SignverOD row has no embedded image bytes")
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("SignverOD image bytes could not be decoded")
    return image


def evaluate(paths: list[Path], *, max_candidates: int, min_confidence: float, iou_threshold: float) -> dict[str, object]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError(
            "SignverOD evaluation requires the optional pyarrow dependency; "
            "install the research environment before running this tool."
        ) from exc

    extractor = SignatureExtractor()
    cases: list[dict[str, object]] = []
    predictions_by_case: list[list[tuple[tuple[float, float, float, float], float]]] = []
    total_rows = 0
    skipped_rows = 0
    for path in paths:
        parquet_file = pq.ParquetFile(path)
        for batch in parquet_file.iter_batches(columns=["image", "width", "height", "objects", "image_id"]):
            rows = batch.to_pylist()
            for row in rows:
                total_rows += 1
                image = _decode_image(row["image"])
                height, width = image.shape[:2]
                truth = _signature_boxes(row["objects"], width, height)
                session_id = str(uuid.uuid4())
                extractor.sessions[session_id] = ProcessingSession(
                    session_id=session_id,
                    original_image=image,
                    processed_image=None,
                    created_at=0.0,
                    file_path=f"{path}#image_id={row['image_id']}",
                    dimensions=(height, width),
                )
                candidates = extractor.auto_detect_signatures(
                    session_id,
                    max_candidates=max_candidates,
                    min_confidence=min_confidence,
                )
                predictions = [
                    ((float(x1), float(y1), float(x2), float(y2)), float(candidate.confidence))
                    for candidate in candidates
                    for x1, y1, x2, y2 in [candidate.bbox]
                ]
                case = {"name": f"image-{row['image_id']}", "ground_truth": truth}
                case_result = evaluate_case(truth, [box for box, _ in predictions], iou_threshold=iou_threshold)
                cases.append(case)
                predictions_by_case.append(predictions)
                if not truth and not predictions:
                    skipped_rows += 1
                extractor.sessions.clear()

    results = [
        evaluate_case(case["ground_truth"], [box for box, _ in predictions], iou_threshold=iou_threshold)
        for case, predictions in zip(cases, predictions_by_case)
    ]
    total_truth = sum(result["truth_count"] for result in results)
    total_predictions = sum(result["prediction_count"] for result in results)
    total_matches = sum(len(result["matches"]) for result in results)
    matched_ious = [iou for result in results for iou in result["matched_iou"]]
    count_errors = [result["count_absolute_error"] for result in results]
    presence_truth = sum(bool(case["ground_truth"]) for case in cases)
    presence_predictions = sum(bool(predictions) for predictions in predictions_by_case)
    presence_correct = sum(bool(case["ground_truth"]) == bool(predictions) for case, predictions in zip(cases, predictions_by_case))
    return {
        "schema_version": "1.0.0",
        "dataset": "SignverOD",
        "rows": total_rows,
        "skipped_negative_rows": skipped_rows,
        "iou_threshold": iou_threshold,
        "max_candidates": max_candidates,
        "min_confidence": min_confidence,
        "presence": {
            "truth_present": presence_truth,
            "prediction_present": presence_predictions,
            "exact_accuracy": presence_correct / len(cases) if cases else 0.0,
        },
        "instances": {
            "truth": total_truth,
            "predictions": total_predictions,
            "matched": total_matches,
            "precision": total_matches / total_predictions if total_predictions else 0.0,
            "recall": total_matches / total_truth if total_truth else 0.0,
        },
        "localization": {
            "matched_count": len(matched_ious),
            "mean_iou": statistics.mean(matched_ious) if matched_ious else 0.0,
        },
        "count": {
            "exact_accuracy": sum(error == 0 for error in count_errors) / len(count_errors) if count_errors else 0.0,
            "mean_absolute_error": statistics.mean(count_errors) if count_errors else 0.0,
        },
        "average_precision": average_precision(cases, predictions_by_case, iou_threshold=iou_threshold),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet", nargs="+", type=Path)
    parser.add_argument("--max-candidates", type=int, default=2)
    parser.add_argument("--min-confidence", type=float, default=0.75)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(
        args.parquet,
        max_candidates=args.max_candidates,
        min_confidence=args.min_confidence,
        iou_threshold=args.iou_threshold,
    )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
