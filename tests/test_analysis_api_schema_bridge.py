from api.v1.schemas.analysis import AnalyzeRequest, AnalysisResultResponse
from src.schemas.analysis_contract import DecisionAction, Market, QuerySource


def test_analyze_request_to_contract_request() -> None:
    request = AnalyzeRequest(
        stock_code="600519",
        report_type="brief",
        force_refresh=True,
        async_mode=True,
        stock_name="贵州茅台",
        original_query="茅台",
        selection_source="autocomplete",
    )

    contract = request.to_contract_request(
        stock_input="600519",
        stock_code="600519",
        market="cn",
        query_source=QuerySource.API,
    )

    assert contract.stock.input == "600519"
    assert contract.stock.code == "600519"
    assert contract.stock.market == Market.CN
    assert contract.mode.value == "quick"
    assert contract.execution.async_mode is True
    assert contract.execution.force_refresh is True
    assert contract.output.format.value == "summary"
    assert contract.context.original_query == "茅台"
    assert contract.context.selection_source.value == "autocomplete"


def test_analyze_request_to_batch_contract() -> None:
    request = AnalyzeRequest(
        stock_codes=["600519", "AAPL"],
        report_type="detailed",
        async_mode=True,
    )

    batch = request.to_batch_contract(stock_inputs=["600519", "AAPL"], query_source=QuerySource.API)

    assert len(batch.batch) == 2
    assert batch.execution.async_mode is True
    assert batch.shared.mode.value == "standard"
    assert batch.shared.output.format.value == "dashboard"



def test_analysis_result_response_from_unified_roundtrip() -> None:
    unified = AnalysisResultResponse.from_unified(
        AnalysisResultResponse(
            query_id="legacy-1",
            stock_code="600519",
            stock_name="贵州茅台",
            report={
                "decision": {
                    "action": "wait",
                    "summary": "先观望",
                    "confidence": "medium",
                },
                "metadata": {
                    "request_id": "legacy-1",
                    "generated_at": "2026-04-11T23:00:00+08:00",
                    "degraded": False,
                    "partial": True,
                    "errors": [],
                    "query_source": "api",
                },
            },
            created_at="2026-04-11T23:00:00+08:00",
        ).to_unified(market="cn"),
        query_id="legacy-1",
        created_at="2026-04-11T23:00:00+08:00",
    )

    assert unified.stock_code == "600519"
    assert unified.report["decision"]["action"] == DecisionAction.WAIT.value
    assert unified.report["metadata"]["query_source"] == QuerySource.API.value
