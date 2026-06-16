import { Checkpoint, CheckpointStatus } from "./types.js";
import { randomUUID } from "node:crypto";

export function newCheckpoint(
  taskId: string,
  agentId: string,
  taskSummary: string,
  status: CheckpointStatus = "partial"
): Checkpoint {
  return {
    ac_version: "0.1.0",
    checkpoint_id: randomUUID(),
    task_id: taskId,
    agent_id: agentId,
    emitted_at: new Date().toISOString(),
    status,
    task_summary: taskSummary,
    completed_steps: [],
    remaining_steps: [],
  };
}

export function resumeFrom(previous: Checkpoint, agentId: string): Checkpoint {
  return {
    ac_version: "0.1.0",
    checkpoint_id: randomUUID(),
    task_id: previous.task_id,
    agent_id: agentId,
    emitted_at: new Date().toISOString(),
    status: "partial",
    task_summary: previous.task_summary,
    completed_steps: [...(previous.completed_steps || [])],
    remaining_steps: [...(previous.remaining_steps || [])],
    parent_checkpoint_id: previous.checkpoint_id,
  };
}
