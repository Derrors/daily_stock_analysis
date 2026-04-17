# -*- coding: utf-8 -*-
"""Deterministic Markdown renderers for agent-facing outputs."""

from __future__ import annotations

from src.stock_analysis_skill.contracts import AnalysisResponse, MarketAnalysisResponse, StrategyResolutionResponse


class SkillMarkdownRenderer:
    """Minimal markdown rendering for agent-facing skill outputs."""

    @staticmethod
    def render_stock(response: AnalysisResponse) -> str:
        lines = [
            f"# Stock Analysis · {response.stock.code}",
            "",
            f"- Market: {response.stock.market.value}",
            f"- Decision: {response.decision.action.value}",
            f"- Summary: {response.decision.summary}",
        ]
        if response.trend is not None:
            lines.extend([
                f"- Trend: {response.trend.status.value}",
                f"- Trend Summary: {response.trend.summary}",
            ])
        if response.dashboard and response.dashboard.one_sentence:
            lines.extend(["", "## Dashboard", response.dashboard.one_sentence])
        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def render_market(response: MarketAnalysisResponse) -> str:
        lines = [
            f"# Market Analysis · {response.region}",
            "",
            response.summary,
        ]
        if response.indices:
            lines.append("")
            lines.append("## Indices")
            for index in response.indices:
                change = f"{index.change_pct:+.2f}%" if index.change_pct is not None else "N/A"
                current = f"{index.current:.2f}" if index.current is not None else "N/A"
                lines.append(f"- {index.name} ({index.code}): {current} / {change}")
        if response.report:
            lines.extend(["", "## Report", response.report])
        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def render_strategy_resolution(response: StrategyResolutionResponse) -> str:
        if not response.matched or response.strategy is None:
            return f"# Strategy Resolution\n\nNo strategy matched for: {response.query}\n"
        return (
            f"# Strategy Resolution\n\n"
            f"- Query: {response.query}\n"
            f"- Strategy: {response.strategy.display_name} (`{response.strategy.id}`)\n"
            f"- Description: {response.strategy.description}\n"
        )
