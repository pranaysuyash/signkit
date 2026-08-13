"""Calibration and discrimination metrics (pure numpy, no sklearn).

All functions take numpy arrays / plain sequences and return floats or lists so
the harness has zero heavy ML dependencies.
"""

from __future__ import annotations

import numpy as np


def iou(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> float:
    """IoU of two ``(x, y, w, h)`` boxes. Returns 0.0 when disjoint."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix0 = max(ax, bx)
    iy0 = max(ay, by)
    ix1 = min(ax + aw, bx + bw)
    iy1 = min(ay + ah, by + bh)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    union = aw * ah + bw * bh - inter
    if union <= 0:
        return 0.0
    return inter / union


def max_iou(
    bbox: tuple[float, float, float, float],
    gts: list[tuple[float, float, float, float]],
) -> float:
    """Best IoU between ``bbox`` and any ground-truth box."""
    best = 0.0
    for g in gts:
        v = iou(bbox, g)
        if v > best:
            best = v
    return best


def candidate_labels(
    candidates: list[tuple[float, float, float, float]],
    gts: list[tuple[float, float, float, float]],
    iou_thr: float,
    candidate_page_indexes: list[int | None] | None = None,
    gt_page_indexes: list[int | None] | None = None,
) -> list[int]:
    """Label candidates with deterministic one-to-one IoU matching.

    A single ground-truth box can only explain one candidate. Pair matches are
    considered from highest IoU downward, which avoids inflating precision or
    calibration metrics when overlapping candidates duplicate one signature.
    Optional page indexes prevent a PDF candidate from matching a box on a
    different page while keeping the simple image-call signature compatible.
    """
    candidate_pages = candidate_page_indexes or [None] * len(candidates)
    gt_pages = gt_page_indexes or [None] * len(gts)
    if len(candidate_pages) != len(candidates) or len(gt_pages) != len(gts):
        raise ValueError("page-index arrays must match candidate and ground-truth lengths")

    pairs: list[tuple[float, int, int]] = []
    for candidate_index, candidate in enumerate(candidates):
        for gt_index, gt in enumerate(gts):
            candidate_page = candidate_pages[candidate_index]
            gt_page = gt_pages[gt_index]
            if candidate_page is not None and gt_page is not None and candidate_page != gt_page:
                continue
            overlap = iou(candidate, gt)
            if overlap >= iou_thr:
                pairs.append((overlap, candidate_index, gt_index))

    labels = [0] * len(candidates)
    matched_candidates: set[int] = set()
    matched_gts: set[int] = set()
    for _overlap, candidate_index, gt_index in sorted(
        pairs, key=lambda item: (-item[0], item[1], item[2])
    ):
        if candidate_index in matched_candidates or gt_index in matched_gts:
            continue
        labels[candidate_index] = 1
        matched_candidates.add(candidate_index)
        matched_gts.add(gt_index)
    return labels


def reliability(
    conf: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15,
) -> list[tuple[float, float, float, float, int]]:
    """Reliability bins: (bin_lo, bin_hi, mean_conf, mean_acc, count)."""
    conf = np.asarray(conf, dtype=float)
    labels = np.asarray(labels, dtype=float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(conf, bins) - 1, 0, n_bins - 1)
    out: list[tuple[float, float, float, float, int]] = []
    for b in range(n_bins):
        mask = idx == b
        cnt = int(mask.sum())
        if cnt == 0:
            out.append((float(bins[b]), float(bins[b + 1]), 0.0, 0.0, 0))
        else:
            out.append(
                (
                    float(bins[b]),
                    float(bins[b + 1]),
                    float(conf[mask].mean()),
                    float(labels[mask].mean()),
                    cnt,
                )
            )
    return out


def ece(conf: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float:
    """Expected Calibration Error (absolute, weighted by bin count)."""
    conf = np.asarray(conf, dtype=float)
    labels = np.asarray(labels, dtype=float)
    total = len(conf)
    if total == 0:
        return 0.0
    s = 0.0
    for lo, hi, mean_conf, mean_acc, cnt in reliability(conf, labels, n_bins):
        if cnt == 0:
            continue
        s += (cnt / total) * abs(mean_conf - mean_acc)
    return float(s)


def roc_auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """ROC AUC via the Mann-Whitney / rank statistic (ties averaged)."""
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    pos = labels == 1
    neg = labels == 0
    n_pos = int(pos.sum())
    n_neg = int(neg.sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    # Average ranks across ties.
    _, inv, counts = np.unique(scores, return_inverse=True, return_counts=True)
    avg = np.zeros(len(counts))
    np.add.at(avg, inv, ranks)
    avg /= counts
    ranks = avg[inv]
    sum_ranks_pos = float(ranks[pos].sum())
    return float((sum_ranks_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def pr_auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """Average precision (integral of precision over recall), [0, 1]."""
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    order = np.argsort(-scores, kind="mergesort")
    y = labels[order]
    n_pos = int(y.sum())
    if n_pos == 0:
        return float("nan")
    tp = np.cumsum(y)
    fp = np.cumsum(1 - y)
    recall = tp / n_pos
    prec = tp / (tp + fp)
    ap = 0.0
    prev_recall = 0.0
    for i in range(len(y)):
        if y[i] == 1:
            ap += float(prec[i]) * (recall[i] - prev_recall)
            prev_recall = recall[i]
    return ap


def recall_at_k(
    per_sample: list[tuple[list[tuple], list[tuple]]],
    k: int,
    iou_thr: float,
) -> float:
    """Mean recall of GT boxes covered by the top-k candidates per sample.

    ``per_sample`` is a list of ``(candidates, gts)`` where each candidate is
    ``(bbox, confidence)``. Samples with no GT are skipped.
    """
    recalls: list[float] = []
    for cands, gts in per_sample:
        if not gts:
            continue
        order = sorted(range(len(cands)), key=lambda i: cands[i][1], reverse=True)[:k]
        matched: set[int] = set()
        for i in order:
            cb = cands[i][0]
            for j, gb in enumerate(gts):
                if j in matched:
                    continue
                if iou(cb, gb) >= iou_thr:
                    matched.add(j)
                    break
        recalls.append(len(matched) / len(gts))
    if not recalls:
        return float("nan")
    return float(np.mean(recalls))


def precision_recall_at_threshold(
    conf: np.ndarray,
    labels: np.ndarray,
    thr: float,
) -> tuple[float, float]:
    """Precision/recall of *predicted-positive* candidates at a confidence cut."""
    conf = np.asarray(conf, dtype=float)
    labels = np.asarray(labels, dtype=int)
    pred = conf >= thr
    tp = int(np.logical_and(pred, labels == 1).sum())
    fp = int(np.logical_and(pred, labels == 0).sum())
    fn = int(np.logical_and(~pred, labels == 1).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return precision, recall
