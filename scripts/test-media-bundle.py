#!/usr/bin/env python3
"""Exercise the StudySyndicate media bundle pack/validate loop with temporary assets."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "media-bundle.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("study_media_bundle", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load media-bundle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tool = load_tool()

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        assets = root / "assets-source"
        assets.mkdir()

        voice = assets / "sql-having.mp3"
        voice.write_bytes(b"ID3-study-syndicate-voice-node")
        image = assets / "join-card.png"
        image.write_bytes(b"\x89PNG\r\n\x1a\nstudy-syndicate-visual-node")

        study_json = root / "study.json"
        study_json.write_text(
            json.dumps(
                {
                    "actors": [
                        {"id": "prompt-sql-having", "kind": "prompt"},
                        {"id": "media-sql-having-voice", "kind": "media"},
                        {"id": "media-sql-join-image", "kind": "media"},
                    ],
                    "relationships": [
                        {
                            "id": "rel-prompt-voice",
                            "kind": "uses-media",
                            "fromActorId": "prompt-sql-having",
                            "toActorId": "media-sql-having-voice",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        descriptor = root / "descriptor.json"
        descriptor.write_text(
            json.dumps(
                {
                    "schema": tool.SOURCE_SCHEMA,
                    "bundleId": "test-multimodal-bundle",
                    "createdAt": "2026-08-10T16:44:00-04:00",
                    "media": [
                        {
                            "id": "media-sql-having-voice",
                            "path": "sql-having.mp3",
                            "kind": "audio",
                            "mimeType": "audio/mpeg",
                            "origin": "generated",
                            "speech": True,
                            "language": "en-US",
                            "transcript": "WHERE filters rows before grouping; HAVING filters groups after aggregation.",
                            "voice": {"generator": "test-generator", "label": "study-voice"},
                        },
                        {
                            "id": "media-sql-join-image",
                            "path": "join-card.png",
                            "kind": "image",
                            "mimeType": "image/png",
                            "origin": "imported",
                            "altText": "Diagram showing a task joined to a project through project_id.",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        bundle = root / "study-media.zip"
        manifest = tool.pack_bundle(descriptor, assets, study_json, bundle)
        validated = tool.validate_bundle(bundle)

        assert validated["schema"] == tool.MANIFEST_SCHEMA
        assert len(validated["media"]) == 2
        assert validated["media"][0]["voice"]["sourceTextSha256"]
        assert validated["media"][0]["transcriptSha256"]
        assert "transcript" not in validated["media"][0]
        assert "role" not in validated["media"][0]
        assert "learningMode" not in validated["media"][0]
        assert validated["media"][1]["altTextSha256"]
        assert "altText" not in validated["media"][1]
        assert manifest == validated

        broken_descriptor = root / "broken.json"
        broken_descriptor.write_text(
            json.dumps(
                {
                    "schema": tool.SOURCE_SCHEMA,
                    "bundleId": "broken",
                    "createdAt": "2026-08-10T16:44:00-04:00",
                    "media": [
                        {
                            "id": "missing-transcript",
                            "path": "sql-having.mp3",
                            "kind": "audio",
                            "mimeType": "audio/mpeg",
                            "origin": "generated",
                            "speech": True,
                            "language": "en-US",
                            "voice": {"generator": "test-generator"},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        try:
            tool.build_manifest(tool.load_json(broken_descriptor), assets, study_json)
        except tool.BundleError as exc:
            assert "transcript" in str(exc)
        else:
            raise AssertionError("spoken audio without transcript should fail")

        corrupt = root / "corrupt.zip"
        with zipfile.ZipFile(bundle, "r") as source, zipfile.ZipFile(corrupt, "w") as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.startswith("assets/") and item.filename.endswith(".mp3"):
                    data += b"corruption"
                target.writestr(item, data)

        try:
            tool.validate_bundle(corrupt)
        except tool.BundleError as exc:
            assert "byteLength mismatch" in str(exc) or "sha256 mismatch" in str(exc)
        else:
            raise AssertionError("corrupted asset should fail validation")

    print("media bundle tests PASS: voice transcript gate, visual alt-text gate, pack/import integrity, corruption rejection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
