#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "sql-runner.py"


def run_attempt(sql: str, timeout_ms: int = 1500) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        attempt = Path(temp_dir) / "attempt.sql"
        attempt.write_text(sql, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(RUNNER), str(attempt), "--timeout-ms", str(timeout_ms)],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    return json.loads(completed.stdout)


class SqlRunnerTests(unittest.TestCase):
    def test_success_returns_rows_and_required_outcome_fields(self):
        result = run_attempt(
            "CREATE TABLE t(x INTEGER); "
            "INSERT INTO t VALUES (2),(1); "
            "SELECT x FROM t ORDER BY x;"
        )
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["runnerId"], "sql-session")
        self.assertTrue(result["recoverable"])
        self.assertEqual(result["data"]["columns"], ["x"])
        self.assertEqual(result["data"]["rows"], [[1], [2]])

    def test_guest_sql_error_normalizes_to_runtime_error(self):
        result = run_attempt("SELECT missing_column FROM missing_table;")
        self.assertEqual(result["status"], "runtime-error")
        self.assertEqual(result["runnerId"], "sql-session")
        self.assertTrue(result["recoverable"])
        self.assertIn("OperationalError", result["detail"])

    def test_timeout_interrupts_unbounded_recursive_query(self):
        result = run_attempt(
            "WITH RECURSIVE cnt(x) AS ("
            "VALUES(0) UNION ALL SELECT x+1 FROM cnt"
            ") SELECT sum(x) FROM cnt;",
            timeout_ms=50,
        )
        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["runnerId"], "sql-session")
        self.assertTrue(result["recoverable"])

    def test_attach_is_denied_to_keep_session_in_memory(self):
        result = run_attempt("ATTACH DATABASE '/tmp/not-allowed.db' AS disk;")
        self.assertEqual(result["status"], "runtime-error")
        self.assertIn("not authorized", result["detail"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
