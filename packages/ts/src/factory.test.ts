import { describe, it, expect } from "vitest";
import { newCheckpoint, resumeFrom } from "./factory.js";

describe("factory", () => {
  it("newCheckpoint sets correct ac_version", () => {
    const cp = newCheckpoint("task-1", "agent-1", "summary");
    expect(cp.ac_version).toBe("0.1.0");
  });

  it("newCheckpoint generates valid UUID", () => {
    const cp = newCheckpoint("task-1", "agent-1", "summary");
    const parts = cp.checkpoint_id.split("-");
    expect(parts.length).toBe(5);
    expect(parts[0].length).toBe(8);
    expect(parts[2][0]).toBe("4"); // UUID v4 marker
  });

  it("newCheckpoint uses ISO 8601 timestamp", () => {
    const cp = newCheckpoint("task-1", "agent-1", "summary");
    const date = new Date(cp.emitted_at);
    expect(isNaN(date.getTime())).toBe(false);
    expect(cp.emitted_at).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  it("resumeFrom sets parent_checkpoint_id", () => {
    const previous = newCheckpoint("task-1", "agent-1", "summary");
    const resumed = resumeFrom(previous, "agent-2");
    expect(resumed.parent_checkpoint_id).toBe(previous.checkpoint_id);
  });

  it("resumeFrom preserves task_id", () => {
    const previous = newCheckpoint("task-1", "agent-1", "summary");
    const resumed = resumeFrom(previous, "agent-2");
    expect(resumed.task_id).toBe(previous.task_id);
  });

  it("resumeFrom copies completed_steps", () => {
    const previous = newCheckpoint("task-1", "agent-1", "summary");
    previous.completed_steps = ["step1", "step2"];
    const resumed = resumeFrom(previous, "agent-2");
    expect(resumed.completed_steps).toEqual(["step1", "step2"]);
    expect(resumed.completed_steps).not.toBe(previous.completed_steps); // Ensure copy
  });

  it("resumeFrom generates new checkpoint_id", () => {
    const previous = newCheckpoint("task-1", "agent-1", "summary");
    const resumed = resumeFrom(previous, "agent-2");
    expect(resumed.checkpoint_id).not.toBe(previous.checkpoint_id);
    expect(resumed.checkpoint_id.length).toBe(36);
  });
});
