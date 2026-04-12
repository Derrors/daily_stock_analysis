# -*- coding: utf-8 -*-
"""Context-first analysis service.

This service builds structured analysis context without invoking any LLM.
It is the repository-owned implementation behind `scripts/build_analysis_context.py`,
so the script can stay as a thin adapter instead of becoming a second analysis core.
"""

from __future__ import annotations

from typing import Any, Optional

from data_provider import DataFetcherManager, is_hk_stock_code, is_us_stock_code
from src.config import get_config
from src.schemas.analysis_contract import AnalysisRequest, DataCompleteness
from src.search_service import SearchService
from src.stock_analyzer import StockTrendAnalyzer
from src.utils.analysis_runtime_contract import apply_component_completeness


def infer_market_from_code(code: str) -> str:
    """Infer market code from a stock identifier."""
    normalized = (code or "").strip()
    if is_us_stock_code(normalized):
        return "us"
    if is_hk_stock_code(normalized):
        return "hk"
    return "cn"


def make_search_service() -> Optional[SearchService]:
    """Create the repo-owned search service if any provider is available."""
    config = get_config()
    try:
        service = SearchService(
            bocha_keys=config.bocha_api_keys,
            tavily_keys=config.tavily_api_keys,
            brave_keys=config.brave_api_keys,
            serpapi_keys=config.serpapi_keys,
            news_max_age_days=config.news_max_age_days,
            news_strategy_profile=getattr(config, "news_strategy_profile", "short"),
        )
        return service if service.is_available else None
    except Exception:
        return None


