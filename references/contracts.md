# Contracts

## Canonical module

Use:

- `src.stock_analysis_skill.contracts`

`src.schemas` no longer re-exports the unified analysis contract. Import analysis request/response models directly from the canonical module.

## Core request

`AnalysisRequest`

Key fields:
- `stock`: raw input / resolved code / market / name
- `mode`: `quick | standard | deep | strategy | context_only`
- `strategy`: optional strategy id
- `features`: toggles for news / fundamental / market context / realtime / chip data
- `output`: format / language / verbosity
- `execution`: async / force_refresh / save_history / dry_run
- `context`: query source / original query / selection source

## Core response

`AnalysisResponse`

Key blocks:
- `stock`
- `decision`
- `trend`
- `intel`
- `dashboard`
- `evidence`
- `metadata`

## Additional skill-first contracts

- `MarketAnalysisRequest`
- `MarketAnalysisResponse`
- `StrategySpec`
- `StrategyResolutionResponse`

These support the new market-analysis and strategy-resolution mainline in `src.stock_analysis_skill`.

## Usage rule

Use the unified contract as the single semantic boundary for:
- scripts
- agent invocation
- future skill wrappers
- future tests

Do not introduce new parallel response shapes unless a migration layer is required.
