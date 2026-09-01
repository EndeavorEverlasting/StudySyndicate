#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "yt-dlp-playlist.json"
URL_CORPUS = ROOT / "tests" / "fixtures" / "youtube-url-corpus.json"


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
        self.document = INGEST.normalize_collection(
            self.raw,
            requested_url=self.raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )

    def test_factored_records_preserve_playlist_order_metadata_and_fallback_source(self):
        self.assertEqual(self.document["schema"], "study-syndicate/source-import/v1")
        self.assertEqual(self.document["inputKind"], "playlist")
        self.assertEqual(self.document["playlistActorId"], "source:youtube:playlist:PL_TEST_123")
        self.assertEqual(len(self.document["actors"]), 3)
        self.assertEqual([item["position"] for item in self.document["occurrences"]], [1, 2])
        self.assertEqual(
            [item["positionSource"] for item in self.document["occurrences"]],
            ["encounter_order", "encounter_order"],
        )
        self.assertEqual(self.document["completeness"]["state"], "COMPLETE")
        refs = {
            item["ownerId"]: item["data"]
            for item in self.document["components"]
            if item["kind"] == "source-ref"
        }
        playlist_ref = refs["source:youtube:playlist:PL_TEST_123"]
        self.assertEqual(playlist_ref["channelId"], "UC_PLAYLIST_OWNER")
        self.assertEqual(refs["source:youtube:video:videoA001"]["durationSeconds"], 615)
        self.assertEqual(
            refs["source:youtube:video:videoB002"]["thumbnailUrl"],
            "https://i.ytimg.com/vi/videoB002/maxresdefault.jpg",
        )
        rows = INGEST.csv_rows(self.document)
        self.assertEqual(rows[1]["donor_commit"], "94eba4c156af080e87caf10cf8ffbea03bd17407")
        self.assertIn("東京", rows[1]["description"])
        self.assertIn('embedded "quote"', rows[1]["description"])

    def test_playlist_index_is_preferred_when_extractor_supplies_it(self):
        raw = json.loads(json.dumps(self.raw))
        raw["entries"][0]["playlist_index"] = 11
        raw["entries"][1]["playlist_index"] = 17
        document = INGEST.normalize_collection(
            raw,
            requested_url=raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )
        self.assertEqual([item["position"] for item in document["occurrences"]], [11, 17])
        self.assertEqual(
            [item["positionSource"] for item in document["occurrences"]],
            ["playlist_index", "playlist_index"],
        )
        self.assertEqual([rel["order"] for rel in document["relationships"]], [11, 17])
        self.assertEqual([rel["positionSource"] for rel in document["relationships"]], ["playlist_index", "playlist_index"])

    def test_explicit_packet_corpus_census_is_26_occurrences_24_unique(self):
        corpus = json.loads(URL_CORPUS.read_text(encoding="utf-8"))["urls"]
        census = INGEST.census_youtube_urls(corpus)
        self.assertEqual(census["occurrenceCount"], 26)
        self.assertEqual(census["uniqueVideoCount"], 24)
        self.assertEqual(census["unparseableEntries"], [])
        repeated = {item["videoId"]: item["positions"] for item in census["repeatedVideoIds"]}
        self.assertEqual(repeated["_CuibYl_Fh0"], [7, 8])
        self.assertEqual(repeated["bBdq2hf5R0I"], [17, 18])
        self.assertEqual(
            INGEST.youtube_video_id_from_url(corpus[6]),
            INGEST.youtube_video_id_from_url(corpus[7]),
        )

    def test_source_list_preserves_all_occurrences_without_duplicate_video_actors(self):
        corpus = json.loads(URL_CORPUS.read_text(encoding="utf-8"))["urls"]
        entries = []
        for position, url in enumerate(corpus, start=1):
            video_id = INGEST.youtube_video_id_from_url(url)
            entries.append({
                "id": video_id,
                "title": f"Video {video_id}",
                "webpage_url": url,
                "playlist_index": position,
            })
        raw = {
            "id": "fixture-list",
            "title": "Packet URL corpus",
            "_source_kind": "source-list",
            "_input_census": INGEST.census_youtube_urls(corpus),
            "_requested_urls": corpus,
            "entries": entries,
        }
        document = INGEST.normalize_collection(
            raw,
            requested_url=None,
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )
        video_actors = [actor for actor in document["actors"] if actor["id"].startswith("source:youtube:video:")]
        self.assertEqual(len(video_actors), 24)
        self.assertEqual(len(document["occurrences"]), 26)
        self.assertEqual(len(document["relationships"]), 26)
        self.assertEqual([item["position"] for item in document["occurrences"]], list(range(1, 27)))
        self.assertTrue(all(item["positionSource"] == "input_order" for item in document["occurrences"]))

    def test_single_video_is_valid_without_playlist_container(self):
        raw = dict(self.raw["entries"][0])
        document = INGEST.normalize_video(
            raw,
            requested_url=raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )
        self.assertEqual(document["inputKind"], "video")
        self.assertIsNone(document["playlistActorId"])
        self.assertEqual(document["rootActorId"], "source:youtube:video:videoA001")
        self.assertEqual(len(document["actors"]), 1)
        self.assertEqual(len(document["relationships"]), 0)
        self.assertEqual(len(document["occurrences"]), 1)

    def test_unavailable_slot_is_tombstone_and_partial_not_silently_dropped(self):
        raw = json.loads(json.dumps(self.raw))
        raw["entries"].insert(1, None)
        document = INGEST.normalize_collection(
            raw,
            requested_url=raw["webpage_url"],
            extractor_version="2026.08.19",
            mode="full",
            captured_at="2026-08-26T21:00:00Z",
        )
        self.assertEqual(len(document["occurrences"]), 3)
        self.assertTrue(document["occurrences"][1]["tombstone"])
        self.assertEqual(document["occurrences"][1]["status"], "UNAVAILABLE")
        self.assertEqual(document["completeness"]["state"], "PARTIAL")
        self.assertEqual(document["completeness"]["unavailableOccurrences"], 1)
        rows = INGEST.csv_rows(document)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["occurrence_status"], "UNAVAILABLE")

    def test_csv_is_projection_utf8_bom_unicode_and_all_formula_prefixes(self):
        raw = json.loads(json.dumps(self.raw))
        raw["title"] = "-Playlist, 東京"
        raw["entries"][0]["title"] = '=HYPERLINK("https://example.invalid","Café")'
        raw["entries"][0]["channel"] = "+SUM(1,1)"
        raw["entries"][0]["description"] = "@danger\nwith comma, quote \" and Unicode Ω"
        raw["entries"][1]["title"] = "-123"
        document = INGEST.normalize_collection(
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
            self.assertEqual(path.read_bytes()[:3], b"\xef\xbb\xbf")
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertTrue(rows[0]["playlist_title"].startswith("'-"))
        self.assertTrue(rows[0]["title"].startswith("'="))
        self.assertTrue(rows[0]["channel"].startswith("'+"))
        self.assertTrue(rows[0]["description"].startswith("'@"))
        self.assertTrue(rows[1]["title"].startswith("'-"))
        self.assertIn("Café", actor["label"])
        self.assertIn(
            "Ω",
            next(
                item["data"]["body"]
                for item in document["components"]
                if item["ownerId"] == actor["id"] and item["kind"] == "text-content"
            ),
        )

    def test_command_modes_never_download_media(self):
        full = INGEST.build_yt_dlp_command("yt-dlp", "https://example.invalid/watch?v=abc", "full")
        flat = INGEST.build_yt_dlp_command("yt-dlp", "https://example.invalid/playlist", "flat")
        for flag in ("--skip-download", "--dump-single-json", "--no-warnings"):
            self.assertIn(flag, full)
        self.assertNotIn("--flat-playlist", full)
        self.assertIn("--flat-playlist", flat)

    def test_unpinned_donor_reference_fails_closed(self):
        manifest = json.loads(
            (ROOT / "harness" / "sources" / "youtube-playlist-donor.v1.json").read_text(encoding="utf-8")
        )
        yt = next(item for item in manifest["donors"] if item["id"] == "yt-dlp")
        yt["commit"] = "master"
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_donor_manifest(manifest)

    def test_fixture_cli_writes_json_and_csv_deterministically(self):
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
            self.assertEqual(csv_path.read_bytes()[:3], b"\xef\xbb\xbf")
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(data["capturedAt"], "2026-08-26T21:00:00Z")
            self.assertEqual(len(data["occurrences"]), 2)
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 2)

    def test_collision_is_rejected_before_write_and_input_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            collision = temp_path / "collision.json"
            collision.write_bytes(FIXTURE.read_bytes())
            before = hashlib.sha256(collision.read_bytes()).hexdigest()
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "source-ingest-youtube.py"),
                    "--input-json",
                    str(collision),
                    "--extractor-version",
                    "2026.08.19",
                    "--captured-at",
                    "2026-08-26T21:00:00Z",
                    "--output-dir",
                    str(temp_path),
                    "--basename",
                    "collision",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("path collision", completed.stderr)
            self.assertEqual(hashlib.sha256(collision.read_bytes()).hexdigest(), before)
            self.assertFalse((temp_path / "collision.csv").exists())

    def test_input_json_requires_version_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "source-ingest-youtube.py"),
                    "--input-json",
                    str(FIXTURE),
                    "--output-dir",
                    temp,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("--extractor-version", completed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
