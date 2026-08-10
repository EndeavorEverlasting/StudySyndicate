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


def block(task_id: str, priority: str, work_class: str, status: str = "READY", next_action: str | None = None) -> str:
    if next_action is None:
        next_action = (
            "create two bounded child tasks before implementation"
            if work_class == "UNBOUNDED"
            else "create the bounded implementation and run its validator"
        )
    owner = "unclaimed" if status == "READY" else "session-123"
    gate = "exact external dependency missing" if status in {"BLOCKED", "OPERATOR"} else "none"
    return f"""## {task_id} — Task {task_id}
- **Status:** {status}
- **Priority:** {priority}
- **Work class:** {work_class}
- **Owner:** {owner}
- **Branch / PR:** none / none
- **Scope:** bounded scope
- **Forbidden:** unrelated work
- **Dependencies:** none
- **References:** none
- **Acceptance gate:** validator passes
- **Gate:** {gate}
- **Last proof:** artifact:docs/example.md
- **Next action:** {next_action}
- **Updated:** 2026-08-10T17:06:00-04:00
"""


class FrontierTests(unittest.TestCase):
    def parse(self, *blocks: str):
        return repo_ledger.parse_ledger_text("# Queue\n\n" + "\n".join(blocks))

    def test_highest_priority_selected(self):
        tasks = self.parse(block("SSQ-001", "P2", "BOUNDED"), block("SSQ-002", "P0", "BOUNDED"))
        self.assertEqual("SSQ-002", repo_ledger.select_frontier(tasks).id)

    def test_same_priority_preserves_ledger_order(self):
        tasks = self.parse(block("SSQ-001", "P1", "BOUNDED"), block("SSQ-002", "P1", "BOUNDED"))
        self.assertEqual("SSQ-001", repo_ledger.select_frontier(tasks).id)

    def test_bounded_ready_routes_execute(self):
        task = self.parse(block("SSQ-001", "P0", "BOUNDED"))[0]
        self.assertEqual("EXECUTE", repo_ledger.derive_route(task))

    def test_unbounded_ready_routes_decompose(self):
        task = self.parse(block("SSQ-001", "P0", "UNBOUNDED"))[0]
        self.assertEqual("DECOMPOSE", repo_ledger.derive_route(task))

    def test_blocked_not_selected(self):
        tasks = self.parse(
            block("SSQ-001", "P0", "BOUNDED", "BLOCKED", "resolve the exact external dependency"),
            block("SSQ-002", "P1", "BOUNDED"),
        )
        self.assertEqual("SSQ-002", repo_ledger.select_frontier(tasks).id)

    def test_prompt_is_self_contained_and_anti_rumination(self):
        task = self.parse(block("SSQ-001", "P0", "BOUNDED"))[0]
        prompt = repo_ledger.render_prompt(task)
        self.assertIn("EXECUTE THIS BOUNDED SPRINT", prompt)
        self.assertIn("SCOPE:", prompt)
        self.assertIn("FORBIDDEN:", prompt)
        self.assertIn("ACCEPTANCE GATE:", prompt)
        self.assertIn("FIRST ACTION:", prompt)
        self.assertIn("STOP RULE:", prompt)

    def test_empty_frontier(self):
        done = block("SSQ-001", "P0", "BOUNDED", "DONE", repo_ledger.TERMINAL_ACTION)
        tasks = self.parse(done)
        self.assertIsNone(repo_ledger.select_frontier(tasks))


if __name__ == "__main__":
    unittest.main(verbosity=2)
