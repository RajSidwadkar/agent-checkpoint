from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .models import Checkpoint, CheckpointStatus, RetryStrategy, TrustedValue, TrustTier
from .validator import ValidationError, validate


@dataclass
class ParseResult:
    """The result of a parse operation."""

    ok: bool
    checkpoint: Optional[Checkpoint]
    errors: List[ValidationError]


def parse(data: Union[str, Dict[str, Any]]) -> ParseResult:
    """
    Parses a JSON string or dictionary into a Checkpoint object.
    Performs validation and returns a ParseResult.
    """
    if isinstance(data, str):
        try:
            raw_dict = json.loads(data)
        except json.JSONDecodeError as e:
            return ParseResult(
                ok=False,
                checkpoint=None,
                errors=[ValidationError("json", f"Invalid JSON: {str(e)}")],
            )
    else:
        raw_dict = data

    # 1. Validate the dictionary
    errors = validate(raw_dict)
    if errors:
        return ParseResult(ok=False, checkpoint=None, errors=errors)

    # 2. Build Checkpoint from dict
    try:
        # Convert enum strings to actual enum members for the constructor
        status = CheckpointStatus(raw_dict["status"])

        retry_strategy = None
        if raw_dict.get("retry_strategy"):
            retry_strategy = RetryStrategy(raw_dict["retry_strategy"])

        # Handle context_snapshot deserialization for Trust Tiers
        context_snapshot = raw_dict.get("context_snapshot")
        if isinstance(context_snapshot, dict):
            deserialized_snapshot: Dict[str, Union[TrustedValue, object]] = {}
            for k, v in context_snapshot.items():
                if isinstance(v, dict) and "value" in v and "trust" in v:
                    try:
                        deserialized_snapshot[k] = TrustedValue(
                            value=v["value"], trust=TrustTier(v["trust"])
                        )
                    except ValueError:
                        # Fallback to plain object if trust tier is unrecognized
                        deserialized_snapshot[k] = v
                else:
                    deserialized_snapshot[k] = v
            context_snapshot = deserialized_snapshot

        checkpoint = Checkpoint(
            # Required fields
            ac_version=raw_dict["ac_version"],
            checkpoint_id=raw_dict["checkpoint_id"],
            task_id=raw_dict["task_id"],
            agent_id=raw_dict["agent_id"],
            emitted_at=raw_dict["emitted_at"],
            status=status,
            task_summary=raw_dict["task_summary"],
            # Optional fields
            completed_steps=raw_dict.get("completed_steps", []),
            remaining_steps=raw_dict.get("remaining_steps", []),
            partial_output=raw_dict.get("partial_output"),
            failure_reason=raw_dict.get("failure_reason"),
            confidence=raw_dict.get("confidence"),
            retry_strategy=retry_strategy,
            executor_hint=raw_dict.get("executor_hint"),
            context_snapshot=context_snapshot,
            parent_checkpoint_id=raw_dict.get("parent_checkpoint_id"),
        )
        return ParseResult(ok=True, checkpoint=checkpoint, errors=[])
    except (KeyError, ValueError, TypeError) as e:
        # This catch-all handles unexpected type mismatches not caught by validate()
        return ParseResult(
            ok=False,
            checkpoint=None,
            errors=[ValidationError("internal", f"Failed to instantiate Checkpoint: {str(e)}")],
        )


def emit(checkpoint: Checkpoint) -> Dict[str, Any]:
    """
    Converts a Checkpoint to a dictionary for serialization.
    Omits fields with None values entirely.
    """
    # Use __dict__ to avoid complex serialization of nested objects if any,
    # but since Checkpoint is simple dataclass, this works well.
    raw = checkpoint.__dict__.copy()

    # Clean up enums and omit None values
    clean: Dict[str, Any] = {}
    for k, v in raw.items():
        if v is None:
            continue

        # Handle enums
        if isinstance(v, (CheckpointStatus, RetryStrategy)):
            clean[k] = v.value
        elif k == "context_snapshot" and isinstance(v, dict):
            # Special handling for context_snapshot to serialize TrustedValue
            serialized_snapshot = {}
            for sk, sv in v.items():
                if isinstance(sv, TrustedValue):
                    serialized_snapshot[sk] = {"value": sv.value, "trust": sv.trust.value}
                else:
                    serialized_snapshot[sk] = sv
            clean[k] = serialized_snapshot
        else:
            clean[k] = v

    return clean


def emit_json(checkpoint: Checkpoint, indent: int = 2) -> str:
    """
    Converts a Checkpoint to a JSON string.
    """
    return json.dumps(emit(checkpoint), indent=indent, default=str)
