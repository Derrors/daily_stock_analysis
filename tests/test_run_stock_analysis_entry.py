# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_stock_analysis.py"
DOCTOR_PATH = PROJECT_ROOT / "scripts" / "doctor.py"


def test_run_stock_analysis_dry_run() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--stock", "600519", "--dry-run"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["stock"]["input"] == "600519"
    assert payload["mode"] == "standard"


def test_doctor_script_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, str(DOCTOR_PATH)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["checks"]["contracts_import"] is True
    assert payload["checks"]["service_import"] is True
