from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from psycopg import Connection

from .schemas import PaperMetadata
from .urls import URLIdentity


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return (slug[:72] or "research-item").strip("-")


@dataclass(frozen=True)
class UpsertedItem:
    item_id: UUID
    work_id: UUID
    created: bool
    merged: bool


def upsert_research_item(
    conn: Connection,
    metadata: PaperMetadata,
    identity: URLIdentity,
    context: str | None,
) -> UpsertedItem:
    identity_pairs = [
        ("arxiv", identity.arxiv_id),
        ("doi", identity.doi),
        ("openreview", identity.openreview_id),
        ("github", identity.github_repo),
    ]
    existing = None
    for kind, value in identity_pairs:
        if not value:
            continue
        existing = conn.execute(
            """
            SELECT ri.id AS item_id, ri.work_id
            FROM source_identities si
            JOIN research_items ri ON ri.id = si.research_item_id
            WHERE si.identity_type = %s AND si.identity_value = %s
            """,
            (kind, value),
        ).fetchone()
        if existing:
            break
    if not existing:
        existing = conn.execute(
            "SELECT id AS item_id, work_id FROM research_items WHERE canonical_url = %s",
            (str(metadata.canonical_url),),
        ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE research_items SET title = %s, abstract = coalesce(%s, abstract),
              authors = %s::jsonb, year = coalesce(%s, year), venue = coalesce(%s, venue),
              confidence = greatest(confidence, %s), updated_at = now()
            WHERE id = %s
            """,
            (
                metadata.title,
                metadata.abstract,
                json.dumps(metadata.authors),
                metadata.year,
                metadata.venue,
                metadata.confidence,
                existing["item_id"],
            ),
        )
        conn.commit()
        return UpsertedItem(existing["item_id"], existing["work_id"], False, True)

    base_slug = slugify(metadata.title)
    slug = base_slug
    suffix = 1
    while conn.execute("SELECT 1 FROM works WHERE slug = %s", (slug,)).fetchone():
        suffix += 1
        slug = f"{base_slug}-{suffix}"
    work = conn.execute(
        """
        INSERT INTO works (canonical_title, slug, abstract, year, venue)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """,
        (metadata.title, slug, metadata.abstract, metadata.year, metadata.venue),
    ).fetchone()
    item = conn.execute(
        """
        INSERT INTO research_items (
          work_id, item_type, title, canonical_url, abstract, authors, year, venue,
          source_kind, confidence, added_context
        ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            work["id"],
            metadata.item_type.value,
            metadata.title,
            str(metadata.canonical_url),
            metadata.abstract,
            json.dumps(metadata.authors),
            metadata.year,
            metadata.venue,
            metadata.source_kind,
            metadata.confidence,
            context,
        ),
    ).fetchone()
    for kind, value in identity_pairs + [("url", identity.normalized_url)]:
        if value:
            conn.execute(
                """
                INSERT INTO source_identities (research_item_id, identity_type, identity_value, is_primary)
                VALUES (%s, %s, %s, %s) ON CONFLICT (identity_type, identity_value) DO NOTHING
                """,
                (item["id"], kind, value, kind != "url"),
            )
    conn.execute(
        """
        INSERT INTO item_sources (research_item_id, url, source_type, is_official)
        VALUES (%s, %s, %s, true) ON CONFLICT DO NOTHING
        """,
        (item["id"], str(metadata.canonical_url), metadata.source_kind),
    )
    conn.commit()
    return UpsertedItem(item["id"], work["id"], True, False)


def insert_document(
    conn: Connection,
    *,
    item_id: UUID,
    source_url: str,
    media_type: str,
    storage_path: str,
    extracted,
) -> UUID:
    existing = conn.execute(
        "SELECT id FROM document_versions WHERE research_item_id = %s AND sha256 = %s",
        (item_id, extracted.sha256),
    ).fetchone()
    if existing:
        return existing["id"]
    row = conn.execute(
        """
        INSERT INTO document_versions (
          research_item_id, source_url, media_type, sha256, storage_path, byte_size, page_count
        ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (
            item_id,
            source_url,
            media_type,
            extracted.sha256,
            storage_path,
            extracted.byte_size,
            extracted.page_count,
        ),
    ).fetchone()
    for chunk in extracted.chunks:
        conn.execute(
            """
            INSERT INTO document_chunks (
              document_version_id, ordinal, page, heading, content, bbox, token_count
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
            """,
            (
                row["id"],
                chunk.ordinal,
                chunk.page,
                chunk.heading,
                chunk.content,
                json.dumps(chunk.bbox) if chunk.bbox else None,
                chunk.token_count,
            ),
        )
    conn.commit()
    return row["id"]


def hybrid_search(
    conn: Connection, query: str, embedding: list[float] | None, limit: int = 12
) -> list[dict[str, Any]]:
    if embedding:
        rows = conn.execute(
            """
            WITH ranked AS (
              SELECT dc.id, dc.document_version_id, dc.page, dc.heading, dc.content,
                ts_rank_cd(dc.search_vector, websearch_to_tsquery('simple', %s)) AS text_score,
                1 - (dc.embedding <=> %s::vector) AS vector_score
              FROM document_chunks dc
              WHERE dc.embedding IS NOT NULL
                OR dc.search_vector @@ websearch_to_tsquery('simple', %s)
            )
            SELECT *, (0.45 * text_score + 0.55 * coalesce(vector_score, 0)) AS score
            FROM ranked ORDER BY score DESC LIMIT %s
            """,
            (query, embedding, query, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT dc.id, dc.document_version_id, dc.page, dc.heading, dc.content,
              ts_rank_cd(dc.search_vector, websearch_to_tsquery('simple', %s)) AS score
            FROM document_chunks dc
            WHERE dc.search_vector @@ websearch_to_tsquery('simple', %s)
            ORDER BY score DESC LIMIT %s
            """,
            (query, query, limit),
        ).fetchall()
    return [dict(row) for row in rows]
