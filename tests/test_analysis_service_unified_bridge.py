from types import SimpleNamespace

from src.schemas.analysis_contract import DecisionAction, Market, QuerySource
from src.services.analysis_service import AnalysisService


class _FakeAnalysisResult(SimpleNamespace):
    def get_core_conclusion(self):
        return "趋势偏强，可关注回踩机会"

    def get_sniper_points(self):
        return {
            "ideal_buy": 1668.4,
            "secondary_buy": 1649.1,
            "stop_loss": 1618.0,
            "take_profit": 1748.0,
        }

    def get_checklist(self):
        return ["✅ 多头排列", "⚠️ 不追高"]

    def get_risk_alerts(self):
        return ["估值偏高，防追高"]


def test_build_unified_analysis_response_maps_analysis_result() -> None:
    service = AnalysisService()
    result = _FakeAnalysisResult(
        code="600519",
        name="贵州茅台",
        sentiment_score=78,
        trend_prediction="看多",
        operation_advice="买入",
        confidence_level="中",
        report_language="zh",
        dashboard={"core_conclusion": {"one_sentence": "趋势偏强，可关注回踩机会"}},
        technical_analysis="均线多头，趋势偏强",
        trend_analysis="上升趋势延续",
        analysis_summary="趋势偏强，但不宜追高",
        buy_reason="MA 多头排列且无明显利空",
        risk_warning="接近短期压力位",
        news_summary="近期未见明显利空",
        search_performed=True,
        error_message=None,
        current_price=1685.0,
        change_pct=1.2,
        decision_type="buy",
    )

    unified = service._build_unified_analysis_response(
        result,
        query_id="req-1",
        report_type="detailed",
        query_source=QuerySource.API,
    )

    assert unified.stock.code == "600519"
    assert unified.stock.market == Market.CN
    assert unified.decision.action == DecisionAction.BUY
    assert unified.dashboard is not None
    assert unified.dashboard.one_sentence == "趋势偏强，可关注回踩机会"
    assert unified.metadata.request_id == "req-1"
    assert unified.metadata.query_source == QuerySource.API
