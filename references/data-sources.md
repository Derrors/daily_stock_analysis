# Data Sources

## Runtime boundary

Current skill-first boundary keeps these sources:

### Market data
- Tushare

### News search
- Bocha
- Tavily
- Brave
- SerpAPI

### Market coverage
- A-shares (`cn`)
- Hong Kong stocks (`hk`)
- US stocks (`us`)

## Guidance

- Treat Tushare as the canonical runtime market-data provider.
- Treat search providers as optional enrichers, not hard dependencies for every call.
- Do not reintroduce removed legacy runtime fetchers into the new mainline unless the task explicitly requires it.
