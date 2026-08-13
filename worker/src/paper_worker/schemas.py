from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator

Probability = Annotated[float, Field(ge=0, le=1)]


class ItemType(StrEnum):
    PAPER = "paper"
    BLOG = "blog"
    ARTICLE = "article"
    PROJECT = "project"
    REPOSITORY = "repository"
    DATASET = "dataset"
    BENCHMARK = "benchmark"
    COLLECTION = "collection"


class ClaimKind(StrEnum):
    FACT = "fact"
    INFERENCE = "inference"
    PERSONAL = "personal"


class EvidenceRef(BaseModel):
    document_version_id: UUID | None = None
    url: HttpUrl | None = None
    source_title: str | None = None
    page: int | None = Field(default=None, ge=1)
    section: str | None = None
    figure: str | None = None
    table: str | None = None
    quote: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def has_locator(self) -> EvidenceRef:
        if not self.document_version_id and not self.url:
            raise ValueError("an evidence reference requires a document version or URL")
        if self.document_version_id and not any((self.page, self.section, self.figure, self.table)):
            raise ValueError("a document evidence reference requires a locator")
        return self


class Claim(BaseModel):
    text: str = Field(min_length=1)
    kind: ClaimKind
    evidence: list[EvidenceRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def facts_need_evidence(self) -> Claim:
        if self.kind == ClaimKind.FACT and not self.evidence:
            raise ValueError("factual claims require evidence")
        return self


class PaperMetadata(BaseModel):
    title: str
    item_type: ItemType
    canonical_url: HttpUrl
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    year: int | None = Field(default=None, ge=1800, le=2200)
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    openreview_id: str | None = None
    pdf_url: HttpUrl | None = None
    topics: list[str] = Field(default_factory=list)
    source_kind: str
    confidence: float = Field(ge=0, le=1)


class CatalogResult(BaseModel):
    research_item_id: UUID
    topics: list[str]
    value_judgment: str
    why_relevant: str
    recommended_depth: Literal["skip", "skim", "standard", "deep"]
    confidence: Probability


class CriticFinding(BaseModel):
    section_key: str
    severity: Literal["info", "warning", "error"]
    finding: str
    suggested_fix: str | None = None


class CriticReport(BaseModel):
    approved: bool
    findings: list[CriticFinding]
    unsupported_claims: list[str]


class LinkerResult(BaseModel):
    relations: list[RelationCandidate]


class RoadmapSectionDraft(BaseModel):
    key: str
    title: str
    markdown: str
    claims: list[Claim] = Field(default_factory=list)


class RoadmapDraft(BaseModel):
    roadmap_slug: str
    sections: list[RoadmapSectionDraft]


class TutorResponse(BaseModel):
    short_answer: str
    intuition: str
    technical_detail: str
    checks_for_understanding: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)


class ReadingSection(BaseModel):
    key: str
    title: str
    markdown: str
    claims: list[Claim] = Field(default_factory=list)
    required: bool = True


class ReadingNoteDraft(BaseModel):
    research_item_id: UUID
    title: str
    language: Literal["zh-en"] = "zh-en"
    sections: list[ReadingSection]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    schema_version: int = 1


class RelationCandidate(BaseModel):
    source_work_id: UUID
    target_work_id: UUID
    relation_type: Literal[
        "builds_on",
        "extends",
        "contrasts_with",
        "evaluates",
        "explains",
        "implements",
        "uses_dataset",
        "critiques",
        "reproduces",
    ]
    rationale: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ResearchAnswer(BaseModel):
    conclusion: str
    explanation_markdown: str
    claims: list[Claim]
    related_item_ids: list[UUID] = Field(default_factory=list)
    external_candidates: list[str] = Field(default_factory=list)


class JobPayload(BaseModel):
    type: Literal[
        "ingest_url",
        "deep_read",
        "research",
        "publish_review",
        "reindex_markdown",
        "refresh_roadmap",
    ]
    data: dict


class LegacyRecord(BaseModel):
    source_file: str
    line_number: int
    occurrence_index: int = 0
    raw_text: str
    url: str
    normalized_url: str
    detected_type: ItemType
    arxiv_id: str | None = None


class LegacyScanReport(BaseModel):
    discovered_urls: int
    accounted_urls: int
    unique_normalized_urls: int
    duplicate_occurrences: int
    by_type: dict[str, int]
    records: list[LegacyRecord]
