#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "Invoke-StudySyndicateSqlFieldProof.ps1"


class SqlFieldProofContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_single_entrypoint_exists(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertIn("FIELD_PROOF=PASS", self.source)
        self.assertIn("PROVIDER_FIELD_PROOF=PASS", self.source)

    def test_preserves_dirty_or_non_main_checkout(self):
        self.assertIn("status --porcelain=v1", self.source)
        self.assertIn("worktree add --detach", self.source)
        self.assertIn("ISOLATED_PRESERVE", self.source)
        self.assertNotIn("reset --hard", self.source)
        self.assertNotIn("pull --force", self.source)

    def test_exact_target_and_required_sql_integration_are_proved(self):
        self.assertIn("merge-base --is-ancestor", self.source)
        self.assertIn("62872f9f442582b076e79f94d046fe4d4792126d", self.source)
        self.assertIn("Proof checkout moved from exact target", self.source)

    def test_owning_validation_and_live_sql_are_required(self):
        for required in (
            "scripts/validate-practice-workbench.py",
            "tests/test_sql_runner.py",
            "harness/practice-workbench.v1.json",
            "scripts/sql-runner.py",
            "SELECT 1 AS field_proof;",
        ):
            self.assertIn(required, self.source)

    def test_provider_mode_cannot_masquerade_as_operator_proof(self):
        self.assertIn("ProviderValidation", self.source)
        self.assertIn("reserved for GitHub Actions", self.source)
        self.assertIn("windows-desktop-dev", self.source)
        self.assertIn("PROVIDER_EXACT_HEAD", self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
