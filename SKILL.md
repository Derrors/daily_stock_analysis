---
name: stock-analysis-skill
description: Agent-first stock and market analysis skill for A-shares, Hong Kong stocks, and US stocks. Use when the agent needs structured stock analysis, market review, strategy-based analysis, or reusable command-line execution for equity research. Supports unified request/response contracts, Tushare-backed market data, and news-search-assisted analysis workflows.
---

# Stock Analysis Skill

Use this skill to run reusable stock analysis workflows for agents.

## Start with the executable entry

Run the stock analysis entry script:

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

Use `--dry-run` first when checking normalized request payloads.

## Use the unified contract

Read `references/contracts.md` when you need the request/response structure.

Prefer the unified contract for:
- single-stock analysis
- strategy-scoped analysis
- agent-to-script invocation
- future market-analysis script alignment

## Use the current data-source boundary

Read `references/data-sources.md` when checking runtime dependencies.

Current boundary:
- market data: Tushare
- news search: Bocha / Tavily / Brave / SerpAPI
- markets: CN / HK / US

Do not assume legacy API/Web fallback paths are part of the new skill contract.

## Use strategy resources

Read `references/strategies.md` when mapping a request to strategy YAML files.

Treat `strategies/*.yaml` as the current strategy resource layer.

## Use output guidance

Read `references/output-format.md` when deciding how to return results to an agent.

Prefer structured response first, then Markdown/summary rendering as a secondary output form.

## Migration note

This repository is being rewritten toward a skill-first shape.

Prefer new code under `src/stock_analysis_skill/`.
Treat legacy `api/`, `server.py`, and product-shell modules as migration debt unless the current task explicitly requires them.
