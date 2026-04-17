# -*- coding: utf-8 -*-
"""Shared schema exports.

`src.schemas` now only exports report schema types.
Analysis request/response contracts live in
`src.stock_analysis_skill.contracts` and should be imported directly.
"""

from src.schemas.report_schema import AnalysisReportSchema

__all__ = [
    "AnalysisReportSchema",
]
