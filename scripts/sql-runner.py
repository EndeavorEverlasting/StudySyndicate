#!/usr/bin/env python3
"""Execute one learner-authored SQL script in a bounded in-memory SQLite session."""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

RUNNER_ID = "sql-session"
DEFAULT_TIMEOUT_MS = 1500
MIN_TIMEOUT_MS = 50
MAX_TIMEOUT_MS = 10000
MAX_INPUT_BYTES = 256 * 1024
MAX_ROWS = 200
MAX_COLUMNS = 128
MAX_CELL_BYTES = 8 * 1024
MAX_RESULT_BYTES = 64 * 1024
MAX_SQLITE_VALUE_BYTES = 64 * 1024
MAX_DETAIL_CHARS = 8000


def outcome(status: str, summary: str, detail: str, *, data: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "runnerId": RUNNER_ID,
        "summary": summary,
        "detail": detail[:MAX_DETAIL_CHARS],
        "recoverable": True,
    }
    if data is not None:
        payload["data"] = data
    return payload


def split_statements(script: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    for char in script:
        buffer.append(char)
        if char == ";":
            candidate = "".join(buffer)
            if sqlite3.complete_statement(candidate):
                if candidate.strip():
                    statements.append(candidate.strip())
                buffer = []
    tail = "".join(buffer).strip()
    if tail:
        statements.append(tail)
    return statements


def bounded_text(value: str, max_bytes: int = MAX_CELL_BYTES) -> tuple[str, bool]:
    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value, False
    clipped = encoded[:max_bytes].decode("utf-8", errors="ignore")
    return f"{clipped}…", True


def bounded_json_value(value: Any) -> tuple[Any, bool]:
    if value is None or isinstance(value, (int, float)):
        return value, False
    if isinstance(value, str):
        return bounded_text(value)
    if isinstance(value, bytes):
        max_blob_bytes = max(1, MAX_CELL_BYTES // 2)
        clipped = value[:max_blob_bytes]
        truncated = len(value) > len(clipped)
        payload: dict[str, Any] = {"blobHex": clipped.hex()}
        if truncated:
            payload["truncated"] = True
            payload["originalBytes"] = len(value)
        return payload, truncated
    return bounded_text(str(value))


def install_authorizer(connection: sqlite3.Connection) -> None:
    denied = {
        code
        for code in (
            getattr(sqlite3, "SQLITE_ATTACH", None),
            getattr(sqlite3, "SQLITE_DETACH", None),
            getattr(sqlite3, "SQLITE_PRAGMA", None),
        )
        if code is not None
    }

    def authorize(
        action_code: int,
        _arg1: str | None,
        _arg2: str | None,
        _db: str | None,
        _trigger: str | None,
    ) -> int:
        return sqlite3.SQLITE_DENY if action_code in denied else sqlite3.SQLITE_OK

    connection.set_authorizer(authorize)


def timeout_outcome(timeout_ms: int, phase: str) -> dict[str, Any]:
    return outcome(
        "timeout",
        "SQL execution exceeded the runner time limit.",
        f"Interrupted after {timeout_ms} ms during {phase}. Reduce the attempt or inspect accidental unbounded work.",
    )


def execute_sql(script: str, timeout_ms: int) -> dict[str, Any]:
    timeout_ms = max(MIN_TIMEOUT_MS, min(MAX_TIMEOUT_MS, timeout_ms))
    deadline = time.monotonic() + (timeout_ms / 1000.0)
    timed_out = False

    connection = sqlite3.connect(":memory:", isolation_level=None)
    connection.enable_load_extension(False)
    if hasattr(connection, "setlimit"):
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_SQLITE_VALUE_BYTES)
        connection.setlimit(sqlite3.SQLITE_LIMIT_COLUMN, MAX_COLUMNS)
    install_authorizer(connection)

    def interrupt_expired_query() -> int:
        nonlocal timed_out
        if time.monotonic() >= deadline:
            timed_out = True
            return 1
        return 0

    connection.set_progress_handler(interrupt_expired_query, 1000)

    statements = split_statements(script)
    if time.monotonic() >= deadline:
        connection.close()
        return timeout_outcome(timeout_ms, "input parsing")
    if not statements:
        connection.close()
        return outcome("failed", "No SQL statement was provided.", "Write at least one SQL statement and try again.")

    last_columns: list[str] = []
    last_rows: list[list[Any]] = []
    result_bytes = 0
    truncated = False
    cell_truncated = False
    truncation_reason: str | None = None

    try:
        for statement in statements:
            cursor = connection.execute(statement)
            if cursor.description is None:
                continue

            last_columns = []
            for description in cursor.description[:MAX_COLUMNS]:
                column, column_was_truncated = bounded_text(str(description[0]))
                last_columns.append(column)
                cell_truncated = cell_truncated or column_was_truncated
            if len(cursor.description) > MAX_COLUMNS:
                truncated = True
                truncation_reason = "column-limit"

            result_bytes = len(json.dumps(last_columns, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
            if result_bytes > MAX_RESULT_BYTES:
                return outcome(
                    "failed",
                    "SQL result metadata exceeded the runner output budget.",
                    f"Column metadata exceeded the {MAX_RESULT_BYTES}-byte result budget.",
                )

            last_rows = []
            for row_index, row in enumerate(cursor):
                if row_index >= MAX_ROWS:
                    truncated = True
                    truncation_reason = truncation_reason or "row-limit"
                    break

                bounded_row: list[Any] = []
                for value in row[:MAX_COLUMNS]:
                    encoded_value, value_was_truncated = bounded_json_value(value)
                    bounded_row.append(encoded_value)
                    cell_truncated = cell_truncated or value_was_truncated

                row_bytes = len(json.dumps(bounded_row, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
                if result_bytes + row_bytes > MAX_RESULT_BYTES:
                    truncated = True
                    truncation_reason = "result-byte-budget"
                    break
                last_rows.append(bounded_row)
                result_bytes += row_bytes

            if cell_truncated:
                truncated = True
                truncation_reason = truncation_reason or "cell-byte-budget"
    except sqlite3.Error as exc:
        if timed_out or "interrupted" in str(exc).lower():
            return timeout_outcome(timeout_ms, "SQLite execution")
        return outcome(
            "runtime-error",
            "SQLite rejected the learner SQL, but the host runner remained available.",
            f"{type(exc).__name__}: {exc}",
        )
    except Exception as exc:  # defensive host boundary
        return outcome(
            "host-error",
            "The SQL runner failed outside the guest SQLite error boundary.",
            f"{type(exc).__name__}: {exc}",
        )
    finally:
        connection.close()

    data = {
        "statementCount": len(statements),
        "columns": last_columns,
        "rows": last_rows,
        "rowCount": len(last_rows),
        "truncated": truncated,
        "truncationReason": truncation_reason,
        "cellTruncated": cell_truncated,
        "resultBytes": result_bytes,
        "database": "sqlite-memory",
    }
    detail = (
        f"Executed {len(statements)} statement(s); returned {len(last_rows)} row(s) from the final result set."
        + (f" Output truncated by {truncation_reason}." if truncated and truncation_reason else "")
    )
    return outcome(
        "passed",
        "SQL executed successfully in an isolated in-memory SQLite session.",
        detail,
        data=data,
    )


def read_attempt(path: Path) -> tuple[str | None, dict[str, Any] | None]:
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        return None, outcome("host-error", "SQL attempt file could not be read.", f"{type(exc).__name__}: {exc}")

    if len(raw) > MAX_INPUT_BYTES:
        return None, outcome(
            "failed",
            "SQL attempt exceeds the runner input budget.",
            f"Attempt is larger than the {MAX_INPUT_BYTES}-byte input limit.",
        )
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, outcome("failed", "SQL attempt is not valid UTF-8 text.", f"UnicodeDecodeError: {exc}")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("path", help="Path to the learner-authored .sql attempt")
    command.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS)
    return command


def main() -> int:
    args = parser().parse_args()
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        payload = outcome("host-error", "SQL attempt file was not found.", f"attempt file not found: {path}")
    else:
        script, read_failure = read_attempt(path)
        payload = read_failure if read_failure is not None else execute_sql(script or "", args.timeout_ms)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
