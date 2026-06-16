from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .models import Checkpoint, CheckpointStatus


def new_checkpoint(
    task_id: str,
    agent_id: str,
    task_summary: str,
    status: CheckpointStatus = CheckpointStatus.PARTIAL,
) -> Checkpoint:
    """
    Creates a new Checkpoint for a fresh task.
    """
    return Checkpoint(
        ac_version="0.1.0",
        checkpoint_id=str(uuid.uuid4()),
        task_id=task_id,
        agent_id=agent_id,
        emitted_at=datetime.now(timezone.utc).isoformat(),
        status=status,
        task_summary=task_summary,
    )


def resume_from(previous: Checkpoint, agent_id: str) -> Checkpoint:
    """
    Creates a new Checkpoint linked to a previous one, preserving task context.
    """
    return Checkpoint(
        ac_version="0.1.0",
        checkpoint_id=str(uuid.uuid4()),
        task_id=previous.task_id,
        agent_id=agent_id,
        emitted_at=datetime.now(timezone.utc).isoformat(),
        status=CheckpointStatus.PARTIAL,
        task_summary=previous.task_summary,
        completed_steps=list(previous.completed_steps),  # copy the list
        parent_checkpoint_id=previous.checkpoint_id,
    )
