import { createHash } from "node:crypto";
import { db } from "@/lib/db";

export type JobType =
  | "ingest_url"
  | "deep_read"
  | "research"
  | "publish_review"
  | "reindex_markdown"
  | "refresh_roadmap";

export async function enqueueJob(
  jobType: JobType,
  payload: Record<string, unknown>,
  options: { idempotencyKey?: string; priority?: number } = {},
) {
  const jsonPayload = JSON.parse(JSON.stringify(payload)) as never;
  const idempotencyKey =
    options.idempotencyKey ??
    createHash("sha256").update(`${jobType}:${JSON.stringify(payload)}`).digest("hex");
  const rows = await db()`
    insert into jobs (job_type, payload, idempotency_key, priority)
    values (${jobType}, ${db().json(jsonPayload)}, ${idempotencyKey}, ${options.priority ?? 100})
    on conflict (idempotency_key) do update set idempotency_key = excluded.idempotency_key
    returning id, status, created_at
  `;
  return rows[0] as { id: string; status: string; created_at: Date };
}
