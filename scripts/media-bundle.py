#!/usr/bin/env python3
"""Pack and validate StudySyndicate portable media bundles.

Transport authority only:
- study.json owns study semantics (actors, relationships, components, transcripts, alt text,
  media roles, and learning modes).
- manifest.json owns binary transport facts (paths, hashes, sizes, MIME types, origins, and
  reproducibility/accessibility hashes).

This utility does not decode media codecs or validate the full semantic study-record schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SOURCE_SCHEMA = "study-syndicate/media-bundle-source/v1"
MANIFEST_SCHEMA = "study-syndicate/media-bundle/v1"
MEDIA_KINDS = {"image", "audio", "video"}
ORIGINS = {"recorded", "generated", "imported"}
SHA256_HEX_LEN = 64


class BundleError(ValueError):
    pass


def fail(message: str) -> None:
    raise BundleError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read JSON {path}: {exc}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def ensure_safe_relative(path_text: str, label: str) -> PurePosixPath:
    normalized = path_text.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail(f"{label} must be a safe relative path: {path_text!r}")
    return path


def ensure_under(root: Path, candidate: Path, label: str) -> Path:
    root_resolved = root.resolve()
    candidate_resolved = candidate.resolve()
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError:
        fail(f"{label} escapes assets root: {candidate}")
    return candidate_resolved


def normalize_entry(raw: Any, assets_root: Path) -> tuple[dict[str, Any], Path]:
    if not isinstance(raw, dict):
        fail("every media entry must be an object")

    required = ("id", "path", "kind", "mimeType", "origin")
    missing = [key for key in required if not raw.get(key)]
    if missing:
        fail(f"media entry missing required fields: {missing}")

    kind = raw["kind"]
    if kind not in MEDIA_KINDS:
        fail(f"unsupported media kind {kind!r}")
    if raw["origin"] not in ORIGINS:
        fail(f"unsupported media origin {raw['origin']!r}")

    relative = ensure_safe_relative(str(raw["path"]), "media.path")
    source = ensure_under(assets_root, assets_root / Path(*relative.parts), "media.path")
    if not source.is_file():
        fail(f"media file does not exist: {relative.as_posix()}")

    speech = bool(raw.get("speech", False))
    transcript = raw.get("transcript")
    language = raw.get("language")

    if kind == "audio" and speech:
        if not isinstance(transcript, str) or not transcript.strip():
            fail(f"spoken audio {raw['id']!r} requires a non-empty transcript")
        if not isinstance(language, str) or not language.strip():
            fail(f"spoken audio {raw['id']!r} requires language")

    decorative = bool(raw.get("decorative", False))
    alt_text = raw.get("altText")
    if kind == "image" and not decorative:
        if not isinstance(alt_text, str) or not alt_text.strip():
            fail(f"meaningful image {raw['id']!r} requires altText")

    voice = raw.get("voice")
    if raw["origin"] == "generated" and kind == "audio":
        if not isinstance(voice, dict) or not str(voice.get("generator", "")).strip():
            fail(f"generated audio {raw['id']!r} requires voice.generator")
        voice = dict(voice)
        if speech:
            voice["sourceTextSha256"] = sha256_bytes(transcript.encode("utf-8"))

    sha256, byte_length = sha256_file(source)
    extension = source.suffix.lower()
    if not extension:
        guessed = mimetypes.guess_extension(str(raw["mimeType"]).split(";", 1)[0].strip())
        extension = (guessed or ".bin").lower()

    asset_path = f"assets/{sha256}{extension}"
    entry: dict[str, Any] = {
        "id": str(raw["id"]),
        "kind": kind,
        "mimeType": str(raw["mimeType"]),
        "origin": raw["origin"],
        "assetPath": asset_path,
        "sha256": sha256,
        "byteLength": byte_length,
        "originalFileName": source.name,
    }

    for key in ("language", "durationMs", "width", "height", "speech", "decorative"):
        if key in raw:
            entry[key] = raw[key]

    if speech and isinstance(transcript, str):
        entry["transcriptSha256"] = sha256_bytes(transcript.encode("utf-8"))
    if kind == "image" and not decorative and isinstance(alt_text, str):
        entry["altTextSha256"] = sha256_bytes(alt_text.encode("utf-8"))
    if voice is not None:
        entry["voice"] = voice

    return entry, source


def build_manifest(descriptor: Any, assets_root: Path, study_json: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    if not isinstance(descriptor, dict):
        fail("descriptor must be a JSON object")
    if descriptor.get("schema") != SOURCE_SCHEMA:
        fail(f"descriptor schema must be {SOURCE_SCHEMA!r}")
    if not descriptor.get("bundleId"):
        fail("descriptor.bundleId is required")
    if not descriptor.get("createdAt"):
        fail("descriptor.createdAt is required")

    study_data = load_json(study_json)
    if not isinstance(study_data, (dict, list)):
        fail("study.json must contain a JSON object or array")

    raw_media = descriptor.get("media")
    if not isinstance(raw_media, list) or not raw_media:
        fail("descriptor.media must be a non-empty list")

    seen_ids: set[str] = set()
    media: list[dict[str, Any]] = []
    files_by_asset_path: dict[str, Path] = {}

    for raw in raw_media:
        entry, source = normalize_entry(raw, assets_root)
        if entry["id"] in seen_ids:
            fail(f"duplicate media id: {entry['id']}")
        seen_ids.add(entry["id"])
        media.append(entry)
        files_by_asset_path.setdefault(entry["assetPath"], source)

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "bundleId": str(descriptor["bundleId"]),
        "createdAt": str(descriptor["createdAt"]),
        "structuredData": "study.json",
        "media": media,
    }
    return manifest, files_by_asset_path


def pack_bundle(descriptor_path: Path, assets_root: Path, study_json: Path, output: Path) -> dict[str, Any]:
    descriptor = load_json(descriptor_path)
    manifest, files = build_manifest(descriptor, assets_root, study_json)
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    study_bytes = study_json.read_bytes()

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".zip":
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", manifest_bytes)
            archive.writestr("study.json", study_bytes)
            for asset_path, source in sorted(files.items()):
                archive.write(source, asset_path)
    else:
        if output.exists() and not output.is_dir():
            fail(f"output exists and is not a directory: {output}")
        output.mkdir(parents=True, exist_ok=True)
        (output / "manifest.json").write_bytes(manifest_bytes)
        (output / "study.json").write_bytes(study_bytes)
        for asset_path, source in sorted(files.items()):
            target = output / Path(*PurePosixPath(asset_path).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    return manifest


def validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict):
        fail("manifest must be a JSON object")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        fail(f"manifest schema must be {MANIFEST_SCHEMA!r}")
    if manifest.get("structuredData") != "study.json":
        fail("manifest.structuredData must be 'study.json'")
    if not manifest.get("bundleId") or not manifest.get("createdAt"):
        fail("manifest requires bundleId and createdAt")

    media = manifest.get("media")
    if not isinstance(media, list) or not media:
        fail("manifest.media must be a non-empty list")

    seen_ids: set[str] = set()
    for entry in media:
        if not isinstance(entry, dict):
            fail("manifest media entries must be objects")
        for key in ("id", "kind", "mimeType", "origin", "assetPath", "sha256", "byteLength"):
            if key not in entry:
                fail(f"manifest media entry missing {key!r}")
        if entry["id"] in seen_ids:
            fail(f"duplicate manifest media id: {entry['id']}")
        seen_ids.add(entry["id"])

        if entry["kind"] not in MEDIA_KINDS:
            fail(f"unsupported manifest media kind {entry['kind']!r}")
        if entry["origin"] not in ORIGINS:
            fail(f"unsupported manifest media origin {entry['origin']!r}")

        ensure_safe_relative(str(entry["assetPath"]), "assetPath")
        if not str(entry["assetPath"]).startswith("assets/"):
            fail("assetPath must live under assets/")
        sha = str(entry["sha256"])
        if len(sha) != SHA256_HEX_LEN or any(ch not in "0123456789abcdef" for ch in sha):
            fail(f"invalid sha256 for media {entry['id']!r}")
        if not isinstance(entry["byteLength"], int) or entry["byteLength"] < 0:
            fail(f"invalid byteLength for media {entry['id']!r}")

        if entry["kind"] == "audio" and entry.get("speech"):
            if not str(entry.get("language", "")).strip():
                fail(f"spoken audio {entry['id']!r} missing language")
            transcript_sha = str(entry.get("transcriptSha256", ""))
            if len(transcript_sha) != SHA256_HEX_LEN:
                fail(f"spoken audio {entry['id']!r} missing transcriptSha256")
        if entry["kind"] == "image" and not entry.get("decorative", False):
            alt_sha = str(entry.get("altTextSha256", ""))
            if len(alt_sha) != SHA256_HEX_LEN:
                fail(f"meaningful image {entry['id']!r} missing altTextSha256")

        # Semantic study usage belongs only in study.json.
        for forbidden in ("role", "learningMode", "transcript", "altText"):
            if forbidden in entry:
                fail(f"manifest must not duplicate study semantic field {forbidden!r}")

    return media


def _validate_files(manifest: dict[str, Any], read_bytes) -> None:
    try:
        study = json.loads(read_bytes("study.json").decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"invalid study.json: {exc}")
    if not isinstance(study, (dict, list)):
        fail("study.json must contain a JSON object or array")

    for entry in manifest["media"]:
        try:
            data = read_bytes(entry["assetPath"])
        except KeyError:
            fail(f"missing required binary asset: {entry['assetPath']}")
        if len(data) != entry["byteLength"]:
            fail(f"byteLength mismatch for {entry['assetPath']}")
        actual = sha256_bytes(data)
        if actual != entry["sha256"]:
            fail(f"sha256 mismatch for {entry['assetPath']}")


def validate_bundle(bundle: Path) -> dict[str, Any]:
    if bundle.is_dir():
        root = bundle.resolve()

        def read_bytes(name: str) -> bytes:
            rel = ensure_safe_relative(name, "bundle member")
            path = ensure_under(root, root / Path(*rel.parts), "bundle member")
            if not path.is_file():
                raise KeyError(name)
            return path.read_bytes()

        try:
            manifest = json.loads(read_bytes("manifest.json").decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(f"invalid manifest.json: {exc}")
        validate_manifest(manifest)
        _validate_files(manifest, read_bytes)
        return manifest

    if not bundle.is_file() or bundle.suffix.lower() != ".zip":
        fail("bundle must be a directory or .zip file")

    with zipfile.ZipFile(bundle, "r") as archive:
        names = archive.namelist()
        for name in names:
            ensure_safe_relative(name, "zip member")
        if "manifest.json" not in names or "study.json" not in names:
            fail("zip bundle requires manifest.json and study.json")

        def read_bytes(name: str) -> bytes:
            return archive.read(name)

        try:
            manifest = json.loads(read_bytes("manifest.json").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(f"invalid manifest.json: {exc}")
        validate_manifest(manifest)

        expected = {"manifest.json", "study.json"}
        expected.update(entry["assetPath"] for entry in manifest["media"])
        extras = {name for name in names if not name.endswith("/")} - expected
        if extras:
            fail(f"bundle contains unreferenced files: {sorted(extras)}")

        _validate_files(manifest, read_bytes)
        return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    pack = sub.add_parser("pack", help="Pack study JSON and media files into a validated directory or ZIP bundle.")
    pack.add_argument("--descriptor", type=Path, required=True)
    pack.add_argument("--assets-root", type=Path, required=True)
    pack.add_argument("--study-json", type=Path, required=True)
    pack.add_argument("--output", type=Path, required=True)

    validate = sub.add_parser("validate", help="Validate an existing directory or ZIP media bundle.")
    validate.add_argument("bundle", type=Path)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "pack":
            manifest = pack_bundle(args.descriptor, args.assets_root, args.study_json, args.output)
            validate_bundle(args.output)
            print(
                "media bundle pack PASS: "
                f"{len(manifest['media'])} media nodes -> {args.output}"
            )
        else:
            manifest = validate_bundle(args.bundle)
            print(
                "media bundle validation PASS: "
                f"{len(manifest['media'])} media nodes in {args.bundle}"
            )
        return 0
    except (BundleError, OSError, zipfile.BadZipFile) as exc:
        print(f"media bundle FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
