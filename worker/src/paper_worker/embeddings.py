from __future__ import annotations

from collections.abc import Sequence

from openai import OpenAI
from psycopg import Connection

from .config import Settings


def embed_texts(settings: Settings, texts: Sequence[str]) -> list[list[float]]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for embeddings")
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
    response = client.embeddings.create(
        model=settings.model_embedding,
        input=list(texts),
        dimensions=settings.embedding_dimensions,
    )
    return [item.embedding for item in response.data]


def embed_missing_chunks(conn: Connection, settings: Settings, document_version_id, batch_size=64) -> int:
    rows = conn.execute(
        """
        SELECT id, content FROM document_chunks
        WHERE document_version_id = %s AND embedding IS NULL
        ORDER BY ordinal
        """,
        (document_version_id,),
    ).fetchall()
    updated = 0
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        vectors = embed_texts(settings, [row["content"] for row in batch])
        for row, vector in zip(batch, vectors, strict=True):
            conn.execute(
                "UPDATE document_chunks SET embedding = %s::vector, embedding_model = %s WHERE id = %s",
                (vector, settings.model_embedding, row["id"]),
            )
            updated += 1
        conn.commit()
    return updated
