# -*- coding: utf-8 -*-
"""LLM analyzer facade migrated out of ``src.analyzer``.

This module hosts the runtime assembly and public analyzer methods so the legacy
``src.analyzer`` file can progressively shrink into a compatibility wrapper.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Callable

from src.config import Config, get_config
from src.data.stock_mapping import STOCK_NAME_MAP
from src.report_language import normalize_report_language
from .execution import execute_stock_analysis
from .litellm_caller import call_litellm
from .litellm_runtime import (
    dispatch_litellm_completion,
    has_channel_config,
    init_analyzer_litellm,
)
from .litellm_streaming import (
    consume_litellm_stream,
    extract_stream_text,
    normalize_usage,
)
from .postprocess import (
    apply_placeholder_fill,
    check_content_integrity,
)
from .presentation import (
    build_market_snapshot,
    format_amount,
    format_percent,
    format_price,
    format_volume,
)
from .prompt_builder import build_stock_analysis_prompt
from .prompts import (
    build_integrity_complement_prompt,
    build_integrity_retry_prompt,
)
from .response_parser import (
    fix_json_string,
    parse_response,
    parse_text_response,
)
from .result import AnalysisResult
from .system_prompt import (
    ANALYSIS_SYSTEM_PROMPT_TEMPLATE,
    BUILTIN_DEFAULT_TREND_SYSTEM_PROMPT_TEMPLATE,
    TEXT_SYSTEM_PROMPT_TEMPLATE,
    build_analysis_system_prompt,
    resolve_skill_prompt_sections,
)

logger = logging.getLogger(__name__)


class StockAnalysisLLMAnalyzer:
    """Skill-first LLM analyzer facade."""

    BUILTIN_DEFAULT_TREND_SYSTEM_PROMPT = BUILTIN_DEFAULT_TREND_SYSTEM_PROMPT_TEMPLATE
    SYSTEM_PROMPT = ANALYSIS_SYSTEM_PROMPT_TEMPLATE
    TEXT_SYSTEM_PROMPT = TEXT_SYSTEM_PROMPT_TEMPLATE

    def _uses_legacy_analyzer_bridge(self) -> bool:
        """Return True when runtime compatibility should honor `src.analyzer` shims."""
        return self.__class__.__module__ == "src.analyzer"

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        config: Optional[Config] = None,
        skills: Optional[List[str]] = None,
        skill_instructions: Optional[str] = None,
        default_skill_policy: Optional[str] = None,
        use_builtin_default_trend_prompt: Optional[bool] = None,
    ):
        """Initialize LLM analyzer via LiteLLM.

        Args:
            api_key: Ignored (retained only for constructor compatibility). Keys are loaded from config.
        """
        self._config_override = config
        self._requested_skills = list(skills) if skills is not None else None
        self._skill_instructions_override = skill_instructions
        self._default_skill_policy_override = default_skill_policy
        self._use_builtin_default_trend_prompt_override = use_builtin_default_trend_prompt
        self._resolved_prompt_state: Optional[Dict[str, Any]] = None
        self._router = None
        self._litellm_available = False
        self._init_litellm()
        if not self._litellm_available:
            logger.warning("No LLM configured (LITELLM_MODEL / API keys), AI analysis will be unavailable")

    def _get_runtime_config(self) -> Config:
        """Return the runtime config, honoring injected overrides for tests/pipeline."""
        override = getattr(self, "_config_override", None)
        if override is not None:
            return override
        if self._uses_legacy_analyzer_bridge():
            try:
                from src import analyzer as legacy_analyzer_module

                return legacy_analyzer_module.get_config()
            except Exception:
                pass
        return get_config()

    def _get_skill_prompt_sections(self) -> tuple[str, str, bool]:
        """Resolve skill instructions + default baseline + prompt mode."""
        sections, resolved_state = resolve_skill_prompt_sections(
            self._get_runtime_config(),
            requested_skills=getattr(self, "_requested_skills", None),
            skill_instructions=getattr(self, "_skill_instructions_override", None),
            default_skill_policy=getattr(self, "_default_skill_policy_override", None),
            use_builtin_default_trend_prompt=getattr(self, "_use_builtin_default_trend_prompt_override", None),
            resolved_state=getattr(self, "_resolved_prompt_state", None),
        )
        self._resolved_prompt_state = resolved_state
        return sections

    def _get_analysis_system_prompt(self, report_language: str, stock_code: str = "") -> str:
        """Build the analyzer system prompt with output-language guidance."""
        skill_instructions, default_skill_policy, use_builtin_default_trend_prompt = self._get_skill_prompt_sections()
        return build_analysis_system_prompt(
            report_language,
            stock_code=stock_code,
            builtin_default_trend_system_prompt=self.BUILTIN_DEFAULT_TREND_SYSTEM_PROMPT,
            system_prompt=self.SYSTEM_PROMPT,
            skill_instructions=skill_instructions,
            default_skill_policy=default_skill_policy,
            use_builtin_default_trend_prompt=use_builtin_default_trend_prompt,
        )

    def _has_channel_config(self, config: Config) -> bool:
        """Delegate to runtime helper."""
        return has_channel_config(config)

    def _init_litellm(self) -> None:
        """Initialize analyzer router/runtime state."""
        self._router, self._litellm_available = init_analyzer_litellm(
            self._get_runtime_config()
        )

    def is_available(self) -> bool:
        """Check if LiteLLM is properly configured with at least one API key."""
        return self._router is not None or self._litellm_available

    def _dispatch_litellm_completion(
        self,
        model: str,
        call_kwargs: Dict[str, Any],
        *,
        config: Config,
        use_channel_router: bool,
        router_model_names: set[str],
    ) -> Any:
        """Delegate to runtime helper."""
        return dispatch_litellm_completion(
            model,
            call_kwargs,
            config=config,
            router=self._router,
            use_channel_router=use_channel_router,
            router_model_names=router_model_names,
        )

    def _normalize_usage(self, usage_obj: Any) -> Dict[str, Any]:
        """Delegate to streaming helper."""
        return normalize_usage(usage_obj)

    def _extract_stream_text(self, chunk: Any) -> str:
        """Delegate to streaming helper."""
        return extract_stream_text(chunk)

    def _consume_litellm_stream(
        self,
        stream_response: Any,
        *,
        model: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Delegate to streaming helper."""
        return consume_litellm_stream(
            stream_response,
            model=model,
            progress_callback=progress_callback,
        )

    def _call_litellm(
        self,
        prompt: str,
        generation_config: dict,
        *,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        stream_progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Delegate to LiteLLM call/fallback orchestrator."""
        return call_litellm(
            prompt,
            generation_config,
            config=self._get_runtime_config(),
            text_system_prompt=self.TEXT_SYSTEM_PROMPT,
            dispatch_completion=self._dispatch_litellm_completion,
            consume_stream=self._consume_litellm_stream,
            normalize_usage=self._normalize_usage,
            has_channel_config_fn=self._has_channel_config,
            system_prompt=system_prompt,
            stream=stream,
            stream_progress_callback=stream_progress_callback,
        )

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """Public entry point for free-form text generation."""
        try:
            result = self._call_litellm(
                prompt,
                generation_config={"max_tokens": max_tokens, "temperature": temperature},
            )
            if isinstance(result, tuple):
                text, model_used, usage = result
                self._persist_usage(usage, model_used, call_type="market_review")
                return text
            return result
        except Exception as exc:
            logger.error("[generate_text] LLM call failed: %s", exc)
            return None

    def analyze(
        self,
        context: Dict[str, Any],
        news_context: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        stream_progress_callback: Optional[Callable[[int], None]] = None,
    ) -> AnalysisResult:
        """Analyze one stock via the extracted execution workflow."""
        return execute_stock_analysis(
            context,
            news_context=news_context,
            progress_callback=progress_callback,
            stream_progress_callback=stream_progress_callback,
            stock_name_map=STOCK_NAME_MAP,
            get_runtime_config=self._get_runtime_config,
            get_analysis_system_prompt=self._get_analysis_system_prompt,
            is_available_fn=self.is_available,
            format_prompt=self._format_prompt,
            call_litellm=self._call_litellm,
            parse_response=self._parse_response,
            build_market_snapshot=self._build_market_snapshot,
            check_content_integrity=self._check_content_integrity,
            build_integrity_retry_prompt=self._build_integrity_retry_prompt,
            apply_placeholder_fill=self._apply_placeholder_fill,
            persist_usage=self._persist_usage,
        )

    def _format_prompt(
        self,
        context: Dict[str, Any],
        name: str,
        news_context: Optional[str] = None,
        report_language: str = "zh",
    ) -> str:
        """Delegate to prompt builder."""
        _, _, use_builtin_default_trend_prompt = self._get_skill_prompt_sections()
        return build_stock_analysis_prompt(
            context,
            name,
            news_context=news_context,
            report_language=report_language,
            use_builtin_default_trend_prompt=use_builtin_default_trend_prompt,
            runtime_config=self._get_runtime_config(),
        )

    def _format_volume(self, volume: Optional[float]) -> str:
        return format_volume(volume)

    def _format_amount(self, amount: Optional[float]) -> str:
        return format_amount(amount)

    def _format_percent(self, value: Optional[float]) -> str:
        return format_percent(value)

    def _format_price(self, value: Optional[float]) -> str:
        return format_price(value)

    def _build_market_snapshot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return build_market_snapshot(context)

    def _check_content_integrity(self, result: AnalysisResult) -> Tuple[bool, List[str]]:
        return check_content_integrity(result)

    def _build_integrity_complement_prompt(self, missing_fields: List[str], report_language: str = "zh") -> str:
        return build_integrity_complement_prompt(missing_fields, report_language=report_language)

    def _build_integrity_retry_prompt(
        self,
        base_prompt: str,
        previous_response: str,
        missing_fields: List[str],
        report_language: str = "zh",
    ) -> str:
        return build_integrity_retry_prompt(
            base_prompt,
            previous_response,
            missing_fields,
            report_language=report_language,
        )

    def _apply_placeholder_fill(self, result: AnalysisResult, missing_fields: List[str]) -> None:
        apply_placeholder_fill(result, missing_fields)

    def _persist_usage(self, usage: Dict[str, Any], model_used: Optional[str], **kwargs: Any) -> None:
        """Persist LLM usage lazily so analyzer imports do not require storage deps."""
        if self._uses_legacy_analyzer_bridge():
            try:
                from src import analyzer as legacy_analyzer_module

                legacy_analyzer_module.persist_llm_usage(usage, model_used, **kwargs)
                return
            except Exception as exc:
                logger.debug("[persist_usage] legacy bridge skipped: %s", exc)
        try:
            from src.llm_usage import persist_llm_usage

            persist_llm_usage(usage, model_used, **kwargs)
        except Exception as exc:
            logger.debug("[persist_usage] skipped: %s", exc)

    def _parse_response(
        self,
        response_text: str,
        code: str,
        name: str,
    ) -> AnalysisResult:
        report_language = normalize_report_language(
            getattr(self._get_runtime_config(), "report_language", "zh")
        )
        return parse_response(response_text, code, name, report_language=report_language)

    def _fix_json_string(self, json_str: str) -> str:
        return fix_json_string(json_str)

    def _parse_text_response(
        self,
        response_text: str,
        code: str,
        name: str,
    ) -> AnalysisResult:
        report_language = normalize_report_language(
            getattr(self._get_runtime_config(), "report_language", "zh")
        )
        return parse_text_response(response_text, code, name, report_language=report_language)

    def batch_analyze(
        self,
        contexts: List[Dict[str, Any]],
        delay_between: float = 2.0,
    ) -> List[AnalysisResult]:
        """Analyze multiple contexts sequentially with pacing."""
        results = []
        for i, context in enumerate(contexts):
            if i > 0:
                logger.debug("等待 %s 秒后继续...", delay_between)
                time.sleep(delay_between)
            result = self.analyze(context)
            results.append(result)
        return results


__all__ = ["StockAnalysisLLMAnalyzer"]
