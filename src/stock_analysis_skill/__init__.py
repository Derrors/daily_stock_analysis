# -*- coding: utf-8 -*-
"""Agent-first stock analysis skill package.

This package is the canonical home for the skill-first runtime.
Keep package-level imports lightweight: importing `src.stock_analysis_skill.contracts`
must not pull in heavy service/pipeline modules during startup.
"""

from .contracts import AnalysisRequest, AnalysisResponse, MarketAnalysisRequest, MarketAnalysisResponse

__all__ = [
    "AnalysisRequest",
    "AnalysisResponse",
    "MarketAnalysisRequest",
    "MarketAnalysisResponse",
]
