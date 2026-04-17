# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.stock_analysis_skill.analyzers.strategy import StrategyResolver
from src.stock_analysis_skill.contracts import MarketAnalysisRequest
from src.stock_analysis_skill.service import StockAnalysisSkillService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MARKET_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_market_analysis.py"
STRATEGY_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "resolve_strategy.py"


def test_strategy_resolver_matches_alias() -> None:
    resolver = StrategyResolver()
    response = resolver.resolve("金叉")
    assert response.matched is True
    assert response.strategy is not None
    assert response.strategy.id == "ma_golden_cross"


def test_market_request_contract_defaults() -> None:
    request = MarketAnalysisRequest(region="us", include_news=False)
    assert request.region == "us"
    assert request.include_news is False


def test_service_resolve_strategy() -> None:
    service = StockAnalysisSkillService()
    response = service.resolve_strategy("ma_golden_cross")
    assert response.matched is True
    assert response.strategy is not None


def test_run_market_analysis_dry_run() -> None:
    completed = subprocess.run(
        [sys.executable, str(MARKET_SCRIPT_PATH), "--region", "us", "--dry-run"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["region"] == "us"
    assert payload["include_news"] is True


def test_resolve_strategy_script() -> None:
    completed = subprocess.run(
        [sys.executable, str(STRATEGY_SCRIPT_PATH), "均线金叉"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["matched"] is True
    assert payload["strategy"]["id"] == "ma_golden_cross"
