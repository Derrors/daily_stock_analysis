# -*- coding: utf-8 -*-
"""Tests for task queue result payload contraction."""

from src.services.task_queue import TaskInfo


def test_task_info_exposes_unified_response_without_redundant_legacy_field() -> None:
    unified = {"stock": {"code": "600519", "name": "贵州茅台"}}
    legacy = {"stock_code": "600519", "stock_name": "贵州茅台", "unified_response": unified}
    task = TaskInfo(
        task_id="task-1",
        stock_code="600519",
        unified_result=unified,
        result=legacy,
    )

    payload = task.to_dict()
    copied = task.copy()

    assert payload["result"] == unified
    assert payload["unified_response"] == unified
    assert payload["runtime_payload"] == legacy
    assert "legacy_result" not in payload
    assert task.get_preferred_result() == unified
    assert task.result == legacy
    assert copied.unified_result == unified
    assert copied.result == legacy


def test_task_info_prefers_embedded_unified_response_when_field_missing() -> None:
    unified = {"stock": {"code": "AAPL", "name": "Apple"}}
    legacy = {"stock_code": "AAPL", "stock_name": "Apple", "unified_response": unified}
    task = TaskInfo(task_id="task-2", stock_code="AAPL", result=legacy)

    payload = task.to_dict()

    assert task.get_preferred_result() == unified
    assert payload["result"] == unified
    assert payload["runtime_payload"] == legacy
    assert "legacy_result" not in payload
    assert payload["unified_response"] is None
