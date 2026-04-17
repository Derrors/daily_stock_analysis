# -*- coding: utf-8 -*-
"""Skill-first service entry for stock analysis.

This module is the canonical service surface. During Phase F it progressively
absorbs both the synchronous mainline and the async task-entry path from older
product-shell modules.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from src.services.analysis_service import AnalysisService as LegacyAnalysisService
from src.stock_analysis_skill.runtime.stock_pipeline import StockAnalysisMainlineRuntime

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
    """Canonical agent-facing stock/market/strategy service.

    Scripts and agents should depend on this service instead of the historical
    `AnalysisService -> StockAnalysisPipeline` chain.
    """

    def __init__(self, analysis_service: Optional[LegacyAnalysisService] = None):
        self.mainline_runtime = StockAnalysisMainlineRuntime()
        self.stock_analyzer = StockSkillAnalyzer(
            analysis_service=analysis_service,
            runtime=self.mainline_runtime,
        )
        self.market_analyzer = MarketSkillAnalyzer()
        self.skill_resolver = SkillResolver()

    @property
    def last_error(self) -> Optional[str]:
        return (
            self.mainline_runtime.last_error
            or self.stock_analyzer.last_error
            or self.market_analyzer.last_error
        )

    def analyze_request(self, request: AnalysisRequest) -> Optional[AnalysisResponse]:
        """Execute the stock-analysis mainline through the canonical facade."""
        return self.stock_analyzer.analyze(request)

    def analyze_stock_payload(
        self,
        stock_code: str,
        *,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Optional[dict[str, Any]]:
        """Compatibility payload entry for async task/runtime callers.

        This keeps the task queue on the canonical skill service while preserving
        the current legacy result-dict contract for task state storage/events.
        """
        return self.mainline_runtime.analyze_stock(
            stock_code=stock_code,
            report_type=report_type,
            force_refresh=force_refresh,
            query_id=query_id,
            progress_callback=progress_callback,
        )

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
