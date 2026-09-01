#!/usr/bin/env python3
"""Import YouTube sources as StudySyndicate source records and CSV.

yt-dlp owns live YouTube extraction. This adapter owns only input census,
normalization, completeness/provenance, and deterministic JSON/CSV projection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
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
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
COMPLETENESS_STATES = {"COMPLETE", "PARTIAL", "EMPTY_CONFIRMED", "EMPTY_UNPROVEN", "FAILED"}


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
    if not re.fullmatch(r"[0-9a-f]{40}", str(donor.get("commit", ""))):
        fail("yt-dlp donor reference must be pinned to a 40-character commit SHA")
    return donor


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def first_url(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    return None


def playlist_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        values = parse_qs(urlparse(url).query).get("list") or []
    except ValueError:
        return None
    return values[0].strip() if values and values[0].strip() else None


def youtube_video_id_from_url(url: str | None) -> str | None:
    """Resolve stable identity from a supplied locator; never parse YouTube HTML."""
    if not url:
        return None
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return None
    host = parsed.netloc.lower().split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    candidate: str | None = None
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.path == "/watch":
            values = parse_qs(parsed.query).get("v") or []
            candidate = values[0] if values else None
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            candidate = parts[1]
    return candidate if candidate and VIDEO_ID_RE.fullmatch(candidate) else None


def census_youtube_urls(urls: list[str]) -> dict[str, Any]:
    positions: dict[str, list[int]] = {}
    unparseable: list[dict[str, Any]] = []
    for position, url in enumerate(urls, start=1):
        video_id = youtube_video_id_from_url(url)
        if video_id:
            positions.setdefault(video_id, []).append(position)
        else:
            unparseable.append({"position": position, "url": url})
    return {
        "occurrenceCount": len(urls),
        "uniqueVideoCount": len(positions),
        "uniqueVideoIds": list(positions),
        "repeatedVideoIds": [
            {"videoId": video_id, "positions": seen}
            for video_id, seen in positions.items()
            if len(seen) > 1
        ],
        "unparseableEntries": unparseable,
    }


def thumbnail_url(item: dict[str, Any]) -> str | None:
    direct = first_url(item.get("thumbnail"))
    if direct:
        return direct
    thumbs = item.get("thumbnails")
    if isinstance(thumbs, list):
        for thumb in reversed(thumbs):
            if isinstance(thumb, dict) and first_url(thumb.get("url")):
                return thumb["url"]
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
            video_id = youtube_video_id_from_url(value)
            return f"https://www.youtube.com/watch?v={video_id}" if video_id else value
    video_id = str(item.get("id", "")).strip()
    if not video_id:
        fail("video metadata is missing a video id")
    return f"https://www.youtube.com/watch?v={video_id}"


def collection_locator(raw: dict[str, Any], requested_url: str | None, collection_id: str, source_kind: str) -> str:
    if source_kind == "playlist":
        for key in ("webpage_url", "original_url"):
            value = first_url(raw.get(key))
            if value and playlist_id_from_url(value):
                return value
        if requested_url and playlist_id_from_url(requested_url):
            return requested_url
        return f"https://www.youtube.com/playlist?list={collection_id}"
    return f"youtube-url-list:{collection_id}"


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
    components.append({
        "id": component_id("source-ref", actor_id),
        "kind": "source-ref",
        "ownerType": "actor",
        "ownerId": actor_id,
        "data": source_ref,
        "createdAt": captured_at,
        "updatedAt": captured_at,
    })
    provenance: dict[str, Any] = {"importId": import_id, "revision": f"yt-dlp:{extractor_version}"}
    if provenance_source_id:
        provenance["sourceId"] = provenance_source_id
    if author:
        provenance["author"] = author
    components.append({
        "id": component_id("provenance", actor_id),
        "kind": "provenance",
        "ownerType": "actor",
        "ownerId": actor_id,
        "data": provenance,
        "createdAt": captured_at,
        "updatedAt": captured_at,
    })
    if isinstance(description, str) and description:
        components.append({
            "id": component_id("description", actor_id),
            "kind": "text-content",
            "ownerType": "actor",
            "ownerId": actor_id,
            "data": {"format": "plain-text", "body": description},
            "createdAt": captured_at,
            "updatedAt": captured_at,
        })


def add_video_actor(
    entry: dict[str, Any],
    *,
    actors: list[dict[str, Any]],
    components: list[dict[str, Any]],
    seen_ids: set[str],
    captured: str,
    import_id: str,
    extractor_version: str,
    parent_external_id: str | None,
    provenance_source_id: str | None,
) -> tuple[str, str]:
    video_id = str(entry.get("id", "")).strip()
    if not video_id:
        fail("video metadata is missing a video id")
    actor_id = f"source:youtube:video:{video_id}"
    if video_id in seen_ids:
        return video_id, actor_id
    seen_ids.add(video_id)
    actors.append({
        "id": actor_id,
        "kind": "source",
        "label": str(entry.get("title") or video_id),
        "createdAt": captured,
        "updatedAt": captured,
    })
    source_ref: dict[str, Any] = {
        "sourceKind": "video",
        "provider": YT_PROVIDER,
        "locator": canonical_video_url(entry),
        "externalId": video_id,
    }
    if parent_external_id:
        source_ref["parentExternalId"] = parent_external_id
    optional = {
        "durationSeconds": int_or_none(entry.get("duration")),
        "channelId": entry.get("channel_id") or entry.get("uploader_id"),
        "thumbnailUrl": thumbnail_url(entry),
        "uploadDate": entry.get("upload_date") or entry.get("release_date"),
        "viewCount": int_or_none(entry.get("view_count")),
        "availability": entry.get("availability"),
    }
    source_ref.update({key: value for key, value in optional.items() if value not in (None, "")})
    add_source_components(
        components,
        actor_id,
        captured,
        source_ref,
        import_id=import_id,
        author=str(entry.get("channel") or entry.get("uploader") or "").strip() or None,
        extractor_version=extractor_version,
        description=entry.get("description") if isinstance(entry.get("description"), str) else None,
        provenance_source_id=provenance_source_id,
    )
    return video_id, actor_id


def occurrence(
    root_id: str,
    position: int,
    position_source: str,
    *,
    actor_id: str | None,
    video_id: str | None,
    requested_url: str | None = None,
    detail: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": f"occurrence:youtube:{root_id}:{position}",
        "position": position,
        "positionSource": position_source,
        "sourceActorId": actor_id,
        "externalId": video_id,
        "status": "AVAILABLE" if actor_id else "UNAVAILABLE",
        "tombstone": actor_id is None,
    }
    if requested_url:
        value["requestedLocator"] = requested_url
    if detail:
        value["detail"] = detail
    return value


def completeness(occurrences: list[dict[str, Any]], *, extractor_evidence: bool = True) -> dict[str, Any]:
    total = len(occurrences)
    usable = sum(1 for item in occurrences if not item.get("tombstone"))
    if total == 0:
        state = "EMPTY_CONFIRMED" if extractor_evidence else "EMPTY_UNPROVEN"
    elif usable == total:
        state = "COMPLETE"
    elif usable == 0:
        state = "FAILED"
    else:
        state = "PARTIAL"
    return {
        "state": state,
        "totalOccurrences": total,
        "usableOccurrences": usable,
        "unavailableOccurrences": total - usable,
        "evidence": "extractor" if extractor_evidence else "input-only",
    }


def extraction_receipt(extractor_version: str, mode: str) -> dict[str, Any]:
    donor = yt_dlp_donor()
    return {
        "tool": "yt-dlp",
        "runtimeVersion": extractor_version,
        "mode": mode,
        "donorRepository": donor["repository"],
        "donorCommit": donor["commit"],
    }


def normalize_collection(
    raw: dict[str, Any],
    *,
    requested_url: str | None,
    extractor_version: str,
    mode: str,
    captured_at: str | None = None,
) -> dict[str, Any]:
    entries = raw.get("entries")
    if not isinstance(entries, list):
        fail("yt-dlp collection output must contain an entries list")
    source_kind = str(raw.get("_source_kind") or "playlist")
    if source_kind not in {"playlist", "source-list"}:
        fail(f"unsupported source collection kind: {source_kind}")
    captured = captured_at or now_utc()
    collection_id = str(raw.get("id") or playlist_id_from_url(requested_url) or "").strip()
    if not collection_id:
        fail("cannot resolve collection id")
    root_actor_id = f"source:youtube:{source_kind}:{collection_id}"
    import_id = f"youtube-{source_kind}:{collection_id}:{captured}"
    actors: list[dict[str, Any]] = [{
        "id": root_actor_id,
        "kind": "source",
        "label": str(raw.get("title") or f"YouTube {source_kind} {collection_id}"),
        "createdAt": captured,
        "updatedAt": captured,
    }]
    components: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    add_source_components(
        components,
        root_actor_id,
        captured,
        {
            "sourceKind": source_kind,
            "provider": YT_PROVIDER,
            "locator": collection_locator(raw, requested_url, collection_id, source_kind),
            "externalId": collection_id,
        },
        import_id=import_id,
        author=str(raw.get("channel") or raw.get("uploader") or "").strip() or None,
        extractor_version=extractor_version,
        description=raw.get("description") if isinstance(raw.get("description"), str) else None,
    )

    errors = raw.get("_occurrence_errors") if isinstance(raw.get("_occurrence_errors"), dict) else {}
    requested_urls = raw.get("_requested_urls") if isinstance(raw.get("_requested_urls"), list) else []
    seen_ids: set[str] = set()
    for offset, entry in enumerate(entries, start=1):
        requested_entry_url = requested_urls[offset - 1] if offset <= len(requested_urls) else None
        if not isinstance(entry, dict):
            occurrences.append(occurrence(
                collection_id, offset, "input_order" if source_kind == "source-list" else "encounter_order",
                actor_id=None, video_id=youtube_video_id_from_url(requested_entry_url),
                requested_url=requested_entry_url, detail=str(errors.get(str(offset)) or "extractor slot unavailable"),
            ))
            continue
        playlist_index = int_or_none(entry.get("playlist_index"))
        position = offset if source_kind == "source-list" else (playlist_index or offset)
        position_source = "input_order" if source_kind == "source-list" else ("playlist_index" if playlist_index else "encounter_order")
        video_id = str(entry.get("id", "")).strip()
        if not video_id:
            occurrences.append(occurrence(
                collection_id, position, position_source, actor_id=None, video_id=None,
                requested_url=requested_entry_url, detail=str(entry.get("availability") or "missing video id"),
            ))
            continue
        video_id, actor_id = add_video_actor(
            entry,
            actors=actors,
            components=components,
            seen_ids=seen_ids,
            captured=captured,
            import_id=import_id,
            extractor_version=extractor_version,
            parent_external_id=collection_id,
            provenance_source_id=root_actor_id,
        )
        occurrences.append(occurrence(
            collection_id, position, position_source, actor_id=actor_id, video_id=video_id,
            requested_url=requested_entry_url,
        ))
        relationships.append({
            "id": f"relationship:contains:{collection_id}:{offset}:{video_id}",
            "kind": "contains",
            "fromActorId": root_actor_id,
            "toActorId": actor_id,
            "order": position,
            "positionSource": position_source,
            "createdAt": captured,
            "updatedAt": captured,
        })

    return {
        "schema": OUTPUT_SCHEMA,
        "importId": import_id,
        "capturedAt": captured,
        "provider": YT_PROVIDER,
        "inputKind": "playlist" if source_kind == "playlist" else "url-list",
        "rootActorId": root_actor_id,
        "playlistActorId": root_actor_id if source_kind == "playlist" else None,
        "actors": actors,
        "relationships": relationships,
        "occurrences": occurrences,
        "components": components,
        "completeness": completeness(occurrences),
        "inputCensus": raw.get("_input_census"),
        "extraction": extraction_receipt(extractor_version, mode),
    }


def normalize_video(
    raw: dict[str, Any],
    *,
    requested_url: str | None,
    extractor_version: str,
    mode: str,
    captured_at: str | None = None,
) -> dict[str, Any]:
    captured = captured_at or now_utc()
    video_id = str(raw.get("id") or youtube_video_id_from_url(requested_url) or "").strip()
    if not video_id:
        fail("cannot resolve video id")
    entry = dict(raw)
    entry["id"] = video_id
    if requested_url and not first_url(entry.get("webpage_url")):
        entry["webpage_url"] = requested_url
    actor_id = f"source:youtube:video:{video_id}"
    import_id = f"youtube-video:{video_id}:{captured}"
    actors: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    add_video_actor(
        entry,
        actors=actors,
        components=components,
        seen_ids=set(),
        captured=captured,
        import_id=import_id,
        extractor_version=extractor_version,
        parent_external_id=None,
        provenance_source_id=None,
    )
    occurrences = [occurrence(
        video_id, 1, "input_order", actor_id=actor_id, video_id=video_id, requested_url=requested_url,
    )]
    return {
        "schema": OUTPUT_SCHEMA,
        "importId": import_id,
        "capturedAt": captured,
        "provider": YT_PROVIDER,
        "inputKind": "video",
        "rootActorId": actor_id,
        "playlistActorId": None,
        "actors": actors,
        "relationships": [],
        "occurrences": occurrences,
        "components": components,
        "completeness": completeness(occurrences),
        "inputCensus": census_youtube_urls([requested_url]) if requested_url else None,
        "extraction": extraction_receipt(extractor_version, mode),
    }


def normalize_extractor_response(raw: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        fail("yt-dlp output must be a JSON object")
    return normalize_collection(raw, **kwargs) if isinstance(raw.get("entries"), list) else normalize_video(raw, **kwargs)


def component_maps(document: dict[str, Any]) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    refs: dict[str, dict] = {}
    provenance: dict[str, dict] = {}
    descriptions: dict[str, str] = {}
    for component in document.get("components") or []:
        if not isinstance(component, dict) or not isinstance(component.get("data"), dict):
            continue
        owner, data = str(component.get("ownerId", "")), component["data"]
        if component.get("kind") == "source-ref":
            refs[owner] = data
        elif component.get("kind") == "provenance":
            provenance[owner] = data
        elif component.get("kind") == "text-content" and isinstance(data.get("body"), str):
            descriptions[owner] = data["body"]
    return refs, provenance, descriptions


def csv_rows(document: dict[str, Any]) -> list[dict[str, Any]]:
    columns = load_contract()["csvProjection"]["columns"]
    actors = {item["id"]: item for item in document.get("actors") or [] if isinstance(item, dict) and item.get("id")}
    refs, provenance, descriptions = component_maps(document)
    root_id = str(document.get("rootActorId") or document.get("playlistActorId") or "")
    root_actor, root_ref = actors.get(root_id, {}), refs.get(root_id, {})
    extraction, completion = document.get("extraction") or {}, document.get("completeness") or {}
    rows: list[dict[str, Any]] = []
    for item in document.get("occurrences") or []:
        actor_id = str(item.get("sourceActorId") or "")
        actor, ref, prov = actors.get(actor_id, {}), refs.get(actor_id, {}), provenance.get(actor_id, {})
        row = {
            "import_id": document.get("importId", ""),
            "input_kind": document.get("inputKind", ""),
            "playlist_id": root_ref.get("externalId", "") if root_ref.get("sourceKind") == "playlist" else "",
            "playlist_title": root_actor.get("label", "") if root_ref.get("sourceKind") == "playlist" else "",
            "playlist_url": root_ref.get("locator", "") if root_ref.get("sourceKind") == "playlist" else "",
            "playlist_index": item.get("position", ""),
            "position_source": item.get("positionSource", ""),
            "occurrence_status": item.get("status", ""),
            "video_id": item.get("externalId", ""),
            "title": actor.get("label", ""),
            "url": ref.get("locator", item.get("requestedLocator", "")),
            "channel": prov.get("author", ""),
            "channel_id": ref.get("channelId", ""),
            "duration_seconds": ref.get("durationSeconds", ""),
            "upload_date": ref.get("uploadDate", ""),
            "view_count": ref.get("viewCount", ""),
            "availability": ref.get("availability", ""),
            "thumbnail_url": ref.get("thumbnailUrl", ""),
            "description": descriptions.get(actor_id, item.get("detail", "")),
            "completeness_state": completion.get("state", ""),
            "extractor": extraction.get("tool", ""),
            "extractor_version": extraction.get("runtimeVersion", ""),
            "donor_commit": extraction.get("donorCommit", ""),
        }
        rows.append({key: row.get(key, "") for key in columns})
    return rows


def write_json(document: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def spreadsheet_safe_cell(value: Any) -> Any:
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_csv(document: dict[str, Any], path: Path) -> None:
    columns = load_contract()["csvProjection"]["columns"]
    safe_rows = [{key: spreadsheet_safe_cell(value) for key, value in row.items()} for row in csv_rows(document)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(safe_rows)


def build_yt_dlp_command(executable: str, url: str, mode: str) -> list[str]:
    command = [executable, "--skip-download", "--dump-single-json", "--no-warnings"]
    if mode == "flat":
        command.append("--flat-playlist")
    return [*command, url]


def extractor_version(executable: str) -> str:
    try:
        completed = subprocess.run([executable, "--version"], text=True, capture_output=True, check=False)
    except FileNotFoundError:
        fail(f"{executable!r} was not found. On Windows install yt-dlp with: winget install --id yt-dlp.yt-dlp -e")
    if completed.returncode or not completed.stdout.strip():
        fail(f"{executable} --version failed: {completed.stderr.strip() or 'no version returned'}")
    return completed.stdout.strip()


def extract_live(executable: str, url: str, mode: str) -> dict[str, Any]:
    try:
        completed = subprocess.run(build_yt_dlp_command(executable, url, mode), text=True, capture_output=True, check=False)
    except FileNotFoundError:
        fail(f"{executable!r} was not found. On Windows install yt-dlp with: winget install --id yt-dlp.yt-dlp -e")
    if completed.returncode:
        fail(f"yt-dlp extraction failed with exit {completed.returncode}: {completed.stderr.strip()}")
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(f"yt-dlp returned invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail("yt-dlp returned a non-object JSON value")
    return data


def build_url_list_raw(executable: str, urls: list[str], mode: str) -> dict[str, Any]:
    census = census_youtube_urls(urls)
    if census["unparseableEntries"]:
        positions = ", ".join(str(item["position"]) for item in census["unparseableEntries"])
        fail(f"unparseable YouTube URL(s) at position(s): {positions}")
    first_url_by_id: dict[str, str] = {}
    for url in urls:
        first_url_by_id.setdefault(youtube_video_id_from_url(url) or "", url)
    extracted: dict[str, dict[str, Any] | None] = {}
    errors_by_id: dict[str, str] = {}
    for video_id, url in first_url_by_id.items():
        try:
            raw = extract_live(executable, url, mode)
        except SourceImportError as exc:
            extracted[video_id], errors_by_id[video_id] = None, str(exc)
            continue
        returned_id = str(raw.get("id") or "").strip()
        if returned_id and returned_id != video_id:
            extracted[video_id], errors_by_id[video_id] = None, f"yt-dlp identity mismatch: returned {returned_id}"
        else:
            raw = dict(raw)
            raw["id"] = video_id
            raw.setdefault("webpage_url", f"https://www.youtube.com/watch?v={video_id}")
            extracted[video_id] = raw
    material = "\n".join(youtube_video_id_from_url(url) or "" for url in urls)
    list_id = hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]
    entries, errors = [], {}
    for position, url in enumerate(urls, start=1):
        video_id = youtube_video_id_from_url(url) or ""
        entry = extracted.get(video_id)
        if isinstance(entry, dict):
            item = dict(entry)
            item["playlist_index"] = position
            entries.append(item)
        else:
            entries.append(None)
            errors[str(position)] = errors_by_id.get(video_id, "metadata unavailable")
    return {
        "id": list_id,
        "title": f"YouTube URL list ({len(urls)} occurrences)",
        "_source_kind": "source-list",
        "_input_census": census,
        "_requested_urls": urls,
        "_occurrence_errors": errors,
        "entries": entries,
    }


def safe_basename(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-._")
    return cleaned[:120] or "youtube-source"


def assert_output_paths_safe(inputs: list[Path], outputs: list[Path]) -> None:
    resolved_inputs = {path.expanduser().resolve(strict=False): path for path in inputs}
    seen_outputs: dict[Path, Path] = {}
    for output in outputs:
        target = output.expanduser().resolve(strict=False)
        if target in resolved_inputs:
            fail(f"path collision: output {output} resolves to protected input {resolved_inputs[target]}; no files were written")
        if target in seen_outputs:
            fail(f"path collision: outputs {seen_outputs[target]} and {output} resolve to the same path")
        seen_outputs[target] = output


def enforce_completeness(document: dict[str, Any], allow_empty: bool) -> None:
    state = str((document.get("completeness") or {}).get("state") or "")
    if state not in COMPLETENESS_STATES:
        fail(f"unknown completeness state: {state!r}")
    if state in {"FAILED", "EMPTY_UNPROVEN"} and not allow_empty:
        fail(f"source import completeness is {state}; use --allow-empty only when intentional")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", help="One playlist/video URL or an ordered list of YouTube video URLs.")
    parser.add_argument("--mode", choices=("full", "flat"), default="full")
    parser.add_argument("--format", choices=("both", "json", "csv"), default="both")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "local-study-exports")
    parser.add_argument("--basename")
    parser.add_argument("--yt-dlp", default="yt-dlp")
    parser.add_argument("--input-json", type=Path, help="Use saved yt-dlp JSON instead of live extraction.")
    parser.add_argument("--extractor-version", help="Required version override for --input-json fixtures.")
    parser.add_argument("--captured-at", help="UTC timestamp override for deterministic fixtures/tests.")
    parser.add_argument("--allow-empty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        protected_inputs = [DONOR_MANIFEST, CONTRACT]
        if args.input_json:
            if len(args.urls) > 1:
                fail("--input-json accepts at most one locator hint")
            raw = load_json(args.input_json)
            if not isinstance(raw, dict):
                fail("--input-json must contain a JSON object")
            version = args.extractor_version or str(raw.get("extractor_version") or "").strip()
            if not version:
                fail("--input-json requires --extractor-version or extractor_version in saved JSON")
            requested = args.urls[0] if args.urls else raw.get("webpage_url") or raw.get("original_url")
            document = normalize_extractor_response(
                raw, requested_url=str(requested) if requested else None,
                extractor_version=version, mode=args.mode, captured_at=args.captured_at,
            )
            protected_inputs.append(args.input_json)
        else:
            if not args.urls:
                fail("at least one YouTube URL is required unless --input-json is used")
            version = extractor_version(args.yt_dlp)
            if len(args.urls) == 1:
                raw = extract_live(args.yt_dlp, args.urls[0], args.mode)
                document = normalize_extractor_response(
                    raw, requested_url=args.urls[0], extractor_version=version,
                    mode=args.mode, captured_at=args.captured_at,
                )
            else:
                raw = build_url_list_raw(args.yt_dlp, args.urls, args.mode)
                document = normalize_collection(
                    raw, requested_url=None, extractor_version=version,
                    mode=args.mode, captured_at=args.captured_at,
                )

        enforce_completeness(document, args.allow_empty)
        root_id = str(document.get("rootActorId") or "").rsplit(":", 1)[-1] or "source"
        basename = safe_basename(args.basename or f"youtube-{document.get('inputKind', 'source')}-{root_id}")
        json_path, csv_path = args.output_dir / f"{basename}.json", args.output_dir / f"{basename}.csv"
        assert_output_paths_safe(protected_inputs, [json_path, csv_path])
        if args.format in ("both", "json"):
            write_json(document, json_path)
            print(json_path)
        if args.format in ("both", "csv"):
            write_csv(document, csv_path)
            print(csv_path)
        result = document["completeness"]
        print(f"source import PASS: {result['usableOccurrences']}/{result['totalOccurrences']} usable ({result['state']})")
        return 0
    except (SourceImportError, OSError, KeyError, TypeError) as exc:
        print(f"source import FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
