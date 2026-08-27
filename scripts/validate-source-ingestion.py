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
WORKFLOW = ROOT / ".github" / "workflows" / "harness-infrastructure.yml"


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
    record = contract.get("recordContract") or {}
    if record.get("actorKinds") != ["source"] or "contains" not in (record.get("relationshipKinds") or []):
        fail("source import must use source actors with ordered contains relationships")
    if not {"source-ref", "text-content", "provenance"} <= set(record.get("componentKinds") or []):
        fail("source import component contract is incomplete")
    projection = contract.get("csvProjection") or {}
    required = {"playlist_id", "playlist_index", "video_id", "title", "url", "channel", "duration_seconds", "extractor_version", "donor_commit"}
    if not required <= set(projection.get("columns") or []):
        fail("CSV projection is missing required columns")
    if "projection" not in str(projection.get("authorityRule", "")).lower():
        fail("CSV must be explicitly subordinate to normalized JSON")
    cell_safety = str(projection.get("cellSafety", ""))
    if "canonical JSON remains unchanged" not in cell_safety or not all(prefix in cell_safety for prefix in ("=", "+", "-", "@")):
        fail("CSV contract must preserve canonical JSON while neutralizing spreadsheet formula prefixes")
    rules = "\n".join(str(item) for item in contract.get("rules") or [])
    if "repeated videos reuse the source actor" not in rules or "every playlist occurrence" not in rules:
        fail("source-import contract must preserve repeated playlist occurrences without duplicating actors")


def validate_repo_surfaces() -> None:
    types = TYPES.read_text(encoding="utf-8")
    for literal in ("'source-ref'", "export interface SourceRefData", "sourceKind: string", "locator: string"):
        if literal not in types:
            fail(f"factored domain types missing {literal!r}")

    validation = load(VALIDATION)
    commands = {tuple(item.get("argv") or []) for item in validation.get("checks") or []}
    for command in (("python", "scripts/validate-source-ingestion.py"), ("python", "tests/test_youtube_source_ingestion.py")):
        if command not in commands:
            fail(f"validation manifest missing {command}")

    source_adapters = set((load(HARNESS).get("components") or {}).get("sourceAdapters") or [])
    for path in ("harness/sources/youtube-playlist-donor.v1.json", "content/learning/source-import.v1.json", "scripts/source-ingest-youtube.py"):
        if path not in source_adapters:
            fail(f"harness sourceAdapters missing {path}")

    readme = README.read_text(encoding="utf-8")
    for literal in ("## YouTube Playlist Source Ingestion", "source-ingest-youtube.py", "yt-dlp.yt-dlp", ".csv"):
        if literal not in readme:
            fail(f"README missing source-ingestion navigation: {literal}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for literal in ("scripts/source-ingest-youtube.py", "scripts/validate-source-ingestion.py", "tests/test_youtube_source_ingestion.py"):
        if literal not in workflow:
            fail(f"harness workflow does not trigger for source-ingestion surface: {literal}")


def main() -> int:
    try:
        validate_donor_manifest(load(DONOR))
        validate_contract(load(CONTRACT))
        validate_repo_surfaces()
        print("source ingestion validation PASS: pinned donor authority, normalized JSON contract, CSV projection, adapter registration")
        return 0
    except (ValidationError, OSError, UnicodeDecodeError) as exc:
        print(f"source ingestion validation FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
