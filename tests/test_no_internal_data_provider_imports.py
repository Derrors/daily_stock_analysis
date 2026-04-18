# -*- coding: utf-8 -*-
"""Guardrail: internal code must use canonical provider import paths."""

from pathlib import Path

LEGACY_TOKENS = ("from data_provider", "import data_provider")
ALLOWED_FILES = {
    Path("tests/test_data_provider_compat_bridge.py"),
    Path("tests/test_no_internal_data_provider_imports.py"),
}
SCAN_ROOTS = (Path("src"), Path("scripts"), Path("tests"))


def test_internal_code_does_not_use_legacy_data_provider_imports() -> None:
    repo = Path(__file__).resolve().parents[1]
    offenders: list[str] = []

    for root in SCAN_ROOTS:
        for py in (repo / root).rglob("*.py"):
            rel = py.relative_to(repo)
            if rel in ALLOWED_FILES:
                continue

            text = py.read_text(encoding="utf-8")
            for token in LEGACY_TOKENS:
                if token in text:
                    offenders.append(str(rel))
                    break

    assert not offenders, (
        "Found internal legacy imports. Use canonical path "
        "src.stock_analysis_skill.providers.* instead:\n"
        + "\n".join(sorted(offenders))
    )
