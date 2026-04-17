# -*- coding: utf-8 -*-
"""Canonical analysis result model for the skill-first runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.report_language import get_signal_level


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
