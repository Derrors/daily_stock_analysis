# -*- coding: utf-8 -*-
"""
===================================
分析相关模型
===================================

职责：
1. 定义分析请求和响应模型
2. 定义任务状态模型
3. 定义异步任务队列相关模型
"""

from typing import Optional, List, Any
from enum import Enum

from pydantic import BaseModel, Field
from src.schemas.analysis_contract import (
    AnalysisContextMeta as UnifiedAnalysisContextMeta,
    AnalysisExecution as UnifiedAnalysisExecution,
    AnalysisFeatures as UnifiedAnalysisFeatures,
    AnalysisMode as UnifiedAnalysisMode,
    AnalysisOutput as UnifiedAnalysisOutput,
    AnalysisRequest as UnifiedAnalysisRequest,
    AnalysisResponse as UnifiedAnalysisResponse,
    BatchAnalysisRequest as UnifiedBatchAnalysisRequest,
    BatchSharedOptions as UnifiedBatchSharedOptions,
    DecisionAction,
    Market,
    QuerySource,
    SelectionSource,
    StockInfo as UnifiedStockInfo,
    StockTarget as UnifiedStockTarget,
)
from src.utils.analysis_metadata import SELECTION_SOURCE_PATTERN


class TaskStatusEnum(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalyzeRequest(BaseModel):
    """Legacy API request model with bridge helpers to the v2 unified contract."""

    stock_code: Optional[str] = Field(
        None,
        description="单只股票代码",
        example="600519"
    )
    stock_codes: Optional[List[str]] = Field(
        None,
        description="多只股票代码（与 stock_code 二选一）",
        example=["600519", "000858"]
    )
    report_type: str = Field(
        "detailed",
        description="报告类型：simple(精简) / detailed(完整) / full(完整) / brief(简洁)",
        pattern="^(simple|detailed|full|brief)$",
    )
    force_refresh: bool = Field(
        False,
        description="是否强制刷新（忽略缓存）"
    )
    async_mode: bool = Field(
        False,
        description="是否使用异步模式"
    )
    stock_name: Optional[str] = Field(
        None,
        description="用户选中的股票名称（自动补全时提供）",
        example="贵州茅台"
    )
    original_query: Optional[str] = Field(
        None,
        description="用户原始输入（如茅台、gzmt、600519）",
        example="茅台"
    )
    selection_source: Optional[str] = Field(
        None,
        description="股票选择来源：manual(手动输入) | autocomplete(自动补全) | import(导入) | image(图片识别)",
        pattern=SELECTION_SOURCE_PATTERN,
        example="autocomplete"
    )
    notify: bool = Field(
        True,
        description="是否发送推送通知（Telegram/企业微信等）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "600519",
                "report_type": "detailed",
                "force_refresh": False,
                "async_mode": False,
                "stock_name": "贵州茅台",
                "original_query": "茅台",
                "selection_source": "autocomplete",
                "notify": True
            }
        }

    def iter_raw_inputs(self) -> List[str]:
        """Return raw stock inputs from the legacy API shape."""
        values: List[str] = []
        if self.stock_code:
            values.append(self.stock_code)
        if self.stock_codes:
            values.extend(self.stock_codes)
        return [value for value in values if value and str(value).strip()]

    def _report_type_to_mode(self) -> UnifiedAnalysisMode:
        if self.report_type == "brief":
            return UnifiedAnalysisMode.QUICK
        return UnifiedAnalysisMode.STANDARD

    def _selection_source_enum(self) -> SelectionSource:
        raw = (self.selection_source or "manual").strip().lower()
        try:
            return SelectionSource(raw)
        except ValueError:
            return SelectionSource.UNKNOWN

    def _build_contract_context(self, *, query_source: QuerySource) -> UnifiedAnalysisContextMeta:
        return UnifiedAnalysisContextMeta(
            query_source=query_source,
            original_query=self.original_query,
            selection_source=self._selection_source_enum(),
        )

    def to_contract_request(
        self,
        *,
        stock_input: str,
        stock_code: Optional[str] = None,
        market: Optional[str] = None,
        query_source: QuerySource = QuerySource.API,
    ) -> UnifiedAnalysisRequest:
        """Bridge one legacy API request into the v2 unified single-stock contract."""
        target_market = None
        if market:
            try:
                target_market = Market(market)
            except ValueError:
                target_market = None

        return UnifiedAnalysisRequest(
            stock=UnifiedStockTarget(
                input=stock_input,
                code=stock_code,
                market=target_market,
                name=self.stock_name,
            ),
            mode=self._report_type_to_mode(),
            strategy=None,
            features=UnifiedAnalysisFeatures(
                include_news=True,
                include_fundamental=False,
                include_market_context=False,
                include_realtime_quote=True,
                include_chip_data=False,
            ),
            output=UnifiedAnalysisOutput(
                format=("summary" if self.report_type == "brief" else "dashboard"),
                language="zh",
                verbosity=("brief" if self.report_type == "brief" else "standard"),
            ),
            execution=UnifiedAnalysisExecution(
                async_mode=self.async_mode,
                force_refresh=self.force_refresh,
                save_history=True,
                dry_run=False,
            ),
            context=self._build_contract_context(query_source=query_source),
        )

    def to_batch_contract(
        self,
        *,
        stock_inputs: List[str],
        query_source: QuerySource = QuerySource.API,
    ) -> UnifiedBatchAnalysisRequest:
        """Bridge the legacy batch API shape into the v2 unified batch contract."""
        requests = [
            self.to_contract_request(stock_input=stock_input, query_source=query_source)
            for stock_input in stock_inputs
        ]
        return UnifiedBatchAnalysisRequest(
            batch=requests,
            shared=UnifiedBatchSharedOptions(
                mode=self._report_type_to_mode(),
                strategy=None,
                features=UnifiedAnalysisFeatures(
                    include_news=True,
                    include_fundamental=False,
                    include_market_context=False,
                    include_realtime_quote=True,
                    include_chip_data=False,
                ),
                output=UnifiedAnalysisOutput(
                    format=("summary" if self.report_type == "brief" else "dashboard"),
                    language="zh",
                    verbosity=("brief" if self.report_type == "brief" else "standard"),
                ),
            ),
            execution=UnifiedAnalysisExecution(
                async_mode=True,
                force_refresh=self.force_refresh,
                save_history=True,
                dry_run=False,
            ),
        )


