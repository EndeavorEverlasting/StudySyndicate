#!/usr/bin/env python3
"""Validate StudySyndicate multimodal media doctrine, contract, and domain coupling."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "MULTIMODAL_MEDIA.md"
SPEC = ROOT / "content" / "media" / "multimodal-media-contract.v1.json"
DOMAIN = ROOT / "src" / "domain" / "factored.ts"
DOMAIN_DOC = ROOT / "docs" / "DOMAIN_MODEL.md"
PMP_SPEC = ROOT / "content" / "pmp" / "mvp-spec.v1.json"

EXPECTED_SCHEMA = "study-syndicate/multimodal-media/v1"
MEDIA_KINDS = ["image", "audio", "video"]
ROLES = ["prompt", "answer", "explanation", "mnemonic", "context"]
LEARNING_MODES = ["audio-first", "visual-first", "multimodal", "text-fallback"]
ORIGINS = ["recorded", "generated", "imported"]
ACCEPTANCE_IDS = [
    "ac-media-node",
    "ac-voice-node",
    "ac-usage",
    "ac-bundle",
    "ac-dedupe",
    "ac-accessibility",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def require_text(text: str, required: list[str], label: str) -> None:
    for item in required:
        if item not in text:
            fail(f"{label} missing required text: {item!r}")


def main() -> int:
    for path in (DOC, SPEC, DOMAIN, DOMAIN_DOC, PMP_SPEC):
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec.get("schema") != EXPECTED_SCHEMA:
        fail(f"unexpected media schema: {spec.get('schema')!r}")
    if spec.get("mediaKinds") != MEDIA_KINDS:
        fail("mediaKinds must be image/audio/video in canonical order")
    if spec.get("roles") != ROLES:
        fail("roles are out of canonical order")
    if spec.get("learningModes") != LEARNING_MODES:
        fail("learningModes are out of canonical order")
    if spec.get("origins") != ORIGINS:
        fail("origins are out of canonical order")

    factored = spec.get("factoredModel") or {}
    expected_factored = {
        "actorKind": "media",
        "assetComponentKind": "media-ref",
        "usageRelationshipKind": "uses-media",
        "usageComponentKind": "media-usage",
    }
    for key, expected in expected_factored.items():
        if factored.get(key) != expected:
            fail(f"factoredModel.{key} must be {expected!r}")

    required_asset_fields = (spec.get("assetFields") or {}).get("required") or []
    for field in ("assetId", "mediaKind", "storageKey", "mimeType", "sha256", "byteLength", "origin"):
        if field not in required_asset_fields:
            fail(f"assetFields.required missing {field!r}")

    voice = spec.get("voiceNode") or {}
    if voice.get("kind") != "audio":
        fail("voiceNode.kind must be audio")
    if voice.get("speechTranscriptRequired") is not True:
        fail("spoken audio transcript must be required")
    if voice.get("speechLanguageRequired") is not True:
        fail("spoken audio language must be required")
    if voice.get("generatedSourceTextHash") != "sha256-of-transcript":
        fail("generated voice source text hash contract drifted")
    if "generator" not in (voice.get("generatedVoiceMetadata") or []):
        fail("generated voice metadata must include generator")

    visual = spec.get("visualNode") or {}
    if visual.get("meaningfulImageAltTextRequired") is not True:
        fail("meaningful images must require alt text")
    if visual.get("decorativeImagesMayOmitAltText") is not True:
        fail("decorative image accessibility exception missing")

    usage = spec.get("usage") or {}
    if usage.get("required") != ["role", "learningMode"]:
        fail("media usage must require role and learningMode")
    if usage.get("autoplayDefault") is not False:
        fail("autoplay must default false")

    portability = spec.get("portability") or {}
    structured = portability.get("structuredJson") or {}
    if structured.get("artifact") != "study.json":
        fail("structuredJson.artifact must be study.json")
    if structured.get("containsBinaryPayloads") is not False:
        fail("study.json must not contain binary payloads")

    bundle = portability.get("mediaBundle") or {}
    if bundle.get("manifestSchema") != "study-syndicate/media-bundle/v1":
        fail("media bundle manifest schema drifted")
    if bundle.get("sourceDescriptorSchema") != "study-syndicate/media-bundle-source/v1":
        fail("media bundle source descriptor schema drifted")
    if bundle.get("rootManifest") != "manifest.json":
        fail("bundle root manifest must be manifest.json")
    if bundle.get("structuredData") != "study.json":
        fail("bundle structured data must be study.json")
    if bundle.get("assetsDirectory") != "assets":
        fail("bundle assets directory must be assets")
    if bundle.get("integrityFields") != ["sha256", "byteLength"]:
        fail("bundle integrity fields must be sha256 and byteLength")

    authority = portability.get("authority") or {}
    if "media-usage-role" not in (authority.get("studyJson") or []):
        fail("study.json must own media usage role")
    if "learning-mode" not in (authority.get("studyJson") or []):
        fail("study.json must own learning mode")
    if "asset-path" not in (authority.get("manifestJson") or []):
        fail("manifest.json must own asset path")
    if "sha256" not in (authority.get("manifestJson") or []):
        fail("manifest.json must own binary sha256")
    if "media-usage-role" in (authority.get("manifestJson") or []):
        fail("manifest.json must not duplicate media usage semantics")

    import_rules = bundle.get("importRules") or []
    for rule in (
        "reject-path-traversal",
        "verify-every-asset-sha256-and-byteLength",
        "deduplicate-binary-assets-by-sha256",
        "preserve-stable-media-node-id",
        "fail-if-required-binary-asset-is-missing",
    ):
        if rule not in import_rules:
            fail(f"media bundle importRules missing {rule!r}")

    acceptance = spec.get("acceptanceContract") or []
    got_ids = [item.get("id") for item in acceptance if isinstance(item, dict)]
    if got_ids != ACCEPTANCE_IDS:
        fail(f"acceptanceContract ids/order must be {ACCEPTANCE_IDS}")

    doc = DOC.read_text(encoding="utf-8")
    require_text(
        doc,
        [
            "# Multimodal Media and Voice Nodes",
            "## Voice nodes",
            "## Visual nodes",
            "## Portable media bundle",
            "## Import rules",
            "study-syndicate/media-bundle/v1",
            "study.json",
            "manifest.json",
            "SHA-256",
            "transcript",
            "alt text",
            "media-usage",
            "uses-media",
        ],
        "multimodal doctrine",
    )

    domain = DOMAIN.read_text(encoding="utf-8")
    require_text(
        domain,
        [
            "| 'media-usage'",
            "export type MediaKind = 'image' | 'audio' | 'video';",
            "export type MediaRole =",
            "export type MediaLearningMode =",
            "export type MediaOrigin =",
            "sha256: string;",
            "byteLength: number;",
            "speech?: boolean;",
            "transcriptComponentId?: string;",
            "export interface MediaUsageData",
        ],
        "factored TypeScript contract",
    )

    domain_doc = DOMAIN_DOC.read_text(encoding="utf-8")
    require_text(
        domain_doc,
        [
            "`media-usage`",
            "voice node",
            "SHA-256",
            "transcript",
            "alt text",
        ],
        "domain model doc",
    )

    pmp = json.loads(PMP_SPEC.read_text(encoding="utf-8"))
    local_first = pmp.get("localFirst") or {}
    if local_first.get("portability") != ["json-export-import", "media-bundle-import-export"]:
        fail("PMP localFirst.portability must include media-bundle-import-export")
    pmp_bundle = local_first.get("mediaBundle") or {}
    if pmp_bundle.get("contract") != "study-syndicate/multimodal-media/v1":
        fail("PMP mediaBundle must reference the reusable multimodal contract")
    if pmp_bundle.get("manifestSchema") != "study-syndicate/media-bundle/v1":
        fail("PMP mediaBundle manifest schema drifted")

    build_order = pmp.get("buildOrder") or []
    phase1 = next((item for item in build_order if item.get("phase") == 1), {})
    phase5 = next((item for item in build_order if item.get("phase") == 5), {})
    if "media-bundle-import-export" not in (phase1.get("deliverables") or []):
        fail("PMP phase 1 must include media-bundle-import-export")
    if "media-authoring-tools" not in (phase5.get("deliverables") or []):
        fail("PMP phase 5 must retain richer media authoring as deferred tooling")
    if any("bundle" in item for item in (phase5.get("deliverables") or [])):
        fail("PMP phase 5 must not defer bundle portability")

    print(
        "multimodal media validation PASS: "
        f"{len(MEDIA_KINDS)} media kinds, "
        f"{len(ROLES)} roles, "
        f"{len(LEARNING_MODES)} learning modes, "
        f"{len(ACCEPTANCE_IDS)} acceptance criteria"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError) as exc:
        print(f"multimodal media validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
