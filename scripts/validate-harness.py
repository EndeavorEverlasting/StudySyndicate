#!/usr/bin/env python3
"""Validate StudySyndicate harness completeness and cross-file contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"

MANIFEST = HARNESS / "harness-manifest.v1.json"
ARTIFACTS = HARNESS / "artifact-registry.v1.json"
VALIDATION = HARNESS / "validation-manifest.v1.json"
SOURCE = HARNESS / "sources" / "parallaxport-claims.v1.json"
README = ROOT / "README.md"

EXPECTED_COMPONENTS = {
    "codebaseMap",
    "workflowSpecs",
    "artifactRegistry",
    "validators",
    "hooks",
    "skills",
    "operatorReports",
    "sourceAdapters",
}
EXPECTED_CLAIMS = {
    "Python", "JavaScript", "TypeScript", "Java", "C",
    "Pandas", "NumPy", "Matplotlib",
    "React", "Django", "Flask", "Node.js",
    "PostgreSQL", "MySQL", "SQLite",
}
REQUIRED_FULL_COMMANDS = {
    ("bash", "scripts/validate-governance.sh"),
    ("python", "scripts/validate-pmp-doctrine.py"),
    ("python", "scripts/validate-software-foundations.py"),
    ("python", "scripts/validate-arrays-mastery.py"),
    ("python", "tests/test_two_sum.py"),
    ("python", "scripts/validate-multimodal-media.py"),
    ("python", "scripts/test-media-bundle.py"),
    ("python", "scripts/validate-mental-math-content.py"),
    ("git", "diff", "--check"),
}
FORBIDDEN_SOURCE_KEYS = {"secret", "token", "password", "apiKey", "privateKey", "credential"}


def fail(message: str) -> None:
    raise AssertionError(message)


def load(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def relative_paths(component_map: dict) -> list[str]:
    paths: list[str] = []
    for values in component_map.values():
        if not isinstance(values, list) or not values:
            fail("every harness component category must contain at least one path")
        paths.extend(values)
    return paths


def assert_tracked(paths: list[str]) -> None:
    if not (ROOT / ".git").exists():
        return
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *paths],
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        fail(f"harness component not tracked: {completed.stderr.strip()}")


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def main() -> int:
    manifest = load(MANIFEST)
    artifacts = load(ARTIFACTS)
    validation = load(VALIDATION)
    source = load(SOURCE)

    if manifest.get("schema") != "study-syndicate/harness/v1":
        fail("unexpected harness schema")
    if manifest.get("governanceAuthority") != "AGENTS.md":
        fail("harness must point to AGENTS.md rather than duplicate governance")
    components = manifest.get("components")
    if set(components or {}) != EXPECTED_COMPONENTS:
        fail(f"harness component categories mismatch: {sorted((components or {}).keys())}")

    component_paths = relative_paths(components)
    for rel in component_paths:
        if not (ROOT / rel).is_file():
            fail(f"missing harness component: {rel}")
    assert_tracked(component_paths)

    workflows = manifest.get("workflows") or []
    workflow_ids = [item.get("id") for item in workflows]
    if workflow_ids != ["guided-study", "public-claim-to-study", "repo-change"]:
        fail(f"workflow order/ids drifted: {workflow_ids}")
    for workflow in workflows:
        if not (ROOT / workflow["entrypoint"]).is_file():
            fail(f"workflow entrypoint missing: {workflow['entrypoint']}")
        for skill in workflow.get("skillRefs", []):
            if not (ROOT / skill).is_file():
                fail(f"workflow skill missing: {skill}")

    modes = manifest.get("studyModes") or {}
    if list(modes) != ["guided", "docs-assisted", "mastery"]:
        fail("study modes must preserve guided -> docs-assisted -> mastery")

    if artifacts.get("schema") != "study-syndicate/artifact-registry/v1":
        fail("unexpected artifact registry schema")
    artifact_items = artifacts.get("artifacts") or []
    artifact_ids = [item.get("id") for item in artifact_items]
    if len(artifact_ids) != len(set(artifact_ids)):
        fail("artifact ids must be unique")
    for item in artifact_items:
        path = item.get("path")
        if item.get("kind", "").startswith("tracked-") and (not path or not (ROOT / path).is_file()):
            fail(f"tracked artifact path missing: {path}")

    if validation.get("schema") != "study-syndicate/validation-manifest/v1":
        fail("unexpected validation manifest schema")
    checks = validation.get("checks") or []
    ids = [item.get("id") for item in checks]
    if len(ids) != len(set(ids)):
        fail("validation check ids must be unique")
    commands = {tuple(item.get("argv") or []) for item in checks if item.get("tier") == "full"}
    missing_commands = REQUIRED_FULL_COMMANDS - commands
    if missing_commands:
        fail(f"full validation missing commands: {sorted(missing_commands)}")
    if not all(item.get("required") is True for item in checks):
        fail("all registered harness checks must be required at this floor")

    if source.get("schema") != "study-syndicate/public-claim-source/v1":
        fail("unexpected public claim source schema")
    if source.get("sourceId") != "parallaxport":
        fail("public claim source must be parallaxport")
    source_keys = set(walk_keys(source))
    if source_keys & FORBIDDEN_SOURCE_KEYS:
        fail(f"source adapter contains forbidden secret-like keys: {sorted(source_keys & FORBIDDEN_SOURCE_KEYS)}")

    claims = source.get("claims") or []
    claim_names = {item.get("claim") for item in claims}
    if claim_names != EXPECTED_CLAIMS:
        fail(f"ParallaxPort public claim snapshot drifted: {sorted(claim_names)}")
    claim_ids = [item.get("id") for item in claims]
    if len(claim_ids) != len(set(claim_ids)):
        fail("public claim ids must be unique")

    target_authorities = source.get("targetAuthorities") or {}
    for target, path in target_authorities.items():
        if not (ROOT / path).is_file():
            fail(f"study target authority missing for {target}: {path}")
    for claim in claims:
        if claim.get("initialState") not in {"exposed", "practicing", "defensible"}:
            fail(f"invalid claim state: {claim}")
        if not claim.get("firstPractice"):
            fail(f"claim missing firstPractice: {claim.get('claim')}")
        for target in claim.get("studyTargets") or []:
            if target not in target_authorities:
                fail(f"claim references unknown study target {target!r}")

    readme = README.read_text(encoding="utf-8")
    for literal in (
        "## Operational Harness",
        "python scripts/harness.py inspect",
        "harness/reports/PARALLAXPORT_STUDY_FODDER.md",
    ):
        if literal not in readme:
            fail(f"README missing harness navigation: {literal}")

    guided = (HARNESS / "workflows" / "GUIDED_STUDY.md").read_text(encoding="utf-8")
    for literal in ("Guided", "Docs-assisted", "Mastery", "Two Sum", "documentation-lookup", "guided-feedback"):
        if literal not in guided:
            fail(f"guided workflow missing {literal!r}")

    hooks = [
        (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8"),
        (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8"),
    ]
    if not all("scripts/harness.py" in hook for hook in hooks):
        fail("tracked hooks must route through the harness CLI")

    print(
        "harness validation PASS: "
        f"{len(component_paths)} component files, "
        f"{len(workflows)} workflows, "
        f"{len(artifact_items)} artifacts, "
        f"{len(checks)} checks, "
        f"{len(claims)} ParallaxPort claims"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, TypeError, KeyError) as exc:
        print(f"harness validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
