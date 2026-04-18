# -*- coding: utf-8 -*-
"""Skill-first synchronous stock-analysis mainline runtime.

This module is the first internalization step for Phase F. It keeps the existing
`src.core.pipeline.StockAnalysisPipeline` as the low-level execution engine but
moves the synchronous orchestration entrypoint into the canonical
`src.stock_analysis_skill` namespace.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Dict, Optional

from src.config import get_config
from src.enums import ReportType
from src.stock_analysis_skill.contracts import (
    AnalysisResponse,
    QuerySource,
)
from src.stock_analysis_skill.runtime.legacy_pipeline_adapter import LegacyPipelineRunner
from src.stock_analysis_skill.runtime.mainline import (
    LegacySingleStockRunRequest,
    run_legacy_single_stock_mainline,
)
from src.stock_analysis_skill.runtime.result_mapper import (
    build_runtime_payload,
    build_unified_analysis_response,
    map_checklist_status,
    map_confidence,
    map_decision_action,
    map_trend_status,
    resolve_market,
)


class StockAnalysisMainlineRuntime:
    """Canonical synchronous analysis runtime for skill-facing entrypoints."""

    def __init__(
        self,
        *,
        config_provider: Callable[[], Any] = get_config,
        legacy_runner: Optional[LegacyPipelineRunner] = None,
    ):
        self._config_provider = config_provider
        self.legacy_runner = legacy_runner or LegacyPipelineRunner()
        self.last_error: Optional[str] = None

    def analyze_stock(
        self,
        stock_code: str,
        report_type: str = "detailed",
        force_refresh: bool = False,
        query_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Run the synchronous stock-analysis mainline and return runtime payload."""
        try:
            self.last_error = None
            if query_id is None:
                query_id = uuid.uuid4().hex

            config = self._config_provider()
            rt = ReportType.from_str(report_type)
            request = LegacySingleStockRunRequest(
                config=config,
                stock_code=stock_code,
                report_type=rt,
                query_id=query_id,
                progress_callback=progress_callback,
                force_refresh=force_refresh,
            )
            result = run_legacy_single_stock_mainline(self.legacy_runner, request)

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
            runtime_payload = self.build_runtime_payload(
                result,
                query_id=query_id,
                report_type=rt.value,
            )
            runtime_payload["unified_response"] = unified_response.model_dump(mode="json")
            return runtime_payload
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
    def resolve_market(stock_code: str):
        return resolve_market(stock_code)

    @staticmethod
    def map_decision_action(result: Any):
        return map_decision_action(result)

    @staticmethod
    def map_confidence(result: Any):
        return map_confidence(result)

    @staticmethod
    def map_trend_status(result: Any):
        return map_trend_status(result)

    @staticmethod
    def map_checklist_status(item: str):
        return map_checklist_status(item)

    def build_unified_analysis_response(
        self,
        result: Any,
        *,
        query_id: str,
        report_type: str,
        query_source: QuerySource,
    ) -> AnalysisResponse:
        return build_unified_analysis_response(
            result,
            query_id=query_id,
            report_type=report_type,
            query_source=query_source,
        )

    def build_runtime_payload(
        self,
        result: Any,
        *,
        query_id: str,
        report_type: str = "detailed",
    ) -> Dict[str, Any]:
        return build_runtime_payload(
            result,
            query_id=query_id,
            report_type=report_type,
        )
