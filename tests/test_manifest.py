import json

import pytest

from agent_checkpoint import AgentManifest, emit_manifest, parse_manifest
from agent_checkpoint.manifest import ConfidenceRange


@pytest.fixture
def valid_manifest_dict():
    return {
        "ac_version": "0.1.0",
        "agent_id": "reviewer-gpt-4",
        "capabilities": ["code-review", "unit-testing"],
        "confidence_range": {"min": 0.6, "max": 0.9},
        "contact": "support@example.com",
    }


def test_parse_manifest_valid_dict(valid_manifest_dict):
    manifest = parse_manifest(valid_manifest_dict)
    assert isinstance(manifest, AgentManifest)
    assert manifest.agent_id == "reviewer-gpt-4"
    assert manifest.capabilities == ["code-review", "unit-testing"]
    assert manifest.confidence_range.min == 0.6


def test_parse_manifest_valid_json_string(valid_manifest_dict):
    json_str = json.dumps(valid_manifest_dict)
    manifest = parse_manifest(json_str)
    assert isinstance(manifest, AgentManifest)
    assert manifest.agent_id == "reviewer-gpt-4"


def test_parse_manifest_missing_agent_id(valid_manifest_dict):
    data = valid_manifest_dict.copy()
    del data["agent_id"]
    # Should return None, never raise
    manifest = parse_manifest(data)
    assert manifest is None


def test_parse_manifest_invalid_json():
    manifest = parse_manifest("{invalid json")
    assert manifest is None


def test_emit_manifest_produces_valid_json(valid_manifest_dict):
    manifest = parse_manifest(valid_manifest_dict)
    json_str = emit_manifest(manifest)
    data = json.loads(json_str)
    assert data["agent_id"] == "reviewer-gpt-4"


def test_emit_manifest_omits_none_fields(valid_manifest_dict):
    data = valid_manifest_dict.copy()
    if "contact" in data:
        del data["contact"]
    manifest = parse_manifest(data)
    json_str = emit_manifest(manifest)
    assert "contact" not in json_str


def test_manifest_round_trip(valid_manifest_dict):
    manifest = parse_manifest(valid_manifest_dict)
    json_str = emit_manifest(manifest)
    round_tripped = parse_manifest(json_str)
    assert manifest == round_tripped


def test_confidence_range_validation():
    # Valid
    ConfidenceRange(min=0.1, max=0.5)
    # Invalid: min > max
    with pytest.raises(ValueError, match="cannot be greater than max"):
        ConfidenceRange(min=0.8, max=0.2)
    # Invalid: out of bounds
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        ConfidenceRange(min=-0.1, max=0.5)


def test_agent_agnostic_usage():
    """
    Demonstrates that an agent doesn't need to know about manifests
    to receive and use checkpoints.
    """
    # A checkpoint with a capability hint
    checkpoint_data = {
        "ac_version": "0.1.0",
        "checkpoint_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
        "task_id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "agent_id": "source-agent",
        "emitted_at": "2026-06-16T14:30:00Z",
        "status": "partial",
        "task_summary": "Review code",
        "executor_hint": "capability:code-review",
    }

    # An agent receives this. It doesn't call parse_manifest.
    # It just looks at the hint.
    hint = checkpoint_data.get("executor_hint")
    assert hint == "capability:code-review"

    # It can decide to handle it based on its own internal logic
    # without ever seeing an agent-caps.json manifest.
    if hint.startswith("capability:"):
        capability = hint.split(":")[1]
        assert capability == "code-review"
        # Proceed to handle...
