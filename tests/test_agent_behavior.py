# -*- coding: utf-8 -*-
"""Focused tests for agent-local behavior outside orchestration runtime."""

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


class TestDecisionAgentChatMode(unittest.TestCase):
    """Test DecisionAgent chat-mode output path."""

    def test_post_process_stores_free_form_response(self):
        from src.agent.agents.decision_agent import DecisionAgent

        agent = DecisionAgent(tool_registry=MagicMock(), llm_adapter=MagicMock())
        ctx = AgentContext(query="帮我总结一下", stock_code="600519")
        ctx.meta["response_mode"] = "chat"
        ctx.add_opinion(AgentOpinion(agent_name="technical", signal="buy", confidence=0.8, reasoning="趋势偏强"))

        opinion = agent.post_process(ctx, "建议继续观察量价配合，分批参与。")

        self.assertIsNotNone(opinion)
        self.assertEqual(ctx.get_data("final_response_text"), "建议继续观察量价配合，分批参与。")
        self.assertIsNone(ctx.get_data("final_dashboard"))
        self.assertEqual(opinion.signal, "buy")


class TestTechnicalAgentSkillPolicy(unittest.TestCase):
    """TechnicalAgent should only receive the legacy trend baseline for implicit/default runs."""

    def test_prompt_omits_legacy_default_policy_when_explicit_skill_selected(self):
        from src.agent.agents.technical_agent import TechnicalAgent

        agent = TechnicalAgent(
            tool_registry=MagicMock(),
            llm_adapter=MagicMock(),
            skill_instructions="### 技能 1: 缠论",
            technical_skill_policy="",
        )
        prompt = agent.system_prompt(AgentContext(query="分析 600519", stock_code="600519"))

        self.assertNotIn("Bias from MA5 < 2%", prompt)
        self.assertIn("### 技能 1: 缠论", prompt)

    def test_prompt_includes_legacy_default_policy_for_implicit_default_run(self):
        from src.agent.agents.technical_agent import TechnicalAgent
        from src.agent.skills.defaults import TECHNICAL_SKILL_RULES_EN

        agent = TechnicalAgent(
            tool_registry=MagicMock(),
            llm_adapter=MagicMock(),
            skill_instructions="### 技能 1: 默认多头趋势",
            technical_skill_policy=TECHNICAL_SKILL_RULES_EN,
        )
        prompt = agent.system_prompt(AgentContext(query="分析 600519", stock_code="600519"))

        self.assertIn("Bias from MA5 < 2%", prompt)
        self.assertIn("### 技能 1: 默认多头趋势", prompt)


class TestBaseAgentMessageAssembly(unittest.TestCase):
    """Test BaseAgent message assembly helpers."""

    @staticmethod
    def _make_agent():
        from src.agent.agents.base_agent import BaseAgent

        class DummyAgent(BaseAgent):
            agent_name = "dummy"

            def system_prompt(self, ctx: AgentContext) -> str:
                return "system"

            def build_user_message(self, ctx: AgentContext) -> str:
                return "current turn"

        return DummyAgent(tool_registry=MagicMock(), llm_adapter=MagicMock())

    def test_build_messages_includes_conversation_history(self):
        agent = self._make_agent()
        ctx = AgentContext(query="hello")
        ctx.meta["conversation_history"] = [
            {"role": "user", "content": "old question"},
            {"role": "assistant", "content": "old answer"},
        ]

        messages = agent._build_messages(ctx)

        self.assertEqual(messages[1], {"role": "user", "content": "old question"})
        self.assertEqual(messages[2], {"role": "assistant", "content": "old answer"})
        self.assertEqual(messages[-1], {"role": "user", "content": "current turn"})


class TestPortfolioAgentPostProcess(unittest.TestCase):
    """Test PortfolioAgent.post_process uses try_parse_json correctly."""

    def _make_agent(self):
        from src.agent.agents.portfolio_agent import PortfolioAgent
        mock_registry = MagicMock()
        mock_adapter = MagicMock()
        return PortfolioAgent(tool_registry=mock_registry, llm_adapter=mock_adapter)

    def test_parse_plain_json(self):
        agent = self._make_agent()
        ctx = AgentContext()
        data = {"portfolio_risk_score": 3, "summary": "Looks good"}
        op = agent.post_process(ctx, json.dumps(data))
        self.assertIsNotNone(op)
        self.assertEqual(op.signal, "buy")
        self.assertEqual(ctx.data.get("portfolio_assessment"), data)

    def test_parse_markdown_json(self):
        agent = self._make_agent()
        ctx = AgentContext()
        data = {"portfolio_risk_score": 8, "summary": "High risk"}
        raw = f"Here is the analysis:\n```json\n{json.dumps(data)}\n```"
        op = agent.post_process(ctx, raw)
        self.assertIsNotNone(op)
        self.assertEqual(op.signal, "sell")

    def test_parse_failure_returns_hold(self):
        agent = self._make_agent()
        ctx = AgentContext()
        op = agent.post_process(ctx, "This is not JSON at all")
        self.assertIsNotNone(op)
        self.assertEqual(op.signal, "hold")
        self.assertAlmostEqual(op.confidence, 0.3)


class TestDecisionAgentPostProcess(unittest.TestCase):
    """Test DecisionAgent dashboard normalization behaviour."""

    def test_normalizes_strong_decision_type_to_legacy_enum(self):
        from src.agent.agents.decision_agent import DecisionAgent

        agent = DecisionAgent(tool_registry=MagicMock(), llm_adapter=MagicMock())
        ctx = AgentContext(query="test", stock_code="600519")
        dashboard = {
            "decision_type": "strong_buy",
            "sentiment_score": 88,
            "analysis_summary": "High conviction",
            "stock_name": "贵州茅台",
        }

        opinion = agent.post_process(ctx, json.dumps(dashboard))

        self.assertIsNotNone(opinion)
        self.assertEqual(opinion.signal, "buy")
        self.assertEqual(ctx.get_data("final_dashboard")["decision_type"], "buy")


class TestIntelAgentPostProcess(unittest.TestCase):
    """Test IntelAgent JSON parsing and context caching behaviour."""

    def test_repairs_json_and_caches_intel_context(self):
        from src.agent.agents.intel_agent import IntelAgent

        agent = IntelAgent(tool_registry=MagicMock(), llm_adapter=MagicMock())
        ctx = AgentContext(query="test", stock_code="600519")
        raw = """```json
        {
          "signal": "hold",
          "confidence": 0.72,
          "reasoning": "情绪中性偏谨慎",
          "risk_alerts": ["股东减持"],
          "positive_catalysts": ["行业复苏"],
        }
        ```"""

        opinion = agent.post_process(ctx, raw)

        self.assertIsNotNone(opinion)
        self.assertEqual(opinion.signal, "hold")
        self.assertEqual(ctx.get_data("intel_opinion")["positive_catalysts"], ["行业复苏"])
        self.assertEqual(ctx.risk_flags[0]["description"], "股东减持")


if __name__ == "__main__":
    unittest.main()
