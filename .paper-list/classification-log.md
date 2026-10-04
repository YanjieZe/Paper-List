# Paper classification log

<!-- paper-classifier-baseline: a6f4894567d0fa7cab3f93747ca2aa6fdb0bf4fb -->

All entries present in `README.md` at the baseline commit are intentionally treated as already seen. Future classification runs append their decisions below; existing paper lists remain unchanged.

## Runs

## 2026-10-03 — full reorganization (user-requested)

- Classified every README inbox entry (≈650) into `topics/*.md`; new entries sit under `## Added from README inbox` (or topic-specific sections), newest first as ordered in README.
- New topics created by explicit user request: `self_improving_robots_agents.md`, `world_action_models.md`, `human_video_to_robot.md` (seeded and sectioned).
- Seeded `self_improving_robots_agents.md` with four papers from the 2026-10-03 arXiv scan that are not in README: InterEvolve (2610.02196), DynaHarness (2609.40306), Recova (2610.01178), Failure-Bank Self-Evolution for VLAs (2609.39820).
- README `Topics` index rewritten; the 21 newest inbox lines were sorted by arXiv ID. Exact duplicate lines inside topic files were removed.
- Classification was keyword-assisted plus manual overrides; some borderline placements (e.g. generic RL vs. visual imitation) may deserve review.

## 2026-10-04 — daily scan

### Classified
- [Magic-W0](https://arxiv.org/abs/2609.39870) → `topics/world_action_models.md` / `World-action models (WAM)`
- [Dream4ACT](https://arxiv.org/abs/2609.40153) → `topics/world_action_models.md` / `World-action models (WAM)`
