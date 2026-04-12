# -*- coding: utf-8 -*-
"""
===================================
分析服务层
===================================

职责：
1. 封装股票分析逻辑
2. 调用 analyzer 和 pipeline 执行分析
3. 保存分析结果到数据库
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Callable

from data_provider import is_hk_stock_code, is_us_stock_code
from src.repositories.analysis_repo import AnalysisRepository
from src.report_language import (
    get_sentiment_label,
    get_localized_stock_name,
    localize_operation_advice,
    localize_trend_prediction,
    normalize_report_language,
)
from src.schemas.analysis_contract import (
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

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    分析服务
    
    封装股票分析相关的业务逻辑
    """
    
    def __init__(self):
        """初始化分析服务"""
        self.repo = AnalysisRepository()
        self.last_error: Optional[str] = None
    
    def analyze_stock(
        self,
        stock_code: str,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        send_notification: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        执行股票分析
        
        Args:
            stock_code: 股票代码
            report_type: 报告类型 (simple/detailed)
            force_refresh: 是否强制刷新
            query_id: 查询 ID（可选）
            send_notification: 是否发送通知（API 触发默认发送）
            
        Returns:
            分析结果字典，包含:
            - stock_code: 股票代码
            - stock_name: 股票名称
            - report: 分析报告
        """
        try:
            self.last_error = None
            # 导入分析相关模块
            from src.config import get_config
            from src.core.pipeline import StockAnalysisPipeline
            from src.enums import ReportType
            
            # 生成 query_id
            if query_id is None:
                query_id = uuid.uuid4().hex
            
            # 获取配置
            config = get_config()
            
            # 创建分析流水线
            pipeline = StockAnalysisPipeline(
                config=config,
                query_id=query_id,
                query_source="api",
                progress_callback=progress_callback,
            )
            
            # 确定报告类型 (API: simple/detailed/full/brief -> ReportType)
            rt = ReportType.from_str(report_type)
            
            # 执行分析
            result = pipeline.process_single_stock(
                code=stock_code,
                skip_analysis=False,
                single_stock_notify=send_notification,
                report_type=rt,
            )
            
            if result is None:
                logger.warning(f"分析股票 {stock_code} 返回空结果")
                self.last_error = self.last_error or f"分析股票 {stock_code} 返回空结果"
                return None

            if not getattr(result, "success", True):
                self.last_error = getattr(result, "error_message", None) or f"分析股票 {stock_code} 失败"
                logger.warning(f"分析股票 {stock_code} 未成功完成: {self.last_error}")
                return None
            
            # 构建统一响应，再桥接回当前兼容返回结构
            unified_response = self._build_unified_analysis_response(
                result,
                query_id=query_id,
                report_type=rt.value,
                query_source=QuerySource.API,
            )
            legacy_response = self._build_analysis_response(result, query_id, report_type=rt.value)
            legacy_response["unified_response"] = unified_response.model_dump(mode="json")
            return legacy_response
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"分析股票 {stock_code} 失败: {e}", exc_info=True)
            return None
    
    def analyze_stock_unified(
        self,
        stock_code: str,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        send_notification: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        query_source: QuerySource = QuerySource.API,
    ) -> Optional[AnalysisResponse]:
        """Unified analysis entry that returns the v2 response contract."""
        payload = self.analyze_stock(
            stock_code=stock_code,
            report_type=report_type,
            force_refresh=force_refresh,
            query_id=query_id,
            send_notification=send_notification,
            progress_callback=progress_callback,
        )
        if payload is None:
            return None
        unified_payload = payload.get("unified_response")
        if unified_payload:
            return AnalysisResponse.model_validate(unified_payload)
        return None

    def _resolve_market(self, stock_code: str) -> Market:
        if is_us_stock_code(stock_code):
            return Market.US
        if is_hk_stock_code(stock_code):
            return Market.HK
        return Market.CN

    def _map_decision_action(self, result: Any) -> DecisionAction:
        decision_type = str(getattr(result, "decision_type", "") or "").strip().lower()
        if decision_type == "buy":
            return DecisionAction.BUY
        if decision_type == "sell":
            return DecisionAction.SELL
        operation_advice = str(getattr(result, "operation_advice", "") or "").strip().lower()
        if operation_advice in {"观望", "watch", "wait", "wait and see"}:
            return DecisionAction.WAIT
        return DecisionAction.HOLD

    def _map_confidence(self, result: Any) -> ConfidenceLevel:
        raw = str(getattr(result, "confidence_level", "") or "").strip().lower()
        if raw in {"高", "high"}:
            return ConfidenceLevel.HIGH
        if raw in {"低", "low"}:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.MEDIUM

    def _map_trend_status(self, result: Any) -> TrendStatus:
        raw = str(getattr(result, "trend_prediction", "") or "").strip().lower()
        if any(key in raw for key in ["强烈看多", "看多", "bull", "uptrend"]):
            return TrendStatus.BULL
        if any(key in raw for key in ["震荡", "neutral", "sideways"]):
            return TrendStatus.CONSOLIDATION
        if any(key in raw for key in ["强烈看空", "看空", "bear", "downtrend"]):
            return TrendStatus.BEAR
        return TrendStatus.CONSOLIDATION

    def _map_checklist_status(self, item: str) -> ChecklistStatus:
        if item.startswith("✅"):
            return ChecklistStatus.PASS
        if item.startswith("⚠") or item.startswith("⚠️"):
            return ChecklistStatus.WARN
        if item.startswith("❌"):
            return ChecklistStatus.FAIL
        return ChecklistStatus.WARN

    def _build_unified_analysis_response(
        self,
        result: Any,
        *,
        query_id: str,
        report_type: str,
        query_source: QuerySource,
    ) -> AnalysisResponse:
        """Build the unified v2 analysis response contract from AnalysisResult."""
        report_language = normalize_report_language(getattr(result, "report_language", "zh"))
        stock_name = get_localized_stock_name(getattr(result, "name", None), result.code, report_language)
        market = self._resolve_market(result.code)
        decision_action = self._map_decision_action(result)
        confidence = self._map_confidence(result)
        trend_status = self._map_trend_status(result)
        checklist = [
            DashboardChecklistItem(item=item, status=self._map_checklist_status(item))
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

    def _build_analysis_response(
        self,
        result: Any,
        query_id: str,
        report_type: str = "detailed",
    ) -> Dict[str, Any]:
        """
        构建分析响应
        
        Args:
            result: AnalysisResult 对象
            query_id: 查询 ID
            report_type: 归一化后的报告类型
            
        Returns:
            格式化的响应字典
        """
        # 获取狙击点位
        sniper_points = {}
        if hasattr(result, 'get_sniper_points'):
            sniper_points = result.get_sniper_points() or {}
        
        # 计算情绪标签
        report_language = normalize_report_language(getattr(result, "report_language", "zh"))
        sentiment_label = get_sentiment_label(result.sentiment_score, report_language)
        stock_name = get_localized_stock_name(getattr(result, "name", None), result.code, report_language)
        
        # 构建报告结构
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
            }
        }
        
        return {
            "stock_code": result.code,
            "stock_name": stock_name,
            "report": report,
        }
