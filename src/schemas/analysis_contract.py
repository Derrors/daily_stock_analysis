# -*- coding: utf-8 -*-
"""Unified request/response contracts for stock analysis.

These models are the code-level landing zone for the v2 planning docs:
- analysis request schema
- analysis response schema

They intentionally avoid coupling to transport details (API/Bot/Web) so the
same contracts can be reused by CLI, API, Agent tools, and future skill
scripts.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class Market(str, Enum):
    CN = "cn"
    HK = "hk"
    US = "us"


class AnalysisMode(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    STRATEGY = "strategy"
    CONTEXT_ONLY = "context_only"


class OutputFormat(str, Enum):
    DASHBOARD = "dashboard"
    SUMMARY = "summary"
    CONTEXT = "context"
    MARKDOWN = "markdown"


class OutputVerbosity(str, Enum):
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


class QuerySource(str, Enum):
    CLI = "cli"
    API = "api"
    BOT = "bot"
    WEB = "web"
    AGENT = "agent"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class SelectionSource(str, Enum):
    MANUAL = "manual"
    AUTOCOMPLETE = "autocomplete"
    IMPORT = "import"
    IMAGE = "image"
    HISTORY = "history"
    BATCH = "batch"
    STRATEGY = "strategy"
    UNKNOWN = "unknown"


class DecisionAction(str, Enum):
    BUY = "buy"
    HOLD = "hold"
    WAIT = "wait"
    SELL = "sell"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrendStatus(str, Enum):
    BULL = "bull"
    WEAK_BULL = "weak_bull"
    CONSOLIDATION = "consolidation"
    WEAK_BEAR = "weak_bear"
    BEAR = "bear"


class ChecklistStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class DataCompleteness(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    MISSING = "missing"
    NOT_REQUESTED = "not_requested"


class StockTarget(BaseModel):
    """Normalized stock target for a single analysis request."""

    model_config = ConfigDict(str_strip_whitespace=True)

    input: str = Field(..., min_length=1, description="Raw user input or stock code")
    code: Optional[str] = Field(default=None, description="Canonical stock code")
    market: Optional[Market] = Field(default=None, description="Resolved market")
    name: Optional[str] = Field(default=None, description="Resolved stock name")


class AnalysisFeatures(BaseModel):
    include_news: bool = True
    include_fundamental: bool = False
    include_market_context: bool = False
    include_realtime_quote: bool = True
    include_chip_data: bool = False


class AnalysisOutput(BaseModel):
    format: OutputFormat = OutputFormat.DASHBOARD
    language: str = Field(default="zh", pattern="^(zh|en)$")
    verbosity: OutputVerbosity = OutputVerbosity.STANDARD


class AnalysisExecution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    async_mode: bool = Field(default=False, alias="async")
    force_refresh: bool = False
    save_history: bool = True
    dry_run: bool = False


class AnalysisContextMeta(BaseModel):
    query_source: QuerySource = QuerySource.UNKNOWN
    original_query: Optional[str] = None
    selection_source: SelectionSource = SelectionSource.MANUAL


class AnalysisRequest(BaseModel):
    """Unified single-stock analysis request."""

    stock: StockTarget
    mode: AnalysisMode = AnalysisMode.STANDARD
    strategy: Optional[str] = None
    features: AnalysisFeatures = Field(default_factory=AnalysisFeatures)
    output: AnalysisOutput = Field(default_factory=AnalysisOutput)
    execution: AnalysisExecution = Field(default_factory=AnalysisExecution)
    context: AnalysisContextMeta = Field(default_factory=AnalysisContextMeta)

    @classmethod
    def minimal(cls, stock_input: str) -> "AnalysisRequest":
        return cls(stock=StockTarget(input=stock_input))


class BatchSharedOptions(BaseModel):
    mode: AnalysisMode = AnalysisMode.STANDARD
    strategy: Optional[str] = None
    features: AnalysisFeatures = Field(default_factory=AnalysisFeatures)
    output: AnalysisOutput = Field(default_factory=AnalysisOutput)


class BatchAnalysisRequest(BaseModel):
    batch: list[AnalysisRequest]
    shared: BatchSharedOptions = Field(default_factory=BatchSharedOptions)
    execution: AnalysisExecution = Field(default_factory=lambda: AnalysisExecution(async_mode=True))


class StockInfo(BaseModel):
    code: str
    market: Market
    name: Optional[str] = None
    input: Optional[str] = None


class TrendBlock(BaseModel):
    status: TrendStatus
    signal: DecisionAction
    score: int = Field(..., ge=0, le=100)
    summary: str
    status_text: Optional[str] = None
    signal_text: Optional[str] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    supports: list[float] = Field(default_factory=list)
    resistances: list[float] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)


class IntelNewsItem(BaseModel):
    title: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class IntelBlock(BaseModel):
    summary: str = ""
    highlights: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    news_items: list[IntelNewsItem] = Field(default_factory=list)


class DecisionBlock(BaseModel):
    action: DecisionAction
    summary: str
    action_text: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DashboardChecklistItem(BaseModel):
    item: str
    status: ChecklistStatus


class DashboardBlock(BaseModel):
    one_sentence: str = ""
    positioning: Optional[str] = None
    battle_plan: dict[str, Any] = Field(default_factory=dict)
    checklist: list[DashboardChecklistItem] = Field(default_factory=list)


class EvidenceBlock(BaseModel):
    providers: dict[str, list[str]] = Field(default_factory=dict)
    used_features: list[str] = Field(default_factory=list)
    data_completeness: dict[str, DataCompleteness] = Field(default_factory=dict)


class MetadataBlock(BaseModel):
    request_id: Optional[str] = None
    generated_at: Optional[str] = None
    mode: Optional[AnalysisMode] = None
    degraded: bool = False
    partial: bool = False
    errors: list[str] = Field(default_factory=list)
    duration_ms: Optional[int] = Field(default=None, ge=0)
    query_source: Optional[QuerySource] = None


class AnalysisResponse(BaseModel):
    """Unified analysis response shared across API/Bot/Agent consumers."""

    stock: StockInfo
    decision: DecisionBlock
    trend: Optional[TrendBlock] = None
    intel: Optional[IntelBlock] = None
    dashboard: Optional[DashboardBlock] = None
    evidence: Optional[EvidenceBlock] = None
    metadata: MetadataBlock = Field(default_factory=MetadataBlock)

    @classmethod
    def minimal(
        cls,
        *,
        code: str,
        market: Market,
        action: DecisionAction,
        summary: str,
        name: Optional[str] = None,
        degraded: bool = False,
        partial: bool = False,
        errors: Optional[list[str]] = None,
    ) -> "AnalysisResponse":
        return cls(
            stock=StockInfo(code=code, market=market, name=name),
            decision=DecisionBlock(action=action, summary=summary),
            metadata=MetadataBlock(degraded=degraded, partial=partial, errors=errors or []),
        )


__all__ = [
    "AnalysisContextMeta",
    "AnalysisExecution",
    "AnalysisFeatures",
    "AnalysisMode",
    "AnalysisOutput",
    "AnalysisRequest",
    "AnalysisResponse",
    "BatchAnalysisRequest",
    "BatchSharedOptions",
    "ChecklistStatus",
    "ConfidenceLevel",
    "DashboardBlock",
    "DashboardChecklistItem",
    "DataCompleteness",
    "DecisionAction",
    "DecisionBlock",
    "EvidenceBlock",
    "IntelBlock",
    "IntelNewsItem",
    "Market",
    "MetadataBlock",
    "OutputFormat",
    "OutputVerbosity",
    "QuerySource",
    "SelectionSource",
    "StockInfo",
    "StockTarget",
    "TrendBlock",
    "TrendStatus",
]
