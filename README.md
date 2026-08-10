# StudySyndicate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local-first study app for multimedia flashcards, recall drills, weak-area tracking, adaptive practice,
and evidence-oriented software-skills work.

## Purpose

StudySyndicate helps learners build their own study system instead of relying on rigid flashcard tools.
It supports text, image, audio, and video-based cards, tracks weak areas, recommends targeted practice,
and turns public software-skill claims into repeatable evidence-backed exercises.

## Core Features

- Local-first storage model
- PMP domain and competency mapping
- Multimedia flashcards
- Reusable voice, image, and video media nodes
- Portable media bundles with integrity-checked saved files
- Scenario-based exercises
- Free recall with rubric-based scoring
- Weak-area dashboard
- Spaced repetition scheduling
- SQL/Rust/software-foundations practice
- Arrays/algorithms mastery practice
- Multi-language Practice Workbench
- Import/export support

## MVP Stack

- Vite
- React
- TypeScript
- Dexie.js
- IndexedDB
- ts-fsrs

The browser shell is now scaffolded with Vite/React/TypeScript. Dexie/IndexedDB persistence remains a
separate product sprint rather than being silently introduced by the Practice Workbench.

## Browser App

Install dependencies and run the local application with:

```bash
npm install
npm run dev
```

Lint and build the production bundle with:

```bash
npm run lint
npm run build
```

`dist/` and `node_modules/` are generated/ignored outputs and must not be committed.

## Storage Model

Primary structured data should use IndexedDB through Dexie.js. Browser localStorage should only be used
for lightweight preferences. Binary image/audio/video assets are local files/blobs referenced by reusable
media nodes; they are never embedded directly inside prompt or response records.

The current Practice Workbench intentionally keeps attempt text in component state until the persistence
contract is implemented; it does not invent a competing storage model.

## Domain Model

Model the app around a factored abstraction so actors, relationships, and components remain explicit as the
study engine grows. Start with durable actors such as learners, sources, concepts, prompts, responses,
sessions, attempts, and media; connect them through typed relationships; and attach content, scoring,
scheduling, provenance, and UI details as components. See [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md)
and [`src/domain/factored.ts`](src/domain/factored.ts).

## Multimodal Media and Voice Nodes

Audio, images, and video are first-class reusable `media` actors. A flashcard attaches them through
`uses-media` relationships plus `media-usage` components, so the same voice explanation or visual can be
reused without duplicating the binary asset.

Spoken audio carries a transcript and language. Meaningful images carry alt text. Generated voice nodes
retain provenance and source-text integrity metadata without storing credentials.

Full media portability is part of the local-first floor: a bundle carries `study.json`, `manifest.json`,
and SHA-256-addressed binary assets. See [`docs/MULTIMODAL_MEDIA.md`](docs/MULTIMODAL_MEDIA.md) and
[`content/media/multimodal-media-contract.v1.json`](content/media/multimodal-media-contract.v1.json).

Validate the contract and bundle behavior with:

```bash
python scripts/validate-multimodal-media.py
python scripts/test-media-bundle.py
```

Pack or validate a concrete bundle with:

```bash
python scripts/media-bundle.py pack --descriptor media-source.json --assets-root assets --study-json study.json --output study-media.zip
python scripts/media-bundle.py validate study-media.zip
```

## PMP Study System Doctrine

StudySyndicate is a study system, not merely a flashcard app: `source-note` -> `atomic-concept` ->
`exercise-variants` -> `review-attempts` -> `mastery-weakness-map` -> `recommended-practice-queue`.
The canonical architecture and MVP contract are defined in [`docs/PMP_STUDY_SYSTEM.md`](docs/PMP_STUDY_SYSTEM.md)
with a machine-readable companion at [`content/pmp/mvp-spec.v1.json`](content/pmp/mvp-spec.v1.json).

Validate the doctrine and MVP spec with:

```bash
python scripts/validate-pmp-doctrine.py
```

## Software Foundations Practice

Resume-visible software skill claims have a dedicated practice contract with **SQL as the primary lane**,
**Rust as the secondary lane**, and a smaller maintenance lane for other public claims. Skills move from
`exposed` to `practicing` to `defensible` through no-AI reconstruction, explanation, and mastery gates.

See [`docs/software/SQL_RUST_FOUNDATIONS.md`](docs/software/SQL_RUST_FOUNDATIONS.md) and
[`content/software/sql-rust-foundations.v1.json`](content/software/sql-rust-foundations.v1.json).

Validate the foundations pack with:

```bash
python scripts/validate-software-foundations.py
```

## Arrays and Algorithms Mastery

Arrays have a dedicated evidence-oriented track beginning with **Two Sum front to back**: correct brute
force, complement reasoning, hash-map optimization, edge-case defense, complexity explanation, blank-file
no-AI reconstruction, and transfer.

See [`docs/software/ARRAYS_MASTERY.md`](docs/software/ARRAYS_MASTERY.md),
[`content/software/arrays-mastery.v1.json`](content/software/arrays-mastery.v1.json), and
[`practice/arrays/two_sum.py`](practice/arrays/two_sum.py).

Validate the contract and run the kata harness with:

```bash
python scripts/validate-arrays-mastery.py
python tests/test_two_sum.py
```

## Practice Workbench

The browser Practice Workbench is the visual renderer for the study contracts, not a second curriculum
authority. A session is configured through a modal with four explicit dimensions:

