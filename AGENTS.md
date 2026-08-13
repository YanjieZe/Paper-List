# Paper-List Research OS engineering guide

## Product invariants

- PostgreSQL owns operational state; reviewed Markdown owns published knowledge.
- Never commit API keys, raw conversations, PDFs, agent traces, or unreviewed drafts.
- Human-edited review text is authoritative and must never be overwritten by an agent.
- Every factual claim about a method, metric, experiment, or limitation must carry an evidence reference.
- Git publication must be fast-forward only. Never force-push or silently rebase generated knowledge.
- Every legacy URL must finish in an auditable imported, merged, unresolved, or retryable-failure state.

## Commands

- `npm install`: install web dependencies.
- `uv sync --project worker --extra dev`: install worker dependencies.
- `npm run typecheck`: type-check the web app.
- `npm test`: run web tests.
- `uv run --project worker pytest`: run worker tests.
- `uv run --project worker paper-worker migrate`: apply database migrations.
- `uv run --project worker paper-worker legacy-scan --root .`: dry-run the legacy catalog.

## Verification

Run web type-check/tests/build and worker lint/tests before publishing code. Run the legacy scan and verify that its accounted URL count equals its discovered URL count.
