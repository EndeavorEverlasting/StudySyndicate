#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "harness" / "promotion-contract.v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "promote-main.yml"
PROMOTION = ROOT / "scripts" / "promotion.py"
APP_E2E = ROOT / "scripts" / "application-e2e.py"
TESTS = ROOT / "tests" / "test_promotion_contract.py"

EXPECTED_REPO = "EndeavorEverlasting/StudySyndicate"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("schema") != "study-syndicate/promotion-contract/v1":
        fail("unexpected promotion contract schema")
    if contract.get("repository") != EXPECTED_REPO:
        fail("promotion repository identity drifted")

    target = contract.get("target") or {}
    if target.get("branch") != "main" or target.get("mergeMethod") != "squash":
        fail("promotion target must remain squash -> main")
    if target.get("unauthorizedTargets") != "reject":
        fail("unauthorized promotion targets must fail closed")

    trigger = contract.get("trigger") or {}
    if trigger.get("event") != "pull_request" or trigger.get("activityType") != "ready_for_review":
        fail("promotion authorization must remain the ready_for_review gesture")
    if trigger.get("requiredAuthor") != "repository-owner":
        fail("promotion must remain owner-authorized at this floor")

    gates = contract.get("gates") or []
    gate_map = {item.get("id"): item for item in gates}
    if set(gate_map) != {"harness-full", "application-http-smoke"}:
        fail(f"unexpected promotion gates: {sorted(gate_map)}")
    if gate_map["harness-full"].get("command") != ["python", "scripts/harness.py", "validate", "--level", "full"]:
        fail("promotion must compose the canonical full harness command")
    if gate_map["harness-full"].get("kind") != "harness-e2e":
        fail("full harness proof must remain distinct from application E2E")
    if gate_map["application-http-smoke"].get("command") != [
        "python", "scripts/application-e2e.py", "--receipt", ".promotion/application-e2e.json"
    ]:
        fail("promotion application E2E command drifted")
    if gate_map["application-http-smoke"].get("kind") != "application-e2e":
        fail("application E2E must remain separately classified")
    if any(item.get("classification") != "REQUIRED" for item in gates):
        fail("all promotion gates are REQUIRED at this floor")

    permissions = contract.get("permissions") or {}
    if permissions.get("separateWriteJob") is not True or permissions.get("adminBypassForbidden") is not True:
        fail("promotion write authority must remain separate and may not bypass protection")
    if contract.get("concurrency", {}).get("group") != "studysyndicate-promote-main":
        fail("promotion writer concurrency group drifted")
    if contract.get("concurrency", {}).get("cancelInProgress") is not False:
        fail("promotion writer may not cancel another in-progress writer")

    for path in (WORKFLOW, PROMOTION, APP_E2E, TESTS):
        if not path.is_file():
            fail(f"missing promotion surface: {path.relative_to(ROOT)}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    required_workflow_literals = (
        "types: [ready_for_review]",
        "group: studysyndicate-promote-main",
        "needs: [authorize, validate]",
        "contents: write",
        "pull-requests: write",
        "test \"$ACTOR\" = \"$REPOSITORY_OWNER\"",
        "test \"$HEAD_REPOSITORY\" = \"$REPOSITORY\"",
        "test \"$BASE_REF\" = \"main\"",
        "python scripts/harness.py validate --level full",
        "python scripts/application-e2e.py --receipt .promotion/application-e2e.json",
        "candidate moved after validation",
        "'{merge_method:\"squash\",sha:$sha}'",
        "merge-base --is-ancestor",
        "name: application-e2e-proof",
        "name: promotion-receipt",
    )
    for literal in required_workflow_literals:
        if literal not in workflow:
            fail(f"promotion workflow missing required guard: {literal}")
    for forbidden in ("continue-on-error", "--admin", "push --force", "reset --hard"):
        if forbidden in workflow:
            fail(f"promotion workflow contains forbidden bypass: {forbidden}")

    promotion = PROMOTION.read_text(encoding="utf-8")
    for literal in ("candidate head moved", "unauthorized base branch", "head repository is not authorized", "promotion-receipt.v1"):
        if literal not in promotion:
            fail(f"promotion policy helper missing fail-closed behavior: {literal}")

    app = APP_E2E.read_text(encoding="utf-8")
    for literal in ("command = [npm, \"run\", \"preview\"", "127.0.0.1", "distSha256", "browserInteraction"):
        if literal not in app:
            fail(f"application E2E missing real-entrypoint proof marker: {literal}")

    print("promotion validation PASS: owner-ready gesture -> exact SHA -> full harness -> application HTTP E2E -> expected-head squash merge -> containment receipt")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, KeyError, TypeError) as exc:
        print(f"promotion validation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(1)
