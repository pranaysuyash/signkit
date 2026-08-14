"""Confidence calibrators implemented in pure numpy (no sklearn/scipy).

Two methods are provided:

- ``platt``  : logistic regression on the raw score (Platt scaling).
- ``isotonic``: isotonic regression via Pool Adjacent Violators (PAVA).

Both return a fitted object that ``apply_calibrator`` maps new scores through.

Calibration must be a *non-decreasing* function of the raw confidence: the
detector's confidence is used as a ranking for auto-placement, so an inverted
map would silently reverse the ranking. If a fit comes out decreasing (which
happens on noisy / heavily imbalanced splits where the raw score is a poor
discriminator), we flip it back to non-decreasing and flag ``inverted=True``
so the report surfaces that the raw confidence direction was unreliable.
"""

from __future__ import annotations

import numpy as np


def platt_fit(
    conf: np.ndarray,
    labels: np.ndarray,
    n_iter: int = 300,
    lr: float = 0.5,
    l2: float = 1e-3,
) -> dict:
    """Fit ``p = sigmoid(a*x + b)`` via gradient descent (L2-regularized).

    Returns a dict with ``a``, ``b`` and ``inverted`` (True when the fitted
    slope was negative and was flipped to keep the map non-decreasing).
    """
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
    inverted = a < 0
    if inverted:
        # Flip to a non-decreasing map: sigmoid(-(a*x+b)) = 1 - sigmoid(a*x+b).
        a = -a
        b = -b
    return {"a": float(a), "b": float(b), "inverted": inverted}


def platt_apply(params: dict, conf: np.ndarray) -> np.ndarray:
    a, b = params["a"], params["b"]
    z = a * np.asarray(conf, dtype=float) + b
    return 1.0 / (1.0 + np.exp(-z))


def isotonic_fit(
    conf: np.ndarray,
    labels: np.ndarray,
) -> dict:
    """Isotonic regression (non-decreasing) via PAVA.

    Aggregates by unique score first (avoids float-tie noise), runs PAVA on the
    per-score mean label, then returns a strictly-increasing ``block_x`` grid and
    the calibrated ``block_y`` so ``np.interp`` can be used for a guaranteed
    non-decreasing lookup.
    """
    x = np.asarray(conf, dtype=float)
    y = np.asarray(labels, dtype=float)
    uniq_x, inv = np.unique(x, return_inverse=True)
    # Weighted by count so the PAVA merge uses the true per-score base rate.
    counts = np.array([int((inv == i).sum()) for i in range(len(uniq_x))], dtype=float)
    means = np.array([float(y[inv == i].mean()) for i in range(len(uniq_x))])

    blocks: list[list[float]] = []  # [x_mean, y_mean, count]
    for xi, yi, ci in zip(uniq_x, means, counts):
        blocks.append([float(xi), float(yi), float(ci)])
        # Compare the stored means directly (position [1]); the count is only
        # used to weight the merged mean. Dividing the mean by its count here
        # was a bug that broke monotonicity when blocks had unequal counts.
        while len(blocks) >= 2 and blocks[-1][1] < blocks[-2][1]:
            b2 = blocks.pop()
            b1 = blocks.pop()
            merged_count = b1[2] + b2[2]
            merged_y = (b1[1] * b1[2] + b2[1] * b2[2]) / merged_count
            merged_x = (b1[0] * b1[2] + b2[0] * b2[2]) / merged_count
            blocks.append([merged_x, merged_y, merged_count])

    block_x = np.array([b[0] for b in blocks], dtype=float)
    block_y = np.array([b[1] for b in blocks], dtype=float)
    inverted = block_y[0] > block_y[-1]
    return {"block_x": block_x, "block_y": block_y, "inverted": inverted}


def isotonic_apply(
    params: dict,
    conf: np.ndarray,
) -> np.ndarray:
    block_x = params["block_x"]
    block_y = params["block_y"]
    return np.interp(np.asarray(conf, dtype=float), block_x, block_y)


def fit_calibrator(
    conf: np.ndarray,
    labels: np.ndarray,
    method: str = "isotonic",
) -> tuple[str, dict]:
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
