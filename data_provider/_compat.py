# -*- coding: utf-8 -*-
"""Shared compatibility helpers for legacy `data_provider.*` modules."""

from __future__ import annotations

import importlib
import os
import sys
import warnings


_WARNED: set[str] = set()


def _warn_enabled() -> bool:
    return os.getenv("DSA_WARN_LEGACY_IMPORTS", "0").strip().lower() in {"1", "true", "yes"}


def alias_module(legacy_name: str, canonical_name: str):
    """Alias a legacy module path to the canonical module path.

    This keeps old imports executable while making canonical imports explicit.
    """
    edge = f"{legacy_name}->{canonical_name}"
    if _warn_enabled() and edge not in _WARNED:
        warnings.warn(
            f"`{legacy_name}` is deprecated; use `{canonical_name}` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        _WARNED.add(edge)

    module = importlib.import_module(canonical_name)
    sys.modules[legacy_name] = module
    return module
