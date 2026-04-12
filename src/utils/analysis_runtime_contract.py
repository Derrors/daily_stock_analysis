# -*- coding: utf-8 -*-
"""Shared runtime and contract semantics for analysis scripts.

This module centralizes two things that must stay consistent across
script/tooling entrypoints:
1. full-analysis runtime preflight rules
2. requested-component completeness semantics
"""

from __future__ import annotations

import os
from typing import Any, Mapping, MutableMapping

FULL = "full"
PARTIAL = "partial"
MISSING = "missing"
NOT_REQUESTED = "not_requested"

PROVIDER_KEYS = (
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "AIHUBMIX_KEY",
    "DEEPSEEK_API_KEY",
    "ANTHROPIC_API_KEY",
)


def _env_mapping(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return env if env is not None else os.environ


def _split_csv_env(source: Mapping[str, str], key: str) -> list[str]:
    raw = (source.get(key, "") or "").strip()
    return [item.strip() for item in raw.split(",") if item.strip()]


def infer_litellm_model_from_env(env: Mapping[str, str] | None = None) -> str | None:
    source = _env_mapping(env)
    explicit = (source.get("LITELLM_MODEL", "") or "").strip()
    if explicit:
        return explicit

    gemini_keys = _split_csv_env(source, "GEMINI_API_KEYS")
    if not gemini_keys:
        single = (source.get("GEMINI_API_KEY", "") or "").strip()
        if single:
            gemini_keys = [single]

    anthropic_keys = _split_csv_env(source, "ANTHROPIC_API_KEYS")
    if not anthropic_keys:
        single = (source.get("ANTHROPIC_API_KEY", "") or "").strip()
        if single:
            anthropic_keys = [single]

    openai_keys = _split_csv_env(source, "OPENAI_API_KEYS")
    if not openai_keys:
        aihubmix = (source.get("AIHUBMIX_KEY", "") or "").strip()
        direct_openai = (source.get("OPENAI_API_KEY", "") or "").strip()
        if aihubmix:
            openai_keys = [aihubmix]
        elif direct_openai:
            openai_keys = [direct_openai]

    deepseek_key = (source.get("DEEPSEEK_API_KEY", "") or "").strip()

    if gemini_keys:
        return f"gemini/{(source.get('GEMINI_MODEL', 'gemini-3-flash-preview') or 'gemini-3-flash-preview').strip()}"
    if anthropic_keys:
        return f"anthropic/{(source.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022') or 'claude-3-5-sonnet-20241022').strip()}"
    if deepseek_key:
        return "deepseek/deepseek-chat"
    if openai_keys:
        openai_model = (source.get("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini").strip()
        return openai_model if "/" in openai_model else f"openai/{openai_model}"
    return None


def get_provider_key_presence(env: Mapping[str, str] | None = None) -> dict[str, bool]:
    source = _env_mapping(env)
    return {
        "GEMINI_API_KEY": bool(_split_csv_env(source, "GEMINI_API_KEYS") or (source.get("GEMINI_API_KEY", "") or "").strip()),
        "OPENAI_API_KEY": bool(_split_csv_env(source, "OPENAI_API_KEYS") or (source.get("OPENAI_API_KEY", "") or "").strip()),
        "AIHUBMIX_KEY": bool((source.get("AIHUBMIX_KEY", "") or "").strip()),
        "DEEPSEEK_API_KEY": bool((source.get("DEEPSEEK_API_KEY", "") or "").strip()),
        "ANTHROPIC_API_KEY": bool(_split_csv_env(source, "ANTHROPIC_API_KEYS") or (source.get("ANTHROPIC_API_KEY", "") or "").strip()),
    }


def evaluate_full_analysis_runtime(
    *,
    litellm_model: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    source = _env_mapping(env)
    inferred_model = infer_litellm_model_from_env(source)
    model_value = (litellm_model if litellm_model is not None else inferred_model or "").strip()
    provider_keys_present = get_provider_key_presence(source)
    has_provider_key = any(provider_keys_present.values())

    missing_requirements: list[str] = []
    if not model_value:
        missing_requirements.append("LITELLM_MODEL")
    if not has_provider_key:
        missing_requirements.append("provider_key")

    return {
        "litellm_model": bool(model_value),
        "litellm_model_value": model_value or None,
        "provider_key": has_provider_key,
        "provider_keys_present": provider_keys_present,
        "missing_requirements": missing_requirements,
        "available": not missing_requirements,
    }


def build_full_analysis_preflight_error(
    *,
    litellm_model: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any] | None:
    runtime = evaluate_full_analysis_runtime(litellm_model=litellm_model, env=env)
    if runtime["available"]:
        return None

    return {
        "error": "preflight_failed",
        "message": "full-analysis 运行条件不满足，已提前终止以避免无意义搜索链路。",
        "missing_requirements": runtime["missing_requirements"],
        "hint": (
            "请先配置 LITELLM_MODEL，并至少提供一个可用的 provider key "
            "（如 GEMINI_API_KEY / OPENAI_API_KEY / AIHUBMIX_KEY / DEEPSEEK_API_KEY / ANTHROPIC_API_KEY）。"
        ),
    }


def apply_component_completeness(
    payload: MutableMapping[str, Any],
    component: str,
    status: Any,
    *,
    error: str | None = None,
) -> None:
    evidence = payload.setdefault("evidence", {})
    completeness = evidence.setdefault("data_completeness", {})
    status_value = getattr(status, "value", status)
    completeness[component] = status_value

    metadata = payload.setdefault("metadata", {})
    metadata.setdefault("errors", [])
    metadata.setdefault("degraded", False)
    metadata.setdefault("partial", False)

    if status_value in (PARTIAL, MISSING):
        metadata["degraded"] = True
        metadata["partial"] = True

    if error and error not in metadata["errors"]:
        metadata["errors"].append(error)
