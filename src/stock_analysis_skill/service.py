# -*- coding: utf-8 -*-
"""Skill-first service entry for stock analysis.

This module provides a stable agent-facing service wrapper while the legacy
implementation is being migrated out of product-shell modules.
"""

from __future__ import annotations

from typing import Optional

from src.services.analysis_service import AnalysisService as LegacyAnalysisService

from .analyzers.market import MarketSkillAnalyzer
from .analyzers.stock import StockSkillAnalyzer
from .analyzers.strategy import SkillResolver
from .renderers.markdown import SkillMarkdownRenderer
from .contracts import (
    AnalysisMode,
    AnalysisRequest,
    AnalysisResponse,
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    QuerySource,
    StrategyResolutionResponse,
)

MODE_TO_REPORT_TYPE = {
    AnalysisMode.QUICK: "brief",
    AnalysisMode.STANDARD: "simple",
    AnalysisMode.DEEP: "full",
    AnalysisMode.STRATEGY: "full",
    AnalysisMode.CONTEXT_ONLY: "simple",
}


def resolve_report_type(mode: AnalysisMode) -> str:
    """Map unified analysis mode to the current legacy report type."""
    return MODE_TO_REPORT_TYPE.get(mode, "simple")


class StockAnalysisSkillService:
    """Agent-facing stock/market/strategy service.

    During migration this service keeps legacy execution paths behind a new
    skill-first facade so scripts and agents no longer couple directly to the
    old product-shell layout.
    """

    def __init__(self, analysis_service: Optional[LegacyAnalysisService] = None):
        self.stock_analyzer = StockSkillAnalyzer(analysis_service=analysis_service)
        self.market_analyzer = MarketSkillAnalyzer()
        self.skill_resolver = SkillResolver()
        self.strategy_resolver = self.skill_resolver  # backward-compatible alias

    @property
    def last_error(self) -> Optional[str]:
        return (
            self.stock_analyzer.last_error
            or self.market_analyzer.last_error
        )

    def analyze_request(self, request: AnalysisRequest) -> Optional[AnalysisResponse]:
        """Execute the stock-analysis mainline through the new facade."""
        return self.stock_analyzer.analyze(request)

    def analyze_market(self, request: MarketAnalysisRequest) -> Optional[MarketAnalysisResponse]:
        """Execute market analysis through the new facade."""
        return self.market_analyzer.analyze(request)

    def resolve_strategy(self, query: str) -> StrategyResolutionResponse:
        """Resolve a user-facing strategy resource through the internal skill resolver."""
        return self.skill_resolver.resolve(query)

    def render_stock_markdown(self, response: AnalysisResponse) -> str:
        return SkillMarkdownRenderer.render_stock(response)

    def render_market_markdown(self, response: MarketAnalysisResponse) -> str:
        return SkillMarkdownRenderer.render_market(response)

    def render_strategy_markdown(self, response: StrategyResolutionResponse) -> str:
        return SkillMarkdownRenderer.render_strategy_resolution(response)

    @staticmethod
    def _normalize_query_source(query_source: QuerySource) -> QuerySource:
        if query_source in {QuerySource.UNKNOWN, QuerySource.SYSTEM}:
            return QuerySource.AGENT
        return query_source
