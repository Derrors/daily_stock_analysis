# -*- coding: utf-8 -*-
"""Tests for config_registry after notification descope."""
import unittest

from src.core.config_registry import build_schema_response, get_field_definition


class TestRegistryAfterNotificationDescope(unittest.TestCase):
    def test_notification_fields_are_not_registered(self):
        for key in (
            "WECHAT_WEBHOOK_URL",
            "FEISHU_WEBHOOK_URL",
            "TELEGRAM_BOT_TOKEN",
            "EMAIL_SENDER",
            "DISCORD_WEBHOOK_URL",
            "SLACK_BOT_TOKEN",
            "PUSHPLUS_TOKEN",
            "SERVERCHAN3_SENDKEY",
            "CUSTOM_WEBHOOK_URLS",
            "SINGLE_STOCK_NOTIFY",
            "MERGE_EMAIL_NOTIFICATION",
        ):
            field = get_field_definition(key)
            self.assertNotEqual(field.get("category"), "notification")
            self.assertEqual(field.get("display_order"), 9000)

    def test_report_related_fields_remain_registered(self):
        for key in (
            "REPORT_TYPE",
            "REPORT_LANGUAGE",
            "REPORT_SUMMARY_ONLY",
            "REPORT_TEMPLATES_DIR",
            "REPORT_RENDERER_ENABLED",
            "REPORT_INTEGRITY_ENABLED",
        ):
            field = get_field_definition(key)
            self.assertEqual(field.get("category"), "system")
            self.assertNotEqual(field.get("display_order"), 9000)

    def test_notification_category_has_no_channel_fields(self):
        schema = build_schema_response()
        notification_cat = next((c for c in schema["categories"] if c["category"] == "notification"), None)
        if notification_cat is None:
            self.assertIsNone(notification_cat)
            return
        field_keys = {f["key"] for f in notification_cat["fields"]}
        self.assertTrue(
            field_keys.isdisjoint(
                {
                    "WECHAT_WEBHOOK_URL",
                    "FEISHU_WEBHOOK_URL",
                    "TELEGRAM_BOT_TOKEN",
                    "EMAIL_SENDER",
                    "DISCORD_WEBHOOK_URL",
                    "SLACK_BOT_TOKEN",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
