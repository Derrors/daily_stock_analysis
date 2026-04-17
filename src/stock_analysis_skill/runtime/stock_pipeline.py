# -*- coding: utf-8 -*-
"""Skill-first synchronous stock-analysis mainline runtime.

This module is the first internalization step for Phase F. It keeps the existing
`src.core.pipeline.StockAnalysisPipeline` as the low-level execution engine but
moves the synchronous orchestration entrypoint into the canonical
`src.stock_analysis_skill` namespace.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from src.config import get_config
from src.core.pipeline import StockAnalysisPipeline
from src.enums import ReportType
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


class StockAnalysisMainlineRuntime:
    """Canonical synchronous analysis runtime for skill-facing entrypoints."""

    def __init__(self):
        self.last_error: Optional[str] = None

    def analyze_stock(
        self,
        stock_code: str,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Run the synchronous stock-analysis mainline and return the legacy payload."""
        try:
            self.last_error = None
            if query_id is None:
                query_id = uuid.uuid4().hex

            config = get_config()
            pipeline = StockAnalysisPipeline(
                config=config,
                query_id=query_id,
                query_source="api",
                progress_callback=progress_callback,
            )
            rt = ReportType.from_str(report_type)
            result = pipeline.process_single_stock(
                code=stock_code,
                skip_analysis=False,
                report_type=rt,
            )

            if result is None:
                self.last_error = self.last_error or f"分析股票 {stock_code} 返回空结果"
                return None
            if not getattr(result, "success", True):
                self.last_error = getattr(result, "error_message", None) or f"分析股票 {stock_code} 失败"
                return None

            unified_response = self.build_unified_analysis_response(
                result,
                query_id=query_id,
                report_type=rt.value,
                query_source=QuerySource.API,
            )
            legacy_response = self.build_legacy_analysis_response(
                result,
                query_id=query_id,
                report_type=rt.value,
            )
            legacy_response["unified_response"] = unified_response.model_dump(mode="json")
            return legacy_response
        except Exception as exc:
            self.last_error = str(exc)
            return None

    def analyze_stock_unified(
        self,
        stock_code: str,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        query_source: QuerySource = QuerySource.API,
    ) -> Optional[AnalysisResponse]:
        """Run the synchronous mainline and return the v2 unified response."""
        payload = self.analyze_stock(
            stock_code=stock_code,
            report_type=report_type,
            force_refresh=force_refresh,
            query_id=query_id,
            progress_callback=progress_callback,
        )
        if payload is None:
            return None
        unified_payload = payload.get("unified_response")
        if unified_payload:
            response = AnalysisResponse.model_validate(unified_payload)
            response.metadata.query_source = query_source
            return response
        return None

    @staticmethod
    def resolve_market(stock_code: str) -> Market:
        try:
            from data_provider import is_hk_stock_code, is_us_stock_code
        except Exception:
            is_hk_stock_code = lambda _code: False  # type: ignore[assignment]
            is_us_stock_code = lambda _code: False  # type: ignore[assignment]
        if is_us_stock_code(stock_code):
            return Market.US
        if is_hk_stock_code(stock_code):
            return Market.HK
        return Market.CN

    @staticmethod
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

    @staticmethod
    def map_confidence(result: Any) -> ConfidenceLevel:
        raw = str(getattr(result, "confidence_level", "") or "").strip().lower()
        if raw in {"高", "high"}:
            return ConfidenceLevel.HIGH
        if raw in {"低", "low"}:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.MEDIUM

    @staticmethod
    def map_trend_status(result: Any) -> TrendStatus:
        raw = str(getattr(result, "trend_prediction", "") or "").strip().lower()
        if any(key in raw for key in ["强烈看多", "看多", "bull", "uptrend"]):
            return TrendStatus.BULL
        if any(key in raw for key in ["震荡", "neutral", "sideways"]):
            return TrendStatus.CONSOLIDATION
        if any(key in raw for key in ["强烈看空", "看空", "bear", "downtrend"]):
            return TrendStatus.BEAR
        return TrendStatus.CONSOLIDATION

    @staticmethod
    def map_checklist_status(item: str) -> ChecklistStatus:
        if item.startswith("✅"):
            return ChecklistStatus.PASS
        if item.startswith("⚠") or item.startswith("⚠️"):
            return ChecklistStatus.WARN
        if item.startswith("❌"):
            return ChecklistStatus.FAIL
        return ChecklistStatus.WARN

    def build_unified_analysis_response(
        self,
        result: Any,
        *,
        query_id: str,
        report_type: str,
        query_source: QuerySource,
    ) -> AnalysisResponse:
        report_language = normalize_report_language(getattr(result, "report_language", "zh"))
        stock_name = get_localized_stock_name(getattr(result, "name", None), result.code, report_language)
        market = self.resolve_market(result.code)
        decision_action = self.map_decision_action(result)
        confidence = self.map_confidence(result)
        trend_status = self.map_trend_status(result)
        checklist = [
            DashboardChecklistItem(item=item, status=self.map_checklist_status(item))
            for item in (result.get_checklist() if hasattr(result, "get_checklist") else [])
        ]
        sniper_points = result.get_sniper_points() if hasattr(result, "get_sniper_points") else {}

        trend_block = TrendBlock(
            status=trend_status,
            status_text=getattr(result, "trend_prediction", None),
            signal=decision_action,
            signal_text=localize_operation_advice(getattr(result, "operation_advice", ""), report_language),
            score=max(0, min(int(getattr(result, "sentiment_score", 50) or 50), 100)),
            summary=(getattr(result, "technical_analysis", None) or getattr(result, "trend_analysis", None) or getattr(result, "analysis_summary", "") or "").strip(),
            metrics={
                "current_price": getattr(result, "current_price", None),
                "change_pct": getattr(result, "change_pct", None),
            },
            supports=[value for value in [sniper_points.get("ideal_buy"), sniper_points.get("secondary_buy")] if isinstance(value, (int, float))],
            resistances=[value for value in [sniper_points.get("take_profit")] if isinstance(value, (int, float))],
            risk_factors=[getattr(result, "risk_warning", "")] if getattr(result, "risk_warning", None) else [],
        )

        intel_block = IntelBlock(
            summary=(getattr(result, "news_summary", "") or "").strip(),
            highlights=[getattr(result, "key_points", "")] if getattr(result, "key_points", None) else [],
            risks=result.get_risk_alerts() if hasattr(result, "get_risk_alerts") else ([getattr(result, "risk_warning", "")] if getattr(result, "risk_warning", None) else []),
            news_items=[],
        )

        decision_block = DecisionBlock(
            action=decision_action,
            action_text=localize_operation_advice(getattr(result, "operation_advice", ""), report_language),
            confidence=confidence,
            summary=(getattr(result, "analysis_summary", "") or getattr(result, "buy_reason", "") or "").strip(),
            reasoning=[value for value in [getattr(result, "buy_reason", None), getattr(result, "technical_analysis", None)] if value],
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
                "intel": DataCompleteness.PARTIAL if getattr(result, "search_performed", False) else DataCompleteness.NOT_REQUESTED,
                "dashboard": DataCompleteness.FULL if getattr(result, "dashboard", None) else DataCompleteness.PARTIAL,
            },
        )

        metadata_block = MetadataBlock(
            request_id=query_id,
            generated_at=datetime.now().isoformat(),
            mode=None,
            degraded=not bool(getattr(result, "search_performed", False)) and bool(getattr(result, "news_summary", "")) is False,
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

    def build_legacy_analysis_response(
        self,
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


class StockAnalysisSkillPipeline(StockAnalysisPipeline):
    """Canonical skill-runtime alias over the existing low-level pipeline engine."""
