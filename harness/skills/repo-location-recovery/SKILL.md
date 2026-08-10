# Skill: Repository Location Recovery

## Trigger

Use this skill when any of the following is true:

- Git reports `not a git repository`.
- A terminal restart changed the current directory.
- The durable clone and a detached `%TEMP%` worktree may both exist.
- The operator says `cd StudySyndicate` or `cd dev\StudySyndicate` cannot find the repository.
- A command was written assuming the shell was already inside the repository.

## Required inputs

- Repository identity: `EndeavorEverlasting/StudySyndicate`.
- One or more plausible local roots, normally `$HOME\Desktop\Dev`, `$HOME\Desktop\dev`, or `$HOME\dev`.
- The task's intended branch/commit when a specific revision matters.

## Procedure

1. Do not mutate or clean anything while location is uncertain.
2. Resolve candidate paths with `Test-Path` and Git itself; never infer repository state from folder names alone.
3. Prove the candidate with both:
   - `git -C <candidate> rev-parse --show-toplevel`
   - `git -C <candidate> remote get-url origin`
4. Reject candidates whose origin is not the canonical StudySyndicate repository.
5. Record the resolved absolute root, branch/detached state, and HEAD SHA.
6. Inspect `git -C <root> status --short` before mutation.
7. Prefer `git -C <root> ...` or absolute script paths until the operator intentionally changes directory.
8. Run the repository ledger validator and bounded frontier before choosing work.

## Expected outputs

- Canonical absolute repository root.
- Repository identity/origin proof.
- Branch or `(detached)` state.
- Exact HEAD SHA.
- Clean/dirty status evidence.
- Ledger validation result and the next bounded frontier packet.

## Failure handling

If no candidate is valid, stop with the searched locations and expected GitHub origin. Do not clone a second copy until existing durable and temporary worktrees have been deliberately ruled out.

If the correct root is dirty or separately owned, preserve it and create an isolated worktree/branch from the required commit rather than resetting it.

## Reference

See `harness/workflows/REPO_LOCATION_RECOVERY.md` and `scripts/Resolve-StudySyndicateRepo.ps1`.
