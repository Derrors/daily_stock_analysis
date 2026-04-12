# -*- coding: utf-8 -*-
"""
Compatibility tests for removed notification sender implementations.
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

for optional_module in ("litellm", "json_repair"):
    try:
        __import__(optional_module)
    except ModuleNotFoundError:
        sys.modules[optional_module] = mock.MagicMock()

from src.config import Config
from src.notification import NotificationService, NotificationChannel


def _make_config(**overrides) -> Config:
    return Config(stock_list=[], **overrides)


class TestNotificationCompatibilityStubs(unittest.TestCase):
    @mock.patch("src.notification.get_config")
    def test_image_and_channel_helpers_are_inert(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = NotificationService()

        self.assertFalse(service._should_use_image_for_channel(NotificationChannel.WECHAT, b"png"))
        self.assertFalse(service._send_wechat_image(b"png"))
        self.assertFalse(service._send_telegram_photo(b"png"))
        self.assertFalse(service._send_email_with_inline_image(b"png"))
        self.assertFalse(service._send_custom_webhook_image(b"png", fallback_content="x"))
        self.assertFalse(service._send_slack_image(b"png", fallback_content="x"))

    @mock.patch("src.notification.get_config")
    def test_detect_all_channels_returns_empty_list(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = NotificationService()

        self.assertEqual(service._detect_all_channels(), [])
        self.assertEqual(service.get_available_channels(), [])
        self.assertFalse(service.is_available())


if __name__ == "__main__":
    unittest.main()
