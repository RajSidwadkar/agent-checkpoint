import json

import pytest

from agent_checkpoint.codec import emit, emit_json, parse
from agent_checkpoint.models import Checkpoint, CheckpointStatus


@pytest.fixture
def VALID_DICT():
    return {
        "ac_version": "0.1.0",
        "checkpoint_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
        "task_id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "agent_id": "coder-gpt-4",
        "emitted_at": "2026-06-16T14:30:00Z",
        "status": "partial",
        "task_summary": "Implement auth module",
        "confidence": 0.75,
        "executor_hint": "same",
        "retry_strategy": "resume",
        "completed_steps": ["step1"],
    }


def test_parse_valid_dict(VALID_DICT):
    result = parse(VALID_DICT)
    assert result.ok is True
    assert isinstance(result.checkpoint, Checkpoint)
    assert result.checkpoint.status == CheckpointStatus.PARTIAL
    assert result.checkpoint.confidence == 0.75


def test_parse_valid_json_string(VALID_DICT):
    json_str = json.dumps(VALID_DICT)
    result = parse(json_str)
    assert result.ok is True
    assert result.checkpoint.checkpoint_id == VALID_DICT["checkpoint_id"]


def test_parse_empty_dict():
    result = parse({})
    assert result.ok is False
    # Errors should list missing required fields
    required_fields = [
        "ac_version",
        "checkpoint_id",
        "task_id",
        "agent_id",
        "emitted_at",
        "status",
        "task_summary",
    ]
    error_fields = [e.field for e in result.errors]
    for field in required_fields:
        assert field in error_fields


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("confidence", 1.5),
        ("checkpoint_id", "not-a-uuid"),
    ],
)
def test_parse_invalid_values(VALID_DICT, field, invalid_value):
    invalid_dict = VALID_DICT.copy()
    invalid_dict[field] = invalid_value
    result = parse(invalid_dict)
    assert result.ok is False
    assert any(e.field == field for e in result.errors)


def test_parse_unknown_extra_field(VALID_DICT):
    extra_dict = VALID_DICT.copy()
    extra_dict["extra_field"] = "some value"
    result = parse(extra_dict)
    assert result.ok is True


def test_emit_no_none_values(VALID_DICT):
    checkpoint = parse(VALID_DICT).checkpoint
    # Manually ensure some fields are None if they weren't already
    # but the valid_dict has some Nones by omission anyway.
    emitted = emit(checkpoint)
    for value in emitted.values():
        assert value is not None
    assert "failure_reason" not in emitted


def test_emit_json_valid_json(VALID_DICT):
    checkpoint = parse(VALID_DICT).checkpoint
    json_str = emit_json(checkpoint)
    # Should be a valid JSON string
    data = json.loads(json_str)
    assert data["checkpoint_id"] == VALID_DICT["checkpoint_id"]


def test_round_trip(VALID_DICT):
    # parse(emit_json(parse(VALID_DICT).checkpoint)) returns ok=True
    first_parse = parse(VALID_DICT)
    assert first_parse.ok is True

    json_output = emit_json(first_parse.checkpoint)
    second_parse = parse(json_output)

    assert second_parse.ok is True
    assert second_parse.checkpoint == first_parse.checkpoint
