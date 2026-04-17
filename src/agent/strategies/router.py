"""Compatibility wrapper for the legacy strategy router import path."""

from src.agent.skills.router import StrategyRouter, _DEFAULT_STRATEGIES

# Internal aliases kept only to avoid surprising breakage for older imports.
SkillRouter = StrategyRouter
_DEFAULT_SKILLS = _DEFAULT_STRATEGIES

__all__ = ["StrategyRouter", "_DEFAULT_STRATEGIES"]
