#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_REPOSITORY = "EndeavorEverlasting/StudySyndicate"
EXPECTED_BASE = "main"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class PromotionError(ValueError):
    pass


def fail(message: str) -> None:
    raise PromotionError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read JSON {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON document {path} must be an object")
    return value


def validate_candidate(
    payload: dict[str, Any],
    *,
    expected_head: str,
    repository: str = EXPECTED_REPOSITORY,
    base: str = EXPECTED_BASE,
) -> dict[str, str]:
    if not SHA_RE.fullmatch(expected_head):
        fail("expected head SHA must be exactly 40 lowercase hexadecimal characters")
    if repository != EXPECTED_REPOSITORY:
        fail(f"unauthorized repository target: {repository!r}")
    if base != EXPECTED_BASE:
        fail(f"unauthorized base branch: {base!r}")
    if payload.get("state") != "open":
        fail("pull request must still be open")
    if payload.get("draft") is True:
        fail("pull request must be ready for review before promotion")

    head = payload.get("head") or {}
    base_payload = payload.get("base") or {}
    head_sha = str(head.get("sha") or "")
    head_repo = str((head.get("repo") or {}).get("full_name") or "")
    base_ref = str(base_payload.get("ref") or "")
    base_sha = str(base_payload.get("sha") or "")

    if head_sha != expected_head:
        fail(f"candidate head moved: expected {expected_head}, found {head_sha or '<missing>'}")
    if head_repo != repository:
        fail(f"pull request head repository is not authorized: {head_repo!r}")
    if base_ref != base:
        fail(f"pull request base drifted: expected {base!r}, found {base_ref!r}")
    if not SHA_RE.fullmatch(base_sha):
        fail("pull request base SHA is missing or malformed")

    return {
        "repository": repository,
        "baseRef": base_ref,
        "baseSha": base_sha,
        "headSha": head_sha,
        "state": "open",
    }


def write_receipt(
    *,
    candidate: dict[str, Any],
    application: dict[str, Any],
    merge: dict[str, Any],
    run_id: str,
    actor: str,
    event: str,
    output: Path,
    contained: bool = False,
) -> dict[str, Any]:
    normalized = validate_candidate(
        candidate,
        expected_head=str((candidate.get("head") or {}).get("sha") or ""),
    )
    merge_sha = str(merge.get("sha") or "")
    if merge.get("merged") is not True or not SHA_RE.fullmatch(merge_sha):
        fail("merge response does not prove a successful merge SHA")
    dist_sha = str(application.get("distSha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", dist_sha):
        fail("application E2E receipt is missing a dist SHA-256")

    payload = {
        "schema": "studysyndicate.promotion-receipt.v1",
        "provider": "github-actions",
        "runId": str(run_id),
        "event": event,
        "actor": actor,
        "repository": normalized["repository"],
        "target": normalized["baseRef"],
        "baseSha": normalized["baseSha"],
        "candidateHeadSha": normalized["headSha"],
        "requiredGates": {
            "harnessFull": "success",
            "applicationHttpSmoke": "success",
        },
        "applicationArtifact": {
            "distSha256": dist_sha,
            "receiptSchema": application.get("schema"),
        },
        "mergeSha": merge_sha,
        "postPromotionContainment": "success" if contained else "pending-provider-check",
        "proofCeiling": {
            "remoteIntegrated": True,
            "devCheckoutCurrent": False,
            "prodPathCurrent": False,
            "entrypointProvedOnWindows": False,
            "browserInteractionBeyondHttpSmoke": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def cmd_check(args: argparse.Namespace) -> int:
    payload = load_json(args.input)
    normalized = validate_candidate(
        payload,
        expected_head=args.expected_head,
        repository=args.repository,
        base=args.base,
    )
    print(json.dumps(normalized, sort_keys=True))
    return 0


def cmd_receipt(args: argparse.Namespace) -> int:
    payload = write_receipt(
        candidate=load_json(args.candidate),
        application=load_json(args.application),
        merge=load_json(args.merge),
        run_id=args.run_id,
        actor=args.actor,
        event=args.event,
        output=args.output,
        contained=args.contained,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="StudySyndicate exact-candidate promotion policy helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check-candidate")
    check.add_argument("--input", type=Path, required=True)
    check.add_argument("--expected-head", required=True)
    check.add_argument("--repository", default=EXPECTED_REPOSITORY)
    check.add_argument("--base", default=EXPECTED_BASE)
    check.set_defaults(func=cmd_check)

    receipt = subparsers.add_parser("write-receipt")
    receipt.add_argument("--candidate", type=Path, required=True)
    receipt.add_argument("--application", type=Path, required=True)
    receipt.add_argument("--merge", type=Path, required=True)
    receipt.add_argument("--run-id", required=True)
    receipt.add_argument("--actor", required=True)
    receipt.add_argument("--event", required=True)
    receipt.add_argument("--output", type=Path, required=True)
    receipt.add_argument("--contained", action="store_true")
    receipt.set_defaults(func=cmd_receipt)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PromotionError, OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
        print(f"promotion FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
