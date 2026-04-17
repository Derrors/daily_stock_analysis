# -*- coding: utf-8 -*-
"""
Compatibility re-exports for the legacy strategy namespace.

New code should import from ``src.agent.skills`` directly. This package stays
only as an import bridge for older tests/callers.
"""

from src.agent.skills.aggregator import StrategyAggregator
from src.agent.skills.router import StrategyRouter
from src.agent.skills.skill_agent import StrategyAgent

__all__ = [
    "StrategyAgent",
    "StrategyRouter",
    "StrategyAggregator",
]
