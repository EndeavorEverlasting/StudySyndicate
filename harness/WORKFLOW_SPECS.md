# Workflow Specifications

## Pick up a task

1. Prove the repository root before mutation. If Git says `not a git repository`, the shell was restarted, or a `%TEMP%` worktree may be active, use `harness/workflows/REPO_LOCATION_RECOVERY.md` first.
2. Read `AGENTS.md` and declare repo, branch, lane, owned scope, forbidden scope, expected artifacts,
   validation commands, and proof ceiling.
3. Run `python scripts/get-repo-ledger-frontier.py --prompt` and obey the selected bounded route before free-form planning.
4. Run `python scripts/harness.py inspect`.
5. Run `python scripts/harness.py workflows`.
6. Select exactly one primary workflow from `harness/harness-manifest.v1.json`.
7. Run the quick validation floor before mutation.
8. Search existing doctrine, packs, scripts, validators, and naming before creating a new authority.

Use an isolated branch/worktree when the current checkout is dirty or separately owned. Do not reset or clean a checkout merely because the current shell lost its directory.

## Repository location recovery

Repository identity is proven by Git, not by the prompt path. A durable clone at `$HOME\Desktop\Dev\StudySyndicate` is different from `$HOME\dev\StudySyndicate`; a detached `%TEMP%\StudySyndicate-*` worktree may also exist.

From a reachable checkout, run:

```powershell
pwsh -NoLogo -NoProfile -File scripts/Resolve-StudySyndicateRepo.ps1 -RunHarness
```

The resolver must emit the canonical root, origin, branch/detached state, and HEAD. It must reject a repository whose origin is not `EndeavorEverlasting/StudySyndicate`.

When the script itself is not reachable, use the self-contained PowerShell recovery snippet in `harness/workflows/REPO_LOCATION_RECOVERY.md`; it searches durable candidate paths without assuming the current directory is correct.

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

## Learning-event selection

Use `learning-event-cascade` when a learner has produced work worth preserving even if the final answer is
wrong, incomplete, assisted, or exploratory.

1. Preserve learner-produced evidence before replacing it with agent/source output.
2. Read `docs/LEARNING_EVIDENCE_DOCTRINE.md`.
3. Record an assistance band and observed facet qualities.
4. Run `python scripts/learning-evidence.py score PATH_TO_EVENT.json`.
5. Report earned facets, assistance provenance, event credit, cascade recognition, and the weakest next facet.
6. Never convert cascade recognition or a single-event signal into mastery.

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
in `harness/validation-manifest.v1.json`, including repository-location and learning-evidence proof.

## Handle failures

Do not respond to a red check by broad rewriting.

1. Capture the exact failing command and exit code.
2. Reduce to the smallest failing input or contract.
3. Classify the failure: wrong repository/current directory, syntax/import, structural contract, wrong output, edge case, complexity,
   generated-artifact drift, environment/tooling, or unrelated pre-existing failure.
4. If the failure is repository/current-directory related, recover the root and rerun using `git -C` or absolute paths before changing files.
5. Repair only the owning layer.
6. Re-run the smallest failing check first.
7. Re-run full validation before claiming recovery.
8. If blocked by environment/tool availability, report the blocker and the exact command that should
   run in the required environment.

For study failures, use the feedback ladder in `harness/skills/guided-feedback/SKILL.md`; do not jump
from confusion directly to copying the reference solution. For evidence-scoring failures, repair the event
packet or versioned learning-evidence contract rather than improvising an untracked scoring rule.

## Handoff

A handoff must contain:

- repo and exact branch/commit
- resolved local root when local-path state matters
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
- hints/docs/AI assistance used
- event credit and earned facets when a learning event was recorded
- direct vs derived/cascade evidence
- smallest failing case or successful test evidence
- next retrieval target

Never report `mastery` merely because repository reference code or an AI-generated answer exists.
