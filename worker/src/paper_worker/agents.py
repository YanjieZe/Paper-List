from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from agents import Agent, ModelSettings, RunConfig, Runner, WebSearchTool
from openai.types.shared import Reasoning
from psycopg import Connection

from .config import Settings
from .costs import BudgetExceeded, estimate_text_cost
from .embeddings import embed_texts
from .repository import hybrid_search
from .schemas import (
    CatalogResult,
    CriticReport,
    LinkerResult,
    ReadingNoteDraft,
    ResearchAnswer,
    RoadmapDraft,
    TutorResponse,
)

AUTONOMY_POLICY = """
You may read supplied evidence, search approved sources, and produce a draft. You must not publish,
modify human-authored text, merge unrelated works, or perform external writes. Stop with an explicit
structured gap when evidence is missing. Never turn an inference into a factual claim.
"""


@dataclass(frozen=True)
class AgentExecution:
    output: Any
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    estimated_cost_usd: float
    tool_cost_usd: float = 0.0


def _model_settings(effort: str, verbosity: str = "medium") -> ModelSettings:
    return ModelSettings(
        reasoning=Reasoning(effort=effort, context="current_turn"),
        verbosity=verbosity,
        include_usage=True,
        store=False,
    )


def _usage(result) -> tuple[int, int, int]:
    usage = result.context_wrapper.usage
    cached = getattr(usage.input_tokens_details, "cached_tokens", 0) or 0
    return usage.input_tokens, usage.output_tokens, cached


def _web_search_calls(result) -> int:
    calls = 0
    for item in result.new_items:
        raw = getattr(item, "raw_item", None)
        kind = getattr(raw, "type", "") if raw is not None else ""
        calls += int("web_search" in str(kind))
    return calls


def build_agent_registry(settings: Settings) -> dict[str, Agent]:
    """Create the named v1 specialist inventory with explicit model roles and contracts."""
    return {
        "ingestion": Agent(
            name="Ingestion",
            instructions=AUTONOMY_POLICY + " Inspect supplied source metadata and report extraction gaps.",
            model=settings.model_fast,
            model_settings=_model_settings("low", "low"),
            output_type=CatalogResult,
        ),
        "catalog": Agent(
            name="Catalog",
            instructions=AUTONOMY_POLICY
            + " Classify robotics research using short stable topic slugs and judge reading value.",
            model=settings.model_fast,
            model_settings=_model_settings("low", "medium"),
            output_type=CatalogResult,
        ),
        "reader": Agent(
            name="Reader",
            instructions=AUTONOMY_POLICY
            + " Explain difficult robotics ideas from intuition to method, equations, evidence, and critique.",
            model=settings.model_deep,
            model_settings=_model_settings("high", "high"),
            output_type=ReadingNoteDraft,
        ),
        "critic": Agent(
            name="Critic",
            instructions=AUTONOMY_POLICY
            + " Audit every factual statement against supplied evidence; report unsupported or overstated claims.",
            model=settings.model_deep,
            model_settings=_model_settings("high", "medium"),
            output_type=CriticReport,
        ),
        "linker": Agent(
            name="Linker",
            instructions=AUTONOMY_POLICY
            + " Propose only evidence-backed relations between already identified Works.",
            model=settings.model_standard,
            model_settings=_model_settings("medium", "medium"),
            output_type=LinkerResult,
        ),
        "roadmap": Agent(
            name="Roadmap",
            instructions=AUTONOMY_POLICY
            + " Build an evidence-backed Robotics field map covering evolution, branches, disputes, frontier, and open questions.",
            model=settings.model_deep,
            model_settings=_model_settings("high", "high"),
            output_type=RoadmapDraft,
        ),
        "tutor": Agent(
            name="Tutor",
            instructions=AUTONOMY_POLICY
            + " Teach in Chinese from intuition upward while preserving English terminology, variables, and equations.",
            model=settings.model_standard,
            model_settings=_model_settings("medium", "high"),
            output_type=TutorResponse,
        ),
        "librarian": Agent(
            name="Librarian",
            instructions=AUTONOMY_POLICY
            + " Coordinate bounded specialists, preserve provenance, and return one evidence-complete research answer.",
            model=settings.model_standard,
            model_settings=_model_settings("medium", "medium"),
            output_type=ResearchAnswer,
        ),
    }


