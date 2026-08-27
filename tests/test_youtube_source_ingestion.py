#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "yt-dlp-playlist.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


INGEST = load_module("source_ingest_youtube", ROOT / "scripts" / "source-ingest-youtube.py")
VALIDATOR = load_module("validate_source_ingestion", ROOT / "scripts" / "validate-source-ingestion.py")


class YoutubeSourceIngestionTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.document = INGEST.normalize_playlist(
            self.raw,
            requested_url=self.raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )

    def test_factored_records_preserve_playlist_order(self):
        self.assertEqual(self.document["schema"], "study-syndicate/source-import/v1")
        self.assertEqual(self.document["playlistActorId"], "source:youtube:playlist:PL_TEST_123")
        self.assertEqual(len(self.document["actors"]), 3)
        self.assertEqual([rel["order"] for rel in self.document["relationships"]], [1, 2])
        refs = {
            item["ownerId"]: item["data"]
            for item in self.document["components"]
            if item["kind"] == "source-ref"
        }
        self.assertEqual(refs["source:youtube:video:videoA001"]["durationSeconds"], 615)
        self.assertEqual(refs["source:youtube:video:videoB002"]["locator"], "https://www.youtube.com/watch?v=videoB002")
        self.assertEqual(refs["source:youtube:video:videoB002"]["thumbnailUrl"], "https://i.ytimg.com/vi/videoB002/maxresdefault.jpg")

    def test_csv_is_projection_of_normalized_records(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "playlist.csv"
            INGEST.write_csv(self.document, path)
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["playlist_index"], "1")
        self.assertEqual(rows[0]["video_id"], "videoA001")
        self.assertEqual(rows[1]["channel"], "Second Channel")
        self.assertIn("with commas,\nand a newline", rows[1]["description"])
        self.assertEqual(rows[1]["donor_commit"], "94eba4c156af080e87caf10cf8ffbea03bd17407")

    def test_repeated_video_preserves_occurrences_without_duplicate_actor(self):
        raw = json.loads(json.dumps(self.raw))
        repeated = dict(raw["entries"][0])
        repeated["playlist_index"] = 3
        raw["entries"].append(repeated)
        document = INGEST.normalize_playlist(
            raw,
            requested_url=raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )
        video_actors = [item for item in document["actors"] if item["id"] == "source:youtube:video:videoA001"]
        self.assertEqual(len(video_actors), 1)
        occurrences = [rel for rel in document["relationships"] if rel["toActorId"] == "source:youtube:video:videoA001"]
        self.assertEqual([rel["order"] for rel in occurrences], [1, 3])
        self.assertEqual(len({rel["id"] for rel in occurrences}), 2)
        rows = INGEST.csv_rows(document)
        self.assertEqual([row["playlist_index"] for row in rows if row["video_id"] == "videoA001"], [1, 3])

    def test_csv_neutralizes_spreadsheet_formulas_without_changing_json(self):
        raw = json.loads(json.dumps(self.raw))
        raw["entries"][0]["title"] = "=HYPERLINK(\"https://example.invalid\",\"click\")"
        raw["entries"][0]["channel"] = "+SUM(1,1)"
        raw["entries"][0]["description"] = "@danger"
        document = INGEST.normalize_playlist(
            raw,
            requested_url=raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )
        actor = next(item for item in document["actors"] if item["id"] == "source:youtube:video:videoA001")
        self.assertTrue(actor["label"].startswith("="))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "playlist.csv"
            INGEST.write_csv(document, path)
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
        self.assertTrue(row["title"].startswith("'="))
        self.assertTrue(row["channel"].startswith("'+"))
        self.assertTrue(row["description"].startswith("'@"))

    def test_command_never_downloads_media(self):
        full = INGEST.build_yt_dlp_command("yt-dlp", "https://example.invalid/playlist", "full")
        flat = INGEST.build_yt_dlp_command("yt-dlp", "https://example.invalid/playlist", "flat")
        self.assertIn("--skip-download", full)
        self.assertIn("--dump-single-json", full)
        self.assertNotIn("--flat-playlist", full)
        self.assertIn("--flat-playlist", flat)

    def test_unpinned_donor_reference_fails_closed(self):
        manifest = json.loads((ROOT / "harness" / "sources" / "youtube-playlist-donor.v1.json").read_text(encoding="utf-8"))
        yt = next(item for item in manifest["donors"] if item["id"] == "yt-dlp")
        yt["commit"] = "master"
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_donor_manifest(manifest)

    def test_fixture_cli_writes_json_and_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "source-ingest-youtube.py"),
                    "--input-json",
                    str(FIXTURE),
                    "--extractor-version",
                    "2026.08.19",
                    "--captured-at",
                    "2026-08-26T21:00:00Z",
                    "--output-dir",
                    temp,
                    "--basename",
                    "building-the-llm",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            json_path = Path(temp) / "building-the-llm.json"
            csv_path = Path(temp) / "building-the-llm.csv"
            self.assertTrue(json_path.is_file())
            self.assertTrue(csv_path.is_file())
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(len(data["relationships"]), 2)
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
