# Phase J Draft - `data_provider` Compatibility Bridge Retirement

## Background

Phase I has completed provider internalization:

- Canonical provider runtime path: `src.stock_analysis_skill.providers`
- Legacy path retained as compatibility bridge: `data_provider/*`
- Internal repository imports have already migrated to canonical paths.

Current state is stable, but bridge removal still needs an explicit, low-risk retirement plan.

---

## Goal

Retire `data_provider/*` compatibility bridges in a controlled way without breaking external consumers.

---

## Non-goals

- No immediate bridge deletion in this phase
- No behavior changes to provider runtime logic
- No forced migration for unknown external callers without warning window

---

## Migration principles

1. **Canonical-first**: all new code must import from `src.stock_analysis_skill.providers.*`.
2. **Bridge is compatibility-only**: no business logic is allowed under `data_provider/*`.
3. **Observable deprecation**: legacy usage must be measurable before deletion.
4. **Gate-based removal**: delete only when objective gates are met.

---

## Proposed milestones

### J.1 Inventory & contract freeze

- Freeze canonical public provider surface under `src.stock_analysis_skill.providers`.
- Confirm `data_provider/*` is only alias/compat glue.
- Keep CI check to prevent new internal legacy imports.

**Exit criteria**
- No internal `data_provider.*` imports except explicit compat tests.
- Canonical exports documented.

### J.2 Legacy usage observability

- Keep `DSA_WARN_LEGACY_IMPORTS` switch.
- Add rollout guidance for enabling warnings in non-prod / canary environments.
- Collect legacy import evidence from user bug reports / integration logs.

**Exit criteria**
- At least one release window with warning-enabled validation.
- No critical regressions attributed to canonical provider path.

### J.3 External consumer audit

- Enumerate known external entrypoints (scripts, docs snippets, downstream automation).
- Publish migration note: `data_provider.* -> src.stock_analysis_skill.providers.*`.
- Track unresolved external references.

**Exit criteria**
- Known consumer list audited and migration guidance delivered.
- No unresolved Tier-1 consumer blocked on legacy path.

### J.4 Soft enforcement

- Optional: escalate warning strategy for legacy imports in CI/dev (still non-breaking).
- Keep runtime compatibility in released versions.

**Exit criteria**
- Bridge remains behaviorally stable.
- Migration pressure is visible but controlled.

### J.5 Removal decision gate

Bridge deletion can only start when all are true:

- Internal imports remain clean for >= 2 release cycles.
- External consumer audit has no unresolved Tier-1 blockers.
- Migration note has been available for >= 1 full deprecation window.
- Final rollback plan is documented.

---

## Risk matrix

### Risk A: hidden external scripts still import `data_provider.*`

- **Impact**: runtime import break after deletion
- **Mitigation**: warning window + consumer audit + phased communication

### Risk B: drift re-introduces internal legacy imports

- **Impact**: canonical path consistency regresses
- **Mitigation**: CI guard test to fail on internal legacy imports

### Risk C: compatibility expectations around private symbols

- **Impact**: niche tests/tools break unexpectedly
- **Mitigation**: keep alias bridge behavior and targeted compat tests until final removal gate

---

## Rollback strategy

If a post-removal import break occurs:

1. Re-introduce thin alias bridge modules from release branch patch.
2. Re-enable warning-only mode for one additional cycle.
3. Update migration note with concrete breakage case and fix path.

---

## Deliverables (Phase J draft scope)

- This plan document
- CI/pytest guard for "no new internal `data_provider.*` imports"
- TASKS/README references aligned to Phase J as planned next step

---

## Decision

Phase J is a **governance + deprecation management** phase, not a behavior-rewrite phase.

The compatibility bridge should remain until objective retirement gates are satisfied.