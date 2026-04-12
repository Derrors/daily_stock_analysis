# -*- coding: utf-8 -*-
"""Stage runtime helpers for :mod:`src.agent.orchestrator`.

Phase A extraction: move per-stage runtime compatibility logic out of
``AgentOrchestrator`` while preserving behaviour.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Optional

from src.agent.protocols import StageResult
from src.config import AGENT_MAX_STEPS_DEFAULT


class OrchestratorStageRuntime:
    """Compatibility helpers for orchestrator stage execution."""

    def __init__(self, *, max_steps: int) -> None:
        self.max_steps = max_steps

    def prepare_agent(self, agent: Any) -> Any:
        """Apply orchestrator-level runtime settings to a child agent."""
        if hasattr(agent, "max_steps"):
            if self.max_steps > AGENT_MAX_STEPS_DEFAULT:
                agent.max_steps = self.max_steps
            else:
                agent.max_steps = min(agent.max_steps, self.max_steps)
        return agent

    def callable_accepts_timeout_kwarg(self, func: Any) -> Optional[bool]:
        """Return whether a callable accepts ``timeout_seconds`` when inspectable."""
        if not callable(func):
            return None
        try:
            signature = inspect.signature(func)
        except (TypeError, ValueError):
            return None

        if "timeout_seconds" in signature.parameters:
            return True
        return any(
            param.kind is inspect.Parameter.VAR_KEYWORD
            for param in signature.parameters.values()
        )

    def agent_run_accepts_timeout(self, run_callable: Any) -> bool:
        """Best-effort compatibility check for legacy test doubles / custom agents."""
        side_effect = getattr(run_callable, "side_effect", None)
        accepts_timeout = self.callable_accepts_timeout_kwarg(side_effect)
        if accepts_timeout is not None:
            return accepts_timeout

        accepts_timeout = self.callable_accepts_timeout_kwarg(run_callable)
        if accepts_timeout is not None:
            return accepts_timeout

        return True

    def run_stage_agent(
        self,
        agent: Any,
        ctx: Any,
        progress_callback: Optional[Callable] = None,
        timeout_seconds: Optional[float] = None,
    ) -> StageResult:
        """Run a stage agent while preserving compatibility with older signatures."""
        run_kwargs = {"progress_callback": progress_callback}
        if (
            timeout_seconds is not None
            and timeout_seconds > 0
            and self.agent_run_accepts_timeout(agent.run)
        ):
            run_kwargs["timeout_seconds"] = timeout_seconds
        return agent.run(ctx, **run_kwargs)
