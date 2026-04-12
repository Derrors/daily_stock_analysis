# -*- coding: utf-8 -*-
"""Unified CLI/script entry for stock analysis.

This script is the first concrete executable brick for the future
`stock-analysis-core` skill. It consumes the unified AnalysisRequest contract
and returns the unified AnalysisResponse contract as JSON.

Current implementation is intentionally conservative:
- reuses the existing AnalysisService
- defaults to NO notification side effects
- supports both CLI flags and JSON request input
- keeps report-type mapping minimal while v2 refactor is still in progress
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

# Ensure project root is importable when running via `python scripts/...`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_config  # noqa: E402
from src.schemas.analysis_contract import (  # noqa: E402
    AnalysisContextMeta,
    AnalysisExecution,
    AnalysisFeatures,
    AnalysisMode,
    AnalysisOutput,
    AnalysisRequest,
    OutputFormat,
    OutputVerbosity,
    QuerySource,
    SelectionSource,
    StockTarget,
)
from src.services.analysis_service import AnalysisService  # noqa: E402
from src.utils.analysis_runtime_contract import build_full_analysis_preflight_error  # noqa: E402


MODE_TO_REPORT_TYPE = {
    AnalysisMode.QUICK: "brief",
    AnalysisMode.STANDARD: "simple",
    AnalysisMode.DEEP: "full",
    AnalysisMode.STRATEGY: "full",
    AnalysisMode.CONTEXT_ONLY: "simple",
}


def _parse_market(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def _parse_selection_source(value: Optional[str]) -> SelectionSource:
    if not value:
        return SelectionSource.MANUAL
    try:
        return SelectionSource(value.strip().lower())
    except ValueError:
        return SelectionSource.UNKNOWN


def _load_request_from_json(path_or_dash: str) -> AnalysisRequest:
    if path_or_dash == "-":
        payload = json.load(sys.stdin)
    else:
        payload = json.loads(Path(path_or_dash).read_text(encoding="utf-8"))
    return AnalysisRequest.model_validate(payload)


def _build_request_from_args(args: argparse.Namespace) -> AnalysisRequest:
    if not args.stock:
        raise ValueError("--stock is required when --input-json is not provided")

    return AnalysisRequest(
        stock=StockTarget(
            input=args.stock,
            code=args.stock if args.stock and args.stock.strip() else None,
            market=_parse_market(args.market),
            name=args.stock_name,
        ),
        mode=AnalysisMode(args.mode),
        strategy=args.strategy,
        features=AnalysisFeatures(
            include_news=args.include_news,
            include_fundamental=args.include_fundamental,
            include_market_context=args.include_market_context,
            include_realtime_quote=args.include_realtime_quote,
            include_chip_data=args.include_chip_data,
        ),
        output=AnalysisOutput(
            format=OutputFormat(args.output_format),
            language=args.language,
            verbosity=OutputVerbosity(args.verbosity),
        ),
        execution=AnalysisExecution(
            async_mode=False,
            force_refresh=args.force_refresh,
            save_history=not args.no_save_history,
            dry_run=args.dry_run,
        ),
        context=AnalysisContextMeta(
            query_source=QuerySource.CLI,
            original_query=args.original_query,
            selection_source=_parse_selection_source(args.selection_source),
        ),
    )


def _resolve_report_type(request: AnalysisRequest) -> str:
    return MODE_TO_REPORT_TYPE.get(request.mode, "simple")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run unified stock analysis and emit v2 AnalysisResponse JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/run_stock_analysis.py --stock 600519
  python3 scripts/run_stock_analysis.py --stock AAPL --mode deep --market us
  python3 scripts/run_stock_analysis.py --input-json request.json --pretty
  cat request.json | python3 scripts/run_stock_analysis.py --input-json -
        """,
    )
    parser.add_argument("--input-json", help="Path to AnalysisRequest JSON file, or '-' for stdin")
    parser.add_argument("--stock", help="Stock input (code or name) when not using --input-json")
    parser.add_argument("--stock-name", help="Optional resolved stock name")
    parser.add_argument("--market", choices=["cn", "hk", "us"], help="Optional market hint")
    parser.add_argument(
        "--mode",
        default=AnalysisMode.STANDARD.value,
        choices=[mode.value for mode in AnalysisMode],
        help="Analysis mode",
    )
    parser.add_argument("--strategy", help="Optional strategy/skill id")
    parser.add_argument(
        "--output-format",
        default=OutputFormat.DASHBOARD.value,
        choices=[fmt.value for fmt in OutputFormat],
        help="Desired output format in the unified contract",
    )
    parser.add_argument(
        "--verbosity",
        default=OutputVerbosity.STANDARD.value,
        choices=[level.value for level in OutputVerbosity],
        help="Desired output verbosity",
    )
    parser.add_argument("--language", default="zh", choices=["zh", "en"], help="Output language")
    parser.add_argument("--original-query", help="Original user text for traceability")
    parser.add_argument(
        "--selection-source",
        choices=[source.value for source in SelectionSource],
        default=SelectionSource.MANUAL.value,
        help="Where the stock selection came from",
    )
    parser.add_argument("--force-refresh", action="store_true", help="Bypass cache/history reuse")
    parser.add_argument("--dry-run", action="store_true", help="Emit normalized request without running analysis")
    parser.add_argument("--no-save-history", action="store_true", help="Request-level hint to avoid saving history")
    parser.add_argument("--notify", action="store_true", help="Allow downstream notification side effects")
    parser.add_argument("--include-news", dest="include_news", action="store_true", default=True)
    parser.add_argument("--no-include-news", dest="include_news", action="store_false")
    parser.add_argument("--include-fundamental", action="store_true", default=False)
    parser.add_argument("--include-market-context", action="store_true", default=False)
    parser.add_argument("--include-realtime-quote", dest="include_realtime_quote", action="store_true", default=True)
    parser.add_argument("--no-include-realtime-quote", dest="include_realtime_quote", action="store_false")
    parser.add_argument("--include-chip-data", action="store_true", default=False)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser


def _preflight_request(request: AnalysisRequest) -> Optional[dict[str, Any]]:
    """Return a JSON-serializable error payload when preflight fails, else None."""
    config = get_config()
    return build_full_analysis_preflight_error(litellm_model=getattr(config, "litellm_model", None))


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        request = _load_request_from_json(args.input_json) if args.input_json else _build_request_from_args(args)
    except Exception as exc:
        print(json.dumps({"error": "invalid_request", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    if request.execution.dry_run:
        payload = request.model_dump(mode="json", by_alias=True)
        print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    preflight_error = _preflight_request(request)
    if preflight_error is not None:
        print(json.dumps(preflight_error, ensure_ascii=False), file=sys.stderr)
        return 3

    service = AnalysisService()
    response = service.analyze_stock_unified(
        stock_code=request.stock.code or request.stock.input,
        report_type=_resolve_report_type(request),
        force_refresh=request.execution.force_refresh,
        send_notification=args.notify,
        query_source=request.context.query_source,
    )

    if response is None:
        print(
            json.dumps(
                {"error": "analysis_failed", "message": service.last_error or "Unknown analysis failure"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1

    payload = response.model_dump(mode="json")
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
