from typing import Any, Dict, List, Optional

from .models import Checkpoint, CheckpointStatus, RetryStrategy
from .storage import Storage


class CheckpointManager:
    """Coordinates checkpoint creation and retrieval based on SPEC.md."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def create_checkpoint(
        self,
        task_id: str,
        agent_id: str,
        task_summary: str,
        status: CheckpointStatus = CheckpointStatus.PARTIAL,
        completed_steps: Optional[List[str]] = None,
        remaining_steps: Optional[List[str]] = None,
        partial_output: Optional[Dict[str, Any]] = None,
        failure_reason: Optional[str] = None,
        confidence: Optional[float] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        executor_hint: Optional[str] = None,
        context_snapshot: Optional[Dict[str, Any]] = None,
        parent_checkpoint_id: Optional[str] = None,
    ) -> Checkpoint:
        """Creates and saves a new checkpoint following the spec."""
        checkpoint = Checkpoint(
            task_id=task_id,
            agent_id=agent_id,
            task_summary=task_summary,
            status=status,
            completed_steps=completed_steps or [],
            remaining_steps=remaining_steps or [],
            partial_output=partial_output or {},
            failure_reason=failure_reason,
            confidence=confidence,
            retry_strategy=retry_strategy,
            executor_hint=executor_hint,
            context_snapshot=context_snapshot or {},
            parent_checkpoint_id=parent_checkpoint_id,
        )
        self.storage.save(checkpoint)
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Retrieves a checkpoint by ID."""
        return self.storage.load(checkpoint_id)
