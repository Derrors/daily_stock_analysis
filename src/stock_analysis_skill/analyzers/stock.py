# -*- coding: utf-8 -*-
"""Stock analyzer wrapper for the skill-first mainline."""

from __future__ import annotations

from typing import Optional

from src.services.analysis_service import AnalysisService as LegacyAnalysisService
from src.stock_analysis_skill.contracts import AnalysisMode, AnalysisRequest, AnalysisResponse, QuerySource

MODE_TO_REPORT_TYPE = {
    AnalysisMode.QUICK: "brief",
    AnalysisMode.STANDARD: "simple",
    AnalysisMode.DEEP: "full",
    AnalysisMode.STRATEGY: "full",
    AnalysisMode.CONTEXT_ONLY: "simple",
}


def _resolve_report_type(mode: AnalysisMode) -> str:
    return MODE_TO_REPORT_TYPE.get(mode, "simple")


class StockSkillAnalyzer:
    """Thin wrapper over the current stock-analysis mainline."""

    def __init__(self, analysis_service: Optional[LegacyAnalysisService] = None):
        self.analysis_service = analysis_service or LegacyAnalysisService()

    @property
    def last_error(self) -> Optional[str]:
        return getattr(self.analysis_service, "last_error", None)

    def analyze(self, request: AnalysisRequest) -> Optional[AnalysisResponse]:
        return self.analysis_service.analyze_stock_unified(
            stock_code=request.stock.code or request.stock.input,
            report_type=_resolve_report_type(request.mode),
            force_refresh=request.execution.force_refresh,
            query_source=self._normalize_query_source(request.context.query_source),
        )

    @staticmethod
    def _normalize_query_source(query_source: QuerySource) -> QuerySource:
        if query_source in {QuerySource.UNKNOWN, QuerySource.SYSTEM}:
            return QuerySource.AGENT
        return query_source
