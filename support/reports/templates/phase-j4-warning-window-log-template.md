# Phase J.4 Warning Window Log (Template)

## Window meta
- Window ID:
- Owner:
- Start date:
- End date:
- Environments in scope:
- `DSA_WARN_LEGACY_IMPORTS` enabled: yes/no

## Evidence commands
- `bash scripts/check_legacy_import_window.sh`
- Additional job commands:

## Warning hits summary
| Date | Environment | Script/Job | Legacy import path | Severity | Owner | ETA |
|---|---|---|---|---|---|---|
| YYYY-MM-DD | staging | xxx | data_provider.xxx | high/med/low | @owner | YYYY-MM-DD |

## Migration actions
- [ ] Open ticket(s) for each warning hit
- [ ] Confirm canonical replacement path
- [ ] Re-run job with warning flag
- [ ] Mark resolved with evidence link

## Residual risks
- 

## Sign-off
- Window owner:
- Reviewer:
- Date:
