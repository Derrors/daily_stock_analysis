# Strategies

## Current strategy resource layer

Use files under:

- `strategies/*.yaml`

Examples include:
- `ma_golden_cross.yaml`
- `bull_trend.yaml`
- `chan_theory.yaml`
- `wave_theory.yaml`

## Guidance

- Treat strategy YAML files as reusable analysis resources.
- Keep strategy resolution separate from product-shell logic.
- Prefer explicit strategy ids in agent requests when the user asks for a specific analytical style.
