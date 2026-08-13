"""Confidence calibrators implemented in pure numpy (no sklearn/scipy).

Two methods are provided:

- ``platt``  : logistic regression on the raw score (Platt scaling).
- ``isotonic``: isotonic regression via Pool Adjacent Violators (PAVA).

Both return a fitted object that ``apply_calibrator`` maps new scores through.
"""

from __future__ import annotations

import numpy as np


def platt_fit(
    conf: np.ndarray,
    labels: np.ndarray,
    n_iter: int = 300,
    lr: float = 0.5,
    l2: float = 1e-3,
) -> tuple[float, float]:
    """Fit ``p = sigmoid(a*x + b)`` via gradient descent (L2-regularized)."""
    x = np.asarray(conf, dtype=float)
    y = np.asarray(labels, dtype=float)
    a = 0.0
    b = 0.0
    for _ in range(n_iter):
        z = a * x + b
        p = 1.0 / (1.0 + np.exp(-z))
        dz = p - y
        ga = float((dz * x).mean()) + l2 * a
        gb = float(dz.mean()) + l2 * b
        a -= lr * ga
        b -= lr * gb
    return float(a), float(b)


def platt_apply(params: tuple[float, float], conf: np.ndarray) -> np.ndarray:
    a, b = params
    z = a * np.asarray(conf, dtype=float) + b
    return 1.0 / (1.0 + np.exp(-z))


def isotonic_fit(
    conf: np.ndarray,
    labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Isotonic regression (non-decreasing) via PAVA.

    Returns ``(block_x, block_y)`` defining a monotone step function.
    """
    x = np.asarray(conf, dtype=float)
    y = np.asarray(labels, dtype=float)
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    ys = y[order]
    # Blocks of (x_sum, y_sum, count).
    blocks: list[list[float]] = []
    for xi, yi in zip(xs, ys):
        blocks.append([xi, yi, 1.0])
        while len(blocks) >= 2 and (blocks[-1][1] / blocks[-1][2]) < (
            blocks[-2][1] / blocks[-2][2]
        ):
            b2 = blocks.pop()
            b1 = blocks.pop()
            blocks.append([b1[0] + b2[0], b1[1] + b2[1], b1[2] + b2[2]])
    block_x = np.array([b[0] / b[2] for b in blocks], dtype=float)
    block_y = np.array([b[1] / b[2] for b in blocks], dtype=float)
    return block_x, block_y


def isotonic_apply(
    fit: tuple[np.ndarray, np.ndarray],
    conf: np.ndarray,
) -> np.ndarray:
    block_x, block_y = fit
    c = np.asarray(conf, dtype=float)
    idx = np.searchsorted(block_x, c, side="right") - 1
    idx = np.clip(idx, 0, len(block_x) - 1)
    return block_y[idx]


def fit_calibrator(
    conf: np.ndarray,
    labels: np.ndarray,
    method: str = "isotonic",
):
    """Fit a calibrator on ``(conf, labels)``. Returns ``(kind, params)``."""
    conf = np.asarray(conf, dtype=float)
    labels = np.asarray(labels, dtype=int)
    if method == "platt":
        return ("platt", platt_fit(conf, labels))
    return ("isotonic", isotonic_fit(conf, labels))


def apply_calibrator(cal, conf: np.ndarray) -> np.ndarray:
    """Apply a fitted calibrator to raw scores, returning calibrated scores."""
    kind, params = cal
    if kind == "platt":
        return platt_apply(params, conf)
    return isotonic_apply(params, conf)
