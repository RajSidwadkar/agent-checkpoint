from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from .models import CheckpointStatus, RetryStrategy


@dataclass
class ValidationError:
    """Represents a single validation failure."""

    field: str
    message: str


# UUID v4 pattern (simplified but strict enough for spec compliance)
UUID_V4_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.IGNORECASE
)
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def validate(data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validates a dictionary against the agent-checkpoint specification.
    Returns a list of ValidationError objects; an empty list indicates success.
    """
    errors: List[ValidationError] = []

    # 1. Required fields presence and basic type check
    required_fields = [
        "ac_version",
        "checkpoint_id",
        "task_id",
        "agent_id",
        "emitted_at",
        "status",
        "task_summary",
    ]

    for field in required_fields:
        if field not in data:
            errors.append(ValidationError(field, "Field is missing"))
        elif not isinstance(data[field], str) or not data[field].strip():
            errors.append(ValidationError(field, "Field must be a non-empty string"))

    # If basic requirements are missing, we still continue to check patterns for existing fields

    # 2. Pattern and Logic Validations
    if "ac_version" in data and isinstance(data["ac_version"], str):
        if not SEMVER_PATTERN.match(data["ac_version"]):
            errors.append(
                ValidationError("ac_version", "Must match semver pattern \\d+\\.\\d+\\.\\d+")
            )

    # UUID checks
    for uuid_field in ["checkpoint_id", "task_id", "parent_checkpoint_id"]:
        if uuid_field in data and data[uuid_field] is not None:
            if not isinstance(data[uuid_field], str):
                errors.append(ValidationError(uuid_field, "Must be a string"))
            elif not UUID_V4_PATTERN.match(data[uuid_field]):
                errors.append(ValidationError(uuid_field, "Must be a valid UUID v4"))

    # Timestamp check
    if "emitted_at" in data and isinstance(data["emitted_at"], str):
        try:
            # Handle the 'Z' suffix which fromisoformat might not like in older 3.11 patches
            ts = data["emitted_at"].replace("Z", "+00:00")
            datetime.fromisoformat(ts)
        except ValueError:
            errors.append(ValidationError("emitted_at", "Must be a valid ISO 8601 timestamp"))

    # Enum checks
    if "status" in data and isinstance(data["status"], str):
        if data["status"] not in [s.value for s in CheckpointStatus]:
            errors.append(
                ValidationError(
                    "status", f"Must be one of: {', '.join(s.value for s in CheckpointStatus)}"
                )
            )

    if "retry_strategy" in data and data["retry_strategy"] is not None:
        if data["retry_strategy"] not in [r.value for r in RetryStrategy]:
            errors.append(
                ValidationError(
                    "retry_strategy", f"Must be one of: {', '.join(r.value for r in RetryStrategy)}"
                )
            )

    # Confidence check
    if "confidence" in data and data["confidence"] is not None:
        if not isinstance(data["confidence"], (int, float)):
            errors.append(ValidationError("confidence", "Must be a number"))
        elif not (0.0 <= float(data["confidence"]) <= 1.0):
            errors.append(ValidationError("confidence", "Must be between 0.0 and 1.0"))

    # Executor hint check
    if "executor_hint" in data and data["executor_hint"] is not None:
        val = data["executor_hint"]
        if not isinstance(val, str):
            errors.append(ValidationError("executor_hint", "Must be a string"))
        elif not (val in ("same", "any") or val.startswith("capability:")):
            errors.append(
                ValidationError(
                    "executor_hint", "Must be 'same', 'any', or start with 'capability:'"
                )
            )

    return errors
