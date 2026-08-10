# StudySyndicate Work Queue

Authority: coordination index only. Repository code, tests, manifests, workflows, PRs, artifacts, and runtime evidence remain authoritative for implementation truth.

Portable contract: `EndeavorEverlasting/BlacksmithGuild` `RepoLedgerInteroperability.v1` pinned at `429237aa41d8712d71859865c9be407ca23d8580`.

Local execution profile: `studysyndicate.repository-work-ledger.profile.v1@1.0.0`.

Weak-model rule: run `python scripts/get-repo-ledger-frontier.py --prompt` first. Execute only the returned task. Do not reread or summarize the whole ledger unless the frontier says `DECOMPOSE` or a collision must be reconciled.

Canonical terminal action: `none; no safe actionable work remains`

## SSQ-001 — Scaffold the browser application shell

- **Status:** READY
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** unclaimed
- **Branch / PR:** none / none
- **Scope:** create the minimal Vite + React + TypeScript application shell, package scripts, and one buildable empty study-app entrypoint without implementing feature behavior
- **Forbidden:** Dexie schema implementation; media playback or recording; cloud sync; AI grading; PMP content rewrites; SQL/Rust or arrays curriculum rewrites; generated dependency folders or build output
- **Dependencies:** none
- **References:** `README.md`, `docs/DOMAIN_MODEL.md`, `docs/PMP_STUDY_SYSTEM.md`
- **Acceptance gate:** `package.json` and the minimal Vite/React/TypeScript source/config files are tracked; dependency installation succeeds; the canonical build command exits 0; existing repository validators remain green; no generated dependency or build-output directory is committed
- **Gate:** none
- **Last proof:** merge:6f7b65ef5aa88eba1d7bc4286a97235252b7e181 established the current local-first media/domain floor before app scaffolding
- **Next action:** create an isolated branch from current main, scaffold only the Vite + React + TypeScript shell, run the build plus existing repository validators, and commit the bounded shell if all gates pass
- **Updated:** 2026-08-10T17:06:00-04:00
