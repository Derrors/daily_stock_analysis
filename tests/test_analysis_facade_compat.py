import sys
from unittest.mock import MagicMock, patch


def test_legacy_analyzer_import_path_still_works() -> None:
    # Analyzer depends on optional runtime deps; keep it importable in minimal env.
    if "litellm" not in sys.modules:
        sys.modules["litellm"] = MagicMock()

    from src.stock_analysis_skill.analysis.facade import StockAnalysisLLMAnalyzer as GeminiAnalyzer

    with patch.object(GeminiAnalyzer, "_init_litellm", return_value=None):
        analyzer = GeminiAnalyzer()

    assert analyzer is not None
