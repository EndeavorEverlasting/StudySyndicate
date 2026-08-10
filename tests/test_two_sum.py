#!/usr/bin/env python3
"""Dependency-free correctness harness for the Two Sum reference implementations."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "practice" / "arrays"))

from two_sum import two_sum_bruteforce, two_sum_hash  # noqa: E402


IMPLEMENTATIONS = (two_sum_bruteforce, two_sum_hash)


class TwoSumContractTests(unittest.TestCase):
    def assert_pair(self, solver, nums, target, expected=None):
        snapshot = list(nums)
        pair = solver(nums, target)
        self.assertEqual(len(pair), 2)
        left, right = pair
        self.assertNotEqual(left, right, "a solution must use two distinct indices")
        self.assertEqual(nums[left] + nums[right], target)
        self.assertEqual(list(nums), snapshot, "solver must not mutate the input")
        if expected is not None:
            self.assertEqual(pair, expected)

    def test_canonical_example(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                self.assert_pair(solver, [2, 7, 11, 15], 9, [0, 1])

    def test_complement_appears_after_first_value(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                self.assert_pair(solver, [3, 2, 4], 6, [1, 2])

    def test_duplicate_values_use_distinct_indices(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                self.assert_pair(solver, [3, 3], 6, [0, 1])

    def test_negative_values(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                self.assert_pair(solver, [-3, 4, 3, 90], 0, [0, 2])

    def test_zero_and_mixed_signs(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                self.assert_pair(solver, [-1, 0, 1], 0, [0, 2])

    def test_single_value_cannot_be_reused(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                with self.assertRaises(ValueError):
                    solver([3], 6)

    def test_no_solution_is_explicit(self):
        for solver in IMPLEMENTATIONS:
            with self.subTest(solver=solver.__name__):
                with self.assertRaises(ValueError):
                    solver([1, 2, 4], 99)


if __name__ == "__main__":
    unittest.main(verbosity=2)
