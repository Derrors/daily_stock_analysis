# Provider Import Migration

## Canonical import path

Use:

- `src.stock_analysis_skill.providers.*`

Do not introduce new imports from:

- `data_provider.*`

`data_provider/*` is compatibility-only and scheduled for retirement after deprecation windows.

---

## Mapping examples

### Before

```python
from data_provider import DataFetcherManager
from data_provider.base import normalize_stock_code
from data_provider.tushare_fetcher import TushareFetcher
from data_provider.us_index_mapping import is_us_stock_code
```

### After

```python
from src.stock_analysis_skill.providers import DataFetcherManager
from src.stock_analysis_skill.providers.base import normalize_stock_code
from src.stock_analysis_skill.providers.tushare_fetcher import TushareFetcher
from src.stock_analysis_skill.providers.us_index_mapping import is_us_stock_code
```

---

## Diagnostic switch

When auditing legacy consumers, enable:

```bash
DSA_WARN_LEGACY_IMPORTS=1
```

This keeps compatibility behavior but emits deprecation warnings for legacy import edges.

---

## Retirement policy (summary)

- Bridge remains during migration window.
- New code must use canonical path.
- Bridge removal requires passing Phase J retirement gates (consumer audit + warning window + rollback readiness).