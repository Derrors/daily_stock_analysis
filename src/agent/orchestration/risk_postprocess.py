# -*- coding: utf-8 -*-
"""Risk post-processing helpers for :mod:`src.agent.orchestrator`.

Phase A extraction: move risk override / warning merge control flow out of
``AgentOrchestrator`` while preserving its existing helper functions and
behaviour via callback injection.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

from src.agent.protocols import AgentContext, normalize_decision_signal

logger = logging.getLogger(__name__)


class OrchestratorRiskPostprocessor:
    """Apply post-decision risk overrides to a synthesized dashboard."""

    def apply_risk_override(
        self,
        ctx: AgentContext,
        *,
        risk_override_enabled: bool,
        merge_risk_warning: Callable[[Any, Dict[str, Any], List[Dict[str, Any]], str], str],
        adjust_sentiment_score: Callable[[int, str], int],
        adjust_operation_advice: Callable[[str, str], str],
        downgrade_signal: Callable[[str, int], str],
    ) -> None:
        """Apply risk-agent veto/downgrade rules to the final dashboard."""
        if ctx.get_data("risk_override_applied"):
            return

        if not risk_override_enabled:
            return

        dashboard = ctx.get_data("final_dashboard")
        if not isinstance(dashboard, dict):
            return

        risk_opinion = next((op for op in reversed(ctx.opinions) if op.agent_name == "risk"), None)
        risk_raw = risk_opinion.raw_data if risk_opinion and isinstance(risk_opinion.raw_data, dict) else {}

        adjustment = str(risk_raw.get("signal_adjustment") or "").lower()
        has_high_flag = any(str(flag.get("severity", "")).lower() == "high" for flag in ctx.risk_flags)
        veto_buy = bool(risk_raw.get("veto_buy")) or adjustment == "veto" or has_high_flag

        current_signal = normalize_decision_signal(dashboard.get("decision_type", "hold"))
        new_signal = current_signal
        if veto_buy and current_signal == "buy":
            new_signal = "hold"
        elif adjustment == "downgrade_one":
            new_signal = downgrade_signal(current_signal, steps=1)
        elif adjustment == "downgrade_two":
            new_signal = downgrade_signal(current_signal, steps=2)

        if new_signal == current_signal:
            return

        dashboard["decision_type"] = new_signal
        dashboard["risk_warning"] = merge_risk_warning(
            dashboard.get("risk_warning"),
            risk_raw,
            ctx.risk_flags,
            new_signal,
        )

        sentiment_score = dashboard.get("sentiment_score")
        try:
            score = int(sentiment_score)
        except (TypeError, ValueError):
            score = 50
        dashboard["sentiment_score"] = adjust_sentiment_score(score, new_signal)

        operation_advice = dashboard.get("operation_advice")
        if isinstance(operation_advice, str):
            dashboard["operation_advice"] = adjust_operation_advice(operation_advice, new_signal)

        summary = dashboard.get("analysis_summary")
        if isinstance(summary, str) and summary:
            dashboard["analysis_summary"] = f"[风控下调: {current_signal} -> {new_signal}] {summary}"

        dashboard_block = dashboard.get("dashboard")
        if isinstance(dashboard_block, dict):
            core = dashboard_block.get("core_conclusion")
            if isinstance(core, dict):
                signal_type = {
                    "buy": "🟡持有观望",
                    "hold": "🟡持有观望",
                    "sell": "🔴卖出信号",
                }.get(new_signal, "⚠️风险警告")
                core["signal_type"] = signal_type
                sentence = core.get("one_sentence")
                if isinstance(sentence, str) and sentence:
                    core["one_sentence"] = f"{sentence}（风控下调）"
                position = core.get("position_advice")
                if isinstance(position, dict):
                    if new_signal == "hold":
                        position["no_position"] = "风险未解除前先观望，等待更清晰的入场条件。"
                        position["has_position"] = "谨慎持有并收紧止损，待风险缓解后再考虑加仓。"
                    elif new_signal == "sell":
                        position["no_position"] = "风险明显偏高，暂不新开仓。"
                        position["has_position"] = "优先控制回撤，建议减仓或退出高风险仓位。"

        ctx.set_data(
            "final_dashboard",
            dashboard,
        )
        ctx.set_data(
            "risk_override_applied",
            {
                "from": current_signal,
                "to": new_signal,
                "adjustment": adjustment or ("veto" if veto_buy else "none"),
            },
        )

        for opinion in reversed(ctx.opinions):
            if opinion.agent_name == "decision":
                opinion.signal = new_signal
                if isinstance(dashboard.get("analysis_summary"), str):
                    opinion.reasoning = dashboard["analysis_summary"]
                opinion.raw_data = dashboard
                break

        logger.info(
            "[RiskPostprocess] risk override applied: %s -> %s (adjustment=%s, high_flag=%s)",
            current_signal,
            new_signal,
            adjustment or ("veto" if veto_buy else "none"),
            has_high_flag,
        )

    @staticmethod
    def merge_risk_warning(
        existing_warning: Any,
        risk_raw: Dict[str, Any],
        risk_flags: List[Dict[str, Any]],
        signal: str,
    ) -> str:
        """Build a concise risk warning after a forced downgrade."""
        warnings: List[str] = []
        if isinstance(existing_warning, str) and existing_warning.strip():
            warnings.append(existing_warning.strip())
        if isinstance(risk_raw.get("reasoning"), str) and risk_raw["reasoning"].strip():
            warnings.append(risk_raw["reasoning"].strip())
        for flag in risk_flags[:3]:
            description = str(flag.get("description", "")).strip()
            severity = str(flag.get("severity", "")).lower()
            if description:
                warnings.append(f"[{severity or 'risk'}] {description}")
        prefix = f"风控接管：最终信号已下调为 {signal}。"
        merged = " ".join(dict.fromkeys([prefix] + warnings))
        return merged[:500]
