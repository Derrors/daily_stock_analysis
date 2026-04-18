# -*- coding: utf-8 -*-
"""Compatibility checks for legacy data_provider import paths."""

import importlib
import sys
import warnings


def test_legacy_submodule_aliases_to_canonical_module() -> None:
    legacy = importlib.import_module("data_provider.base")
    canonical = importlib.import_module("src.stock_analysis_skill.providers.base")
    assert legacy is canonical


def test_legacy_tushare_module_aliases_to_canonical_module() -> None:
    legacy = importlib.import_module("data_provider.tushare_fetcher")
    canonical = importlib.import_module("src.stock_analysis_skill.providers.tushare_fetcher")
    assert legacy is canonical


def test_top_level_legacy_exports_still_resolve() -> None:
    from data_provider import DataFetcherManager
    from src.stock_analysis_skill.providers import DataFetcherManager as CanonicalManager

    assert DataFetcherManager is CanonicalManager


def _reload_legacy_module(module_name: str):
    for key in (module_name, "data_provider._compat", "data_provider"):
        sys.modules.pop(key, None)
    return importlib.import_module(module_name)


def test_legacy_import_warning_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("DSA_WARN_LEGACY_IMPORTS", raising=False)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        _reload_legacy_module("data_provider.base")

    assert not [w for w in captured if issubclass(w.category, DeprecationWarning)]


def test_legacy_import_warning_enabled_with_flag(monkeypatch) -> None:
    monkeypatch.setenv("DSA_WARN_LEGACY_IMPORTS", "1")
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        _reload_legacy_module("data_provider.base")

    messages = [str(w.message) for w in captured if issubclass(w.category, DeprecationWarning)]
    assert any("data_provider.base" in msg for msg in messages)
