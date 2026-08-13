from __future__ import annotations

import pytest

from tools.evaluate_signature_corpus import average_precision, evaluate_case


def test_average_precision_is_one_for_ranked_perfect_predictions() -> None:
    cases = [{"ground_truth": [(0.0, 0.0, 10.0, 10.0)]}]

    score = average_precision(
        cases,
        [[((0.0, 0.0, 10.0, 10.0), 1.0)]],
        iou_threshold=0.5,
    )

    assert score == pytest.approx(1.0)


def test_average_precision_penalizes_high_confidence_false_positive() -> None:
    cases = [{"ground_truth": [(0.0, 0.0, 10.0, 10.0)]}]

    score = average_precision(
        cases,
        [[
            ((20.0, 20.0, 30.0, 30.0), 1.0),
            ((0.0, 0.0, 10.0, 10.0), 0.5),
        ]],
        iou_threshold=0.5,
    )

    assert 0.0 < score < 1.0


def test_evaluate_case_matches_multiple_signature_instances_one_to_one() -> None:
    truth = [(0.0, 0.0, 10.0, 10.0), (20.0, 20.0, 30.0, 30.0)]
    predictions = [(0.0, 0.0, 10.0, 10.0), (20.0, 20.0, 30.0, 30.0)]

    result = evaluate_case(truth, predictions, iou_threshold=0.5)

    assert result["true_positive"] == 2
    assert result["false_positive"] == 0
    assert result["false_negative"] == 0
    assert result["count_absolute_error"] == 0
