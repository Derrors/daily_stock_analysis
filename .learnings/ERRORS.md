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
