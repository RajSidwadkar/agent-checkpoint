from agent_checkpoint import CheckpointManager, InMemoryStorage, emit
from agent_checkpoint.models import CheckpointStatus, RetryStrategy


def test_checkpoint_lifecycle():
    storage = InMemoryStorage()
    manager = CheckpointManager(storage)

    task_id = "f9e8d7c6-b5a4-4d3c-2b1a-0f9e8d7c6b5a"
    agent_id = "coder-gpt-4"
    summary = "Implement auth"

    checkpoint = manager.create_checkpoint(
        task_id=task_id,
        agent_id=agent_id,
        task_summary=summary,
        status=CheckpointStatus.PARTIAL,
        partial_output={"file.py": "print('hello')"},
        retry_strategy=RetryStrategy.RESUME,
    )

    assert checkpoint.checkpoint_id is not None
    assert checkpoint.task_id == task_id
    assert checkpoint.agent_id == agent_id
    assert checkpoint.status == CheckpointStatus.PARTIAL
    assert checkpoint.partial_output == {"file.py": "print('hello')"}

    retrieved = manager.get_checkpoint(checkpoint.checkpoint_id)
    assert retrieved == checkpoint

    # Test dictionary conversion for JSON compatibility
    d = emit(checkpoint)
    assert d["ac_version"] == "0.1.0"
    assert d["status"] == "partial"
    assert d["retry_strategy"] == "resume"
