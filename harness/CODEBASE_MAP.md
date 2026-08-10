# Codebase Map

## Repository purpose

StudySyndicate is a local-first study-system repository. The current floor is contract-first:
study doctrine, machine-readable packs, reference practice code, validators, media bundle tooling,
and an operational repository ledger/harness exist before the full browser application shell is scaffolded.

## Top-level structure

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Canonical governance contract. Harness work must not duplicate or weaken it. |
| `README.md` | Human entry point and current feature/command summary. |
| `.ai/` | Canonical repository coordination ledger, adoption metadata, and bounded frontier policy. |
| `docs/` | Canonical study, domain, media, and practice doctrine. |
| `content/` | Machine-readable study contracts and reusable content packs. |
| `practice/` | Known-good reference implementations used as study material. |
| `src/` | Product/domain TypeScript contracts; product changes are outside harness scope. |
| `tests/` | Executable practice and harness tests. |
| `scripts/` | Validators, media bundle tooling, ledger/frontier tooling, repository locator, and harness CLI. |
| `.github/workflows/` | Pull-request CI for governance and owned contracts. |
| `harness/` | Operational map, workflows, registries, skills, source adapters, and reports. |
| `.githooks/` | Optional tracked pre-commit/pre-push harness checks. |
| `local-study-exports/` | Ignored operator-owned session/evidence exports when created locally. |
| `media-bundles/` | Ignored local portable media bundles when created. |

## Canonical entry points

- Governance: `AGENTS.md`
- Harness: `harness/README.md`
- Work ledger: `.ai/WORK_QUEUE.md`
- Bounded frontier: `scripts/get-repo-ledger-frontier.py`
- Repository-location recovery: `harness/workflows/REPO_LOCATION_RECOVERY.md`
- Windows repository locator: `scripts/Resolve-StudySyndicateRepo.ps1`
- Domain contracts: `src/domain/factored.ts`
- PMP doctrine: `docs/PMP_STUDY_SYSTEM.md`
- Multimodal media doctrine: `docs/MULTIMODAL_MEDIA.md`
- Software foundations: `docs/software/SQL_RUST_FOUNDATIONS.md`
- Arrays mastery: `docs/software/ARRAYS_MASTERY.md`
- Two Sum reference: `practice/arrays/two_sum.py`
- Public-claim study source: `harness/sources/parallaxport-claims.v1.json`

## Configuration and registries

- `.gitignore` — machine-local and generated-output exclusions.
- `.ai/repository-work-ledger.policy.json` — local bounded/unbounded execution profile.
- `harness/harness-manifest.v1.json` — harness component/workflow authority.
- `harness/artifact-registry.v1.json` — output locations and naming.
- `harness/validation-manifest.v1.json` — command authority for quick/full validation.
- `.github/workflows/*.yml` — remote CI.
- No root `package.json` or application build manifest exists at this floor.

## Local checkout and worktree behavior

Repository identity comes from Git, not from the shell prompt or a folder name. The common durable Windows clone is:

`C:\Users\<user>\Desktop\Dev\StudySyndicate`

`C:\Users\<user>\dev\StudySyndicate` is a different path because it omits `Desktop`. A detached worktree under `%TEMP%\StudySyndicate-*` may be valid for a bounded task, but it is not the durable clone.

When the current directory is uncertain, use `git -C <candidate> ...` and prove both the top-level root and canonical origin before mutation. See `harness/workflows/REPO_LOCATION_RECOVERY.md`.

Tracked location verification from a reachable checkout:

```powershell
pwsh -NoLogo -NoProfile -File scripts/Resolve-StudySyndicateRepo.ps1 -Json
```

## Build, test, validation, deploy

### Harness

```bash
python scripts/harness.py validate --level quick
python scripts/harness.py validate --level full
```

### Individual validators

```bash
bash scripts/validate-governance.sh
python scripts/validate-repo-ledger.py
python tests/test_repo_ledger_contract.py
python tests/test_repo_ledger_frontier.py
python scripts/validate-pmp-doctrine.py
python scripts/validate-software-foundations.py
python scripts/validate-arrays-mastery.py
python tests/test_two_sum.py
python scripts/validate-multimodal-media.py
python scripts/test-media-bundle.py
python scripts/validate-mental-math-content.py
pwsh -NoLogo -NoProfile -File scripts/Test-RepoLocationRecovery.ps1
```

### Artifact builders

```bash
python scripts/harness.py study-fodder
python scripts/media-bundle.py pack --descriptor media-source.json --assets-root assets --study-json study.json --output study-media.zip
python scripts/media-bundle.py validate study-media.zip
```

### Lint/format floor

There is no repository-wide formatter or linter configured yet. The current enforced static floor is
Python compilation for harness scripts plus `git diff --check`. Do not invent a formatter contract
without a dedicated sprint.

### Application build/deploy floor

The full Vite/React application shell described by the product doctrine is not yet scaffolded in the
repository root, so there is no honest root application build or StudySyndicate deployment command
to run. Current executable build verification is contract validation, reference-kata execution, and
media-bundle pack/validate behavior. Never claim browser/runtime/deployment proof from these checks.
