# -*- coding: utf-8 -*-
"""Tests for backward-compatible config env aliases and skill runtime config loading."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.config import Config, setup_env


class ConfigEnvCompatibilityTestCase(unittest.TestCase):
    def tearDown(self):
        Config.reset_instance()

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_load_from_env_keeps_tushare_only_runtime_priority(
        self, _mock_parse_litellm_yaml, _mock_setup_env
    ):
        with patch.dict(
            os.environ,
            {
                "STOCK_LIST": "600519",
            },
            clear=True,
        ):
            config = Config._load_from_env()

        self.assertEqual(
            config.realtime_source_priority,
            "tushare",
        )

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_realtime_source_priority_warns_and_normalizes_to_tushare(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "REALTIME_SOURCE_PRIORITY": "tencent,akshare_sina",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs("src.config", level="WARNING") as captured:
                config = Config._load_from_env()

        self.assertEqual(config.realtime_source_priority, "tushare")
        self.assertTrue(any("REALTIME_SOURCE_PRIORITY" in message for message in captured.output))

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_schedule_run_immediately_falls_back_to_legacy_run_immediately(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "RUN_IMMEDIATELY": "false",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertFalse(config.schedule_run_immediately)
        self.assertFalse(config.run_immediately)

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_schedule_run_immediately_prefers_schedule_specific_setting(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "RUN_IMMEDIATELY": "false",
            "SCHEDULE_RUN_IMMEDIATELY": "true",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertTrue(config.schedule_run_immediately)
        self.assertFalse(config.run_immediately)

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_empty_legacy_run_immediately_stays_false_when_schedule_alias_is_unset(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "RUN_IMMEDIATELY": "",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertFalse(config.schedule_run_immediately)
        self.assertFalse(config.run_immediately)

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_empty_schedule_run_immediately_stays_false_without_falling_back(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "RUN_IMMEDIATELY": "true",
            "SCHEDULE_RUN_IMMEDIATELY": "",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertFalse(config.schedule_run_immediately)
        self.assertTrue(config.run_immediately)

    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_blank_schedule_time_falls_back_to_default(
        self,
        _mock_parse_yaml,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "STOCK_LIST=600519",
                        "SCHEDULE_TIME=",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "ENV_FILE": str(env_path),
                },
                clear=True,
            ):
                config = Config._load_from_env()

        self.assertEqual(config.schedule_time, "18:00")

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_report_language_prefers_preexisting_process_env_over_env_file(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("REPORT_LANGUAGE=zh\n", encoding="utf-8")

            with patch.dict(
                os.environ,
                {
                    "ENV_FILE": str(env_path),
                    "REPORT_LANGUAGE": "en",
                },
                clear=True,
            ):
                config = Config._load_from_env()

        self.assertEqual(config.report_language, "en")

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_report_language_uses_env_file_when_process_env_is_absent(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("REPORT_LANGUAGE=en\n", encoding="utf-8")

            with patch.dict(
                os.environ,
                {
                    "ENV_FILE": str(env_path),
                },
                clear=True,
            ):
                config = Config._load_from_env()

        self.assertEqual(config.report_language, "en")

    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_runtime_mutable_keys_reload_from_updated_env_file_after_runtime_refresh(
        self,
        _mock_parse_yaml,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "STOCK_LIST=600519",
                        "SCHEDULE_ENABLED=false",
                        "SCHEDULE_TIME=18:00",
                        "RUN_IMMEDIATELY=true",
                        "SCHEDULE_RUN_IMMEDIATELY=false",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "ENV_FILE": str(env_path),
                    "STOCK_LIST": "600519",
                    "SCHEDULE_ENABLED": "false",
                    "SCHEDULE_TIME": "18:00",
                    "RUN_IMMEDIATELY": "true",
                    "SCHEDULE_RUN_IMMEDIATELY": "false",
                },
                clear=True,
            ):
                Config._load_from_env()
                env_path.write_text(
                    "\n".join(
                        [
                            "STOCK_LIST=300750,TSLA",
                            "SCHEDULE_ENABLED=true",
                            "SCHEDULE_TIME=09:30",
                            "RUN_IMMEDIATELY=false",
                            "SCHEDULE_RUN_IMMEDIATELY=true",
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )
                Config.reset_instance()
                setup_env(override=True)
                config = Config._load_from_env()

        self.assertEqual(config.stock_list, ["300750", "TSLA"])
        self.assertTrue(config.schedule_enabled)
        self.assertEqual(config.schedule_time, "09:30")
        self.assertFalse(config.run_immediately)
        self.assertTrue(config.schedule_run_immediately)

    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_runtime_mutable_keys_prefer_process_env_when_values_differ(
        self,
        _mock_parse_yaml,
    ) -> None:
        """When process env explicitly sets a runtime-priority key to a value
        that differs from .env, the process env must win because
        ``_capture_bootstrap_runtime_env_overrides`` runs before dotenv loads
        and the mismatch proves an intentional override.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "STOCK_LIST=300750,TSLA",
                        "SCHEDULE_ENABLED=true",
                        "SCHEDULE_TIME=09:30",
                        "RUN_IMMEDIATELY=false",
                        "SCHEDULE_RUN_IMMEDIATELY=true",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "ENV_FILE": str(env_path),
                    "STOCK_LIST": "600519,000001",
                    "SCHEDULE_ENABLED": "false",
                    "SCHEDULE_TIME": "18:00",
                    "RUN_IMMEDIATELY": "true",
                    "SCHEDULE_RUN_IMMEDIATELY": "false",
                },
                clear=True,
            ):
                config = Config._load_from_env()

        # Explicit process env overrides win when values differ from .env
        self.assertEqual(config.stock_list, ["600519", "000001"])
        self.assertFalse(config.schedule_enabled)
        self.assertEqual(config.schedule_time, "18:00")
        self.assertTrue(config.run_immediately)
        self.assertFalse(config.schedule_run_immediately)

    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_runtime_mutable_keys_use_process_env_when_absent_from_file(
        self,
        _mock_parse_yaml,
    ) -> None:
        """When a runtime-priority key exists only in process env (not in .env),
        it IS a genuine explicit override and must be honoured.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            # .env has no STOCK_LIST or SCHEDULE_* keys at all
            env_path.write_text("LOG_LEVEL=INFO\n", encoding="utf-8")

            with patch.dict(
                os.environ,
                {
                    "ENV_FILE": str(env_path),
                    "STOCK_LIST": "600519,000001",
                },
                clear=True,
            ):
                config = Config._load_from_env()

        self.assertEqual(config.stock_list, ["600519", "000001"])

    def test_parse_report_language_accepts_known_alias_without_warning(self) -> None:
        with self.assertNoLogs("src.config", level="WARNING"):
            parsed = Config._parse_report_language("zh-cn")

        self.assertEqual(parsed, "zh")

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_invalid_numeric_env_values_fall_back_to_defaults(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "AGENT_ORCHESTRATOR_TIMEOUT_S": "oops",
            "NEWS_MAX_AGE_DAYS": "bad",
            "MAX_WORKERS": "",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertEqual(config.agent_orchestrator_timeout_s, 600)
        self.assertEqual(config.news_max_age_days, 3)
        self.assertEqual(config.max_workers, 3)

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_legacy_stock_group_env_is_ignored_by_skill_runtime(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "STOCK_LIST": "600519,300750",
            "STOCK_GROUP_1": "600519",
            "EMAIL_GROUP_1": "user@example.com",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertFalse(hasattr(config, "stock_email_groups"))

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_agent_skill_autoweight_warns_that_flag_is_currently_no_op(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "AGENT_SKILL_AUTOWEIGHT": "false",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs("src.config", level="WARNING") as captured:
                config = Config._load_from_env()

        self.assertFalse(config.agent_skill_autoweight)
        self.assertTrue(any("currently a no-op" in message for message in captured.output))

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_agent_strategy_dir_warns_and_is_ignored(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "AGENT_STRATEGY_DIR": "./strategies",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs("src.config", level="WARNING") as captured:
                config = Config._load_from_env()

        self.assertIsNone(config.agent_skill_dir)
        self.assertTrue(any("AGENT_STRATEGY_DIR is retired and ignored" in message for message in captured.output))

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_legacy_agent_strategy_autoweight_warns_and_is_ignored(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "AGENT_STRATEGY_AUTOWEIGHT": "false",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs("src.config", level="WARNING") as captured:
                config = Config._load_from_env()

        self.assertTrue(config.agent_skill_autoweight)
        self.assertTrue(any("AGENT_STRATEGY_AUTOWEIGHT is retired and ignored" in message for message in captured.output))

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_gemini_model_fallback_warns_and_is_ignored_for_runtime_resolution(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "GEMINI_API_KEY": "test-key",
            "GEMINI_MODEL_FALLBACK": "gemini-2.0-flash-exp",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs("src.config", level="WARNING") as captured:
                config = Config._load_from_env()

        self.assertEqual(config.gemini_model_fallback, "gemini-2.5-flash")
        self.assertEqual(config.litellm_fallback_models, ["gemini/gemini-2.5-flash"])
        self.assertTrue(any("GEMINI_MODEL_FALLBACK is retired and ignored" in message for message in captured.output))

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_openai_api_keys_take_priority_over_aihubmix_and_single_openai_key(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "OPENAI_API_KEYS": "key-a,key-b",
            "AIHUBMIX_KEY": "aihubmix-key",
            "OPENAI_API_KEY": "openai-key",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertEqual(config.openai_api_keys, ["key-a", "key-b"])
        self.assertEqual(config.openai_api_key, "key-a")
        self.assertIsNone(config.openai_base_url)

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_aihubmix_key_sets_default_openai_compatible_base_url_when_no_override(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "AIHUBMIX_KEY": "aihubmix-key",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertEqual(config.openai_api_keys, ["aihubmix-key"])
        self.assertEqual(config.openai_api_key, "aihubmix-key")
        self.assertEqual(config.openai_base_url, "https://aihubmix.com/v1")

    @patch("src.config.setup_env")
    @patch.object(Config, "_parse_litellm_yaml", return_value=[])
    def test_explicit_openai_base_url_overrides_aihubmix_default_base_url(
        self,
        _mock_parse_yaml,
        _mock_setup_env,
    ) -> None:
        env = {
            "AIHUBMIX_KEY": "aihubmix-key",
            "OPENAI_BASE_URL": "https://proxy.example.com/v1",
        }

        with patch.dict(os.environ, env, clear=True):
            config = Config._load_from_env()

        self.assertEqual(config.openai_api_keys, ["aihubmix-key"])
        self.assertEqual(config.openai_api_key, "aihubmix-key")
        self.assertEqual(config.openai_base_url, "https://proxy.example.com/v1")


if __name__ == "__main__":
    unittest.main()
