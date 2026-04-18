# -*- coding: utf-8 -*-
"""Resolve user-facing strategy resources through the internal skill resolver."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stock_analysis_skill.contracts import StrategyResolutionRequest  # noqa: E402
from src.stock_analysis_skill.service import StockAnalysisSkillService  # noqa: E402

PUBLIC_API_VERSION = "v1"
EXIT_CODE_SUCCESS = 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve stock-analysis strategy resources.")
    parser.add_argument("query", nargs="?", default="", help="Strategy id, display name, or alias")
    parser.add_argument("--list", action="store_true", help="List available strategy ids")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def build_request_from_args(args: argparse.Namespace) -> StrategyResolutionRequest:
    return StrategyResolutionRequest(query=args.query)


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    service = StockAnalysisSkillService()
    request = build_request_from_args(args)

    if args.list:
        payload = {"strategies": [spec.model_dump(mode="json") for spec in service.list_strategies()]}
    else:
        payload = service.resolve_strategy(request).model_dump(mode="json")

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return EXIT_CODE_SUCCESS


__all__ = [
    "PUBLIC_API_VERSION",
    "EXIT_CODE_SUCCESS",
    "build_parser",
    "build_request_from_args",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
