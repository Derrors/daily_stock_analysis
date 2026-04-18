# -*- coding: utf-8 -*-
"""Skill-first service entry for stock analysis.

This module is the canonical service surface. During Phase F it progressively
absorbs both the synchronous mainline and the async task-entry path from older
product-shell modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

from .contracts import (
    AnalysisMode,
    AnalysisRequest,
    AnalysisResponse,
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    QuerySource,
    StrategyResolutionRequest,
    StrategyResolutionResponse,
    StrategySpec,
)

if TYPE_CHECKING:
    from src.stock_analysis_skill.runtime.stock_pipeline import StockAnalysisMainlineRuntime
    from .analyzers.market import MarketSkillAnalyzer
    from .analyzers.stock import StockSkillAnalyzer
    from .analyzers.strategy import SkillResolver

PUBLIC_API_VERSION = "v1"
PUBLIC_SERVICE_METHODS = (
    "last_error",
    "analyze_request",
    "analyze_stock_payload",
    "analyze_market",
    "resolve_strategy",
    "list_strategies",
    "render_stock_markdown",
    "render_market_markdown",
    "render_strategy_markdown",
)

MODE_TO_PIPELINE_REPORT_TYPE = {
    AnalysisMode.QUICK: "brief",
    AnalysisMode.STANDARD: "simple",
    AnalysisMode.DEEP: "full",
    AnalysisMode.STRATEGY: "full",
    AnalysisMode.CONTEXT_ONLY: "simple",
}


def resolve_report_type(mode: AnalysisMode) -> str:
    """Map unified analysis mode to the runtime pipeline report type."""
    return MODE_TO_PIPELINE_REPORT_TYPE.get(mode, "simple")


class StockAnalysisSkillService:
    """Canonical agent-facing stock/market/strategy service.

    Scripts and agents should depend on this service instead of the historical
    `AnalysisService -> StockAnalysisPipeline` chain.
    """

    def __init__(self):
        self._mainline_runtime: Optional["StockAnalysisMainlineRuntime"] = None
        self._stock_analyzer: Optional["StockSkillAnalyzer"] = None
        self._market_analyzer: Optional["MarketSkillAnalyzer"] = None
        self._skill_resolver: Optional["SkillResolver"] = None

    @property
    def mainline_runtime(self) -> "StockAnalysisMainlineRuntime":
        if self._mainline_runtime is None:
            from src.stock_analysis_skill.runtime.stock_pipeline import StockAnalysisMainlineRuntime

            self._mainline_runtime = StockAnalysisMainlineRuntime()
        return self._mainline_runtime

    @property
    def stock_analyzer(self) -> "StockSkillAnalyzer":
        if self._stock_analyzer is None:
            from .analyzers.stock import StockSkillAnalyzer

            self._stock_analyzer = StockSkillAnalyzer(runtime=self.mainline_runtime)
        return self._stock_analyzer

    @property
    def market_analyzer(self) -> "MarketSkillAnalyzer":
        if self._market_analyzer is None:
            from .analyzers.market import MarketSkillAnalyzer

            self._market_analyzer = MarketSkillAnalyzer()
        return self._market_analyzer

    @property
    def skill_resolver(self) -> "SkillResolver":
        if self._skill_resolver is None:
            from .analyzers.strategy import SkillResolver

            self._skill_resolver = SkillResolver()
        return self._skill_resolver

    @property
    def last_error(self) -> Optional[str]:
        return (
            (self._mainline_runtime.last_error if self._mainline_runtime is not None else None)
            or (self._stock_analyzer.last_error if self._stock_analyzer is not None else None)
            or (self._market_analyzer.last_error if self._market_analyzer is not None else None)
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
        """Runtime payload entry for async task/runtime callers.

        Keeps task-queue writes on the canonical skill service while returning
        the current task/event storage payload shape.
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

    def resolve_strategy(self, query: str | StrategyResolutionRequest) -> StrategyResolutionResponse:
        """Resolve a user-facing strategy resource through the internal skill resolver."""
        query_text = query.query if isinstance(query, StrategyResolutionRequest) else query
        return self.skill_resolver.resolve(query_text)

    def list_strategies(self) -> list[StrategySpec]:
        """Return the canonical repository strategy resources."""
        return self.skill_resolver.list_strategy_specs()

    def render_stock_markdown(self, response: AnalysisResponse) -> str:
        from .renderers.markdown import SkillMarkdownRenderer

        return SkillMarkdownRenderer.render_stock(response)

    def render_market_markdown(self, response: MarketAnalysisResponse) -> str:
        from .renderers.markdown import SkillMarkdownRenderer

        return SkillMarkdownRenderer.render_market(response)

    def render_strategy_markdown(self, response: StrategyResolutionResponse) -> str:
        from .renderers.markdown import SkillMarkdownRenderer

        return SkillMarkdownRenderer.render_strategy_resolution(response)

    @staticmethod
    def _normalize_query_source(query_source: QuerySource) -> QuerySource:
        if query_source in {QuerySource.UNKNOWN, QuerySource.SYSTEM}:
            return QuerySource.AGENT
        return query_source


__all__ = [
    "PUBLIC_API_VERSION",
    "PUBLIC_SERVICE_METHODS",
    "StockAnalysisSkillService",
    "resolve_report_type",
]
