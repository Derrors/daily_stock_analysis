# -*- coding: utf-8 -*-
"""Compatibility checks for legacy data_provider import paths."""

import importlib


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
