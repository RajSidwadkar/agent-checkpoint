import { Checkpoint, ParseResult, TrustedValue, TrustTier } from "./types.js";
import { validate } from "./validator.js";

export function parse(data: string | object): ParseResult {
  let rawObj: Record<string, unknown>;

  if (typeof data === "string") {
    try {
      rawObj = JSON.parse(data);
    } catch (e) {
      return {
        ok: false,
        checkpoint: null,
        errors: [{ field: "json", message: `Invalid JSON: ${e instanceof Error ? e.message : String(e)}` }],
      };
    }
  } else {
    rawObj = data as Record<string, unknown>;
  }

  const errors = validate(rawObj);
  if (errors.length > 0) {
    return { ok: false, checkpoint: null, errors };
  }

  try {
    let contextSnapshot = rawObj.context_snapshot as Record<string, unknown> | undefined;
    if (contextSnapshot && typeof contextSnapshot === "object") {
      const deserialized: Record<string, TrustedValue | unknown> = {};
      for (const [key, val] of Object.entries(contextSnapshot)) {
        if (
          val &&
          typeof val === "object" &&
          !Array.isArray(val) &&
          "value" in val &&
          "trust" in val
        ) {
          const v = val as Record<string, unknown>;
          const trustTiers: TrustTier[] = ["system", "agent", "user", "verified"];
          if (typeof v.trust === "string" && trustTiers.includes(v.trust as TrustTier)) {
            deserialized[key] = {
              value: v.value,
              trust: v.trust as TrustTier,
            };
          } else {
            deserialized[key] = val;
          }
        } else {
          deserialized[key] = val;
        }
      }
      contextSnapshot = deserialized as Record<string, unknown>;
    }

    const checkpoint: Checkpoint = {
      ac_version: rawObj.ac_version as string,
      checkpoint_id: rawObj.checkpoint_id as string,
      task_id: rawObj.task_id as string,
      agent_id: rawObj.agent_id as string,
      emitted_at: rawObj.emitted_at as string,
      status: rawObj.status as Checkpoint["status"],
      task_summary: rawObj.task_summary as string,
      completed_steps: (rawObj.completed_steps as string[]) || [],
      remaining_steps: (rawObj.remaining_steps as string[]) || [],
      partial_output: rawObj.partial_output as Record<string, unknown>,
      failure_reason: rawObj.failure_reason as string,
      confidence: rawObj.confidence as number,
      retry_strategy: rawObj.retry_strategy as Checkpoint["retry_strategy"],
      executor_hint: rawObj.executor_hint as string,
      context_snapshot: contextSnapshot as Record<string, unknown>,
      parent_checkpoint_id: rawObj.parent_checkpoint_id as string,
    };

    return { ok: true, checkpoint, errors: [] };
  } catch (e) {
    return {
      ok: false,
      checkpoint: null,
      errors: [{ field: "internal", message: `Failed to instantiate Checkpoint: ${e instanceof Error ? e.message : String(e)}` }],
    };
  }
}

export function emit(checkpoint: Checkpoint): Record<string, unknown> {
  const raw = { ...checkpoint } as Record<string, unknown>;
  const clean: Record<string, unknown> = {};

  for (const [key, val] of Object.entries(raw)) {
    if (val === undefined || val === null) continue;

    if (key === "context_snapshot" && typeof val === "object" && !Array.isArray(val)) {
      const snapshot: Record<string, unknown> = {};
      for (const [sk, sv] of Object.entries(val)) {
        if (sv && typeof sv === "object" && "trust" in sv && "value" in sv) {
            const safeSv = sv as Record<string, unknown>;
            snapshot[sk] = { value: safeSv.value, trust: safeSv.trust };
        } else {
          snapshot[sk] = sv;
        }
      }
      clean[key] = snapshot;
    } else {
      clean[key] = val;
    }
  }

  return clean;
}

export function emitJson(checkpoint: Checkpoint, indent: number = 2): string {
  return JSON.stringify(emit(checkpoint), null, indent);
}
