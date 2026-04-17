# -*- coding: utf-8 -*-
"""Market-analysis wrapper for the skill-first rewrite."""

from __future__ import annotations

from typing import Optional

from src.market_analyzer import MarketAnalyzer
from src.stock_analysis_skill.contracts import (
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    MarketIndexSummary,
    MetadataBlock,
)


class MarketSkillAnalyzer:
    """Structured market-analysis entry built on the legacy market analyzer."""

    def __init__(self, analyzer_factory=MarketAnalyzer):
        self.analyzer_factory = analyzer_factory
        self.last_error: Optional[str] = None

    def analyze(self, request: MarketAnalysisRequest) -> Optional[MarketAnalysisResponse]:
        region = request.region if request.region in {"cn", "us"} else "cn"
        try:
            analyzer = self.analyzer_factory(region=region)
            overview = analyzer.get_market_overview()
            news = analyzer.search_market_news() if request.include_news else []
            report = analyzer.generate_market_review(overview, news)
            summary = self._build_summary(region, overview, report)
            return MarketAnalysisResponse(
                region=region,
                summary=summary,
                report=report or "",
                indices=[
                    MarketIndexSummary(
                        code=index.code,
                        name=index.name,
                        current=index.current,
                        change_pct=index.change_pct,
                    )
                    for index in overview.indices
                ],
                metadata=MetadataBlock(partial=not bool(report)),
            )
        except Exception as exc:
            self.last_error = str(exc)
            return None

    @staticmethod
    def _build_summary(region: str, overview, report: str) -> str:
        market_label = "US" if region == "us" else "A-share"
        lead = overview.indices[0] if overview.indices else None
        if lead is None:
            return f"{market_label} market analysis generated."
        return (
            f"{market_label} market review ready: {lead.name} {lead.current:.2f} "
            f"({lead.change_pct:+.2f}%), report length={len(report or '')}."
        )
