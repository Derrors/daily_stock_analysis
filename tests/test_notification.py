# -*- coding: utf-8 -*-
"""
Regression tests for NotificationService after notification descope.
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
from src.notification import NotificationService
from src.enums import ReportType


def _make_config(**overrides) -> Config:
    return Config(stock_list=[], **overrides)


class TestNotificationServiceAfterDescope(unittest.TestCase):
    @mock.patch("src.notification.get_config")
    def test_service_is_unavailable_and_send_is_noop(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = NotificationService()

        self.assertFalse(service.is_available())
        self.assertEqual(service.get_available_channels(), [])
        self.assertEqual(service.get_channel_names(), "")
        self.assertFalse(service.send("test content"))

    @mock.patch("src.notification.get_config")
    def test_only_generic_send_entry_remains_noop(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = NotificationService()

        self.assertFalse(service.send_to_context("x"))
        self.assertFalse(service.send("x"))
        self.assertFalse(service._has_context_channel())

    @mock.patch("src.notification.get_config")
    def test_generate_aggregate_report_still_delegates_by_report_type(self, mock_get_config):
        mock_get_config.return_value = _make_config()
        service = NotificationService()

        with mock.patch.object(service, "generate_brief_report", return_value="brief-report") as brief_mock, \
             mock.patch.object(service, "generate_dashboard_report", return_value="dashboard-report") as dashboard_mock:
            self.assertEqual(service.generate_aggregate_report([], ReportType.BRIEF), "brief-report")
            self.assertEqual(service.generate_aggregate_report([], ReportType.SIMPLE), "dashboard-report")

        brief_mock.assert_called_once()
        dashboard_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
