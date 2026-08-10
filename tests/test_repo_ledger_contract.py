#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "repo_ledger.py"
spec = importlib.util.spec_from_file_location("repo_ledger", MODULE)
repo_ledger = importlib.util.module_from_spec(spec)
sys.modules["repo_ledger"] = repo_ledger
assert spec.loader
spec.loader.exec_module(repo_ledger)

BASE = """# Queue

## SSQ-001 — Example
- **Status:** READY
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** unclaimed
- **Branch / PR:** none / none
- **Scope:** change one bounded thing
- **Forbidden:** unrelated work
- **Dependencies:** none
- **References:** none
- **Acceptance gate:** exact test passes
- **Gate:** none
- **Last proof:** artifact:docs/example.md
- **Next action:** create the bounded implementation and run its validator
- **Updated:** 2026-08-10T17:06:00-04:00
"""


class LedgerContractTests(unittest.TestCase):
    def errors(self, source: str) -> list[str]:
        return repo_ledger.validate_tasks(repo_ledger.parse_ledger_text(source))

    def test_current_ledger_passes(self):
        tasks = repo_ledger.parse_ledger(ROOT / ".ai" / "WORK_QUEUE.md")
        self.assertEqual([], repo_ledger.validate_tasks(tasks, ROOT))

    def test_duplicate_field_rejected(self):
        bad = BASE.replace("- **Priority:** P0", "- **Priority:** P0\n- **Priority:** P1")
        with self.assertRaises(repo_ledger.LedgerError):
            repo_ledger.parse_ledger_text(bad)

    def test_malformed_heading_rejected(self):
        bad = BASE.replace("## SSQ-001 — Example", "## SSQ-001 - Example")
        with self.assertRaises(repo_ledger.LedgerError):
            repo_ledger.parse_ledger_text(bad)

    def test_invalid_status_rejected(self):
        self.assertTrue(any("invalid Status" in e for e in self.errors(BASE.replace("READY", "WAITING", 1))))

    def test_invalid_priority_rejected(self):
        self.assertTrue(any("invalid Priority" in e for e in self.errors(BASE.replace("P0", "P9", 1))))

    def test_fake_claimed_owner_rejected(self):
        bad = BASE.replace("READY", "CLAIMED", 1).replace("unclaimed", "agent", 1)
        self.assertTrue(any("concrete owner" in e for e in self.errors(bad)))

    def test_vague_next_action_rejected(self):
        bad = BASE.replace("create the bounded implementation and run its validator", "wait for later")
        self.assertTrue(any("executable verb" in e for e in self.errors(bad)))

    def test_blocked_requires_exact_gate(self):
        bad = BASE.replace("READY", "BLOCKED", 1)
        self.assertTrue(any("exact non-placeholder Gate" in e for e in self.errors(bad)))

    def test_done_requires_durable_proof(self):
        bad = BASE.replace("READY", "DONE", 1).replace("artifact:docs/example.md", "tests passed").replace(
            "create the bounded implementation and run its validator", repo_ledger.TERMINAL_ACTION
        )
        self.assertTrue(any("durable proof" in e for e in self.errors(bad)))

    def test_done_requires_terminal_action(self):
        bad = BASE.replace("READY", "DONE", 1)
        self.assertTrue(any("DONE Next action" in e for e in self.errors(bad)))

    def test_unbounded_monolithic_claim_rejected(self):
        bad = BASE.replace("READY", "CLAIMED", 1).replace("BOUNDED", "UNBOUNDED", 1).replace("unclaimed", "session-123", 1)
        self.assertTrue(any("UNBOUNDED may not" in e for e in self.errors(bad)))

    def test_ready_unbounded_requires_bounded_children(self):
        bad = BASE.replace("BOUNDED", "UNBOUNDED", 1).replace(
            "create the bounded implementation and run its validator", "inspect the parent scope and keep planning"
        )
        self.assertTrue(any("bounded child work" in e for e in self.errors(bad)))

    def test_stale_local_reference_rejected(self):
        bad = BASE.replace("- **References:** none", "- **References:** `docs/DOES_NOT_EXIST.md`")
        tasks = repo_ledger.parse_ledger_text(bad)
        errors = repo_ledger.validate_tasks(tasks, ROOT)
        self.assertTrue(any("stale local reference" in e for e in errors))

    def test_duplicate_task_id_rejected(self):
        bad = BASE + "\n" + BASE.split("# Queue\n", 1)[1]
        with self.assertRaises(repo_ledger.LedgerError):
            repo_ledger.parse_ledger_text(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
