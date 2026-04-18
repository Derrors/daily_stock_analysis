---
name: "stock-analysis"
description: "Analyzes single stocks, market reviews, and strategy resources through the repository skill contracts. Invoke when users ask for stock analysis, market review, strategy lookup, or skill-surface changes."
---

# Stock Analysis

Use this skill when the user asks for stock analysis, market review, strategy lookup, or requests changes to the repository's stock-analysis skill surface.

## Scope

- Single-stock analysis through the canonical `AnalysisRequest` / `AnalysisResponse` contract
- Market review through the canonical market-analysis contract
- Strategy resolution through `strategies/*.yaml`
- Skill-first architecture changes around `src/stock_analysis_skill/`, `scripts/`, and related runtime assets

## Canonical Paths

- Skill entry: `.trae/skills/stock-analysis/SKILL.md`
- Service facade: `src.stock_analysis_skill.service`
- Contracts: `src.stock_analysis_skill.contracts`
- Stock runtime: `src.stock_analysis_skill.runtime`
- Providers: `src.stock_analysis_skill.providers`
- Scripts: `scripts/run_stock_analysis.py`, `scripts/run_market_analysis.py`, `scripts/resolve_strategy.py`

## Working Rules

- Prefer the skill-first boundary under `src/stock_analysis_skill/`.
- Reuse existing contracts, scripts, tests, and providers before introducing new layers.
- Keep structured response contracts as the primary output; use Markdown only as a renderer.
- When changing user-visible behavior or skill assets, update the relevant repository docs.

## Recommended Workflow

1. Read `.trae/skills/stock-analysis/SKILL.md`.
2. Confirm whether the request touches contracts, runtime, providers, adapters, or docs.
3. Prefer changes that tighten the skill boundary instead of expanding legacy paths.
4. Validate with the smallest relevant test matrix first, then run broader checks when needed.

## Key Validation

- `python scripts/check_ai_assets.py` for skill and governance assets
- `python -m py_compile <changed_python_files>` for Python syntax checks
- `./scripts/ci_gate.sh` for broader backend validation when code changes are substantial

## Migration Bias

- Move logic toward `src/stock_analysis_skill/`
- Downgrade legacy modules to shims before deletion
- Keep migration steps reversible until the new canonical path is fully covered by tests
