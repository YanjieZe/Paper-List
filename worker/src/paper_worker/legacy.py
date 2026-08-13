from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .schemas import LegacyRecord, LegacyScanReport
from .urls import identify_url

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
BARE_URL_RE = re.compile(r"(?<!\()https?://[^\s)>]+")


def scan_legacy(root: Path) -> LegacyScanReport:
    files = [root / "README.md", *sorted((root / "topics").glob("*.md"))]
    records: list[LegacyRecord] = []
    for path in files:
        if not path.exists():
            continue
        relative = str(path.relative_to(root))
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            urls = MARKDOWN_LINK_RE.findall(line)
            urls.extend(BARE_URL_RE.findall(MARKDOWN_LINK_RE.sub("", line)))
            for occurrence_index, raw_url in enumerate(urls):
                identity = identify_url(raw_url)
                records.append(
                    LegacyRecord(
                        source_file=relative,
                        line_number=line_number,
                        occurrence_index=occurrence_index,
                        raw_text=line,
                        url=raw_url,
                        normalized_url=identity.normalized_url,
                        detected_type=identity.item_type,
                        arxiv_id=identity.arxiv_id,
                    )
                )
    normalized_counts = Counter(record.normalized_url for record in records)
    type_counts = Counter(record.detected_type.value for record in records)
    return LegacyScanReport(
        discovered_urls=len(records),
        accounted_urls=len(records),
        unique_normalized_urls=len(normalized_counts),
        duplicate_occurrences=sum(count - 1 for count in normalized_counts.values()),
        by_type=dict(sorted(type_counts.items())),
        records=records,
    )


def persist_legacy_records(conn, report: LegacyScanReport) -> int:
    inserted = 0
    for record in report.records:
        result = conn.execute(
            """
            INSERT INTO migration_records (
              source_file, line_number, occurrence_index, raw_text, raw_url,
              normalized_url, detected_type, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'discovered')
            ON CONFLICT (source_file, line_number, occurrence_index) DO NOTHING
            RETURNING id
            """,
            (
                record.source_file,
                record.line_number,
                record.occurrence_index,
                record.raw_text,
                record.url,
                record.normalized_url,
                record.detected_type.value,
            ),
        ).fetchone()
        if result:
            inserted += 1
    conn.commit()
    return inserted


def _legacy_title(raw_text: str, normalized_url: str) -> str:
    matches = re.findall(r"\[([^\]]+)\]\(https?://[^)]+\)", raw_text)
    if matches:
        return re.sub(r"\s+", " ", matches[0]).strip()[:500]
    text = re.sub(r"https?://\S+", "", raw_text)
    text = re.sub(r"^[\s#*\-]+", "", text).strip(" ,:/")
    if text:
        return text[:500]
    return normalized_url


def import_legacy_catalog(conn, report: LegacyScanReport) -> dict[str, int]:
    persist_legacy_records(conn, report)
    item_by_url: dict[str, str] = {}
    imported = 0
    merged = 0
    for record in report.records:
        item_id = item_by_url.get(record.normalized_url)
        status = "merged"
        if not item_id:
            existing = conn.execute(
                "SELECT id FROM research_items WHERE canonical_url = %s", (record.normalized_url,)
            ).fetchone()
            if existing:
                item_id = str(existing["id"])
            else:
                title = _legacy_title(record.raw_text, record.normalized_url)
                base_slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:64]
                base_slug = base_slug or f"legacy-{imported + 1}"
                slug = base_slug
                suffix = 1
                while conn.execute("SELECT 1 FROM works WHERE slug = %s", (slug,)).fetchone():
                    suffix += 1
                    slug = f"{base_slug}-{suffix}"
                work = conn.execute(
                    "INSERT INTO works (canonical_title, slug) VALUES (%s, %s) RETURNING id",
                    (title, slug),
                ).fetchone()
                item = conn.execute(
                    """
                    INSERT INTO research_items (
                      work_id, item_type, title, canonical_url, source_kind,
                      confidence, lifecycle_status
                    ) VALUES (%s, %s, %s, %s, 'legacy', 0.5, 'candidate') RETURNING id
                    """,
                    (work["id"], record.detected_type.value, title, record.normalized_url),
                ).fetchone()
                item_id = str(item["id"])
                conn.execute(
                    """
                    INSERT INTO source_identities (
                      research_item_id, identity_type, identity_value, is_primary
                    ) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
                    """,
                    (
                        item_id,
                        "arxiv" if record.arxiv_id else "url",
                        record.arxiv_id or record.normalized_url,
                        bool(record.arxiv_id),
                    ),
                )
                imported += 1
            item_by_url[record.normalized_url] = item_id
            status = "imported"
        else:
            merged += 1
        conn.execute(
            """
            UPDATE migration_records SET status = %s, research_item_id = %s
            WHERE source_file = %s AND line_number = %s AND occurrence_index = %s
            """,
            (status, item_id, record.source_file, record.line_number, record.occurrence_index),
        )
        if record.source_file.startswith("topics/"):
            topic_slug = Path(record.source_file).stem.replace("_", "-")
            topic = conn.execute(
                """
                INSERT INTO topics (slug, name) VALUES (%s, %s)
                ON CONFLICT (slug) DO UPDATE SET name = excluded.name RETURNING id
                """,
                (topic_slug, Path(record.source_file).stem.replace("_", " ").title()),
            ).fetchone()
            conn.execute(
                """
                INSERT INTO research_item_topics (research_item_id, topic_id, source, confidence)
                VALUES (%s, %s, 'migration', 1)
                ON CONFLICT (research_item_id, topic_id) DO NOTHING
                """,
                (item_id, topic["id"]),
            )
    conn.commit()
    return {"items": imported, "mergedOccurrences": merged, "records": len(report.records)}
