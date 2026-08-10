#!/usr/bin/env python3
"""Validate the multi-language Practice Workbench contract and UI coupling."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "harness" / "practice-workbench.v1.json"
PACKET_CONTRACT = ROOT / "harness" / "problems" / "problem-packet-contract.v1.json"
PACKAGE = ROOT / "package.json"
APP = ROOT / "src" / "App.tsx"
MODAL = ROOT / "src" / "components" / "PracticeModal.tsx"
CATALOG = ROOT / "src" / "practice" / "catalog.ts"
EXECUTION = ROOT / "src" / "practice" / "execution.ts"
WORKFLOW = ROOT / "harness" / "workflows" / "PRACTICE_WORKBENCH.md"
SKILL = ROOT / "harness" / "skills" / "runner-adapter" / "SKILL.md"

REQUIRED_LANGUAGES = {"python", "rust", "sql", "c", "javascript", "typescript", "java", "lua"}
REQUIRED_FACETS = {"understand", "implement", "test", "explain", "docs"}
REQUIRED_STATUSES = {"not-run", "passed", "failed", "compile-error", "runtime-error", "timeout", "unsupported", "host-error"}
FORBIDDEN_UI_EXECUTION = ("eval(", "new Function", "child_process", "execSync(", "spawnSync(")


def fail(message: str) -> None:
    raise AssertionError(message)


def load(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing required workbench file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    spec = load(SPEC)
    packet = load(PACKET_CONTRACT)
    package = load(PACKAGE)

    if spec.get("schema") != "study-syndicate/practice-workbench/v1":
        fail("unexpected workbench schema")

    ui = spec.get("uiContract") or {}
    if ui.get("premiseFirst") is not True or ui.get("sessionConfiguration") != "modal":
        fail("workbench must be premise-first and modal-configured")
    if ui.get("workspace") != "draggable-panels" or ui.get("textFallback") != "textarea-notepad":
        fail("workbench must preserve draggable panels and text fallback")

    facets = {item.get("id") for item in spec.get("facets") or []}
    if facets != REQUIRED_FACETS:
        fail(f"practice facets drifted: {sorted(facets)}")

    languages = spec.get("languages") or []
    ids = {item.get("id") for item in languages}
    if ids != REQUIRED_LANGUAGES:
        fail(f"language registry drifted: {sorted(ids)}")
    if len(languages) != len(ids):
        fail("language ids must be unique")
    for language in languages:
        runner = language.get("runner") or {}
        for key in ("id", "kind", "status", "exceptionModel"):
            if not runner.get(key):
                fail(f"language {language.get('id')} missing runner {key}")

    lua = next(item for item in languages if item["id"] == "lua")
    if lua["runner"].get("kind") != "embedded-host" or "host catches" not in lua["runner"].get("exceptionModel", ""):
        fail("Lua must explicitly model guest error -> host catch")

    boundary = spec.get("executionBoundary") or {}
    if set(boundary.get("normalizedStatuses") or []) != REQUIRED_STATUSES:
        fail("normalized execution statuses drifted")
    invariants = "\n".join(boundary.get("invariants") or [])
    for phrase in ("Never infer runner availability", "finite timeout", "React event loop", "eval or new Function"):
        if phrase not in invariants:
            fail(f"execution boundary missing invariant: {phrase}")

    layout = spec.get("panelLayout") or {}
    if layout.get("draggable") is not True or layout.get("defaultOrder") != ["premise", "workspace", "feedback"]:
        fail("panel layout must default premise -> workspace -> feedback and remain draggable")

    tracks = {item.get("id"): item for item in spec.get("sourceTracks") or []}
    if tracks.get("two-sum", {}).get("starterPolicy") != "packet-specific":
        fail("Two Sum must retain a packet-specific starter policy")
    if tracks.get("arrays-roadmap", {}).get("starterPolicy") != "neutral-empty-until-packet":
        fail("arrays catalog must use neutral starters until each exercise owns a packet")
    for track_id in ("sql-foundations", "rust-foundations"):
        if tracks.get(track_id, {}).get("starterPolicy") != "track-neutral-comment":
            fail(f"{track_id} must use a track-neutral starter")

    gate = packet.get("uiGate") or {}
    if gate.get("status") != "foundation-ready":
        fail("problem packet UI gate must be foundation-ready before browser UI ships")
    if "renderer" not in gate.get("rule", "").lower():
        fail("problem packet UI gate must constrain the UI to renderer semantics")

    scripts = package.get("scripts") or {}
    for script in ("dev", "build", "lint", "validate:workbench", "test:workbench"):
        if not scripts.get(script):
            fail(f"package.json missing {script} script")

    source_paths = [APP, MODAL, CATALOG, EXECUTION, WORKFLOW, SKILL]
    for path in source_paths:
        if not path.is_file():
            fail(f"missing workbench surface: {path.relative_to(ROOT)}")

    app = APP.read_text(encoding="utf-8")
    modal = MODAL.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    all_src = "\n".join(path.read_text(encoding="utf-8") for path in (APP, MODAL, CATALOG, EXECUTION))

    for literal in ("draggable", "onDrop", "premise-panel", "workspace-panel", "feedback-panel", "anchor.remove()", "URL.revokeObjectURL(url), 1000"):
        if literal not in app:
            fail(f"App missing required UI mechanic: {literal}")
    for literal in ('role="dialog"', "Study target", "Facet", "Language / environment", "Study mode", "handleTargetChange", "masteryBlocked && draft.mode === 'mastery'"):
        if literal not in modal:
            fail(f"modal missing session safety/control: {literal}")
    for authority in ("harness/problems/two-sum.v1.json", "content/software/arrays-mastery.v1.json", "content/software/sql-rust-foundations.v1.json"):
        if authority not in catalog:
            fail(f"catalog must import canonical study authority: {authority}")

    if "neutralCatalogStarters" not in catalog:
        fail("arrays exercise catalog must define a neutral starter surface")
    array_section = catalog.split("function arrayTargets", 1)[1].split("export const practiceTargets", 1)[0]
    if "twoSumStarters" in array_section:
        fail("arrays catalog must not leak Two Sum-specific starters into unrelated exercises")
    if "starterByLanguage: neutralCatalogStarters" not in array_section:
        fail("arrays catalog must bind neutral starters explicitly")

    for forbidden in FORBIDDEN_UI_EXECUTION:
        if forbidden in all_src:
            fail(f"browser UI contains forbidden direct execution primitive: {forbidden}")

    print(
        "practice workbench validation PASS: "
        f"{len(languages)} languages, {len(facets)} facets, "
        f"{len(spec.get('sourceTracks') or [])} source tracks, host-safe execution boundary"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, KeyError, TypeError, IndexError) as exc:
        print(f"practice workbench validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
