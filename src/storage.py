# -*- coding: utf-8 -*-
"""Lazy storage import surface.

This wrapper keeps ``src.storage`` importable without eagerly bootstrapping the
full SQLAlchemy runtime. Heavy ORM models and database wiring now live in
``src.storage_runtime`` and are loaded on first real use.
"""

from __future__ import annotations

from typing import Any

from src.llm_usage import persist_llm_usage as _persist_llm_usage

_RUNTIME_MODULE = None
_MODEL_EXPORTS = {
    "Base",
    "StockDaily",
    "NewsIntel",
    "FundamentalSnapshot",
    "AnalysisHistory",
    "BacktestResult",
    "BacktestSummary",
    "ConversationSession",
    "ConversationMessage",
    "LLMUsage",
    "PortfolioAccount",
    "PortfolioCashLedger",
    "PortfolioCorporateAction",
    "PortfolioDailySnapshot",
    "PortfolioFxRate",
    "PortfolioPosition",
    "PortfolioPositionLot",
    "PortfolioTrade",
}


def _load_runtime_module():
    global _RUNTIME_MODULE
    if _RUNTIME_MODULE is None:
        from src import storage_runtime as runtime_module

        _RUNTIME_MODULE = runtime_module
    return _RUNTIME_MODULE


def _get_runtime_attr(name: str):
    return getattr(_load_runtime_module(), name)


class _DatabaseManagerProxyMeta(type):
    def __getattr__(cls, name: str):
        return getattr(_get_runtime_attr("DatabaseManager"), name)

    def __call__(cls, *args: Any, **kwargs: Any):
        return _get_runtime_attr("DatabaseManager")(*args, **kwargs)


class DatabaseManager(metaclass=_DatabaseManagerProxyMeta):
    """Proxy that loads the heavy storage runtime on first real use."""



def get_db():
    return _get_runtime_attr("get_db")()



def persist_llm_usage(usage, model, call_type, stock_code=None):
    return _persist_llm_usage(usage, model, call_type, stock_code=stock_code)



def __getattr__(name: str):
    if name in _MODEL_EXPORTS:
        return _get_runtime_attr(name)
    if name in {"get_db", "persist_llm_usage", "DatabaseManager"}:
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AnalysisHistory",
    "BacktestResult",
    "BacktestSummary",
    "Base",
    "ConversationMessage",
    "ConversationSession",
    "DatabaseManager",
    "FundamentalSnapshot",
    "LLMUsage",
    "NewsIntel",
    "PortfolioAccount",
    "PortfolioCashLedger",
    "PortfolioCorporateAction",
    "PortfolioDailySnapshot",
    "PortfolioFxRate",
    "PortfolioPosition",
    "PortfolioPositionLot",
    "PortfolioTrade",
    "StockDaily",
    "get_db",
    "persist_llm_usage",
]
