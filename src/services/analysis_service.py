# -*- coding: utf-8 -*-
"""
===================================
分析服务兼容层
===================================

职责：
1. 兼容旧 `AnalysisService` 调用路径
2. 将同步股票分析请求转发到 `stock_analysis_skill` 主 runtime
3. 为旧测试/调用方保留少量 bridge 方法
"""

import logging
from typing import Optional, Dict, Any, Callable

from src.stock_analysis_skill.runtime.stock_pipeline import StockAnalysisMainlineRuntime
from src.schemas.analysis_contract import (
    AnalysisResponse,
    ChecklistStatus,
    ConfidenceLevel,
    DecisionAction,
    Market,
    QuerySource,
    TrendStatus,
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    分析服务兼容层。

    新的同步主链真相源已迁到 `src.stock_analysis_skill.runtime.stock_pipeline`；
    本类继续保留是为了兼容旧导入路径与旧调用方。
    """
    
    def __init__(self):
        """初始化兼容服务壳。"""
        self.runtime = StockAnalysisMainlineRuntime()
        self.last_error: Optional[str] = None
    
    def analyze_stock(
        self,
        stock_code: str,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        执行股票分析（兼容入口）。

        Args:
            stock_code: 股票代码
            report_type: 报告类型 (simple/detailed)
            force_refresh: 是否强制刷新
            query_id: 查询 ID（可选）

        Returns:
            兼容旧调用方的结果字典。
        """
        try:
            self.last_error = None
            payload = self.runtime.analyze_stock(
                stock_code=stock_code,
                report_type=report_type,
                force_refresh=force_refresh,
                query_id=query_id,
                progress_callback=progress_callback,
            )
            self.last_error = self.runtime.last_error
            return payload
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
        progress_callback: Optional[Callable[[int, str], None]] = None,
        query_source: QuerySource = QuerySource.API,
    ) -> Optional[AnalysisResponse]:
        """Unified analysis entry that returns the v2 response contract."""
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
            return AnalysisResponse.model_validate(unified_payload)
        return None

    # --- Compatibility bridge methods kept for older tests/callers ---

    def _resolve_market(self, stock_code: str) -> Market:
        return self.runtime.resolve_market(stock_code)

    def _map_decision_action(self, result: Any) -> DecisionAction:
        return self.runtime.map_decision_action(result)

    def _map_confidence(self, result: Any) -> ConfidenceLevel:
        return self.runtime.map_confidence(result)

    def _map_trend_status(self, result: Any) -> TrendStatus:
        return self.runtime.map_trend_status(result)

    def _map_checklist_status(self, item: str) -> ChecklistStatus:
        return self.runtime.map_checklist_status(item)

    def _build_unified_analysis_response(
        self,
        result: Any,
        *,
        query_id: str,
        report_type: str,
        query_source: QuerySource,
    ) -> AnalysisResponse:
        return self.runtime.build_unified_analysis_response(
            result,
            query_id=query_id,
            report_type=report_type,
            query_source=query_source,
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
        return self.runtime.build_legacy_analysis_response(
            result,
            query_id=query_id,
            report_type=report_type,
        )
