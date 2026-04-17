"""Compatibility wrapper for the legacy strategy agent import path."""

from src.agent.skills.skill_agent import SkillAgent as _CanonicalSkillAgent
from src.agent.skills.skill_agent import StrategyAgent

__all__ = ["StrategyAgent"]


def __getattr__(name):
    if name == "SkillAgent":
        return _CanonicalSkillAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
