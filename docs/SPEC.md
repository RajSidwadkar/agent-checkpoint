# Agent-Checkpoint Format Specification (v0.1.0)

## 1. Purpose
An agent that fails mid-task emits a checkpoint. Any future executor—same agent retrying, different agent, or human—reads the checkpoint and resumes without losing work. The receiver needs no SDK, library, or knowledge of this format; it reads plain JSON. That is the entire contract.

## 2. The Checkpoint Object
A JSON object with the following fields:

### Required
- `ac_version`: string (semver, "0.1.0")
- `checkpoint_id`: string (UUID v4)
- `task_id`: string (UUID v4, stable across retries)
- `agent_id`: string (identifies emitting agent)
- `emitted_at`: string (ISO 8601)
- `status`: enum ("partial" | "failed" | "paused" | "completed")
- `task_summary`: string (one-line task description)

### Optional
- `completed_steps`: array of strings
- `remaining_steps`: array of strings
- `partial_output`: object (arbitrary agent output)
- `failure_reason`: string (free text)
- `confidence`: number (0.0 to 1.0)
- `retry_strategy`: enum ("resume" | "restart" | "escalate")
- `executor_hint`: enum ("same" | "any" | "capability:X")
- `context_snapshot`: object (key facts for continuation)
- `parent_checkpoint_id`: string (UUID v4)

## 3. executor_hint values
- `same`: Retry with the same agent.
- `any`: Any available agent can continue.
- `capability:X`: Needs an agent advertising capability X.
*Note: Hints are non-binding recommendations, not routing requirements.*

## 4. What this is NOT
- **Not a protocol**: No handshake required.
- **Not a channel**: Emit anywhere (stdout, file, HTTP, queue).
- **Not mandatory**: Receivers may ignore any or all fields.

## 5. Example
```json
{
  "ac_version": "0.1.0",
  "checkpoint_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "task_id": "f9e8d7c6-b5a4-4d3c-2b1a-0f9e8d7c6b5a",
  "agent_id": "coder-gpt-4",
  "emitted_at": "2026-06-16T14:30:00Z",
  "status": "partial",
  "task_summary": "Implement authentication module in Python",
  "completed_steps": ["Define user model", "Setup JWT utility"],
  "remaining_steps": ["Write login endpoint", "Add password reset flow"],
  "partial_output": {
    "src/auth.py": "import jwt\nclass User:\n    pass\n"
  },
  "failure_reason": "Context window limit reached mid-file",
  "retry_strategy": "resume",
  "executor_hint": "same",
  "context_snapshot": {
    "framework": "FastAPI",
    "db": "PostgreSQL"
  }
}
```

## 6. Versioning
`ac_version` follows semver. Receivers must be liberal and ignore unknown fields. Senders must not remove required fields across minor/patch versions.

## 7. Trust Tiers (optional)
`context_snapshot` values may optionally include trust levels. Instead of raw strings/objects, a field can use an object with `value` and `trust`.

```json
"context_snapshot": {
  "user_request": { "value": "summarise this doc", "trust": "user" }
}
```

### Trust Tier Values
- `system`: Set by agent runtime, not influenced by user input.
- `agent`: Produced by a prior agent; not yet human-verified.
- `user`: Raw user input; treat as untrusted.
- `verified`: Checked by a human or a verification agent.

### Rules
- **Optional**: Receivers that do not understand tiers ignore `trust` and read `value` directly.
- **Self-reported**: Tiers are advisory labels with no cryptographic proof.
- **Scope**: Signing and verification protocols are out of scope for v0.1.
