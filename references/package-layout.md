# Package Layout

## Primary skill surface

Treat these paths as the primary skill package boundary:

- `SKILL.md`
- `references/`
- `scripts/`
- `strategies/`
- `assets/`
- `src/stock_analysis_skill/`

## Secondary engineering/support surface

These paths still exist for maintenance and validation, but they are not the first place a new skill consumer should look:

- `docs/` — supplemental human-facing docs
- `support/` — planning notes, review artifacts, historical patch utilities
- `tests/` — regression and contract validation
- `data_provider/` — runtime data-access layer retained outside `src/stock_analysis_skill/` in this phase

## Asset layout

- `assets/templates/` — Jinja2 report templates
- `assets/media/` — images, branding files, screenshots, sample media

## Guidance

When documenting or integrating this repository, present the primary skill surface first.
Use support/engineering paths only when the task explicitly requires implementation history, CI workflow details, or debugging collateral.
