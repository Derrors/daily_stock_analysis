# Phase J External Consumer Audit (`data_provider` compatibility bridge)

## Scope

This audit focuses on **externally visible** legacy import surfaces that can keep `data_provider.*` alive, even after internal code has migrated to:

- `src.stock_analysis_skill.providers.*`

The audit is repository-evidence-based (docs/scripts/tests/history). Unknown private downstream callers are marked separately.

---

## Executive Summary

- Internal code imports are already canonical (enforced by guard test).
- `data_provider/*` now acts as compat-only bridge.
- External risk still exists in historical usage patterns (notably top-level module import style and legacy patch paths in existing test/automation habits).

### Decision

- Mark **J.3 complete (repository-visible audit complete)**.
- Keep **J.4 pending** for warning-window execution and final deletion gate.

---

## Inventory of potential external consumers

| Surface | Evidence | Risk tier | Why it matters | Action |
|---|---|---|---|---|
| Legacy Python scripts importing `data_provider.*` | Compat bridge retained and documented | T1 | Most likely real-world break source once bridge is removed | Keep bridge during window; publish migration note |
| Direct module import via `sys.path` to `data_provider/` (e.g. `from us_index_mapping import ...`) | Existing compatibility scenario covered by tests | T1 | Bypasses package-style imports; easy to miss during retirement | Keep fallback import in shim modules until final gate |
| Ad-hoc notebooks / local automation | Not directly observable in repo | T2 | Common in quant workflows; import path inertia likely | Enable warning-window guidance (`DSA_WARN_LEGACY_IMPORTS=1`) |
| Internal CI / repo code | Guard test + grep clean | T3 (low) | Should not regress, but still needs enforcement | Keep `test_no_internal_data_provider_imports.py` gate |
| Historical docs / review artifacts | Plan/review docs contain legacy path references | T3 (low) | Informational only; not runtime entry | Keep as historical context; no runtime impact |

---

## Known risk edges

1. **Hidden Tier-1 callers outside repo**
   - We cannot enumerate private scripts from downstream users in this repo alone.
   - Removal without warning window may break unattended jobs.

2. **Top-level module import pattern**
   - Legacy style (`sys.path += data_provider`) is unusual but real; currently preserved by bridge fallback.

3. **String-based patch/reference usage**
   - Some tests/tools may refer to old dotted paths in monkeypatch strings.
   - Not always caught by simple import grep.

---

## Migration guidance produced in this phase

- New note: `references/provider-import-migration.md`
- Canonical replacement rule:
  - `data_provider.*` → `src.stock_analysis_skill.providers.*`

---

## J.4 prerequisites status

- [x] Internal imports clean and guarded.
- [x] External-facing migration note available.
- [x] Compat bridge behavior documented (`data_provider/README.md`).
- [ ] Warning-window evidence from downstream environments collected.
- [ ] Tier-1 downstream callers explicitly acknowledged migrated.

---

## Recommendation

Proceed with J.4 as a **windowed operational rollout**, not immediate code deletion:

1. Enable `DSA_WARN_LEGACY_IMPORTS=1` in canary/non-prod environments.
2. Collect and triage warning hits.
3. Confirm no unresolved Tier-1 callers.
4. Only then schedule bridge deletion candidate in a dedicated release gate.