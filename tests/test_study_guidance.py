#!/usr/bin/env python3
import importlib.util, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("study_guidance", ROOT / "scripts/study-guidance.py")
mod = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

class StudyGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "content/learning/study-guidance.v1.json").read_text(encoding="utf-8"))
        self.packet = self.contract["examplePacket"]

    def test_example_validates(self):
        mod.validate_packet(self.packet)

    def test_book_is_preserved_as_first_class_material(self):
        out = mod.derive(self.packet)
        books = [x for x in out["materials"] if x["materialKind"] == "book-guidance"]
        self.assertEqual(1, len(books))
        self.assertEqual("Learning SQL", books[0]["title"])
        self.assertEqual("Alan Beaulieu", books[0]["author"])
        self.assertFalse(books[0]["countsTowardMastery"])

    def test_cascade_target_is_schedule_only(self):
        out = mod.derive(self.packet)
        cascades = [x for x in out["materials"] if x["materialKind"] == "cascade-target"]
        self.assertEqual(["databases.relational-model"], [x["conceptId"] for x in cascades])
        self.assertTrue(all(x["countsTowardMastery"] is False for x in cascades))

    def test_resource_cannot_reference_unknown_concept(self):
        bad = json.loads(json.dumps(self.packet))
        bad["resources"][0]["conceptIds"] = ["sql.unknown"]
        with self.assertRaises(mod.GuidanceError):
            mod.validate_packet(bad)

    def test_iteration_must_advance_from_one(self):
        bad = json.loads(json.dumps(self.packet)); bad["iteration"] = 0
        with self.assertRaises(mod.GuidanceError):
            mod.validate_packet(bad)

if __name__ == "__main__":
    unittest.main(verbosity=2)
