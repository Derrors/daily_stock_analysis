# -*- coding: utf-8 -*-
"""Unified CLI/script entry for market analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stock_analysis_skill.contracts import MarketAnalysisRequest  # noqa: E402
from src.stock_analysis_skill.service import StockAnalysisSkillService  # noqa: E402

PUBLIC_API_VERSION = "v1"
EXIT_CODE_SUCCESS = 0
EXIT_CODE_ANALYSIS_FAILED = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run market analysis and emit structured JSON.")
    parser.add_argument("--region", default="cn", choices=["cn", "hk", "us", "both"])
    parser.add_argument("--no-news", action="store_true", help="Skip news search")
    parser.add_argument("--dry-run", action="store_true", help="Emit normalized request only")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def build_request_from_args(args: argparse.Namespace) -> MarketAnalysisRequest:
    return MarketAnalysisRequest(region=args.region, include_news=not args.no_news)


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    request = build_request_from_args(args)

    if args.dry_run:
        print(json.dumps(request.model_dump(mode="json"), ensure_ascii=False, indent=2 if args.pretty else None))
        return EXIT_CODE_SUCCESS

    service = StockAnalysisSkillService()
    response = service.analyze_market(request)
    if response is None:
        print(
            json.dumps(
                {"error": "market_analysis_failed", "message": service.last_error or "Unknown failure"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return EXIT_CODE_ANALYSIS_FAILED

    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=False, indent=2 if args.pretty else None))
    return EXIT_CODE_SUCCESS


__all__ = [
    "PUBLIC_API_VERSION",
    "EXIT_CODE_SUCCESS",
    "EXIT_CODE_ANALYSIS_FAILED",
    "build_parser",
    "build_request_from_args",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
