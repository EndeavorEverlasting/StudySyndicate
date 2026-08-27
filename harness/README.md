# StudySyndicate Operational Harness

This directory is the operational entry point for agents and operators. It does not replace
`AGENTS.md`; repository governance remains authoritative there.

## If the shell lost the repository

If Git says `fatal: not a git repository`, do not assume the clone is missing and do not create a second clone immediately. Start with `harness/canonical-paths.v1.json` and `harness/workflows/REPO_LOCATION_RECOVERY.md`.

For the Windows operator profile, the durable rule is **Windows Desktop Known Folder -> `Dev\StudySyndicate`**. Resolve Desktop with `Environment.SpecialFolder.Desktop`; do not assume `%USERPROFILE%\Desktop` and do not rewrite the location under OneDrive unless Windows has actually redirected the Desktop Known Folder there. Parallel worktrees belong under the sibling `Dev\StudySyndicate-worktrees` root, not in another durable clone.

Once this checkout is reachable, the tracked resolver proves the selected profile, canonical path, Git origin, branch, and HEAD and can run quick intake without depending on the current directory:

```powershell
pwsh -NoLogo -NoProfile -File scripts/Resolve-StudySyndicateRepo.ps1 -RunHarness
```

A noncanonical checkout is evidence to preserve and inspect, not fallback authority.

## First five minutes

1. Prove the repository root. If location is uncertain, use `harness/canonical-paths.v1.json` and `harness/workflows/REPO_LOCATION_RECOVERY.md` first.
2. Read `AGENTS.md`.
3. Run `python scripts/get-repo-ledger-frontier.py --prompt` before free-form planning.
4. If the packet says `EXECUTE`, work only that bounded task. If it says `DECOMPOSE`, create bounded child tasks before implementation. If it says `EMPTY`, do not invent work.
5. Run `python scripts/harness.py inspect`, then `python scripts/harness.py workflows` and choose the smallest workflow that supports the selected ledger task.
6. Run `python scripts/harness.py validate --level quick` before editing.
7. Work inside the selected lane, then run `python scripts/harness.py validate --level full` before commit or handoff and update `.ai/WORK_QUEUE.md` before stopping.

The compact frontier is deliberately the default intake for weak models and hurried humans. It emits one self-contained sprint packet with scope, forbidden scope, dependencies, acceptance gate, current proof, and the first executable action. Do not make a low-capability worker infer those fields from the whole repository or from a long queue.

If the study task feels too hard to begin, do **not** jump directly to the answer. Use
`harness/workflows/GUIDED_STUDY.md`. Guided work is legitimate practice; it is simply recorded
as `guided` or `docs-assisted` rather than `mastery`.

For browser-based practice, use `harness/workflows/PRACTICE_WORKBENCH.md`. The UI renders canonical
problem/study contracts through a modal target/facet/language/mode selector and draggable premise,
workspace, and feedback panels. A language appearing in the selector never implies that its runner is
available; `harness/practice-workbench.v1.json` owns that capability state.

## Harness authority map

- `.ai/WORK_QUEUE.md` — canonical repository coordination ledger; implementation truth remains in repository-owned evidence surfaces.
- `.ai/README.md` — ledger intake, routes, authority/version pins, and weak-model rules.
- `scripts/get-repo-ledger-frontier.py` — deterministic one-task frontier and copy/paste sprint packet generator.
- `harness/canonical-paths.v1.json` — machine/profile-aware development, use, and worktree path authority.
- `scripts/Resolve-StudySyndicateRepo.ps1` — executable canonical-path/profile resolver and path-input receipt generator.
- `CODEBASE_MAP.md` — repository layout, entry points, commands, and current build/deploy floor.
- `WORKFLOW_SPECS.md` — task pickup, failure handling, validation, and handoff.
- `workflows/REPO_LOCATION_RECOVERY.md` — fail-closed recovery workflow for wrong-directory and worktree/path-drift traps.
- `harness/promotion-contract.v1.json` — exact-candidate promotion authority for `main`.
- `workflows/PROMOTION.md` — provider promotion graph, proof levels, permissions, and failure handoff.
- `.github/workflows/promote-main.yml` — GitHub orchestration that validates and promotes only the exact authorized candidate.
- `workflows/PRACTICE_WORKBENCH.md` — browser practice workflow and execution-capability boundary.
- `practice-workbench.v1.json` — language, facet, panel, and runner-capability contract.
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
python scripts/harness.py start practice-workbench
python scripts/harness.py study-fodder
python scripts/validate-canonical-paths.py
python scripts/validate-promotion.py
python tests/test_promotion_contract.py
python scripts/validate-practice-workbench.py
python tests/test_practice-workbench_contract.py
npm run lint
npm run build
python scripts/harness.py validate --level quick
python scripts/harness.py validate --level full
```

Windows location proof:

```powershell
$Desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
$Repo = Join-Path $Desktop 'Dev\StudySyndicate'
& (Join-Path $Repo 'scripts\Resolve-StudySyndicateRepo.ps1') -StartPath (Get-Location).Path -Json
```

Install the tracked hooks only when you intentionally want this checkout to use them:

```bash
git config core.hooksPath .githooks
```

## Promotion proof is separate from workstation deployment

Marking an owner-authored same-repository draft PR ready for review is the explicit promotion gesture at this floor. `Promote Exact Candidate` then pins the PR head SHA, runs the canonical full harness, runs a distinct application HTTP E2E through the built Vite preview entrypoint, rechecks the candidate immediately before mutation, squash-merges with the expected-head guard, proves containment in refreshed `main`, and emits a promotion receipt.

That provider receipt proves remote integration only. It does not prove the Windows canonical development checkout is current, that the same-path local use role has consumed the version, or that `npm run dev` has been observed on the workstation.

## Runner capability is explicit

Guest code failure is data, not a host-shell failure. A runner adapter catches or receives language/runtime
failures and normalizes them before the result reaches React. For embedded Lua, the host catches the raised
Lua error and returns a `runtime-error` outcome. Planned runners remain visibly planned until runtime proof
exists; browser `eval`/`new Function` is not an approved shortcut.

## Public claims are inputs, not proof

ParallaxPort is treated as a source of **study targets**. A technology displayed publicly creates
a reason to practice and defend that claim; it does not automatically create evidence of mastery.
The source snapshot maps each visible claim into an existing StudySyndicate track or a bounded
maintenance exercise. Refresh the snapshot deliberately when the public portfolio changes.
