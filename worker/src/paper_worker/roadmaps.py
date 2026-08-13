from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

from psycopg import Connection

from .agents import run_roadmap_agent
from .config import Settings


def _git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() or None


def create_roadmap_review(conn: Connection, settings: Settings, slug: str) -> dict:
    roadmap = conn.execute("SELECT * FROM roadmaps WHERE slug = %s", (slug,)).fetchone()
    if not roadmap:
        raise ValueError(f"roadmap {slug} does not exist")
    nodes = conn.execute(
        "SELECT * FROM roadmap_nodes WHERE roadmap_id = %s ORDER BY ordinal", (roadmap["id"],)
    ).fetchall()
    execution = asyncio.run(run_roadmap_agent(conn, settings, slug))
    draft = execution.output
    run = conn.execute(
        """
        INSERT INTO agent_runs (
          agent_name, model, reasoning_effort, prompt_version, schema_version, status,
          max_cost_usd, finished_at,
          input_tokens, output_tokens, cached_tokens, total_cost_usd
        ) VALUES ('Roadmap', %s, 'high', 'v1', 1, 'succeeded', %s, now(), %s, %s, %s, %s)
        RETURNING id
        """,
        (
            settings.model_deep,
            settings.budget_roadmap_usd,
            execution.input_tokens,
            execution.output_tokens,
            execution.cached_tokens,
            execution.estimated_cost_usd,
        ),
    ).fetchone()
    by_key = {section.key: section for section in draft.sections}
    content = {
        "title": roadmap["title"],
        "sections": [
            {
                "key": node["slug"],
                "title": node["title"],
                "markdown": by_key[node["slug"]].markdown,
                "claims": [
                    claim.model_dump(mode="json") for claim in by_key[node["slug"]].claims
                ],
                "required": True,
            }
            for node in nodes
        ],
    }
    artifact = conn.execute(
        """
        INSERT INTO artifacts (agent_run_id, artifact_type, schema_version, content)
        VALUES (%s, 'roadmap', 1, %s::jsonb) RETURNING id
        """,
        (run["id"], json.dumps(content, ensure_ascii=False)),
    ).fetchone()
    review = conn.execute(
        """
        INSERT INTO review_items (roadmap_id, artifact_id, review_type, status, base_git_sha)
        VALUES (%s, %s, 'roadmap', 'pending', %s) RETURNING id
        """,
        (roadmap["id"], artifact["id"], _git_head(settings.repository_root)),
    ).fetchone()
    for ordinal, section in enumerate(content["sections"]):
        conn.execute(
            """
            INSERT INTO review_sections (
              review_item_id, section_key, title, generated_markdown, claims, required, ordinal
            ) VALUES (%s, %s, %s, %s, %s::jsonb, true, %s)
            """,
            (
                review["id"],
                section["key"],
                section["title"],
                section["markdown"],
                json.dumps(section["claims"]),
                ordinal,
            ),
        )
    conn.execute("UPDATE roadmaps SET status = 'review' WHERE id = %s", (roadmap["id"],))
    conn.execute(
        """
        INSERT INTO notifications (kind, title, message, href)
        VALUES ('roadmap_review', 'Roadmap update ready', %s, %s)
        """,
        (roadmap["title"], f"/reviews/{review['id']}"),
    )
    conn.commit()
    return {"reviewId": str(review["id"]), "artifactId": str(artifact["id"])}
