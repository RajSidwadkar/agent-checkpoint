import { describe, it, expect } from "vitest";
import { parse, emit, emitJson } from "./codec.js";
import { Checkpoint } from "./types.js";

const VALID_DICT = {
  ac_version: "0.1.0",
  checkpoint_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  task_id: "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
  agent_id: "coder-gpt-4",
  emitted_at: "2026-06-16T14:30:00Z",
  status: "partial",
  task_summary: "Implement auth module",
  confidence: 0.75,
  executor_hint: "same",
  retry_strategy: "resume" as const,
  completed_steps: ["step1"],
};

describe("codec", () => {
  it("parses valid dict", () => {
    const result = parse(VALID_DICT);
    expect(result.ok).toBe(true);
    expect(result.checkpoint?.status).toBe("partial");
    expect(result.checkpoint?.confidence).toBe(0.75);
  });

  it("parses valid JSON string", () => {
    const jsonStr = JSON.stringify(VALID_DICT);
    const result = parse(jsonStr);
    expect(result.ok).toBe(true);
    expect(result.checkpoint?.checkpoint_id).toBe(VALID_DICT.checkpoint_id);
  });

  it("fails on empty object", () => {
    const result = parse({});
    expect(result.ok).toBe(false);
    const errorFields = result.errors.map((e) => e.field);
    const required = [
      "ac_version",
      "checkpoint_id",
      "task_id",
      "agent_id",
      "emitted_at",
      "status",
      "task_summary",
    ];
    required.forEach((f) => expect(errorFields).toContain(f));
  });

  it.each([
    ["confidence", 1.5],
    ["checkpoint_id", "not-a-uuid"],
  ])("fails on invalid value for %s", (field, value) => {
    const invalid = { ...VALID_DICT, [field]: value };
    const result = parse(invalid);
    expect(result.ok).toBe(false);
    expect(result.errors.some((e) => e.field === field)).toBe(true);
  });

  it("tolerates unknown extra fields", () => {
    const extra = { ...VALID_DICT, extra_field: "value" };
    const result = parse(extra);
    expect(result.ok).toBe(true);
  });

  it("emits dict with no undefined/null values", () => {
    const result = parse(VALID_DICT);
    const checkpoint = result.checkpoint!;
    const emitted = emit(checkpoint);
    Object.values(emitted).forEach((val) => {
      expect(val).not.toBeNull();
      expect(val).not.toBeUndefined();
    });
    expect(emitted).not.toHaveProperty("failure_reason");
  });

  it("emits valid JSON", () => {
    const result = parse(VALID_DICT);
    const jsonStr = emitJson(result.checkpoint!);
    const data = JSON.parse(jsonStr);
    expect(data.checkpoint_id).toBe(VALID_DICT.checkpoint_id);
  });

  it("round-trips correctly", () => {
    const firstParse = parse(VALID_DICT);
    const jsonStr = emitJson(firstParse.checkpoint!);
    const secondParse = parse(jsonStr);
    expect(secondParse.ok).toBe(true);
    expect(secondParse.checkpoint).toEqual(firstParse.checkpoint);
  });

  describe("trust tiers", () => {
    it("deserializes trust tiers correctly", () => {
      const data = {
        ...VALID_DICT,
        context_snapshot: {
          user_request: { value: "summarise", trust: "user" },
          system_id: "machine-1",
        },
      };
      const result = parse(data);
      const snapshot = result.checkpoint!.context_snapshot!;
      expect(snapshot.user_request).toEqual({ value: "summarise", trust: "user" });
      expect(snapshot.system_id).toBe("machine-1");
    });

    it("serializes trust tiers correctly", () => {
      const checkpoint: Checkpoint = {
        ...VALID_DICT,
        status: "partial",
        context_snapshot: {
          user_request: { value: "summarise", trust: "user" },
          system_id: "machine-1",
        },
      };
      const emitted = emit(checkpoint);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const snapshot = emitted.context_snapshot as any;
      expect(snapshot.user_request).toEqual({ value: "summarise", trust: "user" });
      expect(snapshot.system_id).toBe("machine-1");
    });

    it("ensures receiver compatibility", () => {
      const data = {
        ...VALID_DICT,
        context_snapshot: {
          user_request: { value: "summarise", trust: "user" },
        },
      };
      const result = parse(data);
      const emitted = emit(result.checkpoint!);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const snapshot = emitted.context_snapshot as any;
      expect(snapshot.user_request.value).toBe("summarise");
    });
  });
});
