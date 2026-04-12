# -*- coding: utf-8 -*-
"""Focused tests for orchestrator-level risk override post-processing."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock as _MagicMock
    sys.modules["litellm"] = _MagicMock()

from src.agent.protocols import AgentContext, AgentOpinion


class TestRiskOverride(unittest.TestCase):
    """Test orchestrator-level risk override integration."""

    def _make_dashboard(self):
        return {
            "decision_type": "buy",
            "sentiment_score": 76,
            "operation_advice": "买入",
            "analysis_summary": "原始结论",
            "risk_warning": "原风险提示",
            "dashboard": {
                "core_conclusion": {
                    "one_sentence": "可以参与",
                    "signal_type": "🟢买入信号",
                    "position_advice": {
                        "no_position": "分批买入",
                        "has_position": "继续持有",
                    },
                }
            },
        }

    def test_risk_override_vetoes_buy_signal(self):
        from src.agent.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator(
            tool_registry=MagicMock(),
            llm_adapter=MagicMock(),
            config=SimpleNamespace(agent_risk_override=True),
        )
        ctx = AgentContext(query="test", stock_code="600519")
        ctx.set_data("final_dashboard", self._make_dashboard())
        ctx.add_opinion(AgentOpinion(agent_name="decision", signal="buy", confidence=0.8, reasoning="原始结论"))
        ctx.add_opinion(AgentOpinion(
            agent_name="risk",
            signal="strong_sell",
            confidence=0.9,
            reasoning="重大风险",
            raw_data={"veto_buy": True, "reasoning": "存在重大减持风险"},
        ))
        ctx.add_risk_flag("insider", "大股东减持", severity="high")

        orch._apply_risk_override(ctx)
        dashboard = ctx.get_data("final_dashboard")

        self.assertEqual(dashboard["decision_type"], "hold")
        self.assertLessEqual(dashboard["sentiment_score"], 59)
        self.assertIn("风控接管", dashboard["risk_warning"])
        self.assertEqual(ctx.opinions[0].signal, "hold")

    def test_risk_override_normalizes_strong_buy_before_veto(self):
        from src.agent.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator(
            tool_registry=MagicMock(),
            llm_adapter=MagicMock(),
            config=SimpleNamespace(agent_risk_override=True),
        )
        ctx = AgentContext(query="test", stock_code="600519")
        dashboard = self._make_dashboard()
        dashboard["decision_type"] = "strong_buy"
        dashboard["sentiment_score"] = 92
        ctx.set_data("final_dashboard", dashboard)
        ctx.add_opinion(AgentOpinion(agent_name="decision", signal="strong_buy", confidence=0.9, reasoning="原始结论"))
        ctx.add_opinion(AgentOpinion(
            agent_name="risk",
            signal="strong_sell",
            confidence=0.9,
            raw_data={"veto_buy": True, "reasoning": "存在重大风险"},
        ))
        ctx.add_risk_flag("insider", "大股东减持", severity="high")

        orch._apply_risk_override(ctx)

        self.assertEqual(dashboard["decision_type"], "hold")
        self.assertEqual(ctx.opinions[0].signal, "hold")

    def test_risk_override_respects_disable_flag(self):
        from src.agent.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator(
            tool_registry=MagicMock(),
            llm_adapter=MagicMock(),
            config=SimpleNamespace(agent_risk_override=False),
        )
        ctx = AgentContext(query="test", stock_code="600519")
        dashboard = self._make_dashboard()
        ctx.set_data("final_dashboard", dashboard)
        ctx.add_opinion(AgentOpinion(
            agent_name="risk",
            signal="strong_sell",
            confidence=0.9,
            raw_data={"veto_buy": True},
        ))
        ctx.add_risk_flag("insider", "大股东减持", severity="high")

        orch._apply_risk_override(ctx)

        self.assertEqual(dashboard["decision_type"], "buy")


if __name__ == "__main__":
    unittest.main()
