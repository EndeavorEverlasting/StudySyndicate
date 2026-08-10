#!/usr/bin/env python3
"""Validate StudySyndicate's local repository work ledger and adoption metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from repo_ledger import LedgerError, parse_ledger, validate_tasks

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / ".ai" / "WORK_QUEUE.md"
ADOPTION = ROOT / ".ai" / "repository-work-ledger-adoption.json"
POLICY = ROOT / ".ai" / "repository-work-ledger.policy.json"
PORTABLE_OWNER = "EndeavorEverlasting/BlacksmithGuild"
PORTABLE_VERSION = "RepoLedgerInteroperability.v1"
PORTABLE_COMMIT = "429237aa41d8712d71859865c9be407ca23d8580"
AGENTSWITCHBOARD_FRONTIER_COMMIT = "b090637be810b2b25c35a11c299b4f2d9cc90ca3"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    for path in (LEDGER, ADOPTION, POLICY):
        if not path.is_file():
            fail(f"missing ledger artifact: {path.relative_to(ROOT)}")

    adoption = json.loads(ADOPTION.read_text(encoding="utf-8"))
    if adoption.get("schema") != "RepoLedgerAdoption.v1":
        fail("adoption schema must be RepoLedgerAdoption.v1")
    if adoption.get("repository") != "EndeavorEverlasting/StudySyndicate":
        fail("adoption repository mismatch")
    if adoption.get("adoptionStatus") != "implemented":
        fail("adoptionStatus must be implemented")
    contract = adoption.get("contract") or {}
    if contract != {
        "repository": PORTABLE_OWNER,
        "commit": PORTABLE_COMMIT,
        "path": ".tbg/workflows/repo-ledger-interoperability.contract.json",
        "version": PORTABLE_VERSION,
    }:
        fail("portable contract authority/version/pin mismatch")
    donor = adoption.get("donor") or {}
    if donor.get("repository") != "EndeavorEverlasting/AxTask" or donor.get("commit") != "9351c952b057ae4520b1ea0d388e1d8908f4c093":
        fail("donor provenance mismatch")
    local = adoption.get("local") or {}
    if local != {
        "ledgerPath": ".ai/WORK_QUEUE.md",
        "validatorPath": "scripts/validate-repo-ledger.py",
        "taskNamespace": "SSQ",
        "format": "markdown",
    }:
        fail("local adoption paths/namespace mismatch")
    authority = adoption.get("authority") or {}
    if authority.get("runtimeOwner") != "EndeavorEverlasting/StudySyndicate":
        fail("runtime authority must remain StudySyndicate")
    if authority.get("contractOwner") != PORTABLE_OWNER or authority.get("noCircularAuthority") is not True:
        fail("portable authority boundary is invalid")
    if adoption.get("proofCeiling") != "repository_harness_only":
        fail("adoption proof ceiling must remain repository_harness_only")

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if policy.get("schema") != "studysyndicate.repository-work-ledger.profile.v1":
        fail("unexpected local policy schema")
    if policy.get("version") != "1.0.0":
        fail("unexpected local policy version")
    if policy.get("portableContract") != {"repository": PORTABLE_OWNER, "version": PORTABLE_VERSION, "commit": PORTABLE_COMMIT}:
        fail("policy portable contract pin mismatch")
    strengthening = policy.get("referenceOnlyStrengthening") or {}
    if strengthening.get("repository") != "EndeavorEverlasting/AgentSwitchboard":
        fail("reference-only strengthening owner mismatch")
    if strengthening.get("commit") != AGENTSWITCHBOARD_FRONTIER_COMMIT:
        fail("reference-only frontier source must use exact durable commit")
    profile = ((policy.get("local") or {}).get("executionProfile") or {})
    if profile.get("requiredField") != "Work class":
        fail("local execution profile must require Work class")
    if profile.get("classes") != ["BOUNDED", "UNBOUNDED"]:
        fail("local execution profile classes mismatch")
    if profile.get("routesAreDerived") is not True:
        fail("frontier routes must be derived, not stored mutable state")

    tasks = parse_ledger(LEDGER)
    errors = validate_tasks(tasks, ROOT)
    if errors:
        fail("; ".join(errors))

    print(
        "repository ledger validation PASS: "
        f"{len(tasks)} task(s), portable={PORTABLE_VERSION}@{PORTABLE_COMMIT[:12]}, "
        "local_profile=1.0.0, frontier=deterministic"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, LedgerError, json.JSONDecodeError, OSError) as exc:
        print(f"repository ledger validation FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
