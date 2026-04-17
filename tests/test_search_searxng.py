# -*- coding: utf-8 -*-
"""Compatibility tests for the retired SearXNG search provider."""

import sys
import unittest
from unittest.mock import MagicMock

# Mock newspaper before search_service import (optional dependency)
if "newspaper" not in sys.modules:
    mock_np = MagicMock()
    mock_np.Article = MagicMock()
    mock_np.Config = MagicMock()
    sys.modules["newspaper"] = mock_np

from src.search_service import SearchService


class TestRetiredSearXNGCompatibility(unittest.TestCase):
    def test_search_service_does_not_add_public_searxng_provider_after_runtime_descope(self):
        with self.assertLogs("src.search_service", level="WARNING") as captured:
            service = SearchService(searxng_public_instances_enabled=True)

        self.assertFalse(service.is_available)
        self.assertFalse(any(provider.name == "SearXNG" for provider in service._providers))
        self.assertTrue(any("已下线搜索源配置" in message for message in captured.output))

    def test_search_service_warns_for_legacy_search_provider_config_without_adding_runtime_providers(self):
        with self.assertLogs("src.search_service", level="WARNING") as captured:
            service = SearchService(
                anspire_keys=["legacy-anspire-key"],
                minimax_keys=["legacy-minimax-key"],
                searxng_base_urls=["https://searx.example.org"],
                searxng_public_instances_enabled=True,
            )

        self.assertFalse(service.is_available)
        self.assertEqual(service._providers, [])
        self.assertTrue(any("Anspire/MiniMax/SearXNG" in message for message in captured.output))


if __name__ == "__main__":
    unittest.main()
