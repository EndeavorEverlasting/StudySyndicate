# Codebase Map

## Repository purpose

StudySyndicate is a local-first study system with contract-first study content plus a Vite/React/TypeScript
Practice Workbench. The browser is a renderer over repository-owned study/harness authority rather than a
second source of curriculum truth. Learning events are also modeled as evidence: direct facet credit,
assistance provenance, bounded cascade recognition, and mastery boundaries are repository-owned contracts.

## Top-level structure

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Canonical governance contract. |
| `README.md` | Human entry point, app commands, and study tracks. |
| `.ai/` | Repository coordination ledger and bounded frontier. |
| `docs/` | Study, domain, media, practice, and learning-evidence doctrine. |
| `content/` | Machine-readable study contracts, exercise packs, and learning-evidence contracts. |
| `practice/` | Known-good reference implementations. |
| `src/` | React app, Practice Workbench UI, practice registry adapters, and domain contracts. |
| `tests/` | Executable practice, harness, ledger, workbench, learning-evidence, and promotion tests. |
| `scripts/` | Validators, media tooling, ledger/frontier, canonical path resolver, promotion policy/E2E, study checker, evidence engine, and harness CLI. |
| `harness/` | Operational map, path/promotion contracts, workflows, registries, problem packets, skills, sources, and reports. |
| `.github/workflows/` | Pull-request validation plus guarded exact-candidate main promotion. |
| `dist/` | Ignored Vite production build output. |
| `local-study-exports/` | Ignored operator-owned study attempts/evidence. |

## Canonical entry points

- Governance: `AGENTS.md`
- Browser app: `src/main.tsx` -> `src/App.tsx`
- Windows canonical development/use/worktree path authority: `harness/canonical-paths.v1.json`
- Canonical path resolver and receipt: `scripts/Resolve-StudySyndicateRepo.ps1`
- Exact-candidate main promotion authority: `harness/promotion-contract.v1.json`
- Promotion provider workflow: `.github/workflows/promote-main.yml`
- Promotion policy/receipt helper: `scripts/promotion.py`
- Application HTTP E2E: `scripts/application-e2e.py`
- Practice Workbench contract: `harness/practice-workbench.v1.json`
- Practice Workbench workflow: `harness/workflows/PRACTICE_WORKBENCH.md`
- Learning-evidence doctrine: `docs/LEARNING_EVIDENCE_DOCTRINE.md`
- Learning-evidence contract: `content/learning/learning-evidence.v1.json`
- Learning-event engine: `scripts/learning-evidence.py`
- Learning-event workflow: `harness/workflows/LEARNING_EVENT_CASCADE.md`
- Problem-packet contract: `harness/problems/problem-packet-contract.v1.json`
- Two Sum packet: `harness/problems/two-sum.v1.json`
- Software foundations pack: `content/software/sql-rust-foundations.v1.json`
- Harness: `harness/README.md`
- Work ledger: `.ai/WORK_QUEUE.md`
- Bounded frontier: `scripts/get-repo-ledger-frontier.py`

## App configuration

- `package.json` — Vite/React dependencies plus `dev`, `build`, `lint`, and workbench validation scripts.
- `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` — TypeScript project configuration.
- `vite.config.ts` — Vite React plugin configuration.
- `index.html` — browser entry document.

## Build, test, validation

```bash
npm install
npm run lint
npm run build
python scripts/validate-canonical-paths.py
python scripts/validate-promotion.py
python tests/test_promotion_contract.py
python scripts/validate-practice-workbench.py
python tests/test_practice-workbench_contract.py
python scripts/learning-evidence.py validate-contract
python tests/test_learning_evidence_engine.py
python scripts/harness.py validate --level quick
python scripts/harness.py validate --level full
```

`python scripts/harness.py validate --level full` is the repository convergence check and includes application
lint/build proof. A fresh checkout must install Node dependencies before full validation.

The promotion workflow deliberately runs that full harness first and then runs the distinct application HTTP
E2E through the built Vite preview entrypoint. Harness E2E and application E2E are separate proof levels.

## Location boundary

For the Windows operator profile, the repository-owned rule resolves the Windows Desktop Known Folder and
appends `Dev\StudySyndicate`. Normal local use shares that checkout and enters through `npm run dev`.
Parallel writers use the sibling `Dev\StudySyndicate-worktrees` root. Alternate checkouts do not become
canonical because they are convenient; preserve unique work and diagnose drift before moving or cloning.

## Learning evidence boundary

A learning event may earn direct partial credit for `construct`, `apply`, `debug`, `explain`, and `discover`.
The recorded assistance band caps the event claim. Explicit prerequisite/adjacent relationships may receive
bounded cascade recognition, but derived credit never counts toward mastery. One event can emit a mastery
signal only; aggregate direct repetitions and transfer are required for a mastery claim.

## Execution boundary

The app does not infer executable capability from the selected language. Runner availability and failure
semantics come from `harness/practice-workbench.v1.json`. Guest throws/panics/compiler failures/database
errors/process failures/timeouts become normalized outcomes at the adapter boundary. The React host remains
mounted and recoverable.

No browser `eval`/`new Function` learner-code execution is approved at this floor.

## Promotion and deploy floor

`harness/promotion-contract.v1.json` and `.github/workflows/promote-main.yml` own guarded integration of an
exact validated pull-request head into `main`. Promotion requires the canonical full harness plus distinct
application HTTP E2E, rechecks the head immediately before mutation, squash-merges with an expected-head
SHA, proves containment, and emits a provider receipt.

This is **repository integration**, not a hosted-product deployment. A production build exists through
`npm run build`, but no external hosting/deployment contract has been adopted. Likewise, a successful GitHub
promotion does not prove the Windows canonical checkout/use path has been refreshed or that `npm run dev`
has been observed there.
