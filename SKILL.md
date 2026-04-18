---
name: stock-analysis-skill
description: Agent-first stock and market analysis skill for A-shares, Hong Kong stocks, and US stocks. Use when an agent needs structured stock analysis, market review, strategy-based analysis, or reusable command-line execution for equity research. Supports unified request/response contracts, Tushare-backed market data, news-search-assisted workflows, and deterministic scripts.
---

# Stock Analysis Skill

Use this skill to run reusable stock and market analysis workflows for agents.

## Primary workflow

1. Start with a dry run to verify request normalization.
2. Run the stock / market / strategy script needed by the task.
3. Prefer structured responses for downstream chaining.
4. Render Markdown only when the agent needs a human-readable report.

## Executable entries

Run stock analysis request normalization:

```bash
python scripts/run_stock_analysis.py --stock 600519 --dry-run --pretty
```

Run market analysis request normalization:

```bash
python scripts/run_market_analysis.py --region cn --dry-run --pretty
```

Resolve a strategy resource:

```bash
python scripts/resolve_strategy.py 均线金叉 --pretty
```

## References to load when needed

- `references/package-layout.md` — read when you need to understand the package boundary.
- `references/contracts.md` — read when you need request/response fields.
- `references/data-sources.md` — read when checking runtime dependencies.
- `references/strategies.md` — read when mapping a user request to strategy YAML files.
- `references/output-format.md` — read when deciding how to return results.

## Package boundary

Treat these as the primary skill surface:

- `SKILL.md`
- `references/`
- `scripts/`
- `strategies/`
- `assets/`
- `src/stock_analysis_skill/`

Treat these as engineering/support surfaces, not default user-facing entrypoints:

- `docs/`
- `support/`
- `tests/`
- `data_provider/`

## Current runtime boundary

- market data: Tushare
- news search: Bocha / Tavily / Brave / SerpAPI
- markets: CN / HK / US
- report templates: `assets/templates/`

Do not assume API/Web/Docker fallback paths are part of the skill contract.
Prefer new code under `src/stock_analysis_skill/`.
