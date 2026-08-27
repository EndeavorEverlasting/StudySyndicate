# StudySyndicate Work Queue

Authority: coordination index only. Repository code, tests, manifests, workflows, PRs, artifacts, and runtime evidence remain authoritative for implementation truth.

Portable contract: `EndeavorEverlasting/BlacksmithGuild` `RepoLedgerInteroperability.v1` pinned at `429237aa41d8712d71859865c9be407ca23d8580`.

Local execution profile: `studysyndicate.repository-work-ledger.profile.v1@1.0.0`.

Weak-model rule: run `python scripts/get-repo-ledger-frontier.py --prompt` first. Execute only the returned task. Do not reread or summarize the whole ledger unless the frontier says `DECOMPOSE` or a collision must be reconciled.

Canonical terminal action: `none; no safe actionable work remains`

## SSQ-001 — Scaffold the browser application shell

- **Status:** DONE
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** workbench-sprint-20260810
- **Branch / PR:** `feat/multilanguage-practice-workbench-20260810` / #13
- **Scope:** create the minimal Vite + React + TypeScript application shell, package scripts, and one buildable study-app entrypoint while preserving contract-first study authority
- **Forbidden:** Dexie schema implementation; media playback or recording; cloud sync; AI grading; PMP content rewrites; generated dependency folders or build output
- **Dependencies:** none
- **References:** `README.md`, `docs/DOMAIN_MODEL.md`, `docs/PMP_STUDY_SYSTEM.md`, `harness/practice-workbench.v1.json`
- **Acceptance gate:** `package.json` and Vite/React/TypeScript source/config are tracked; dependency installation, lint, and build pass in CI; existing repository validators remain green; no generated dependency or build-output directory is committed
- **Gate:** none
- **Last proof:** commit:752da1ae46d60a4b5b62d553e51314dba905fb2c workflow:31441430835 proved full harness validation including npm lint/build; workflow:31441430845 proved targeted app install/lint/build
- **Next action:** none; no safe actionable work remains
- **Updated:** 2026-08-10T19:18:00-04:00

## SSQ-002 — Build the multi-language Practice Workbench foundation

- **Status:** DONE
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** workbench-sprint-20260810
- **Branch / PR:** `feat/multilanguage-practice-workbench-20260810` / #13
- **Scope:** render canonical study targets through a premise-first modal workbench with facet/language/mode selection, draggable panels, plain-text fallback, explicit runner capabilities, and host-safe normalized failure semantics
- **Forbidden:** arbitrary browser code execution; direct `eval` or `new Function`; cloud execution; secrets; silently claiming planned runners are available; curriculum duplication; unrelated source-repository mutation
- **Dependencies:** SSQ-001
- **References:** `harness/workflows/PRACTICE_WORKBENCH.md`, `harness/practice-workbench.v1.json`, `harness/problems/problem-packet-contract.v1.json`, `src/App.tsx`
- **Acceptance gate:** target/facet/language/mode modal is tracked; premise appears before workspace; required panels support drag-and-drop; plain-text fallback remains usable; eight language capabilities are explicit; guest failure semantics are normalized; workbench validators/tests plus npm lint/build pass
- **Gate:** none
- **Last proof:** commit:752da1ae46d60a4b5b62d553e51314dba905fb2c workflow:31441430845 proved contract tests, Oxlint, TypeScript/Vite build, and diff check; workflow:31441430835 proved full repository validation
- **Next action:** none; no safe actionable work remains
- **Updated:** 2026-08-10T19:18:00-04:00

## SSQ-003 — Prove the first real Practice Workbench execution adapter

