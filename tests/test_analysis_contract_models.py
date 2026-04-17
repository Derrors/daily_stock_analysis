from src.schemas.analysis_contract import (
    AnalysisMode,
    AnalysisRequest,
    AnalysisResponse,
    DataCompleteness,
    DecisionAction,
    EvidenceBlock,
    Market,
    OutputFormat,
    QuerySource,
    SelectionSource,
    TrendBlock,
    TrendStatus,
)


def test_analysis_request_minimal_defaults() -> None:
    req = AnalysisRequest.minimal("600519")

    assert req.stock.input == "600519"
    assert req.mode == AnalysisMode.STANDARD
    assert req.features.include_news is True
    assert req.output.format == OutputFormat.DASHBOARD
    assert req.execution.async_mode is False
    assert req.context.query_source == QuerySource.UNKNOWN
    assert req.context.selection_source == SelectionSource.MANUAL


def test_analysis_request_async_alias_roundtrip() -> None:
    req = AnalysisRequest.model_validate(
        {
            "stock": {"input": "AAPL", "market": "us"},
            "execution": {"async": True, "force_refresh": True},
        }
    )

    dumped = req.model_dump(by_alias=True)

    assert req.execution.async_mode is True
    assert dumped["execution"]["async"] is True
    assert dumped["execution"]["force_refresh"] is True


def test_analysis_response_minimal_factory() -> None:
    resp = AnalysisResponse.minimal(
        code="600519",
        market=Market.CN,
        action=DecisionAction.WAIT,
        summary="当前数据不足，建议观望",
        degraded=True,
        partial=True,
        errors=["news_search_unavailable"],
    )

    assert resp.stock.code == "600519"
    assert resp.decision.action == DecisionAction.WAIT
    assert resp.metadata.degraded is True
    assert resp.metadata.partial is True
    assert resp.metadata.errors == ["news_search_unavailable"]


def test_analysis_response_supports_evidence_completeness_enum() -> None:
    resp = AnalysisResponse.minimal(
        code="NVDA",
        market=Market.US,
        action=DecisionAction.BUY,
        summary="趋势偏强",
    )
    resp.trend = TrendBlock(
        status=TrendStatus.BULL,
        signal=DecisionAction.BUY,
        score=82,
        summary="均线多头，趋势偏强",
    )
    resp.evidence = EvidenceBlock(
        providers={"daily": ["yfinance"]},
        used_features=["trend_analysis"],
        data_completeness={"trend": DataCompleteness.FULL},
    )

    validated = AnalysisResponse.model_validate(resp.model_dump())

    assert validated.evidence is not None
    assert validated.evidence.data_completeness["trend"] == DataCompleteness.FULL
