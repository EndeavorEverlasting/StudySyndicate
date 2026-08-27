#!/usr/bin/env python3
"""Import a YouTube playlist as StudySyndicate source records and CSV.

YouTube parsing is intentionally delegated to yt-dlp. This adapter owns only
StudySyndicate normalization, provenance, and export projection.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DONOR_MANIFEST = ROOT / "harness" / "sources" / "youtube-playlist-donor.v1.json"
CONTRACT = ROOT / "content" / "learning" / "source-import.v1.json"
OUTPUT_SCHEMA = "study-syndicate/source-import/v1"
YT_PROVIDER = "youtube"


class SourceImportError(ValueError):
    pass


def fail(message: str) -> None:
    raise SourceImportError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read JSON {path}: {exc}")


def load_contract() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    if contract.get("outputSchema") != OUTPUT_SCHEMA:
        fail("source-import contract output schema drifted")
    return contract


def yt_dlp_donor() -> dict[str, Any]:
    manifest = load_json(DONOR_MANIFEST)
    donors = manifest.get("donors") or []
    donor = next((item for item in donors if item.get("id") == "yt-dlp"), None)
    if not isinstance(donor, dict):
        fail("donor manifest does not contain yt-dlp")
    commit = str(donor.get("commit", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        fail("yt-dlp donor reference must be pinned to a 40-character commit SHA")
    return donor


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def playlist_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        values = parse_qs(urlparse(url).query).get("list") or []
    except ValueError:
        return None
    return values[0] if values else None


def first_url(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    return None


def thumbnail_url(item: dict[str, Any]) -> str | None:
    direct = first_url(item.get("thumbnail"))
    if direct:
        return direct
    thumbs = item.get("thumbnails")
    if isinstance(thumbs, list):
        for thumb in reversed(thumbs):
            if isinstance(thumb, dict):
                url = first_url(thumb.get("url"))
                if url:
                    return url
    return None


def int_or_none(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def canonical_video_url(item: dict[str, Any]) -> str:
    for key in ("webpage_url", "original_url"):
        value = first_url(item.get(key))
        if value:
            return value
    video_id = str(item.get("id", "")).strip()
    if not video_id:
        fail("playlist entry is missing a video id")
    return f"https://www.youtube.com/watch?v={video_id}"


def canonical_playlist_url(raw: dict[str, Any], requested_url: str | None, playlist_id: str) -> str:
    for key in ("webpage_url", "original_url"):
        value = first_url(raw.get(key))
        if value and "playlist" in value:
            return value
    if requested_url and playlist_id_from_url(requested_url):
        return requested_url
    return f"https://www.youtube.com/playlist?list={playlist_id}"


def component_id(kind: str, actor_id: str) -> str:
    return f"component:{kind}:{actor_id}"


def add_source_components(
    components: list[dict[str, Any]],
    actor_id: str,
    captured_at: str,
    source_ref: dict[str, Any],
    *,
    import_id: str,
    author: str | None,
    extractor_version: str,
    description: str | None,
    provenance_source_id: str | None = None,
) -> None:
    components.append(
        {
            "id": component_id("source-ref", actor_id),
            "kind": "source-ref",
            "ownerType": "actor",
            "ownerId": actor_id,
            "data": source_ref,
            "createdAt": captured_at,
            "updatedAt": captured_at,
        }
    )
    provenance: dict[str, Any] = {
        "importId": import_id,
        "revision": f"yt-dlp:{extractor_version}",
    }
    if provenance_source_id:
        provenance["sourceId"] = provenance_source_id
    if author:
        provenance["author"] = author
    components.append(
        {
            "id": component_id("provenance", actor_id),
            "kind": "provenance",
            "ownerType": "actor",
            "ownerId": actor_id,
            "data": provenance,
            "createdAt": captured_at,
            "updatedAt": captured_at,
        }
    )
    if isinstance(description, str) and description.strip():
        components.append(
            {
                "id": component_id("description", actor_id),
                "kind": "text-content",
                "ownerType": "actor",
                "ownerId": actor_id,
                "data": {"format": "plain-text", "body": description.strip()},
                "createdAt": captured_at,
                "updatedAt": captured_at,
            }
        )


def normalize_playlist(
    raw: dict[str, Any],
    *,
    requested_url: str | None,
    extractor_version: str,
    mode: str,
    captured_at: str | None = None,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        fail("yt-dlp output must be a JSON object")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        fail("yt-dlp playlist output must contain an entries list")

    captured = captured_at or now_utc()
    playlist_id = str(raw.get("id") or playlist_id_from_url(requested_url) or "").strip()
    if not playlist_id:
        fail("cannot resolve playlist id")
    playlist_url = canonical_playlist_url(raw, requested_url, playlist_id)
    playlist_title = str(raw.get("title") or f"YouTube playlist {playlist_id}").strip()
    playlist_actor_id = f"source:youtube:playlist:{playlist_id}"
    import_id = f"youtube-playlist:{playlist_id}:{captured}"

    actors: list[dict[str, Any]] = [
        {
            "id": playlist_actor_id,
            "kind": "source",
            "label": playlist_title,
            "createdAt": captured,
            "updatedAt": captured,
        }
    ]
    components: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    playlist_ref: dict[str, Any] = {
        "sourceKind": "playlist",
        "provider": YT_PROVIDER,
        "locator": playlist_url,
        "externalId": playlist_id,
    }
    playlist_channel_id = raw.get("channel_id") or raw.get("uploader_id")
    if playlist_channel_id:
        playlist_ref["channelId"] = str(playlist_channel_id)
    thumb = thumbnail_url(raw)
    if thumb:
        playlist_ref["thumbnailUrl"] = thumb
    add_source_components(
        components,
        playlist_actor_id,
        captured,
        playlist_ref,
        import_id=import_id,
        author=str(raw.get("channel") or raw.get("uploader") or "").strip() or None,
        extractor_version=extractor_version,
        description=raw.get("description") if isinstance(raw.get("description"), str) else None,
    )

    seen_ids: set[str] = set()
    for offset, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            fail(f"playlist entry {offset} is not an object")
        video_id = str(entry.get("id", "")).strip()
        if not video_id:
            fail(f"playlist entry {offset} is missing a video id")
        if video_id in seen_ids:
            fail(f"playlist contains duplicate video id {video_id!r}")
        seen_ids.add(video_id)

        actor_id = f"source:youtube:video:{video_id}"
        title = str(entry.get("title") or video_id).strip()
        actors.append(
            {
                "id": actor_id,
                "kind": "source",
                "label": title,
                "createdAt": captured,
                "updatedAt": captured,
            }
        )

        playlist_index = int_or_none(entry.get("playlist_index")) or offset
        source_ref: dict[str, Any] = {
            "sourceKind": "video",
            "provider": YT_PROVIDER,
            "locator": canonical_video_url(entry),
            "externalId": video_id,
            "parentExternalId": playlist_id,
            "playlistIndex": playlist_index,
        }
        optional = {
            "durationSeconds": int_or_none(entry.get("duration")),
            "channelId": entry.get("channel_id") or entry.get("uploader_id"),
            "thumbnailUrl": thumbnail_url(entry),
            "uploadDate": entry.get("upload_date") or entry.get("release_date"),
            "viewCount": int_or_none(entry.get("view_count")),
            "availability": entry.get("availability"),
        }
        for key, value in optional.items():
            if value not in (None, ""):
                source_ref[key] = value

        author = str(entry.get("channel") or entry.get("uploader") or "").strip() or None
        add_source_components(
            components,
            actor_id,
            captured,
            source_ref,
            import_id=import_id,
            author=author,
            extractor_version=extractor_version,
            description=entry.get("description") if isinstance(entry.get("description"), str) else None,
            provenance_source_id=playlist_actor_id,
        )
        relationships.append(
            {
                "id": f"relationship:contains:{playlist_id}:{video_id}",
                "kind": "contains",
                "fromActorId": playlist_actor_id,
                "toActorId": actor_id,
                "order": playlist_index,
                "createdAt": captured,
                "updatedAt": captured,
            }
        )

    donor = yt_dlp_donor()
    return {
        "schema": OUTPUT_SCHEMA,
        "importId": import_id,
        "capturedAt": captured,
        "provider": YT_PROVIDER,
        "playlistActorId": playlist_actor_id,
        "actors": actors,
        "relationships": relationships,
        "components": components,
        "extraction": {
            "tool": "yt-dlp",
            "runtimeVersion": extractor_version,
            "mode": mode,
            "donorRepository": donor["repository"],
            "donorCommit": donor["commit"],
        },
    }


def component_maps(document: dict[str, Any]) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    refs: dict[str, dict] = {}
    provenance: dict[str, dict] = {}
    descriptions: dict[str, str] = {}
    for component in document.get("components") or []:
        if not isinstance(component, dict):
            continue
        owner = str(component.get("ownerId", ""))
        data = component.get("data")
        if not isinstance(data, dict):
            continue
        if component.get("kind") == "source-ref":
            refs[owner] = data
        elif component.get("kind") == "provenance":
            provenance[owner] = data
        elif component.get("kind") == "text-content" and isinstance(data.get("body"), str):
            descriptions[owner] = data["body"]
    return refs, provenance, descriptions


def csv_rows(document: dict[str, Any]) -> list[dict[str, Any]]:
    contract = load_contract()
    columns = contract["csvProjection"]["columns"]
    actors = {item["id"]: item for item in document.get("actors") or [] if isinstance(item, dict) and item.get("id")}
    refs, provenance, descriptions = component_maps(document)
    playlist_actor_id = document.get("playlistActorId")
    playlist_actor = actors.get(playlist_actor_id, {})
    playlist_ref = refs.get(str(playlist_actor_id), {})
    extraction = document.get("extraction") or {}

    rows: list[dict[str, Any]] = []
    contains = [
        rel
        for rel in document.get("relationships") or []
        if isinstance(rel, dict) and rel.get("kind") == "contains" and rel.get("fromActorId") == playlist_actor_id
    ]
    contains.sort(key=lambda rel: int_or_none(rel.get("order")) or 0)
    for rel in contains:
        actor_id = str(rel.get("toActorId", ""))
        actor = actors.get(actor_id, {})
        ref = refs.get(actor_id, {})
        prov = provenance.get(actor_id, {})
        row = {
            "import_id": document.get("importId", ""),
            "playlist_id": playlist_ref.get("externalId", ""),
            "playlist_title": playlist_actor.get("label", ""),
            "playlist_url": playlist_ref.get("locator", ""),
            "playlist_index": ref.get("playlistIndex", rel.get("order", "")),
            "video_id": ref.get("externalId", ""),
            "title": actor.get("label", ""),
            "url": ref.get("locator", ""),
            "channel": prov.get("author", ""),
            "channel_id": ref.get("channelId", ""),
            "duration_seconds": ref.get("durationSeconds", ""),
            "upload_date": ref.get("uploadDate", ""),
            "view_count": ref.get("viewCount", ""),
            "availability": ref.get("availability", ""),
            "thumbnail_url": ref.get("thumbnailUrl", ""),
            "description": descriptions.get(actor_id, ""),
            "extractor": extraction.get("tool", ""),
            "extractor_version": extraction.get("runtimeVersion", ""),
            "donor_commit": extraction.get("donorCommit", ""),
        }
        rows.append({key: row.get(key, "") for key in columns})
    return rows


def write_json(document: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(document: dict[str, Any], path: Path) -> None:
    columns = load_contract()["csvProjection"]["columns"]
    rows = csv_rows(document)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def build_yt_dlp_command(executable: str, url: str, mode: str) -> list[str]:
    command = [executable, "--skip-download", "--dump-single-json", "--no-warnings"]
    if mode == "flat":
        command.append("--flat-playlist")
    command.append(url)
    return command


def extractor_version(executable: str) -> str:
    try:
        completed = subprocess.run([executable, "--version"], text=True, capture_output=True, check=False)
    except FileNotFoundError:
        fail(
            f"{executable!r} was not found. On Windows install yt-dlp with: "
            "winget install --id yt-dlp.yt-dlp -e"
        )
    if completed.returncode:
        fail(f"{executable} --version failed: {completed.stderr.strip()}")
    version = completed.stdout.strip()
    if not version:
        fail(f"{executable} --version returned no version")
    return version


def extract_live(executable: str, url: str, mode: str) -> dict[str, Any]:
    command = build_yt_dlp_command(executable, url, mode)
    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        fail(
            f"{executable!r} was not found. On Windows install yt-dlp with: "
            "winget install --id yt-dlp.yt-dlp -e"
        )
    if completed.returncode:
        fail(f"yt-dlp extraction failed with exit {completed.returncode}: {completed.stderr.strip()}")
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(f"yt-dlp returned invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail("yt-dlp returned a non-object JSON value")
    return data


def safe_basename(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-._")
    return cleaned[:120] or "youtube-playlist"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="YouTube playlist URL. Optional with --input-json.")
    parser.add_argument("--mode", choices=("full", "flat"), default="full")
    parser.add_argument("--format", choices=("both", "json", "csv"), default="both")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "local-study-exports")
    parser.add_argument("--basename")
    parser.add_argument("--yt-dlp", default="yt-dlp")
    parser.add_argument("--input-json", type=Path, help="Use saved yt-dlp JSON instead of live extraction.")
    parser.add_argument("--extractor-version", help="Required version override for --input-json fixtures.")
    parser.add_argument("--captured-at", help="UTC timestamp override for deterministic fixtures/tests.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.input_json:
            raw = load_json(args.input_json)
            if not isinstance(raw, dict):
                fail("--input-json must contain a JSON object")
            version = args.extractor_version or str(raw.get("extractor_version") or "saved-json")
            requested_url = args.url or raw.get("webpage_url") or raw.get("original_url")
        else:
            if not args.url:
                fail("a YouTube playlist URL is required unless --input-json is used")
            requested_url = args.url
            version = extractor_version(args.yt_dlp)
            raw = extract_live(args.yt_dlp, args.url, args.mode)

        document = normalize_playlist(
            raw,
            requested_url=str(requested_url) if requested_url else None,
            extractor_version=version,
            mode=args.mode,
            captured_at=args.captured_at,
        )
        playlist_id = document["extraction"] and document["playlistActorId"].rsplit(":", 1)[-1]
        basename = safe_basename(args.basename or f"youtube-playlist-{playlist_id}")
        json_path = args.output_dir / f"{basename}.json"
        csv_path = args.output_dir / f"{basename}.csv"

        if args.format in ("both", "json"):
            write_json(document, json_path)
            print(json_path)
        if args.format in ("both", "csv"):
            write_csv(document, csv_path)
            print(csv_path)
        print(f"source import PASS: {len(document['relationships'])} videos from {document['playlistActorId']}")
        return 0
    except (SourceImportError, OSError, KeyError, TypeError) as exc:
        print(f"source import FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