class AnalysisResultResponse(BaseModel):
    """Legacy API response model with compatibility helpers for v2 unified output."""

    query_id: str = Field(..., description="分析记录唯一标识")
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    report: Optional[Any] = Field(None, description="分析报告")
    created_at: str = Field(..., description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "abc123def456",
                "stock_code": "600519",
                "stock_name": "贵州茅台",
                "report": {
                    "summary": {
                        "sentiment_score": 75,
                        "operation_advice": "持有"
                    }
                },
                "created_at": "2024-01-01T12:00:00"
            }
        }

    @classmethod
    def from_unified(
        cls,
        response: UnifiedAnalysisResponse,
        *,
        query_id: str,
        created_at: str,
    ) -> "AnalysisResultResponse":
        """Build the legacy API payload shape from the unified v2 response."""
        report = {
            "stock": response.stock.model_dump(mode="json") if response.stock else None,
            "trend": response.trend.model_dump(mode="json") if response.trend else None,
            "intel": response.intel.model_dump(mode="json") if response.intel else None,
            "decision": response.decision.model_dump(mode="json") if response.decision else None,
            "dashboard": response.dashboard.model_dump(mode="json") if response.dashboard else None,
            "evidence": response.evidence.model_dump(mode="json") if response.evidence else None,
            "metadata": response.metadata.model_dump(mode="json") if response.metadata else None,
        }
        return cls(
            query_id=query_id,
            stock_code=response.stock.code,
            stock_name=response.stock.name,
            report=report,
            created_at=created_at,
        )

    def to_unified(self, *, market: Optional[str] = None) -> UnifiedAnalysisResponse:
        """Best-effort conversion from the legacy API payload to the unified v2 response."""
        market_value = Market.CN
        if market:
            try:
                market_value = Market(market)
            except ValueError:
                market_value = Market.CN

        report = self.report if isinstance(self.report, dict) else {}
        unified_payload = {
            "stock": report.get("stock") or UnifiedStockInfo(
                code=self.stock_code,
                name=self.stock_name,
                market=market_value,
            ).model_dump(mode="json"),
            "trend": report.get("trend"),
            "intel": report.get("intel"),
            "decision": report.get("decision") or {
                "action": DecisionAction.WAIT,
                "summary": report.get("summary", {}).get("analysis_summary")
                or "Legacy response has not been migrated to unified decision block.",
            },
            "dashboard": report.get("dashboard"),
            "evidence": report.get("evidence"),
            "metadata": report.get("metadata") or {
                "request_id": self.query_id,
                "generated_at": self.created_at,
                "degraded": False,
                "partial": report.get("trend") is None or report.get("intel") is None,
                "errors": [],
                "query_source": QuerySource.API,
            },
        }
        return UnifiedAnalysisResponse.model_validate(unified_payload)


class TaskAccepted(BaseModel):
    """异步任务接受响应"""
    
    task_id: str = Field(..., description="任务 ID，用于查询状态")
    status: str = Field(
        ..., 
        description="任务状态",
        pattern="^(pending|processing)$"
    )
    message: Optional[str] = Field(None, description="提示信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_abc123",
                "status": "pending",
                "message": "Analysis task accepted"
            }
        }


