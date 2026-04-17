# -*- coding: utf-8 -*-
"""Analyzer result post-processing helpers.

This module hosts pure/near-pure helper logic extracted from ``src.analyzer`` so
Phase F can progressively shrink the analyzer monolith without changing public
imports yet.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Tuple

from src.report_language import get_placeholder_text, localize_chip_health

logger = logging.getLogger(__name__)

_CHIP_KEYS: tuple = ("profit_ratio", "avg_cost", "concentration", "chip_health")
_PRICE_POS_KEYS = (
    "ma5",
    "ma10",
    "ma20",
    "bias_ma5",
    "bias_status",
    "current_price",
    "support_level",
    "resistance_level",
)


def check_content_integrity(result: Any) -> Tuple[bool, List[str]]:
    """Check mandatory fields for report content integrity."""
    missing: List[str] = []
    if getattr(result, "sentiment_score", None) is None:
        missing.append("sentiment_score")
    advice = getattr(result, "operation_advice", None)
    if not advice or not isinstance(advice, str) or not advice.strip():
        missing.append("operation_advice")
    summary = getattr(result, "analysis_summary", None)
    if not summary or not isinstance(summary, str) or not summary.strip():
        missing.append("analysis_summary")
    dash = result.dashboard if isinstance(getattr(result, "dashboard", None), dict) else {}
    core = dash.get("core_conclusion")
    core = core if isinstance(core, dict) else {}
    if not (core.get("one_sentence") or "").strip():
        missing.append("dashboard.core_conclusion.one_sentence")
    intel = dash.get("intelligence")
    intel = intel if isinstance(intel, dict) else None
    if intel is None or "risk_alerts" not in intel:
        missing.append("dashboard.intelligence.risk_alerts")
    if getattr(result, "decision_type", None) in ("buy", "hold"):
        battle = dash.get("battle_plan")
        battle = battle if isinstance(battle, dict) else {}
        sp = battle.get("sniper_points")
        sp = sp if isinstance(sp, dict) else {}
        stop_loss = sp.get("stop_loss")
        if stop_loss is None or (isinstance(stop_loss, str) and not stop_loss.strip()):
            missing.append("dashboard.battle_plan.sniper_points.stop_loss")
    return len(missing) == 0, missing


def apply_placeholder_fill(result: Any, missing_fields: List[str]) -> None:
    """Fill missing mandatory fields with placeholders (in-place)."""
    placeholder = get_placeholder_text(getattr(result, "report_language", "zh"))
    for field in missing_fields:
        if field == "sentiment_score":
            result.sentiment_score = 50
        elif field == "operation_advice":
            result.operation_advice = getattr(result, "operation_advice", None) or placeholder
        elif field == "analysis_summary":
            result.analysis_summary = getattr(result, "analysis_summary", None) or placeholder
        elif field == "dashboard.core_conclusion.one_sentence":
            if not getattr(result, "dashboard", None):
                result.dashboard = {}
            if "core_conclusion" not in result.dashboard:
                result.dashboard["core_conclusion"] = {}
            result.dashboard["core_conclusion"]["one_sentence"] = (
                result.dashboard["core_conclusion"].get("one_sentence") or placeholder
            )
        elif field == "dashboard.intelligence.risk_alerts":
            if not getattr(result, "dashboard", None):
                result.dashboard = {}
            if "intelligence" not in result.dashboard:
                result.dashboard["intelligence"] = {}
            if "risk_alerts" not in result.dashboard["intelligence"]:
                result.dashboard["intelligence"]["risk_alerts"] = []
        elif field == "dashboard.battle_plan.sniper_points.stop_loss":
            if not getattr(result, "dashboard", None):
                result.dashboard = {}
            if "battle_plan" not in result.dashboard:
                result.dashboard["battle_plan"] = {}
            if "sniper_points" not in result.dashboard["battle_plan"]:
                result.dashboard["battle_plan"]["sniper_points"] = {}
            result.dashboard["battle_plan"]["sniper_points"]["stop_loss"] = placeholder


def _is_value_placeholder(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, (int, float)) and v == 0:
        return True
    s = str(v).strip().lower()
    return s in ("", "n/a", "na", "数据缺失", "未知", "data unavailable", "unknown", "tbd")


def _safe_float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return default
    if isinstance(v, (int, float)):
        try:
            return default if math.isnan(float(v)) else float(v)
        except (ValueError, TypeError):
            return default
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return default


def _derive_chip_health(profit_ratio: float, concentration_90: float, language: str = "zh") -> str:
    if profit_ratio >= 0.9:
        return localize_chip_health("警惕", language)
    if concentration_90 >= 0.25:
        return localize_chip_health("警惕", language)
    if concentration_90 < 0.15 and 0.3 <= profit_ratio < 0.9:
        return localize_chip_health("健康", language)
    return localize_chip_health("一般", language)


def _build_chip_structure_from_data(chip_data: Any, language: str = "zh") -> Dict[str, Any]:
    if hasattr(chip_data, "profit_ratio"):
        pr = _safe_float(chip_data.profit_ratio)
        ac = chip_data.avg_cost
        c90 = _safe_float(chip_data.concentration_90)
    else:
        d = chip_data if isinstance(chip_data, dict) else {}
        pr = _safe_float(d.get("profit_ratio"))
        ac = d.get("avg_cost")
        c90 = _safe_float(d.get("concentration_90"))
    chip_health = _derive_chip_health(pr, c90, language=language)
    return {
        "profit_ratio": f"{pr:.1%}",
        "avg_cost": ac if (ac is not None and _safe_float(ac) != 0.0) else "N/A",
        "concentration": f"{c90:.2%}",
        "chip_health": chip_health,
    }


def fill_chip_structure_if_needed(result: Any, chip_data: Any) -> None:
    if not result or not chip_data:
        return
    try:
        if not getattr(result, "dashboard", None):
            result.dashboard = {}
        dash = result.dashboard
        dp = dash.get("data_perspective") or {}
        dash["data_perspective"] = dp
        cs = dp.get("chip_structure") or {}
        filled = _build_chip_structure_from_data(
            chip_data,
            language=getattr(result, "report_language", "zh"),
        )
        merged = dict(cs)
        for k in _CHIP_KEYS:
            if _is_value_placeholder(merged.get(k)):
                merged[k] = filled[k]
        if merged != cs:
            dp["chip_structure"] = merged
            logger.info("[chip_structure] Filled placeholder chip fields from data source (Issue #589)")
    except Exception as e:
        logger.warning("[chip_structure] Fill failed, skipping: %s", e)


def fill_price_position_if_needed(result: Any, trend_result: Any = None, realtime_quote: Any = None) -> None:
    if not result:
        return
    try:
        if not getattr(result, "dashboard", None):
            result.dashboard = {}
        dash = result.dashboard
        dp = dash.get("data_perspective") or {}
        dash["data_perspective"] = dp
        pp = dp.get("price_position") or {}

        computed: Dict[str, Any] = {}
        if trend_result:
            tr = trend_result if isinstance(trend_result, dict) else (
                trend_result.__dict__ if hasattr(trend_result, "__dict__") else {}
            )
            computed["ma5"] = tr.get("ma5")
            computed["ma10"] = tr.get("ma10")
            computed["ma20"] = tr.get("ma20")
            computed["bias_ma5"] = tr.get("bias_ma5")
            computed["current_price"] = tr.get("current_price")
            support_levels = tr.get("support_levels") or []
            resistance_levels = tr.get("resistance_levels") or []
            if support_levels:
                computed["support_level"] = support_levels[0]
            if resistance_levels:
                computed["resistance_level"] = resistance_levels[0]
        if realtime_quote:
            rq = realtime_quote if isinstance(realtime_quote, dict) else (
                realtime_quote.to_dict() if hasattr(realtime_quote, "to_dict") else {}
            )
            if _is_value_placeholder(computed.get("current_price")):
                computed["current_price"] = rq.get("price")

        filled = False
        for k in _PRICE_POS_KEYS:
            if _is_value_placeholder(pp.get(k)) and not _is_value_placeholder(computed.get(k)):
                pp[k] = computed[k]
                filled = True
        if filled:
            dp["price_position"] = pp
            logger.info("[price_position] Filled placeholder fields from computed data")
    except Exception as e:
        logger.warning("[price_position] Fill failed, skipping: %s", e)