async def run_catalog_agent(
    settings: Settings,
    item_id: UUID,
    title: str,
    abstract: str | None,
    item_type: str,
) -> AgentExecution:
    agent = build_agent_registry(settings)["catalog"]
    result = await Runner.run(
        agent,
        f"Research Item ID: {item_id}\nType: {item_type}\nTitle: {title}\nAbstract: {abstract or 'Unavailable'}",
        max_turns=3,
        run_config=RunConfig(workflow_name="paper_catalog", trace_include_sensitive_data=False),
    )
    input_tokens, output_tokens, cached = _usage(result)
    cost = estimate_text_cost(settings.model_fast, input_tokens, output_tokens)
    if cost > settings.budget_triage_usd:
        raise BudgetExceeded(
            f"catalog cost ${cost:.4f} exceeded ${settings.budget_triage_usd:.2f}"
        )
    return AgentExecution(result.final_output, input_tokens, output_tokens, cached, cost)


async def run_critic_agent(
    settings: Settings, draft: ReadingNoteDraft, evidence_index: list[dict]
) -> AgentExecution:
    agent = build_agent_registry(settings)["critic"]
    result = await Runner.run(
        agent,
        "Audit the draft. A factual claim is valid only when its EvidenceRef resolves to the supplied "
        "evidence index. Do not rewrite the note.\n\nDRAFT:\n"
        + draft.model_dump_json()
        + "\n\nEVIDENCE INDEX:\n"
        + json.dumps(evidence_index, ensure_ascii=False),
        max_turns=4,
        run_config=RunConfig(workflow_name="paper_critic", trace_include_sensitive_data=False),
    )
    input_tokens, output_tokens, cached = _usage(result)
    cost = estimate_text_cost(settings.model_deep, input_tokens, output_tokens)
    return AgentExecution(result.final_output, input_tokens, output_tokens, cached, cost)


async def run_reading_agent(
    conn: Connection,
    settings: Settings,
    item_id: UUID,
    *,
    max_cost_usd: float | None = None,
) -> AgentExecution:
    item = conn.execute(
        "SELECT id, title, item_type, abstract FROM research_items WHERE id = %s", (item_id,)
    ).fetchone()
    if not item:
        raise ValueError(f"Research Item {item_id} does not exist")
    chunks = conn.execute(
        """
        SELECT dc.document_version_id, dc.page, dc.heading, dc.content
        FROM document_chunks dc JOIN document_versions dv ON dv.id = dc.document_version_id
        WHERE dv.research_item_id = %s ORDER BY dc.ordinal LIMIT 240
        """,
        (item_id,),
    ).fetchall()
    if not chunks:
        raise ValueError("Deep reading requires an extracted document")
    evidence = [
        {
            "document_version_id": str(row["document_version_id"]),
            "page": row["page"],
            "section": row["heading"],
            "content": row["content"],
        }
        for row in chunks
    ]
    prompt = f"""
Research Item ID: {item_id}
Title: {item['title']}
Type: {item['item_type']}
Abstract: {item['abstract'] or 'Unavailable'}

Create a Chinese-first, English-terminology-preserving layered reading note. Use only evidence in the
EVIDENCE JSON below for factual claims. Every factual claim must use the exact document_version_id and
page/section supplied. Mark synthesis without direct support as inference. Do not invent experiments for
blogs or project pages. Include the fourteen product sections, using a short explicit N/A explanation when
a section is genuinely inapplicable.

EVIDENCE JSON:
{json.dumps(evidence, ensure_ascii=False)}
"""
    agent = build_agent_registry(settings)["reader"]
    result = await Runner.run(
        agent,
        prompt,
        max_turns=6,
        run_config=RunConfig(
            workflow_name="paper_deep_read",
            trace_include_sensitive_data=False,
        ),
    )
    input_tokens, output_tokens, cached = _usage(result)
    cost = estimate_text_cost(settings.model_deep, input_tokens, output_tokens)
    limit = max_cost_usd or settings.budget_deep_usd
    if cost > limit:
        raise BudgetExceeded(f"deep read cost ${cost:.4f} exceeded ${limit:.2f}")
    output = result.final_output
    _validate_evidence(conn, output)
    critic = await run_critic_agent(settings, output, evidence)
    report: CriticReport = critic.output
    total_cost = cost + critic.estimated_cost_usd
    if total_cost > limit:
        raise BudgetExceeded(f"reader + critic cost ${total_cost:.4f} exceeded ${limit:.2f}")
    if not report.approved or report.unsupported_claims:
        findings = "; ".join(report.unsupported_claims or [item.finding for item in report.findings])
        raise ValueError(f"Critic rejected the reading draft: {findings}")
    return AgentExecution(
        output,
        input_tokens + critic.input_tokens,
        output_tokens + critic.output_tokens,
        cached + critic.cached_tokens,
        total_cost,
    )