- study target
- facet (`understand`, `implement`, `test`, `explain`, or `docs`)
- language/runtime
- study mode (`guided`, `docs-assisted`, or `mastery`)

The workbench renders **premise -> workspace -> feedback** as draggable panels. The editor deliberately
remains usable as a plain text/Notepad-style surface when richer language services are unavailable.

Two Sum is rendered from [`harness/problems/two-sum.v1.json`](harness/problems/two-sum.v1.json).
The arrays roadmap is sourced from `content/software/arrays-mastery.v1.json`, and SQL/Rust exercises are
sourced from the existing foundations pack. Runner capability and failure semantics are owned by [`harness/practice-workbench.v1.json`](harness/practice-workbench.v1.json).

The language registry currently includes Python, Rust, SQL, C, JavaScript, TypeScript, Java, and Lua.
A language appearing in the UI does **not** imply that browser execution exists. Guest failures must be
caught/received by the runner adapter and normalized to an `ExecutionOutcome`; the React shell must stay
usable. For embedded Lua, a raised Lua error is caught by the host and returned as `runtime-error` rather
than becoming a host-shell crash.

Direct browser `eval`/`new Function` learner-code execution is not approved at this floor.

Validate the workbench contract with:

```bash
python scripts/validate-practice-workbench.py
python tests/test_practice-workbench_contract.py
```

## Operational Harness

The repository has a tracked operational harness for agents and operators. Start at
[`harness/README.md`](harness/README.md), inspect the repo with `python scripts/harness.py inspect`, and
select a workflow with `python scripts/harness.py workflows`.

The harness also treats technologies presented on **ParallaxPort** as versioned study fodder. The source
snapshot is [`harness/sources/parallaxport-claims.v1.json`](harness/sources/parallaxport-claims.v1.json)
and the generated human queue is
[`harness/reports/PARALLAXPORT_STUDY_FODDER.md`](harness/reports/PARALLAXPORT_STUDY_FODDER.md).
Public claims create practice priority; they do not count as mastery proof.

For guided problem mechanics:

```bash
python scripts/harness.py start guided-study
python scripts/study-problem.py render two-sum --mode guided --format comments
```

Run the harness validation floor with:

```bash
python scripts/harness.py validate --level quick
python scripts/harness.py validate --level full
```

Full validation expects Node dependencies to be installed and includes the application lint/build.

## Seed Study Content

The first reusable study pack captures fraction-comparison mental models: landmark comparisons,
gap-from-one reasoning, residuals, common-numerator scaling, and an exact cross-multiplication fallback.
See [`docs/mental-math/FRACTION_COMPARISON.md`](docs/mental-math/FRACTION_COMPARISON.md) and
[`content/mental-math/fraction-comparison.v1.json`](content/mental-math/fraction-comparison.v1.json).

Validate that seed content with:

```bash
python scripts/validate-mental-math-content.py
```

## UI Principles

- Keep primary actions obvious and close to the current study context.
- Recite the premise before context-dependent questions or code.
- Make study mode and runner capability visible; never imply mastery or execution from appearance alone.
- Favor calm, task-oriented screens over decorative chrome.
- Use compact dashboards that expose progress, weak areas, and next actions without requiring navigation.
- Preserve a plain-text fallback even when richer editors or language services are introduced.
- Drag-and-drop may change presentation, never source authority, grading, or runner semantics.
- Let media presentation be context-sensitive: audio-first, visual-first, multimodal, or text fallback.
- Design empty states as setup guides so the first study loop is clear.

## Repository Hygiene

Keep the default branch clean and avoid committing generated artifacts, dependency folders, local
environment files, editor-specific state, user media bundles, or local study attempts. In particular,
`node_modules/`, `dist/`, `local-study-exports/`, and `media-bundles/` remain machine-local/generated.

## Repository Files

Key operational/application paths include:

- `package.json` — browser app scripts and dependencies.
- `src/App.tsx` — Practice Workbench shell and draggable panel surface.
- `src/components/PracticeModal.tsx` — target/facet/language/mode session configuration.
- `src/practice/` — UI practice catalog, capability registry binding, execution outcomes, and types.
- `harness/practice-workbench.v1.json` — canonical language/runner/UI capability contract.
- `harness/workflows/PRACTICE_WORKBENCH.md` — workbench operating workflow.
- `harness/skills/runner-adapter/SKILL.md` — bounded procedure for adding execution adapters.
- `scripts/validate-practice-workbench.py` — cross-file workbench validator.
- `tests/test_practice_workbench_contract.py` — language/runner/modal/drag-drop contract tests.
- `docs/DOMAIN_MODEL.md` / `src/domain/factored.ts` — factored study-domain authority.
- `docs/MULTIMODAL_MEDIA.md` / `content/media/multimodal-media-contract.v1.json` — media authority.
- `docs/PMP_STUDY_SYSTEM.md` / `content/pmp/mvp-spec.v1.json` — PMP study-system authority.
- `docs/software/SQL_RUST_FOUNDATIONS.md` / `content/software/sql-rust-foundations.v1.json` — SQL/Rust authority.
- `docs/software/ARRAYS_MASTERY.md` / `content/software/arrays-mastery.v1.json` — arrays authority.
- `harness/problems/two-sum.v1.json` — canonical premise-first Two Sum packet.
- `.ai/WORK_QUEUE.md` — deterministic repository coordination frontier.

## License

This project is licensed under the [MIT License](LICENSE).
