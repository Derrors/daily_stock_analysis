# -*- coding: utf-8 -*-
"""Preferred report-output entrypoints for the skill-first runtime.

`src.notification` remains as a backward-compatible import surface for older
callers and tests. New code should import report-output services from here so
runtime semantics stay aligned with the current repository shape and no longer
expand the deprecated "notification delivery" mental model.
"""

from __future__ import annotations

from src.notification import ReportOutputService, get_report_output_service

__all__ = [
    "ReportOutputService",
    "get_report_output_service",
]
