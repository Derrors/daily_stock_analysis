#!/usr/bin/env bash

set -euo pipefail

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PY="$PYTHON_BIN"
elif [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "No python interpreter found. Set PYTHON_BIN or create .venv." >&2
  exit 1
fi

echo "==> legacy-import-window: using interpreter: $PY"

DSA_WARN_LEGACY_IMPORTS=1 "$PY" -m pytest \
  tests/test_data_provider_compat_bridge.py \
  tests/test_no_internal_data_provider_imports.py \
  tests/test_us_index_mapping.py

echo "==> legacy-import-window: checks passed"
