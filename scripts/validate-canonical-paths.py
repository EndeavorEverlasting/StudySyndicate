#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "harness" / "canonical-paths.v1.json"
RESOLVER = ROOT / "scripts" / "Resolve-StudySyndicateRepo.ps1"
WORKFLOW = ROOT / "harness" / "workflows" / "REPO_LOCATION_RECOVERY.md"

REPOSITORY = "EndeavorEverlasting/StudySyndicate"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("schema") != "study-syndicate/canonical-paths/v1":
        fail("unexpected canonical-path schema")
    if contract.get("repository") != REPOSITORY:
        fail("canonical-path contract repository identity drifted")

    profiles = {item["key"]: item for item in contract.get("profiles") or []}
    if set(profiles) != {"windows-desktop-dev", "github-actions"}:
        fail(f"unexpected canonical-path profiles: {sorted(profiles)}")

    windows = profiles["windows-desktop-dev"]
    dev = windows["development"]
    if dev.get("base") != "known-folder:Desktop" or dev.get("segments") != ["Dev", "StudySyndicate"]:
        fail("Windows development path must resolve Desktop Known Folder -> Dev -> StudySyndicate")
    if dev.get("classification") != "CLONE" or dev.get("mutable") is not True:
        fail("Windows canonical development role must be one mutable CLONE")

    use = windows["use"]
    if use.get("relation") != "same-as-development":
        fail("Windows use path must explicitly share the canonical development checkout at this floor")
    if use.get("entrypoint") != ["npm", "run", "dev"]:
        fail("Windows operator entrypoint must remain npm run dev")
    if use.get("productionDeployment") != "none-separate-at-this-floor":
        fail("remote integration must not masquerade as a separate local deployment")

    worktree = windows["worktree"]
    if worktree.get("base") != "known-folder:Desktop" or worktree.get("segments") != ["Dev", "StudySyndicate-worktrees"]:
        fail("parallel worktrees must stay under Desktop/Dev/StudySyndicate-worktrees")
    if worktree.get("nestedBelowDevelopment") is not False:
        fail("worktree root must not be nested inside the canonical mutable checkout")

    policy = contract.get("driftPolicy") or {}
    for key in ("forbidSilentFallback", "forbidSecondMutableCheckoutWhenCanonicalUsable", "preserveDirtyUnpushedUniqueWork"):
        if policy.get(key) is not True:
            fail(f"drift policy must enforce {key}")

    resolver = RESOLVER.read_text(encoding="utf-8")
    required_resolver_literals = (
        "harness/canonical-paths.v1.json",
        "Environment+SpecialFolder]::Desktop",
        "NONCANONICAL + PRESERVE",
        "CANONICAL + PROVED",
        "OneDriveConsumer",
        "OneDriveCommercial",
        "exit 2",
    )
    for literal in required_resolver_literals:
        if literal not in resolver:
            fail(f"resolver missing required behavior marker: {literal}")

    forbidden = (
        r"Join-Path\s+\$HOME\s+['\"]Desktop",
        r"C:\\Users\\",
        r"Desktop[/\\]dev[/\\]StudySyndicate",
        r"\$HOME[/\\]dev[/\\]StudySyndicate",
    )
    for pattern in forbidden:
        if re.search(pattern, resolver, flags=re.IGNORECASE):
            fail(f"resolver contains noncanonical fallback or hard-coded user path: {pattern}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for literal in ("canonical-paths.v1.json", "Environment.SpecialFolder", "NONCANONICAL + PRESERVE", "StudySyndicate-worktrees"):
        if literal not in workflow:
            fail(f"repo-location workflow missing canonical path doctrine marker: {literal}")

    print("canonical path validation PASS: Windows Desktop Known Folder -> Dev/StudySyndicate, same-path local use, sibling worktree root, fail-closed drift")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, KeyError, TypeError) as exc:
        print(f"canonical path validation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(1)
