# -*- coding: utf-8 -*-
"""Focused tests for EventMonitor / alert rule integration."""

import asyncio
import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from unittest.mock import MagicMock as _MagicMock
    sys.modules["litellm"] = _MagicMock()


class TestEventMonitor(unittest.TestCase):
    """Test EventMonitor serialize/deserialize round-trip."""

    def test_round_trip(self):
        from src.agent.events import EventMonitor, PriceAlert, VolumeAlert
        monitor = EventMonitor()
        monitor.add_alert(PriceAlert(stock_code="600519", direction="above", price=1800.0))
        monitor.add_alert(VolumeAlert(stock_code="000858", multiplier=3.0))

        data = monitor.to_dict_list()
        self.assertEqual(len(data), 2)

        restored = EventMonitor.from_dict_list(data)
        self.assertEqual(len(restored.rules), 2)
        self.assertEqual(restored.rules[0].stock_code, "600519")
        self.assertEqual(restored.rules[1].stock_code, "000858")

    def test_remove_expired(self):
        import time
        from src.agent.events import EventMonitor, PriceAlert
        monitor = EventMonitor()
        alert = PriceAlert(stock_code="600519", direction="above", price=1800.0, ttl_hours=0.0)
        alert.created_at = time.time() - 3600
        monitor.rules.append(alert)
        removed = monitor.remove_expired()
        self.assertEqual(removed, 1)
        self.assertEqual(len(monitor.rules), 0)

    def test_add_alert_rejects_unsupported_rule_type(self):
        from src.agent.events import EventMonitor, SentimentAlert

        monitor = EventMonitor()
        with self.assertRaises(ValueError):
            monitor.add_alert(SentimentAlert(stock_code="600519"))


class TestEventMonitorAsync(unittest.IsolatedAsyncioTestCase):
    """Test async EventMonitor checks offload blocking fetches."""

    async def test_check_price_uses_to_thread_and_triggers(self):
        from src.agent.events import EventMonitor, PriceAlert

        monitor = EventMonitor()
        rule = PriceAlert(stock_code="600519", direction="above", price=1800.0)
        quote = SimpleNamespace(price=1810.0)

        with patch("src.agent.events.asyncio.to_thread", new=AsyncMock(return_value=quote)) as to_thread:
            triggered = await monitor._check_price(rule)

        self.assertIsNotNone(triggered)
        self.assertEqual(triggered.rule.stock_code, "600519")
        to_thread.assert_awaited_once()

    async def test_check_volume_safe_when_fetch_returns_none(self):
        from src.agent.events import EventMonitor, VolumeAlert

        monitor = EventMonitor()
        rule = VolumeAlert(stock_code="600519", multiplier=2.0)

        with patch("src.agent.events.asyncio.to_thread", new=AsyncMock(return_value=None)):
            result = await monitor._check_volume(rule)

        self.assertIsNone(result)

    async def test_check_all_async_callback(self):
        from src.agent.events import EventMonitor, PriceAlert

        monitor = EventMonitor()
        rule = PriceAlert(stock_code="600519", direction="above", price=1800.0)
        monitor.add_alert(rule)

        callback_values = []
        async_cb = AsyncMock(side_effect=lambda alert: callback_values.append(alert.rule.stock_code))
        monitor.on_trigger(async_cb)

        quote = SimpleNamespace(price=1810.0)
        with patch("src.agent.events.asyncio.to_thread", new=AsyncMock(return_value=quote)):
            triggered = await monitor.check_all()

        self.assertEqual(len(triggered), 1)
        async_cb.assert_awaited_once()


class TestEventMonitorConfigIntegration(unittest.TestCase):
    """Test config-driven EventMonitor construction."""

    def test_build_event_monitor_from_config(self):
        from src.agent.events import build_event_monitor_from_config

        config = SimpleNamespace(
            agent_event_monitor_enabled=True,
            agent_event_alert_rules_json='[{"stock_code":"600519","alert_type":"price_cross","direction":"above","price":1800}]',
        )

        with patch("src.notification.NotificationService", return_value=MagicMock()):
            monitor = build_event_monitor_from_config(config=config)

        self.assertIsNotNone(monitor)
        self.assertEqual(len(monitor.rules), 1)
        self.assertEqual(monitor.rules[0].stock_code, "600519")

    def test_build_event_monitor_returns_none_on_invalid_json(self):
        from src.agent.events import build_event_monitor_from_config

        config = SimpleNamespace(
            agent_event_monitor_enabled=True,
            agent_event_alert_rules_json='[invalid',
        )

        monitor = build_event_monitor_from_config(config=config)
        self.assertIsNone(monitor)

    def test_build_event_monitor_skips_invalid_rule_entries(self):
        from src.agent.events import build_event_monitor_from_config

        config = SimpleNamespace(
            agent_event_monitor_enabled=True,
            agent_event_alert_rules_json=(
                '[{"stock_code":"600519","alert_type":"price_cross","direction":"above","price":1800},'
                '{"stock_code":"000858","alert_type":"price_cross","status":"bad","direction":"above","price":120}]'
            ),
        )

        with patch("src.notification.NotificationService", return_value=MagicMock()):
            monitor = build_event_monitor_from_config(config=config)

        self.assertIsNotNone(monitor)
        self.assertEqual(len(monitor.rules), 1)
        self.assertEqual(monitor.rules[0].stock_code, "600519")

    def test_build_event_monitor_skips_unsupported_rule_types(self):
        from src.agent.events import build_event_monitor_from_config

        config = SimpleNamespace(
            agent_event_monitor_enabled=True,
            agent_event_alert_rules_json=(
                '[{"stock_code":"600519","alert_type":"sentiment_shift"},'
                '{"stock_code":"000858","alert_type":"price_cross","direction":"above","price":120}]'
            ),
        )

        with patch("src.notification.NotificationService", return_value=MagicMock()):
            monitor = build_event_monitor_from_config(config=config)

        self.assertIsNotNone(monitor)
        self.assertEqual(len(monitor.rules), 1)
        self.assertEqual(monitor.rules[0].stock_code, "000858")


if __name__ == "__main__":
    unittest.main()
