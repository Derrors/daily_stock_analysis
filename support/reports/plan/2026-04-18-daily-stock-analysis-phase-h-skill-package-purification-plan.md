# Phase H Skill Package Purification Plan

Date: 2026-04-18
Project: `daily_stock_analysis`

## Goal

Push the repository from a skill-first engineering repo toward a purer skill-package shape without breaking the working runtime.

## Classification

### Keep as top-level skill core

- `SKILL.md`
- `references/`
- `scripts/`
- `src/stock_analysis_skill/`
- `strategies/`
- `tests/`
- `data_provider/` (runtime dependency layer; not safe to move in this phase)

### Down-rank from top-level visibility now

- `templates/` -> `assets/templates/`
  - They are output assets, not top-level skill navigation content.
- `sources/` -> `assets/media/`
  - They are media/branding/sample assets.
- `reports/` -> `support/reports/`
  - They are planning/review artifacts, not current skill usage surface.
- `patch/` -> `support/patch/`
  - Historical patch utilities belong in support space, not the skill root.

### Keep in place for now

- `docs/`
  - Still heavily cross-linked and useful as human-facing supplemental docs.
  - In this phase it will be de-emphasized in README/SKILL rather than moved.
- `.github/`
  - Repo automation; not part of runtime surface but harmless.

## Scope of Phase H implementation

1. Move top-level assets/support directories to lower-visibility homes.
2. Update runtime/config defaults impacted by the moves.
3. Rewrite README / SKILL / references to emphasize the skill package surface.
4. Run targeted and full regression validation.

## Explicit non-goals for this phase

- Moving `data_provider/` into `src/stock_analysis_skill/`.
- Rebuilding the entire docs system.
- Collapsing the repository into a minimal one-skill template.

## Rollback points

- Restore moved directories from git history if runtime/document links break.
- Revert `report_templates_dir` default if report rendering path assumptions fail.

## Validation matrix

- Report rendering / config path: `tests/test_report_renderer.py`, `tests/test_config_registry.py`, `tests/test_config_env_compat.py`
- Script entry sanity: `tests/test_run_stock_analysis_script.py`, `tests/test_run_stock_analysis_entry.py`
- Skill runtime: `tests/test_stock_analysis_skill_contracts.py`, `tests/test_stock_analysis_skill_market_strategy.py`, `tests/test_stock_analysis_skill_renderers.py`
- Full regression: `pytest -q`
