# -*- coding: utf-8 -*-
"""Tests that skill-loading exceptions emit warning logs instead of being silently swallowed."""

import logging
import unittest
from unittest.mock import patch

try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    from tests.litellm_stub import ensure_litellm_stub

    ensure_litellm_stub()

from src.agent.skills.aggregator import SkillAggregator
from src.agent.skills.router import SkillRouter


class SkillRouterWarningTests(unittest.TestCase):
    """SkillRouter methods must log on failure."""

    def test_get_available_skills_logs_warning(self) -> None:
        with patch("src.agent.factory.get_skill_manager", side_effect=RuntimeError("no manager")):
            with patch("src.agent.factory._SKILL_MANAGER_PROTOTYPE", None):
                with self.assertLogs("src.agent.skills.router", level=logging.WARNING) as cm:
                    result = SkillRouter._get_available_skills()
        self.assertEqual(result, [])
        self.assertTrue(any("Failed to get available skills" in line for line in cm.output))

    def test_get_routing_mode_logs_warning(self) -> None:
        with patch("src.config.get_config", side_effect=RuntimeError("no config")):
            with self.assertLogs("src.agent.skills.router", level=logging.WARNING) as cm:
                result = SkillRouter._get_routing_mode()
        self.assertEqual(result, "auto")
        self.assertTrue(any("Failed to get routing mode" in line for line in cm.output))

    def test_get_manual_skills_logs_warning(self) -> None:
        with patch("src.config.get_config", side_effect=RuntimeError("cfg error")):
            with patch.object(SkillRouter, "_get_available_skills", return_value=[]):
                with self.assertLogs("src.agent.skills.router", level=logging.WARNING) as cm:
                    result = SkillRouter._get_manual_skills(max_count=3)
        self.assertIsInstance(result, list)
        self.assertTrue(any("Failed to get manual skills config" in line for line in cm.output))


if __name__ == "__main__":
    unittest.main()
