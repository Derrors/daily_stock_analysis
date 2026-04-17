# -*- coding: utf-8 -*-
"""Tests for config_registry after skill-runtime config minimization."""
import unittest

from src.core.config_registry import build_schema_response, get_field_definition


class TestRegistryAfterSkillRuntimeMinimization(unittest.TestCase):
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

    def test_notification_category_is_removed(self):
        schema = build_schema_response()
        categories = {c["category"] for c in schema["categories"]}
        self.assertNotIn("notification", categories)

    def test_removed_legacy_fields_fall_back_to_inferred_metadata(self):
        for key in (
            "PYTDX_HOST",
            "PYTDX_PORT",
            "PYTDX_SERVERS",
            "BACKTEST_ENABLED",
            "BACKTEST_EVAL_WINDOW_DAYS",
        ):
            field = get_field_definition(key)
            self.assertEqual(field.get("display_order"), 9000)


if __name__ == "__main__":
    unittest.main()
