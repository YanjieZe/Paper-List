from __future__ import annotations

import json
from uuid import UUID

from psycopg import Connection

from .schemas import ReadingNoteDraft


def create_reading_review(
    conn: Connection, draft: ReadingNoteDraft, artifact_id: UUID, base_git_sha: str | None
) -> UUID:
    review = conn.execute(
        """
        INSERT INTO review_items (
          research_item_id, artifact_id, review_type, status, base_git_sha
        ) VALUES (%s, %s, 'reading_note', 'pending', %s) RETURNING id
        """,
        (draft.research_item_id, artifact_id, base_git_sha),
    ).fetchone()
    for ordinal, section in enumerate(draft.sections):
        conn.execute(
            """
            INSERT INTO review_sections (
              review_item_id, section_key, title, generated_markdown, claims, required, ordinal
            ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
            """,
            (
                review["id"],
                section.key,
                section.title,
                section.markdown,
                json.dumps([claim.model_dump(mode="json") for claim in section.claims]),
                section.required,
                ordinal,
            ),
        )
    conn.execute(
        "UPDATE research_items SET lifecycle_status = 'review' WHERE id = %s",
        (draft.research_item_id,),
    )
    conn.execute(
        """
        INSERT INTO notifications (kind, title, message, href)
        VALUES ('review_ready', 'Reading note ready', %s, %s)
        """,
        (draft.title, f"/reviews/{review['id']}"),
    )
    conn.commit()
    return review["id"]


def validate_review_publishable(conn: Connection, review_id: UUID) -> dict:
    review = conn.execute(
        """
        SELECT rv.*, ri.title AS item_title, ri.item_type, ri.canonical_url, ri.authors,
               ri.year, ri.venue, w.slug AS item_slug, w.id AS work_id,
               rm.title AS roadmap_title, rm.slug AS roadmap_slug, rm.description AS roadmap_description,
               rm.version AS roadmap_version
        FROM review_items rv
        LEFT JOIN research_items ri ON ri.id = rv.research_item_id
        LEFT JOIN works w ON w.id = ri.work_id
        LEFT JOIN roadmaps rm ON rm.id = rv.roadmap_id
        WHERE rv.id = %s FOR UPDATE
        """,
        (review_id,),
    ).fetchone()
    if not review:
        raise ValueError("review does not exist")
    sections = conn.execute(
        "SELECT * FROM review_sections WHERE review_item_id = %s ORDER BY ordinal", (review_id,)
    ).fetchall()
    unresolved = [
        section["section_key"]
        for section in sections
        if section["required"] and section["status"] == "pending"
    ]
    if unresolved:
        raise ValueError(f"required sections remain pending: {', '.join(unresolved)}")
    accepted = [section for section in sections if section["status"] in {"accepted", "edited"}]
    if not accepted:
        raise ValueError("a publication requires at least one accepted section")
    for section in accepted:
        for claim in section["claims"] or []:
            if claim.get("kind") == "fact" and not claim.get("evidence"):
                raise ValueError(f"factual claim in {section['section_key']} has no evidence")
            for evidence in claim.get("evidence", []):
                document_id = evidence.get("document_version_id")
                if not document_id:
                    continue
                page = evidence.get("page")
                found = conn.execute(
                    """
                    SELECT 1 FROM document_versions
                    WHERE id = %s AND (%s::integer IS NULL OR page_count IS NULL OR %s <= page_count)
                    """,
                    (document_id, page, page),
                ).fetchone()
                if not found:
                    raise ValueError(f"claim in {section['section_key']} has invalid evidence")
    return {**dict(review), "sections": [dict(section) for section in accepted]}
