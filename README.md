# agent-checkpoint

A tiny, language-agnostic JSON format for agentic state recovery.

## The problem
When an agent fails mid-task, its execution context is typically lost. No standard exists for representing what was completed, what remains, and what the next executor needs to resume.

## What this is
`agent-checkpoint` is a minimal JSON schema and supporting library. An agent that fails (or pauses) emits a checkpoint containing its progress and required context. Any future executor—the same agent, a different model, or a human—can read this checkpoint as plain JSON. It requires no SDK on the receiving side, no handshake, and no specific communication protocol.

## Install
```bash
pip install agent-checkpoint
npm install agent-checkpoint
```

## Quickstart (Python)
```python
from agent_checkpoint import new_checkpoint, emit_json, parse

def failing_agent():
    # Progress: 1 step done, 1 remains
    cp = new_checkpoint("task-42", "gpt-4", "Data analysis")
    cp.completed_steps.append("Load CSV")
    print(emit_json(cp)) # Emit and fail

def resuming_agent(json_str):
    res = parse(json_str)
    if res.ok:
        print(f"Resuming task {res.checkpoint.task_id}")
        print(f"Already done: {res.checkpoint.completed_steps}")
```

## Quickstart (TypeScript)
```typescript
import { newCheckpoint, emitJson, parse } from 'agent-checkpoint';

function failingAgent() {
  const cp = newCheckpoint("task-42", "gpt-4", "Data analysis");
  cp.completed_steps?.push("Load CSV");
  console.log(emitJson(cp)); // Emit and fail
}

function resumingAgent(jsonStr: string) {
  const res = parse(jsonStr);
  if (res.ok && res.checkpoint) {
    console.log(`Resuming task ${res.checkpoint.task_id}`);
    console.log(`Already done: ${res.checkpoint.completed_steps}`);
  }
}
```

## The spec
See [docs/SPEC.md](docs/SPEC.md) for the JSON schema and field definitions.

## What this is NOT
- **Not a protocol**: No message sequencing or handshakes.
- **Not a channel**: You decide how to move the JSON (stdout, HTTP, files).
- **Not A2A or MCP**: It describes *state*, not *interaction*.
- The receiver needs zero implementation to read the data.

## Optional extensions
- **Trust tiers**: Metadata for context source verification. See [docs/SPEC.md §7](docs/SPEC.md#7-trust-tiers-optional).
- **Capability manifest**: Optional discovery for agent servers. See [docs/CAPABILITY_MANIFEST.md](docs/CAPABILITY_MANIFEST.md).

## License
MIT
