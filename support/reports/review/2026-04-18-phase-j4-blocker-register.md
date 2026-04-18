# Phase J.4 Blocker Register

## Blockers

| ID | Consumer | Import path | Blocker type | Impact | Mitigation | Owner | Target date | Status |
|---|---|---|---|---|---|---|---|---|
| J4-BLK-001 | Unknown repo-external automation | `data_provider.*` (unknown exact path) | unresolved migration evidence | high | run warning-window in staging/non-prod and collect real hits | TBD | 2026-04-25 | open |
| J4-BLK-002 | Release governance owner not assigned | N/A | missing owner | medium | assign release owner + reviewer for Go/No-Go record | TBD | 2026-04-25 | open |

## Notes
- Current repo-local canary only proves internal migration safety and compat test behavior.
- External consumers still need explicit audit evidence before bridge-deletion decision.

## Exit criteria
- [ ] No unresolved high-impact blocker
- [ ] Tier-1 consumers all have migration owner + ETA
- [ ] All open blockers have workaround or rollback path
