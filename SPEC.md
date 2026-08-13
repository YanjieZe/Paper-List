# Paper-List Research OS v1

Paper-List is a single-user Robotics research cognition system. A research question should produce a Chinese-first explanation with preserved English terminology, a navigable field map, key Research Items, evolutionary relationships, and evidence that resolves to source pages or sections.

## Sources of truth

- PostgreSQL owns Research Item identity, Work aggregation, jobs, reviews, conversations, merge history, notifications, and search projections.
- Reviewed Markdown owns published notes, roadmap narratives, taxonomy, and approved personal conclusions.
- Private versioned PDF/HTML snapshots own primary evidence.

## Publication boundary

Reviewed knowledge may be public. API keys, PDFs, raw conversations, unreviewed drafts, worker logs, and model traces are never written to Git. Git publication is performed in a temporary worktree and is fast-forward only.

## Research object model

A `Work` groups the official manifestations of one research effort. A `ResearchItem` is a separately readable paper, blog, article, project page, repository, dataset, benchmark, or collection. Independent commentary remains a separate Item linked to the Work it explains or critiques.

## User workflow

1. Paste a URL or ask a research question.
2. The system creates a durable background job and streams progress.
3. New sources are normalized, versioned, indexed, classified, and placed in Inbox.
4. Deep-reading outputs are divided into independently reviewable sections.
5. Accepted or edited sections render to Markdown and are committed/pushed to `main`.
6. Related roadmaps become stale and receive a reviewable update draft.

## Evidence contract

Claims are typed as `fact`, `inference`, or `personal`. Factual method, metric, experiment, and limitation claims require at least one `EvidenceRef` containing a document version plus a page, section, figure, or table locator. Inference must be visibly labeled. Human-authored personal text is immutable to agents.

## Completion definition

v1 is complete only when every legacy URL is accounted for, the end-to-end ingest/research/review/Git/roadmap loop works, evidence and retrieval evals pass, production backup can be restored, and API cost/failure state is observable.
