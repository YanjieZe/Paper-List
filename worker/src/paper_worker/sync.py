from __future__ import annotations

from pathlib import Path

import frontmatter
from psycopg import Connection


def reindex_markdown(conn: Connection, root: Path) -> dict:
    indexed = 0
    skipped = 0
    for path in sorted((root / "knowledge" / "items").glob("*.md")):
        post = frontmatter.load(path)
        item_id = str(post.metadata.get("id", "")).removeprefix("item:")
        if not item_id:
            skipped += 1
            continue
        row = conn.execute("SELECT id FROM research_items WHERE id = %s", (item_id,)).fetchone()
        if not row:
            skipped += 1
            continue
        conn.execute(
            """
            UPDATE research_items SET title = %s, item_type = %s,
              canonical_url = %s, reading_status = %s, published_path = %s,
              lifecycle_status = 'published'
            WHERE id = %s
            """,
            (
                post.metadata.get("title"),
                post.metadata.get("type"),
                post.metadata.get("url"),
                post.metadata.get("reading_status", "read"),
                str(path.relative_to(root)),
                item_id,
            ),
        )
        indexed += 1
    conn.commit()
    return {"indexed": indexed, "skipped": skipped}
