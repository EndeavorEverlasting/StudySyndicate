# Operator State Report

Status captured for the Harness Infrastructure Build on 2026-08-10.

## Working

- Canonical governance exists at `AGENTS.md`.
- PMP, software-foundations, arrays, mental-math, and multimodal-media contract validators exist.
- Two Sum has a dependency-free executable kata harness.
- Portable media bundles have pack/validate tooling and integrity tests.
- The operational harness now has a single entrypoint, workflow selector, artifact registry,
  validation registry, source adapter, scoped skills, hooks, and operator reports.
- ParallaxPort public skill claims are versioned as study fodder rather than treated as mastery proof.
- A learner who is blocked at a blank file has an explicit guided start, documentation lookup path,
  and graduated feedback ladder.

## Broken

No tracked harness defect is intentionally accepted at this snapshot. This statement is only
repository-state prose; the executable proof is `python scripts/harness.py validate --level full`
and the corresponding CI run.

## Missing / intentionally deferred

- The full browser application shell is not yet scaffolded, so there is no honest root app build or
  StudySyndicate deploy command.
- No repository-wide formatter/linter is configured; the current static floor is Python compilation
  plus `git diff --check`.
- ParallaxPort claim refresh is explicit rather than live-scraped. This avoids hidden network,
  credential, and cross-repository mutation dependencies.
- Tracked Git hooks are opt-in and are not installed automatically.

## Known traps

- Do not confuse the reference solution in `practice/arrays/two_sum.py` with learner mastery.
- Do not search the exact challenge solution during a docs-assisted/mastery attempt.
- Do not create a second governance contract inside the harness.
- Do not run broad rewrites to fix one validator failure.
- Do not commit local study exports, media bundles, secrets, logs, caches, or editor state.
- Do not mutate ParallaxPort from the StudySyndicate public-claim workflow.

## Next proof target

Use `python scripts/harness.py start guided-study` for the first guided Two Sum rep. The proof to
capture is not a perfect answer: it is an honest attempt, the highest hint level needed, a test or
small counterexample, and the next retrieval target.
