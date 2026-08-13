#!/usr/bin/env python3
"""Evaluate signature presence, localization, and count against labeled boxes."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from desktop_app.processing.extractor import SignatureCandidate, SignatureExtractor


Box = tuple[float, float, float, float]


@dataclass(frozen=True)
class Match:
    truth_index: int
    prediction_index: int
    iou: float


def _coerce_box(value: Sequence[float], *, field: str) -> Box:
    if len(value) != 4:
        raise ValueError(f"{field} must contain four coordinates")
    x1, y1, x2, y2 = (float(part) for part in value)
    if not (x1 < x2 and y1 < y2):
        raise ValueError(f"{field} must have positive area")
    return x1, y1, x2, y2


def intersection_over_union(left: Box, right: Box) -> float:
    """Return IoU for half-open [x1, y1, x2, y2] boxes."""

    ix1 = max(left[0], right[0])
    iy1 = max(left[1], right[1])
    ix2 = min(left[2], right[2])
    iy2 = min(left[3], right[3])
    intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    left_area = (left[2] - left[0]) * (left[3] - left[1])
    right_area = (right[2] - right[0]) * (right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def match_boxes(truth: Iterable[Box], predictions: Iterable[Box], iou_threshold: float) -> list[Match]:
    """Greedily create one-to-one matches from highest IoU pairs first."""

    if not 0.0 <= iou_threshold <= 1.0:
        raise ValueError("iou_threshold must be between 0 and 1")
    candidates = []
    truth_list = list(truth)
    prediction_list = list(predictions)
    for truth_index, truth_box in enumerate(truth_list):
        for prediction_index, prediction_box in enumerate(prediction_list):
            iou = intersection_over_union(truth_box, prediction_box)
            if iou >= iou_threshold:
                candidates.append((iou, truth_index, prediction_index))
    matches: list[Match] = []
    used_truth: set[int] = set()
    used_predictions: set[int] = set()
    for iou, truth_index, prediction_index in sorted(candidates, reverse=True):
        if truth_index in used_truth or prediction_index in used_predictions:
            continue
        used_truth.add(truth_index)
        used_predictions.add(prediction_index)
        matches.append(Match(truth_index, prediction_index, iou))
    return matches


def evaluate_counts(truth_count: int, prediction_count: int, matched_count: int) -> dict[str, float | int]:
    """Calculate instance-level counts and derived precision/recall/F1."""

    true_positive = matched_count
    false_positive = prediction_count - matched_count
    false_negative = truth_count - matched_count
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def evaluate_case(
    truth: Iterable[Box], predictions: Iterable[Box], *, iou_threshold: float
) -> dict[str, object]:
    truth_list = list(truth)
    prediction_list = list(predictions)
    matches = match_boxes(truth_list, prediction_list, iou_threshold)
    counts = evaluate_counts(len(truth_list), len(prediction_list), len(matches))
    ious = [match.iou for match in matches]
    return {
        "truth_count": len(truth_list),
        "prediction_count": len(prediction_list),
        "matches": [
            {
                "truth_index": match.truth_index,
                "prediction_index": match.prediction_index,
                "iou": match.iou,
            }
            for match in matches
        ],
        "matched_iou": ious,
        "count_absolute_error": abs(len(truth_list) - len(prediction_list)),
        **counts,
    }


def average_precision(
    cases: Sequence[dict],
    predictions_by_case: Sequence[Sequence[tuple[Box, float]]],
    *,
    iou_threshold: float,
) -> float:
    """Calculate all-points AP from scored one-to-one box predictions."""
    total_truth = sum(len(case["ground_truth"]) for case in cases)
    ranked: list[tuple[float, int, Box]] = []
    for case_index, predictions in enumerate(predictions_by_case):
        ranked.extend((confidence, case_index, box) for box, confidence in predictions)
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    matched_truth: set[tuple[int, int]] = set()
    true_positives: list[int] = []
    false_positives: list[int] = []
    for _, case_index, prediction in ranked:
        best = max(
            (
                (intersection_over_union(prediction, truth), truth_index)
                for truth_index, truth in enumerate(cases[case_index]["ground_truth"])
                if (case_index, truth_index) not in matched_truth
            ),
            default=(0.0, -1),
        )
        if best[0] >= iou_threshold:
            matched_truth.add((case_index, best[1]))
            true_positives.append(1)
            false_positives.append(0)
        else:
            true_positives.append(0)
            false_positives.append(1)
    if total_truth == 0:
        return 0.0
    cumulative_tp = 0
    cumulative_fp = 0
    precisions: list[float] = []
    recalls: list[float] = []
    for true_positive, false_positive in zip(true_positives, false_positives):
        cumulative_tp += true_positive
        cumulative_fp += false_positive
        precisions.append(cumulative_tp / (cumulative_tp + cumulative_fp))
        recalls.append(cumulative_tp / total_truth)
    recall_points = [0.0, *recalls, 1.0]
    precision_points = [0.0, *precisions, 0.0]
    for index in range(len(precision_points) - 2, -1, -1):
        precision_points[index] = max(precision_points[index], precision_points[index + 1])
    return sum(
        (recall_points[index + 1] - recall_points[index]) * precision_points[index + 1]
        for index in range(len(recall_points) - 1)
    )


def _load_corpus(path: Path, repo_root: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("annotation_schema") != "ground_truth boxes are [x1, y1, x2, y2] in source-image pixels":
        raise ValueError("corpus annotation_schema is missing or unsupported")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("corpus must contain at least one case")
    for case in cases:
        image_path = repo_root / case["file"]
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        case["ground_truth"] = [
            _coerce_box(box, field=f"{case['name']}.ground_truth")
            for box in case.get("ground_truth", [])
        ]
    return cases


def evaluate_corpus(
    cases: list[dict],
    repo_root: Path,
    iou_threshold: float,
    *,
    max_candidates: int = 2,
    min_confidence: float = 0.75,
) -> dict[str, object]:
    extractor = SignatureExtractor()
    case_results = []
    total_truth = total_predictions = total_matches = 0
    presence_truth = presence_predictions = presence_correct = 0
    matched_ious: list[float] = []
    count_errors: list[int] = []
    predictions_by_case: list[list[tuple[Box, float]]] = []

    for case in cases:
        image_path = repo_root / case["file"]
        session_id = extractor.create_session(str(image_path))
        candidates: list[SignatureCandidate] = extractor.auto_detect_signatures(
            session_id,
            max_candidates=max_candidates,
            min_confidence=min_confidence,
        )
        scored_predictions = [
            (
                _coerce_box(candidate.bbox, field=f"{case['name']}.prediction"),
                candidate.confidence,
            )
            for candidate in candidates
        ]
        predictions = [box for box, _ in scored_predictions]
        predictions_by_case.append(scored_predictions)
        result = evaluate_case(case["ground_truth"], predictions, iou_threshold=iou_threshold)
        result["name"] = case["name"]
        result["file"] = case["file"]
        case_results.append(result)
        total_truth += result["truth_count"]
        total_predictions += result["prediction_count"]
        total_matches += len(result["matches"])
        matched_ious.extend(result["matched_iou"])
        count_errors.append(result["count_absolute_error"])
        truth_present = bool(case["ground_truth"])
        prediction_present = bool(predictions)
        presence_truth += int(truth_present)
        presence_predictions += int(prediction_present)
        presence_correct += int(truth_present == prediction_present)

    instance_metrics = evaluate_counts(total_truth, total_predictions, total_matches)
    presence_tp = sum(
        1 for result, case in zip(case_results, cases)
        if bool(case["ground_truth"]) and result["prediction_count"] > 0
    )
    presence_fp = sum(
        1 for result, case in zip(case_results, cases)
        if not case["ground_truth"] and result["prediction_count"] > 0
    )
    presence_fn = sum(
        1 for result, case in zip(case_results, cases)
        if case["ground_truth"] and result["prediction_count"] == 0
    )
    presence_metrics = evaluate_counts(presence_truth, presence_predictions, presence_tp)
    presence_metrics.update({"false_positive": presence_fp, "false_negative": presence_fn})
    return {
        "schema_version": "1.0.0",
        "iou_threshold": iou_threshold,
        "case_count": len(cases),
        "presence": {
            **presence_metrics,
            "exact_accuracy": presence_correct / len(cases),
        },
        "instances": instance_metrics,
        "localization": {
            "matched_count": len(matched_ious),
            "mean_iou": statistics.mean(matched_ious) if matched_ious else 0.0,
            "median_iou": statistics.median(matched_ious) if matched_ious else 0.0,
        },
        "count": {
            "exact_accuracy": sum(error == 0 for error in count_errors) / len(cases),
            "mean_absolute_error": statistics.mean(count_errors),
            "max_absolute_error": max(count_errors),
        },
        "average_precision": average_precision(
            cases, predictions_by_case, iou_threshold=iou_threshold
        ),
        "average_precision_note": "All-points AP from deterministic per-image ranking scores; scores are not calibrated probabilities.",
        "cases": case_results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="desktop_app/tests/fixtures/signature_edge_cases/metadata.json")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--max-candidates", type=int, default=2)
    parser.add_argument("--min-confidence", type=float, default=0.75)
    parser.add_argument(
        "--split",
        action="append",
        help="Evaluate only cases in this split; repeat for multiple splits.",
    )
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    cases = _load_corpus(repo_root / args.corpus, repo_root)
    if args.split:
        selected_splits = set(args.split)
        cases = [case for case in cases if case.get("split") in selected_splits]
        if not cases:
            parser.error("--split selected no corpus cases")
    report = evaluate_corpus(
        cases,
        repo_root,
        args.iou_threshold,
        max_candidates=args.max_candidates,
        min_confidence=args.min_confidence,
    )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        (repo_root / args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
