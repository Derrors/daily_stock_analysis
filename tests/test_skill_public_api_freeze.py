from __future__ import annotations

import json

import scripts.resolve_strategy as resolve_strategy_script
import scripts.run_market_analysis as run_market_analysis_script
import scripts.run_stock_analysis as run_stock_analysis_script
from src.stock_analysis_skill import contracts as skill_contracts
from src.stock_analysis_skill import service as skill_service
from src.stock_analysis_skill.contracts import (
    MarketAnalysisResponse,
    StrategyResolutionRequest,
    StrategyResolutionResponse,
    StrategySpec,
)
from src.stock_analysis_skill.service import StockAnalysisSkillService


def test_contract_public_api_frozen() -> None:
    assert skill_contracts.PUBLIC_API_VERSION == "v1"
    assert skill_contracts.__all__[:2] == ["PUBLIC_API_VERSION", "PUBLIC_CONTRACT_EXPORTS"]
    assert skill_contracts.PUBLIC_CONTRACT_EXPORTS == skill_contracts.__all__[2:]
    assert "AnalysisRequest" in skill_contracts.PUBLIC_CONTRACT_EXPORTS
    assert "AnalysisResponse" in skill_contracts.PUBLIC_CONTRACT_EXPORTS
    assert "MarketAnalysisRequest" in skill_contracts.PUBLIC_CONTRACT_EXPORTS
    assert "StrategyResolutionResponse" in skill_contracts.PUBLIC_CONTRACT_EXPORTS


def test_service_public_api_frozen() -> None:
    assert skill_service.PUBLIC_API_VERSION == "v1"
    assert skill_service.__all__ == [
        "PUBLIC_API_VERSION",
        "PUBLIC_SERVICE_METHODS",
        "StockAnalysisSkillService",
        "resolve_report_type",
    ]
    service = StockAnalysisSkillService()
    for method_name in skill_service.PUBLIC_SERVICE_METHODS:
        assert hasattr(service, method_name)


def test_service_accepts_strategy_resolution_request() -> None:
    service = StockAnalysisSkillService()
    response = service.resolve_strategy(StrategyResolutionRequest(query="ma_golden_cross"))
    assert response.matched is True
    assert response.strategy is not None
    assert response.strategy.id == "ma_golden_cross"


def test_market_script_uses_service_facade(monkeypatch, capsys) -> None:
    class DummyService:
        last_error = None

        def analyze_market(self, request):
            assert request.region == "us"
            return MarketAnalysisResponse(region="us", summary="ready")

    monkeypatch.setattr(run_market_analysis_script, "StockAnalysisSkillService", lambda: DummyService())

    exit_code = run_market_analysis_script.main(["--region", "us"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["region"] == "us"
    assert payload["summary"] == "ready"


def test_strategy_script_uses_service_facade(monkeypatch, capsys) -> None:
    class DummyService:
        def list_strategies(self):
            return [
                StrategySpec(
                    id="ma_golden_cross",
                    display_name="均线金叉",
                    aliases=["金叉"],
                )
            ]

        def resolve_strategy(self, query):
            assert isinstance(query, StrategyResolutionRequest)
            assert query.query == "金叉"
            return StrategyResolutionResponse(
                query="金叉",
                matched=True,
                strategy=StrategySpec(id="ma_golden_cross", display_name="均线金叉"),
            )

    monkeypatch.setattr(resolve_strategy_script, "StockAnalysisSkillService", lambda: DummyService())

    exit_code = resolve_strategy_script.main(["金叉"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["matched"] is True
    assert payload["strategy"]["id"] == "ma_golden_cross"
