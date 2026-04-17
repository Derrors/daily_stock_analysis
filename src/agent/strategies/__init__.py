# -*- coding: utf-8 -*-
"""Legacy strategy namespace.

New code should import from ``src.agent.skills`` directly. This package stays
only as a compatibility bridge for older tests/callers that still use the
historical ``src.agent.strategies`` import path.
"""

from .aggregator import StrategyAggregator
from .router import StrategyRouter
from .strategy_agent import StrategyAgent

__all__ = [
    "StrategyAgent",
    "StrategyRouter",
    "StrategyAggregator",
]