def _validate_evidence(conn: Connection, draft: ReadingNoteDraft) -> None:
    for section in draft.sections:
        for claim in section.claims:
            for evidence in claim.evidence:
                row = conn.execute(
                    """
                    SELECT 1 FROM document_versions dv
                    WHERE dv.id = %s AND dv.research_item_id = %s
                      AND (%s::integer IS NULL OR dv.page_count IS NULL OR %s <= dv.page_count)
                    """,
                    (
                        evidence.document_version_id,
                        draft.research_item_id,
                        evidence.page,
                        evidence.page,
                    ),
                ).fetchone()
                if not row:
                    raise ValueError("agent returned an evidence reference outside the source document")


async def run_research_agent(
    conn: Connection,
    settings: Settings,
    query: str,
    *,
    max_cost_usd: float | None = None,
) -> AgentExecution:
    query_embedding = embed_texts(settings, [query])[0] if settings.openai_api_key else None
    local_chunks = hybrid_search(conn, query, query_embedding, limit=16)
    local_context = [
        {
            "document_version_id": str(row["document_version_id"]),
            "page": row["page"],
            "section": row["heading"],
            "content": row["content"],
        }
        for row in local_chunks
    ]
    agent = Agent(
        name="Research Librarian",
        instructions=AUTONOMY_POLICY
        + """
Answer robotics research questions in Chinese while preserving English technical terminology. Start from
the private library evidence, then search the web for current primary sources and official project/code
pages. Separate facts from inference. Return external candidate URLs worth adding to the Inbox.
""",
        tools=[WebSearchTool(search_context_size="high", external_web_access=True)],
        model=settings.model_deep,
        model_settings=_model_settings("high", "high"),
        output_type=ResearchAnswer,
    )
    result = await Runner.run(
        agent,
        f"QUESTION:\n{query}\n\nLOCAL EVIDENCE JSON:\n{json.dumps(local_context, ensure_ascii=False)}",
        max_turns=8,
        run_config=RunConfig(
            workflow_name="robotics_research",
            trace_include_sensitive_data=False,
        ),
    )
    input_tokens, output_tokens, cached = _usage(result)
    tool_cost = _web_search_calls(result) * settings.web_search_cost_usd
    cost = estimate_text_cost(settings.model_deep, input_tokens, output_tokens) + tool_cost
    limit = max_cost_usd or settings.budget_research_usd
    if cost > limit:
        raise BudgetExceeded(f"research cost ${cost:.4f} exceeded ${limit:.2f}")
    return AgentExecution(result.final_output, input_tokens, output_tokens, cached, cost, tool_cost)


