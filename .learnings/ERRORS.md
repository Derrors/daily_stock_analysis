## [ERR-20260417-001] openai-compatible-base-url-precedence

**Logged**: 2026-04-17T18:38:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
OpenAI-compatible key precedence was centralized, but default `openai_base_url` still looked at raw `AIHUBMIX_KEY` presence instead of the effective winning key source.

### Error
```
AssertionError: 'https://aihubmix.com/v1' is not None
```

### Context
- Operation attempted: pytest regression for config compatibility cleanup in Phase E.5
- Command: `.venv/bin/python -m pytest tests/test_config_env_compat.py tests/test_run_stock_analysis_script.py tests/test_agent_pipeline.py tests/test_analyzer_news_prompt.py`
- Trigger case: `OPENAI_API_KEYS` and `AIHUBMIX_KEY` were both set; keys resolved to `OPENAI_API_KEYS`, but `openai_base_url` still defaulted to `https://aihubmix.com/v1`

### Suggested Fix
Derive default OpenAI-compatible base URL from the same effective precedence chain as keys. Only inject `https://aihubmix.com/v1` when `AIHUBMIX_KEY` is the active winning source and `OPENAI_BASE_URL` is unset.

### Metadata
- Reproducible: yes
- Related Files: src/config.py, tests/test_config_env_compat.py, src/core/config_registry.py, .env.example
- See Also: none

### Resolution
- **Resolved**: 2026-04-17T18:39:00+08:00
- **Commit/PR**: pending
- **Notes**: Tightened `_resolve_openai_compatible_base_url()` so `OPENAI_API_KEYS` suppresses the AIHubmix default base URL unless `OPENAI_BASE_URL` is explicitly set.

---

## [ERR-20260417-002] project-doc-checks-should-use-venv-python

**Logged**: 2026-04-17T19:18:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tooling

### Summary
A quick doc-validation shell used bare `python`, but this project host environment does not expose `python`; validation should use the project virtualenv interpreter.

### Error
```
/bin/bash: line 1: python: command not found
```

### Context
- Operation attempted: lightweight validation while cleaning Phase E.7 docs
- Command: `python - <<'PY' ...`
- Trigger case: host shell only had project `.venv/bin/python` available

### Suggested Fix
For repo-local validation commands, prefer `.venv/bin/python` explicitly instead of assuming bare `python` exists on the host.

### Metadata
- Reproducible: yes
- Related Files: docs/CHANGELOG.md, docs/CONTRIBUTING_EN.md, TASKS.md
- See Also: TOOLS.md note about preferring project-local runtime environments when validating this repo

### Resolution
- **Resolved**: 2026-04-17T19:19:00+08:00
- **Commit/PR**: pending
- **Notes**: Re-ran the validation with `.venv/bin/python` and confirmed the rewritten `Unreleased` section no longer contains the retired doc/runtime cues.

---

## [ERR-20260417-003] pytest-target-file-name-mismatch

**Logged**: 2026-04-17T19:48:53+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
A targeted pytest command referenced a non-existent test file name (`tests/test_skill_aggregator.py`) instead of the repo's actual aggregator test file.

### Error
```
ERROR: file or directory not found: tests/test_skill_aggregator.py
```

### Context
- Operation attempted: targeted regression for `src/agent/memory.py` compat-wrapper cleanup
- Command: `.venv/bin/python -m pytest tests/test_agent_memory.py tests/test_skill_aggregator.py tests/test_base_agent.py`
- Trigger case: guessed the aggregator test filename instead of discovering the real file name first

### Suggested Fix
Before running targeted pytest on inferred filenames, resolve the actual test paths with `find tests` / `grep` and then run the matrix using the discovered file names.

### Metadata
- Reproducible: yes
- Related Files: tests/test_agent_memory.py, tests/test_agent_strategy_aggregator.py, tests/test_base_agent.py
- See Also: ERR-20260417-002

### Resolution
- **Resolved**: 2026-04-17T19:48:53+08:00
- **Commit/PR**: pending
- **Notes**: Switched to discovering the real aggregator test file name first (`tests/test_agent_strategy_aggregator.py`) before re-running the focused suite.

---

## [ERR-20260417-004] delete-first-wrapper-removal-broke-test-imports

**Logged**: 2026-04-17T21:22:30+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
After removing internal compat wrappers (`_is_code_like` / `_normalize_code`) from `name_to_code_resolver`, targeted tests still imported those private symbols and failed during collection.

### Error
```
ImportError: cannot import name '_is_code_like' from 'src.services.name_to_code_resolver'
```

### Context
- Operation attempted: delete-first cleanup of internal compatibility wrappers
- Command: `.venv/bin/python -m pytest tests/test_name_to_code_resolver.py tests/test_search_performance.py`
- Trigger case: tests were coupled to deleted private helper names

### Suggested Fix
When deleting compatibility wrappers, first check tests for private-symbol imports and migrate them to canonical utilities (`src.services.stock_code_utils`) in the same change.

### Metadata
- Reproducible: yes
- Related Files: src/services/name_to_code_resolver.py, tests/test_name_to_code_resolver.py
- See Also: ERR-20260417-003

### Resolution
- **Resolved**: 2026-04-17T21:23:30+08:00
- **Commit/PR**: pending
- **Notes**: Updated tests to import/use `is_code_like` and `normalize_code` directly; reran focused suite with 22 passed.

---
