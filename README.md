# StudySyndicate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local-first PMP study app for multimedia flashcards, recall drills, weak-area tracking, and adaptive practice.

## Purpose

StudySyndicate helps PMP candidates build their own study system instead of relying on rigid flashcard tools. It supports text, image, audio, and video-based cards, tracks weak areas, and recommends targeted practice based on review history.

## Core Features

- Local-first storage
- PMP domain and competency mapping
- Multimedia flashcards
- Scenario-based exercises
- Free recall with rubric-based scoring
- Weak-area dashboard
- Spaced repetition scheduling
- Import/export support

## MVP Stack

- Vite
- React
- TypeScript
- Dexie.js
- IndexedDB
- ts-fsrs

## Storage Model

Primary data should use IndexedDB through Dexie.js. Browser localStorage should only be used for lightweight preferences.

## Domain Model

Model the app around a factored abstraction so actors, relationships, and components remain explicit as the study engine grows. Start with durable actors such as learners, sources, concepts, prompts, responses, sessions, attempts, and media; connect them through typed relationships; and attach content, scoring, scheduling, provenance, and UI details as components. See [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md) for the working model and [`src/domain/factored.ts`](src/domain/factored.ts) for the initial TypeScript contracts.

## PMP Study System Doctrine

StudySyndicate is a study system, not merely a flashcard app: `source-note` -> `atomic-concept`
-> `exercise-variants` -> `review-attempts` -> `mastery-weakness-map` ->
`recommended-practice-queue`. The canonical product architecture, PMP source model, core
entities, exercise taxonomy, grading doctrine, weakness/mastery model, session modes, phased
build order, and MVP acceptance contract are defined in
[`docs/PMP_STUDY_SYSTEM.md`](docs/PMP_STUDY_SYSTEM.md) with a machine-readable companion at
[`content/pmp/mvp-spec.v1.json`](content/pmp/mvp-spec.v1.json).

Validate the doctrine and MVP spec with:

```bash
python scripts/validate-pmp-doctrine.py
```

## Software Foundations Practice

Resume-visible software skill claims have a dedicated practice contract with **SQL as the
primary lane**, **Rust as the secondary lane**, and a smaller maintenance lane for other
public claims. The pack is evidence-oriented: skills move from `exposed` to `practicing` to
`defensible` through no-AI reconstruction, explanation, and mastery gates rather than visual
confidence scores alone.

See [`docs/software/SQL_RUST_FOUNDATIONS.md`](docs/software/SQL_RUST_FOUNDATIONS.md) for the
study doctrine and [`content/software/sql-rust-foundations.v1.json`](content/software/sql-rust-foundations.v1.json)
for the machine-readable modules, exercises, cadence, mastery gates, and `taskq` Rust + SQLite
integration project.

Validate the foundations pack with:

```bash
python scripts/validate-software-foundations.py
```

## Seed Study Content

The first reusable study pack captures the fraction-comparison mental models developed for mental arithmetic: landmark comparisons, gap-from-one reasoning, residuals, common-numerator scaling, and an exact cross-multiplication fallback. See [`docs/mental-math/FRACTION_COMPARISON.md`](docs/mental-math/FRACTION_COMPARISON.md) for the playbook and [`content/mental-math/fraction-comparison.v1.json`](content/mental-math/fraction-comparison.v1.json) for flashcards and practice problems.

Validate that seed content with:

```bash
python scripts/validate-mental-math-content.py
```

## UI Principles

Use AxTask-inspired product principles when the app shell is scaffolded later:

- Keep primary actions obvious and close to the user's current study context.
- Favor calm, task-oriented screens over decorative chrome.
- Use compact dashboards that expose progress, weak areas, and next actions without requiring navigation.
- Make local-first state visible: import, export, backup, and sync status should be easy to find.
- Design empty states as setup guides so the first study loop is clear.

## Repository Hygiene

This repository is intentionally light until the app is scaffolded. Before adding a framework, keep the default branch clean and avoid committing generated artifacts, dependency folders, local environment files, or editor-specific state.

## Repository Files

- `README.md` — project overview, stack, storage model, study content, and UI principles.
- `LICENSE` — MIT license for reuse and distribution terms.
- `.gitignore` — Node-friendly ignore rules for dependencies, build output, caches, environment files, and editor artifacts.
- `docs/DOMAIN_MODEL.md` — factored actor, relationship, and component abstraction for the study engine.
- `src/domain/factored.ts` — initial TypeScript contracts for actors, relationships, and components.
- `docs/PMP_STUDY_SYSTEM.md` — canonical PMP study system doctrine and MVP specification.
- `content/pmp/mvp-spec.v1.json` — machine-readable MVP contract for entities, exercises, grading, sources, competency mapping, weakness policy, session modes, and build order.
- `scripts/validate-pmp-doctrine.py` — validator enforcing the PMP doctrine sections and MVP spec structural completeness.
- `docs/software/SQL_RUST_FOUNDATIONS.md` — canonical SQL/Rust resume-claim practice doctrine, mastery gates, and `taskq` integration project.
- `content/software/sql-rust-foundations.v1.json` — machine-readable SQL/Rust modules, exercises, cadence, maintenance roster, and acceptance contract.
- `scripts/validate-software-foundations.py` — validator enforcing the software-foundations doctrine and machine-readable practice pack.
- `docs/mental-math/FRACTION_COMPARISON.md` — canonical fraction-comparison mental models and fallback ladder.
- `content/mental-math/fraction-comparison.v1.json` — reusable flashcards, exact practice problems, strategy paths, and answer explanations.
- `scripts/validate-mental-math-content.py` — exact-rational validator for the mental-math seed.
- `docs/SPRINT_HANDOFF.md` — handoff notes, known gaps, risks, targets, and next-agent plan.

## License

This project is licensed under the [MIT License](LICENSE).
