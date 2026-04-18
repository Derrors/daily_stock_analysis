from unittest.mock import patch

from src.stock_analysis_skill.providers.base import BaseFetcher


class DummyFetcher(BaseFetcher):
    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str):
        raise NotImplementedError()

    def _normalize_data(self, df, stock_code: str):
        return df


def test_base_fetcher_clean_data_delegates_to_helper() -> None:
    fetcher = DummyFetcher()
    marker = object()
    cleaned = object()

    with patch(
        "src.stock_analysis_skill.providers.base.clean_standard_ohlcv_dataframe",
        return_value=cleaned,
    ) as mock_helper:
        result = fetcher._clean_data(marker)

    assert result is cleaned
    mock_helper.assert_called_once()
    assert mock_helper.call_args.args[0] is marker
    assert "pd_module" in mock_helper.call_args.kwargs


def test_base_fetcher_calculate_indicators_delegates_to_helper() -> None:
    fetcher = DummyFetcher()
    marker = object()
    enriched = object()

    with patch(
        "src.stock_analysis_skill.providers.base.calculate_standard_technical_indicators",
        return_value=enriched,
    ) as mock_helper:
        result = fetcher._calculate_indicators(marker)

    assert result is enriched
    mock_helper.assert_called_once_with(marker)
