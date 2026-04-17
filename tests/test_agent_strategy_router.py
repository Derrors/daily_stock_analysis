# -*- coding: utf-8 -*-
"""Focused tests for canonical SkillRouter behavior."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock
    sys.modules["litellm"] = MagicMock()

from src.agent.protocols import AgentContext, AgentOpinion


class TestSkillRouter(unittest.TestCase):
    """Test canonical SkillRouter behavior."""

    def test_user_requested_strategies_take_priority(self):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext(query="test")
        ctx.meta["skills_requested"] = ["chan_theory", "wave_theory"]
        result = router.select_skills(ctx)
        self.assertEqual(result, ["chan_theory", "wave_theory"])

    def test_user_requested_capped_at_max(self):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext()
        ctx.meta["skills_requested"] = ["a", "b", "c", "d", "e"]
        result = router.select_skills(ctx, max_count=2)
        self.assertEqual(len(result), 2)

    @patch("src.agent.skills.router.SkillRouter._get_routing_mode", return_value="manual")
    @patch(
        "src.agent.skills.router.SkillRouter._get_available_skills",
        return_value=[
            SimpleNamespace(name="chan_theory"),
            SimpleNamespace(name="wave_theory"),
        ],
    )
    @patch("src.config.get_config", return_value=SimpleNamespace(agent_skills=["chan_theory", "wave_theory"]))
    def test_manual_mode_uses_configured_agent_skills(self, _mock_config, _mock_available, _mock):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext()
        result = router.select_skills(ctx)
        self.assertEqual(result, ["chan_theory", "wave_theory"])

    @patch("src.agent.skills.router.SkillRouter._get_routing_mode", return_value="manual")
    @patch(
        "src.agent.skills.router.SkillRouter._get_available_skills",
        return_value=[
            SimpleNamespace(name="bull_trend", default_router=True, default_priority=10),
            SimpleNamespace(name="shrink_pullback", default_router=True, default_priority=40),
        ],
    )
    @patch("src.config.get_config", return_value=SimpleNamespace(agent_skills=[]))
    def test_manual_mode_falls_back_to_defaults_when_no_skills_configured(self, _mock_config, _mock_available, _mock):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext()
        result = router.select_skills(ctx)
        self.assertEqual(result, ["bull_trend", "shrink_pullback"])

    def test_detect_regime_bullish(self):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext()
        ctx.add_opinion(AgentOpinion(
            agent_name="technical",
            signal="buy",
            confidence=0.8,
            raw_data={"ma_alignment": "bullish", "trend_score": 80, "volume_status": "normal"},
        ))
        regime = router._detect_regime(ctx)
        self.assertEqual(regime, "trending_up")

    def test_detect_regime_bearish(self):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext()
        ctx.add_opinion(AgentOpinion(
            agent_name="technical",
            signal="sell",
            confidence=0.7,
            raw_data={"ma_alignment": "bearish", "trend_score": 20, "volume_status": "light"},
        ))
        regime = router._detect_regime(ctx)
        self.assertEqual(regime, "trending_down")

    def test_detect_regime_none_without_technical(self):
        from src.agent.skills.router import SkillRouter
        router = SkillRouter()
        ctx = AgentContext()
        regime = router._detect_regime(ctx)
        self.assertIsNone(regime)


if __name__ == "__main__":
    unittest.main()