async def run_roadmap_agent(
    conn: Connection,
    settings: Settings,
    slug: str,
    *,
    max_cost_usd: float | None = None,
) -> AgentExecution:
    roadmap = conn.execute("SELECT * FROM roadmaps WHERE slug = %s", (slug,)).fetchone()
    if not roadmap:
        raise ValueError(f"roadmap {slug} does not exist")
    nodes = conn.execute(
        "SELECT slug, title, narrative FROM roadmap_nodes WHERE roadmap_id = %s ORDER BY ordinal",
        (roadmap["id"],),
    ).fetchall()
    sources = conn.execute(
        """
        SELECT ri.id, ri.title, ri.abstract, ri.year, ri.venue, ri.item_type,
               w.id AS work_id, array_remove(array_agg(DISTINCT t.name), NULL) AS topics
        FROM research_items ri
        JOIN works w ON w.id = ri.work_id
        LEFT JOIN research_item_topics rit ON rit.research_item_id = ri.id
        LEFT JOIN topics t ON t.id = rit.topic_id
        WHERE ri.lifecycle_status IN ('review', 'published')
        GROUP BY ri.id, w.id
        ORDER BY ri.year NULLS LAST, ri.title
        LIMIT 400
        """
    ).fetchall()
    evidence = conn.execute(
        """
        SELECT dc.document_version_id, dc.page, dc.heading, left(dc.content, 1800) AS content
        FROM document_chunks dc
        JOIN document_versions dv ON dv.id = dc.document_version_id
        JOIN research_items ri ON ri.id = dv.research_item_id
        WHERE ri.lifecycle_status IN ('review', 'published')
        ORDER BY ri.year NULLS LAST, dc.ordinal
        LIMIT 240
        """
    ).fetchall()
    prompt = {
        "roadmap": {"slug": slug, "title": roadmap["title"]},
        "required_sections": [dict(row) for row in nodes],
        "works": [dict(row) for row in sources],
        "evidence": [dict(row) for row in evidence],
    }
    agent = build_agent_registry(settings)["roadmap"]
    result = await Runner.run(
        agent,
        "Generate exactly one section for every required section key. Explain problem definition, "
        "prerequisites, foundational works, technical branches, turning points, disputes, frontier, "
        "and open questions where applicable. Use Chinese explanation and preserve English terms. "
        "Every factual claim needs an exact supplied document_version_id plus page or section; "
        "otherwise label it inference. Do not claim the catalog is exhaustive.\n\nINPUT JSON:\n"
        + json.dumps(prompt, ensure_ascii=False, default=str),
        max_turns=8,
        run_config=RunConfig(workflow_name="robotics_roadmap", trace_include_sensitive_data=False),
    )
    input_tokens, output_tokens, cached = _usage(result)
    cost = estimate_text_cost(settings.model_deep, input_tokens, output_tokens)
    limit = max_cost_usd or settings.budget_roadmap_usd
    if cost > limit:
        raise BudgetExceeded(f"roadmap cost ${cost:.4f} exceeded ${limit:.2f}")
    output: RoadmapDraft = result.final_output
    if output.roadmap_slug != slug:
        raise ValueError("roadmap agent returned the wrong roadmap slug")
    required = {row["slug"] for row in nodes}
    returned = {section.key for section in output.sections}
    if returned != required:
        raise ValueError(f"roadmap sections differ: missing={required-returned}, extra={returned-required}")
    for section in output.sections:
        for claim in section.claims:
            for ref in claim.evidence:
                if ref.document_version_id:
                    exists = conn.execute(
                        """
                        SELECT 1 FROM document_versions
                        WHERE id = %s AND (%s::integer IS NULL OR page_count IS NULL OR %s <= page_count)
                        """,
                        (ref.document_version_id, ref.page, ref.page),
                    ).fetchone()
                    if not exists:
                        raise ValueError("roadmap agent returned an invalid document evidence reference")
    return AgentExecution(result.final_output, input_tokens, output_tokens, cached, cost)


