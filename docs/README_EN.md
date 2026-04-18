# daily_stock_analysis

Agent-first **stock-analysis skill package repository**.

This repository has been rewritten from a legacy multi-entry stock-analysis system into a skill-centered package whose primary surface is:

- `SKILL.md`
- `references/`
- `scripts/`
- `strategies/`
- `assets/`
- `src/stock_analysis_skill/`

## Core skill capabilities
- single-stock analysis
- market review / market analysis
- strategy resolution from `strategies/*.yaml`
- structured request/response contracts
- deterministic markdown rendering
- agent-friendly scripts

## Primary package surface
- `SKILL.md`
- `references/package-layout.md`
- `references/contracts.md`
- `scripts/run_stock_analysis.py`
- `scripts/run_market_analysis.py`
- `scripts/resolve_strategy.py`
- `scripts/doctor.py`

## Canonical modules
- `src.stock_analysis_skill.contracts`
- `src.stock_analysis_skill.service`
- `src.stock_analysis_skill.analyzers.stock`
- `src.stock_analysis_skill.analyzers.market`
- `src.stock_analysis_skill.analyzers.strategy`
- `src.stock_analysis_skill.renderers.markdown`

## Secondary engineering/support surface
These paths still exist, but they are not the first place a new skill consumer should look:
- `docs/`
- `support/`
- `tests/`
- `data_provider/` (legacy import shim; canonical provider modules now live under `src/stock_analysis_skill/providers/`; see `data_provider/README.md`)

## Assets and support layout
- `assets/templates/` — Jinja2 report templates
- `assets/media/` — media, screenshots, brand assets
- `support/reports/` — planning/review artifacts
- `support/patch/` — historical patch utilities

## Quick checks

```bash
python scripts/doctor.py
python scripts/run_stock_analysis.py --stock 600519 --dry-run --pretty
python scripts/run_market_analysis.py --region us --dry-run --pretty
python scripts/resolve_strategy.py ma_golden_cross --pretty
bash scripts/check_legacy_import_window.sh
```

## Runtime requirements
At minimum:
- `LITELLM_MODEL`
- one provider key such as `GEMINI_API_KEY`, `OPENAI_API_KEY`, `AIHUBMIX_KEY`, `DEEPSEEK_API_KEY`, or `ANTHROPIC_API_KEY`
- `TUSHARE_TOKEN` is strongly recommended for the market-data mainline
- `REPORT_TEMPLATES_DIR` defaults to `assets/templates`

## Validation
The current minimal skill test suite is:

```bash
.venv/bin/python -m pytest \
  tests/test_stock_analysis_skill_contracts.py \
  tests/test_run_stock_analysis_entry.py \
  tests/test_stock_analysis_skill_market_strategy.py \
  tests/test_stock_analysis_skill_renderers.py
```

## Current status
- Phase A: done
- Phase B: done
- Phase C: minimal mainline done
- Phase D: structural slimming done
- Phase E: semantic alignment + compatibility-surface reduction completed
- Phase F: mainline internalization and contract regression completed
- Phase G: compatibility contraction completed
- Phase H: first-pass skill-package purification completed

This repository no longer treats FastAPI/Web/Docker as its product shape.
Current work is focused on keeping the primary skill surface obvious while pushing engineering support material to the background.

## Historical references
REST/API-oriented integration notes such as `docs/openclaw-skill-integration.md` remain as historical compatibility references only, not the current mainline recommendation.

For legacy provider import migration, see `references/provider-import-migration.md` and `data_provider/README.md`.
