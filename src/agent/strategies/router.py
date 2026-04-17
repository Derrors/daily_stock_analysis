"""Compatibility wrapper for the legacy strategy router import path."""

from src.agent.skills.router import SkillRouter as _CanonicalSkillRouter
from src.agent.skills.router import StrategyRouter, _DEFAULT_STRATEGIES

__all__ = ["StrategyRouter", "_DEFAULT_STRATEGIES"]


def __getattr__(name):
    if name == "SkillRouter":
        return _CanonicalSkillRouter
    if name == "_DEFAULT_SKILLS":
        return _DEFAULT_STRATEGIES
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
