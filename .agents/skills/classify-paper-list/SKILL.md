---
name: classify-paper-list
description: Classify papers newly added to Paper-List README.md into the repository's Markdown topic files. Use when the user asks to organize, sort, classify, or maintain new papers, says "整理新 papers", or asks whether the topic taxonomy needs a new topic or subsection.
---

# Classify Paper List

Keep `README.md` as the chronological inbox and `topics/*.md` as curated views. Do not introduce a database, service, generated summary, or background automation.

## Workflow

1. Read `.paper-list/classification-log.md` and `references/topic-policy.md` completely.
2. Run `python3 .agents/skills/classify-paper-list/scripts/find_new_papers.py --repo . --pretty`.
3. If there are no candidates, report that the inbox is current and make no content edits.
4. For every candidate, open the linked primary source and establish the actual research problem, method, embodiment, and paper identity. Prefer arXiv, OpenReview, publisher pages, official project pages, and official repositories. Do not classify from the title alone when it is ambiguous.
5. Check every existing topic filename and relevant headings before choosing a destination. A paper may enter at most two topics when the two views are materially different.
6. Apply the decision rules in `references/topic-policy.md`:
   - Add clear matches directly to existing topic files.
   - Add a subsection only when the policy threshold is met.
   - Record a proposed new topic and ask for approval; never create one silently.
   - Keep unresolved topic proposals out of `misc.md` unless the user rejects the proposal or explicitly asks for a fallback.
7. Copy the original README bullet verbatim into the chosen topic section unless a minimal formatting repair is necessary. Never remove, reorder, or rewrite the source entry in README.
8. Avoid duplicate paper identities by checking arXiv ID, DOI, OpenReview ID, canonical URL, and normalized title across all topic files.
9. Append one concise run entry to `.paper-list/classification-log.md`, including every classified, pending, or skipped candidate. Preserve the baseline marker and remove the `No classification runs yet.` placeholder on the first run.
10. Review the diff. Do not commit or push unless the user asks.

## Guardrails

- Treat the baseline commit as already seen; do not backfill historical README entries unless requested.
- Preserve existing taxonomy and prose outside the lines needed for the current batch.
- Do not invent metadata, venues, dates, topic fit, or paper relationships.
- Treat project pages and repositories as aliases of a paper when they describe the same work.
- Skip conference indexes, generic collections, products, and blog posts unless the user explicitly wants them in a research topic.
- Surface ambiguous classifications with a short reason instead of guessing.

## Run log format

Append:

```markdown
## YYYY-MM-DD — source `<git HEAD>`

### Classified
- [Paper title](primary URL) → `topics/example.md` / `Subsection`

### Topic proposals
- `proposed-topic`: scope; seed papers; why existing topics are insufficient — pending approval

### Skipped or unresolved
- [Item](URL) — reason
```

Omit empty subsections. Log each candidate exactly once so the detector does not offer it again unless the user requests reprocessing.
