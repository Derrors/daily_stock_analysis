# -*- coding: utf-8 -*-
"""Shared dataframe helpers for provider-side OHLCV processing."""

from __future__ import annotations

from typing import Any


def clean_standard_ohlcv_dataframe(df: Any, *, pd_module: Any) -> Any:
    """Clean a normalized OHLCV dataframe before indicator calculation."""
    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd_module.to_datetime(df["date"])

    numeric_cols = ["open", "high", "low", "close", "volume", "amount", "pct_chg"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd_module.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close", "volume"])
    df = df.sort_values("date", ascending=True).reset_index(drop=True)
    return df


def calculate_standard_technical_indicators(df: Any) -> Any:
    """Add standard moving-average and volume-ratio indicators."""
    df = df.copy()

    df["ma5"] = df["close"].rolling(window=5, min_periods=1).mean()
    df["ma10"] = df["close"].rolling(window=10, min_periods=1).mean()
    df["ma20"] = df["close"].rolling(window=20, min_periods=1).mean()

    avg_volume_5 = df["volume"].rolling(window=5, min_periods=1).mean()
    df["volume_ratio"] = df["volume"] / avg_volume_5.shift(1)
    df["volume_ratio"] = df["volume_ratio"].fillna(1.0)

    for col in ["ma5", "ma10", "ma20", "volume_ratio"]:
        if col in df.columns:
            df[col] = df[col].round(2)

    return df
