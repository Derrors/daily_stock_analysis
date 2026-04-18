# -*- coding: utf-8 -*-
"""System-prompt assembly helpers for the analyzer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.market_context import get_market_guidelines, get_market_role
from src.report_language import normalize_report_language


def resolve_skill_prompt_sections(
    config: Any,
    *,
    requested_skills: Optional[List[str]] = None,
    skill_instructions: Optional[str] = None,
    default_skill_policy: Optional[str] = None,
    use_builtin_default_trend_prompt: Optional[bool] = None,
    resolved_state: Optional[Dict[str, Any]] = None,
) -> Tuple[Tuple[str, str, bool], Dict[str, Any]]:
    """Resolve skill instructions + default baseline + prompt mode with cache support."""
    if skill_instructions is not None and default_skill_policy is not None:
        sections = (
            skill_instructions,
            default_skill_policy,
            bool(use_builtin_default_trend_prompt) if use_builtin_default_trend_prompt is not None else False,
        )
        state = {
            "skill_instructions": sections[0],
            "default_skill_policy": sections[1],
            "use_builtin_default_trend_prompt": sections[2],
        }
        return sections, state

    if resolved_state is None:
        from src.agent.factory import resolve_skill_prompt_state

        prompt_state = resolve_skill_prompt_state(config, skills=requested_skills)
        resolved_state = {
            "skill_instructions": prompt_state.skill_instructions,
            "default_skill_policy": prompt_state.default_skill_policy,
            "use_builtin_default_trend_prompt": bool(getattr(prompt_state, "use_builtin_default_trend_prompt", False)),
        }

    sections = (
        skill_instructions if skill_instructions is not None else resolved_state.get("skill_instructions", ""),
        default_skill_policy if default_skill_policy is not None else resolved_state.get("default_skill_policy", ""),
        use_builtin_default_trend_prompt if use_builtin_default_trend_prompt is not None else bool(resolved_state.get("use_builtin_default_trend_prompt", False)),
    )
    return sections, resolved_state


def build_analysis_system_prompt(
    report_language: str,
    *,
    stock_code: str = "",
    builtin_default_trend_system_prompt: str,
    system_prompt: str,
    skill_instructions: str,
    default_skill_policy: str,
    use_builtin_default_trend_prompt: bool,
) -> str:
    """Build analyzer system prompt with market-role and language guidance."""
    lang = normalize_report_language(report_language)
    market_role = get_market_role(stock_code, lang)
    market_guidelines = get_market_guidelines(stock_code, lang)

    if use_builtin_default_trend_prompt:
        base_prompt = builtin_default_trend_system_prompt.replace(
            "{market_placeholder}", market_role
        ).replace(
            "{guidelines_placeholder}", market_guidelines
        )
    else:
        skills_section = ""
        if skill_instructions:
            skills_section = f"## 激活的交易技能\n\n{skill_instructions}\n"
        default_skill_policy_section = ""
        if default_skill_policy:
            default_skill_policy_section = f"{default_skill_policy}\n"
        base_prompt = (
            system_prompt.replace("{market_placeholder}", market_role)
            .replace("{guidelines_placeholder}", market_guidelines)
            .replace("{default_skill_policy_section}", default_skill_policy_section)
            .replace("{skills_section}", skills_section)
        )

    if lang == "en":
        return base_prompt + """

## Output Language (highest priority)

- Keep all JSON keys unchanged.
- `decision_type` must remain `buy|hold|sell`.
- All human-readable JSON values must be written in English.
- Use the common English company name when you are confident; otherwise keep the original listed company name instead of inventing one.
- This includes `stock_name`, `trend_prediction`, `operation_advice`, `confidence_level`, nested dashboard text, checklist items, and all narrative summaries.
"""

    return base_prompt + """

## 输出语言（最高优先级）

- 所有 JSON 键名保持不变。
- `decision_type` 必须保持为 `buy|hold|sell`。
- 所有面向用户的人类可读文本值必须使用中文。
"""