class AnalysisContextService:
    """Repository-owned builder for structured context-first analysis payloads."""

    def __init__(
        self,
        *,
        fetcher: Optional[DataFetcherManager] = None,
        trend_analyzer: Optional[StockTrendAnalyzer] = None,
        search_service: Optional[SearchService] = None,
    ) -> None:
        self.fetcher = fetcher if fetcher is not None else DataFetcherManager()
        self.trend_analyzer = trend_analyzer if trend_analyzer is not None else StockTrendAnalyzer()
        self.search_service = search_service if search_service is not None else make_search_service()

    def build_context(self, request: AnalysisRequest, *, days: int = 60) -> dict[str, Any]:
        stock_code = request.stock.code or request.stock.input
        stock_name = request.stock.name or self.fetcher.get_stock_name(stock_code, allow_realtime=False) or stock_code

        context: dict[str, Any] = {
            "request": request.model_dump(mode="json", by_alias=True),
            "stock": {
                "code": stock_code,
                "name": stock_name,
                "market": request.stock.market.value if request.stock.market else infer_market_from_code(stock_code),
            },
            "trend": None,
            "realtime": None,
            "chip": None,
            "intel": None,
            "market_context": None,
            "evidence": {
                "providers": {},
                "used_features": [],
                "data_completeness": {},
            },
            "metadata": {
                "mode": request.mode.value,
                "query_source": request.context.query_source.value,
                "degraded": False,
                "partial": False,
                "errors": [],
            },
        }

        self._populate_trend(context, stock_code=stock_code, days=days)
        self._populate_realtime(context, stock_code=stock_code, enabled=request.features.include_realtime_quote)
        self._populate_chip(context, stock_code=stock_code, enabled=request.features.include_chip_data)
        self._populate_intel(
            context,
            stock_code=stock_code,
            stock_name=stock_name,
            enabled=request.features.include_news,
        )
        self._populate_market_context(context, enabled=request.features.include_market_context)

        return context

    def _populate_trend(self, context: dict[str, Any], *, stock_code: str, days: int) -> None:
        try:
            df, source_name = self.fetcher.get_daily_data(stock_code, days=max(30, days))
            context["evidence"]["providers"]["daily"] = [source_name]
            context["evidence"]["used_features"].append("daily_history")
            trend_result = self.trend_analyzer.analyze(df, stock_code)
            context["trend"] = trend_result.to_dict()
            apply_component_completeness(context, "trend", DataCompleteness.FULL)
        except Exception as exc:
            apply_component_completeness(
                context,
                "trend",
                DataCompleteness.MISSING,
                error=f"daily_or_trend_failed: {exc}",
            )

    def _populate_realtime(self, context: dict[str, Any], *, stock_code: str, enabled: bool) -> None:
        if not enabled:
            apply_component_completeness(context, "realtime", DataCompleteness.NOT_REQUESTED)
            return

        try:
            quote = self.fetcher.get_realtime_quote(stock_code, log_final_failure=False)
            if quote is None:
                apply_component_completeness(
                    context,
                    "realtime",
                    DataCompleteness.MISSING,
                    error="realtime_unavailable: no quote returned",
                )
                return

            context["realtime"] = quote.to_dict() if hasattr(quote, "to_dict") else quote
            context["evidence"]["used_features"].append("realtime_quote")
            if isinstance(context["realtime"], dict):
                source = context["realtime"].get("source")
                if source:
                    context["evidence"]["providers"]["realtime"] = [str(source)]
            apply_component_completeness(context, "realtime", DataCompleteness.FULL)
        except Exception as exc:
            apply_component_completeness(
                context,
                "realtime",
                DataCompleteness.MISSING,
                error=f"realtime_failed: {exc}",
            )

    def _populate_chip(self, context: dict[str, Any], *, stock_code: str, enabled: bool) -> None:
        if not enabled:
            apply_component_completeness(context, "chip", DataCompleteness.NOT_REQUESTED)
            return

        try:
            chip = self.fetcher.get_chip_distribution(stock_code)
            if chip is None:
                apply_component_completeness(
                    context,
                    "chip",
                    DataCompleteness.MISSING,
                    error="chip_unavailable: no chip data returned",
                )
                return

            context["chip"] = chip.to_dict() if hasattr(chip, "to_dict") else chip
            context["evidence"]["used_features"].append("chip_distribution")
            apply_component_completeness(context, "chip", DataCompleteness.FULL)
        except Exception as exc:
            apply_component_completeness(
                context,
                "chip",
                DataCompleteness.MISSING,
                error=f"chip_failed: {exc}",
            )

    def _populate_intel(
        self,
        context: dict[str, Any],
        *,
        stock_code: str,
        stock_name: str,
        enabled: bool,
    ) -> None:
        if not enabled:
            apply_component_completeness(context, "intel", DataCompleteness.NOT_REQUESTED)
            return

        if self.search_service is None:
            apply_component_completeness(
                context,
                "intel",
                DataCompleteness.MISSING,
                error="news_unavailable: no search provider configured",
            )
            return

        try:
            news = self.search_service.search_stock_news(stock_code=stock_code, stock_name=stock_name, max_results=5)
            context["intel"] = {
                "query": news.query,
                "provider": news.provider,
                "success": news.success,
                "error_message": news.error_message,
                "results": [result.__dict__ for result in news.results],
            }
            context["evidence"]["used_features"].append("news_search")
            completeness = DataCompleteness.FULL if news.success else DataCompleteness.PARTIAL
            apply_component_completeness(
                context,
                "intel",
                completeness,
                error=(f"news_unavailable: {news.error_message}" if (not news.success and news.error_message) else None),
            )
        except Exception as exc:
            apply_component_completeness(
                context,
                "intel",
                DataCompleteness.MISSING,
                error=f"news_failed: {exc}",
            )

    def _populate_market_context(self, context: dict[str, Any], *, enabled: bool) -> None:
        if not enabled:
            apply_component_completeness(context, "market_context", DataCompleteness.NOT_REQUESTED)
            return

        context["market_context"] = {
            "requested": True,
            "note": "Market context hook reserved for next iteration; use get_market_overview.py later.",
        }
        apply_component_completeness(
            context,
            "market_context",
            DataCompleteness.PARTIAL,
            error="market_context_partial: hook not implemented yet",
        )
