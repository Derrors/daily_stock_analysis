from __future__ import annotations

from src.stock_analysis_skill.contracts import QuerySource
from src.stock_analysis_skill.runtime.result_mapper import (
    build_runtime_payload,
    build_unified_analysis_response,
    map_checklist_status,
)


class FakeResult:
    code = "600519"
    name = "贵州茅台"
    decision_type = "buy"
    operation_advice = "买入"
    confidence_level = "high"
    trend_prediction = "看多"
    sentiment_score = 82
    technical_analysis = "趋势保持强势。"
    trend_analysis = "均线多头排列。"
    analysis_summary = "基本面稳健，趋势向上。"
    current_price = 1688.0
    change_pct = 2.3
    risk_warning = "注意短期波动"
    key_points = "量价配合良好"
    news_summary = "近期新闻偏正面。"
    search_performed = True
    dashboard = {"summary": "ok"}
    error_message = None
    buy_reason = "趋势与基本面共振"
    model_used = "gemini/test"
    report_language = "zh"
    fundamental_analysis = "估值处于合理区间"

    def get_checklist(self):
        return ["✅ 趋势向上", "⚠ 注意回撤"]

    def get_sniper_points(self):
        return {
            "ideal_buy": 1600.0,
            "secondary_buy": 1550.0,
            "stop_loss": 1490.0,
            "take_profit": 1780.0,
        }

    def get_core_conclusion(self):
        return "继续沿趋势持有。"

    def get_risk_alerts(self):
        return ["估值波动风险"]


def test_build_unified_analysis_response() -> None:
    response = build_unified_analysis_response(
        FakeResult(),
        query_id="q1",
        report_type="full",
        query_source=QuerySource.CLI,
    )

    assert response.stock.code == "600519"
    assert response.decision.action.value == "buy"
    assert response.trend is not None
    assert response.trend.score == 82
    assert response.dashboard is not None
    assert response.metadata.request_id == "q1"
    assert response.metadata.query_source == QuerySource.CLI


def test_build_runtime_payload() -> None:
    payload = build_runtime_payload(
        FakeResult(),
        query_id="q2",
        report_type="full",
    )

    assert payload["stock_code"] == "600519"
    assert payload["report"]["meta"]["query_id"] == "q2"
    assert payload["report"]["summary"]["sentiment_score"] == 82
    assert payload["report"]["strategy"]["ideal_buy"] == 1600.0


def test_map_checklist_status_defaults_to_warn() -> None:
    assert map_checklist_status("普通提示").value == "warn"
    assert map_checklist_status("✅ 通过").value == "pass"
