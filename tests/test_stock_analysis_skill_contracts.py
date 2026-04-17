# -*- coding: utf-8 -*-

from src.stock_analysis_skill.contracts import AnalysisMode, AnalysisRequest
from src.stock_analysis_skill.service import resolve_report_type


def test_resolve_report_type_mapping() -> None:
    assert resolve_report_type(AnalysisMode.QUICK) == "brief"
    assert resolve_report_type(AnalysisMode.STANDARD) == "simple"
    assert resolve_report_type(AnalysisMode.DEEP) == "full"


def test_minimal_request_contract() -> None:
    request = AnalysisRequest.minimal("AAPL")
    assert request.stock.input == "AAPL"
    assert request.mode is AnalysisMode.STANDARD
