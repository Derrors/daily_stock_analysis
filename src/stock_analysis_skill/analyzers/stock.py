# -*- coding: utf-8 -*-
"""Stock analyzer wrapper for the skill-first mainline."""

from __future__ import annotations

from typing import Optional

from src.stock_analysis_skill.contracts import AnalysisMode, AnalysisRequest, AnalysisResponse, QuerySource
from src.stock_analysis_skill.runtime.stock_pipeline import StockAnalysisMainlineRuntime

MODE_TO_PIPELINE_REPORT_TYPE = {
    AnalysisMode.QUICK: "brief",
    AnalysisMode.STANDARD: "simple",
    AnalysisMode.DEEP: "full",
    AnalysisMode.STRATEGY: "full",
    AnalysisMode.CONTEXT_ONLY: "simple",
}


def _resolve_report_type(mode: AnalysisMode) -> str:
    return MODE_TO_PIPELINE_REPORT_TYPE.get(mode, "simple")


class StockSkillAnalyzer:
    """Thin wrapper over the canonical stock-analysis runtime."""

    def __init__(
        self,
        runtime: Optional[StockAnalysisMainlineRuntime] = None,
    ):
        self.runtime = runtime or StockAnalysisMainlineRuntime()

    @property
    def last_error(self) -> Optional[str]:
        return getattr(self.runtime, "last_error", None)

    def analyze(self, request: AnalysisRequest) -> Optional[AnalysisResponse]:
        stock_code = request.stock.code or request.stock.input
        report_type = _resolve_report_type(request.mode)
        query_source = self._normalize_query_source(request.context.query_source)
        return self.runtime.analyze_stock_unified(
            stock_code=stock_code,
            report_type=report_type,
            force_refresh=request.execution.force_refresh,
            query_source=query_source,
        )

    @staticmethod
    def _normalize_query_source(query_source: QuerySource) -> QuerySource:
        if query_source in {QuerySource.UNKNOWN, QuerySource.SYSTEM}:
            return QuerySource.AGENT
        return query_source
