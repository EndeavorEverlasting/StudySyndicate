#!/usr/bin/env python3
"""Render guided problem packets, give bounded hints/docs, and check learner attempts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "harness" / "problems"


def load_problem(problem_id: str) -> dict:
    path = PROBLEMS / f"{problem_id}.v1.json"
    if not path.is_file():
        available = ", ".join(
            sorted(
                p.name.removesuffix(".v1.json")
                for p in PROBLEMS.glob("*.v1.json")
                if p.name != "problem-packet-contract.v1.json"
            )
        )
        raise ValueError(f"unknown problem {problem_id!r}; available: {available or 'none'}")
    spec = json.loads(path.read_text(encoding="utf-8"))
    if spec.get("schema") != "study-syndicate/problem-packet/v1" or spec.get("id") != problem_id:
        raise ValueError(f"invalid problem packet: {path.relative_to(ROOT)}")
    return spec


def render_problem(spec: dict, mode: str, comment_format: bool = False) -> str:
    example = spec["example"]
    help_rules = {
        "guided": "Hints, examples, documentation, and executable feedback are allowed. This is a learning rep, not mastery proof.",
        "docs-assisted": "Attempt first. Official documentation may then be used for syntax/API facts; record what you consulted.",
        "mastery": "Do not use hints, AI, or solution lookup. Use the premise and tests only, then explain your reasoning.",
    }
    lines = [
        f"# {spec['title']} — {mode} problem packet",
        "",
        "## Premise",
        spec["premise"],
        "",
        "## Inputs",
    ]
    lines.extend(f"- {item['name']} ({item['type']}): {item['meaning']}" for item in spec["inputs"])
    lines.extend(["", "## What to return", spec["output"], "", "## Guarantees"])
    lines.extend(f"- {item}" for item in spec["guarantees"])
    lines.extend(
        [
            "",
            "## Example",
            f"nums = {example['nums']}",
            f"target = {example['target']}",
            f"output = {example['output']}",
            f"why: {example['explanation']}",
            "",
            "## Help allowed in this mode",
            help_rules[mode],
            "",
            "## Your first goal",
            spec["attemptContract"]["guidedGoal"]
            if mode != "mastery"
            else "Solve from the stated contract, explain correctness and complexity, and pass the checker.",
            "",
            "## Checkpoints",
        ]
    )
    for number, item in enumerate(spec["guidedCheckpoints"], start=1):
        if mode == "mastery" and item["id"] not in {"restate", "implement"}:
            continue
        lines.extend([f"{number}. {item['prompt']}", "   YOUR RESPONSE:", ""])
    lines.extend(
        [
            "## Feedback",
            f"- Check your file: {spec['feedback']['checkCommand']}",
            f"- Ask for one graduated hint: {spec['feedback']['hintCommand']}",
            f"- Find allowed official documentation: {spec['feedback']['docsCommand']}",
            "",
            "## Starter",
            spec["attemptContract"]["signature"],
            "    # Write the simplest correct version you can explain.",
            "    raise NotImplementedError",
            "",
        ]
    )

    if not comment_format:
        return "\n".join(lines)

    rendered: list[str] = []
    starter_seen = False
    for line in lines:
        if line == spec["attemptContract"]["signature"]:
            starter_seen = True
            rendered.extend(["", line])
            continue
        if starter_seen:
            if line.startswith("    "):
                rendered.append(line)
                continue
            if line == "":
                rendered.append("")
                starter_seen = False
                continue
        if line.startswith("# "):
            rendered.append(f"# {line[2:]}")
        else:
            rendered.append(f"# {line}" if line else "#")
    return "\n".join(rendered).rstrip() + "\n"


def cmd_render(args: argparse.Namespace) -> int:
    try:
        spec = load_problem(args.problem)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    rendered = render_problem(spec, args.mode, comment_format=args.format == "comments")
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output)
    else:
        print(rendered, end="" if rendered.endswith("\n") else "\n")
    return 0


def cmd_hint(args: argparse.Namespace) -> int:
    try:
        spec = load_problem(args.problem)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    hints = {item["level"]: item for item in spec["hints"]}
    hint = hints.get(args.level)
    if not hint:
        print(f"hint level must be one of: {', '.join(map(str, sorted(hints)))}", file=sys.stderr)
        return 2
    print(f"Hint {hint['level']} — {hint['name']}")
    print(hint["text"])
    print("Use only this hint, make another attempt, then run the checker again.")
    return 0


def cmd_docs(args: argparse.Namespace) -> int:
    try:
        spec = load_problem(args.problem)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    docs = spec["documentation"]
    print(docs["policy"])
    print()
    for item in docs["topics"]:
        print(f"Need: {item['need']}")
        print(f"Search: {item['search']}")
        print(f"Official: {item['officialUrl']}")
        print()
    return 0


def load_attempt(path: Path):
    module_spec = importlib.util.spec_from_file_location("studysyndicate_attempt", path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"could not load Python file: {path}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def pair_error(result, nums: list[int], target: int) -> str | None:
    if not isinstance(result, (list, tuple)) or len(result) != 2:
        return "return exactly two indices in a list or tuple"
    left, right = result
    if not isinstance(left, int) or not isinstance(right, int):
        return "both returned indices must be integers"
    if left == right:
        return "the same index was returned twice"
    if not (0 <= left < len(nums) and 0 <= right < len(nums)):
        return "one or both returned indices are out of range"
    if nums[left] + nums[right] != target:
        return f"nums[{left}] + nums[{right}] does not equal target"
    return None


def cmd_check(args: argparse.Namespace) -> int:
    try:
        spec = load_problem(args.problem)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        print(f"attempt file not found: {path}", file=sys.stderr)
        return 2

    try:
        module = load_attempt(path)
    except Exception as exc:
        print(f"[FAIL] could not import attempt: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    function_name = spec["attemptContract"]["functionName"]
    solver = getattr(module, function_name, None)
    if not callable(solver):
        print(f"[FAIL] define callable `{function_name}(nums, target)` in {path.name}", file=sys.stderr)
        return 1

    for case in spec["validationCases"]:
        nums = list(case["nums"])
        snapshot = list(nums)
        try:
            result = solver(nums, case["target"])
        except Exception as exc:
            print(f"[FAIL] {case['name']}: {type(exc).__name__}: {exc}", file=sys.stderr)
            print("Next: fix this error and rerun the checker. If blocked, request hint level 1.", file=sys.stderr)
            return 1
        if nums != snapshot:
            print(f"[FAIL] {case['name']}: the attempt mutated nums", file=sys.stderr)
            return 1
        error = pair_error(result, nums, case["target"])
        if error:
            print(f"[FAIL] {case['name']}: {error}; returned {result!r}", file=sys.stderr)
            return 1
        print(f"[PASS] {case['name']}: returned {list(result)}")

    print(
        f"attempt feedback PASS: {len(spec['validationCases'])} cases. "
        "A passing guided attempt is evidence of correctness, not yet mastery."
    )
    return 0


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render", help="render a self-contained problem packet")
    render.add_argument("problem")
    render.add_argument("--mode", choices=("guided", "docs-assisted", "mastery"), default="guided")
    render.add_argument("--format", choices=("text", "comments"), default="text")
    render.add_argument("--output")
    render.set_defaults(func=cmd_render)

    hint = sub.add_parser("hint", help="reveal exactly one graduated hint")
    hint.add_argument("problem")
    hint.add_argument("--level", type=int, required=True)
    hint.set_defaults(func=cmd_hint)

    docs = sub.add_parser("docs", help="show bounded official-documentation lookups")
    docs.add_argument("problem")
    docs.set_defaults(func=cmd_docs)

    check = sub.add_parser("check", help="run executable feedback against a learner attempt")
    check.add_argument("problem")
    check.add_argument("path")
    check.set_defaults(func=cmd_check)

    return parser


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
