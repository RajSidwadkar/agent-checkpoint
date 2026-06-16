import { AgentManifest, ConfidenceRange } from "./types.js";

export function parseManifest(data: string | object): AgentManifest | null {
  try {
    let obj: Record<string, unknown>;
    if (typeof data === "string") {
      obj = JSON.parse(data);
    } else {
      obj = data as Record<string, unknown>;
    }

    if (!obj || typeof obj !== "object" || Array.isArray(obj)) return null;

    if (typeof obj.ac_version !== "string" || typeof obj.agent_id !== "string" || !Array.isArray(obj.capabilities)) {
      return null;
    }

    let confidenceRange: ConfidenceRange | undefined;
    if (obj.confidence_range && typeof obj.confidence_range === "object" && !Array.isArray(obj.confidence_range)) {
      const cr = obj.confidence_range as Record<string, unknown>;
      const min = Number(cr.min ?? 0.0);
      const max = Number(cr.max ?? 1.0);

      if (!isNaN(min) && !isNaN(max) && min >= 0 && min <= 1 && max >= 0 && max <= 1 && min <= max) {
        confidenceRange = { min, max };
      }
    }

    return {
      ac_version: obj.ac_version,
      agent_id: obj.agent_id,
      capabilities: obj.capabilities as string[],
      refuses: Array.isArray(obj.refuses) ? (obj.refuses as string[]) : [],
      confidence_range: confidenceRange,
      max_context_tokens: typeof obj.max_context_tokens === "number" ? obj.max_context_tokens : undefined,
      contact: typeof obj.contact === "string" ? obj.contact : undefined,
    };
  } catch {
    return null;
  }
}

export function emitManifest(manifest: AgentManifest): string {

  function removeNone(obj: unknown): unknown {
    if (obj !== null && typeof obj === "object" && !Array.isArray(obj)) {
      const result: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(obj)) {
        if (v !== undefined && v !== null) {
          result[k] = removeNone(v);
        }
      }
      return result;
    }
    return obj;
  }

  return JSON.stringify(removeNone(manifest), null, 2);
}
