# -*- coding: utf-8 -*-
"""Unified request/response contracts for the skill-first stock analysis runtime.

These models are the canonical contract layer for agent-facing execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.report_language import get_signal_level

PUBLIC_API_VERSION = "v1"


@dataclass
class AnalysisResult:
    """Structured stock analysis result with dashboard-oriented helpers."""

    code: str
    name: str

    sentiment_score: int
    trend_prediction: str
    operation_advice: str
    decision_type: str = "hold"
    confidence_level: str = "中"
    report_language: str = "zh"

    dashboard: Optional[Dict[str, Any]] = None

    trend_analysis: str = ""
    short_term_outlook: str = ""
    medium_term_outlook: str = ""

    technical_analysis: str = ""
    ma_analysis: str = ""
    volume_analysis: str = ""
    pattern_analysis: str = ""

    fundamental_analysis: str = ""
    sector_position: str = ""
    company_highlights: str = ""

    news_summary: str = ""
    market_sentiment: str = ""
    hot_topics: str = ""

    analysis_summary: str = ""
    key_points: str = ""
    risk_warning: str = ""
    buy_reason: str = ""

    market_snapshot: Optional[Dict[str, Any]] = None
    raw_response: Optional[str] = None
    search_performed: bool = False
    data_sources: str = ""
    success: bool = True
    error_message: Optional[str] = None

    current_price: Optional[float] = None
    change_pct: Optional[float] = None

    model_used: Optional[str] = None
    query_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "sentiment_score": self.sentiment_score,
            "trend_prediction": self.trend_prediction,
            "operation_advice": self.operation_advice,
            "decision_type": self.decision_type,
            "confidence_level": self.confidence_level,
            "report_language": self.report_language,
            "dashboard": self.dashboard,
            "trend_analysis": self.trend_analysis,
            "short_term_outlook": self.short_term_outlook,
            "medium_term_outlook": self.medium_term_outlook,
            "technical_analysis": self.technical_analysis,
            "ma_analysis": self.ma_analysis,
            "volume_analysis": self.volume_analysis,
            "pattern_analysis": self.pattern_analysis,
            "fundamental_analysis": self.fundamental_analysis,
            "sector_position": self.sector_position,
            "company_highlights": self.company_highlights,
            "news_summary": self.news_summary,
            "market_sentiment": self.market_sentiment,
            "hot_topics": self.hot_topics,
            "analysis_summary": self.analysis_summary,
            "key_points": self.key_points,
            "risk_warning": self.risk_warning,
            "buy_reason": self.buy_reason,
            "market_snapshot": self.market_snapshot,
            "search_performed": self.search_performed,
            "success": self.success,
            "error_message": self.error_message,
            "current_price": self.current_price,
            "change_pct": self.change_pct,
            "model_used": self.model_used,
        }

    def get_core_conclusion(self) -> str:
        if self.dashboard and "core_conclusion" in self.dashboard:
            return self.dashboard["core_conclusion"].get("one_sentence", self.analysis_summary)
        return self.analysis_summary

    def get_position_advice(self, has_position: bool = False) -> str:
        if self.dashboard and "core_conclusion" in self.dashboard:
            pos_advice = self.dashboard["core_conclusion"].get("position_advice", {})
            if has_position:
                return pos_advice.get("has_position", self.operation_advice)
            return pos_advice.get("no_position", self.operation_advice)
        return self.operation_advice

    def get_sniper_points(self) -> Dict[str, str]:
        if self.dashboard and "battle_plan" in self.dashboard:
            return self.dashboard["battle_plan"].get("sniper_points", {})
        return {}

    def get_checklist(self) -> List[str]:
        if self.dashboard and "battle_plan" in self.dashboard:
            return self.dashboard["battle_plan"].get("action_checklist", [])
        return []

    def get_risk_alerts(self) -> List[str]:
        if self.dashboard and "intelligence" in self.dashboard:
            return self.dashboard["intelligence"].get("risk_alerts", [])
        return []

    def get_emoji(self) -> str:
        _, emoji, _ = get_signal_level(
            self.operation_advice,
            self.sentiment_score,
            self.report_language,
        )
        return emoji

    def get_confidence_stars(self) -> str:
        star_map = {
            "高": "⭐⭐⭐",
            "high": "⭐⭐⭐",
            "中": "⭐⭐",
            "medium": "⭐⭐",
            "低": "⭐",
            "low": "⭐",
        }
        return star_map.get(str(self.confidence_level or "").strip().lower(), "⭐⭐")


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
    """Unified analysis response shared across agent-facing consumers."""

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


class MarketAnalysisRequest(BaseModel):
    """Agent-facing market review request."""

    region: str = Field(default="cn", pattern="^(cn|hk|us|both)$")
    include_news: bool = True
    output: AnalysisOutput = Field(default_factory=AnalysisOutput)
    execution: AnalysisExecution = Field(default_factory=AnalysisExecution)


class MarketIndexSummary(BaseModel):
    code: str
    name: str
    current: Optional[float] = None
    change_pct: Optional[float] = None


class MarketAnalysisResponse(BaseModel):
    """Structured market-analysis result for agent consumption."""

    region: str
    summary: str
    report: str = ""
    indices: list[MarketIndexSummary] = Field(default_factory=list)
    metadata: MetadataBlock = Field(default_factory=MetadataBlock)


class StrategySpec(BaseModel):
    """Resolved strategy resource loaded from `strategies/*.yaml`."""

    id: str
    display_name: str
    description: str = ""
    category: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    instructions: str = ""
    source_path: Optional[str] = None


class StrategyResolutionRequest(BaseModel):
    query: str


class StrategyResolutionResponse(BaseModel):
    query: str
    matched: bool
    strategy: Optional[StrategySpec] = None
    available: list[str] = Field(default_factory=list)


PUBLIC_CONTRACT_EXPORTS = [
    "AnalysisContextMeta",
    "AnalysisExecution",
    "AnalysisFeatures",
    "AnalysisMode",
    "AnalysisOutput",
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisResult",
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
    "MarketAnalysisRequest",
    "MarketAnalysisResponse",
    "MarketIndexSummary",
    "MetadataBlock",
    "OutputFormat",
    "OutputVerbosity",
    "QuerySource",
    "SelectionSource",
    "StockInfo",
    "StockTarget",
    "StrategyResolutionRequest",
    "StrategyResolutionResponse",
    "StrategySpec",
    "TrendBlock",
    "TrendStatus",
]

__all__ = [
    "PUBLIC_API_VERSION",
    "PUBLIC_CONTRACT_EXPORTS",
    *PUBLIC_CONTRACT_EXPORTS,
]
