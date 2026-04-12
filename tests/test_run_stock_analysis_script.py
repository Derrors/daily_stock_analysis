from argparse import Namespace
from types import SimpleNamespace

from scripts.run_stock_analysis import _build_request_from_args, _preflight_request, _resolve_report_type
from src.schemas.analysis_contract import AnalysisMode, AnalysisRequest, OutputFormat


def test_build_request_from_args_defaults() -> None:
    args = Namespace(
        input_json=None,
        stock="600519",
        stock_name="贵州茅台",
        market="cn",
        mode="standard",
        strategy=None,
        output_format="dashboard",
        verbosity="standard",
        language="zh",
        original_query="茅台",
        selection_source="manual",
        force_refresh=False,
        dry_run=False,
        no_save_history=False,
        include_news=True,
        include_fundamental=False,
        include_market_context=False,
        include_realtime_quote=True,
        include_chip_data=False,
        pretty=False,
    )

    request = _build_request_from_args(args)

    assert request.stock.input == "600519"
    assert request.stock.name == "贵州茅台"
    assert request.mode == AnalysisMode.STANDARD
    assert request.output.format == OutputFormat.DASHBOARD
    assert request.execution.async_mode is False
    assert request.execution.save_history is True


def test_resolve_report_type_mapping() -> None:
    args = Namespace(
        input_json=None,
        stock="AAPL",
        stock_name=None,
        market="us",
        mode="deep",
        strategy=None,
        output_format="dashboard",
        verbosity="detailed",
        language="en",
        original_query=None,
        selection_source="manual",
        force_refresh=True,
        dry_run=False,
        no_save_history=True,
        include_news=True,
        include_fundamental=True,
        include_market_context=True,
        include_realtime_quote=True,
        include_chip_data=False,
        pretty=False,
    )

    request = _build_request_from_args(args)

    assert _resolve_report_type(request) == "full"


def test_preflight_requires_provider_key(monkeypatch) -> None:
    monkeypatch.setattr("scripts.run_stock_analysis.get_config", lambda: SimpleNamespace(litellm_model="gemini/test"))
    for key in ["GEMINI_API_KEY", "OPENAI_API_KEY", "AIHUBMIX_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"]:
        monkeypatch.delenv(key, raising=False)

    payload = _preflight_request(AnalysisRequest.minimal("600519"))

    assert payload is not None
    assert payload["error"] == "preflight_failed"
    assert "provider_key" in payload["missing_requirements"]


def test_preflight_passes_with_model_and_provider_key(monkeypatch) -> None:
    monkeypatch.setattr("scripts.run_stock_analysis.get_config", lambda: SimpleNamespace(litellm_model="gemini/test"))
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    payload = _preflight_request(AnalysisRequest.minimal("600519"))

    assert payload is None
