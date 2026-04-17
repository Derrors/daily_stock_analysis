# -*- coding: utf-8 -*-
"""Minimal doctor for the skill-first rewrite."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_config  # noqa: E402
from src.stock_analysis_skill.contracts import AnalysisRequest  # noqa: E402
from src.stock_analysis_skill.service import StockAnalysisSkillService  # noqa: E402


def main() -> int:
    config = get_config()
    payload = {
        "ok": True,
        "checks": {
            "contracts_import": True,
            "service_import": True,
            "sample_request": AnalysisRequest.minimal("600519").model_dump(mode="json"),
            "tushare_token_configured": bool(getattr(config, "tushare_token", None)),
            "litellm_model": getattr(config, "litellm_model", None),
            "llm_key_present": any(
                bool(os.getenv(name))
                for name in [
                    "GEMINI_API_KEY",
                    "OPENAI_API_KEY",
                    "AIHUBMIX_KEY",
                    "DEEPSEEK_API_KEY",
                    "ANTHROPIC_API_KEY",
                ]
            ),
            "service_class": StockAnalysisSkillService.__name__,
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
