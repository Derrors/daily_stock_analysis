# -*- coding: utf-8 -*-
"""Execution workflow helpers for stock analyzer mainline."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional

from src.report_language import normalize_report_language
from .result import AnalysisResult


logger = logging.getLogger(__name__)


def execute_stock_analysis(
    context: Dict[str, Any],
    *,
    news_context: Optional[str],
    progress_callback: Optional[Callable[[int, str], None]],
    stream_progress_callback: Optional[Callable[[int], None]],
    stock_name_map: Dict[str, str],
    get_runtime_config: Callable[[], Any],
    get_analysis_system_prompt: Callable[[str, str], str],
    is_available_fn: Callable[[], bool],
    format_prompt: Callable[..., str],
    call_litellm: Callable[..., Any],
    parse_response: Callable[[str, str, str], AnalysisResult],
    build_market_snapshot: Callable[[Dict[str, Any]], Dict[str, Any]],
    check_content_integrity: Callable[[AnalysisResult], Any],
    build_integrity_retry_prompt: Callable[[str, str, list[str], str], str],
    apply_placeholder_fill: Callable[[AnalysisResult, list[str]], None],
    persist_usage: Callable[..., Any],
) -> AnalysisResult:
    """Run the analyzer main workflow with injected hooks for compatibility."""

    def _emit_progress(progress: int, message: str) -> None:
        if progress_callback is None:
            return
        try:
            progress_callback(progress, message)
        except Exception as exc:
            logger.debug("[analyzer] progress callback skipped: %s", exc)

    code = context.get("code", "Unknown")
    config = get_runtime_config()
    report_language = normalize_report_language(getattr(config, "report_language", "zh"))
    system_prompt = get_analysis_system_prompt(report_language, stock_code=code)

    request_delay = config.gemini_request_delay
    if request_delay > 0:
        logger.debug("[LLM] 请求前等待 %.1f 秒...", request_delay)
        _emit_progress(65, f"{code}：LLM 请求前等待 {request_delay:.1f} 秒")
        time.sleep(request_delay)

    name = context.get("stock_name")
    if not name or name.startswith("股票"):
        if "realtime" in context and context["realtime"].get("name"):
            name = context["realtime"]["name"]
        else:
            name = stock_name_map.get(code, f"股票{code}")

    if not is_available_fn():
        return AnalysisResult(
            code=code,
            name=name,
            sentiment_score=50,
            trend_prediction="Sideways" if report_language == "en" else "震荡",
            operation_advice="Hold" if report_language == "en" else "持有",
            confidence_level="Low" if report_language == "en" else "低",
            analysis_summary="AI analysis is unavailable because no API key is configured." if report_language == "en" else "AI 分析功能未启用（未配置 API Key）",
            risk_warning="Configure an LLM API key (GEMINI_API_KEY/ANTHROPIC_API_KEY/OPENAI_API_KEY) and retry." if report_language == "en" else "请配置 LLM API Key（GEMINI_API_KEY/ANTHROPIC_API_KEY/OPENAI_API_KEY）后重试",
            success=False,
            error_message="LLM API key is not configured" if report_language == "en" else "LLM API Key 未配置",
            model_used=None,
            report_language=report_language,
        )

    try:
        prompt = format_prompt(context, name, news_context, report_language=report_language)

        config = get_runtime_config()
        model_name = config.litellm_model or "unknown"
        logger.info("========== AI 分析 %s(%s) ==========", name, code)
        logger.info("[LLM配置] 模型: %s", model_name)
        logger.info("[LLM配置] Prompt 长度: %s 字符", len(prompt))
        logger.info("[LLM配置] 是否包含新闻: %s", "是" if news_context else "否")

        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        logger.info("[LLM Prompt 预览]\n%s", prompt_preview)
        logger.debug("=== 完整 Prompt (%s字符) ===\n%s\n=== End Prompt ===", len(prompt), prompt)

        generation_config = {
            "temperature": config.llm_temperature,
            "max_output_tokens": 8192,
        }

        logger.info("[LLM调用] 开始调用 %s...", model_name)
        _emit_progress(68, f"{name}：LLM 已接收请求，等待响应")

        current_prompt = prompt
        retry_count = 0
        max_retries = config.report_integrity_retry if config.report_integrity_enabled else 0

        while True:
            start_time = time.time()
            response_text, model_used, llm_usage = call_litellm(
                current_prompt,
                generation_config,
                system_prompt=system_prompt,
                stream=True,
                stream_progress_callback=stream_progress_callback,
            )
            elapsed = time.time() - start_time

            logger.info("[LLM返回] %s 响应成功, 耗时 %.2fs, 响应长度 %s 字符", model_name, elapsed, len(response_text))
            response_preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
            logger.info("[LLM返回 预览]\n%s", response_preview)
            logger.debug(
                "=== %s 完整响应 (%s字符) ===\n%s\n=== End Response ===",
                model_name,
                len(response_text),
                response_text,
            )
            parse_progress = min(99, 93 + retry_count * 2)
            _emit_progress(parse_progress, f"{name}：LLM 返回完成，正在解析 JSON")

            result = parse_response(response_text, code, name)
            result.raw_response = response_text
            result.search_performed = bool(news_context)
            result.market_snapshot = build_market_snapshot(context)
            result.model_used = model_used
            result.report_language = report_language

            if not config.report_integrity_enabled:
                break
            pass_integrity, missing_fields = check_content_integrity(result)
            if pass_integrity:
                break
            if retry_count < max_retries:
                current_prompt = build_integrity_retry_prompt(
                    prompt,
                    response_text,
                    missing_fields,
                    report_language=report_language,
                )
                retry_count += 1
                logger.info(
                    "[LLM完整性] 必填字段缺失 %s，第 %d 次补全重试",
                    missing_fields,
                    retry_count,
                )
                retry_progress = min(99, 92 + retry_count * 2)
                _emit_progress(
                    retry_progress,
                    f"{name}：报告字段不完整，正在补全重试（{retry_count}/{max_retries}）",
                )
            else:
                apply_placeholder_fill(result, missing_fields)
                logger.warning("[LLM完整性] 必填字段缺失 %s，已占位补全，不阻塞流程", missing_fields)
                break

        persist_usage(llm_usage, model_used, call_type="analysis", stock_code=code)
        logger.info("[LLM解析] %s(%s) 分析完成: %s, 评分 %s", name, code, result.trend_prediction, result.sentiment_score)
        return result

    except Exception as exc:
        logger.error("AI 分析 %s(%s) 失败: %s", name, code, exc)
        return AnalysisResult(
            code=code,
            name=name,
            sentiment_score=50,
            trend_prediction="Sideways" if report_language == "en" else "震荡",
            operation_advice="Hold" if report_language == "en" else "持有",
            confidence_level="Low" if report_language == "en" else "低",
            analysis_summary=(f"Analysis failed: {str(exc)[:100]}" if report_language == "en" else f"分析过程出错: {str(exc)[:100]}"),
            risk_warning="Analysis failed. Please retry later or review manually." if report_language == "en" else "分析失败，请稍后重试或手动分析",
            success=False,
            error_message=str(exc),
            model_used=None,
            report_language=report_language,
        )
