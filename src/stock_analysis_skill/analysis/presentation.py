# -*- coding: utf-8 -*-
"""Presentation/context helpers extracted from ``src.analyzer``.

These helpers are intentionally LLM-agnostic so ``GeminiAnalyzer`` can keep
shrinking without touching the high-risk completion/parsing mainline.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from src.data.stock_mapping import STOCK_NAME_MAP

logger = logging.getLogger(__name__)


def get_stock_name_multi_source(
    stock_code: str,
    context: Optional[Dict] = None,
    data_manager=None,
) -> str:
    """Resolve a stock display name from context, cache, or data manager."""
    if context:
        if context.get("stock_name"):
            name = context["stock_name"]
            if name and not name.startswith("股票"):
                return name
        if "realtime" in context and context["realtime"].get("name"):
            return context["realtime"]["name"]

    if stock_code in STOCK_NAME_MAP:
        return STOCK_NAME_MAP[stock_code]

    if data_manager is None:
        try:
            from src.stock_analysis_skill.providers.base import DataFetcherManager

            data_manager = DataFetcherManager()
        except Exception as e:
            logger.debug("无法初始化 DataFetcherManager: %s", e)

    if data_manager:
        try:
            name = data_manager.get_stock_name(stock_code)
            if name:
                STOCK_NAME_MAP[stock_code] = name
                return name
        except Exception as e:
            logger.debug("从数据源获取股票名称失败: %s", e)

    return f"股票{stock_code}"


def format_volume(volume: Optional[float]) -> str:
    if volume is None:
        return "N/A"
    if volume >= 1e8:
        return f"{volume / 1e8:.2f} 亿股"
    if volume >= 1e4:
        return f"{volume / 1e4:.2f} 万股"
    return f"{volume:.0f} 股"


def format_amount(amount: Optional[float]) -> str:
    if amount is None:
        return "N/A"
    if amount >= 1e8:
        return f"{amount / 1e8:.2f} 亿元"
    if amount >= 1e4:
        return f"{amount / 1e4:.2f} 万元"
    return f"{amount:.0f} 元"


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_price(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "N/A"


def build_market_snapshot(context: Dict[str, Any]) -> Dict[str, Any]:
    """Build a presentation-friendly market snapshot from analysis context."""
    today = context.get("today", {}) or {}
    realtime = context.get("realtime", {}) or {}
    yesterday = context.get("yesterday", {}) or {}

    prev_close = yesterday.get("close")
    close = today.get("close")
    high = today.get("high")
    low = today.get("low")

    amplitude = None
    change_amount = None
    if prev_close not in (None, 0) and high is not None and low is not None:
        try:
            amplitude = (float(high) - float(low)) / float(prev_close) * 100
        except (TypeError, ValueError, ZeroDivisionError):
            amplitude = None
    if prev_close is not None and close is not None:
        try:
            change_amount = float(close) - float(prev_close)
        except (TypeError, ValueError):
            change_amount = None

    snapshot = {
        "date": context.get("date", "未知"),
        "close": format_price(close),
        "open": format_price(today.get("open")),
        "high": format_price(high),
        "low": format_price(low),
        "prev_close": format_price(prev_close),
        "pct_chg": format_percent(today.get("pct_chg")),
        "change_amount": format_price(change_amount),
        "amplitude": format_percent(amplitude),
        "volume": format_volume(today.get("volume")),
        "amount": format_amount(today.get("amount")),
    }

    if realtime:
        snapshot.update(
            {
                "price": format_price(realtime.get("price")),
                "volume_ratio": realtime.get("volume_ratio", "N/A"),
                "turnover_rate": format_percent(realtime.get("turnover_rate")),
                "source": getattr(realtime.get("source"), "value", realtime.get("source", "N/A")),
            }
        )

    return snapshot
