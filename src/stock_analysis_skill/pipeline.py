# -*- coding: utf-8 -*-
"""Skill-first pipeline compatibility wrapper.

The real execution path is still backed by `src.core.pipeline.StockAnalysisPipeline`
during migration. This wrapper gives the new package a canonical import target
without forcing a full pipeline rewrite in Phase B.
"""

from src.core.pipeline import StockAnalysisPipeline as LegacyStockAnalysisPipeline


class StockAnalysisSkillPipeline(LegacyStockAnalysisPipeline):
    """Transitional alias for the canonical skill pipeline path."""


__all__ = ["StockAnalysisSkillPipeline"]
