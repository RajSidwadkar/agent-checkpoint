from agent_checkpoint import CheckpointManager, InMemoryStorage


def test_checkpoint_lifecycle():
    storage = InMemoryStorage()
    manager = CheckpointManager(storage)

    data = {"step": 1, "status": "running"}
    checkpoint = manager.create_checkpoint(data)

    assert checkpoint.id is not None
    assert checkpoint.data == data

    retrieved = manager.get_checkpoint(checkpoint.id)
    assert retrieved == checkpoint

    all_checkpoints = storage.list_all()
    assert len(all_checkpoints) == 1
    assert all_checkpoints[0] == checkpoint
