# -*- coding: utf-8 -*-
"""Focused result / chat-mode tests for AgentOrchestrator."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock as _MagicMock
    sys.modules["litellm"] = _MagicMock()

from src.agent.protocols import AgentContext, AgentOpinion, StageResult, StageStatus


class TestOrchestratorResults(unittest.TestCase):
    @staticmethod
    def _make_orchestrator(config=None):
        from src.agent.orchestrator import AgentOrchestrator
        return AgentOrchestrator(
            tool_registry=MagicMock(),
            llm_adapter=MagicMock(),
            config=config,
        )

    @staticmethod
    def _stage_result(name, status=StageStatus.COMPLETED, error=None, raw_text="ok"):
        result = StageResult(stage_name=name, status=status, error=error)
        result.meta["raw_text"] = raw_text
        result.meta["models_used"] = ["test/model"]
        return result

    def test_run_wraps_orchestrator_result(self):
        from src.agent.orchestrator import OrchestratorResult

        orch = self._make_orchestrator()
        fake_result = OrchestratorResult(success=True, content="done", total_steps=2, total_tokens=11, model="x")
        with patch.object(orch, "_execute_pipeline", return_value=fake_result):
            result = orch.run("Analyze 600519")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "done")
        self.assertEqual(result.total_steps, 2)

    def test_chat_loads_prior_history_into_context(self):
        from src.agent.orchestrator import OrchestratorResult

        orch = self._make_orchestrator()
        history = [
            {"role": "user", "content": "之前的问题"},
            {"role": "assistant", "content": "之前的回答"},
        ]
        captured = {}

        def fake_execute(ctx, parse_dashboard=False, progress_callback=None):
            captured["history"] = ctx.meta.get("conversation_history")
            return OrchestratorResult(success=True, content="assistant reply")

        with patch.object(orch, "_execute_pipeline", side_effect=fake_execute):
            with patch("src.agent.conversation.conversation_manager.get_or_create") as get_or_create:
                get_or_create.return_value.get_history.return_value = history
                with patch("src.agent.conversation.conversation_manager.add_message"):
                    orch.chat("hello", "session-1")

        self.assertEqual(captured["history"], history)

    def test_chat_persists_user_and_assistant_messages(self):
        from src.agent.orchestrator import OrchestratorResult

        orch = self._make_orchestrator()
        fake_result = OrchestratorResult(success=True, content="assistant reply")

        with patch.object(orch, "_execute_pipeline", return_value=fake_result):
            with patch("src.agent.conversation.conversation_manager.add_message") as add_message:
                result = orch.chat("hello", "session-1")

        self.assertTrue(result.success)
        self.assertEqual(add_message.call_count, 2)
        add_message.assert_any_call("session-1", "user", "hello")
        add_message.assert_any_call("session-1", "assistant", "assistant reply")

    def test_chat_persists_failure_message(self):
        from src.agent.orchestrator import OrchestratorResult

        orch = self._make_orchestrator()
        fake_result = OrchestratorResult(success=False, error="boom")

        with patch.object(orch, "_execute_pipeline", return_value=fake_result):
            with patch("src.agent.conversation.conversation_manager.add_message") as add_message:
                result = orch.chat("hello", "session-2")

        self.assertFalse(result.success)
        add_message.assert_any_call("session-2", "assistant", "[分析失败] boom")

    def test_execute_pipeline_fails_when_dashboard_parse_fails(self):
        orch = self._make_orchestrator()
        ctx = AgentContext(query="test", stock_code="600519")
        decision = MagicMock(agent_name="decision")

        def fake_run(pipeline_ctx, progress_callback=None):
            pipeline_ctx.set_data("final_dashboard_raw", "not valid json")
            return self._stage_result("decision")

        decision.run.side_effect = fake_run

        with patch.object(orch, "_build_agent_chain", return_value=[decision]):
            result = orch._execute_pipeline(ctx, parse_dashboard=True)

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Failed to parse dashboard JSON from agent response")

    def test_execute_pipeline_chat_prefers_free_form_response(self):
        orch = self._make_orchestrator()
        ctx = AgentContext(query="请总结一下", stock_code="600519")
        ctx.meta["response_mode"] = "chat"
        decision = MagicMock(agent_name="decision")

        def fake_run(pipeline_ctx, progress_callback=None):
            pipeline_ctx.set_data("final_dashboard", {"decision_type": "buy", "analysis_summary": "json dashboard"})
            pipeline_ctx.set_data("final_response_text", "这是自然语言回复")
            return self._stage_result("decision", raw_text="这是自然语言回复")

        decision.run.side_effect = fake_run

        with patch.object(orch, "_build_agent_chain", return_value=[decision]):
            result = orch._execute_pipeline(ctx, parse_dashboard=False)

        self.assertTrue(result.success)
        self.assertEqual(result.content, "这是自然语言回复")

    def test_strategy_agents_are_selected_after_technical_stage(self):
        orch = self._make_orchestrator()
        orch.mode = "specialist"
        ctx = AgentContext(query="分析600519", stock_code="600519")
        ctx.meta["response_mode"] = "chat"

        technical = MagicMock(agent_name="technical")

        def _run_technical(run_ctx, progress_callback=None):
            run_ctx.add_opinion(AgentOpinion(
                agent_name="technical",
                signal="buy",
                confidence=0.8,
                reasoning="trend ok",
                raw_data={"ma_alignment": "bullish", "trend_score": 78, "volume_status": "normal"},
            ))
            return self._stage_result("technical")

        technical.run.side_effect = _run_technical

        intel = MagicMock(agent_name="intel")
        intel.run.return_value = self._stage_result("intel")

        risk = MagicMock(agent_name="risk")
        risk.run.return_value = self._stage_result("risk")

        strategy = MagicMock(agent_name="skill_bull_trend")

        def _run_strategy(run_ctx, progress_callback=None):
            run_ctx.add_opinion(AgentOpinion(
                agent_name="skill_bull_trend",
                signal="buy",
                confidence=0.7,
                reasoning="strategy ok",
            ))
            return self._stage_result("skill_bull_trend")

        strategy.run.side_effect = _run_strategy

        decision = MagicMock(agent_name="decision")
        decision.run.return_value = self._stage_result("decision", raw_text="final answer")

        def _build_specialist_agents(run_ctx):
            self.assertTrue(any(op.agent_name == "technical" for op in run_ctx.opinions))
            return [strategy]

        with patch.object(orch, "_build_agent_chain", return_value=[technical, intel, risk, decision]):
            with patch.object(orch, "_build_specialist_agents", side_effect=_build_specialist_agents) as build_specialist_agents:
                result = orch._execute_pipeline(ctx, parse_dashboard=False)

        self.assertTrue(result.success)
        self.assertEqual(result.content, "final answer")
        build_specialist_agents.assert_called_once()
        strategy.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
