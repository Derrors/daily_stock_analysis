# -*- coding: utf-8 -*-

from src.stock_analysis_skill.contracts import (
    AnalysisResponse,
    DecisionAction,
    Market,
    MarketAnalysisResponse,
)
from src.stock_analysis_skill.renderers.markdown import SkillMarkdownRenderer
from src.stock_analysis_skill.service import StockAnalysisSkillService


def test_render_stock_markdown() -> None:
    response = AnalysisResponse.minimal(
        code="600519",
        market=Market.CN,
        action=DecisionAction.HOLD,
        summary="继续观察量价关系",
        name="贵州茅台",
    )
    markdown = SkillMarkdownRenderer.render_stock(response)
    assert "# Stock Analysis · 600519" in markdown
    assert "继续观察量价关系" in markdown


def test_render_market_markdown() -> None:
    response = MarketAnalysisResponse(region="us", summary="US market review ready")
    markdown = SkillMarkdownRenderer.render_market(response)
    assert "# Market Analysis · us" in markdown
    assert "US market review ready" in markdown


def test_service_render_strategy_markdown() -> None:
    service = StockAnalysisSkillService()
    resolution = service.resolve_strategy("ma_golden_cross")
    markdown = service.render_strategy_markdown(resolution)
    assert "Strategy Resolution" in markdown
    assert "ma_golden_cross" in markdown
