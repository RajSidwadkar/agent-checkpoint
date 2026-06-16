export type CheckpointStatus = "partial" | "failed" | "paused" | "completed";

export type RetryStrategy = "resume" | "restart" | "escalate";

export type TrustTier = "system" | "agent" | "user" | "verified";

export interface TrustedValue {
  value: unknown;
  trust: TrustTier;
}

export interface Checkpoint {
  ac_version: string;
  checkpoint_id: string;
  task_id: string;
  agent_id: string;
  emitted_at: string;
  status: CheckpointStatus;
  task_summary: string;

  completed_steps?: string[];
  remaining_steps?: string[];
  partial_output?: Record<string, unknown>;
  failure_reason?: string;
  confidence?: number;
  retry_strategy?: RetryStrategy;
  executor_hint?: string;
  context_snapshot?: Record<string, TrustedValue | unknown>;
  parent_checkpoint_id?: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ParseResult {
  ok: boolean;
  checkpoint: Checkpoint | null;
  errors: ValidationError[];
}

export interface ConfidenceRange {
  min: number;
  max: number;
}

export interface AgentManifest {
  ac_version: string;
  agent_id: string;
  capabilities: string[];
  refuses?: string[];
  confidence_range?: ConfidenceRange;
  max_context_tokens?: number;
  contact?: string;
}
