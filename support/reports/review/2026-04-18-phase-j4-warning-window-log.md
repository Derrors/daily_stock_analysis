# Phase J.4 Warning Window Log

## Window meta
- Window ID: `J4-WIN-20260418-CANARY-01`
- Owner: coding-agent
- Start date: 2026-04-18
- End date: 2026-04-18
- Environments in scope: repo-local canary
- `DSA_WARN_LEGACY_IMPORTS` enabled: yes (via `scripts/check_legacy_import_window.sh`)

## Evidence commands
- `bash scripts/check_legacy_import_window.sh`

## Result summary
- Test outcome: **33 passed, 88 subtests passed**
- Warning summary: **5 deprecation warnings** (all from intentional legacy-path coverage tests)

## Warning hits summary
| Date | Environment | Script/Job | Legacy import path | Severity | Owner | ETA |
|---|---|---|---|---|---|---|
| 2026-04-18 | repo-local canary | check_legacy_import_window.sh | `us_index_mapping` top-level legacy alias | low | coding-agent | N/A (expected in compat test) |
| 2026-04-18 | repo-local canary | check_legacy_import_window.sh | `data_provider.base` | low | coding-agent | N/A (expected in compat test) |
| 2026-04-18 | repo-local canary | check_legacy_import_window.sh | `data_provider.tushare_fetcher` | low | coding-agent | N/A (expected in compat test) |
| 2026-04-18 | repo-local canary | check_legacy_import_window.sh | `data_provider` top-level import | low | coding-agent | N/A (expected in compat test) |

## Migration actions
- [x] Re-confirm canonical path guidance (`references/provider-import-migration.md`)
- [x] Keep anti-regression guard for internal imports (`tests/test_no_internal_data_provider_imports.py`)
- [ ] Collect real downstream (repo-external) warning evidence in staging/canary environments

## Residual risks
- Repo-local run cannot observe private downstream automation outside this repository.
- Go/no-go for bridge deletion cannot be concluded from this window alone.

## Sign-off
- Window owner: coding-agent
- Reviewer: pending
- Date: 2026-04-18
