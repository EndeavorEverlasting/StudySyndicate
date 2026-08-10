# Workflow Specifications

## Pick up a task

1. Read `AGENTS.md` and declare repo, branch, lane, owned scope, forbidden scope, expected artifacts,
   validation commands, and proof ceiling.
2. Run `python scripts/harness.py inspect`.
3. Run `python scripts/harness.py workflows`.
4. Select exactly one primary workflow from `harness/harness-manifest.v1.json`.
5. Run the quick validation floor before mutation.
6. Search existing doctrine, packs, scripts, validators, and naming before creating a new authority.

Use an isolated branch/worktree when the current checkout is dirty or separately owned.

## Study task selection

If the task comes from a technology publicly presented on ParallaxPort:

1. Run `python scripts/harness.py study-fodder`.
2. Open `harness/reports/PARALLAXPORT_STUDY_FODDER.md`.
3. Choose one claim and one smallest practice target.
4. Choose a study mode:
   - `guided` — hints, examples, and scaffolding are allowed; goal is entry and understanding.
   - `docs-assisted` — official documentation is allowed after an initial attempt; exact solution lookup is not.
   - `mastery` — blank-file/no-AI reconstruction plus explanation and executable proof.
5. Record the mode honestly. Guided success is progress, not failed mastery.

## Validate before commit

Run:

```bash
python scripts/harness.py validate --level full
git diff --check
git status --short
git diff --stat
git diff
```

The full harness validation invokes the existing repository validators and executable tests registered
in `harness/validation-manifest.v1.json`.

## Handle failures

Do not respond to a red check by broad rewriting.

1. Capture the exact failing command and exit code.
2. Reduce to the smallest failing input or contract.
3. Classify the failure: syntax/import, structural contract, wrong output, edge case, complexity,
   generated-artifact drift, environment/tooling, or unrelated pre-existing failure.
4. Repair only the owning layer.
5. Re-run the smallest failing check first.
6. Re-run full validation before claiming recovery.
7. If blocked by environment/tool availability, report the blocker and the exact command that should
   run in the required environment.

For study failures, use the feedback ladder in `harness/skills/guided-feedback/SKILL.md`; do not jump
from confusion directly to copying the reference solution.

## Handoff

A handoff must contain:

- repo and exact branch/commit
- lane and owned/forbidden scope
- files changed and artifacts produced
- validation commands and observed results
- skipped checks and why
- known gaps/risks
- clean/dirty git state
- one exact next command

For study work, also include:

- source claim or study track
- mode (`guided`, `docs-assisted`, or `mastery`)
- what was attempted from memory
- hints/docs used
- smallest failing case or successful test evidence
- next retrieval target

Never report `mastery` merely because repository reference code or an AI-generated answer exists.
