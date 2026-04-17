"""Compatibility wrapper for the legacy strategy agent import path."""

from src.agent.skills.skill_agent import StrategyAgent

# Internal alias kept for unusually old imports; public surface stays strategy-first.
SkillAgent = StrategyAgent

__all__ = ["StrategyAgent"]