- **Status:** DONE
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** sqlite-practice-runner-20260826
- **Branch / PR:** `feat/sqlite-practice-runner-20260826` / #20
- **Scope:** implement exactly one runner adapter behind `harness/practice-workbench.v1.json`; prove success, guest failure normalization, and timeout/cancellation while keeping the host shell usable; update only that runner status after proof
- **Forbidden:** implementing multiple language runners in one sprint; direct browser `eval` or `new Function`; cloud execution service; secrets; weakening the premise-first packet or mastery contracts; unrelated curriculum rewrites
- **Dependencies:** SSQ-001, SSQ-002
- **References:** `harness/workflows/PRACTICE_WORKBENCH.md`, `scripts/sql-runner.py`, `tests/test_sql_runner.py`, `harness/practice-workbench.v1.json`
- **Acceptance gate:** one adapter has targeted pass/failure/timeout tests; guest exceptions/errors normalize to registered `ExecutionOutcome`; the React shell remains recoverable; owning validator plus npm run lint and npm run build pass; runner status matches observed runtime proof
- **Gate:** none
- **Last proof:** commit:c3711d81c358a7e77bbc36afe58dda08974ac528 workflow:33037590036 proved Practice Workbench validator, contract tests, 11 SQL runner boundary/regression cases, Oxlint, Vite build, and diff whitespace; workflow:33037590037 proved the repository ledger/frontier contract on Ubuntu and Windows; workflow:33037590068 proved the full registered harness on the same exact candidate
- **Next action:** none; no safe actionable work remains
- **Updated:** 2026-08-26T23:52:00-04:00

## SSQ-004 — Verify integrated SQL runner on the canonical Windows checkout

- **Status:** OPERATOR
- **Priority:** P0
- **Work class:** BOUNDED
- **Owner:** windows-operator-20260827
- **Branch / PR:** `main` / #22 integrated
- **Scope:** prove that the integrated SQL Practice Workbench adapter is present and executable from the repository-owned canonical Windows checkout or a preservation-first worktree pinned to refreshed `origin/main`; capture canonical-path resolution, workbench validation, SQL runner regression tests, registered runner identity, and one live `SELECT 1` outcome through the repository-owned single field-proof entrypoint
- **Forbidden:** treating pasted commands as executed evidence; inventing `FIELD_PROOF=PASS`; requiring a multi-statement interactive `if`/`else` paste; overwriting dirty or separately owned Windows work; force-resetting or force-pulling the canonical checkout; using a noncanonical fallback clone; allowing provider CI to masquerade as workstation proof; adding the next feature sprint before this runtime gate is dispositioned
- **Dependencies:** SSQ-003
- **References:** `scripts/Invoke-StudySyndicateSqlFieldProof.ps1`, `scripts/Resolve-StudySyndicateRepo.ps1`, `scripts/validate-practice-workbench.py`, `scripts/sql-runner.py`, `tests/test_sql_field_proof_contract.py`, `tests/test_sql_runner.py`, `harness/canonical-paths.v1.json`, `harness/practice-workbench.v1.json`, `harness/reports/STATE.md`
- **Acceptance gate:** operator evidence from `scripts/Invoke-StudySyndicateSqlFieldProof.ps1` shows `FIELD_PROOF=PASS`, proves SQL integration `62872f9f442582b076e79f94d046fe4d4792126d` is contained in the exact refreshed target SHA, uses the canonical checkout or preservation-first isolated worktree, passes the owning workbench validator and SQL runner tests, resolves `sql-session` to `scripts/sql-runner.py`, and returns a strict JSON `passed` outcome whose first result value is `1`
- **Gate:** inaccessible Windows workstation runtime; the 2026-08-27 operator attempt proved remote ancestry but failed before field execution because an interactive PowerShell `else` was submitted as a separate statement, so no `FIELD_PROOF=PASS` exists yet
- **Last proof:** merge:bf135467bc2d3a93fc66caa5e67aea4e97e7a566 workflow:33093146754 proved the single-entrypoint repair through exact-candidate full harness, application HTTP E2E, guarded merge, containment, and promotion receipt; workflow:33092935741 proved the same field-proof entrypoint on a Windows provider runner with workbench validation, 11 SQL regression cases, registered adapter resolution, and `SELECT 1`, emitting only `PROVIDER_FIELD_PROOF=PASS`; operator-proof:interactive-paste-failed-before-field-execution
- **Next action:** execute `scripts/Invoke-StudySyndicateSqlFieldProof.ps1` as one PowerShell file invocation from the canonical Windows environment and record its `FIELD_PROOF=PASS`, proof mode, and exact target SHA before creating the next feature task
- **Updated:** 2026-08-27T12:27:00-04:00
