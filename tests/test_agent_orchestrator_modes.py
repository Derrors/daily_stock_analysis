# -*- coding: utf-8 -*-
"""Focused tests for AgentOrchestrator mode / chain construction behaviour."""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock as _MagicMock
    sys.modules["litellm"] = _MagicMock()

from src.agent.protocols import AgentContext, AgentOpinion
from src.config import AGENT_MAX_STEPS_DEFAULT


class TestOrchestratorModes(unittest.TestCase):
    """Test that _build_agent_chain returns the right agents for each mode."""

    def _make_orchestrator(self, mode="standard"):
        from src.agent.orchestrator import AgentOrchestrator
        mock_registry = MagicMock()
        mock_adapter = MagicMock()
        return AgentOrchestrator(
            tool_registry=mock_registry,
            llm_adapter=mock_adapter,
            mode=mode,
        )

    def test_quick_mode(self):
        orch = self._make_orchestrator("quick")
        ctx = AgentContext(query="test", stock_code="600519")
        chain = orch._build_agent_chain(ctx)
        names = [a.agent_name for a in chain]
        self.assertEqual(names, ["technical", "decision"])

    def test_standard_mode(self):
        orch = self._make_orchestrator("standard")
        ctx = AgentContext(query="test", stock_code="600519")
        chain = orch._build_agent_chain(ctx)
        names = [a.agent_name for a in chain]
        self.assertEqual(names, ["technical", "intel", "decision"])

    def test_full_mode(self):
        orch = self._make_orchestrator("full")
        ctx = AgentContext(query="test", stock_code="600519")
        chain = orch._build_agent_chain(ctx)
        names = [a.agent_name for a in chain]
        self.assertEqual(names, ["technical", "intel", "risk", "decision"])

    def test_invalid_mode_falls_back_to_standard(self):
        orch = self._make_orchestrator("nonsense")
        self.assertEqual(orch.mode, "standard")

    def test_chain_agents_inherit_orchestrator_max_steps(self):
        """Default/lowered limits cap agents; raised limits hard-override all agents."""
        orch = self._make_orchestrator("full")
        orch.max_steps = AGENT_MAX_STEPS_DEFAULT
        high_limit_chain = orch._build_agent_chain(AgentContext(query="test", stock_code="600519"))
        self.assertEqual(
            {agent.agent_name: agent.max_steps for agent in high_limit_chain},
            {"technical": 6, "intel": 4, "risk": 4, "decision": 3},
        )

        orch.max_steps = 5
        low_limit_chain = orch._build_agent_chain(AgentContext(query="test", stock_code="600519"))
        self.assertEqual(
            {agent.agent_name: agent.max_steps for agent in low_limit_chain},
            {"technical": 5, "intel": 4, "risk": 4, "decision": 3},
        )

        orch.max_steps = AGENT_MAX_STEPS_DEFAULT + 2
        raised_limit_chain = orch._build_agent_chain(AgentContext(query="test", stock_code="600519"))
        self.assertEqual(
            {agent.agent_name: agent.max_steps for agent in raised_limit_chain},
            {
                "technical": AGENT_MAX_STEPS_DEFAULT + 2,
                "intel": AGENT_MAX_STEPS_DEFAULT + 2,
                "risk": AGENT_MAX_STEPS_DEFAULT + 2,
                "decision": AGENT_MAX_STEPS_DEFAULT + 2,
            },
        )

    def test_prepare_agent_raised_limit_overrides_low_default_agent(self):
        orch = self._make_orchestrator("full")
        orch.max_steps = AGENT_MAX_STEPS_DEFAULT + 2
        decision = MagicMock(agent_name="decision", max_steps=3)

        prepared = orch._prepare_agent(decision)

        self.assertIs(prepared, decision)
        self.assertEqual(prepared.max_steps, AGENT_MAX_STEPS_DEFAULT + 2)

    def test_build_context_from_dict(self):
        orch = self._make_orchestrator()
        ctx = orch._build_context(
            "Analyze 600519",
            context={"stock_code": "600519", "stock_name": "贵州茅台", "skills": ["bull_trend"]},
        )
        self.assertEqual(ctx.stock_code, "600519")
        self.assertEqual(ctx.stock_name, "贵州茅台")
        self.assertEqual(ctx.meta["skills_requested"], ["bull_trend"])

    def test_build_context_extracts_code_from_query(self):
        orch = self._make_orchestrator()
        ctx = orch._build_context("分析600519的走势")
        self.assertEqual(ctx.stock_code, "600519")

    def test_fallback_summary(self):
        orch = self._make_orchestrator()
        ctx = AgentContext(query="test", stock_code="600519", stock_name="贵州茅台")
        ctx.add_opinion(AgentOpinion(agent_name="tech", signal="buy", confidence=0.8, reasoning="Strong trend"))
        ctx.add_risk_flag("insider", "Minor sell-down", severity="low")
        summary = orch._fallback_summary(ctx)
        self.assertIn("600519", summary)
        self.assertIn("Strong trend", summary)
        self.assertIn("Minor sell-down", summary)


if __name__ == "__main__":
    unittest.main()
