from __future__ import annotations

import json
from uuid import UUID

from psycopg import Connection


def merge_works(
    conn: Connection,
    target_work_id: UUID,
    source_work_id: UUID,
    *,
    reason: str,
    confidence: float,
    evidence: list[dict],
) -> UUID:
    if target_work_id == source_work_id:
        raise ValueError("a Work cannot be merged into itself")
    rows = conn.execute(
        "SELECT id, canonical_title, slug, status, merged_into_id FROM works WHERE id = ANY(%s) FOR UPDATE",
        ([target_work_id, source_work_id],),
    ).fetchall()
    by_id = {row["id"]: dict(row) for row in rows}
    if set(by_id) != {target_work_id, source_work_id}:
        raise ValueError("both Works must exist")
    source = by_id[source_work_id]
    if source["status"] == "merged":
        raise ValueError("source Work is already merged")
    before = {
        "works": [by_id[target_work_id], source],
        "source_item_ids": [
            str(row["id"])
            for row in conn.execute(
                "SELECT id FROM research_items WHERE work_id = %s", (source_work_id,)
            ).fetchall()
        ],
    }
    conn.execute("UPDATE research_items SET work_id = %s WHERE work_id = %s", (target_work_id, source_work_id))
    conn.execute(
        "UPDATE works SET status = 'merged', merged_into_id = %s WHERE id = %s",
        (target_work_id, source_work_id),
    )
    after = {"target_work_id": str(target_work_id), "source_work_id": str(source_work_id)}
    event = conn.execute(
        """
        INSERT INTO merge_events (
          target_work_id, source_work_id, reason, confidence, evidence,
          before_snapshot, after_snapshot
        ) VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb) RETURNING id
        """,
        (
            target_work_id,
            source_work_id,
            reason,
            confidence,
            json.dumps(evidence),
            json.dumps(before, default=str),
            json.dumps(after),
        ),
    ).fetchone()
    conn.commit()
    return event["id"]


def undo_merge(conn: Connection, merge_event_id: UUID) -> None:
    event = conn.execute(
        "SELECT * FROM merge_events WHERE id = %s FOR UPDATE", (merge_event_id,)
    ).fetchone()
    if not event:
        raise ValueError("merge event does not exist")
    if event["undone_at"]:
        raise ValueError("merge event is already undone")
    snapshot = event["before_snapshot"]
    source_item_ids = snapshot.get("source_item_ids", [])
    if source_item_ids:
        conn.execute(
            "UPDATE research_items SET work_id = %s WHERE id = ANY(%s::uuid[])",
            (event["source_work_id"], source_item_ids),
        )
    conn.execute(
        "UPDATE works SET status = 'active', merged_into_id = NULL WHERE id = %s",
        (event["source_work_id"],),
    )
    conn.execute("UPDATE merge_events SET undone_at = now() WHERE id = %s", (merge_event_id,))
    conn.commit()
