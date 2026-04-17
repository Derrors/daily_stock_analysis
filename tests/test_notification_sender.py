# -*- coding: utf-8 -*-
"""
Compatibility tests for the reduced ReportOutputService surface after notification descope.
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
from src.notification import ReportOutputService


def _make_config(**overrides) -> Config:
    return Config(stock_list=[], **overrides)


class TestNotificationCompatibilityStubs(unittest.TestCase):
    @mock.patch("src.notification.get_config")
    def test_detect_all_channels_returns_empty_list(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = ReportOutputService()

        self.assertEqual(service._detect_all_channels(), [])
        self.assertEqual(service.get_available_channels(), [])
        self.assertFalse(service.is_available())

    @mock.patch("src.notification.get_config")
    def test_legacy_channel_specific_methods_are_gone(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = ReportOutputService()

        for attr in (
            "send_to_wechat",
            "send_to_feishu",
            "send_to_telegram",
            "send_to_email",
            "send_to_pushover",
            "send_to_pushplus",
            "send_to_serverchan3",
            "send_to_custom",
            "send_to_discord",
            "send_to_slack",
            "send_to_astrbot",
            "_should_use_image_for_channel",
            "_send_wechat_image",
            "_send_telegram_photo",
            "_send_email_with_inline_image",
            "_send_custom_webhook_image",
            "_send_slack_image",
        ):
            self.assertFalse(hasattr(service, attr), attr)


if __name__ == "__main__":
    unittest.main()
