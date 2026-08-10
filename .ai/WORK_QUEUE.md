# StudySyndicate Work Queue

Authority: coordination index only. Repository code, tests, manifests, workflows, PRs, artifacts, and runtime evidence remain authoritative for implementation truth.

Portable contract: `EndeavorEverlasting/BlacksmithGuild` `RepoLedgerInteroperability.v1` pinned at `429237aa41d8712d71859865c9be407ca23d8580`.

Local execution profile: `studysyndicate.repository-work-ledger.profile.v1@1.0.0`.

Weak-model rule: run `python scripts/get-repo-ledger-frontier.py --prompt` first. Execute only the returned task. Do not reread or summarize the whole ledger unless the frontier says `DECOMPOSE` or a collision must be reconciled.

Canonical terminal action: `none; no safe actionable work remains`

## SSQ-001 — Scaffold the browser application shell

- **Status:** VERIFY
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** workbench-sprint-20260810
- **Branch / PR:** `feat/multilanguage-practice-workbench-20260810` / pending
- **Scope:** create the minimal Vite + React + TypeScript application shell, package scripts, and one buildable study-app entrypoint while preserving contract-first study authority
- **Forbidden:** Dexie schema implementation; media playback or recording; cloud sync; AI grading; PMP content rewrites; generated dependency folders or build output
- **Dependencies:** none
- **References:** `README.md`, `docs/DOMAIN_MODEL.md`, `docs/PMP_STUDY_SYSTEM.md`, `harness/practice-workbench.v1.json`
- **Acceptance gate:** `package.json` and Vite/React/TypeScript source/config are tracked; dependency installation, lint, and build pass in CI; existing repository validators remain green; no generated dependency or build-output directory is committed
- **Gate:** none
- **Last proof:** commit:f223f97c3aba5ac9aac4dc9d5020ac8ae0f2bbd1 established the premise-first packet floor before browser scaffolding
- **Next action:** validate the feature branch with npm lint, npm build, and the full registered harness CI, then record the durable feature commit
- **Updated:** 2026-08-10T18:45:00-04:00

## SSQ-002 — Build the multi-language Practice Workbench foundation

- **Status:** VERIFY
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** workbench-sprint-20260810
- **Branch / PR:** `feat/multilanguage-practice-workbench-20260810` / pending
- **Scope:** render canonical study targets through a premise-first modal workbench with facet/language/mode selection, draggable panels, plain-text fallback, explicit runner capabilities, and host-safe normalized failure semantics
- **Forbidden:** arbitrary browser code execution; direct `eval` or `new Function`; cloud execution; secrets; silently claiming planned runners are available; curriculum duplication; unrelated source-repository mutation
- **Dependencies:** SSQ-001 implementation is delivered in the same branch and must pass its build gate before this task reaches DONE
- **References:** `harness/workflows/PRACTICE_WORKBENCH.md`, `harness/practice-workbench.v1.json`, `harness/problems/problem-packet-contract.v1.json`, `src/App.tsx`
- **Acceptance gate:** target/facet/language/mode modal is tracked; premise appears before workspace; required panels support drag-and-drop; plain-text fallback remains usable; eight language capabilities are explicit; guest failure semantics are normalized; workbench validators/tests plus npm lint/build pass
- **Gate:** none
- **Last proof:** commit:f223f97c3aba5ac9aac4dc9d5020ac8ae0f2bbd1 plus the operator-guided Two Sum run proved the packet mechanics this UI renders
- **Next action:** validate the workbench contract, behavior tests, lint, build, and full harness CI on the feature branch before marking the UI foundation complete
- **Updated:** 2026-08-10T18:45:00-04:00

## SSQ-003 — Prove the first real Practice Workbench execution adapter

- **Status:** BLOCKED
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** unclaimed
- **Branch / PR:** none / none
- **Scope:** implement exactly one runner adapter behind `harness/practice-workbench.v1.json`; prove success, guest failure normalization, and timeout/cancellation while keeping the host shell usable; update only that runner status after proof
- **Forbidden:** implementing multiple language runners in one sprint; direct browser `eval` or `new Function`; cloud execution service; secrets; weakening the premise-first packet or mastery contracts; unrelated curriculum rewrites
- **Dependencies:** SSQ-001 and SSQ-002 must both reach DONE
- **References:** `harness/workflows/PRACTICE_WORKBENCH.md`, `src/practice/execution.ts`, `harness/practice-workbench.v1.json`
- **Acceptance gate:** one adapter has targeted pass/failure/timeout tests; guest exceptions/errors normalize to registered `ExecutionOutcome`; the React shell remains recoverable; owning validator plus npm run lint and npm run build pass; runner status matches observed runtime proof
- **Gate:** SSQ-001 and SSQ-002 must both reach DONE on merged main before runner implementation starts
- **Last proof:** commit:f223f97c3aba5ac9aac4dc9d5020ac8ae0f2bbd1 proves packet mechanics only; runner runtime proof does not exist yet
- **Next action:** validate and merge SSQ-001 and SSQ-002 before selecting exactly one registered runner for implementation
- **Updated:** 2026-08-10T18:45:00-04:00
