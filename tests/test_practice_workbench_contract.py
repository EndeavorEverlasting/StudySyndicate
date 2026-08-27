#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "harness" / "practice-workbench.v1.json").read_text(encoding="utf-8"))


class PracticeWorkbenchContractTests(unittest.TestCase):
    def test_every_language_has_explicit_runner_capability(self):
        for language in SPEC["languages"]:
            with self.subTest(language=language["id"]):
                runner = language["runner"]
                self.assertTrue(runner["id"])
                self.assertTrue(runner["kind"])
                self.assertIn(runner["status"], {"external-host-available", "available-in-browser", "planned", "unavailable"})
                self.assertTrue(runner["exceptionModel"])

    def test_sql_runner_is_bound_to_proven_local_adapter(self):
        sql = next(item for item in SPEC["languages"] if item["id"] == "sql")
        runner = sql["runner"]
        self.assertEqual(runner["id"], "sql-session")
        self.assertEqual(runner["kind"], "database-session")
        self.assertEqual(runner["status"], "external-host-available")
        self.assertEqual(runner["adapter"], "scripts/sql-runner.py")
        self.assertEqual(runner["protocol"], "json-stdout")
        self.assertGreater(runner["timeoutMsDefault"], 0)
        self.assertIn("in-memory SQLite", runner["trustBoundary"])
        self.assertIn("interrupted queries", runner["exceptionModel"])

    def test_lua_error_is_host_caught_not_ui_crash(self):
        lua = next(item for item in SPEC["languages"] if item["id"] == "lua")
        self.assertEqual(lua["runner"]["kind"], "embedded-host")
        self.assertIn("host catches", lua["runner"]["exceptionModel"])
        self.assertIn("runtime-error", lua["runner"]["exceptionModel"])

    def test_language_presence_never_implies_execution(self):
        invariants = "\n".join(SPEC["executionBoundary"]["invariants"])
        self.assertIn("Never infer runner availability", invariants)
        self.assertTrue(any(language["runner"]["status"] == "planned" for language in SPEC["languages"]))

    def test_ui_contract_requires_modal_and_drag_drop_with_text_fallback(self):
        ui = SPEC["uiContract"]
        self.assertEqual(ui["sessionConfiguration"], "modal")
        self.assertEqual(ui["workspace"], "draggable-panels")
        self.assertEqual(ui["textFallback"], "textarea-notepad")
        self.assertEqual(SPEC["panelLayout"]["defaultOrder"], ["premise", "workspace", "feedback"])

    def test_source_tracks_enforce_authority_and_starter_policy(self):
        tracks = {item["id"]: item for item in SPEC["sourceTracks"]}
        self.assertEqual(tracks["two-sum"]["readiness"], "premise-first-packet")
        self.assertEqual(tracks["two-sum"]["starterPolicy"], "packet-specific")
        self.assertIn("javascript", tracks["arrays-roadmap"]["languages"])
        self.assertEqual(tracks["arrays-roadmap"]["starterPolicy"], "neutral-empty-until-packet")
        self.assertEqual(tracks["sql-foundations"]["languages"], ["sql"])
        self.assertEqual(tracks["sql-foundations"]["starterPolicy"], "track-neutral-comment")
        self.assertEqual(tracks["rust-foundations"]["languages"], ["rust"])
        self.assertEqual(tracks["rust-foundations"]["starterPolicy"], "track-neutral-comment")


if __name__ == "__main__":
    unittest.main(verbosity=2)
