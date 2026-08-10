"""Reference implementations for the Two Sum mastery kata.

The repository may contain a known-good reference implementation, but personal mastery is
proved only by reconstructing the optimized solution from a blank file without AI assistance,
explaining the invariant and complexity, and passing the harness again.
"""

from __future__ import annotations

from collections.abc import Sequence


def two_sum_bruteforce(nums: Sequence[int], target: int) -> list[int]:
    """Return indices of two distinct values whose sum equals target in O(n^2) time."""
    for left in range(len(nums)):
        for right in range(left + 1, len(nums)):
            if nums[left] + nums[right] == target:
                return [left, right]
    raise ValueError("no two-sum solution")


def two_sum_hash(nums: Sequence[int], target: int) -> list[int]:
    """Return indices of two distinct values whose sum equals target in average O(n) time."""
    seen: dict[int, int] = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return [seen[complement], index]
        seen[value] = index
    raise ValueError("no two-sum solution")
