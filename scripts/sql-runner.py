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
MAX_ROWS = 200
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


def json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, bytes):
        return {"blobHex": value.hex()}
    return str(value)


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


def execute_sql(script: str, timeout_ms: int) -> dict[str, Any]:
    timeout_ms = max(MIN_TIMEOUT_MS, min(MAX_TIMEOUT_MS, timeout_ms))
    deadline = time.monotonic() + (timeout_ms / 1000.0)
    timed_out = False

    connection = sqlite3.connect(":memory:", isolation_level=None)
    connection.enable_load_extension(False)
    install_authorizer(connection)

    def interrupt_expired_query() -> int:
        nonlocal timed_out
        if time.monotonic() >= deadline:
            timed_out = True
            return 1
        return 0

    connection.set_progress_handler(interrupt_expired_query, 1000)

    statements = split_statements(script)
    if not statements:
        connection.close()
        return outcome("failed", "No SQL statement was provided.", "Write at least one SQL statement and try again.")

    last_columns: list[str] = []
    last_rows: list[list[Any]] = []
    truncated = False

    try:
        for statement in statements:
            cursor = connection.execute(statement)
            if cursor.description is None:
                continue
            last_columns = [item[0] for item in cursor.description]
            fetched = cursor.fetchmany(MAX_ROWS + 1)
            truncated = len(fetched) > MAX_ROWS
            last_rows = [[json_value(value) for value in row] for row in fetched[:MAX_ROWS]]
    except sqlite3.Error as exc:
        if timed_out or "interrupted" in str(exc).lower():
            return outcome(
                "timeout",
                "SQL execution exceeded the runner time limit.",
                f"Interrupted after {timeout_ms} ms. Reduce the query or inspect an accidental unbounded recursion/cartesian expansion.",
            )
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
        "database": "sqlite-memory",
    }
    detail = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return outcome(
        "passed",
        "SQL executed successfully in an isolated in-memory SQLite session.",
        detail,
        data=data,
    )


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
        try:
            script = path.read_text(encoding="utf-8")
        except OSError as exc:
            payload = outcome("host-error", "SQL attempt file could not be read.", f"{type(exc).__name__}: {exc}")
        else:
            payload = execute_sql(script, args.timeout_ms)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