async def run_linker_agent(
    conn: Connection,
    settings: Settings,
    item_id: UUID,
) -> AgentExecution:
    item = conn.execute(
        "SELECT ri.id, ri.title, ri.abstract, ri.work_id FROM research_items ri WHERE ri.id = %s",
        (item_id,),
    ).fetchone()
    if not item or not item["work_id"]:
        raise ValueError("Linker requires a Research Item attached to a Work")
    candidates = conn.execute(
        """
        SELECT DISTINCT w.id AS work_id, w.canonical_title, w.abstract, w.year
        FROM works w
        JOIN research_items ri ON ri.work_id = w.id
        LEFT JOIN research_item_topics candidate_topics ON candidate_topics.research_item_id = ri.id
        WHERE w.status = 'active' AND w.id <> %s
          AND (
            candidate_topics.topic_id IN (
              SELECT topic_id FROM research_item_topics WHERE research_item_id = %s
            ) OR w.abstract IS NOT NULL
          )
        ORDER BY w.year DESC NULLS LAST, w.canonical_title
        LIMIT 30
        """,
        (item["work_id"], item_id),
    ).fetchall()
    evidence = conn.execute(
        """
        SELECT dc.document_version_id, dc.page, dc.heading, left(dc.content, 1600) AS content
        FROM document_chunks dc JOIN document_versions dv ON dv.id = dc.document_version_id
        WHERE dv.research_item_id = %s ORDER BY dc.ordinal LIMIT 100
        """,
        (item_id,),
    ).fetchall()
    agent = build_agent_registry(settings)["linker"]
    result = await Runner.run(
        agent,
        "Identify only high-confidence technical relations between CURRENT WORK and CANDIDATE WORKS. "
        "Return an empty list if evidence is insufficient. A relation rationale may be an inference, "
        "but any factual support must point to the supplied document version and locator. Never relate "
        "a Work to itself.\n\nINPUT JSON:\n"
        + json.dumps(
            {
                "current_work": {
                    "work_id": str(item["work_id"]),
                    "title": item["title"],
                    "abstract": item["abstract"],
                },
                "candidate_works": [dict(row) for row in candidates],
                "evidence": [dict(row) for row in evidence],
            },
            ensure_ascii=False,
            default=str,
        ),
        max_turns=4,
        run_config=RunConfig(workflow_name="paper_linker", trace_include_sensitive_data=False),
    )
    input_tokens, output_tokens, cached = _usage(result)
    cost = estimate_text_cost(settings.model_standard, input_tokens, output_tokens)
    if cost > settings.budget_standard_usd:
        raise BudgetExceeded(
            f"linker cost ${cost:.4f} exceeded ${settings.budget_standard_usd:.2f}"
        )
    output: LinkerResult = result.final_output
    allowed = {item["work_id"], *(row["work_id"] for row in candidates)}
    for relation in output.relations:
        if relation.source_work_id not in allowed or relation.target_work_id not in allowed:
            raise ValueError("Linker returned a Work outside its candidate set")
        if relation.source_work_id == relation.target_work_id:
            raise ValueError("Linker returned a self relation")
        if item["work_id"] not in {relation.source_work_id, relation.target_work_id}:
            raise ValueError("Linker returned a relation unrelated to the current Work")
        for ref in relation.evidence:
            if ref.document_version_id:
                exists = conn.execute(
                    "SELECT 1 FROM document_versions WHERE id = %s",
                    (ref.document_version_id,),
                ).fetchone()
                if not exists:
                    raise ValueError("Linker returned invalid document evidence")
    return AgentExecution(output, input_tokens, output_tokens, cached, cost)