class BatchTaskAcceptedItem(BaseModel):
    """批量异步任务中的单个成功提交项。"""

    task_id: str = Field(..., description="任务 ID，用于查询状态")
    stock_code: str = Field(..., description="股票代码")
    status: str = Field(
        ...,
        description="任务状态",
        pattern="^(pending|processing)$"
    )
    message: Optional[str] = Field(None, description="提示信息")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_abc123",
                "stock_code": "600519",
                "status": "pending",
                "message": "分析任务已加入队列: 600519"
            }
        }


class BatchDuplicateTaskItem(BaseModel):
    """批量异步任务中的重复提交项。"""

    stock_code: str = Field(..., description="股票代码")
    existing_task_id: str = Field(..., description="已存在的任务 ID")
    message: str = Field(..., description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "600519",
                "existing_task_id": "task_existing_123",
                "message": "股票 600519 正在分析中 (task_id: task_existing_123)"
            }
        }


class BatchTaskAcceptedResponse(BaseModel):
    """批量异步任务接受响应。"""

    accepted: List[BatchTaskAcceptedItem] = Field(default_factory=list, description="成功提交的任务列表")
    duplicates: List[BatchDuplicateTaskItem] = Field(default_factory=list, description="重复而跳过的任务列表")
    message: str = Field(..., description="汇总信息")

    class Config:
        json_schema_extra = {
            "example": {
                "accepted": [
                    {
                        "task_id": "task_abc123",
                        "stock_code": "600519",
                        "status": "pending",
                        "message": "分析任务已加入队列: 600519"
                    }
                ],
                "duplicates": [
                    {
                        "stock_code": "000858",
                        "existing_task_id": "task_existing_456",
                        "message": "股票 000858 正在分析中 (task_id: task_existing_456)"
                    }
                ],
                "message": "已提交 1 个任务，1 个重复跳过"
            }
        }


class TaskStatus(BaseModel):
    """Task status model"""
    
    task_id: str = Field(..., description="任务 ID")
    status: str = Field(
        ..., 
        description="任务状态",
        pattern="^(pending|processing|completed|failed)$"
    )
    progress: Optional[int] = Field(
        None, 
        description="进度百分比 (0-100)",
        ge=0,
        le=100
    )
    result: Optional[AnalysisResultResponse] = Field(
        None, 
        description="分析结果（仅在 completed 时存在）"
    )
    error: Optional[str] = Field(
        None, 
        description="错误信息（仅在 failed 时存在）"
    )
    stock_name: Optional[str] = Field(None, description="股票名称")
    original_query: Optional[str] = Field(None, description="用户原始输入")
    selection_source: Optional[str] = Field(
        None,
        description="选择来源",
        pattern=SELECTION_SOURCE_PATTERN,
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_abc123",
                "status": "completed",
                "progress": 100,
                "result": None,
                "error": None,
                "stock_name": "贵州茅台",
                "original_query": "茅台",
                "selection_source": "autocomplete"
            }
        }


class TaskInfo(BaseModel):
    """
    Task details model

    Used for task list and SSE event delivery
    """
    
    task_id: str = Field(..., description="任务 ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(None, description="股票名称")
    status: TaskStatusEnum = Field(..., description="任务状态")
    progress: int = Field(0, description="进度百分比 (0-100)", ge=0, le=100)
    message: Optional[str] = Field(None, description="状态消息")
    report_type: str = Field("detailed", description="报告类型")
    created_at: str = Field(..., description="创建时间")
    started_at: Optional[str] = Field(None, description="开始执行时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    error: Optional[str] = Field(None, description="错误信息（仅在 failed 时存在）")
    original_query: Optional[str] = Field(None, description="用户原始输入")
    selection_source: Optional[str] = Field(
        None,
        description="选择来源",
        pattern=SELECTION_SOURCE_PATTERN,
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123def456",
                "stock_code": "600519",
                "stock_name": "贵州茅台",
                "status": "processing",
                "progress": 50,
                "message": "正在分析中...",
                "report_type": "detailed",
                "created_at": "2026-02-05T10:30:00",
                "started_at": "2026-02-05T10:30:01",
                "completed_at": None,
                "error": None,
                "original_query": "茅台",
                "selection_source": "autocomplete"
            }
        }


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    
    total: int = Field(..., description="任务总数")
    pending: int = Field(..., description="等待中的任务数")
    processing: int = Field(..., description="处理中的任务数")
    tasks: List[TaskInfo] = Field(..., description="任务列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "pending": 1,
                "processing": 2,
                "tasks": []
            }
        }


class DuplicateTaskErrorResponse(BaseModel):
    """重复任务错误响应模型"""
    
    error: str = Field("duplicate_task", description="错误类型")
    message: str = Field(..., description="错误信息")
    stock_code: str = Field(..., description="股票代码")
    existing_task_id: str = Field(..., description="已存在的任务 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "duplicate_task",
                "message": "股票 600519 正在分析中",
                "stock_code": "600519",
                "existing_task_id": "abc123def456"
            }
        }
