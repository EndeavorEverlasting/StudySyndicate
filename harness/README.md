# StudySyndicate Operational Harness

This directory is the operational entry point for agents and operators. It does not replace
`AGENTS.md`; repository governance remains authoritative there.

## First five minutes

1. Read `AGENTS.md`.
2. Run `python scripts/get-repo-ledger-frontier.py --prompt` before free-form planning.
3. If the packet says `EXECUTE`, work only that bounded task. If it says `DECOMPOSE`, create bounded child tasks before implementation. If it says `EMPTY`, do not invent work.
4. Run `python scripts/harness.py inspect`, then `python scripts/harness.py workflows` and choose the smallest workflow that supports the selected ledger task.
5. Run `python scripts/harness.py validate --level quick` before editing.
6. Work inside the selected lane, then run `python scripts/harness.py validate --level full` before commit or handoff and update `.ai/WORK_QUEUE.md` before stopping.

The compact frontier is deliberately the default intake for weak models and hurried humans. It emits one self-contained sprint packet with scope, forbidden scope, dependencies, acceptance gate, current proof, and the first executable action. Do not make a low-capability worker infer those fields from the whole repository or from a long queue.

If the study task feels too hard to begin, do **not** jump directly to the answer. Use
`harness/workflows/GUIDED_STUDY.md`. Guided work is legitimate practice; it is simply recorded
as `guided` or `docs-assisted` rather than `mastery`.

## Harness authority map

- `.ai/WORK_QUEUE.md` — canonical repository coordination ledger; implementation truth remains in repository-owned evidence surfaces.
- `.ai/README.md` — ledger intake, routes, authority/version pins, and weak-model rules.
- `scripts/get-repo-ledger-frontier.py` — deterministic one-task frontier and copy/paste sprint packet generator.
- `CODEBASE_MAP.md` — repository layout, entry points, commands, and current build/deploy floor.
- `WORKFLOW_SPECS.md` — task pickup, failure handling, validation, and handoff.
- `harness-manifest.v1.json` — machine-readable component inventory and workflow selector.
- `artifact-registry.v1.json` — output locations, generators, naming, and retention.
- `validation-manifest.v1.json` — executable validation command registry.
- `sources/parallaxport-claims.v1.json` — versioned public-claim snapshot used as study fodder.
- `workflows/` — executable human procedures.
- `skills/` — repeatable scoped procedures with triggers, inputs, and outputs.
- `reports/` — operator-readable state and generated study-fodder summaries.
- `scripts/harness.py` — inspect, workflow, validation, and report-generation CLI.
- `scripts/validate-harness.py` — harness completeness and contract validator.
- `.githooks/` — opt-in local hooks; they are never installed implicitly.

## Common commands

```bash
python scripts/get-repo-ledger-frontier.py --prompt
python scripts/get-repo-ledger-frontier.py --json
python scripts/validate-repo-ledger.py
python scripts/harness.py inspect
python scripts/harness.py workflows
python scripts/harness.py start guided-study
python scripts/harness.py study-fodder
python scripts/harness.py validate --level quick
python scripts/harness.py validate --level full
```

Install the tracked hooks only when you intentionally want this checkout to use them:

```bash
git config core.hooksPath .githooks
```

## Public claims are inputs, not proof

ParallaxPort is treated as a source of **study targets**. A technology displayed publicly creates
a reason to practice and defend that claim; it does not automatically create evidence of mastery.
The source snapshot maps each visible claim into an existing StudySyndicate track or a bounded
maintenance exercise. Refresh the snapshot deliberately when the public portfolio changes.
