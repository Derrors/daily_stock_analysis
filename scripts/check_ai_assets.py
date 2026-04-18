#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TRAE_SKILLS_DIR = ROOT / ".trae" / "skills"

REQUIRED_SKILL_FILES = {
    "stock-analysis/SKILL.md",
}

REQUIRED_GITIGNORE_SNIPPETS = (
    ".trae/*",
    "!.trae/skills/",
    "!.trae/skills/**",
)


def fail(message: str) -> None:
    print(f"[ai-assets] ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def ensure_file_exists(path: Path, description: str) -> None:
    if not path.exists():
        fail(f"{description} is missing: {path.relative_to(ROOT)}")


def ensure_skill_files() -> None:
    ensure_file_exists(TRAE_SKILLS_DIR, "Trae skills directory")
    actual_skill_dirs = {
        path.name for path in TRAE_SKILLS_DIR.iterdir() if path.is_dir()
    }
    if actual_skill_dirs != {"stock-analysis"}:
        fail(
            "unexpected Trae skills present: "
            f"{', '.join(sorted(actual_skill_dirs - {'stock-analysis'})) or 'none'}"
        )
    for relative_path in REQUIRED_SKILL_FILES:
        trae_path = TRAE_SKILLS_DIR / relative_path
        if not trae_path.exists():
            fail(f"missing repository skill asset: {trae_path.relative_to(ROOT)}")
        if trae_path.is_file():
            content = trae_path.read_text(encoding="utf-8")
            if "Invoke when" not in content:
                fail(
                    f"{trae_path.relative_to(ROOT)} must describe when the skill should be used"
                )


def ensure_gitignore_rules() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for snippet in REQUIRED_GITIGNORE_SNIPPETS:
        if snippet not in gitignore:
            fail(f".gitignore is missing required AI asset rule: {snippet}")


def ensure_no_tracked_workspace_artifacts() -> None:
    checked_dirs = (".trae",)
    allowed_prefixes = (".trae/skills/",)
    for directory in checked_dirs:
        result = subprocess.run(
            ["git", "ls-files", "--", directory],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        tracked = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        for path in tracked:
            if path.startswith(allowed_prefixes):
                continue
            fail(f"tracked workspace artifact outside skills/: {path}")


def main() -> None:
    ensure_skill_files()
    ensure_gitignore_rules()
    ensure_no_tracked_workspace_artifacts()
    print("[ai-assets] OK")


if __name__ == "__main__":
    main()
