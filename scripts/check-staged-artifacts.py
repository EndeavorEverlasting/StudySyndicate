#!/usr/bin/env python3
"""Refuse staged machine-local/generated artifacts without inspecting file contents."""
from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import PurePosixPath

REMEDIATION = (
    "Move live/generated evidence back to ignored local output, or commit a sanitized "
    "fixture under an approved fixture/docs path."
)

APPROVED_FIXTURE_PREFIXES = ("fixtures/", "tests/fixtures/", "docs/fixtures/")
APPROVED_FIXTURE_MARKERS = (".fixture.", ".example.")

BLOCKED_DIR_NAMES = {
    "logs",
    "local-study-exports",
    "media-bundles",
    "playwright-report",
    "test-results",
    "coverage",
    ".cache",
    ".tmp",
    "tmp",
    ".venv",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".local-tools",
    "local-evidence",
    "runtime-evidence",
    "crash-dumps",
    ".study-syndicate",
}

BLOCKED_FILE_GLOBS = (
    "*.log",
    "*.dmp",
    "*.dump",
    "*.core",
    "core",
    "core.*",
    "hs_err_pid*.log",
    "*.stackdump",
    "*.crash",
    "*.pid",
    "*.trace",
    "*.sav",
    "*.save",
    "*.sqlite-wal",
    "*.sqlite-shm",
    ".DS_Store",
    "Thumbs.db",
)

SENSITIVE_FILE_GLOBS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
)


def normalized(path: str) -> str:
    value = path.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def is_approved_fixture(path: str) -> bool:
    p = normalized(path)
    if not p.startswith(APPROVED_FIXTURE_PREFIXES):
        return False
    name = PurePosixPath(p).name
    return any(marker in name for marker in APPROVED_FIXTURE_MARKERS)


def is_sensitive(path: str) -> bool:
    name = PurePosixPath(normalized(path)).name
    if name == ".env.example" or name.endswith(".env.example"):
        return False
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in SENSITIVE_FILE_GLOBS)


def generated_reason(path: str) -> str | None:
    p = normalized(path)
    parts = PurePosixPath(p).parts
    if is_sensitive(p):
        return "sensitive/local credential artifact"
    if is_approved_fixture(p):
        return None
    if any(part in BLOCKED_DIR_NAMES for part in parts[:-1]):
        return "generated/runtime output directory"
    name = PurePosixPath(p).name
    if any(fnmatch.fnmatchcase(name, pattern) for pattern in BLOCKED_FILE_GLOBS):
        return "generated/runtime file"
    return None


def staged_paths() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        sys.stderr.buffer.write(proc.stderr)
        raise SystemExit(proc.returncode)
    return [
        item.decode("utf-8", errors="surrogateescape")
        for item in proc.stdout.split(b"\0")
        if item
    ]


def main() -> int:
    blocked = [path for path in staged_paths() if generated_reason(path)]
    if not blocked:
        return 0
    for path in blocked:
        print(f"[harness] refusing staged generated/runtime artifact: {path}", file=sys.stderr)
    print(REMEDIATION, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
