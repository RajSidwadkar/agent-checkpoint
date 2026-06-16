# Run with: python examples/demo.py
# No dependencies beyond agent-checkpoint

from dataclasses import replace

from agent_checkpoint import (
    CheckpointStatus,
    RetryStrategy,
    emit_json,
    new_checkpoint,
    parse,
    resume_from,
)


def first_agent_run():
    print("--- Agent 1: Starting Task ---")
    task_id = "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
    agent_id = "agent-alpha"
    summary = "Write a 3-module Python package"

    # Create initial checkpoint
    cp = new_checkpoint(task_id, agent_id, summary)

    # Simulate work
    print("Agent 1: Completing module_1...")
    # Checkpoint is frozen, so we use replace() to update state
    cp = replace(
        cp,
        completed_steps=["module_1"],
        remaining_steps=["module_2", "module_3"],
    )

    print("Agent 1: Starting module_2... [CONTEXT LIMIT HIT]")

    # Finalize state before "failure"
    final_cp = replace(
        cp,
        status=CheckpointStatus.PARTIAL,
        confidence=0.9,
        retry_strategy=RetryStrategy.RESUME,
        executor_hint="same",
        context_snapshot={"last_function": "setup_logging"},
    )

    checkpoint_json = emit_json(final_cp)
    print("\n--- EMITTED CHECKPOINT ---")
    print(checkpoint_json)
    print("--------------------------\n")

    return checkpoint_json


def second_agent_run(checkpoint_json):
    print("--- Agent 2: Resuming Task ---")

    # Parse the received checkpoint
    result = parse(checkpoint_json)
    if not result.ok:
        print(f"Failed to parse: {result.errors}")
        return

    cp = result.checkpoint
    print(f"Resuming task. Completed: {cp.completed_steps}. Remaining: {cp.remaining_steps}.")

    # Link a new checkpoint to the previous one
    # resume_from handles the id linking and step copying automatically
    next_cp = resume_from(cp, agent_id="agent-beta")

    print("\n--- NEW RESUMED CHECKPOINT (Linked to previous) ---")
    print(emit_json(next_cp))
    print("--------------------------------------------------\n")

    print("Agent 2: Continuing with module_2...")


if __name__ == "__main__":
    # Internal path setup is not needed if PYTHONPATH is set correctly,
    # but we'll leave it simple for the user.
    json_data = first_agent_run()
    second_agent_run(json_data)
