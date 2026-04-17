# -*- coding: utf-8 -*-
"""
Regression tests for report generation after notification delivery removal.
"""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.litellm_stub import ensure_litellm_stub

ensure_litellm_stub()

from src.core.pipeline import StockAnalysisPipeline
from src.enums import ReportType


class _FakeNotifier:
    def __init__(self):
        self.generate_dashboard_report = MagicMock(side_effect=self._generate_dashboard_report)
        self.generate_brief_report = MagicMock(return_value="brief-report")
        self.generate_single_stock_report = MagicMock(return_value="single-report")
        self.save_report_to_file = MagicMock(return_value="/tmp/report.md")

    @staticmethod
    def _generate_dashboard_report(results):
        return "report:" + ",".join(r.code for r in results)


class TestPipelineReportGenerationAfterDescope(unittest.TestCase):
    def test_generate_aggregate_report_still_uses_dashboard_for_simple(self):
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.report_output_service = _FakeNotifier()
        results = [SimpleNamespace(code="000001"), SimpleNamespace(code="600519")]

        report = pipeline._generate_aggregate_report(results, ReportType.SIMPLE)

        self.assertEqual(report, "report:000001,600519")
        pipeline.report_output_service.generate_dashboard_report.assert_called_once_with(results)
        pipeline.report_output_service.generate_brief_report.assert_not_called()

    def test_generate_aggregate_report_uses_brief_renderer_for_brief(self):
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.report_output_service = _FakeNotifier()
        results = [SimpleNamespace(code="000001")]

        report = pipeline._generate_aggregate_report(results, ReportType.BRIEF)

        self.assertEqual(report, "brief-report")
        pipeline.report_output_service.generate_brief_report.assert_called_once_with(results)
        pipeline.report_output_service.generate_dashboard_report.assert_not_called()

    def test_save_local_report_persists_generated_report(self):
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.report_output_service = _FakeNotifier()
        results = [SimpleNamespace(code="000001")]

        pipeline._save_local_report(results, ReportType.SIMPLE)

        pipeline.report_output_service.generate_dashboard_report.assert_called_once_with(results)
        pipeline.report_output_service.save_report_to_file.assert_called_once_with("report:000001")


if __name__ == "__main__":
    unittest.main()
