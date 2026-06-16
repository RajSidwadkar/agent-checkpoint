import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional


class CheckpointStatus(StrEnum):
    PARTIAL = "partial"
    FAILED = "failed"
    PAUSED = "paused"
    COMPLETED = "completed"


class RetryStrategy(StrEnum):
    RESUME = "resume"
    RESTART = "restart"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class Checkpoint:
    """Represents a single point in time for an agent's state, following SPEC.md."""

    # Required fields
    task_id: str
    agent_id: str
    task_summary: str
    status: CheckpointStatus
    ac_version: str = "0.1.0"
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    emitted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    # Optional fields
    completed_steps: List[str] = field(default_factory=list)
    remaining_steps: List[str] = field(default_factory=list)
    partial_output: Dict[str, Any] = field(default_factory=dict)
    failure_reason: Optional[str] = None
    confidence: Optional[float] = None
    retry_strategy: Optional[RetryStrategy] = None
    executor_hint: Optional[str] = None
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    parent_checkpoint_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dictionary for JSON serialization."""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        # Ensure enums are serialized as strings
        if isinstance(data["status"], CheckpointStatus):
            data["status"] = data["status"].value
        if "retry_strategy" in data and isinstance(data["retry_strategy"], RetryStrategy):
            data["retry_strategy"] = data["retry_strategy"].value
        return data
