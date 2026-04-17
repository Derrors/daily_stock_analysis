# -*- coding: utf-8 -*-
"""Tests for agent model deployment source normalization."""

from types import SimpleNamespace

from src.services.agent_model_service import list_agent_model_deployments


def _make_config(*, llm_models_source: str) -> SimpleNamespace:
    return SimpleNamespace(
        llm_models_source=llm_models_source,
        llm_model_list=[
            {
                "model_name": "primary-deployment",
                "litellm_params": {"model": "openai/gpt-4o-mini"},
            }
        ],
        openai_base_url=None,
    )


def test_list_agent_model_deployments_normalizes_legacy_env_source_label(monkeypatch):
    config = _make_config(llm_models_source="legacy_env")

    monkeypatch.setattr(
        "src.services.agent_model_service.get_effective_agent_primary_model",
        lambda _config: "openai/gpt-4o-mini",
    )
    monkeypatch.setattr(
        "src.services.agent_model_service.get_effective_agent_models_to_try",
        lambda _config: ["openai/gpt-4o-mini"],
    )

    deployments = list_agent_model_deployments(config)

    assert len(deployments) == 1
    assert deployments[0]["source"] == "managed_env"
    assert deployments[0]["deployment_id"] == "managed_env:0"


def test_list_agent_model_deployments_falls_back_to_managed_env_for_unknown_source(monkeypatch):
    config = _make_config(llm_models_source="surprise_source")

    monkeypatch.setattr(
        "src.services.agent_model_service.get_effective_agent_primary_model",
        lambda _config: "openai/gpt-4o-mini",
    )
    monkeypatch.setattr(
        "src.services.agent_model_service.get_effective_agent_models_to_try",
        lambda _config: ["openai/gpt-4o-mini"],
    )

    deployments = list_agent_model_deployments(config)

    assert len(deployments) == 1
    assert deployments[0]["source"] == "managed_env"
    assert deployments[0]["deployment_id"] == "managed_env:0"
