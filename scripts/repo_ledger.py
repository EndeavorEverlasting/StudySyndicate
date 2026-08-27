#!/usr/bin/env python3
"""Shared parser and deterministic routing for the StudySyndicate repository ledger."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

STATUSES = ("READY", "CLAIMED", "VERIFY", "REVIEW", "MERGE", "OPERATOR", "BLOCKED", "DONE")
PRIORITIES = ("P0", "P1", "P2", "P3")
WORK_CLASSES = ("BOUNDED", "UNBOUNDED")
PRIORITY_RANK = {value: index for index, value in enumerate(PRIORITIES)}
REQUIRED_FIELDS = (
    "Status", "Priority", "Work class", "Owner", "Branch / PR", "Scope", "Forbidden",
    "Dependencies", "References", "Acceptance gate", "Gate", "Last proof", "Next action", "Updated",
)
CONTINUATION = {"READY", "CLAIMED", "VERIFY", "REVIEW", "MERGE"}
ACTION_VERBS = {
    "run", "execute", "create", "decompose", "split", "update", "repair", "resolve",
    "merge", "fetch", "inspect", "open", "verify", "validate", "test", "commit", "push",
    "rebase", "retarget", "compare", "generate", "record", "obtain", "install", "apply",
    "build", "launch", "deploy", "restore", "export", "import", "review", "reconcile",
    "invoke", "edit", "write", "move", "copy", "sync", "check", "scaffold",
}
DURABLE_PROOF_RE = re.compile(r"\b(?:commit|merge|workflow|run|artifact|operator-proof):[^\s;,]+")
CANONICAL_HEADING_RE = re.compile(r"^## (SSQ-\d{3,}) — ([^\r\n]+)$", re.MULTILINE)
ANY_PREFIXED_HEADING_RE = re.compile(r"^##[ \t]+(SSQ-[^\r\n]*)$", re.MULTILINE)
FIELD_RE = re.compile(r"^- \*\*([^*]+):\*\*[ \t]*(.*)$", re.MULTILINE)
TERMINAL_ACTION = "none; no safe actionable work remains"


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    fields: dict[str, str]
    index: int

    @property
    def status(self) -> str:
        return self.fields["Status"]

    @property
    def priority(self) -> str:
        return self.fields["Priority"]

    @property
    def work_class(self) -> str:
        return self.fields["Work class"]


class LedgerError(ValueError):
    pass


def parse_ledger_text(source: str) -> list[Task]:
    canonical = list(CANONICAL_HEADING_RE.finditer(source))
    prefixed = list(ANY_PREFIXED_HEADING_RE.finditer(source))
    if not canonical:
        raise LedgerError("ledger contains no canonical SSQ task blocks")
    canonical_lines = {m.group(0) for m in canonical}
    for match in prefixed:
        if match.group(0) not in canonical_lines:
            raise LedgerError(f"malformed SSQ task heading: {match.group(0)!r}")

    tasks: list[Task] = []
    seen_ids: set[str] = set()
    for i, match in enumerate(canonical):
        task_id = match.group(1)
        title = match.group(2).strip()
        if task_id in seen_ids:
            raise LedgerError(f"duplicate task id: {task_id}")
        seen_ids.add(task_id)
        end = canonical[i + 1].start() if i + 1 < len(canonical) else len(source)
        block = source[match.start():end]
        fields: dict[str, str] = {}
        for field_match in FIELD_RE.finditer(block):
            name = field_match.group(1).strip()
            value = field_match.group(2).strip()
            if name in fields:
                raise LedgerError(f"{task_id} duplicate field {name!r}")
            fields[name] = value
        for name in REQUIRED_FIELDS:
            if not fields.get(name, "").strip():
                raise LedgerError(f"{task_id} missing or blank required field {name!r}")
        unknown = sorted(set(fields) - set(REQUIRED_FIELDS))
        if unknown:
            raise LedgerError(f"{task_id} unknown fields: {', '.join(unknown)}")
        tasks.append(Task(task_id, title, fields, i))
    return tasks


def parse_ledger(path: Path) -> list[Task]:
    return parse_ledger_text(path.read_text(encoding="utf-8"))


def _first_word(value: str) -> str:
    match = re.match(r"[A-Za-z-]+", value.strip())
    return match.group(0).lower() if match else ""


def _extract_local_refs(value: str) -> Iterable[str]:
    for token in re.findall(r"`([^`]+)`", value):
        if token.startswith((".ai/", "scripts/", "tests/", "docs/", "src/", "practice/", ".github/", "README.md")):
            yield token


def validate_tasks(tasks: list[Task], repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    ids = {task.id for task in tasks}
    for task in tasks:
        f = task.fields
        if f["Status"] not in STATUSES:
            errors.append(f"{task.id}: invalid Status {f['Status']!r}")
        if f["Priority"] not in PRIORITIES:
            errors.append(f"{task.id}: invalid Priority {f['Priority']!r}")
        if f["Work class"] not in WORK_CLASSES:
            errors.append(f"{task.id}: invalid Work class {f['Work class']!r}")

        if f["Status"] == "READY" and f["Owner"].lower() != "unclaimed":
            errors.append(f"{task.id}: READY owner must be exactly 'unclaimed'")
        if f["Status"] in {"CLAIMED", "VERIFY", "REVIEW", "MERGE"} and f["Owner"].lower() in {"unclaimed", "none", "tbd", "agent", "ai"}:
            errors.append(f"{task.id}: active continuation state needs a concrete owner/session")

        if f["Status"] in {"BLOCKED", "OPERATOR"}:
            if f["Gate"].lower() in {"none", "n/a", "na", "unknown", "tbd"}:
                errors.append(f"{task.id}: {f['Status']} requires an exact non-placeholder Gate")
        elif f["Gate"].lower() != "none" and f["Status"] != "DONE" and len(f["Gate"]) < 8:
            errors.append(f"{task.id}: Gate is too vague")

        if f["Status"] == "DONE":
            if f["Next action"] != TERMINAL_ACTION:
                errors.append(f"{task.id}: DONE Next action must be exactly {TERMINAL_ACTION!r}")
            if f["Gate"].lower() != "none":
                errors.append(f"{task.id}: DONE Gate must be 'none'")
            if not DURABLE_PROOF_RE.search(f["Last proof"]):
                errors.append(f"{task.id}: DONE needs durable proof token in Last proof")
        elif f["Next action"] == TERMINAL_ACTION:
            errors.append(f"{task.id}: non-DONE task cannot use terminal Next action")

        if f["Status"] in CONTINUATION:
            verb = _first_word(f["Next action"])
            if verb not in ACTION_VERBS:
                errors.append(f"{task.id}: Next action must start with an executable verb; got {verb or '<none>'!r}")

        if f["Work class"] == "UNBOUNDED":
            if f["Status"] not in {"READY", "BLOCKED", "OPERATOR", "DONE"}:
                errors.append(f"{task.id}: UNBOUNDED may not enter monolithic {f['Status']}")
            if f["Status"] == "READY":
                verb = _first_word(f["Next action"])
                if verb not in {"create", "decompose", "split"} or "bounded" not in f["Next action"].lower():
                    errors.append(f"{task.id}: READY UNBOUNDED Next action must create/decompose/split bounded child work")

        for dep in re.findall(r"\bSSQ-\d{3,}\b", f["Dependencies"]):
            if dep not in ids:
                errors.append(f"{task.id}: dependency references missing task {dep}")

        if repo_root is not None:
            for ref in _extract_local_refs(f["References"]):
                if not (repo_root / ref).exists():
                    errors.append(f"{task.id}: stale local reference {ref}")
    return errors


def derive_route(task: Task) -> str:
    if task.status == "DONE":
        return "TERMINAL"
    if task.status == "BLOCKED":
        return "BLOCKED"
    if task.status == "OPERATOR":
        return "OPERATOR"
    if task.work_class == "UNBOUNDED" and task.status == "READY":
        return "DECOMPOSE"
    if task.work_class == "BOUNDED" and task.status in CONTINUATION:
        return "EXECUTE"
    return "NON_ACTIONABLE"


def actionable_tasks(tasks: list[Task]) -> list[Task]:
    return [task for task in tasks if derive_route(task) in {"EXECUTE", "DECOMPOSE"}]


def frontier_tasks(tasks: list[Task]) -> list[Task]:
    """Return agent work plus explicit operator gates that must remain visible at the default frontier."""
    return [task for task in tasks if derive_route(task) in {"EXECUTE", "DECOMPOSE", "OPERATOR"}]


def select_frontier(tasks: list[Task]) -> Task | None:
    candidates = frontier_tasks(tasks)
    if not candidates:
        return None
    return min(candidates, key=lambda task: (PRIORITY_RANK[task.priority], task.index))


def task_payload(task: Task) -> dict[str, object]:
    return {
        "schema": "studysyndicate.repository-work-ledger.frontier.v1",
        "status": "ready",
        "route": derive_route(task),
        "task": {"id": task.id, "title": task.title, **task.fields},
    }


def empty_payload() -> dict[str, object]:
    return {"schema": "studysyndicate.repository-work-ledger.frontier.v1", "status": "empty", "route": "EMPTY", "task": None}


def render_compact(task: Task | None) -> str:
    if task is None:
        return "ROUTE: EMPTY\nTASK_ID: none\nNEXT_ACTION: none; no actionable ledger task exists"
    f = task.fields
    return "\n".join([
        f"ROUTE: {derive_route(task)}", f"TASK_ID: {task.id}", f"PRIORITY: {f['Priority']}",
        f"WORK_CLASS: {f['Work class']}", f"TITLE: {task.title}", f"GATE: {f['Gate']}",
        f"NEXT_ACTION: {f['Next action']}",
    ])


def render_prompt(task: Task | None) -> str:
    if task is None:
        return "LEDGER FRONTIER: EMPTY\nDo not invent work. Reconcile repository evidence before adding a new task."
    f = task.fields
    route = derive_route(task)
    instructions = {
        "EXECUTE": "EXECUTE THIS BOUNDED SPRINT. DO NOT ANALYZE OTHER LEDGER ITEMS.",
        "DECOMPOSE": "DECOMPOSE THIS PARENT INTO BOUNDED CHILD SPRINTS. DO NOT IMPLEMENT THE PARENT.",
        "OPERATOR": "OPERATOR GATE. DO NOT INVENT OR IMPLEMENT A FEATURE. COMPLETE THE EXACT GATE OR PRESERVE IT AS USER-ONLY BLOCKED WORK.",
        "BLOCKED": "BLOCKED GATE. DO NOT INVENT SUBSTITUTE WORK. ADVANCE ONLY THE NAMED DEPENDENCY OR RECORD THE BLOCKER.",
    }
    instruction = instructions.get(route, "RECONCILE THIS NON-ACTIONABLE LEDGER STATE BEFORE PROCEEDING.")
    return "\n".join([
        instruction, f"ROUTE: {route}", f"TASK ID: {task.id}", f"TITLE: {task.title}",
        f"STATUS: {f['Status']}", f"PRIORITY: {f['Priority']}", f"WORK CLASS: {f['Work class']}",
        f"OWNER: {f['Owner']}", f"BRANCH / PR: {f['Branch / PR']}", f"SCOPE: {f['Scope']}",
        f"FORBIDDEN: {f['Forbidden']}", f"DEPENDENCIES: {f['Dependencies']}", f"REFERENCES: {f['References']}",
        f"ACCEPTANCE GATE: {f['Acceptance gate']}", f"CURRENT GATE: {f['Gate']}", f"LAST PROOF: {f['Last proof']}",
        f"FIRST ACTION: {f['Next action']}",
        "STOP RULE: update the canonical ledger before stopping; do not claim proof above repository/runtime evidence.",
    ])
