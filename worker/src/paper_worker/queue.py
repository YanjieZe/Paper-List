from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import UUID

from psycopg import Connection


@dataclass(frozen=True)
class LeasedJob:
    id: UUID
    job_type: str
    payload: dict[str, Any]
    attempts: int
    max_attempts: int


def lease_next_job(conn: Connection, worker_id: str, lease_seconds: int) -> LeasedJob | None:
    row = conn.execute(
        """
        WITH candidate AS (
            SELECT id
            FROM jobs
            WHERE status = 'queued'
              AND available_at <= now()
              AND (lease_expires_at IS NULL OR lease_expires_at < now())
            ORDER BY priority ASC, created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        UPDATE jobs j
        SET status = 'running', leased_by = %s,
            lease_expires_at = now() + (%s * interval '1 second'),
            attempts = attempts + 1,
            started_at = coalesce(started_at, now())
        FROM candidate
        WHERE j.id = candidate.id
        RETURNING j.id, j.job_type, j.payload, j.attempts, j.max_attempts
        """,
        (worker_id, lease_seconds),
    ).fetchone()
    conn.commit()
    if not row:
        return None
    return LeasedJob(
        id=row["id"],
        job_type=row["job_type"],
        payload=row["payload"],
        attempts=row["attempts"],
        max_attempts=row["max_attempts"],
    )


def emit_event(
    conn: Connection,
    job_id: UUID,
    event_type: str,
    *,
    stage: str | None = None,
    progress: float | None = None,
    message: str | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO job_events (job_id, event_type, stage, progress, message, data)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """,
        (job_id, event_type, stage, progress, message, json.dumps(data or {})),
    )
    if progress is not None or stage is not None:
        conn.execute(
            "UPDATE jobs SET progress = coalesce(%s, progress), current_stage = coalesce(%s, current_stage) WHERE id = %s",
            (progress, stage, job_id),
        )
    conn.commit()


def complete_job(conn: Connection, job_id: UUID, result: dict[str, Any]) -> None:
    conn.execute(
        """
        UPDATE jobs SET status = 'succeeded', progress = 100, result = %s::jsonb,
          finished_at = now(), leased_by = NULL, lease_expires_at = NULL
        WHERE id = %s
        """,
        (json.dumps(result), job_id),
    )
    emit_event(conn, job_id, "completed", progress=100, message="Task completed", data=result)


def fail_job(conn: Connection, job: LeasedJob, error: Exception) -> None:
    retry = job.attempts < job.max_attempts
    delay = timedelta(seconds=min(300, 2 ** max(0, job.attempts - 1) * 10))
    status = "queued" if retry else "dead"
    conn.execute(
        """
        UPDATE jobs SET status = %s, error = %s::jsonb, available_at = now() + %s,
          leased_by = NULL, lease_expires_at = NULL,
          finished_at = CASE WHEN %s = 'dead' THEN now() ELSE NULL END
        WHERE id = %s
        """,
        (
            status,
            json.dumps({"type": type(error).__name__, "message": str(error)}),
            delay,
            status,
            job.id,
        ),
    )
    emit_event(
        conn,
        job.id,
        "retry_scheduled" if retry else "failed",
        message=str(error),
        data={"attempt": job.attempts, "maxAttempts": job.max_attempts},
    )
