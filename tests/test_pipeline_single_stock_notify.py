# -*- coding: utf-8 -*-
"""
Regression tests for pipeline behavior after single-stock notification removal.
"""

import os
import sys
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.litellm_stub import ensure_litellm_stub

ensure_litellm_stub()

from src.stock_analysis_skill.contracts import AnalysisResult
from src.core.pipeline import StockAnalysisPipeline
from src.enums import ReportType


class _TrackingNotifier:
    def __init__(self):
        self.thread_names = []
        self.email_stock_codes = []
        self.sent_reports = []
        self._lock = threading.Lock()
        self._inflight = 0
        self.max_inflight = 0
        self.generate_dashboard_report = MagicMock(
            side_effect=lambda results: "dashboard:" + ",".join(r.code for r in results)
        )
        self.generate_brief_report = MagicMock(
            side_effect=lambda results: "brief:" + ",".join(r.code for r in results)
        )
        self.generate_single_stock_report = MagicMock(
            side_effect=lambda result: f"single:{result.code}"
        )
        self.send = MagicMock(side_effect=self._send)

    def _send(self, content, email_stock_codes=None):
        with self._lock:
            self._inflight += 1
            self.max_inflight = max(self.max_inflight, self._inflight)

        self.thread_names.append(threading.current_thread().name)
        self.email_stock_codes.append(email_stock_codes)
        self.sent_reports.append(content)
        time.sleep(0.01)

        with self._lock:
            self._inflight -= 1

        return True


def _make_result(code: str, success: bool = True) -> AnalysisResult:
    return AnalysisResult(
        code=code,
        name=f"股票{code}",
        sentiment_score=80,
        trend_prediction="看多",
        operation_advice="持有",
        analysis_summary="测试结果",
        success=success,
        error_message=None if success else "JSON解析失败",
    )


class TestPipelineSingleStockNotify(unittest.TestCase):
    @staticmethod
    def _build_batch_pipeline() -> StockAnalysisPipeline:
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.max_workers = 2
        pipeline.fetcher_manager = MagicMock()
        pipeline.db = MagicMock()
        pipeline.db.has_today_data.return_value = False
        pipeline.report_output_service = _TrackingNotifier()
        pipeline._save_local_report = MagicMock()
        pipeline.config = SimpleNamespace(
            stock_list=["000001", "600519"],
            refresh_stock_list=lambda: None,
            report_type="simple",
            analysis_delay=0,
        )
        return pipeline

    def test_run_no_longer_sends_notifications(self):
        pipeline = self._build_batch_pipeline()
        worker_calls = []

        def _process(code, skip_analysis=False, report_type=None, analysis_query_id=None, current_time=None):
            worker_calls.append((code, threading.current_thread().name))
            return _make_result(code)

        pipeline.process_single_stock = MagicMock(side_effect=_process)

        results = pipeline.run(
            stock_codes=["000001", "600519"],
            dry_run=False,
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(len(worker_calls), 2)
        self.assertEqual(pipeline.report_output_service.thread_names, [])
        self.assertEqual(pipeline.report_output_service.max_inflight, 0)
        self.assertEqual(pipeline.report_output_service.sent_reports, [])
        self.assertEqual(pipeline.report_output_service.email_stock_codes, [])
        pipeline._save_local_report.assert_called_once()

    def test_process_single_stock_does_not_send(self):
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.fetch_and_save_stock_data = MagicMock(return_value=(True, None))
        pipeline.analyze_stock = MagicMock(return_value=_make_result("600519"))
        pipeline.report_output_service = _TrackingNotifier()

        result = pipeline.process_single_stock(
            code="600519",
            skip_analysis=False,
            report_type=ReportType.BRIEF,
            analysis_query_id="query-1",
        )

        self.assertIsNotNone(result)
        pipeline.report_output_service.generate_brief_report.assert_not_called()
        pipeline.report_output_service.send.assert_not_called()

    def test_process_single_stock_does_not_send_when_failed(self):
        pipeline = StockAnalysisPipeline.__new__(StockAnalysisPipeline)
        pipeline.fetch_and_save_stock_data = MagicMock(return_value=(True, None))
        pipeline.analyze_stock = MagicMock(return_value=_make_result("600519", success=False))
        pipeline.report_output_service = _TrackingNotifier()

        result = pipeline.process_single_stock(
            code="600519",
            skip_analysis=False,
            report_type=ReportType.BRIEF,
            analysis_query_id="query-1",
        )

        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        pipeline.report_output_service.generate_brief_report.assert_not_called()
        pipeline.report_output_service.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
