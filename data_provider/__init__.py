# -*- coding: utf-8 -*-
"""Compatibility bridge for legacy `data_provider` imports.

Canonical runtime path moved to:
    src.stock_analysis_skill.providers
"""

from src.stock_analysis_skill import providers as _impl
import os
import warnings

__all__ = getattr(_impl, "__all__", [n for n in dir(_impl) if not n.startswith("__")])


_WARN_ENABLED = os.getenv("DSA_WARN_LEGACY_IMPORTS", "0").strip().lower() in {"1", "true", "yes"}


def __getattr__(name):
    if _WARN_ENABLED:
        warnings.warn(
            "`data_provider` is deprecated; use `src.stock_analysis_skill.providers`.",
            DeprecationWarning,
            stacklevel=2,
        )
    return getattr(_impl, name)


def __dir__():
    return sorted(set(__all__))
