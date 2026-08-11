"""Document matching logic for workflow recipe execution."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, NamedTuple, Optional

from desktop_app.workflows import models


def _get_pikepdf():
    """Load pikepdf only when needed.

    Workflows are shared across environments where optional PDF bindings are
    present. Defer import here so test/runtime surfaces can load this module
    without a hard dependency when matcher features are unused.
    """
    try:
        import pikepdf  # type: ignore[import-not-found]

        return pikepdf
    except ModuleNotFoundError as exc:
        raise RuntimeError("pikepdf is required for workflow matching in this environment") from exc


def compute_pdf_hash(path: str, *, block_size: int = 1024 * 1024) -> str:
    """Compute a stable SHA-256 hash for the full PDF bytes."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(block_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


class MatchResult(NamedTuple):
    match_class: str
    confidence: float
    evidence: Dict[str, str]


def evaluate_match(recipe: models.ControlledSigningRecipe, pdf_path: str) -> MatchResult:
    """Evaluate how a PDF matches a recipe matcher policy.

    Returns one of:
    - exact: strict rule met
    - family: close heuristic match
    - review_only: ambiguous and/or unsupported for unattended execution
    """
    matcher = dict(recipe.document_matcher or {})
    kind = str(matcher.get("kind") or "exact").lower()
    evidence: Dict[str, str] = {"matcher": kind}
    doc_path = Path(pdf_path)

    if not doc_path.exists():
        return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {"error": "input_missing"})
    if doc_path.suffix.lower() != ".pdf":
        return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {"error": "input_not_pdf"})

    try:
        pikepdf = _get_pikepdf()
        pdf = pikepdf.open(str(doc_path))
    except Exception as exc:
        return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {"error": f"pdf_open_failed:{exc}"})

    try:
        page_count = len(pdf.pages)
        first = pdf.pages[0]
        media_box = list(first.MediaBox)
        if len(media_box) < 4:
            raise ValueError("invalid_media_box")
        width = float(media_box[2]) - float(media_box[0])
        height = float(media_box[3]) - float(media_box[1])
        metadata = dict(pdf.docinfo) if pdf.docinfo else {}
    finally:
        pdf.close()

    evidence["page_count"] = str(page_count)
    evidence["page_size"] = json.dumps({"width": round(width, 2), "height": round(height, 2)})

    if kind == models.MatchClass.EXACT.value:
        return _evaluate_exact_match(recipe, doc_path, pdf_path, matcher, page_count, width, height, evidence)
    if kind == models.MatchClass.FAMILY.value:
        return _evaluate_family_match(recipe, doc_path, page_count, width, height, evidence, matcher)

    return _evaluate_exact_match(recipe, doc_path, pdf_path, matcher, page_count, width, height, evidence)


def _evaluate_exact_match(
    recipe: models.ControlledSigningRecipe,
    doc_path: Path,
    pdf_path: str,
    matcher: Dict[str, object],
    page_count: int,
    width: float,
    height: float,
    evidence: Dict[str, str],
) -> MatchResult:
    expected_prefix = _normalize_str(matcher.get("filename_prefix"))
    expected_exact_name = _normalize_str(matcher.get("filename"))
    expected_sha = _normalize_str(matcher.get("sha256"))
    expected_pages = _normalize_int(matcher.get("page_count"))
    expected_page_width = _normalize_float(matcher.get("page_width"))
    expected_page_height = _normalize_float(matcher.get("page_height"))

    if expected_sha:
        actual_sha = compute_pdf_hash(pdf_path)
        evidence["sha256"] = actual_sha
        if actual_sha == expected_sha:
            return MatchResult(models.MatchClass.EXACT.value, 1.0, {**evidence, "sha256_match": "true"})
        return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {**evidence, "sha256_match": "false"})

    if expected_exact_name:
        if doc_path.name == expected_exact_name:
            return MatchResult(models.MatchClass.EXACT.value, 1.0, {**evidence, "filename_exact": "true"})
        return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {**evidence, "filename_exact": "false"})

    if expected_prefix:
        if doc_path.name.startswith(expected_prefix):
            evidence["filename_prefix"] = expected_prefix
            return MatchResult(models.MatchClass.EXACT.value, 0.95, evidence)
        return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.0, {**evidence, "filename_prefix": expected_prefix})

    score = 1.0
    if expected_pages is not None:
        if page_count != expected_pages:
            return MatchResult(models.MatchClass.REVIEW_ONLY.value, 0.2, {**evidence, "page_count_mismatch": "true"})
        evidence["page_count_match"] = "true"
        score *= 0.9

    if expected_page_width is not None and abs(width - expected_page_width) > 1.0:
        evidence["page_width_mismatch"] = "true"
        score *= 0.8

    if expected_page_height is not None and abs(height - expected_page_height) > 1.0:
        evidence["page_height_mismatch"] = "true"
        score *= 0.8

    return MatchResult(models.MatchClass.REVIEW_ONLY.value if score < 0.7 else models.MatchClass.EXACT.value, max(0.0, min(1.0, score)), evidence)


def _evaluate_family_match(
    recipe: models.ControlledSigningRecipe,
    doc_path: Path,
    page_count: int,
    width: float,
    height: float,
    evidence: Dict[str, str],
    matcher: Dict[str, object],
) -> MatchResult:
    del recipe  # reserved for future constraints
    expected_pages = _normalize_int(matcher.get("page_count"))
    expected_page_width = _normalize_float(matcher.get("page_width"))
    expected_page_height = _normalize_float(matcher.get("page_height"))

    score = 0.0
    matched = 0
    total = 0

    if expected_pages is not None:
        total += 1
        if page_count == expected_pages:
            score += 1
            matched += 1
        evidence["expected_page_count"] = str(expected_pages)

    if expected_page_width is not None:
        total += 1
        if abs(width - expected_page_width) <= 1.0:
            score += 1
            matched += 1

    if expected_page_height is not None:
        total += 1
        if abs(height - expected_page_height) <= 1.0:
            score += 1
            matched += 1

    if total == 0:
        score = 0.55
    else:
        score = score / total
    evidence["family_score"] = f"{matched}/{total}"
    if score >= 0.8:
        return MatchResult(models.MatchClass.FAMILY.value, score, evidence)
    if score >= 0.5 and page_count >= 1:
        return MatchResult(models.MatchClass.FAMILY.value, score, {**evidence, "warn": "imperfect_family_match"})
    return MatchResult(models.MatchClass.REVIEW_ONLY.value, score, {**evidence, "warn": "family_failed"})


def _normalize_str(value: object) -> Optional[str]:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _normalize_int(value: object) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
