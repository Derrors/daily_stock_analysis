# daily_stock_analysis

Agent-first **stock-analysis skill repository**.

This repository is being rewritten from a legacy multi-entry stock-analysis system into a skill-first codebase that only serves agents.

## Core capabilities
- single-stock analysis
- market review / market analysis
- strategy resolution from `strategies/*.yaml`
- structured request/response contracts
- deterministic markdown rendering
- agent-friendly scripts

## Primary entry scripts
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

## Quick checks

```bash
python scripts/doctor.py
python scripts/run_stock_analysis.py --stock 600519 --dry-run --pretty
python scripts/run_market_analysis.py --region us --dry-run --pretty
python scripts/resolve_strategy.py ma_golden_cross --pretty
```

## Runtime requirements
At minimum:
- `LITELLM_MODEL`
- one provider key such as `GEMINI_API_KEY`, `OPENAI_API_KEY`, `AIHUBMIX_KEY`, `DEEPSEEK_API_KEY`, or `ANTHROPIC_API_KEY`
- `TUSHARE_TOKEN` is strongly recommended for the market-data mainline

## Validation
The current minimal skill test suite is:

```bash
.venv/bin/python -m pytest \
  tests/test_stock_analysis_skill_contracts.py \
  tests/test_run_stock_analysis_entry.py \
  tests/test_stock_analysis_skill_market_strategy.py \
  tests/test_stock_analysis_skill_renderers.py
```

## Current migration status
- Phase A: done
- Phase B: done
- Phase C: minimal mainline done
- Phase D: structural slimming done
- Phase E: in progress (semantic alignment + compatibility-surface reduction)

This repository no longer treats FastAPI/Web/Docker as its primary product shape.
Current work is focused on naming alignment, report-output semantics, and shrinking compatibility-only runtime surfaces.
