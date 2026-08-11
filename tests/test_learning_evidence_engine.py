#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "learning-evidence.py"
CONTRACT = json.loads((ROOT / "content" / "learning" / "learning-evidence.v1.json").read_text(encoding="utf-8"))

spec = importlib.util.spec_from_file_location("learning_evidence", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class LearningEvidenceEngineTests(unittest.TestCase):
    def event(self, assistance="none", evidence=None, cascade=None):
        return {
            "eventId": "evt-1",
            "conceptId": "concept-a",
            "assistance": assistance,
            "evidence": evidence or [
                {"facet": "construct", "quality": 0.8},
                {"facet": "apply", "quality": 0.4},
                {"facet": "debug", "quality": 0.6},
            ],
            "cascade": cascade or [],
        }

    def test_incomplete_work_keeps_partial_credit(self):
        result = module.score_event(self.event(), CONTRACT)
        self.assertGreater(result["eventCredit"], 0)
        self.assertLess(result["eventCredit"], 1)
        self.assertEqual({x["facet"] for x in result["earnedFacets"]}, {"construct", "apply", "debug"})
        self.assertFalse(result["masteryClaimAllowed"])

    def test_ai_answer_is_bounded_without_erasing_evidence(self):
        evidence = [
            {"facet": "construct", "quality": 1.0},
            {"facet": "apply", "quality": 1.0},
            {"facet": "debug", "quality": 1.0},
            {"facet": "explain", "quality": 1.0},
            {"facet": "discover", "quality": 1.0},
        ]
        result = module.score_event(self.event("ai-answer", evidence), CONTRACT)
        self.assertEqual(result["rawCredit"], 1.0)
        self.assertEqual(result["eventCredit"], 0.2)
        self.assertFalse(result["eventMasterySignal"])

    def test_cascade_credit_is_acknowledgement_only(self):
        result = module.score_event(
            self.event(cascade=[{"conceptId": "prerequisite-b", "relationWeight": 0.8}]),
            CONTRACT,
        )
        cascade = result["cascadeRecognition"][0]
        self.assertGreater(cascade["recognitionCredit"], 0)
        self.assertLessEqual(cascade["recognitionCredit"], result["eventCredit"] * 0.25)
        self.assertFalse(cascade["countsTowardMastery"])

    def test_duplicate_cascade_concepts_are_rejected(self):
        cascade = [
            {"conceptId": "prerequisite-b", "relationWeight": 1.0},
            {"conceptId": "prerequisite-b", "relationWeight": 1.0},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate cascade conceptId"):
            module.score_event(self.event(cascade=cascade), CONTRACT)

    def test_strong_direct_rep_can_emit_signal_but_not_mastery_claim(self):
        evidence = [
            {"facet": "construct", "quality": 0.9},
            {"facet": "apply", "quality": 0.9},
            {"facet": "explain", "quality": 0.9},
        ]
        result = module.score_event(self.event("none", evidence), CONTRACT)
        self.assertTrue(result["eventMasterySignal"])
        self.assertFalse(result["masteryClaimAllowed"])

    def test_invalid_quality_fails(self):
        with self.assertRaises(ValueError):
            module.score_event(self.event(evidence=[{"facet": "construct", "quality": 1.1}]), CONTRACT)

    def test_example_contract_scores(self):
        result = module.score_event(CONTRACT["exampleEvent"], CONTRACT)
        self.assertEqual(result["assistance"], "hint")
        self.assertTrue(result["acknowledgement"]["message"])
        self.assertEqual(result["cascadeRecognition"][0]["conceptId"], "arrays.hash-map")


if __name__ == "__main__":
    unittest.main(verbosity=2)