"""Compatibility wrapper for the legacy strategy aggregator import path."""

from src.agent.skills.aggregator import SkillAggregator as _CanonicalSkillAggregator
from src.agent.skills.aggregator import StrategyAggregator

__all__ = ["StrategyAggregator"]


def __getattr__(name):
    if name == "SkillAggregator":
        return _CanonicalSkillAggregator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
