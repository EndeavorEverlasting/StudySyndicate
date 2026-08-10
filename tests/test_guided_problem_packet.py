#!/usr/bin/env python3
"""Behavior tests for self-contained guided problem packets and executable feedback."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEM_CLI = ROOT / "scripts" / "study-problem.py"
CONTRACT = ROOT / "harness" / "problems" / "problem-packet-contract.v1.json"
PACKET = ROOT / "harness" / "problems" / "two-sum.v1.json"


def run_problem(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(PROBLEM_CLI), *args], cwd=ROOT, text=True, capture_output=True)


class GuidedProblemPacketTests(unittest.TestCase):
    def test_packet_recites_assignment_before_questions(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["schema"], "study-syndicate/problem-packet-contract/v1")
        self.assertEqual(contract["requiredDisplayOrder"][0], "premise")
        self.assertEqual(contract["uiGate"]["status"], "foundation-ready")
        self.assertIn("renderer", contract["uiGate"]["rule"].lower())
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        self.assertEqual(packet["schema"], "study-syndicate/problem-packet/v1")
        self.assertEqual(packet["packetContract"], "study-syndicate/problem-packet-contract/v1")
        self.assertGreater(len(packet["premise"]), 80)
        self.assertIn("indices", packet["output"].lower())
        result = run_problem("render", "two-sum", "--mode", "guided")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(result.stdout.index("## Premise"), result.stdout.index("## Checkpoints"))
        self.assertLess(result.stdout.index("## Example"), result.stdout.index("## Checkpoints"))
        self.assertIn("Given a list of integers named nums", result.stdout)
        self.assertIn("nums = [2, 7, 11, 15]", result.stdout)
        self.assertIn("def two_sum(nums, target):", result.stdout)

    def test_comment_format_is_an_editable_self_contained_attempt(self):
        result = run_problem("render", "two-sum", "--mode", "guided", "--format", "comments")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Two Sum — guided problem packet", result.stdout)
        self.assertIn("# ## Premise", result.stdout)
        self.assertIn("YOUR RESPONSE:", result.stdout)
        self.assertIn("def two_sum(nums, target):", result.stdout)
        self.assertIn("raise NotImplementedError", result.stdout)
        self.assertNotIn("def two_sum_hash", result.stdout)
        self.assertNotIn("seen: dict", result.stdout)

    def test_hints_are_graduated_and_docs_are_official(self):
        first = run_problem("hint", "two-sum", "--level", "1")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertNotIn("lookup", first.stdout.lower())
        self.assertNotIn("target -", first.stdout.lower())
        fourth = run_problem("hint", "two-sum", "--level", "4")
        self.assertEqual(fourth.returncode, 0, fourth.stderr)
        self.assertIn("remember values seen earlier", fourth.stdout)
        docs = run_problem("docs", "two-sum")
        self.assertEqual(docs.returncode, 0, docs.stderr)
        self.assertIn("docs.python.org", docs.stdout)
        self.assertNotIn("Two Sum Python solution", docs.stdout)

    def test_checker_accepts_correct_slow_attempt_without_requiring_optimization(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp) / "attempt.py"
            attempt.write_text("def two_sum(nums, target):\n    for left in range(len(nums)):\n        for right in range(left + 1, len(nums)):\n            if nums[left] + nums[right] == target:\n                return [left, right]\n", encoding="utf-8")
            result = run_problem("check", "two-sum", str(attempt))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("attempt feedback PASS: 4 cases", result.stdout)
        self.assertIn("not yet mastery", result.stdout)

    def test_checker_returns_specific_failure_without_revealing_solution(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = Path(tmp) / "attempt.py"
            attempt.write_text("def two_sum(nums, target):\n    return [0, 0]\n", encoding="utf-8")
            result = run_problem("check", "two-sum", str(attempt))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("same index", result.stderr)
        self.assertNotIn("seen", result.stderr.lower())
        self.assertNotIn("hash", result.stderr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
