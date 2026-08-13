"""Tests for labeled-corpus metric definitions and matching behavior."""

from pathlib import Path

import pytest

from tools.evaluate_signature_corpus import (
    _load_corpus,
    evaluate_corpus,
    evaluate_case,
    evaluate_counts,
    intersection_over_union,
    match_boxes,
)


ROOT = Path(__file__).resolve().parents[1]


def test_iou_is_one_for_identical_boxes_and_zero_for_disjoint_boxes():
    assert intersection_over_union((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert intersection_over_union((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_matching_is_one_to_one_and_prefers_highest_iou():
    truth = [(0, 0, 10, 10), (20, 20, 30, 30)]
    predictions = [(0, 0, 10, 10), (0, 0, 9, 9), (100, 100, 110, 110)]
    matches = match_boxes(truth, predictions, 0.5)
    assert [(match.truth_index, match.prediction_index) for match in matches] == [(0, 0)]


def test_counts_distinguish_false_positive_and_false_negative():
    counts = evaluate_counts(truth_count=3, prediction_count=2, matched_count=1)
    assert counts["true_positive"] == 1
    assert counts["false_positive"] == 1
    assert counts["false_negative"] == 2
    assert counts["precision"] == 0.5
    assert counts["recall"] == 1 / 3


def test_case_reports_localization_and_count_error():
    result = evaluate_case([(0, 0, 10, 10), (20, 20, 30, 30)], [(0, 0, 10, 10)], iou_threshold=0.5)
    assert result["truth_count"] == 2
    assert result["prediction_count"] == 1
    assert result["count_absolute_error"] == 1
    assert result["matched_iou"] == [1.0]


def test_synthetic_corpus_baseline_reports_the_known_single_box_limit():
    corpus = _load_corpus(
        ROOT / "desktop_app/tests/fixtures/signature_edge_cases/metadata.json",
        ROOT,
    )
    report = evaluate_corpus(corpus, ROOT, 0.5)
    assert report["case_count"] == 6
    assert report["presence"]["recall"] == 1.0
    assert report["instances"]["recall"] == 5 / 6
    assert report["count"]["exact_accuracy"] == 5 / 6
    assert report["average_precision"] == pytest.approx(5 / 6)
