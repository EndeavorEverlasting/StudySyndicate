#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check-staged-artifacts.py"
HOOK = REPO_ROOT / ".githooks" / "pre-commit"
VALIDATION = REPO_ROOT / "harness" / "validation-manifest.v1.json"

REMEDIATION = (
    "Move live/generated evidence back to ignored local output, or commit a sanitized "
    "fixture under an approved fixture/docs path."
)


def run(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


class HookArtifactHygieneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.assertEqual(run("git", "init", "-q", cwd=self.repo).returncode, 0)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def stage(self, path: str, content: str = "fixture") -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        proc = run("git", "add", "-f", "--", path, cwd=self.repo)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def check(self) -> subprocess.CompletedProcess[str]:
        return run(sys.executable, str(CHECKER), cwd=self.repo)

    def test_blocks_generated_runtime_evidence_with_guidance(self) -> None:
        self.stage("local-study-exports/session-20260811-interview.json")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "[harness] refusing staged generated/runtime artifact: "
            "local-study-exports/session-20260811-interview.json",
            result.stderr,
        )
        self.assertIn(REMEDIATION, result.stderr)

    def test_blocks_crash_dump_and_local_tool_install(self) -> None:
        self.stage("crash-dumps/app.dmp")
        self.stage(".venv/pyvenv.cfg")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("crash-dumps/app.dmp", result.stderr)
        self.assertIn(".venv/pyvenv.cfg", result.stderr)

    def test_allows_sanitized_fixtures_and_normal_docs_code(self) -> None:
        self.stage("tests/fixtures/runtime.fixture.log", "sanitized log")
        self.stage("docs/interview-prep.md", "# prep")
        self.stage("src/example.ts", "export const value = 1;")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sensitive_content_is_never_printed(self) -> None:
        secret = "SUPER_SECRET_VALUE_SHOULD_NOT_APPEAR"
        self.stage(".env", f"TOKEN={secret}\n")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".env", result.stderr)
        self.assertNotIn(secret, result.stdout + result.stderr)

    def test_pre_commit_is_bounded_to_static_local_checks(self) -> None:
        active = [
            line.strip()
            for line in HOOK.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#") and line.strip() != "set -eu"
        ]
        self.assertEqual(
            active,
            [
                "python scripts/check-staged-artifacts.py",
                "python scripts/harness.py validate --level quick",
                "git diff --cached --check",
            ],
        )

        spec = json.loads(VALIDATION.read_text(encoding="utf-8"))
        forbidden = {
            "curl",
            "wget",
            "start-process",
            "invoke-webrequest",
            "xdg-open",
            "open",
            "vite",
            "playwright",
        }
        for check in spec["checks"]:
            if check["tier"] != "quick":
                continue
            rendered = " ".join(check["argv"]).lower()
            for token in forbidden:
                self.assertNotIn(
                    token,
                    rendered,
                    f"quick hook path contains forbidden runtime/network token: {rendered}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
