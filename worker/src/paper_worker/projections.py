from __future__ import annotations

from pathlib import Path

from psycopg import Connection


def generate_topic_views(conn: Connection, root: Path) -> dict:
    output_dir = root / "knowledge" / "topics"
    output_dir.mkdir(parents=True, exist_ok=True)
    topics = conn.execute("SELECT id, slug, name, description FROM topics ORDER BY name").fetchall()
    written = 0
    for topic in topics:
        items = conn.execute(
            """
            SELECT ri.title, ri.canonical_url, ri.item_type, ri.year, w.slug
            FROM research_item_topics rit
            JOIN research_items ri ON ri.id = rit.research_item_id
            JOIN works w ON w.id = ri.work_id
            WHERE rit.topic_id = %s AND w.status = 'active'
            ORDER BY ri.year DESC NULLS LAST, ri.title
            """,
            (topic["id"],),
        ).fetchall()
        lines = [
            "---",
            f"id: topic:{topic['slug']}",
            f"title: {topic['name']}",
            "generated: true",
            "schema_version: 1",
            "---",
            "",
            f"# {topic['name']}",
            "",
            "This file is generated from reviewed Research Item metadata. Do not edit it by hand.",
            "",
        ]
        for item in items:
            year = f"{item['year']} · " if item["year"] else ""
            lines.append(
                f"- {year}{item['item_type']} · [{item['title']}]({item['canonical_url']})"
            )
        (output_dir / f"{topic['slug']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    return {"topics": written}
