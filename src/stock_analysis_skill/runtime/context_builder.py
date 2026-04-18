# -*- coding: utf-8 -*-
"""Context-building helpers for the skill-first stock-analysis runtime.

These helpers host orchestration-adjacent transformation logic that used to
live directly inside ``src.core.pipeline.StockAnalysisPipeline``.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

import pandas as pd

from src.core.trading_calendar import (
    get_effective_trading_date,
    get_market_for_stock,
    get_market_now,
    is_market_open,
)
from src.report_language import normalize_report_language
from src.search_service import SearchService
from src.stock_analysis_skill.providers.base import normalize_stock_code

logger = logging.getLogger(__name__)


def describe_volume_ratio(volume_ratio: float) -> str:
    """Return a user-facing description for a realtime volume ratio."""
    if volume_ratio < 0.5:
        return "极度萎缩"
    if volume_ratio < 0.8:
        return "明显萎缩"
    if volume_ratio < 1.2:
        return "正常"
    if volume_ratio < 2.0:
        return "温和放量"
    if volume_ratio < 3.0:
        return "明显放量"
    return "巨量"


def compute_ma_status(close: float, ma5: float, ma10: float, ma20: float) -> str:
    """Compute MA alignment status from price and MA values."""
    close = close or 0
    ma5 = ma5 or 0
    ma10 = ma10 or 0
    ma20 = ma20 or 0
    if close > ma5 > ma10 > ma20 > 0:
        return "多头排列 📈"
    if close < ma5 < ma10 < ma20 and ma20 > 0:
        return "空头排列 📉"
    if close > ma5 and ma5 > ma10:
        return "短期向好 🔼"
    if close < ma5 and ma5 < ma10:
        return "短期走弱 🔽"
    return "震荡整理 ↔️"


def safe_to_dict(value: Any) -> Optional[Dict[str, Any]]:
    """Best-effort conversion to a JSON-friendly dict."""
    if value is None:
        return None
    if hasattr(value, "to_dict"):
        try:
            return value.to_dict()
        except Exception:
            return None
    if hasattr(value, "__dict__"):
        try:
            return dict(value.__dict__)
        except Exception:
            return None
    return None


def resolve_resume_target_date(
    code: str,
    current_time: Optional[datetime] = None,
) -> date:
    """Resolve the trading date used by checkpoint/resume checks."""
    market = get_market_for_stock(normalize_stock_code(code))
    return get_effective_trading_date(market, current_time=current_time)


def build_query_context(
    *,
    query_id: Optional[str],
    query_source: Optional[str],
    source_message: Optional[Any],
) -> Dict[str, str]:
    """Build request metadata for history/news persistence."""
    effective_query_id = query_id or ""

    context: Dict[str, str] = {
        "query_id": effective_query_id,
        "query_source": query_source or "",
    }

    if source_message:
        context.update(
            {
                "requester_platform": source_message.platform or "",
                "requester_user_id": source_message.user_id or "",
                "requester_user_name": source_message.user_name or "",
                "requester_chat_id": source_message.chat_id or "",
                "requester_message_id": source_message.message_id or "",
                "requester_query": source_message.content or "",
            }
        )

    return context


def build_context_snapshot(
    *,
    enhanced_context: Dict[str, Any],
    news_content: Optional[str],
    realtime_quote: Any,
    chip_data: Optional[Any],
) -> Dict[str, Any]:
    """Build the persisted analysis context snapshot."""
    return {
        "enhanced_context": enhanced_context,
        "news_content": news_content,
        "realtime_quote_raw": safe_to_dict(realtime_quote),
        "chip_distribution_raw": safe_to_dict(chip_data),
    }


def augment_historical_with_realtime(
    *,
    config: Any,
    df: pd.DataFrame,
    realtime_quote: Any,
    code: str,
) -> pd.DataFrame:
    """Augment historical OHLCV with today's realtime quote for intraday MA calculation."""
    if df is None or df.empty or "close" not in df.columns:
        return df
    if realtime_quote is None:
        return df
    price = getattr(realtime_quote, "price", None)
    if price is None or not (isinstance(price, (int, float)) and price > 0):
        return df

    enable_realtime_tech = getattr(config, "enable_realtime_technical_indicators", True)
    if not enable_realtime_tech:
        return df
    market = get_market_for_stock(code)
    market_today = get_market_now(market).date()
    if market and not is_market_open(market, market_today):
        return df

    last_val = df["date"].max()
    last_date = (
        last_val.date()
        if hasattr(last_val, "date")
        else (last_val if isinstance(last_val, date) else pd.Timestamp(last_val).date())
    )
    yesterday_close = float(df.iloc[-1]["close"]) if len(df) > 0 else price
    open_p = (
        getattr(realtime_quote, "open_price", None)
        or getattr(realtime_quote, "pre_close", None)
        or yesterday_close
    )
    high_p = getattr(realtime_quote, "high", None) or price
    low_p = getattr(realtime_quote, "low", None) or price
    vol = getattr(realtime_quote, "volume", None) or 0
    amt = getattr(realtime_quote, "amount", None)
    pct = getattr(realtime_quote, "change_pct", None)

    if last_date >= market_today:
        df = df.copy()
        idx = df.index[-1]
        df.loc[idx, "close"] = price
        if open_p is not None:
            df.loc[idx, "open"] = open_p
        if high_p is not None:
            df.loc[idx, "high"] = high_p
        if low_p is not None:
            df.loc[idx, "low"] = low_p
        if vol:
            df.loc[idx, "volume"] = vol
        if amt is not None:
            df.loc[idx, "amount"] = amt
        if pct is not None:
            df.loc[idx, "pct_chg"] = pct
    else:
        new_row = {
            "code": code,
            "date": market_today,
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": price,
            "volume": vol,
            "amount": amt if amt is not None else 0,
            "pct_chg": pct if pct is not None else 0,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df


def attach_belong_boards_to_fundamental_context(
    *,
    fetcher_manager: Any,
    code: str,
    fundamental_context: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Attach A-share board membership as a top-level supplemental field."""
    if isinstance(fundamental_context, dict):
        enriched_context = dict(fundamental_context)
    else:
        enriched_context = fetcher_manager.build_failed_fundamental_context(
            code,
            "invalid fundamental context",
        )

    existing_boards = enriched_context.get("belong_boards")
    if isinstance(existing_boards, list):
        enriched_context["belong_boards"] = list(existing_boards)
        return enriched_context

    boards_block = enriched_context.get("boards")
    boards_status = boards_block.get("status") if isinstance(boards_block, dict) else None
    coverage = enriched_context.get("coverage")
    boards_coverage = coverage.get("boards") if isinstance(coverage, dict) else None
    market = enriched_context.get("market")
    if not isinstance(market, str) or not market.strip():
        market = get_market_for_stock(normalize_stock_code(code))

    if market != "cn" or boards_status == "not_supported" or boards_coverage == "not_supported":
        enriched_context["belong_boards"] = []
        return enriched_context

    boards = []
    try:
        raw_boards = fetcher_manager.get_belong_boards(code)
        if isinstance(raw_boards, list):
            boards = raw_boards
    except Exception as exc:
        logger.debug("%s attach belong_boards failed (fail-open): %s", code, exc)

    enriched_context["belong_boards"] = boards
    return enriched_context


def enhance_context(
    *,
    config: Any,
    search_service: Any,
    fetcher_manager: Any,
    context: Dict[str, Any],
    realtime_quote: Any,
    chip_data: Optional[Any],
    trend_result: Optional[Any],
    stock_name: str = "",
    fundamental_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Enhance the analysis context with realtime, chip, trend, and fundamentals."""
    enhanced = context.copy()
    enhanced["report_language"] = normalize_report_language(getattr(config, "report_language", "zh"))

    if stock_name:
        enhanced["stock_name"] = stock_name
    elif realtime_quote and getattr(realtime_quote, "name", None):
        enhanced["stock_name"] = realtime_quote.name

    enhanced["news_window_days"] = getattr(search_service, "news_window_days", 3)

    if realtime_quote:
        volume_ratio = getattr(realtime_quote, "volume_ratio", None)
        enhanced["realtime"] = {
            "name": getattr(realtime_quote, "name", ""),
            "price": getattr(realtime_quote, "price", None),
            "change_pct": getattr(realtime_quote, "change_pct", None),
            "volume_ratio": volume_ratio,
            "volume_ratio_desc": describe_volume_ratio(volume_ratio) if volume_ratio else "无数据",
            "turnover_rate": getattr(realtime_quote, "turnover_rate", None),
            "pe_ratio": getattr(realtime_quote, "pe_ratio", None),
            "pb_ratio": getattr(realtime_quote, "pb_ratio", None),
            "total_mv": getattr(realtime_quote, "total_mv", None),
            "circ_mv": getattr(realtime_quote, "circ_mv", None),
            "change_60d": getattr(realtime_quote, "change_60d", None),
            "source": getattr(realtime_quote, "source", None),
        }
        enhanced["realtime"] = {k: v for k, v in enhanced["realtime"].items() if v is not None}

    if chip_data:
        current_price = getattr(realtime_quote, "price", 0) if realtime_quote else 0
        enhanced["chip"] = {
            "profit_ratio": chip_data.profit_ratio,
            "avg_cost": chip_data.avg_cost,
            "concentration_90": chip_data.concentration_90,
            "concentration_70": chip_data.concentration_70,
            "chip_status": chip_data.get_chip_status(current_price or 0),
        }

    if trend_result:
        enhanced["trend_analysis"] = {
            "trend_status": trend_result.trend_status.value,
            "ma_alignment": trend_result.ma_alignment,
            "trend_strength": trend_result.trend_strength,
            "bias_ma5": trend_result.bias_ma5,
            "bias_ma10": trend_result.bias_ma10,
            "volume_status": trend_result.volume_status.value,
            "volume_trend": trend_result.volume_trend,
            "buy_signal": trend_result.buy_signal.value,
            "signal_score": trend_result.signal_score,
            "signal_reasons": trend_result.signal_reasons,
            "risk_factors": trend_result.risk_factors,
        }

    if realtime_quote and trend_result and getattr(trend_result, "ma5", 0) > 0:
        price = getattr(realtime_quote, "price", None)
        if price is not None and price > 0:
            yesterday_close = None
            if enhanced.get("yesterday") and isinstance(enhanced["yesterday"], dict):
                yesterday_close = enhanced["yesterday"].get("close")
            orig_today = enhanced.get("today") or {}
            open_p = (
                getattr(realtime_quote, "open_price", None)
                or getattr(realtime_quote, "pre_close", None)
                or yesterday_close
                or orig_today.get("open")
                or price
            )
            high_p = getattr(realtime_quote, "high", None) or price
            low_p = getattr(realtime_quote, "low", None) or price
            vol = getattr(realtime_quote, "volume", None)
            amt = getattr(realtime_quote, "amount", None)
            pct = getattr(realtime_quote, "change_pct", None)
            realtime_today = {
                "close": price,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "ma5": trend_result.ma5,
                "ma10": trend_result.ma10,
                "ma20": trend_result.ma20,
            }
            if vol is not None:
                realtime_today["volume"] = vol
            if amt is not None:
                realtime_today["amount"] = amt
            if pct is not None:
                realtime_today["pct_chg"] = pct
            for key, value in orig_today.items():
                if key not in realtime_today and value is not None:
                    realtime_today[key] = value
            enhanced["today"] = realtime_today
            enhanced["ma_status"] = compute_ma_status(
                price,
                trend_result.ma5,
                trend_result.ma10,
                trend_result.ma20,
            )
            enhanced["date"] = get_market_now(
                get_market_for_stock(normalize_stock_code(enhanced.get("code", "")))
            ).date().isoformat()
            if yesterday_close is not None:
                try:
                    yc = float(yesterday_close)
                    if yc > 0:
                        enhanced["price_change_ratio"] = round((price - yc) / yc * 100, 2)
                except (TypeError, ValueError):
                    pass
            if vol is not None and enhanced.get("yesterday"):
                yest_vol = (
                    enhanced["yesterday"].get("volume")
                    if isinstance(enhanced["yesterday"], dict)
                    else None
                )
                if yest_vol is not None:
                    try:
                        yv = float(yest_vol)
                        if yv > 0:
                            enhanced["volume_change_ratio"] = round(float(vol) / yv, 2)
                    except (TypeError, ValueError):
                        pass

    enhanced["is_index_etf"] = SearchService.is_index_or_etf(
        context.get("code", ""),
        enhanced.get("stock_name", stock_name),
    )

    enhanced["fundamental_context"] = (
        fundamental_context
        if isinstance(fundamental_context, dict)
        else fetcher_manager.build_failed_fundamental_context(
            context.get("code", ""),
            "invalid fundamental context",
        )
    )

    return enhanced


__all__ = [
    "attach_belong_boards_to_fundamental_context",
    "augment_historical_with_realtime",
    "build_context_snapshot",
    "build_query_context",
    "compute_ma_status",
    "describe_volume_ratio",
    "enhance_context",
    "resolve_resume_target_date",
    "safe_to_dict",
]
