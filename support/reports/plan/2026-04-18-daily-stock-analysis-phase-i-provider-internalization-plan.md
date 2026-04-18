# Phase I Plan - Provider Layer Internalization

## Background
After Phase H, the repository already exposed a clear skill-package surface. The largest remaining non-core top-level runtime area was `data_provider/`.

## Goal
Internalize runtime provider implementations into the skill package so canonical imports are under `src.stock_analysis_skill.providers`, while preserving compatibility for legacy `data_provider.*` imports.

## Scope

### In scope
- Move provider implementation modules:
  - `data_provider/base.py`
  - `data_provider/fundamental_adapter.py`
  - `data_provider/realtime_types.py`
  - `data_provider/tushare_fetcher.py`
  - `data_provider/us_index_mapping.py`
  - `data_provider/__init__.py`
  into `src/stock_analysis_skill/providers/`.
- Convert `data_provider/*` into compatibility shim modules.
- Update skill canonical imports where applicable.
- Update README / SKILL / references / docs wording.

### Out of scope
- Full removal of `data_provider/` path.
- Rewriting all repo imports in one shot.

## Canonical vs Compatibility
- Canonical runtime path: `src.stock_analysis_skill.providers`
- Compatibility path: `data_provider` (shim only)

## Risks and mitigations
- **Risk**: legacy tests/importers break due to path move.
  - **Mitigation**: keep full module-level shim coverage in `data_provider/*`.
- **Risk**: private helper import breakage (e.g. `_TushareHttpClient`).
  - **Mitigation**: explicitly re-export private symbols needed by tests from shim modules.

## Validation matrix
- Provider-focused tests:
  - `tests/test_fundamental_adapter.py`
  - `tests/test_realtime_types.py`
  - `tests/test_tushare_fetcher_followups.py`
  - `tests/test_tushare_fetcher_get_stock_list.py`
  - `tests/test_tushare_fetcher_http_client.py`
  - `tests/test_fundamental_context.py`
- Skill/runtime tests:
  - `tests/test_stock_analysis_skill_market_strategy.py`
  - `tests/test_run_stock_analysis_script.py`
- Full regression:
  - `pytest -q`

## Acceptance criteria
- Canonical provider implementation is under `src/stock_analysis_skill/providers/`.
- Legacy `data_provider.*` imports remain executable.
- Targeted provider matrix passes.
- Full test suite remains green.
