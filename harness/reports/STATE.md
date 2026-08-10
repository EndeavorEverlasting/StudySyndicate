# Operator State Report

Status captured for the Harness Infrastructure Build on 2026-08-10.

## Working

- Canonical governance exists at `AGENTS.md`.
- PMP, software-foundations, arrays, mental-math, multimodal-media, and repository-ledger validators exist.
- Two Sum has a dependency-free executable kata harness.
- Portable media bundles have pack/validate tooling and integrity tests.
- The operational harness has a single entrypoint, workflow selector, artifact registry,
  validation registry, source adapter, scoped skills, hooks, and operator reports.
- The bounded repository ledger exposes one deterministic `EXECUTE` / `DECOMPOSE` frontier for weak models and hurried operators.
- Repository-location recovery is now explicit: the harness can distinguish the durable clone from a wrong current directory or detached `%TEMP%` worktree and prove the canonical GitHub origin before mutation.
- ParallaxPort public skill claims are versioned as study fodder rather than treated as mastery proof.
- A learner who is blocked at a blank file has an explicit guided start, documentation lookup path,
  and graduated feedback ladder.

## Broken

No tracked harness defect is intentionally accepted at this snapshot. The observed operator failure was environmental/path-state rather than repository corruption: commands were run from `C:\Users\CheeksMcClappeth\Desktop\Dev` and later `C:\Users\CheeksMcClappeth\dev`, while the durable clone was created under `C:\Users\CheeksMcClappeth\Desktop\dev\StudySyndicate`.

This statement is repository-state prose; executable proof is `python scripts/harness.py validate --level full`, including `scripts/Test-RepoLocationRecovery.ps1`, plus the corresponding CI run.

## Missing / intentionally deferred

- The full browser application shell is not yet scaffolded, so there is no honest root app build or
  StudySyndicate deploy command.
- No repository-wide formatter/linter is configured; the current static floor is Python compilation
  plus `git diff --check`.
- ParallaxPort claim refresh is explicit rather than live-scraped. This avoids hidden network,
  credential, and cross-repository mutation dependencies.
- Tracked Git hooks are opt-in and are not installed automatically.
- The harness cannot change the parent shell's working directory; repository recovery therefore prints/proves the root and runs commands with absolute paths or `git -C`. The operator may `Set-Location` deliberately after proof.

## Known traps

- `C:\Users\<user>\Desktop\Dev\StudySyndicate` and `C:\Users\<user>\dev\StudySyndicate` are different locations; missing `Desktop` matters even though `Dev`/`dev` case normally does not on Windows.
- A detached `%TEMP%\StudySyndicate-*` worktree can be valid for a bounded sprint but is not the durable clone.
- Do not issue repo-relative commands until repository identity has been proven after a terminal restart.
- Do not confuse the reference solution in `practice/arrays/two_sum.py` with learner mastery.
- Do not search the exact challenge solution during a docs-assisted/mastery attempt.
- Do not create a second governance contract inside the harness.
- Do not run broad rewrites to fix one validator failure.
- Do not commit local study exports, media bundles, secrets, logs, caches, or editor state.
- Do not mutate ParallaxPort from the StudySyndicate public-claim workflow.

## Next proof target

Use the repository-location workflow first from a shell that is outside the repo, prove the durable root/origin, then run the bounded ledger frontier. That operator proof demonstrates the exact failure mode that triggered this harness hardening without requiring destructive cleanup or a second clone.
