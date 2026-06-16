# Agent Checkpoint

Never lose work when an agent fails.

## Features

- **Industrialized OOP Structure**: Clean separation of concerns between models, storage, and management.
- **Flexible Storage**: Abstract base class allows for multiple storage backends (In-Memory, File-system, Database).
- **Type Safe**: Fully type-hinted and compatible with `mypy`.
- **CI Ready**: Pre-configured with GitHub Actions, `ruff`, and `pytest`.

## Architecture

- `Checkpoint`: Immutable data model for agent states.
- `Storage`: Interface for persisting and retrieving checkpoints.
- `CheckpointManager`: Central API for creating and managing checkpoints.

## Development

```bash
pip install -e .[dev]
ruff check .
mypy src
pytest
```
