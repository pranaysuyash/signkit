"""Shared data types for the calibration harness.

A ``Candidate`` is a detector output normalized to ``(x, y, w, h)`` in the
detector's native coordinate space for that sample. A ``GroundTruth`` box uses
the same convention, so IoU is computed in-sample without cross-space math.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class Candidate:
    """A detector output, normalized to ``(x, y, w, h)``.

    ``bbox`` is in the detector's native coordinate space for its sample
    (PDF points for the PDF detector, pixels for the image detector).
    """

    sample_id: str
    confidence: float
    bbox: tuple[float, float, float, float]
    page_index: Optional[int] = None
    source: str = ""


@dataclass(frozen=True)
class GroundTruth:
    """A labeled box, same ``(x, y, w, h)`` convention as ``Candidate``."""

    sample_id: str
    bbox: tuple[float, float, float, float]
    page_index: Optional[int] = None
    label: str = "signature"


@dataclass
class Sample:
    """One input asset plus its ground-truth boxes (empty = negative sample)."""

    sample_id: str
    asset_path: Optional[str]
    ground_truth: List[GroundTruth] = field(default_factory=list)
    split: str = "all"  # train | val | test | all
    # Precomputed candidates for self-test fixtures (kept out of real manifests).
    synthetic_candidates: Optional[List[Candidate]] = None


@dataclass
class DatasetSpec:
    """A labeled dataset for one detector."""

    name: str
    detector: str  # "pdf" | "image" | "synthetic"
    samples: List[Sample] = field(default_factory=list)
    iou_match_threshold: float = 0.5


@runtime_checkable
class DetectorAdapter(Protocol):
    """Bridges a detector to the harness. Implement ``detect`` per detector."""

    name: str

    def detect(self, sample: Sample) -> List[Candidate]:
        """Run the detector on ``sample`` and return its candidates."""
        ...
