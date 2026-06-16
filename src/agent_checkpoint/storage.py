from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .models import Checkpoint


class Storage(ABC):
    """Abstract base class for checkpoint storage."""

    @abstractmethod
    def save(self, checkpoint: Checkpoint) -> None:
        """Persist a checkpoint."""
        pass

    @abstractmethod
    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Retrieve a checkpoint by ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[Checkpoint]:
        """List all stored checkpoints."""
        pass


class InMemoryStorage(Storage):
    """Simple in-memory implementation of checkpoint storage."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, Checkpoint] = {}

    def save(self, checkpoint: Checkpoint) -> None:
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint

    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        return self._checkpoints.get(checkpoint_id)

    def list_all(self) -> List[Checkpoint]:
        return list(self._checkpoints.values())
