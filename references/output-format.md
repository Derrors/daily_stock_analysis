# Output Format Guidance

## Primary rule

Return structured data first.

Preferred order:
1. `AnalysisResponse` object
2. JSON serialized response
3. Markdown or summary rendering for agent display

## Output modes

Current contract supports:
- `dashboard`
- `summary`
- `context`
- `markdown`

## Agent-facing recommendation

- Use structured response for downstream chaining.
- Use Markdown only when the agent needs a human-readable report.
- Keep transport-specific product payloads out of the new skill boundary.
