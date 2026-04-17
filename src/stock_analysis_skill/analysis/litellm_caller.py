# -*- coding: utf-8 -*-
"""LiteLLM call/fallback orchestration for analyzer core."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Tuple

from src.agent.llm_adapter import get_thinking_extra_body
from src.config import Config, get_configured_llm_models
from .litellm_streaming import LiteLLMStreamError


logger = logging.getLogger(__name__)


def call_litellm(
    prompt: str,
    generation_config: dict,
    *,
    config: Config,
    text_system_prompt: str,
    dispatch_completion: Callable[..., Any],
    consume_stream: Callable[..., Tuple[str, Dict[str, Any]]],
    normalize_usage: Callable[[Any], Dict[str, Any]],
    has_channel_config_fn: Callable[[Config], bool],
    system_prompt: Optional[str] = None,
    stream: bool = False,
    stream_progress_callback: Optional[Callable[[int], None]] = None,
) -> Tuple[str, str, Dict[str, Any]]:
    """Call LiteLLM with configured model fallback and stream/non-stream fallback."""
    max_tokens = (
        generation_config.get("max_output_tokens")
        or generation_config.get("max_tokens")
        or 8192
    )
    temperature = generation_config.get("temperature", 0.7)

    models_to_try = [config.litellm_model] + (config.litellm_fallback_models or [])
    models_to_try = [model for model in models_to_try if model]

    use_channel_router = has_channel_config_fn(config)
    last_error = None
    effective_system_prompt = system_prompt or text_system_prompt
    router_model_names = set(get_configured_llm_models(config.llm_model_list))

    for model in models_to_try:
        try:
            model_short = model.split("/")[-1] if "/" in model else model
            call_kwargs: Dict[str, Any] = {
                "model": model,
                "messages": [
                    {"role": "system", "content": effective_system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            extra = get_thinking_extra_body(model_short)
            if extra:
                call_kwargs["extra_body"] = extra

            if stream:
                try:
                    stream_response = dispatch_completion(
                        model,
                        {**call_kwargs, "stream": True},
                        config=config,
                        use_channel_router=use_channel_router,
                        router_model_names=router_model_names,
                    )
                    response_text, usage = consume_stream(
                        stream_response,
                        model=model,
                        progress_callback=stream_progress_callback,
                    )
                    return response_text, model, usage
                except LiteLLMStreamError as exc:
                    if exc.partial_received:
                        logger.warning(
                            "[LiteLLM] %s stream failed after partial output, retrying non-stream for same model: %s",
                            model,
                            exc,
                        )
                    else:
                        logger.warning(
                            "[LiteLLM] %s stream unavailable before first chunk, falling back to non-stream: %s",
                            model,
                            exc,
                        )
                    last_error = exc
                except Exception as exc:
                    logger.warning(
                        "[LiteLLM] %s stream request failed before first chunk, falling back to non-stream: %s",
                        model,
                        exc,
                    )

            response = dispatch_completion(
                model,
                call_kwargs,
                config=config,
                use_channel_router=use_channel_router,
                router_model_names=router_model_names,
            )

            if response and response.choices and response.choices[0].message.content:
                usage = normalize_usage(getattr(response, "usage", None))
                return response.choices[0].message.content, model, usage
            raise ValueError("LLM returned empty response")

        except Exception as exc:
            logger.warning("[LiteLLM] %s failed: %s", model, exc)
            last_error = exc
            continue

    raise Exception(
        f"All LLM models failed (tried {len(models_to_try)} model(s)). Last error: {last_error}"
    )
