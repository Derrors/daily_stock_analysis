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

## [ERR-20260417-005] rename-alias-left-stale-base-class-reference

**Logged**: 2026-04-17T21:27:30+08:00
**Priority**: low
**Status**: resolved
**Area**: refactor

### Summary
When removing `LegacyStockAnalysisPipeline` alias naming, one class inheritance site still referenced the old symbol, causing import-time NameError during pytest collection.

### Error
```
NameError: name 'LegacyStockAnalysisPipeline' is not defined
```

### Context
- Operation attempted: naming cleanup in `stock_pipeline.py`
- Command: `.venv/bin/python -m pytest tests/test_task_queue_payload_contract.py tests/test_stock_analysis_skill_market_strategy.py tests/test_run_stock_analysis_script.py tests/test_agent_pipeline.py`
- Trigger case: top import alias updated, but `StockAnalysisSkillPipeline(...)` base class not updated in the same patch

### Suggested Fix
When renaming imported symbols, grep the full file for all symbol references (including class bases/type hints) before running tests.

### Metadata
- Reproducible: yes
- Related Files: src/stock_analysis_skill/runtime/stock_pipeline.py
- See Also: ERR-20260417-004

### Resolution
- **Resolved**: 2026-04-17T21:28:30+08:00
- **Commit/PR**: pending
- **Notes**: Updated class base to `StockAnalysisPipeline` and reran focused regression with 55 passed.

---

---

## [ERR-20260418-001] git-add-pathspec-stale-after-directory-move

**Logged**: 2026-04-18T12:41:00+08:00
**Priority**: low
**Status**: resolved
**Area**: git

### Summary
After moving `patch/`, `templates/`, `sources/`, and `reports/` into `assets/` / `support/`, an attempted `git add` still referenced the old `patch` path and failed with a pathspec error.

### Error
```
fatal: pathspec 'patch' did not match any files
```

### Context
- Operation attempted: stage the full Phase H repository-purification change set for commit
- Command: `git add ... patch ... && git commit ...`
- Trigger case: the staging command was composed before re-checking the moved directory paths

### Suggested Fix
After large directory moves, prefer `git status --short --untracked-files=all` or `git add -A` from repo root instead of hand-maintaining stale path lists.

### Metadata
- Reproducible: yes
- Related Files: assets/, support/, .gitignore
- See Also: ERR-20260417-003

### Resolution
- **Resolved**: 2026-04-18T12:42:00+08:00
- **Commit/PR**: pending
- **Notes**: Re-ran staging with `git add -A`, then committed the Phase H repository-shape change successfully.

---

## [ERR-20260418-002] provider-shim-star-import-breaks-private-test-symbols

**Logged**: 2026-04-18T12:56:00+08:00
**Priority**: low
**Status**: resolved
**Area**: compatibility

### Summary
During Phase I provider internalization, compatibility shim modules initially used `from ... import *`, which failed to expose private helper symbols used by tests (for example `_build_dividend_payload`).

### Error
```
ImportError: cannot import name '_build_dividend_payload' from 'data_provider.fundamental_adapter'
```

### Context
- Operation attempted: provider internalization targeted regression matrix
- Trigger case: shim module relied on wildcard import semantics that skip underscored names

### Suggested Fix
Use module-bridge shims (`__getattr__` forwarding to canonical module) instead of wildcard re-export when compatibility paths must preserve private/test-level symbol access.

### Resolution
- **Resolved**: 2026-04-18T12:58:00+08:00
- **Commit/PR**: pending
- **Notes**: Replaced shim modules with `__getattr__` bridge pattern and aligned two tests to canonical provider module patch/log paths.

---

## [ERR-20260418-003] host-python-missing-in-repo-automation

**Logged**: 2026-04-18T13:08:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tooling

### Summary
A bulk import-rewrite helper was first launched with bare `python`, but this host does not provide that binary for the project session.

### Error
```
/bin/bash: line 1: python: command not found
```

### Suggested Fix
Use `.venv/bin/python` (or `python3`) consistently for repo-local automation scripts.

### Resolution
- **Resolved**: 2026-04-18T13:08:00+08:00
- **Notes**: Re-ran the rewrite script with `.venv/bin/python`; replacement pass completed successfully.

---

## [ERR-20260418-004] compat-bridge-relative-import-breaks-top-level-legacy-module-load

**Logged**: 2026-04-18T13:17:00+08:00
**Priority**: low
**Status**: resolved
**Area**: compatibility

### Summary
Thin bridge modules used `from ._compat import alias_module`, which fails when a legacy module is imported as a top-level module file (without package context), e.g. via `sys.path`-based `from us_index_mapping import ...`.

### Error
```
ImportError: attempted relative import with no known parent package
```

### Suggested Fix
In shim modules, add fallback import path:
- first try relative (`from ._compat import ...`)
- fallback to absolute (`from data_provider._compat import ...`)

### Resolution
- **Resolved**: 2026-04-18T13:18:00+08:00
- **Notes**: Added fallback import in all `data_provider/*` shim modules and re-ran targeted + full regression.

---

## [ERR-20260418-005] shell-backtick-command-substitution-in-grep-pattern

**Logged**: 2026-04-18T13:33:00+08:00
**Priority**: low
**Status**: resolved
**Area**: shell

### Summary
A grep command used a pattern containing backticks (`` `pytest` ``) inside double quotes, which triggered shell command substitution unexpectedly.

### Error
```
/bin/bash: line 1: pytest: command not found
```

### Suggested Fix
When searching literals containing backticks, avoid unescaped backticks in double-quoted shell strings; use single quotes, escape backticks, or avoid matching that token directly.

### Resolution
- **Resolved**: 2026-04-18T13:33:00+08:00
- **Notes**: Switched to safer grep patterns without backticks and continued verification.

---

## [ERR-20260418-006] anti-legacy-import-guard-self-matched-its-own-pattern

**Logged**: 2026-04-18T13:47:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The new guard test for banning internal `data_provider` imports scanned itself and falsely failed.

### Error
```
AssertionError: Found internal legacy imports ... tests/test_no_internal_data_provider_imports.py
```

### Suggested Fix
When implementing static-scan guard tests, explicitly allowlist the guard file itself (and explicit compat tests) to avoid self-referential false positives.

### Resolution
- **Resolved**: 2026-04-18T13:48:00+08:00
- **Notes**: Added `tests/test_no_internal_data_provider_imports.py` to allowlist and re-ran targeted + full regression.
