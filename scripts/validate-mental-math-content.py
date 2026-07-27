#!/usr/bin/env python3
"""Validate canonical mental-math fraction comparison seed content."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content" / "mental-math" / "fraction-comparison.v1.json"

EXPECTED_SCHEMA = "study-syndicate/mental-math-fraction-comparison/v1"
EXPECTED_STRATEGY_ORDER = [
    "same-denominator",
    "same-numerator",
    "benchmark-half",
    "benchmark-landmark",
    "gap-from-one",
    "landmark-residual",
    "common-numerator",
    "cross-multiply-fallback",
]
ALLOWED_ANSWERS = {"left", "right", "equal"}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard", "challenge"}


def fail(message: str) -> None:
    raise AssertionError(message)


def exact_answer(left: dict[str, int], right: dict[str, int]) -> str:
    lhs = Fraction(left["n"], left["d"])
    rhs = Fraction(right["n"], right["d"])
    if lhs > rhs:
        return "left"
    if lhs < rhs:
        return "right"
    return "equal"


def validate_fraction(value: dict[str, int], context: str) -> None:
    if set(value) != {"n", "d"}:
        fail(f"{context}: fraction must contain exactly n and d")
    if not isinstance(value["n"], int) or not isinstance(value["d"], int):
        fail(f"{context}: numerator and denominator must be integers")
    if value["d"] <= 0:
        fail(f"{context}: denominator must be positive")
    if value["n"] < 0:
        fail(f"{context}: numerator must be nonnegative")


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def validate_strategy_invariant(problem: dict, strategy: str) -> None:
    left = problem["left"]
    right = problem["right"]
    ln, ld = left["n"], left["d"]
    rn, rd = right["n"], right["d"]
    context = problem["id"]

    if strategy == "same-denominator":
        if ld != rd:
            fail(f"{context}: same-denominator strategy requires matching denominators")

    elif strategy == "same-numerator":
        if ln != rn:
            fail(f"{context}: same-numerator strategy requires matching numerators")

    elif strategy == "benchmark-half":
        lres = 2 * ln - ld
        rres = 2 * rn - rd
        if sign(lres) == sign(rres):
            fail(
                f"{context}: benchmark-half must settle the problem by putting "
                "the fractions on different sides of 1/2 or one exactly on it"
            )

    elif strategy == "benchmark-landmark":
        landmark = problem.get("landmark")
        if not landmark:
            fail(f"{context}: benchmark-landmark requires landmark")
        validate_fraction(landmark, f"{context}.landmark")
        p, q = landmark["n"], landmark["d"]
        lres = q * ln - p * ld
        rres = q * rn - p * rd
        if sign(lres) == sign(rres):
            fail(
                f"{context}: benchmark-landmark must settle the problem by "
                "placing the fractions on different sides or one on the landmark"
            )

    elif strategy == "gap-from-one":
        if not (0 <= ln <= ld and 0 <= rn <= rd):
            fail(f"{context}: gap-from-one seed problems must be fractions in [0, 1]")

    elif strategy == "landmark-residual":
        landmark = problem.get("landmark")
        if not landmark:
            fail(f"{context}: landmark-residual requires landmark")
        validate_fraction(landmark, f"{context}.landmark")
        p, q = landmark["n"], landmark["d"]
        lres = q * ln - p * ld
        rres = q * rn - p * rd
        if sign(lres) != sign(rres):
            fail(
                f"{context}: landmark-residual is reserved for fractions on the "
                "same side of the selected landmark"
            )
        left_offset = Fraction(lres, q * ld)
        right_offset = Fraction(rres, q * rd)
        if left_offset == right_offset and exact_answer(left, right) != "equal":
            fail(f"{context}: residual offsets unexpectedly fail to distinguish fractions")

    elif strategy == "common-numerator":
        common = problem.get("common_numerator")
        if not isinstance(common, int) or common <= 0:
            fail(f"{context}: common-numerator requires positive integer common_numerator")
        if common % ln or common % rn:
            fail(f"{context}: common_numerator must be divisible by both numerators")
        left_scaled_den = ld * (common // ln)
        right_scaled_den = rd * (common // rn)
        derived = (
            "left"
            if left_scaled_den < right_scaled_den
            else "right"
            if left_scaled_den > right_scaled_den
            else "equal"
        )
        if derived != problem["answer"]:
            fail(f"{context}: common-numerator transformed denominators contradict answer")

    elif strategy == "cross-multiply-fallback":
        pass

    else:
        fail(f"{context}: unknown strategy {strategy!r}")


def main() -> int:
    if not DATA.is_file():
        fail(f"missing seed content: {DATA.relative_to(ROOT)}")

    content = json.loads(DATA.read_text(encoding="utf-8"))

    if content.get("schema") != EXPECTED_SCHEMA:
        fail(f"unexpected schema: {content.get('schema')!r}")

    if content.get("strategy_order") != EXPECTED_STRATEGY_ORDER:
        fail("strategy_order does not match the canonical fallback ladder")

    principles = content.get("principles")
    flashcards = content.get("flashcards")
    problems = content.get("problems")
    if not isinstance(principles, list) or not principles:
        fail("principles must be a non-empty list")
    if not isinstance(flashcards, list) or not flashcards:
        fail("flashcards must be a non-empty list")
    if not isinstance(problems, list) or not problems:
        fail("problems must be a non-empty list")

    principle_ids = [item.get("id") for item in principles]
    if principle_ids != EXPECTED_STRATEGY_ORDER:
        fail("principle ids/order must exactly match strategy_order")

    priorities = [item.get("priority") for item in principles]
    if priorities != list(range(1, len(EXPECTED_STRATEGY_ORDER) + 1)):
        fail("principle priorities must be contiguous and match fallback order")

    seen: set[str] = set()
    for collection_name, items in (
        ("principles", principles),
        ("flashcards", flashcards),
        ("problems", problems),
    ):
        for item in items:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                fail(f"{collection_name}: every item needs a non-empty string id")
            if item_id in seen:
                fail(f"duplicate id across seed content: {item_id}")
            seen.add(item_id)

    known_principles = set(EXPECTED_STRATEGY_ORDER)

    for card in flashcards:
        refs = card.get("principle_ids")
        if not isinstance(refs, list) or not refs:
            fail(f"{card['id']}: flashcard needs principle_ids")
        unknown = set(refs) - known_principles
        if unknown:
            fail(f"{card['id']}: unknown principle refs: {sorted(unknown)}")
        if card.get("difficulty") not in ALLOWED_DIFFICULTIES:
            fail(f"{card['id']}: invalid difficulty")
        if not str(card.get("front", "")).strip() or not str(card.get("back", "")).strip():
            fail(f"{card['id']}: flashcard front/back cannot be blank")

    strategy_counts = {strategy: 0 for strategy in EXPECTED_STRATEGY_ORDER}
    for problem in problems:
        left = problem.get("left")
        right = problem.get("right")
        if not isinstance(left, dict) or not isinstance(right, dict):
            fail(f"{problem['id']}: left/right must be fraction objects")
        validate_fraction(left, f"{problem['id']}.left")
        validate_fraction(right, f"{problem['id']}.right")

        answer = problem.get("answer")
        if answer not in ALLOWED_ANSWERS:
            fail(f"{problem['id']}: invalid answer")
        actual = exact_answer(left, right)
        if answer != actual:
            fail(f"{problem['id']}: stored answer {answer!r} != exact answer {actual!r}")

        difficulty = problem.get("difficulty")
        if difficulty not in ALLOWED_DIFFICULTIES:
            fail(f"{problem['id']}: invalid difficulty")

        strategy = problem.get("recommended_strategy")
        if strategy not in known_principles:
            fail(f"{problem['id']}: unknown recommended_strategy")
        strategy_counts[strategy] += 1

        path = problem.get("strategy_path")
        if not isinstance(path, list) or not path:
            fail(f"{problem['id']}: strategy_path must be a non-empty list")
        if path[-1] != strategy:
            fail(f"{problem['id']}: strategy_path must end with recommended_strategy")
        unknown_path = set(path) - known_principles
        if unknown_path:
            fail(f"{problem['id']}: unknown strategy path refs: {sorted(unknown_path)}")

        if not str(problem.get("explanation", "")).strip():
            fail(f"{problem['id']}: explanation cannot be blank")

        validate_strategy_invariant(problem, strategy)

    uncovered = [strategy for strategy, count in strategy_counts.items() if count == 0]
    if uncovered:
        fail(f"no practice problem covers strategies: {uncovered}")

    print(
        "mental-math content validation PASS: "
        f"{len(principles)} principles, "
        f"{len(flashcards)} flashcards, "
        f"{len(problems)} problems"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, ZeroDivisionError) as exc:
        print(f"mental-math content validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
