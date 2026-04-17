# -*- coding: utf-8 -*-
"""Focused tests for legacy strategy-agent compatibility exports."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock
    sys.modules["litellm"] = MagicMock()


class TestStrategyAgentCompat(unittest.TestCase):
    def test_legacy_strategy_module_still_exposes_skill_agent_compatibly(self):
        from src.agent.skills.skill_agent import SkillAgent as CanonicalSkillAgent
        from src.agent.strategies.strategy_agent import SkillAgent as LegacySkillAgent
        from src.agent.strategies.strategy_agent import StrategyAgent

        self.assertIs(LegacySkillAgent, CanonicalSkillAgent)
        self.assertTrue(issubclass(StrategyAgent, CanonicalSkillAgent))


if __name__ == "__main__":
    unittest.main()
