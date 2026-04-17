# -*- coding: utf-8 -*-
"""Compatibility re-export for the unified analysis contract.

Canonical path:
- `src.stock_analysis_skill.contracts`

Keep this module during migration so legacy imports do not break while the
repository is being rewritten toward a skill-first shape.
"""

from src.stock_analysis_skill.contracts import *  # noqa: F401,F403
