# Phase J.4 Execution Plan - Compatibility Bridge Warning Window

## Goal

Execute a controlled deprecation window for `data_provider/*` compatibility bridge before any removal decision.

## Scope (this plan)

- Warning-window rollout steps
- Migration announcement template usage
- Final deletion gate checklist
- Rollback playbook

---

## Timeline (proposed)

### Week 0 - Preparation

- Ensure migration note is published: `references/provider-import-migration.md`
- Ensure compat-only boundary doc is published: `data_provider/README.md`
- Ensure anti-regression guard test is green.
- Prepare execution artifacts from templates:
  - `support/reports/templates/phase-j4-warning-window-log-template.md`
  - `support/reports/templates/phase-j4-blocker-register-template.md`
  - `support/reports/templates/phase-j4-go-no-go-template.md`

### Week 1 - Canary warnings on

- In canary/non-prod automation, set:

```bash
DSA_WARN_LEGACY_IMPORTS=1
```

- Or run the packaged check script:

```bash
bash scripts/check_legacy_import_window.sh
```

- Collect warning hits and source scripts.
- Open migration tickets for each hit.

### Week 2 - Broad non-prod rollout

- Enable warning flag in broader staging/test environments.
- Re-run key scheduled jobs and smoke scripts.
- Verify no critical failures caused by canonical imports.

### Week 3 - Freeze window

- Stop adding new exceptions.
- Re-audit open migration tickets.
- Confirm Tier-1 consumers have migration ETA/owner.

### Week 4 - Deletion readiness review

- Run deletion gate checklist (below).
- If any hard blocker remains, extend warning window by one cycle.

---

## Deletion gate checklist (must all pass)

- [ ] Internal repo imports remain canonical for >= 2 release cycles.
- [ ] No unresolved Tier-1 external callers still require `data_provider.*`.
- [ ] Warning-window evidence collected and reviewed.
- [ ] Migration note has been communicated for >= 1 full window.
- [ ] Rollback patch prepared and validated.

---

## Rollback plan

If removal causes import break:

1. Revert bridge deletion commit.
2. Re-enable warning-only mode (`DSA_WARN_LEGACY_IMPORTS=1`) and keep bridge active.
3. Publish incident note with exact failing import path and canonical replacement.
4. Re-enter warning window with updated consumer audit.

---

## Operational owners (fill during execution)

- Release owner: TBD
- Migration coordinator: TBD
- Downstream communication owner: TBD
- Rollback approver: TBD

---

## Exit criteria for J.4

- A complete warning-window cycle executed with evidence.
- Migration blockers triaged.
- Clear go/no-go decision recorded for bridge deletion candidate.

## Suggested artifact locations

- Window log: `support/reports/review/YYYY-MM-DD-phase-j4-warning-window-log.md`
- Blocker register: `support/reports/review/YYYY-MM-DD-phase-j4-blocker-register.md`
- Go/No-Go decision: `support/reports/review/YYYY-MM-DD-phase-j4-go-no-go.md`