"""Compatibility wrapper for the legacy strategy aggregator import path."""

from src.agent.skills.aggregator import StrategyAggregator

# Keep an internal alias so unusually old call sites do not break, but only the
# legacy strategy-facing name is considered public from this module.
SkillAggregator = StrategyAggregator

__all__ = ["StrategyAggregator"]
