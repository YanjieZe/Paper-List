from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from uuid import UUID, uuid4

from psycopg import Connection

from .agents import (
    AgentExecution,
    run_catalog_agent,
    run_linker_agent,
    run_reading_agent,
    run_research_agent,
)
from .config import Settings
from .ingestion import ingest_url
from .publisher import publish_review
from .queue import LeasedJob, emit_event
from .reviews import create_reading_review


def _git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() or None


def _record_agent_run(
    conn: Connection,
    job: LeasedJob,
    execution: AgentExecution,
    *,
    agent_name: str,
    model: str,
    reasoning: str,
    max_cost: float,
    artifact_type: str,
) -> UUID:
    run = conn.execute(
        """
        INSERT INTO agent_runs (
          job_id, agent_name, model, reasoning_effort, prompt_version, schema_version,
          status, input_tokens, output_tokens, cached_tokens, tool_cost_usd, total_cost_usd, max_cost_usd,
          finished_at
        ) VALUES (%s, %s, %s, %s, 'v1', 1, 'succeeded', %s, %s, %s, %s, %s, %s, now())
        RETURNING id
        """,
        (
            job.id,
            agent_name,
            model,
            reasoning,
            execution.input_tokens,
            execution.output_tokens,
            execution.cached_tokens,
            execution.tool_cost_usd,
            execution.estimated_cost_usd,
            max_cost,
        ),
    ).fetchone()
    output = execution.output
    serialized = output.model_dump(mode="json") if hasattr(output, "model_dump") else output
    artifact = conn.execute(
        """
        INSERT INTO artifacts (agent_run_id, artifact_type, schema_version, content)
        VALUES (%s, %s, 1, %s::jsonb) RETURNING id
        """,
        (run["id"], artifact_type, json.dumps(serialized)),
    ).fetchone()
    conn.commit()
    return artifact["id"]


def _queue_external_candidates(conn: Connection, urls: list[str]) -> int:
    queued = 0
    for url in dict.fromkeys(urls):
        if not url.startswith(("http://", "https://")):
            continue
        row = conn.execute(
            """
            INSERT INTO jobs (job_type, payload, idempotency_key, priority)
            VALUES ('ingest_url', %s::jsonb, %s, 120)
            ON CONFLICT (idempotency_key) DO NOTHING RETURNING id
            """,
            (json.dumps({"url": url, "context": "Discovered during web research"}), f"ingest:{url}"),
        ).fetchone()
        queued += int(row is not None)
    conn.commit()
    return queued


def _apply_catalog(conn: Connection, execution: AgentExecution) -> None:
    result = execution.output
    for topic_slug in dict.fromkeys(result.topics):
        slug = "-".join(
            part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in topic_slug).split()
        )[:80]
        if not slug:
            continue
        topic = conn.execute(
            """
            INSERT INTO topics (slug, name) VALUES (%s, %s)
            ON CONFLICT (slug) DO UPDATE SET name = excluded.name RETURNING id
            """,
            (slug, topic_slug),
        ).fetchone()
        conn.execute(
            """
            INSERT INTO research_item_topics (research_item_id, topic_id, source, confidence)
            VALUES (%s, %s, 'agent', %s)
            ON CONFLICT (research_item_id, topic_id)
            DO UPDATE SET confidence = excluded.confidence
            """,
            (result.research_item_id, topic["id"], result.confidence),
        )
    conn.commit()


def _apply_relations(conn: Connection, execution: AgentExecution) -> int:
    inserted = 0
    for relation in execution.output.relations:
        row = conn.execute(
            """
            INSERT INTO relations (
              source_work_id, target_work_id, relation_type, rationale, evidence, confidence, review_status
            ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, 'pending')
            ON CONFLICT (source_work_id, target_work_id, relation_type) DO NOTHING
            RETURNING id
            """,
            (
                relation.source_work_id,
                relation.target_work_id,
                relation.relation_type,
                relation.rationale,
                json.dumps([ref.model_dump(mode="json") for ref in relation.evidence]),
                relation.confidence,
            ),
        ).fetchone()
        inserted += int(row is not None)
    conn.commit()
    return inserted


