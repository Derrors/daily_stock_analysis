# -*- coding: utf-8 -*-
"""Thin adapter around the legacy ``StockAnalysisPipeline`` executor.

This module isolates the remaining direct dependency on
``src.core.pipeline.StockAnalysisPipeline`` so the canonical runtime can depend
on a narrower runner abstraction instead of constructing the legacy pipeline
inline.
"""

from __future__ import annotations

from typing import Any, Callable, Optional


def _default_pipeline_factory(
    *,
    config: Any,
    query_id: str,
    progress_callback: Optional[Callable[[int, str], None]],
):
    from src.core.pipeline import StockAnalysisPipeline

    return StockAnalysisPipeline(
        config=config,
        query_id=query_id,
        query_source="api",
        progress_callback=progress_callback,
    )


class LegacyPipelineRunner:
    """Create legacy pipeline instances for the canonical runtime."""

    def __init__(self, pipeline_factory=None):
        self.pipeline_factory = pipeline_factory or _default_pipeline_factory

    def create_pipeline(
        self,
        *,
        config: Any,
        query_id: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ):
        return self.pipeline_factory(
            config=config,
            query_id=query_id,
            progress_callback=progress_callback,
        )


__all__ = ["LegacyPipelineRunner"]
