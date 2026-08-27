#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "sql-runner.py"


def run_attempt_bytes(payload: bytes, timeout_ms: int = 1500) -> tuple[dict, int, str, float]:
    with tempfile.TemporaryDirectory() as temp_dir:
        attempt = Path(temp_dir) / "attempt.sql"
        attempt.write_bytes(payload)
        started = time.monotonic()
        completed = subprocess.run(
            [sys.executable, str(RUNNER), str(attempt), "--timeout-ms", str(timeout_ms)],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
        elapsed = time.monotonic() - started
    return json.loads(completed.stdout), len(completed.stdout.encode("utf-8")), completed.stdout, elapsed


def run_attempt(sql: str, timeout_ms: int = 1500) -> tuple[dict, int, str, float]:
    return run_attempt_bytes(sql.encode("utf-8"), timeout_ms=timeout_ms)


class SqlRunnerTests(unittest.TestCase):
    def test_success_returns_rows_and_required_outcome_fields(self):
        result, _, _, _ = run_attempt(
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
        result, _, _, _ = run_attempt("SELECT missing_column FROM missing_table;")
        self.assertEqual(result["status"], "runtime-error")
        self.assertEqual(result["runnerId"], "sql-session")
        self.assertTrue(result["recoverable"])
        self.assertIn("OperationalError", result["detail"])

    def test_timeout_interrupts_unbounded_recursive_query(self):
        result, _, _, _ = run_attempt(
            "WITH RECURSIVE cnt(x) AS ("
            "VALUES(0) UNION ALL SELECT x+1 FROM cnt"
            ") SELECT sum(x) FROM cnt;",
            timeout_ms=50,
        )
        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["runnerId"], "sql-session")
        self.assertTrue(result["recoverable"])

    def test_attach_is_denied_to_keep_session_in_memory(self):
        result, _, _, _ = run_attempt("ATTACH DATABASE '/tmp/not-allowed.db' AS disk;")
        self.assertEqual(result["status"], "runtime-error")
        self.assertIn("not authorized", result["detail"].lower())

    def test_load_extension_function_is_denied_without_optional_python_api(self):
        result, _, _, _ = run_attempt("SELECT load_extension('not-allowed');")
        self.assertEqual(result["status"], "runtime-error")
        self.assertTrue(result["recoverable"])
        self.assertTrue(
            "not authorized" in result["detail"].lower() or "no such function" in result["detail"].lower(),
            result["detail"],
        )

    def test_oversized_input_is_rejected_before_execution(self):
        result, output_bytes, _, _ = run_attempt("SELECT 1; --" + ("x" * 300_000))
        self.assertEqual(result["status"], "failed")
        self.assertIn("input budget", result["summary"].lower())
        self.assertLess(output_bytes, 10_000)

    def test_invalid_utf8_is_normalized_to_recoverable_json(self):
        result, _, _, _ = run_attempt_bytes(b"SELECT '\xff';")
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["recoverable"])
        self.assertIn("utf-8", result["summary"].lower())

    def test_semicolon_heavy_quoted_input_cannot_hold_parser_unbounded(self):
        result, _, _, elapsed = run_attempt("SELECT '" + (";" * 50_000) + "';", timeout_ms=50)
        self.assertIn(result["status"], {"passed", "timeout"})
        self.assertLess(elapsed, 1.0)

    def test_non_finite_float_is_normalized_to_strict_json_value(self):
        result, _, raw, _ = run_attempt("SELECT 1e999 AS value;")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["data"]["rows"], [[{"nonFiniteFloat": "Infinity"}]])
        self.assertIn('"nonFiniteFloat":"Infinity"', raw)

    def test_large_cell_is_truncated_before_serialization(self):
        result, output_bytes, _, _ = run_attempt("SELECT hex(zeroblob(10000)) AS payload;")
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["data"]["cellTruncated"])
        self.assertTrue(result["data"]["truncated"])
        self.assertEqual(result["data"]["truncationReason"], "cell-byte-budget")
        self.assertLessEqual(result["data"]["resultBytes"], 64 * 1024)
        self.assertLess(output_bytes, 80 * 1024)

    def test_large_rowset_stops_at_total_result_budget(self):
        result, output_bytes, _, _ = run_attempt(
            "WITH RECURSIVE cnt(x) AS ("
            "VALUES(1) UNION ALL SELECT x+1 FROM cnt WHERE x<100"
            ") SELECT hex(zeroblob(3000)) AS payload FROM cnt;"
        )
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["data"]["truncated"])
        self.assertEqual(result["data"]["truncationReason"], "result-byte-budget")
        self.assertLess(result["data"]["rowCount"], 100)
        self.assertLessEqual(result["data"]["resultBytes"], 64 * 1024)
        self.assertLess(output_bytes, 80 * 1024)


if __name__ == "__main__":
    unittest.main(verbosity=2)
