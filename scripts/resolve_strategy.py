# -*- coding: utf-8 -*-
"""Resolve strategy resources for agent-facing workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.stock_analysis_skill.analyzers.strategy import StrategyResolver  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve stock-analysis strategy resources.")
    parser.add_argument("query", nargs="?", default="", help="Strategy id, display name, or alias")
    parser.add_argument("--list", action="store_true", help="List available strategy ids")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    resolver = StrategyResolver()

    if args.list:
        payload = {"strategies": [spec.model_dump(mode="json") for spec in resolver.list_strategy_specs()]}
    else:
        payload = resolver.resolve(args.query).model_dump(mode="json")

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
