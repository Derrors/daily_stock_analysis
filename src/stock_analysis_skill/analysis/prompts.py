# -*- coding: utf-8 -*-
"""Prompt helpers for analysis integrity repair flows."""

from __future__ import annotations

from typing import List

from src.report_language import normalize_report_language


def build_integrity_complement_prompt(missing_fields: List[str], report_language: str = "zh") -> str:
    """Build complement instruction for missing mandatory analysis fields."""
    report_language = normalize_report_language(report_language)
    if report_language == "en":
        lines = ["### Completion requirements: fill the missing mandatory fields below and output the full JSON again:"]
        for field in missing_fields:
            if field == "sentiment_score":
                lines.append("- sentiment_score: integer score from 0 to 100")
            elif field == "operation_advice":
                lines.append("- operation_advice: localized action advice")
            elif field == "analysis_summary":
                lines.append("- analysis_summary: concise analysis summary")
            elif field == "dashboard.core_conclusion.one_sentence":
                lines.append("- dashboard.core_conclusion.one_sentence: one-line decision")
            elif field == "dashboard.intelligence.risk_alerts":
                lines.append("- dashboard.intelligence.risk_alerts: risk alert list (can be empty)")
            elif field == "dashboard.battle_plan.sniper_points.stop_loss":
                lines.append("- dashboard.battle_plan.sniper_points.stop_loss: stop-loss level")
        return "\n".join(lines)

    lines = ["### 补全要求：请在上方分析基础上补充以下必填内容，并输出完整 JSON："]
    for field in missing_fields:
        if field == "sentiment_score":
            lines.append("- sentiment_score: 0-100 综合评分")
        elif field == "operation_advice":
            lines.append("- operation_advice: 买入/加仓/持有/减仓/卖出/观望")
        elif field == "analysis_summary":
            lines.append("- analysis_summary: 综合分析摘要")
        elif field == "dashboard.core_conclusion.one_sentence":
            lines.append("- dashboard.core_conclusion.one_sentence: 一句话决策")
        elif field == "dashboard.intelligence.risk_alerts":
            lines.append("- dashboard.intelligence.risk_alerts: 风险警报列表（可为空数组）")
        elif field == "dashboard.battle_plan.sniper_points.stop_loss":
            lines.append("- dashboard.battle_plan.sniper_points.stop_loss: 止损价")
    return "\n".join(lines)


def build_integrity_retry_prompt(
    base_prompt: str,
    previous_response: str,
    missing_fields: List[str],
    report_language: str = "zh",
) -> str:
    """Build retry prompt using the previous response as complement baseline."""
    complement = build_integrity_complement_prompt(missing_fields, report_language=report_language)
    previous_output = previous_response.strip()
    if normalize_report_language(report_language) == "en":
        prefix = "### The previous output is below. Complete the missing fields based on that output and return the full JSON again. Do not omit existing fields:"
    else:
        prefix = "### 上一次输出如下，请在该输出基础上补齐缺失字段，并重新输出完整 JSON。不要省略已有字段："
    return "\n\n".join([
        base_prompt,
        prefix,
        previous_output,
        complement,
    ])
