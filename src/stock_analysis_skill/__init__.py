# -*- coding: utf-8 -*-
"""Agent-first stock analysis skill package.

This package is the new canonical home for the skill-first rewrite.
Keep package-level imports lightweight: importing `src.stock_analysis_skill.contracts`
must not pull in legacy service/pipeline modules during migration.
"""

from .contracts import AnalysisRequest, AnalysisResponse, MarketAnalysisRequest, MarketAnalysisResponse

__all__ = [
    "AnalysisRequest",
    "AnalysisResponse",
    "MarketAnalysisRequest",
    "MarketAnalysisResponse",
]
