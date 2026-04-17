# -*- coding: utf-8 -*-
"""Analysis-side reusable helpers for the skill-first runtime."""

from .postprocess import (
    apply_placeholder_fill,
    check_content_integrity,
    fill_chip_structure_if_needed,
    fill_price_position_if_needed,
)
from .presentation import (
    build_market_snapshot,
    format_amount,
    format_percent,
    format_price,
    format_volume,
    get_stock_name_multi_source,
)
from .execution import execute_stock_analysis
from .litellm_caller import call_litellm
from .litellm_runtime import (
    dispatch_litellm_completion,
    has_channel_config,
    init_analyzer_litellm,
)
from .litellm_streaming import (
    LiteLLMStreamError,
    consume_litellm_stream,
    extract_stream_text,
    normalize_usage,
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
    build_analysis_system_prompt,
    resolve_skill_prompt_sections,
)

__all__ = [
    "AnalysisResult",
    "LiteLLMStreamError",
    "apply_placeholder_fill",
    "call_litellm",
    "execute_stock_analysis",
    "build_analysis_system_prompt",
    "build_integrity_complement_prompt",
    "build_integrity_retry_prompt",
    "build_market_snapshot",
    "build_stock_analysis_prompt",
    "check_content_integrity",
    "consume_litellm_stream",
    "dispatch_litellm_completion",
    "extract_stream_text",
    "fill_chip_structure_if_needed",
    "fill_price_position_if_needed",
    "fix_json_string",
    "format_amount",
    "format_percent",
    "format_price",
    "format_volume",
    "get_stock_name_multi_source",
    "has_channel_config",
    "init_analyzer_litellm",
    "normalize_usage",
    "parse_response",
    "parse_text_response",
    "resolve_skill_prompt_sections",
]
