#!/usr/bin/env python3
"""Validate the arrays mastery doctrine, machine-readable roadmap, and kata surface."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "software" / "ARRAYS_MASTERY.md"
SPEC = ROOT / "content" / "software" / "arrays-mastery.v1.json"
REFERENCE = ROOT / "practice" / "arrays" / "two_sum.py"
HARNESS = ROOT / "tests" / "test_two_sum.py"

EXPECTED_SCHEMA = "study-syndicate/arrays-mastery/v1"
ROADMAP_IDS = [
    "array-mechanics",
    "array-two-sum",
    "array-set-map",
    "array-running-state",
    "array-prefix-suffix",
    "array-two-pointers",
    "array-window",
    "array-binary-search",
    "array-capstone",
]
TWO_SUM_PHASES = [
    "contract-recall",
    "brute-force-reconstruction",
    "complement-model-explanation",
    "hash-map-reconstruction",
    "edge-case-defense",
    "complexity-defense",
    "blank-file-reconstruction",
    "transfer-variant",
]
REQUIRED_LEDGER_FIELDS = [
    "date",
    "problem",
    "attemptMode",
    "artifact",
    "tests",
    "explanation",
    "confusion",
    "nextRep",
    "masteryState",
]
REQUIRED_DOC_SECTIONS = [
    "# Arrays and Algorithms Mastery Contract",
    "## Claim-defense doctrine",
    "## Two Sum front to back",
    "## Two Sum mastery gate",
    "## The 45-minute transition session",
    "## Arrays roadmap",
    "## Freelancer proof packet",
    "## Evidence ledger",
    "## Machine-readable pack",
    "## Validation",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    for path in (DOC, SPEC, REFERENCE, HARNESS):
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    doc = DOC.read_text(encoding="utf-8")
    for section in REQUIRED_DOC_SECTIONS:
        if section not in doc:
            fail(f"doctrine missing required section: {section}")

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec.get("schema") != EXPECTED_SCHEMA:
        fail(f"unexpected schema: {spec.get('schema')!r}")

    claim = spec.get("claimDefense") or {}
    if claim.get("states") != ["exposed", "practicing", "defensible"]:
        fail("claim-defense states must be exposed -> practicing -> defensible")
    if "blank-file" not in (claim.get("rule") or "") or "no-AI" not in (claim.get("rule") or ""):
        fail("claim-defense rule must require blank-file no-AI reconstruction")

    session = spec.get("sessionTemplate") or []
    minutes = [item.get("minutes") for item in session]
    if minutes != [5, 10, 20, 5, 5] or sum(minutes) != 45:
        fail(f"session template must be 5/10/20/5/5 = 45 minutes, got {minutes}")

    two_sum = spec.get("twoSumMastery") or {}
    if two_sum.get("problem") != "Two Sum":
        fail("twoSumMastery.problem must be Two Sum")
    if two_sum.get("phases") != TWO_SUM_PHASES:
        fail("Two Sum mastery phases drifted")
    if two_sum.get("referenceImplementations") != ["two_sum_bruteforce", "two_sum_hash"]:
        fail("Two Sum reference implementation names drifted")
    invariants = " ".join(two_sum.get("invariants") or []).lower()
    for required in ("complement", "earlier indices", "before inserting", "own index", "[3, 3]"):
        if required.lower() not in invariants:
            fail(f"Two Sum invariants missing {required!r}")
    complexity = two_sum.get("complexity") or {}
    if (complexity.get("bruteforce") or {}).get("time") != "O(n^2)":
        fail("brute-force time complexity must be O(n^2)")
    if (complexity.get("hash") or {}).get("time") != "O(n) average":
        fail("hash-map time complexity must be O(n) average")
    if len(two_sum.get("graduationGates") or []) < 8:
        fail("Two Sum requires at least eight graduation gates")

    roadmap = spec.get("roadmap") or []
    ids = [item.get("id") for item in roadmap]
    orders = [item.get("order") for item in roadmap]
    if ids != ROADMAP_IDS:
        fail(f"roadmap order mismatch: {ids}")
    if orders != list(range(1, len(ROADMAP_IDS) + 1)):
        fail(f"roadmap numeric order mismatch: {orders}")

    exercises = spec.get("exercises") or []
    if len(exercises) < 15:
        fail("arrays mastery requires at least 15 exercises")
    exercise_ids: set[str] = set()
    for exercise in exercises:
        exercise_id = exercise.get("id")
        if not isinstance(exercise_id, str) or not exercise_id.startswith("array-"):
            fail(f"invalid exercise id: {exercise_id!r}")
        if exercise_id in exercise_ids:
            fail(f"duplicate exercise id: {exercise_id}")
        exercise_ids.add(exercise_id)
        if exercise.get("module") not in ROADMAP_IDS:
            fail(f"{exercise_id} references unknown module {exercise.get('module')!r}")
        if not exercise.get("prompt") or not exercise.get("proof"):
            fail(f"{exercise_id} must declare prompt and proof")

    ledger = spec.get("evidenceLedger") or {}
    if ledger.get("requiredFields") != REQUIRED_LEDGER_FIELDS:
        fail("evidence ledger fields drifted")
    if ledger.get("attemptModes") != ["assisted-study", "closed-book", "blank-file-no-ai", "transfer"]:
        fail("attempt modes drifted")
    if "defensible" not in (ledger.get("rule") or ""):
        fail("evidence ledger rule must constrain defensible state")

    acceptance = spec.get("acceptanceContract") or []
    if len(acceptance) < 6:
        fail("acceptanceContract must contain at least six criteria")
    acceptance_ids = [item.get("id") for item in acceptance]
    if len(acceptance_ids) != len(set(acceptance_ids)):
        fail("acceptanceContract ids must be unique")

    reference = REFERENCE.read_text(encoding="utf-8")
    for literal in ("def two_sum_bruteforce", "def two_sum_hash", "complement = target - value", "if complement in seen", "seen[value] = index", "raise ValueError"):
        if literal not in reference:
            fail(f"reference implementation missing {literal!r}")

    harness = HARNESS.read_text(encoding="utf-8")
    for literal in ("duplicate_values", "negative_values", "zero_and_mixed_signs", "single_value_cannot_be_reused", "no_solution_is_explicit", "must not mutate"):
        if literal not in harness:
            fail(f"Two Sum harness missing coverage marker {literal!r}")

    for literal in ("lookup-before-insert", "[3, 3]", "O(n^2)", "O(n)", "blank file", "python tests/test_two_sum.py"):
        if literal.lower() not in doc.lower():
            fail(f"doctrine out of sync: missing {literal!r}")

    print(
        "arrays mastery validation PASS: "
        f"{len(roadmap)} roadmap modules, {len(exercises)} exercises, "
        f"{len(two_sum['graduationGates'])} Two Sum gates, 45-minute session contract"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, TypeError) as exc:
        print(f"arrays mastery validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
