# -*- coding: utf-8 -*-
"""LiteLLM router/runtime helpers for analyzer core."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Set, Tuple

import litellm
from litellm import Router

from src.config import Config, get_managed_api_keys_for_model, get_managed_litellm_params


logger = logging.getLogger(__name__)


def has_channel_config(config: Config) -> bool:
    """Check if multi-channel config (channels / YAML / non-placeholder model_list) is active."""
    return bool(config.llm_model_list) and not all(
        entry.get("model_name", "").startswith("__managed_env_")
        for entry in config.llm_model_list
    )


def init_analyzer_litellm(config: Config) -> Tuple[Optional[Any], bool]:
    """Initialize analyzer router/runtime state and return ``(router, available)``."""
    litellm_model = config.litellm_model
    if not litellm_model:
        logger.warning("Analyzer LLM: LITELLM_MODEL not configured")
        return None, False

    if has_channel_config(config):
        model_list = config.llm_model_list
        router = Router(
            model_list=model_list,
            routing_strategy="simple-shuffle",
            num_retries=2,
        )
        unique_models = list(dict.fromkeys(
            entry["litellm_params"]["model"] for entry in model_list
        ))
        logger.info(
            "Analyzer LLM: Router initialized from channels/YAML — %s deployment(s), models: %s",
            len(model_list),
            unique_models,
        )
        return router, True

    keys = get_managed_api_keys_for_model(litellm_model, config)
    if len(keys) > 1:
        extra_params = get_managed_litellm_params(litellm_model, config)
        env_managed_model_list = [
            {
                "model_name": litellm_model,
                "litellm_params": {
                    "model": litellm_model,
                    "api_key": key,
                    **extra_params,
                },
            }
            for key in keys
        ]
        router = Router(
            model_list=env_managed_model_list,
            routing_strategy="simple-shuffle",
            num_retries=2,
        )
        logger.info(
            "Analyzer LLM: Env-managed Router initialized with %s keys for %s",
            len(keys),
            litellm_model,
        )
        return router, True

    if keys:
        logger.info("Analyzer LLM: litellm initialized (model=%s)", litellm_model)
    else:
        logger.info(
            "Analyzer LLM: litellm initialized (model=%s, API key from environment)",
            litellm_model,
        )
    return None, True


def dispatch_litellm_completion(
    model: str,
    call_kwargs: Dict[str, Any],
    *,
    config: Config,
    router: Optional[Any],
    use_channel_router: bool,
    router_model_names: Set[str],
) -> Any:
    """Dispatch a LiteLLM completion through router or direct fallback."""
    effective_kwargs = dict(call_kwargs)
    if use_channel_router and router and model in router_model_names:
        return router.completion(**effective_kwargs)
    if router and model == config.litellm_model and not use_channel_router:
        return router.completion(**effective_kwargs)

    keys = get_managed_api_keys_for_model(model, config)
    if keys:
        effective_kwargs["api_key"] = keys[0]
    effective_kwargs.update(get_managed_litellm_params(model, config))
    return litellm.completion(**effective_kwargs)
