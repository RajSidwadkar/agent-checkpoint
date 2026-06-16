from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ConfidenceRange:
    """Range of confidence scores the agent operates within."""

    min: float = 0.0
    max: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.min <= 1.0):
            raise ValueError(f"min must be between 0.0 and 1.0; got {self.min}")
        if not (0.0 <= self.max <= 1.0):
            raise ValueError(f"max must be between 0.0 and 1.0; got {self.max}")
        if self.min > self.max:
            raise ValueError(f"min ({self.min}) cannot be greater than max ({self.max})")


@dataclass
class AgentManifest:
    """Manifest describing an agent's capabilities and constraints."""

    ac_version: str
    agent_id: str
    capabilities: List[str]
    refuses: List[str] = field(default_factory=list)
    confidence_range: Optional[ConfidenceRange] = None
    max_context_tokens: Optional[int] = None
    contact: Optional[str] = None


def parse_manifest(data: Union[str, Dict[str, Any]]) -> Optional[AgentManifest]:
    """
    Parses a JSON string or dictionary into an AgentManifest object.
    Returns None on any error or if required fields are missing.
    """
    try:
        if isinstance(data, str):
            raw_dict = json.loads(data)
        else:
            raw_dict = data

        if not isinstance(raw_dict, dict):
            return None

        # Check required fields
        if "ac_version" not in raw_dict or "agent_id" not in raw_dict or "capabilities" not in raw_dict:
            return None

        conf_range = None
        raw_conf = raw_dict.get("confidence_range")
        if isinstance(raw_conf, dict):
            try:
                conf_range = ConfidenceRange(
                    min=float(raw_conf.get("min", 0.0)), max=float(raw_conf.get("max", 1.0))
                )
            except (ValueError, TypeError):
                # If confidence range is invalid, we continue without it
                pass

        return AgentManifest(
            ac_version=str(raw_dict["ac_version"]),
            agent_id=str(raw_dict["agent_id"]),
            capabilities=list(raw_dict["capabilities"]),
            refuses=list(raw_dict.get("refuses", [])),
            confidence_range=conf_range,
            max_context_tokens=raw_dict.get("max_context_tokens"),
            contact=raw_dict.get("contact"),
        )
    except Exception:
        # Never raise, return None on any failure
        return None


def emit_manifest(manifest: AgentManifest) -> str:
    """
    Converts an AgentManifest to a JSON string.
    Omits fields with None values.
    """
    raw = asdict(manifest)

    def _remove_none(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _remove_none(v) for k, v in obj.items() if v is not None}
        return obj

    clean = _remove_none(raw)
    return json.dumps(clean, indent=2)
