# Agent Capability Manifest Specification (v0.1.0)

## 1. Purpose
An agent server MAY expose a static JSON file at `/.well-known/agent-caps.json`
describing what it handles. No agent is required to expose this, and no agent is
required to read it before sending a checkpoint. It is a hint, not a contract.

## 2. The Manifest Object
A JSON object with the following fields:

### Required
- `ac_version`: string (semver, "0.1.0")
- `agent_id`: string (identifies the agent)
- `capabilities`: array of strings (list of supported tasks/features)

### Optional
- `refuses`: array of strings (tasks the agent explicitly will not perform)
- `confidence_range`: object with `min` and `max` floats (0.0 to 1.0)
- `max_context_tokens`: integer (maximum supported context window)
- `contact`: string (URL or email for the agent operator)

## 3. How executor_hint relates
A checkpoint with `executor_hint` "capability:code-review" suggests the next 
executor should handle code review. An agent listing "code-review" in its 
manifest is a candidate. No routing infrastructure enforces this; it is a 
convention for developers or custom routers to follow.

## 4. Example
`agent-caps.json`:
```json
{
  "ac_version": "0.1.0",
  "agent_id": "reviewer-gpt-4",
  "capabilities": ["code-review", "unit-testing", "linting"],
  "refuses": ["production-deployment"],
  "confidence_range": {
    "min": 0.6,
    "max": 1.0
  },
  "max_context_tokens": 128000,
  "contact": "https://agent-operator.com/support"
}
```

## 5. What this is NOT
- **Not a registry**: There is no central server or authority.
- **Not required**: Agents can send/receive checkpoints without a manifest.
- **Not an A2A Agent Card**: No handshake, no protocol, no persistent session.
