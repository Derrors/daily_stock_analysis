# -*- coding: utf-8 -*-
"""Build stock analysis context without invoking any LLM.

This script stays as a thin adapter:
- parse CLI args into the unified AnalysisRequest
- delegate context assembly to repository-owned service code
- emit deterministic JSON for Agent / skill orchestration
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stock_analysis_skill.contracts import (  # noqa: E402
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
from src.services.analysis_context_service import AnalysisContextService, infer_market_from_code  # noqa: E402


def _parse_selection_source(value: Optional[str]) -> SelectionSource:
    if not value:
        return SelectionSource.MANUAL
    try:
        return SelectionSource(value.strip().lower())
    except ValueError:
        return SelectionSource.UNKNOWN


def _build_request_from_args(args: argparse.Namespace) -> AnalysisRequest:
    if not args.stock:
        raise ValueError("--stock is required")

    return AnalysisRequest(
        stock=StockTarget(
            input=args.stock,
            code=args.stock,
            market=infer_market_from_code(args.stock),
            name=args.stock_name,
        ),
        mode=AnalysisMode.CONTEXT_ONLY,
        strategy=args.strategy,
        features=AnalysisFeatures(
            include_news=args.include_news,
            include_fundamental=args.include_fundamental,
            include_market_context=args.include_market_context,
            include_realtime_quote=args.include_realtime_quote,
            include_chip_data=args.include_chip_data,
        ),
        output=AnalysisOutput(
            format=OutputFormat.CONTEXT,
            language=args.language,
            verbosity=OutputVerbosity(args.verbosity),
        ),
        execution=AnalysisExecution(
            async_mode=False,
            force_refresh=args.force_refresh,
            save_history=False,
            dry_run=args.dry_run,
        ),
        context=AnalysisContextMeta(
            query_source=QuerySource.CLI,
            original_query=args.original_query,
            selection_source=_parse_selection_source(args.selection_source),
        ),
    )


def _json_default(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build structured stock analysis context without invoking any LLM.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/build_analysis_context.py --stock 600519 --pretty
  python3 scripts/build_analysis_context.py --stock AAPL --include-market-context --pretty
        """,
    )
    parser.add_argument("--stock", required=True, help="Stock input (code or normalized code)")
    parser.add_argument("--stock-name", help="Optional stock name hint")
    parser.add_argument("--strategy", help="Optional strategy hint for downstream Agent")
    parser.add_argument("--language", default="zh", choices=["zh", "en"])
    parser.add_argument("--verbosity", default="standard", choices=["brief", "standard", "detailed"])
    parser.add_argument("--original-query", help="Original user text")
    parser.add_argument(
        "--selection-source",
        choices=[source.value for source in SelectionSource],
        default=SelectionSource.MANUAL.value,
    )
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-news", dest="include_news", action="store_true", default=True)
    parser.add_argument("--no-include-news", dest="include_news", action="store_false")
    parser.add_argument("--include-fundamental", action="store_true", default=False)
    parser.add_argument("--include-market-context", action="store_true", default=False)
    parser.add_argument("--include-realtime-quote", dest="include_realtime_quote", action="store_true", default=True)
    parser.add_argument("--no-include-realtime-quote", dest="include_realtime_quote", action="store_false")
    parser.add_argument("--include-chip-data", action="store_true", default=False)
    parser.add_argument("--days", type=int, default=60, help="Historical bars to request")
    parser.add_argument("--pretty", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        request = _build_request_from_args(args)
    except Exception as exc:
        print(json.dumps({"error": "invalid_request", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    if request.execution.dry_run:
        print(json.dumps(request.model_dump(mode="json", by_alias=True), ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    context = AnalysisContextService().build_context(request, days=args.days)
    print(json.dumps(context, ensure_ascii=False, indent=2 if args.pretty else None, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
