# Exact-Candidate Promotion

`harness/promotion-contract.v1.json` owns the rules for advancing a validated StudySyndicate pull request into `main`. `.github/workflows/promote-main.yml` orchestrates those rules; it is not a second test implementation and it does not author source code.

## Authorization and candidate identity

The promotion gesture is deliberately explicit: the repository owner changes a same-repository draft pull request to **ready for review**. Only `pull_request.ready_for_review` can start the writer pipeline at this floor.

The event must prove all of the following before validation begins:

- actor is the repository owner;
- PR author is the repository owner;
- head repository is `EndeavorEverlasting/StudySyndicate`;
- base branch is `main`;
- event head and base are 40-character commit SHAs;
- the PR is no longer draft.

If the branch changes later, the earlier proof is stale. A `synchronize` event does not promote the new head; return the PR to draft and mark it ready again after the new exact candidate is ready for promotion.

## Promotion graph

1. **AUTHORIZE** — read-only event identity check; records candidate head SHA, base SHA, and PR number.
2. **VALIDATE / HARNESS E2E** — checkout the exact head SHA and run `python scripts/harness.py validate --level full`.
3. **VALIDATE / APPLICATION E2E** — exercise the already-built application through `npm run preview` with `scripts/application-e2e.py`; record the built `dist/` digest and HTTP proof.
4. **RECHECK** — query GitHub immediately before mutation and reject moved head, changed repo/base, closed PR, or returned-draft state.
5. **PROMOTE** — squash-merge through GitHub's PR merge API with the validated SHA supplied as the expected head. No force update or admin bypass is used.
6. **CONTAINMENT** — refresh `main` and prove the returned merge SHA is an ancestor of refreshed `origin/main`.
7. **RECEIPT** — emit `studysyndicate.promotion-receipt.v1` with provider run ID, candidate/base identity, required gate conclusions, application artifact digest, merge SHA, target, and proof ceiling.

## Harness E2E versus application E2E

These are separate required gates.

- Harness E2E proves repository contracts, registries, validators, fixtures, lint, and build together.
- Application E2E proves the built product is served through its real Vite preview HTTP entrypoint and that the referenced JavaScript asset is reachable.

The HTTP smoke does not claim real browser interaction, IndexedDB persistence, or the Windows operator `npm run dev` entrypoint. Those remain beyond its proof ceiling.

## Permissions, concurrency, and recursion

Validation uses read-only repository/PR permission. Only the final promotion job receives `contents: write` and `pull-requests: write`. The workflow serializes writers through `studysyndicate-promote-main` with cancellation disabled.

Because the only writer trigger is `pull_request.ready_for_review`, the resulting merge push does not recursively start another writer.

## Local workstation boundary

A successful provider promotion establishes `REMOTE_INTEGRATED` only. It does not establish `DEV_CHECKOUT_CURRENT`, `PROD_PATH_CURRENT`, or `ENTRYPOINT_PROVED` for the Windows operator profile. Resolve those with `scripts/Resolve-StudySyndicateRepo.ps1` and the canonical path contract after integration.

## Failure handoff

Any required skip, stale identity, harness failure, application E2E failure, unauthorized target, or failed containment keeps promotion blocked. Preserve the candidate SHA/base, first failing command/job, relevant artifact/log identity, owning surface, and acceptance condition for the development repair loop. A repaired branch is a new candidate and must re-enter this workflow from the beginning.
