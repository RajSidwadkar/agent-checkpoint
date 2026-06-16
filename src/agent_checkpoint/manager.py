from typing import Any, Dict, Optional

from .models import Checkpoint
from .storage import Storage


class CheckpointManager:
    """Coordinates checkpoint creation and retrieval."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def create_checkpoint(
        self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """Creates and saves a new checkpoint."""
        checkpoint = Checkpoint(data=data, metadata=metadata or {})
        self.storage.save(checkpoint)
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Retrieves a checkpoint by ID."""
        return self.storage.load(checkpoint_id)
