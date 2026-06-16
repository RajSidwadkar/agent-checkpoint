import { ValidationError } from "./types.js";

const UUID_V4_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SEMVER_PATTERN = /^\d+\.\d+\.\d+$/;

export function validate(data: unknown): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!data || typeof data !== "object" || Array.isArray(data)) {
    errors.push({ field: "root", message: "Data must be a JSON object" });
    return errors;
  }

  const obj = data as Record<string, unknown>;

  const requiredFields = [
    "ac_version",
    "checkpoint_id",
    "task_id",
    "agent_id",
    "emitted_at",
    "status",
    "task_summary",
  ];

  for (const field of requiredFields) {
    const val = obj[field];
    if (val === undefined || val === null) {
      errors.push({ field, message: "Field is missing" });
    } else if (typeof val !== "string" || val.trim() === "") {
      errors.push({ field, message: "Field must be a non-empty string" });
    }
  }

  if (typeof obj.ac_version === "string" && !SEMVER_PATTERN.test(obj.ac_version)) {
    errors.push({ field: "ac_version", message: "Must match semver pattern \\d+\\.\\d+\\.\\d+" });
  }

  for (const uuidField of ["checkpoint_id", "task_id", "parent_checkpoint_id"]) {
    const val = obj[uuidField];
    if (val !== undefined && val !== null) {
      if (typeof val !== "string") {
        errors.push({ field: uuidField, message: "Must be a string" });
      } else if (!UUID_V4_PATTERN.test(val)) {
        errors.push({ field: uuidField, message: "Must be a valid UUID v4" });
      }
    }
  }

  if (typeof obj.emitted_at === "string") {
    const date = new Date(obj.emitted_at);
    if (isNaN(date.getTime())) {
      errors.push({ field: "emitted_at", message: "Must be a valid ISO 8601 timestamp" });
    }
  }

  const validStatuses = ["partial", "failed", "paused", "completed"];
  if (typeof obj.status === "string" && !validStatuses.includes(obj.status)) {
    errors.push({ field: "status", message: `Must be one of: ${validStatuses.join(", ")}` });
  }

  const validRetries = ["resume", "restart", "escalate"];
  if (obj.retry_strategy !== undefined && obj.retry_strategy !== null) {
    if (typeof obj.retry_strategy !== "string" || !validRetries.includes(obj.retry_strategy)) {
      errors.push({
        field: "retry_strategy",
        message: `Must be one of: ${validRetries.join(", ")}`,
      });
    }
  }

  if (obj.confidence !== undefined && obj.confidence !== null) {
    const conf = Number(obj.confidence);
    if (isNaN(conf)) {
      errors.push({ field: "confidence", message: "Must be a number" });
    } else if (conf < 0.0 || conf > 1.0) {
      errors.push({ field: "confidence", message: "Must be between 0.0 and 1.0" });
    }
  }

  if (obj.executor_hint !== undefined && obj.executor_hint !== null) {
    const val = obj.executor_hint;
    if (typeof val !== "string") {
      errors.push({ field: "executor_hint", message: "Must be a string" });
    } else if (!(val === "same" || val === "any" || val.startsWith("capability:"))) {
      errors.push({
        field: "executor_hint",
        message: "Must be 'same', 'any', or start with 'capability:'",
      });
    }
  }

  return errors;
}
