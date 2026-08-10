#!/usr/bin/env python3
"""Return the smallest deterministic StudySyndicate work frontier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from repo_ledger import (
    LedgerError,
    actionable_tasks,
    empty_payload,
    parse_ledger,
    render_compact,
    render_prompt,
    select_frontier,
    task_payload,
    validate_tasks,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / ".ai" / "WORK_QUEUE.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--prompt", action="store_true")
    args = parser.parse_args()

    tasks = parse_ledger(args.ledger)
    errors = validate_tasks(tasks, ROOT if args.ledger.resolve() == DEFAULT_LEDGER.resolve() else None)
    if errors:
        raise LedgerError("; ".join(errors))

    selected = actionable_tasks(tasks) if args.all else [select_frontier(tasks)]
    selected = [task for task in selected if task is not None]

    if args.all:
        payload = {
            "schema": "studysyndicate.repository-work-ledger.frontier.v1",
            "status": "ready" if selected else "empty",
            "route": "MULTI" if selected else "EMPTY",
            "tasks": [task_payload(task)["task"] | {"route": task_payload(task)["route"]} for task in selected],
        }
        print(json.dumps(payload, indent=2) if args.as_json else "\n\n".join(render_compact(task) for task in selected) or render_compact(None))
        return 0

    task = selected[0] if selected else None
    if args.prompt:
        print(render_prompt(task))
    elif args.as_json:
        print(json.dumps(task_payload(task) if task else empty_payload(), indent=2))
    else:
        print(render_compact(task))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LedgerError, OSError) as exc:
        print(f"repository ledger frontier FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
