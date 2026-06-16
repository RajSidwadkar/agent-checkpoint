from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union


class CheckpointStatus(StrEnum):
    """Status of the checkpoint as defined in SPEC.md."""

    PARTIAL = "partial"
    FAILED = "failed"
    PAUSED = "paused"
    COMPLETED = "completed"


class RetryStrategy(StrEnum):
    """Strategy for continuation as defined in SPEC.md."""

    RESUME = "resume"
    RESTART = "restart"
    ESCALATE = "escalate"


class TrustTier(StrEnum):
    """Trust levels for context values as defined in SPEC.md."""

    SYSTEM = "system"
    AGENT = "agent"
    USER = "user"
    VERIFIED = "verified"


@dataclass(frozen=True)
class TrustedValue:
    """A value annotated with a trust tier."""

    value: Any
    trust: TrustTier


@dataclass(frozen=True)
class Checkpoint:
    """
    Represents a single point in time for an agent's state, following SPEC.md.

    Validation:
    - confidence: None or between 0.0 and 1.0 (inclusive)
    - executor_hint: None, 'same', 'any', or starts with 'capability:'
    """

    # Required fields (no defaults)
    ac_version: str
    checkpoint_id: str
    task_id: str
    agent_id: str
    emitted_at: str
    status: CheckpointStatus
    task_summary: str

    # Optional fields
    completed_steps: List[str] = field(default_factory=list)
    remaining_steps: List[str] = field(default_factory=list)
    partial_output: Optional[Dict[str, object]] = None
    failure_reason: Optional[str] = None
    confidence: Optional[float] = None
    retry_strategy: Optional[RetryStrategy] = None
    executor_hint: Optional[str] = None
    context_snapshot: Optional[Dict[str, Union[TrustedValue, object]]] = None
    parent_checkpoint_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate input constraints."""
        if self.confidence is not None:
            if not (0.0 <= self.confidence <= 1.0):
                raise ValueError(f"Confidence must be between 0.0 and 1.0; got {self.confidence}")

        if self.executor_hint is not None:
            if not (
                self.executor_hint in ("same", "any")
                or self.executor_hint.startswith("capability:")
            ):
                raise ValueError(
                    f"executor_hint must be 'same', 'any', or start with 'capability:'; "
                    f"got {self.executor_hint}"
                )


__all__ = ["CheckpointStatus", "RetryStrategy", "Checkpoint", "TrustTier", "TrustedValue"]
