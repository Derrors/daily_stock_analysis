# -*- coding: utf-8 -*-
"""Pipeline-building helpers for :mod:`src.agent.orchestrator`.

Phase A extraction: move agent-chain construction and skill aggregation
out of ``AgentOrchestrator`` while preserving the orchestrator's public API.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, List

from src.agent.protocols import AgentContext

logger = logging.getLogger(__name__)


class OrchestratorPipelineBuilder:
    """Build agent chains and aggregate specialist opinions.

    This helper keeps ``AgentOrchestrator`` focused on orchestration flow while
    preserving the exact runtime behaviour of the previous in-class methods.
    """

    def __init__(
        self,
        *,
        tool_registry: Any,
        llm_adapter: Any,
        skill_instructions: str = "",
        technical_skill_policy: str = "",
        prepare_agent: Callable[[Any], Any],
    ) -> None:
        self.tool_registry = tool_registry
        self.llm_adapter = llm_adapter
        self.skill_instructions = skill_instructions
        self.technical_skill_policy = technical_skill_policy
        self.prepare_agent = prepare_agent

    def _common_kwargs(self) -> dict[str, Any]:
        return {
            "tool_registry": self.tool_registry,
            "llm_adapter": self.llm_adapter,
            "skill_instructions": self.skill_instructions,
            "technical_skill_policy": self.technical_skill_policy,
        }

    def build_agent_chain(self, mode: str, ctx: AgentContext) -> List[Any]:
        """Instantiate the ordered agent list based on orchestrator mode."""
        from src.agent.agents.decision_agent import DecisionAgent
        from src.agent.agents.intel_agent import IntelAgent
        from src.agent.agents.risk_agent import RiskAgent
        from src.agent.agents.technical_agent import TechnicalAgent

        common_kwargs = self._common_kwargs()

        technical = self.prepare_agent(TechnicalAgent(**common_kwargs))
        intel = self.prepare_agent(IntelAgent(**common_kwargs))
        risk = self.prepare_agent(RiskAgent(**common_kwargs))
        decision = self.prepare_agent(DecisionAgent(**common_kwargs))

        if mode == "quick":
            return [technical, decision]
        if mode == "standard":
            return [technical, intel, decision]
        if mode == "full":
            return [technical, intel, risk, decision]
        if mode == "specialist":
            # Specialist agents are inserted lazily right before the decision
            # stage so the router can see the finished technical opinion.
            return [technical, intel, risk, decision]
        return [technical, intel, decision]

    def build_specialist_agents(self, ctx: AgentContext) -> List[Any]:
        """Build specialist sub-agents based on requested skills."""
        try:
            from src.agent.skills.router import SkillRouter
            from src.agent.skills.skill_agent import SkillAgent

            router = SkillRouter()
            selected = router.select_skills(ctx)
            if not selected:
                return []

            common_kwargs = self._common_kwargs()
            agents: List[Any] = []
            for skill_id in selected[:3]:  # cap at 3 concurrent skills
                agent = self.prepare_agent(
                    SkillAgent(
                        skill_id=skill_id,
                        **common_kwargs,
                    )
                )
                agents.append(agent)
            return agents
        except Exception as exc:
            logger.warning("[PipelineBuilder] failed to build skill agents: %s", exc)
            return []

    def aggregate_skill_opinions(self, ctx: AgentContext) -> None:
        """Run SkillAggregator to produce a consensus opinion."""
        try:
            from src.agent.skills.aggregator import SkillAggregator

            aggregator = SkillAggregator()
            consensus = aggregator.aggregate(ctx)
            if consensus:
                ctx.opinions.append(consensus)
                ctx.set_data(
                    "skill_consensus",
                    {
                        "signal": consensus.signal,
                        "confidence": consensus.confidence,
                        "reasoning": consensus.reasoning,
                    },
                )
                logger.info(
                    "[PipelineBuilder] skill consensus: signal=%s confidence=%.2f",
                    consensus.signal,
                    consensus.confidence,
                )
            else:
                logger.info("[PipelineBuilder] no skill opinions to aggregate")
        except Exception as exc:
            logger.warning("[PipelineBuilder] skill aggregation failed: %s", exc)
