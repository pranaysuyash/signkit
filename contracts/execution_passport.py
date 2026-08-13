"""Canonical metadata contract for a topology-aware SignKit execution.

The passport is a read-only projection. It carries workflow identity, state,
event receipts, recovery guidance, and opaque evidence references, never
document bytes or local filesystem paths.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


PASSPORT_VERSION = "1.0"
DATA_BOUNDARY_METADATA_ONLY = "metadata_only_no_document_bytes"
ALLOWED_TOPOLOGIES = frozenset({"local", "cloud", "hybrid"})


@dataclass(frozen=True)
class PassportEvidence:
    """Safe event receipt included in the read-only projection."""

    sequence: int
    code: str
    state_from: Optional[str]
    state_to: str
    actor: str
    occurred_at: str
    message: Optional[str] = None


@dataclass(frozen=True)
class ExecutionPassport:
    """Stable cross-surface description of one execution aggregate."""

    execution_id: str
    topology: str
    source_of_truth: str
    owner_role: str
    template_code: str
    template_version: int
    aggregate_status: str
    child_job_id: Optional[str] = None
    child_job_status: Optional[str] = None
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    input_fingerprint: Optional[str] = None
    output_reference: Optional[str] = None
    attempt: Optional[int] = None
    max_attempts: Optional[int] = None
    evidence: tuple[PassportEvidence, ...] = field(default_factory=tuple)
    recovery_action: str = "none"
    data_boundary: str = DATA_BOUNDARY_METADATA_ONLY
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    passport_version: str = PASSPORT_VERSION

    def validate(self) -> "ExecutionPassport":
        """Fail closed when an adapter emits an invalid cross-surface shape."""
        if self.topology not in ALLOWED_TOPOLOGIES:
            raise ValueError(f"Unsupported execution passport topology: {self.topology}")
        if not self.execution_id:
            raise ValueError("Execution passport requires execution_id")
        if not self.source_of_truth:
            raise ValueError("Execution passport requires source_of_truth")
        if self.data_boundary != DATA_BOUNDARY_METADATA_ONLY:
            raise ValueError("Execution passport cannot carry document bytes")
        if self.attempt is not None and self.attempt < 0:
            raise ValueError("Execution passport attempt cannot be negative")
        if self.max_attempts is not None and self.max_attempts < 1:
            raise ValueError("Execution passport max_attempts must be positive")
        return self

    def to_payload(self) -> dict[str, Any]:
        """Serialize only the intentional, browser-safe contract fields."""
        self.validate()
        payload = asdict(self)
        payload["evidence"] = [asdict(item) for item in self.evidence]
        return payload

