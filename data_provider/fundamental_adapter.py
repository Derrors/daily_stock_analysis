# -*- coding: utf-8 -*-
"""Compatibility bridge for legacy `data_provider.fundamental_adapter` imports."""

try:
    from ._compat import alias_module
except ImportError:  # pragma: no cover - legacy direct module import fallback
    from data_provider._compat import alias_module

alias_module(__name__, "src.stock_analysis_skill.providers.fundamental_adapter")
