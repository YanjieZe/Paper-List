# Golden-set evaluation protocol

The manifests define 30 distinct Research Items across all ten Robotics branches and 50 research questions. `paper-worker eval-contracts` validates cardinality, URL uniqueness, and branch coverage without spending API budget.

A release evaluation is intentionally separate and human-gated:

1. Import the 30 items into a clean evaluation database and resolve metadata conflicts.
2. Deep-read every item with the candidate model registry and retain all AgentRun usage/cost records.
3. Run all 50 questions with `library_and_web`; freeze artifacts before human scoring.
4. Two passes score metadata identity, unsupported key claims, EvidenceRef resolution, claim support, English-term preservation, and roadmap relation provenance.
5. Compute retrieval Recall@10 from a manually annotated relevance file. Do not substitute an LLM judge for the relevance labels.
6. Record model IDs, prompt/schema versions, Git SHA, corpus document SHAs, cost, and failures with the scorecard.

The release gate is the threshold block in `SPEC.md`. Merely passing `eval-contracts` is not a quality pass.
