# -*- coding: utf-8 -*-
"""Unified CLI/script entry for market analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stock_analysis_skill.contracts import MarketAnalysisRequest  # noqa: E402
from src.stock_analysis_skill.analyzers.market import MarketSkillAnalyzer  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run market analysis and emit structured JSON.")
    parser.add_argument("--region", default="cn", choices=["cn", "hk", "us", "both"])
    parser.add_argument("--no-news", action="store_true", help="Skip news search")
    parser.add_argument("--dry-run", action="store_true", help="Emit normalized request only")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    request = MarketAnalysisRequest(region=args.region, include_news=not args.no_news)

    if args.dry_run:
        print(json.dumps(request.model_dump(mode="json"), ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    analyzer = MarketSkillAnalyzer()
    response = analyzer.analyze(request)
    if response is None:
        print(json.dumps({"error": "market_analysis_failed", "message": analyzer.last_error or "Unknown failure"}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
