# -*- coding: utf-8 -*-
"""Focused tests for canonical SkillAggregator behavior."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock
    sys.modules["litellm"] = MagicMock()

from src.agent.protocols import AgentContext, AgentOpinion


class TestSkillAggregator(unittest.TestCase):
    """Test canonical SkillAggregator consensus logic."""

    def test_no_strategy_opinions_returns_none(self):
        from src.agent.skills.aggregator import SkillAggregator

        agg = SkillAggregator()
        ctx = AgentContext()
        ctx.add_opinion(AgentOpinion(agent_name="technical", signal="buy", confidence=0.8))

        result = agg.aggregate(ctx)

        self.assertIsNone(result)

    def test_single_strategy_consensus(self):
        from src.agent.skills.aggregator import SkillAggregator

        agg = SkillAggregator()
        ctx = AgentContext()
        ctx.add_opinion(AgentOpinion(agent_name="skill_bull_trend", signal="buy", confidence=0.7))

        result = agg.aggregate(ctx)

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, "skill_consensus")
        self.assertEqual(result.signal, "buy")

    def test_mixed_signals_produce_hold(self):
        from src.agent.skills.aggregator import SkillAggregator

        agg = SkillAggregator()
        ctx = AgentContext()
        ctx.add_opinion(AgentOpinion(agent_name="skill_a", signal="buy", confidence=0.6))
        ctx.add_opinion(AgentOpinion(agent_name="skill_b", signal="sell", confidence=0.6))

        result = agg.aggregate(ctx)

        self.assertIsNotNone(result)
        self.assertEqual(result.signal, "hold")



if __name__ == "__main__":
    unittest.main()
