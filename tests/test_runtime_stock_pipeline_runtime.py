from __future__ import annotations

from src.enums import ReportType
from src.stock_analysis_skill.contracts import QuerySource
from src.stock_analysis_skill.runtime.mainline import (
    LegacySingleStockRunRequest,
    run_legacy_single_stock_mainline,
)
from src.stock_analysis_skill.runtime.stock_pipeline import StockAnalysisMainlineRuntime


class FakeResult:
    code = "600519"
    name = "贵州茅台"
    decision_type = "buy"
    operation_advice = "买入"
    confidence_level = "high"
    trend_prediction = "看多"
    sentiment_score = 85
    technical_analysis = "趋势强势。"
    trend_analysis = "均线向上。"
    analysis_summary = "趋势和基本面共振。"
    current_price = 1688.0
    change_pct = 2.5
    risk_warning = "注意波动"
    key_points = "量价齐升"
    news_summary = "新闻偏正面"
    search_performed = True
    dashboard = {"summary": "ok"}
    error_message = None
    buy_reason = "多头趋势延续"
    model_used = "gemini/test"
    report_language = "zh"
    fundamental_analysis = "估值合理"
    success = True

    def get_checklist(self):
        return ["✅ 趋势健康"]

    def get_sniper_points(self):
        return {
            "ideal_buy": 1600.0,
            "secondary_buy": 1550.0,
            "stop_loss": 1490.0,
            "take_profit": 1780.0,
        }

    def get_core_conclusion(self):
        return "继续顺势持有。"

    def get_risk_alerts(self):
        return ["波动风险"]


class DummyRunner:
    def __init__(self, result):
        self.result = result
        self.calls = []
        self.pipelines = []

    def create_pipeline(self, **kwargs):
        self.calls.append(kwargs)
        pipeline = DummyPipeline(self.result)
        self.pipelines.append(pipeline)
        return pipeline


class DummyPipeline:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def process_single_stock(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def test_runtime_uses_injected_legacy_runner() -> None:
    runner = DummyRunner(FakeResult())
    runtime = StockAnalysisMainlineRuntime(
        config_provider=lambda: {"env": "test"},
        legacy_runner=runner,
    )

    payload = runtime.analyze_stock("600519", report_type="full", query_id="q-runtime")

    assert payload is not None
    assert runner.calls
    assert runner.calls[0]["query_id"] == "q-runtime"
    assert runner.calls[0]["config"] == {"env": "test"}
    assert runner.pipelines[0].calls[0]["code"] == "600519"
    assert payload["unified_response"]["metadata"]["request_id"] == "q-runtime"


def test_runtime_unified_response_overrides_query_source() -> None:
    runner = DummyRunner(FakeResult())
    runtime = StockAnalysisMainlineRuntime(
        config_provider=lambda: {"env": "test"},
        legacy_runner=runner,
    )

    response = runtime.analyze_stock_unified(
        "600519",
        report_type="detailed",
        query_id="q-unified",
        query_source=QuerySource.CLI,
    )

    assert response is not None
    assert response.metadata.request_id == "q-unified"
    assert response.metadata.query_source == QuerySource.CLI


def test_runtime_sets_last_error_when_runner_returns_none() -> None:
    runner = DummyRunner(None)
    runtime = StockAnalysisMainlineRuntime(
        config_provider=lambda: {"env": "test"},
        legacy_runner=runner,
    )

    payload = runtime.analyze_stock("600519", query_id="q-fail")

    assert payload is None
    assert runtime.last_error == "分析股票 600519 返回空结果"


def test_mainline_helper_owns_legacy_process_single_stock_call() -> None:
    runner = DummyRunner(FakeResult())
    request = LegacySingleStockRunRequest(
        config={"env": "test"},
        stock_code="600519",
        report_type=ReportType.FULL,
        query_id="q-helper",
    )

    result = run_legacy_single_stock_mainline(runner, request)

    assert result is not None
    assert runner.calls[0]["query_id"] == "q-helper"
    assert runner.pipelines[0].calls[0]["code"] == "600519"
    assert runner.pipelines[0].calls[0]["report_type"] == ReportType.FULL
