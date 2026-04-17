# -*- coding: utf-8 -*-
"""Focused runtime / budget / timeout tests for AgentOrchestrator."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock as _MagicMock
    sys.modules["litellm"] = _MagicMock()

from src.agent.protocols import AgentContext, AgentOpinion, StageResult, StageStatus
from src.config import AGENT_MAX_STEPS_DEFAULT


class TestOrchestratorRuntime(unittest.TestCase):
    """Test runtime execution paths after orchestrator refactor."""

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

    def test_prepare_agent_uses_default_constant_as_raise_threshold(self):
        orch = self._make_orchestrator()
        agent = MagicMock(agent_name="technical", max_steps=6)

        prepared = orch._prepare_agent(agent)
        self.assertIs(prepared, agent)
        self.assertEqual(agent.max_steps, 6)

        orch.max_steps = 12
        agent.max_steps = 6
        orch._prepare_agent(agent)
        self.assertEqual(agent.max_steps, 12)

        orch.max_steps = 5
        agent.max_steps = 6
        orch._prepare_agent(agent)
        self.assertEqual(agent.max_steps, 5)

    def test_execute_pipeline_stops_on_critical_failure(self):
        orch = self._make_orchestrator()
        technical = MagicMock(agent_name="technical")
        technical.run.return_value = self._stage_result("technical", StageStatus.FAILED, error="boom")

        with patch.object(orch, "_build_agent_chain", return_value=[technical]):
            result = orch._execute_pipeline(AgentContext(query="test"))

        self.assertFalse(result.success)
        self.assertIn("technical", result.error)
        self.assertEqual(result.total_tokens, 0)

    def test_execute_pipeline_degrades_on_intel_failure(self):
        orch = self._make_orchestrator()
        ctx = AgentContext(query="test", stock_code="600519")
        ctx.add_opinion(AgentOpinion(agent_name="technical", signal="buy", confidence=0.8, reasoning="Strong trend"))

        intel = MagicMock(agent_name="intel")
        intel.run.return_value = self._stage_result("intel", StageStatus.FAILED, error="news down")
        decision = MagicMock(agent_name="decision")
        decision.run.return_value = self._stage_result("decision")

        with patch.object(orch, "_build_agent_chain", return_value=[intel, decision]):
            result = orch._execute_pipeline(ctx, parse_dashboard=False)

        self.assertTrue(result.success)
        self.assertIn("Analysis Summary", result.content)

    def test_execute_pipeline_degrades_on_skill_agent_failure_and_continues_to_decision(self):
        orch = self._make_orchestrator()
        orch.mode = "specialist"
        ctx = AgentContext(query="test", stock_code="600519")
        ctx.add_opinion(AgentOpinion(agent_name="technical", signal="buy", confidence=0.8, reasoning="Strong trend"))

        technical = MagicMock(agent_name="technical")
        technical.run.return_value = self._stage_result("technical")
        intel = MagicMock(agent_name="intel")
        intel.run.return_value = self._stage_result("intel")
        risk = MagicMock(agent_name="risk")
        risk.run.return_value = self._stage_result("risk")
        skill = MagicMock(agent_name="skill_bull_trend")
        skill.run.return_value = self._stage_result("skill_bull_trend", StageStatus.FAILED, error="skill boom")
        decision = MagicMock(agent_name="decision")
        decision.run.return_value = self._stage_result("decision")

        with patch.object(orch, "_build_agent_chain", return_value=[technical, intel, risk, decision]):
            with patch.object(orch, "_build_specialist_agents", return_value=[skill]):
                result = orch._execute_pipeline(ctx, parse_dashboard=False)

        self.assertTrue(result.success)
        self.assertIn("Analysis Summary", result.content)
        skill.run.assert_called_once()
        decision.run.assert_called_once()

    def test_execute_pipeline_skips_stage_when_remaining_budget_below_minimum(self):
        orch = self._make_orchestrator(config=SimpleNamespace(agent_orchestrator_timeout_s=20))
        ctx = AgentContext(query="test", stock_code="600519", stock_name="贵州茅台")

        technical = MagicMock(agent_name="technical")

        def _run_technical(run_ctx, progress_callback=None):
            run_ctx.add_opinion(AgentOpinion(
                agent_name="technical",
                signal="buy",
                confidence=0.8,
                reasoning="技术面结构未出现明显拐点，趋势偏强。",
                raw_data={"ma_alignment": "bullish", "trend_score": 82, "volume_status": "normal"},
            ))
            return self._stage_result("technical")

        technical.run.side_effect = _run_technical
        intel = MagicMock(agent_name="intel", tool_names=["news_search"])
        intel.run.side_effect = AssertionError("intel should be skipped due to budget guard")
        times = iter([0.0, 0.2, 0.3, 14.6, 14.7])

        def _next_time():
            return next(times, 100.0)

        with patch.object(orch, "_build_agent_chain", return_value=[technical, intel]):
            with patch("src.agent.orchestrator.time.time", side_effect=_next_time):
                result = orch._execute_pipeline(ctx)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.dashboard)
        self.assertIsNotNone(result.content)
        self.assertIn("insufficient budget", (result.error or "").lower())
        self.assertIn("[降级结果]", result.dashboard["analysis_summary"])
        technical.run.assert_called_once()
        intel.run.assert_not_called()

    def test_execute_pipeline_skips_toolless_decision_with_low_remaining_budget(self):
        orch = self._make_orchestrator(config=SimpleNamespace(agent_orchestrator_timeout_s=20))
        ctx = AgentContext(query="test", stock_code="600519", stock_name="贵州茅台")

        technical = MagicMock(agent_name="technical")

        def _run_technical(run_ctx, progress_callback=None):
            run_ctx.add_opinion(AgentOpinion(
                agent_name="technical",
                signal="buy",
                confidence=0.8,
                reasoning="技术面结构未出现明显拐点，趋势偏强。",
                raw_data={"ma_alignment": "bullish", "trend_score": 82, "volume_status": "normal"},
            ))
            return self._stage_result("technical")

        technical.run.side_effect = _run_technical
        decision = MagicMock(agent_name="decision", tool_names=[])

        def _run_decision(run_ctx, progress_callback=None):
            run_ctx.add_opinion(AgentOpinion(
                agent_name="decision",
                signal="buy",
                confidence=0.87,
                reasoning="综合技术与情绪判断，倾向于买入。",
            ))
            return self._stage_result("decision")

        decision.run.side_effect = _run_decision
        times = iter([0.0, 0.2, 0.3, 14.6, 14.7])

        def _next_time():
            return next(times, 100.0)

        with patch.object(orch, "_build_agent_chain", return_value=[technical, decision]):
            with patch("src.agent.orchestrator.time.time", side_effect=_next_time):
                result = orch._execute_pipeline(ctx)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.content)
        self.assertIn("insufficient budget", (result.error or "").lower())
        self.assertEqual(result.total_steps, 1)
        technical.run.assert_called_once()
        decision.run.assert_not_called()

    def test_execute_pipeline_first_stage_still_runs_when_timeout_short(self):
        orch = self._make_orchestrator(config=SimpleNamespace(agent_orchestrator_timeout_s=10))
        ctx = AgentContext(query="test", stock_code="600519", stock_name="贵州茅台")

        technical = MagicMock(agent_name="technical")
        technical.run.side_effect = lambda run_ctx, progress_callback=None: self._stage_result("technical")
        times = iter([0.0, 0.2, 0.3, 0.4, 0.5])

        def _next_time():
            return next(times, 1.0)

        with patch.object(orch, "_build_agent_chain", return_value=[technical]):
            with patch("src.agent.orchestrator.time.time", side_effect=_next_time):
                result = orch._execute_pipeline(ctx)

        self.assertIsNotNone(result.error)
        self.assertEqual(result.total_steps, 1)
        technical.run.assert_called_once()
        self.assertNotIn("insufficient budget", (result.error or "").lower())

    def test_execute_pipeline_times_out_after_stage(self):
        orch = self._make_orchestrator(config=SimpleNamespace(agent_orchestrator_timeout_s=1))
        agent = MagicMock(agent_name="technical")
        agent.run.return_value = self._stage_result("technical")

        with patch.object(orch, "_build_agent_chain", return_value=[agent]):
            with patch("src.agent.orchestrator.time.time", side_effect=[0.0, 0.1, 1.2, 1.2, 1.2, 1.2]):
                result = orch._execute_pipeline(AgentContext(query="test"))

        self.assertFalse(result.success)
        self.assertIn("timed out", result.error)

    def test_execute_pipeline_timeout_after_decision_preserves_dashboard(self):
        orch = self._make_orchestrator(config=SimpleNamespace(agent_orchestrator_timeout_s=1, agent_risk_override=True))
        ctx = AgentContext(query="test", stock_code="600519", stock_name="贵州茅台")
        decision = MagicMock(agent_name="decision")

        def _run_decision(run_ctx, progress_callback=None):
            dashboard = {
                "stock_name": "贵州茅台",
                "decision_type": "strong_buy",
                "sentiment_score": 88,
                "operation_advice": {
                    "no_position": "分批布局",
                    "has_position": "继续持有",
                },
                "analysis_summary": "趋势仍强，回踩可观察。",
                "dashboard": {
                    "key_levels": {
                        "support": 1800,
                        "stop_loss": 1760,
                        "resistance": 1900,
                    }
                },
            }
            run_ctx.set_data("final_dashboard", dashboard)
            run_ctx.add_opinion(AgentOpinion(
                agent_name="decision",
                signal="buy",
                confidence=0.88,
                reasoning="趋势仍强，回踩可观察。",
                raw_data=dashboard,
            ))
            return self._stage_result("decision")

        decision.run.side_effect = _run_decision

        with patch.object(orch, "_build_agent_chain", return_value=[decision]):
            with patch("src.agent.orchestrator.time.time", side_effect=[0.0, 0.1, 1.2, 1.2, 1.2]):
                result = orch._execute_pipeline(ctx, parse_dashboard=True)

        self.assertTrue(result.success)
        self.assertIn("timed out", result.error)
        self.assertEqual(result.dashboard["decision_type"], "buy")
        self.assertEqual(result.dashboard["operation_advice"], "买入")
        self.assertEqual(
            result.dashboard["dashboard"]["battle_plan"]["sniper_points"]["stop_loss"],
            1760.0,
        )

    def test_execute_pipeline_timeout_after_intel_synthesizes_dashboard(self):
        orch = self._make_orchestrator(config=SimpleNamespace(agent_orchestrator_timeout_s=1, agent_risk_override=True))
        ctx = AgentContext(query="test", stock_code="301308", stock_name="江波龙")
        ctx.set_data("realtime_quote", {"price": 326.17, "volume_ratio": 1.0, "turnover_rate": 6.77})
        ctx.set_data("chip_distribution", {"profit_ratio": 68.8, "avg_cost": 307.67, "concentration_90": 15.28})

        technical = MagicMock(agent_name="technical")
        intel = MagicMock(agent_name="intel")

        def _run_technical(run_ctx, progress_callback=None):
            run_ctx.add_opinion(AgentOpinion(
                agent_name="technical",
                signal="buy",
                confidence=0.75,
                reasoning="强势多头排列，价格回踩 MA5。",
                key_levels={"support": 301.61, "resistance": 340.44, "stop_loss": 295.0},
                raw_data={"ma_alignment": "bullish", "trend_score": 73, "volume_status": "normal"},
            ))
            return self._stage_result("technical")

        technical.run.side_effect = _run_technical
        intel.run.return_value = self._stage_result("intel")

        with patch.object(orch, "_build_agent_chain", return_value=[technical, intel]):
            with patch("src.agent.orchestrator.time.time", side_effect=[0.0, 0.1, 0.2, 0.3, 1.2, 1.2, 1.2]):
                result = orch._execute_pipeline(ctx, parse_dashboard=True)

        self.assertTrue(result.success)
        self.assertIn("timed out", result.error)
        self.assertEqual(result.dashboard["decision_type"], "buy")
        self.assertIn("降级结果", result.dashboard["analysis_summary"])
        self.assertEqual(
            result.dashboard["dashboard"]["battle_plan"]["sniper_points"]["stop_loss"],
            295.0,
        )


if __name__ == "__main__":
    unittest.main()
