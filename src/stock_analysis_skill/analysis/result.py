# -*- coding: utf-8 -*-
"""Backward-compatible re-export for AnalysisResult.

The canonical definition now lives in
``src.stock_analysis_skill.contracts``.
"""

from src.stock_analysis_skill.contracts import AnalysisResult  # noqa: F401

__all__ = ["AnalysisResult"]
