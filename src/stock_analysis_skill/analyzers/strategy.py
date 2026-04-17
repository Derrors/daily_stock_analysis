# -*- coding: utf-8 -*-
"""User-facing strategy resolver backed by internal skill semantics."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.stock_analysis_skill.contracts import StrategyResolutionResponse, StrategySpec


class SkillResolver:
    """Load and resolve user-facing strategy YAML resources via the internal skill layer."""

    def __init__(self, strategies_dir: Optional[Path] = None):
        self.strategies_dir = strategies_dir or Path(__file__).resolve().parents[3] / "strategies"

    def list_strategy_specs(self) -> list[StrategySpec]:
        specs: list[StrategySpec] = []
        if not self.strategies_dir.exists():
            return specs

        for path in sorted(self.strategies_dir.glob("*.yaml")):
            spec = self._load_strategy(path)
            if spec is not None:
                specs.append(spec)
        return specs

    def resolve(self, query: Optional[str]) -> StrategyResolutionResponse:
        query_text = (query or "").strip()
        specs = self.list_strategy_specs()
        available = [spec.id for spec in specs]
        if not query_text:
            return StrategyResolutionResponse(query=query or "", matched=False, available=available)

        normalized = query_text.casefold()
        for spec in specs:
            candidates = {spec.id.casefold(), spec.display_name.casefold(), *(alias.casefold() for alias in spec.aliases)}
            if normalized in candidates:
                return StrategyResolutionResponse(
                    query=query_text,
                    matched=True,
                    strategy=spec,
                    available=available,
                )

        return StrategyResolutionResponse(query=query_text, matched=False, available=available)

    @staticmethod
    def _load_strategy(path: Path) -> Optional[StrategySpec]:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required to load strategy resources") from exc

        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        strategy_id = str(payload.get("name") or path.stem).strip()
        if not strategy_id:
            return None
        return StrategySpec(
            id=strategy_id,
            display_name=str(payload.get("display_name") or strategy_id),
            description=str(payload.get("description") or ""),
            category=payload.get("category"),
            aliases=list(payload.get("aliases") or []),
            required_tools=list(payload.get("required_tools") or []),
            instructions=str(payload.get("instructions") or ""),
            source_path=str(path),
        )

