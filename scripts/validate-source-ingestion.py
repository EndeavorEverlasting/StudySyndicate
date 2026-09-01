#!/usr/bin/env python3
"""Validate external source-ingestion ownership and compatibility contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DONOR = ROOT / "harness" / "sources" / "youtube-playlist-donor.v1.json"
CONTRACT = ROOT / "content" / "learning" / "source-import.v1.json"
TYPES = ROOT / "src" / "domain" / "factored.ts"
VALIDATION = ROOT / "harness" / "validation-manifest.v1.json"
HARNESS = ROOT / "harness" / "harness-manifest.v1.json"
README = ROOT / "README.md"
RUN_SHEET = ROOT / "docs" / "YOUTUBE_SOURCE_INGESTION.md"
WORKFLOW = ROOT / ".github" / "workflows" / "harness-infrastructure.yml"
URL_CORPUS = ROOT / "tests" / "fixtures" / "youtube-url-corpus.json"


class ValidationError(AssertionError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected JSON object: {path}")
    return value


def pinned_sha(value: Any) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{40}", str(value or "")))


def validate_donor_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "study-syndicate/cross-repo-contribution/v1" or manifest.get("version") != 1:
        fail("unexpected contribution manifest schema/version")
    donors = manifest.get("donors") or []
    by_id = {item.get("id"): item for item in donors if isinstance(item, dict)}
    yt = by_id.get("yt-dlp")
    if not yt or yt.get("repository") != "yt-dlp/yt-dlp" or yt.get("disposition") != "ADOPT":
        fail("yt-dlp must remain the adopted runtime extraction authority")
    if not pinned_sha(yt.get("commit")):
        fail("yt-dlp donor reference is stale/unpinned")
    if "yt_dlp/extractor/youtube/_tab.py" not in (yt.get("authoritativePaths") or []):
        fail("yt-dlp donor must cite the YouTube playlist extractor")
    for donor_id in ("tubearchivist", "newpipe-extractor"):
        donor = by_id.get(donor_id)
        if not donor or donor.get("disposition") != "REFERENCE_ONLY" or not pinned_sha(donor.get("commit")):
            fail(f"{donor_id} must remain reference-only and commit-pinned")
    ownership = manifest.get("ownership") or {}
    if ownership.get("youtubeParsing") != "yt-dlp/yt-dlp":
        fail("YouTube parsing authority must remain with yt-dlp")
    if "StudySyndicate" not in str(ownership.get("studySourceSchema", "")):
        fail("StudySyndicate must own the normalized source schema")


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("schema") != "study-syndicate/source-import-contract/v1" or contract.get("version") != 1:
        fail("unexpected source-import contract schema/version")
    if contract.get("outputSchema") != "study-syndicate/source-import/v1":
        fail("unexpected normalized output schema")
    authority = contract.get("authority") or {}
    if authority.get("runSheet") != "docs/YOUTUBE_SOURCE_INGESTION.md":
        fail("source-import contract must bind the canonical operator run sheet")

    record = contract.get("recordContract") or {}
    if record.get("actorKinds") != ["source"] or "contains" not in (record.get("relationshipKinds") or []):
        fail("source import must use source actors with ordered contains relationships")
    if not {"source-ref", "text-content", "provenance"} <= set(record.get("componentKinds") or []):
        fail("source import component contract is incomplete")
    if set(record.get("sourceKinds") or []) != {"playlist", "source-list", "video"}:
        fail("source import must support playlist, explicit source-list, and video source kinds")
    if set(record.get("inputKinds") or []) != {"playlist", "url-list", "video"}:
        fail("source import input kinds drifted")
    required_top = {"inputKind", "rootActorId", "playlistActorId", "occurrences", "completeness", "inputCensus"}
    if not required_top <= set(record.get("topLevelRequired") or []):
        fail("normalized source contract is missing occurrence/completeness top-level fields")
    occurrence_required = {"id", "position", "positionSource", "sourceActorId", "externalId", "status", "tombstone"}
    if not occurrence_required <= set(record.get("occurrenceRequired") or []):
        fail("occurrence tombstone contract is incomplete")
    if set(record.get("positionSources") or []) != {"playlist_index", "encounter_order", "input_order"}:
        fail("position source vocabulary drifted")
    if set(record.get("completenessStates") or []) != {"COMPLETE", "PARTIAL", "EMPTY_CONFIRMED", "EMPTY_UNPROVEN", "FAILED"}:
        fail("completeness vocabulary drifted")

    projection = contract.get("csvProjection") or {}
    required_columns = {
        "input_kind", "playlist_id", "playlist_index", "position_source", "occurrence_status", "video_id",
        "title", "url", "channel", "duration_seconds", "completeness_state", "extractor_version", "donor_commit",
    }
    if not required_columns <= set(projection.get("columns") or []):
        fail("CSV projection is missing required occurrence/completeness columns")
    if projection.get("encoding") != "utf-8-sig":
        fail("spreadsheet CSV projection must remain utf-8-sig")
    if "projection" not in str(projection.get("authorityRule", "")).lower():
        fail("CSV must be explicitly subordinate to normalized JSON")
    cell_safety = str(projection.get("cellSafety", ""))
    if "canonical JSON remains unchanged" not in cell_safety or not all(prefix in cell_safety for prefix in ("=", "+", "-", "@")):
        fail("CSV contract must preserve canonical JSON while neutralizing spreadsheet formula prefixes")

    census = contract.get("inputCensus") or {}
    if not {"occurrenceCount", "uniqueVideoCount", "uniqueVideoIds", "repeatedVideoIds", "unparseableEntries"} <= set(census.get("requiredFields") or []):
        fail("explicit URL-list census contract is incomplete")
    if "si" not in str(census.get("identityRule", "")):
        fail("URL-list identity contract must reject share/tracking parameters as identity")

    path_safety = contract.get("pathSafety") or {}
    if path_safety.get("defaultOutputRoot") != "local-study-exports":
        fail("repository-owned source output root drifted")
    if "Reject equal resolved paths" not in str(path_safety.get("rule", "")):
        fail("source import path collision rule is missing")

    rules = "\n".join(str(item) for item in contract.get("rules") or [])
    for literal in ("single video is valid input", "repeated videos reuse the source actor", "occurrence tombstones", "playlist_index", "local-study-exports"):
        if literal.lower() not in rules.lower():
            fail(f"source-import rules missing {literal!r}")


def validate_repo_surfaces() -> None:
    types = TYPES.read_text(encoding="utf-8")
    for literal in ("'source-ref'", "export interface SourceRefData", "sourceKind: string", "locator: string", "positionSource?:"):
        if literal not in types:
            fail(f"factored domain types missing {literal!r}")

    validation = load(VALIDATION)
    commands = {tuple(item.get("argv") or []) for item in validation.get("checks") or []}
    for command in (("python", "scripts/validate-source-ingestion.py"), ("python", "tests/test_youtube_source_ingestion.py")):
        if command not in commands:
            fail(f"validation manifest missing {command}")

    source_adapters = set((load(HARNESS).get("components") or {}).get("sourceAdapters") or [])
    for path in (
        "harness/sources/youtube-playlist-donor.v1.json",
        "content/learning/source-import.v1.json",
        "scripts/source-ingest-youtube.py",
        "docs/YOUTUBE_SOURCE_INGESTION.md",
    ):
        if path not in source_adapters:
            fail(f"harness sourceAdapters missing {path}")

    corpus = load(URL_CORPUS)
    urls = corpus.get("urls") or []
    if corpus.get("schema") != "study-syndicate/test-youtube-url-corpus/v1" or len(urls) != 26:
        fail("YouTube URL corpus regression fixture must preserve the supplied 26 occurrences")

    readme = README.read_text(encoding="utf-8")
    for literal in ("## YouTube Playlist Source Ingestion", "source-ingest-youtube.py", "yt-dlp.yt-dlp", ".csv"):
        if literal not in readme:
            fail(f"README missing source-ingestion navigation: {literal}")

    run_sheet = RUN_SHEET.read_text(encoding="utf-8")
    run_sheet_lower = run_sheet.lower()
    for literal in ("multiple video urls", "completeness", "path collision", "local-study-exports", "--input-json", "powershell"):
        if literal not in run_sheet_lower:
            fail(f"YouTube source run sheet missing {literal!r}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for literal in (
        "scripts/source-ingest-youtube.py",
        "scripts/validate-source-ingestion.py",
        "tests/test_youtube_source_ingestion.py",
        '"tests/fixtures/**"',
        '"docs/YOUTUBE_SOURCE_INGESTION.md"',
    ):
        if literal not in workflow:
            fail(f"harness workflow does not trigger for source-ingestion surface: {literal}")


def main() -> int:
    try:
        validate_donor_manifest(load(DONOR))
        validate_contract(load(CONTRACT))
        validate_repo_surfaces()
        print(
            "source ingestion validation PASS: pinned yt-dlp authority, playlist/video/url-list normalization, "
            "occurrence completeness, path safety, CSV projection"
        )
        return 0
    except (ValidationError, OSError, UnicodeDecodeError) as exc:
        print(f"source ingestion validation FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
