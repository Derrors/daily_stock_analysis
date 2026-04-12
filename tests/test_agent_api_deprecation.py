# -*- coding: utf-8 -*-
"""Regression tests for deprecated agent API endpoints."""

import tempfile
import unittest
from pathlib import Path

from tests.litellm_stub import ensure_litellm_stub

ensure_litellm_stub()

try:
    from fastapi.testclient import TestClient
    from api.app import create_app
except Exception:  # pragma: no cover - optional dependency environments
    TestClient = None
    create_app = None


class AgentApiDeprecationTestCase(unittest.TestCase):
    def test_chat_send_returns_gone_with_boundary_message(self) -> None:
        if TestClient is None or create_app is None:
            self.skipTest("FastAPI test client unavailable in this environment")

        with tempfile.TemporaryDirectory() as tmpdir:
            client = TestClient(create_app(static_dir=Path(tmpdir)))
            response = client.post(
                "/api/v1/agent/chat/send",
                json={"content": "hello", "title": "legacy"},
            )

        self.assertEqual(response.status_code, 410)
        body = response.json()
        self.assertIn("message", body)
        self.assertIn("通知发送能力已下线", body["message"])
        self.assertIn("仓库外部", body["message"])


if __name__ == "__main__":
    unittest.main()
