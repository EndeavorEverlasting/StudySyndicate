#!/usr/bin/env python3
"""Validate the PMP study system doctrine and its machine-readable MVP spec.

The doctrine lives in two coupled artifacts:
  - docs/PMP_STUDY_SYSTEM.md        (human-readable product architecture)
  - content/pmp/mvp-spec.v1.json    (machine-readable MVP contract)

This validator fails when either artifact is missing, when the manifest is
structurally incomplete, or when the doctrine document drifts out of sync with
the canonical enumerations declared in the manifest.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PMP_STUDY_SYSTEM.md"
SPEC = ROOT / "content" / "pmp" / "mvp-spec.v1.json"

EXPECTED_SCHEMA = "study-syndicate/pmp-study-system/v1"

REQUIRED_SECTIONS = [
    "# PMP Study System Doctrine",
    "## Product Vision",
    "## Learning Model",
    "## Local-First Architecture",
    "## Provenance and Source Model",
    "## PMP Competency Mapping",
    "## Core Entities",
    "## Multimedia Support",
    "## Exercise Taxonomy",
    "## Grading Doctrine",
    "## Rubric Scoring",
    "## Weakness and Mastery Model",
    "## PMP Concept Record",
    "## MVP Session Modes",
    "## MVP Build Order",
    "## MVP Acceptance Contract",
    "## Scope Boundaries",
]

CORE_ENTITY_KEYS = [
    "source", "competency", "concept", "card", "mediaAsset",
    "exercise", "rubric", "reviewAttempt", "masteryStat",
]
EXERCISE_TYPE_IDS = [
    "basic-flashcard", "cloze", "scenario-mcq", "multi-select", "ordering",
    "matching", "categorization", "image-prompt", "audio-recall",
    "video-critique", "free-recall", "case-drill", "trap-correction",
]
SESSION_MODE_IDS = [
    "due-review", "weakness-drill", "exam-judgment", "formula-pit",
    "mistake-replay", "source-build", "audio-walkthrough",
]
SOURCE_HIERARCHY_IDS = [
    "pmp-examination-content-outline", "pmi-standards-guides",
    "user-course-video-notes", "sanitized-real-work-scenarios", "mistake-log",
]
DELIVERY_APPROACHES = ["predictive", "agile-adaptive", "hybrid", "general"]
COMPETENCY_DIMENSIONS = [
    "examVersion", "domain", "taskOrEnabler", "deliveryApproach", "source", "weight",
]
CONCEPT_RECORD_KEYS = [
    "plainEnglishMeaning", "pmiExamLogic", "commonTrap",
    "realWorldInstinct", "pmiPreferredAnswer", "whyPmiPrefersIt",
]
LEARNING_MODEL = [
    "source-note", "atomic-concept", "exercise-variants",
    "review-attempts", "mastery-weakness-map", "recommended-practice-queue",
]
MULTIMEDIA = ["text", "image", "audio", "video"]


def fail(message: str) -> None:
    raise AssertionError(message)


def check_ids(items, key, expected, label):
    if not isinstance(items, list) or len(items) != len(expected):
        fail(f"{label}: expected {len(expected)} entries")
    got = [item.get(key) if isinstance(item, dict) else item for item in items]
    if got != expected:
        fail(f"{label}: ids/order must be exactly {expected} (got {got})")


def main() -> int:
    if not DOC.is_file():
        fail(f"missing doctrine document: {DOC.relative_to(ROOT)}")
    if not SPEC.is_file():
        fail(f"missing MVP spec: {SPEC.relative_to(ROOT)}")

    doc = DOC.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in doc:
            fail(f"doctrine missing required section: {section!r}")

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec.get("schema") != EXPECTED_SCHEMA:
        fail(f"unexpected schema: {spec.get('schema')!r}")

    if spec.get("learningModel") != LEARNING_MODEL:
        fail("learningModel does not match the canonical pipeline")
    if spec.get("multimedia") != MULTIMEDIA:
        fail("multimedia must be exactly text, image, audio, video")

    check_ids(spec.get("coreEntities"), "key", CORE_ENTITY_KEYS, "coreEntities")
    check_ids(spec.get("exerciseTypes"), "id", EXERCISE_TYPE_IDS, "exerciseTypes")
    check_ids(spec.get("sessionModes"), "id", SESSION_MODE_IDS, "sessionModes")
    check_ids(spec.get("sourceHierarchy"), "id", SOURCE_HIERARCHY_IDS, "sourceHierarchy")
    check_ids(spec.get("conceptRecordFields"), "key", CONCEPT_RECORD_KEYS, "conceptRecordFields")

    mapping = spec.get("competencyMapping") or {}
    if mapping.get("dimensions") != COMPETENCY_DIMENSIONS:
        fail("competencyMapping.dimensions must match the canonical dimensions")
    if mapping.get("deliveryApproaches") != DELIVERY_APPROACHES:
        fail("competencyMapping.deliveryApproaches must be predictive/agile-adaptive/hybrid/general")

    priorities = [s.get("priority") for s in spec["sourceHierarchy"]]
    if priorities != list(range(1, len(SOURCE_HIERARCHY_IDS) + 1)):
        fail("sourceHierarchy priorities must be contiguous 1..N in order")

    phases = [p.get("phase") for p in (spec.get("buildOrder") or [])]
    if phases != [1, 2, 3, 4, 5]:
        fail("buildOrder must define phases 1..5 in order")

    grading = spec.get("gradingModes") or {}
    for mode in ("exact", "typo-tolerant", "accepted-synonyms", "rubric"):
        if mode not in (grading.get("recallModes") or []):
            fail(f"gradingModes.recallModes missing {mode!r}")
    if grading.get("selfGrade") != ["Again", "Hard", "Good", "Easy"]:
        fail("gradingModes.selfGrade must be Again/Hard/Good/Easy")
    if (grading.get("rubric") or {}).get("scoreRange") != [0, 3]:
        fail("rubric scoreRange must be [0, 3]")
    if "semantic-local-ai-grading" not in (grading.get("laterExtensions") or []):
        fail("semantic/local-AI grading must be declared a later extension")

    policy = (spec.get("weaknessModel") or {}).get("recommendationPolicy") or {}
    if (spec.get("weaknessModel") or {}).get("levels") != ["card", "concept", "competency", "domain"]:
        fail("weaknessModel.levels must be card/concept/competency/domain")
    ratio = round(policy.get("weakAreas", 0) + policy.get("dueReviews", 0) + policy.get("newMaterial", 0), 6)
    if ratio != 1.0:
        fail(f"recommendationPolicy ratios must sum to 1.0 (got {ratio})")
    if policy.get("configurable") is not True:
        fail("recommendationPolicy must be marked configurable")

    if not spec.get("acceptanceContract"):
        fail("acceptanceContract must be a non-empty list")

    boundaries = (spec.get("scopeBoundaries") or {}).get("deferred") or []
    for deferred in ("cloud-sync", "ai-grading"):
        if deferred not in boundaries:
            fail(f"scopeBoundaries.deferred must include {deferred!r}")

    for key in CORE_ENTITY_KEYS + EXERCISE_TYPE_IDS + SESSION_MODE_IDS + SOURCE_HIERARCHY_IDS:
        if key not in doc:
            fail(f"doctrine document is out of sync with manifest: missing {key!r}")

    print(
        "pmp doctrine validation PASS: "
        f"{len(REQUIRED_SECTIONS)} sections, "
        f"{len(CORE_ENTITY_KEYS)} entities, "
        f"{len(EXERCISE_TYPE_IDS)} exercise types, "
        f"{len(SESSION_MODE_IDS)} session modes, "
        f"{len(spec['acceptanceContract'])} acceptance criteria"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError) as exc:
        print(f"pmp doctrine validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
