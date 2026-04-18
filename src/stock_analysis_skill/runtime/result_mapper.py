# -*- coding: utf-8 -*-
"""Result-mapping helpers for the skill-first stock-analysis runtime."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from src.report_language import (
    get_localized_stock_name,
    get_sentiment_label,
    localize_operation_advice,
    localize_trend_prediction,
    normalize_report_language,
)
from src.stock_analysis_skill.contracts import (
    AnalysisResponse,
    ChecklistStatus,
    ConfidenceLevel,
    DashboardBlock,
    DashboardChecklistItem,
    DataCompleteness,
    DecisionAction,
    DecisionBlock,
    EvidenceBlock,
    IntelBlock,
    Market,
    MetadataBlock,
    QuerySource,
    StockInfo,
    TrendBlock,
    TrendStatus,
)


def resolve_market(stock_code: str) -> Market:
    try:
        from src.stock_analysis_skill.providers import is_hk_stock_code, is_us_stock_code
    except Exception:
        is_hk_stock_code = lambda _code: False  # type: ignore[assignment]
        is_us_stock_code = lambda _code: False  # type: ignore[assignment]
    if is_us_stock_code(stock_code):
        return Market.US
    if is_hk_stock_code(stock_code):
        return Market.HK
    return Market.CN


def map_decision_action(result: Any) -> DecisionAction:
    decision_type = str(getattr(result, "decision_type", "") or "").strip().lower()
    if decision_type == "buy":
        return DecisionAction.BUY
    if decision_type == "sell":
        return DecisionAction.SELL
    operation_advice = str(getattr(result, "operation_advice", "") or "").strip().lower()
    if operation_advice in {"观望", "watch", "wait", "wait and see"}:
        return DecisionAction.WAIT
    return DecisionAction.HOLD


def map_confidence(result: Any) -> ConfidenceLevel:
    raw = str(getattr(result, "confidence_level", "") or "").strip().lower()
    if raw in {"高", "high"}:
        return ConfidenceLevel.HIGH
    if raw in {"低", "low"}:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.MEDIUM


def map_trend_status(result: Any) -> TrendStatus:
    raw = str(getattr(result, "trend_prediction", "") or "").strip().lower()
    if any(key in raw for key in ["强烈看多", "看多", "bull", "uptrend"]):
        return TrendStatus.BULL
    if any(key in raw for key in ["震荡", "neutral", "sideways"]):
        return TrendStatus.CONSOLIDATION
    if any(key in raw for key in ["强烈看空", "看空", "bear", "downtrend"]):
        return TrendStatus.BEAR
    return TrendStatus.CONSOLIDATION


def map_checklist_status(item: str) -> ChecklistStatus:
    if item.startswith("✅"):
        return ChecklistStatus.PASS
    if item.startswith("⚠") or item.startswith("⚠️"):
        return ChecklistStatus.WARN
    if item.startswith("❌"):
        return ChecklistStatus.FAIL
    return ChecklistStatus.WARN


def build_unified_analysis_response(
    result: Any,
    *,
    query_id: str,
    report_type: str,
    query_source: QuerySource,
) -> AnalysisResponse:
    report_language = normalize_report_language(getattr(result, "report_language", "zh"))
    stock_name = get_localized_stock_name(getattr(result, "name", None), result.code, report_language)
    market = resolve_market(result.code)
    decision_action = map_decision_action(result)
    confidence = map_confidence(result)
    trend_status = map_trend_status(result)
    checklist = [
        DashboardChecklistItem(item=item, status=map_checklist_status(item))
        for item in (result.get_checklist() if hasattr(result, "get_checklist") else [])
    ]
    sniper_points = result.get_sniper_points() if hasattr(result, "get_sniper_points") else {}

    trend_block = TrendBlock(
        status=trend_status,
        status_text=getattr(result, "trend_prediction", None),
        signal=decision_action,
        signal_text=localize_operation_advice(getattr(result, "operation_advice", ""), report_language),
        score=max(0, min(int(getattr(result, "sentiment_score", 50) or 50), 100)),
        summary=(
            getattr(result, "technical_analysis", None)
            or getattr(result, "trend_analysis", None)
            or getattr(result, "analysis_summary", "")
            or ""
        ).strip(),
        metrics={
            "current_price": getattr(result, "current_price", None),
            "change_pct": getattr(result, "change_pct", None),
        },
        supports=[
            value
            for value in [sniper_points.get("ideal_buy"), sniper_points.get("secondary_buy")]
            if isinstance(value, (int, float))
        ],
        resistances=[
            value
            for value in [sniper_points.get("take_profit")]
            if isinstance(value, (int, float))
        ],
        risk_factors=[getattr(result, "risk_warning", "")] if getattr(result, "risk_warning", None) else [],
    )

    intel_block = IntelBlock(
        summary=(getattr(result, "news_summary", "") or "").strip(),
        highlights=[getattr(result, "key_points", "")] if getattr(result, "key_points", None) else [],
        risks=(
            result.get_risk_alerts()
            if hasattr(result, "get_risk_alerts")
            else ([getattr(result, "risk_warning", "")] if getattr(result, "risk_warning", None) else [])
        ),
        news_items=[],
    )

    decision_block = DecisionBlock(
        action=decision_action,
        action_text=localize_operation_advice(getattr(result, "operation_advice", ""), report_language),
        confidence=confidence,
        summary=(getattr(result, "analysis_summary", "") or getattr(result, "buy_reason", "") or "").strip(),
        reasoning=[
            value
            for value in [getattr(result, "buy_reason", None), getattr(result, "technical_analysis", None)]
            if value
        ],
        warnings=[getattr(result, "risk_warning", "")] if getattr(result, "risk_warning", None) else [],
    )

    dashboard_block = DashboardBlock(
        one_sentence=result.get_core_conclusion() if hasattr(result, "get_core_conclusion") else (getattr(result, "analysis_summary", "") or ""),
        positioning=getattr(result, "operation_advice", None),
        battle_plan={
            "ideal_entry": sniper_points.get("ideal_buy"),
            "secondary_entry": sniper_points.get("secondary_buy"),
            "stop_loss": sniper_points.get("stop_loss"),
            "take_profit": sniper_points.get("take_profit"),
        },
        checklist=checklist,
    )

    evidence_block = EvidenceBlock(
        providers={},
        used_features=[
            feature
            for feature, enabled in {
                "trend_analysis": True,
                "news_search": bool(getattr(result, "search_performed", False)),
                "dashboard": bool(getattr(result, "dashboard", None)),
            }.items()
            if enabled
        ],
        data_completeness={
            "trend": DataCompleteness.FULL,
            "intel": DataCompleteness.PARTIAL
            if getattr(result, "search_performed", False)
            else DataCompleteness.NOT_REQUESTED,
            "dashboard": DataCompleteness.FULL
            if getattr(result, "dashboard", None)
            else DataCompleteness.PARTIAL,
        },
    )

    metadata_block = MetadataBlock(
        request_id=query_id,
        generated_at=datetime.now().isoformat(),
        mode=None,
        degraded=not bool(getattr(result, "search_performed", False))
        and bool(getattr(result, "news_summary", "")) is False,
        partial=not bool(getattr(result, "dashboard", None)),
        errors=[getattr(result, "error_message", "")] if getattr(result, "error_message", None) else [],
        query_source=query_source,
    )

    return AnalysisResponse(
        stock=StockInfo(
            code=result.code,
            name=stock_name,
            market=market,
            input=result.code,
        ),
        trend=trend_block,
        intel=intel_block,
        decision=decision_block,
        dashboard=dashboard_block,
        evidence=evidence_block,
        metadata=metadata_block,
    )


def build_runtime_payload(
    result: Any,
    *,
    query_id: str,
    report_type: str = "detailed",
) -> Dict[str, Any]:
    sniper_points = result.get_sniper_points() if hasattr(result, "get_sniper_points") else {}
    report_language = normalize_report_language(getattr(result, "report_language", "zh"))
    sentiment_label = get_sentiment_label(result.sentiment_score, report_language)
    stock_name = get_localized_stock_name(getattr(result, "name", None), result.code, report_language)

    report = {
        "meta": {
            "query_id": query_id,
            "stock_code": result.code,
            "stock_name": stock_name,
            "report_type": report_type,
            "report_language": report_language,
            "current_price": result.current_price,
            "change_pct": result.change_pct,
            "model_used": getattr(result, "model_used", None),
        },
        "summary": {
            "analysis_summary": result.analysis_summary,
            "operation_advice": localize_operation_advice(result.operation_advice, report_language),
            "trend_prediction": localize_trend_prediction(result.trend_prediction, report_language),
            "sentiment_score": result.sentiment_score,
            "sentiment_label": sentiment_label,
        },
        "strategy": {
            "ideal_buy": sniper_points.get("ideal_buy"),
            "secondary_buy": sniper_points.get("secondary_buy"),
            "stop_loss": sniper_points.get("stop_loss"),
            "take_profit": sniper_points.get("take_profit"),
        },
        "details": {
            "news_summary": result.news_summary,
            "technical_analysis": result.technical_analysis,
            "fundamental_analysis": result.fundamental_analysis,
            "risk_warning": result.risk_warning,
        },
    }

    return {
        "stock_code": result.code,
        "stock_name": stock_name,
        "report": report,
    }


__all__ = [
    "build_runtime_payload",
    "build_unified_analysis_response",
    "map_checklist_status",
    "map_confidence",
    "map_decision_action",
    "map_trend_status",
    "resolve_market",
]
