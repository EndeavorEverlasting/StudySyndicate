#!/usr/bin/env python3
"""Validate the SQL/Rust foundations doctrine and machine-readable practice pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "software" / "SQL_RUST_FOUNDATIONS.md"
SPEC = ROOT / "content" / "software" / "sql-rust-foundations.v1.json"

EXPECTED_SCHEMA = "study-syndicate/software-foundations/v1"
TRACK_IDS = ["sql", "rust"]
SQL_MODULE_IDS = [
    "sql-select-filter-sort", "sql-aggregation", "sql-joins", "sql-null",
    "sql-subqueries-ctes", "sql-window-functions", "sql-data-change",
    "sql-modeling", "sql-indexes-plans", "sql-capstone",
]
RUST_MODULE_IDS = [
    "rust-types-functions", "rust-structs-enums", "rust-ownership",
    "rust-borrowing", "rust-option-result", "rust-collections-iterators",
    "rust-traits-generics", "rust-modules-tests", "rust-lifetimes",
    "rust-concurrency",
]
MAINTENANCE = [
    "Python", "JavaScript", "TypeScript", "Pandas", "NumPy", "Matplotlib",
    "React", "Django", "Flask", "Node.js", "Java", "C",
]
REQUIRED_DOC_SECTIONS = [
    "# SQL and Rust Foundations Practice Contract",
    "## Claim-defense doctrine", "## Time allocation", "## SQL track",
    "## Rust track", "## Integration project: taskq",
    "## Maintenance lane for other public claims", "## Weekly cadence",
    "## Machine-readable pack", "## Validation",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def ids(items, key: str) -> list[str]:
    if not isinstance(items, list):
        fail(f"expected a list for {key}")
    return [item.get(key) for item in items if isinstance(item, dict)]


def validate_track(track: dict, expected_modules: list[str], exercise_prefix: str, min_exercises: int) -> None:
    module_ids = ids(track.get("modules"), "id")
    if module_ids != expected_modules:
        fail(f"{track.get('id')} module order mismatch: {module_ids}")

    exercises = track.get("exercises")
    if not isinstance(exercises, list) or len(exercises) < min_exercises:
        fail(f"{track.get('id')} requires at least {min_exercises} exercises")

    seen: set[str] = set()
    for exercise in exercises:
        exercise_id = exercise.get("id")
        if not isinstance(exercise_id, str) or not exercise_id.startswith(exercise_prefix):
            fail(f"invalid {track.get('id')} exercise id: {exercise_id!r}")
        if exercise_id in seen:
            fail(f"duplicate exercise id: {exercise_id}")
        seen.add(exercise_id)
        if exercise.get("module") not in module_ids:
            fail(f"{exercise_id} references unknown module {exercise.get('module')!r}")
        if not exercise.get("prompt") or not exercise.get("proof"):
            fail(f"{exercise_id} must declare prompt and proof")

    gates = track.get("masteryGates")
    if not isinstance(gates, list) or len(gates) < 6:
        fail(f"{track.get('id')} requires at least six mastery gates")


def main() -> int:
    if not DOC.is_file():
        fail(f"missing doctrine document: {DOC.relative_to(ROOT)}")
    if not SPEC.is_file():
        fail(f"missing practice pack: {SPEC.relative_to(ROOT)}")

    doc = DOC.read_text(encoding="utf-8")
    for section in REQUIRED_DOC_SECTIONS:
        if section not in doc:
            fail(f"doctrine missing required section: {section}")

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec.get("schema") != EXPECTED_SCHEMA:
        fail(f"unexpected schema: {spec.get('schema')!r}")

    allocation = spec.get("allocation") or {}
    allocation_values = [allocation.get("sqlPercent"), allocation.get("rustPercent"), allocation.get("maintenancePercent")]
    if allocation_values != [50, 25, 25]:
        fail(f"allocation must be SQL/Rust/maintenance 50/25/25, got {allocation_values}")
    if sum(allocation_values) != 100:
        fail("allocation must sum to 100")
    if allocation.get("sessionMinutes") != [45, 60]:
        fail("sessionMinutes must preserve the 45-60 minute practice window")

    claim_defense = spec.get("claimDefense") or {}
    if claim_defense.get("states") != ["exposed", "practicing", "defensible"]:
        fail("claimDefense.states must be exposed -> practicing -> defensible")
    if claim_defense.get("maintenanceTechnologies") != MAINTENANCE:
        fail("maintenance technology roster drifted")

    tracks = spec.get("tracks")
    if ids(tracks, "id") != TRACK_IDS:
        fail("tracks must be SQL first, Rust second")

    sql, rust = tracks
    if sql.get("priority") != 1 or rust.get("priority") != 2:
        fail("track priorities must keep SQL ahead of Rust")
    validate_track(sql, SQL_MODULE_IDS, "sql-", 15)
    validate_track(rust, RUST_MODULE_IDS, "rust-", 10)

    sql_gate_text = " ".join(sql.get("masteryGates") or [])
    for required in ("window function", "NULL", "transaction", "normalized", "index"):
        if required.lower() not in sql_gate_text.lower():
            fail(f"SQL mastery gates missing {required!r}")

    rust_gate_text = " ".join(rust.get("masteryGates") or [])
    for required in ("String move", "borrowing", "Option", "Result", "trait", "cargo test", "lifetime"):
        if required.lower() not in rust_gate_text.lower():
            fail(f"Rust mastery gates missing {required!r}")

    project = spec.get("integrationProject") or {}
    if project.get("id") != "taskq":
        fail("integration project must be taskq")
    phases = project.get("phases") or []
    if [p.get("phase") for p in phases] != [1, 2, 3, 4]:
        fail("taskq phases must be contiguous 1..4")
    required_deliverables = {"CLI argument parsing", "normalized schema", "latest-event window query", "no-AI reconstruction drill"}
    deliverables = {item for phase in phases for item in (phase.get("deliverables") or [])}
    missing = required_deliverables - deliverables
    if missing:
        fail(f"taskq missing required deliverables: {sorted(missing)}")

    cadence = spec.get("weeklyCadence") or []
    if [item.get("day") for item in cadence] != ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Weekend"]:
        fail("weekly cadence must preserve Monday-Friday + Weekend order")

    session = spec.get("sessionTemplate") or []
    if [item.get("minutes") for item in session] != [10, 25, 15, 5]:
        fail("session template must be 10/25/15/5")
    if sum(item.get("minutes", 0) for item in session) != 55:
        fail("session template must total 55 minutes")

    acceptance = spec.get("acceptanceContract")
    if not isinstance(acceptance, list) or len(acceptance) < 6:
        fail("acceptanceContract must contain at least six criteria")
    acceptance_ids = ids(acceptance, "id")
    if len(acceptance_ids) != len(set(acceptance_ids)):
        fail("acceptanceContract ids must be unique")

    for literal in ("SQL: 50%", "Rust: 25%", "taskq", "ROW_NUMBER()", "ownership", "borrowing", "exposed -> practicing -> defensible", "python scripts/validate-software-foundations.py"):
        if literal not in doc:
            fail(f"doctrine out of sync with practice pack: missing {literal!r}")

    print(
        "software foundations validation PASS: "
        f"{len(sql['modules'])} SQL modules/{len(sql['exercises'])} exercises, "
        f"{len(rust['modules'])} Rust modules/{len(rust['exercises'])} exercises, "
        f"{len(MAINTENANCE)} maintenance technologies, "
        f"{len(acceptance)} acceptance criteria"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, TypeError) as exc:
        print(f"software foundations validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
