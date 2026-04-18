# -*- coding: utf-8 -*-
"""Compatibility bridge for legacy `data_provider.us_index_mapping` imports."""

from src.stock_analysis_skill.providers import us_index_mapping as _impl

__all__ = getattr(_impl, "__all__", [n for n in dir(_impl) if not n.startswith("__")])


def __getattr__(name):
    return getattr(_impl, name)


def __dir__():
    return sorted(set(__all__))