def handle_job(conn: Connection, settings: Settings, job: LeasedJob) -> dict:
    payload = job.payload
    if job.job_type == "ingest_url":
        emit_event(conn, job.id, "progress", stage="resolve", progress=5, message="Resolving URL")
        result = ingest_url(
            conn,
            settings,
            str(payload["url"]),
            payload.get("context"),
            generate_embeddings=not payload.get("skip_embeddings", False),
            candidate_item_id=payload.get("candidateItemId"),
        )
        if settings.openai_api_key:
            item = conn.execute(
                "SELECT id, title, abstract, item_type FROM research_items WHERE id = %s",
                (result["researchItemId"],),
            ).fetchone()
            catalog = asyncio.run(
                run_catalog_agent(
                    settings,
                    item["id"],
                    item["title"],
                    item["abstract"],
                    item["item_type"],
                )
            )
            _record_agent_run(
                conn,
                job,
                catalog,
                agent_name="Catalog",
                model=settings.model_fast,
                reasoning="low",
                max_cost=settings.budget_triage_usd,
                artifact_type="catalog",
            )
            _apply_catalog(conn, catalog)
            result["triage"] = catalog.output.model_dump(mode="json")
            result["triageCostUsd"] = catalog.estimated_cost_usd
        emit_event(
            conn,
            job.id,
            "progress",
            stage="indexed",
            progress=90,
            message="Item normalized and indexed",
            data=result,
        )
        return result

    if job.job_type == "deep_read":
        item_id = UUID(str(payload["researchItemId"]))
        emit_event(conn, job.id, "progress", stage="reading", progress=10, message="Reading evidence")
        execution = asyncio.run(
            run_reading_agent(
                conn,
                settings,
                item_id,
                max_cost_usd=float(payload.get("maxCostUsd", settings.budget_deep_usd)),
            )
        )
        artifact_id = _record_agent_run(
            conn,
            job,
            execution,
            agent_name="Reader",
            model=settings.model_deep,
            reasoning="high",
            max_cost=float(payload.get("maxCostUsd", settings.budget_deep_usd)),
            artifact_type="reading_note",
        )
        review_id = create_reading_review(
            conn, execution.output, artifact_id, _git_head(settings.repository_root)
        )
        result = {
            "reviewId": str(review_id),
            "artifactId": str(artifact_id),
            "costUsd": execution.estimated_cost_usd,
        }
        try:
            linker = asyncio.run(run_linker_agent(conn, settings, item_id))
            linker_artifact_id = _record_agent_run(
                conn,
                job,
                linker,
                agent_name="Linker",
                model=settings.model_standard,
                reasoning="medium",
                max_cost=settings.budget_standard_usd,
                artifact_type="relation_candidates",
            )
            result.update(
                {
                    "linkerArtifactId": str(linker_artifact_id),
                    "relationCandidates": _apply_relations(conn, linker),
                    "linkerCostUsd": linker.estimated_cost_usd,
                }
            )
        except Exception as error:  # noqa: BLE001 - optional follow-up cannot invalidate the draft
            conn.execute(
                """
                INSERT INTO notifications (kind, title, message, href)
                VALUES ('agent_warning', 'Linker follow-up failed', %s, %s)
                """,
                (str(error)[:2000], f"/library/{item_id}"),
            )
            conn.commit()
            result["linkerWarning"] = str(error)
        return result

    if job.job_type == "research":
        query = str(payload["query"])
        conversation_id = UUID(str(payload["conversationId"])) if payload.get("conversationId") else uuid4()
        conn.execute(
            "INSERT INTO conversations (id, title) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (conversation_id, query[:120]),
        )
        conn.execute(
            "INSERT INTO conversation_messages (conversation_id, role, content) VALUES (%s, 'user', %s::jsonb)",
            (conversation_id, json.dumps({"text": query})),
        )
        conn.commit()
        emit_event(
            conn, job.id, "progress", stage="research", progress=10, message="Searching library and web"
        )
        execution = asyncio.run(
            run_research_agent(
                conn,
                settings,
                query,
                max_cost_usd=float(payload.get("maxCostUsd", settings.budget_research_usd)),
            )
        )
        artifact_id = _record_agent_run(
            conn,
            job,
            execution,
            agent_name="Research Librarian",
            model=settings.model_deep,
            reasoning="high",
            max_cost=float(payload.get("maxCostUsd", settings.budget_research_usd)),
            artifact_type="research_answer",
        )
        output = execution.output
        conn.execute(
            "INSERT INTO conversation_messages (conversation_id, role, content) VALUES (%s, 'assistant', %s::jsonb)",
            (conversation_id, output.model_dump_json()),
        )
        candidates = _queue_external_candidates(conn, output.external_candidates)
        return {
            "conversationId": str(conversation_id),
            "artifactId": str(artifact_id),
            "answer": output.model_dump(mode="json"),
            "externalCandidatesQueued": candidates,
            "costUsd": execution.estimated_cost_usd,
        }

    if job.job_type == "publish_review":
        emit_event(
            conn, job.id, "progress", stage="git_publish", progress=10, message="Validating review"
        )
        return publish_review(conn, settings, UUID(str(payload["reviewId"])))

    if job.job_type == "reindex_markdown":
        from .sync import reindex_markdown

        return reindex_markdown(conn, settings.repository_root)

    if job.job_type == "refresh_roadmap":
        from .roadmaps import create_roadmap_review

        return create_roadmap_review(conn, settings, str(payload.get("slug", "robotics")))

    raise ValueError(f"unsupported job type: {job.job_type}")
