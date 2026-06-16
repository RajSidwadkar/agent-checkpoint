from datetime import datetime

from agent_checkpoint.factory import new_checkpoint, resume_from
from agent_checkpoint.models import Checkpoint, CheckpointStatus


def test_new_checkpoint_ac_version():
    cp = new_checkpoint("task-1", "agent-1", "summary")
    assert cp.ac_version == "0.1.0"


def test_new_checkpoint_id_is_uuid():
    cp = new_checkpoint("task-1", "agent-1", "summary")
    # Basic UUID v4 format check (8-4-4-4-12)
    parts = cp.checkpoint_id.split("-")
    assert len(parts) == 5
    assert len(parts[0]) == 8
    assert len(parts[1]) == 4
    assert len(parts[2]) == 4
    assert len(parts[3]) == 4
    assert len(parts[4]) == 12
    # UUID v4 marker
    assert parts[2][0] == "4"


def test_new_checkpoint_emitted_at_iso8601():
    cp = new_checkpoint("task-1", "agent-1", "summary")
    # Should not raise ValueError
    datetime.fromisoformat(cp.emitted_at.replace("Z", "+00:00"))


def test_resume_from_parent_id():
    previous = new_checkpoint("task-1", "agent-1", "summary")
    resumed = resume_from(previous, "agent-2")
    assert resumed.parent_checkpoint_id == previous.checkpoint_id


def test_resume_from_preserves_task_id():
    previous = new_checkpoint("task-1", "agent-1", "summary")
    resumed = resume_from(previous, "agent-2")
    assert resumed.task_id == previous.task_id


def test_resume_from_copies_completed_steps():
    # Actually, let's use the constructor to make a previous with steps
    previous_with_steps = Checkpoint(
        ac_version="0.1.0",
        checkpoint_id="uuid-1",
        task_id="task-1",
        agent_id="agent-1",
        emitted_at="2026-06-16T14:30:00Z",
        status=CheckpointStatus.PARTIAL,
        task_summary="summary",
        completed_steps=["step1", "step2"],
    )
    resumed = resume_from(previous_with_steps, "agent-2")
    assert resumed.completed_steps == ["step1", "step2"]
    # Ensure it's a copy
    assert resumed.completed_steps is not previous_with_steps.completed_steps


def test_resume_from_generates_new_id():
    previous = new_checkpoint("task-1", "agent-1", "summary")
    resumed = resume_from(previous, "agent-2")
    assert resumed.checkpoint_id != previous.checkpoint_id
    assert len(resumed.checkpoint_id) == 36
