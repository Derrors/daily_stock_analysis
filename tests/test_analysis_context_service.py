from src.schemas.analysis_contract import AnalysisRequest
from src.services.analysis_context_service import AnalysisContextService


class _FakeTrendResult:
    def to_dict(self):
        return {"signal": "bull"}


class _FakeTrendAnalyzer:
    def analyze(self, df, stock_code):
        return _FakeTrendResult()


class _FakeFetcher:
    def get_stock_name(self, stock_code, allow_realtime=False):
        return "贵州茅台"

    def get_daily_data(self, stock_code, days=60):
        return object(), "AkshareFetcher"

    def get_realtime_quote(self, stock_code, log_final_failure=False):
        return {"source": "tencent", "price": 1453.96}

    def get_chip_distribution(self, stock_code):
        return None


class _FakeSearchFailure:
    query = "贵州茅台 600519 股票 最新消息"
    provider = "None"
    success = False
    error_message = "所有搜索引擎都不可用或搜索失败"
    results = []


class _FakeSearchService:
    def search_stock_news(self, stock_code, stock_name, max_results=5):
        return _FakeSearchFailure()


def test_context_service_marks_news_failure_as_partial() -> None:
    service = AnalysisContextService(
        fetcher=_FakeFetcher(),
        trend_analyzer=_FakeTrendAnalyzer(),
        search_service=_FakeSearchService(),
    )

    payload = service.build_context(AnalysisRequest.minimal("600519"))

    assert payload["evidence"]["data_completeness"]["trend"] == "full"
    assert payload["evidence"]["data_completeness"]["realtime"] == "full"
    assert payload["evidence"]["data_completeness"]["intel"] == "partial"
    assert payload["metadata"]["degraded"] is True
    assert payload["metadata"]["partial"] is True
    assert "news_unavailable: 所有搜索引擎都不可用或搜索失败" in payload["metadata"]["errors"]


def test_context_service_marks_market_context_placeholder_as_partial() -> None:
    request = AnalysisRequest.minimal("600519")
    request.features.include_news = False
    request.features.include_market_context = True

    service = AnalysisContextService(
        fetcher=_FakeFetcher(),
        trend_analyzer=_FakeTrendAnalyzer(),
        search_service=None,
    )

    payload = service.build_context(request)

    assert payload["evidence"]["data_completeness"]["market_context"] == "partial"
    assert payload["metadata"]["degraded"] is True
    assert payload["metadata"]["partial"] is True
    assert "market_context_partial: hook not implemented yet" in payload["metadata"]["errors"]
