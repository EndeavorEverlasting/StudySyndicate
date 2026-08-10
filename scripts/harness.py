#!/usr/bin/env python3
"""StudySyndicate operational harness CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
MANIFEST = HARNESS / "harness-manifest.v1.json"
VALIDATION = HARNESS / "validation-manifest.v1.json"
ARTIFACTS = HARNESS / "artifact-registry.v1.json"
PARALLAX = HARNESS / "sources" / "parallaxport-claims.v1.json"
FODDER_REPORT = HARNESS / "reports" / "PARALLAXPORT_STUDY_FODDER.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_fodder(spec: dict) -> str:
    categories: dict[str, list[dict]] = {}
    for claim in spec["claims"]:
        categories.setdefault(claim["category"], []).append(claim)
    names = {
        "programming-languages": "Programming Languages",
        "data-science-analytics": "Data Science & Analytics",
        "web-development": "Web Development",
        "databases": "Databases",
    }
    lines = [
        "# ParallaxPort Study Fodder",
        "",
        f"Source snapshot: **{spec['displayName']}** on **{spec['snapshotDate']}**.",
        "",
        "> Public presentation is a study-priority signal, not proof of mastery.",
        "",
        "Use `python scripts/harness.py start guided-study` when a target feels too difficult to begin.",
        "",
    ]
    for category in ("programming-languages", "data-science-analytics", "web-development", "databases"):
        lines.extend([f"## {names[category]}", ""])
        for claim in categories.get(category, []):
            targets = ", ".join(f"`{target}`" for target in claim["studyTargets"])
            lines.extend(
                [
                    f"### {claim['claim']}",
                    f"- State: `{claim['initialState']}`",
                    f"- Study targets: {targets}",
                    f"- First practice: {claim['firstPractice']}",
                    "",
                ]
            )
    lines.extend(
        [
            "## How to use this report",
            "",
            "1. Pick one claim.",
            "2. Choose `guided`, `docs-assisted`, or `mastery`.",
            "3. Perform one bounded rep.",
            "4. Run the relevant validator/test.",
            "5. Record what you could do from memory, what help you used, and the next retrieval target.",
            "",
            "Regenerate after an intentional source snapshot update:",
            "",
            "```bash",
            "python scripts/harness.py study-fodder",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def cmd_inspect(_: argparse.Namespace) -> int:
    manifest = load_json(MANIFEST)
    validation = load_json(VALIDATION)
    artifacts = load_json(ARTIFACTS)
    sources = load_json(PARALLAX)
    print("StudySyndicate harness")
    print(f"entrypoint={manifest['entrypoint']}")
    print(f"governance={manifest['governanceAuthority']}")
    print(f"workflows={len(manifest['workflows'])}")
    print(f"validation_checks={len(validation['checks'])}")
    print(f"artifacts={len(artifacts['artifacts'])}")
    print(f"public_claims={len(sources['claims'])} source={sources['displayName']}")
    print("next=python scripts/harness.py workflows")
    return 0


def cmd_workflows(_: argparse.Namespace) -> int:
    manifest = load_json(MANIFEST)
    for workflow in manifest["workflows"]:
        print(f"{workflow['id']}: {workflow['trigger']}")
        print(f"  {workflow['entrypoint']}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    manifest = load_json(MANIFEST)
    match = next((item for item in manifest["workflows"] if item["id"] == args.workflow), None)
    if not match:
        print(f"unknown workflow: {args.workflow}", file=sys.stderr)
        return 2
    path = ROOT / match["entrypoint"]
    print(path.read_text(encoding="utf-8"))
    return 0


def run_check(check: dict) -> int:
    argv = check["argv"]
    print(f"[RUN] {check['id']}: {' '.join(argv)}", flush=True)
    completed = subprocess.run(argv, cwd=ROOT)
    if completed.returncode:
        print(f"[FAIL] {check['id']} exit={completed.returncode}", file=sys.stderr)
        return completed.returncode
    print(f"[PASS] {check['id']}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    spec = load_json(VALIDATION)
    tiers = {"quick"} if args.level == "quick" else {"quick", "full"}
    for check in spec["checks"]:
        if check["tier"] not in tiers:
            continue
        code = run_check(check)
        if code:
            return code
    print(f"harness validation PASS level={args.level}")
    return 0


def cmd_study_fodder(args: argparse.Namespace) -> int:
    rendered = render_fodder(load_json(PARALLAX))
    if args.check:
        current = FODDER_REPORT.read_text(encoding="utf-8")
        if current != rendered:
            print(
                "ParallaxPort study-fodder report is stale; run "
                "`python scripts/harness.py study-fodder`.",
                file=sys.stderr,
            )
            return 1
        print("ParallaxPort study-fodder report PASS")
        return 0
    FODDER_REPORT.write_text(rendered, encoding="utf-8")
    print(FODDER_REPORT.relative_to(ROOT))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="summarize harness authorities and counts")
    inspect.set_defaults(func=cmd_inspect)

    workflows = sub.add_parser("workflows", help="list workflow triggers and entrypoints")
    workflows.set_defaults(func=cmd_workflows)

    start = sub.add_parser("start", help="print one workflow for immediate use")
    start.add_argument("workflow")
    start.set_defaults(func=cmd_start)

    validate = sub.add_parser("validate", help="run registered validations")
    validate.add_argument("--level", choices=("quick", "full"), default="quick")
    validate.set_defaults(func=cmd_validate)

    fodder = sub.add_parser("study-fodder", help="generate/check ParallaxPort study-fodder report")
    fodder.add_argument("--check", action="store_true")
    fodder.set_defaults(func=cmd_study_fodder)

    return p


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
