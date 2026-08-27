#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "promotion.py"
SPEC = importlib.util.spec_from_file_location("studysyndicate_promotion", MODULE_PATH)
assert SPEC and SPEC.loader
promotion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promotion)

HEAD = "1" * 40
BASE = "2" * 40


def candidate(**overrides):
    value = {
        "state": "open",
        "draft": False,
        "head": {
            "sha": HEAD,
            "repo": {"full_name": "EndeavorEverlasting/StudySyndicate"},
        },
        "base": {"ref": "main", "sha": BASE},
    }
    for key, replacement in overrides.items():
        if key in {"head", "base"}:
            value[key] = {**value[key], **replacement}
        else:
            value[key] = replacement
    return value


class PromotionContractTests(unittest.TestCase):
    def test_exact_candidate_passes(self):
        result = promotion.validate_candidate(candidate(), expected_head=HEAD)
        self.assertEqual(result["headSha"], HEAD)
        self.assertEqual(result["baseSha"], BASE)

    def test_stale_head_fails_closed(self):
        with self.assertRaisesRegex(promotion.PromotionError, "candidate head moved"):
            promotion.validate_candidate(candidate(head={"sha": "3" * 40}), expected_head=HEAD)

    def test_wrong_base_is_rejected(self):
        with self.assertRaisesRegex(promotion.PromotionError, "base drifted"):
            promotion.validate_candidate(candidate(base={"ref": "release"}), expected_head=HEAD)

    def test_cross_repository_head_is_rejected(self):
        with self.assertRaisesRegex(promotion.PromotionError, "head repository is not authorized"):
            promotion.validate_candidate(
                candidate(head={"repo": {"full_name": "someone/fork"}}),
                expected_head=HEAD,
            )

    def test_closed_or_draft_pr_is_rejected(self):
        with self.assertRaisesRegex(promotion.PromotionError, "must still be open"):
            promotion.validate_candidate(candidate(state="closed"), expected_head=HEAD)
        with self.assertRaisesRegex(promotion.PromotionError, "ready for review"):
            promotion.validate_candidate(candidate(draft=True), expected_head=HEAD)

    def test_malformed_expected_sha_is_rejected(self):
        with self.assertRaisesRegex(promotion.PromotionError, "40 lowercase hexadecimal"):
            promotion.validate_candidate(candidate(), expected_head="HEAD")

    def test_receipt_requires_successful_merge_and_application_digest(self):
        application = {
            "schema": "studysyndicate.application-e2e-receipt.v1",
            "distSha256": "a" * 64,
        }
        merge = {"merged": True, "sha": "b" * 40}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "receipt.json"
            receipt = promotion.write_receipt(
                candidate=candidate(),
                application=application,
                merge=merge,
                run_id="123",
                actor="EndeavorEverlasting",
                event="pull_request.ready_for_review",
                output=out,
            )
            self.assertTrue(out.is_file())
            parsed = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(parsed["candidateHeadSha"], HEAD)
            self.assertEqual(parsed["mergeSha"], "b" * 40)
            self.assertEqual(receipt["applicationArtifact"]["distSha256"], "a" * 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
