import json

from scripts import build_analysis_context as module


class _FakeContextService:
    def build_context(self, request, *, days=60):
        return {
            "request": request.model_dump(mode="json", by_alias=True),
            "stock": {"code": request.stock.code, "name": "贵州茅台", "market": "cn"},
            "trend": {"signal": "bull"},
            "realtime": None,
            "chip": None,
            "intel": None,
            "market_context": None,
            "evidence": {"providers": {}, "used_features": [], "data_completeness": {}},
            "metadata": {"mode": request.mode.value, "query_source": request.context.query_source.value, "degraded": False, "partial": False, "errors": []},
            "days": days,
        }


def test_script_delegates_to_context_service(monkeypatch, capsys):
    monkeypatch.setattr(module, "AnalysisContextService", lambda: _FakeContextService())
    monkeypatch.setattr(module.sys, "argv", ["build_analysis_context.py", "--stock", "600519", "--days", "90"])

    rc = module.main()
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert payload["stock"]["code"] == "600519"
    assert payload["days"] == 90
    assert payload["trend"]["signal"] == "bull"


def test_script_dry_run_still_returns_normalized_request(monkeypatch, capsys):
    monkeypatch.setattr(module.sys, "argv", ["build_analysis_context.py", "--stock", "600519", "--dry-run"])

    rc = module.main()
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert payload["stock"]["code"] == "600519"
    assert payload["mode"] == "context_only"
