# Phase G Compatibility Contraction Plan

Date: 2026-04-18
Project: `daily_stock_analysis`

## Goal

Shrink compatibility surfaces that are now real runtime/API contracts, not just wording.

## Classification

### Delete now

- Task queue top-level `legacy_result` response field.
  - Keep `result` as preferred/canonical payload for callers.
  - Keep `runtime_payload` as explicit raw runtime/storage payload.
  - Keep `unified_response` as canonical v2 response when available.
- Managed-env placeholder names using `__legacy_*`.
  - Replace generated placeholders with `__managed_env_*`.
  - Router/channel detection should exclude `__managed_env_*` placeholders.
- `AGENT_SKILL_AUTOWEIGHT` / `AGENT_STRATEGY_AUTOWEIGHT` runtime config surface.
  - Backtest-driven skill auto-weighting is not part of the skill-first runtime.
  - Remove dataclass field, resolver, registry entry, and example config.
- `RUN_IMMEDIATELY` as a config surface.
  - Schedule startup behavior should be controlled by `SCHEDULE_RUN_IMMEDIATELY` only.
  - Remove schedule fallback and registry/example exposure.

### Keep as explicit transition surface

- `runtime_payload` in task queue API responses.
  - It is the raw task/event storage payload and still useful for debugging and internal consumers.
- `provider` argument in `LLMToolAdapter.call_with_tools()` and `api_key` argument in `GeminiAnalyzer.__init__()`.
  - These are harmless constructor/call-site shims and do not affect runtime behavior.

### Keep as historical references

- CHANGELOG entries.
- Historical `docs/openclaw-skill-integration.md` REST/API compatibility reference.
- Tests that intentionally assert historical migration behavior where the behavior remains present.

## Rollback points

- Task payload contraction can be reverted by re-adding `legacy_result: self.result` to `TaskInfo.to_dict()`.
- Placeholder replacement can be reverted by switching generated placeholder tokens back to `__legacy_*` and restoring prefix checks.
- Config retirement can be reverted by restoring the removed dataclass fields, registry definitions, and env parsing.

## Validation matrix

- Task payload: `tests/test_task_queue_payload_contract.py`
- Managed-env placeholders / config validation: `tests/test_config_validate_structured.py`, `tests/test_agent_model_service.py`, `tests/test_llm_channel_config.py`
- Config retirement: `tests/test_config_env_compat.py`, `tests/test_config_registry.py`
- Script path sanity: `tests/test_run_stock_analysis_script.py`
