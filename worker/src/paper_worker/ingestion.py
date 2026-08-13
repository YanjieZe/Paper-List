from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from psycopg import Connection
from pydantic import HttpUrl

from .config import Settings
from .documents import extract_html, extract_pdf, sha256_bytes
from .embeddings import embed_missing_chunks
from .repository import UpsertedItem, insert_document, upsert_research_item
from .schemas import PaperMetadata
from .urls import URLIdentity, identify_url

USER_AGENT = "Paper-List-Research-OS/1.0 (personal research index)"


def _clean(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _arxiv_metadata(client: httpx.Client, identity: URLIdentity) -> PaperMetadata:
    response = client.get(
        "https://export.arxiv.org/api/query", params={"id_list": identity.arxiv_id}, timeout=30
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", namespace)
    if entry is None:
        raise ValueError(f"arXiv did not return metadata for {identity.arxiv_id}")
    title = _clean(entry.findtext("atom:title", namespaces=namespace)) or identity.arxiv_id or "arXiv paper"
    abstract = _clean(entry.findtext("atom:summary", namespaces=namespace))
    authors = [
        _clean(author.findtext("atom:name", namespaces=namespace)) or "Unknown"
        for author in entry.findall("atom:author", namespace)
    ]
    published = entry.findtext("atom:published", namespaces=namespace)
    year = int(published[:4]) if published else None
    pdf_url = f"https://arxiv.org/pdf/{identity.arxiv_id}.pdf"
    return PaperMetadata(
        title=title,
        item_type=identity.item_type,
        canonical_url=HttpUrl(identity.normalized_url),
        authors=authors,
        abstract=abstract,
        year=year,
        arxiv_id=identity.arxiv_id,
        pdf_url=HttpUrl(pdf_url),
        source_kind="arxiv",
        confidence=1.0,
    )


def _web_metadata(client: httpx.Client, identity: URLIdentity) -> tuple[PaperMetadata, bytes, str]:
    response = client.get(identity.normalized_url, timeout=45, follow_redirects=True)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "text/html").split(";", 1)[0]
    if content_type == "application/pdf" or response.url.path.lower().endswith(".pdf"):
        title = Path(response.url.path).stem.replace("-", " ") or "PDF document"
        return (
            PaperMetadata(
                title=title,
                item_type=identity.item_type,
                canonical_url=HttpUrl(identity.normalized_url),
                source_kind="pdf",
                confidence=0.65,
                pdf_url=HttpUrl(str(response.url)),
            ),
            response.content,
            "application/pdf",
        )
    soup = BeautifulSoup(response.content, "html.parser")
    og_title = soup.find("meta", property="og:title")
    description = soup.find("meta", property="og:description") or soup.find(
        "meta", attrs={"name": "description"}
    )
    title = _clean(og_title.get("content") if og_title else None)
    if not title:
        title = _clean(soup.title.string if soup.title else None)
    if not title:
        title = urlparse(identity.normalized_url).netloc
    abstract = _clean(description.get("content") if description else None)
    return (
        PaperMetadata(
            title=title,
            item_type=identity.item_type,
            canonical_url=HttpUrl(identity.normalized_url),
            abstract=abstract,
            source_kind="github" if identity.github_repo else "web",
            confidence=0.75,
        ),
        response.content,
        "text/html",
    )


def fetch_metadata_and_content(
    client: httpx.Client, identity: URLIdentity
) -> tuple[PaperMetadata, bytes | None, str | None, str | None]:
    if identity.arxiv_id:
        metadata = _arxiv_metadata(client, identity)
        pdf_response = client.get(str(metadata.pdf_url), timeout=90, follow_redirects=True)
        pdf_response.raise_for_status()
        return metadata, pdf_response.content, "application/pdf", str(metadata.pdf_url)
    metadata, content, media_type = _web_metadata(client, identity)
    return metadata, content, media_type, identity.normalized_url


def ingest_url(
    conn: Connection,
    settings: Settings,
    url: str,
    context: str | None = None,
    *,
    generate_embeddings: bool = True,
    candidate_item_id: str | None = None,
) -> dict:
    identity = identify_url(url)
    with httpx.Client(headers={"User-Agent": USER_AGENT}) as client:
        metadata, content, media_type, content_url = fetch_metadata_and_content(client, identity)
    if candidate_item_id:
        candidate = conn.execute(
            "SELECT id, work_id FROM research_items WHERE id = %s", (candidate_item_id,)
        ).fetchone()
    else:
        candidate = None
    duplicate = conn.execute(
        "SELECT id, work_id FROM research_items WHERE canonical_url = %s AND id <> coalesce(%s::uuid, gen_random_uuid())",
        (identity.normalized_url, candidate_item_id),
    ).fetchone()
    if not duplicate:
        for kind, value in (
            ("arxiv", identity.arxiv_id),
            ("doi", identity.doi),
            ("openreview", identity.openreview_id),
            ("github", identity.github_repo),
        ):
            if not value:
                continue
            duplicate = conn.execute(
                """
                SELECT ri.id, ri.work_id FROM source_identities si
                JOIN research_items ri ON ri.id = si.research_item_id
                WHERE si.identity_type = %s AND si.identity_value = %s
                  AND ri.id <> coalesce(%s::uuid, gen_random_uuid())
                """,
                (kind, value, candidate_item_id),
            ).fetchone()
            if duplicate:
                break
    if candidate and duplicate:
        conn.execute(
            """
            UPDATE research_items SET title = %s, abstract = coalesce(%s, abstract),
              authors = %s::jsonb, year = coalesce(%s, year), venue = coalesce(%s, venue),
              added_context = coalesce(%s, added_context), confidence = greatest(confidence, %s)
            WHERE id = %s
            """,
            (
                metadata.title,
                metadata.abstract,
                __import__("json").dumps(metadata.authors),
                metadata.year,
                metadata.venue,
                context,
                metadata.confidence,
                duplicate["id"],
            ),
        )
        conn.execute("DELETE FROM research_items WHERE id = %s", (candidate["id"],))
        conn.execute(
            "DELETE FROM works WHERE id = %s AND NOT EXISTS (SELECT 1 FROM research_items WHERE work_id = %s)",
            (candidate["work_id"], candidate["work_id"]),
        )
        conn.commit()
        upserted = UpsertedItem(duplicate["id"], duplicate["work_id"], False, True)
    elif candidate:
        conn.execute(
            """
            UPDATE research_items SET item_type = %s, title = %s, canonical_url = %s,
              abstract = %s, authors = %s::jsonb, year = %s, venue = %s,
              source_kind = %s, confidence = %s, added_context = coalesce(%s, added_context)
            WHERE id = %s
            """,
            (
                metadata.item_type.value,
                metadata.title,
                identity.normalized_url,
                metadata.abstract,
                __import__("json").dumps(metadata.authors),
                metadata.year,
                metadata.venue,
                metadata.source_kind,
                metadata.confidence,
                context,
                candidate_item_id,
            ),
        )
        conn.execute(
            "UPDATE works SET canonical_title = %s, abstract = %s, year = %s, venue = %s WHERE id = %s",
            (metadata.title, metadata.abstract, metadata.year, metadata.venue, candidate["work_id"]),
        )
        for kind, value in (
            ("arxiv", identity.arxiv_id),
            ("doi", identity.doi),
            ("openreview", identity.openreview_id),
            ("github", identity.github_repo),
            ("url", identity.normalized_url),
        ):
            if value:
                conn.execute(
                    """
                    INSERT INTO source_identities (research_item_id, identity_type, identity_value, is_primary)
                    VALUES (%s, %s, %s, %s) ON CONFLICT (identity_type, identity_value) DO NOTHING
                    """,
                    (candidate_item_id, kind, value, kind != "url"),
                )
        conn.commit()
        upserted = UpsertedItem(candidate["id"], candidate["work_id"], True, False)
    else:
        upserted = upsert_research_item(conn, metadata, identity, context)
    document_id = None
    embedded = 0
    if content and media_type:
        digest = sha256_bytes(content)
        suffix = ".pdf" if media_type == "application/pdf" else ".html"
        relative = Path("documents") / str(upserted.item_id) / f"{digest}{suffix}"
        absolute = settings.storage_dir / relative
        absolute.parent.mkdir(parents=True, exist_ok=True)
        if not absolute.exists():
            absolute.write_bytes(content)
        extracted = extract_pdf(absolute) if suffix == ".pdf" else extract_html(content)
        document_id = insert_document(
            conn,
            item_id=upserted.item_id,
            source_url=content_url or identity.normalized_url,
            media_type=media_type,
            storage_path=str(relative),
            extracted=extracted,
        )
        if generate_embeddings and settings.openai_api_key:
            embedded = embed_missing_chunks(conn, settings, document_id)
    conn.execute(
        "UPDATE research_items SET lifecycle_status = 'triaged' WHERE id = %s",
        (upserted.item_id,),
    )
    conn.commit()
    return {
        "researchItemId": str(upserted.item_id),
        "workId": str(upserted.work_id),
        "documentVersionId": str(document_id) if document_id else None,
        "created": upserted.created,
        "merged": upserted.merged,
        "embeddedChunks": embedded,
        "title": metadata.title,
        "itemType": metadata.item_type.value,
    }
