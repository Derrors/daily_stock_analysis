# -*- coding: utf-8 -*-
"""LLM response parsing helpers for stock analysis."""

from __future__ import annotations

import json
import logging
import re

try:
    from json_repair import repair_json
except ModuleNotFoundError:  # pragma: no cover - minimal test env fallback
    def repair_json(value: str) -> str:
        return value

from src.report_language import (
    infer_decision_type_from_advice,
    localize_confidence_level,
    normalize_report_language,
)
from src.schemas.report_schema import AnalysisReportSchema
from .result import AnalysisResult

logger = logging.getLogger(__name__)


def fix_json_string(json_str: str) -> str:
    """Repair common JSON formatting issues produced by LLMs."""
    json_str = re.sub(r"//.*?\n", "\n", json_str)
    json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)
    json_str = json_str.replace("True", "true").replace("False", "false")
    return repair_json(json_str)


def parse_text_response(
    response_text: str,
    code: str,
    name: str,
    report_language: str = "zh",
) -> AnalysisResult:
    """Fallback parser that extracts best-effort sentiment from plain text."""
    report_language = normalize_report_language(report_language)
    sentiment_score = 50
    trend = "Sideways" if report_language == "en" else "震荡"
    advice = "Hold" if report_language == "en" else "持有"

    text_lower = response_text.lower()
    positive_keywords = ["看多", "买入", "上涨", "突破", "强势", "利好", "加仓", "bullish", "buy"]
    negative_keywords = ["看空", "卖出", "下跌", "跌破", "弱势", "利空", "减仓", "bearish", "sell"]

    positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

    if positive_count > negative_count + 1:
        sentiment_score = 65
        trend = "Bullish" if report_language == "en" else "看多"
        advice = "Buy" if report_language == "en" else "买入"
        decision_type = "buy"
    elif negative_count > positive_count + 1:
        sentiment_score = 35
        trend = "Bearish" if report_language == "en" else "看空"
        advice = "Sell" if report_language == "en" else "卖出"
        decision_type = "sell"
    else:
        decision_type = "hold"

    summary = response_text[:500] if response_text else ("No analysis result" if report_language == "en" else "无分析结果")

    return AnalysisResult(
        code=code,
        name=name,
        sentiment_score=sentiment_score,
        trend_prediction=trend,
        operation_advice=advice,
        decision_type=decision_type,
        confidence_level="Low" if report_language == "en" else "低",
        analysis_summary=summary,
        key_points="JSON parsing failed; treat this as best-effort output." if report_language == "en" else "JSON解析失败，仅供参考",
        risk_warning="The result may be inaccurate. Cross-check with other information." if report_language == "en" else "分析结果可能不准确，建议结合其他信息判断",
        raw_response=response_text,
        success=False,
        error_message="LLM response is not valid JSON; analysis result will not be persisted",
        report_language=report_language,
    )


def parse_response(
    response_text: str,
    code: str,
    name: str,
    report_language: str = "zh",
) -> AnalysisResult:
    """Parse LLM JSON response into structured ``AnalysisResult``."""
    report_language = normalize_report_language(report_language)
    try:
        cleaned_text = response_text
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.replace("```", "")

        json_start = cleaned_text.find("{")
        json_end = cleaned_text.rfind("}") + 1

        if json_start >= 0 and json_end > json_start:
            json_str = cleaned_text[json_start:json_end]
            json_str = fix_json_string(json_str)
            data = json.loads(json_str)

            try:
                AnalysisReportSchema.model_validate(data)
            except Exception as e:
                logger.warning(
                    "LLM report schema validation failed, continuing with raw dict: %s",
                    str(e)[:100],
                )

            dashboard = data.get("dashboard", None)
            ai_stock_name = data.get("stock_name")
            if ai_stock_name and (name.startswith("股票") or name == code or "Unknown" in name):
                name = ai_stock_name

            decision_type = data.get("decision_type", "")
            if not decision_type:
                op = data.get("operation_advice", "Hold" if report_language == "en" else "持有")
                decision_type = infer_decision_type_from_advice(op, default="hold")

            return AnalysisResult(
                code=code,
                name=name,
                sentiment_score=int(data.get("sentiment_score", 50)),
                trend_prediction=data.get("trend_prediction", "Sideways" if report_language == "en" else "震荡"),
                operation_advice=data.get("operation_advice", "Hold" if report_language == "en" else "持有"),
                decision_type=decision_type,
                confidence_level=localize_confidence_level(
                    data.get("confidence_level", "Medium" if report_language == "en" else "中"),
                    report_language,
                ),
                report_language=report_language,
                dashboard=dashboard,
                trend_analysis=data.get("trend_analysis", ""),
                short_term_outlook=data.get("short_term_outlook", ""),
                medium_term_outlook=data.get("medium_term_outlook", ""),
                technical_analysis=data.get("technical_analysis", ""),
                ma_analysis=data.get("ma_analysis", ""),
                volume_analysis=data.get("volume_analysis", ""),
                pattern_analysis=data.get("pattern_analysis", ""),
                fundamental_analysis=data.get("fundamental_analysis", ""),
                sector_position=data.get("sector_position", ""),
                company_highlights=data.get("company_highlights", ""),
                news_summary=data.get("news_summary", ""),
                market_sentiment=data.get("market_sentiment", ""),
                hot_topics=data.get("hot_topics", ""),
                analysis_summary=data.get("analysis_summary", "Analysis completed" if report_language == "en" else "分析完成"),
                key_points=data.get("key_points", ""),
                risk_warning=data.get("risk_warning", ""),
                buy_reason=data.get("buy_reason", ""),
                search_performed=data.get("search_performed", False),
                data_sources=data.get("data_sources", "Technical data" if report_language == "en" else "技术面数据"),
                success=True,
            )

        logger.warning("无法从响应中提取 JSON，标记为解析失败")
        return parse_text_response(response_text, code, name, report_language=report_language)

    except json.JSONDecodeError as e:
        logger.warning("JSON 解析失败: %s，标记为解析失败", e)
        return parse_text_response(response_text, code, name, report_language=report_language)
