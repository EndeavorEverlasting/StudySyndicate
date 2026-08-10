# StudySyndicate

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local-first PMP study app for multimedia flashcards, recall drills, weak-area tracking, and adaptive practice.

## Purpose

StudySyndicate helps PMP candidates build their own study system instead of relying on rigid flashcard tools. It supports text, image, audio, and video-based cards, tracks weak areas, and recommends targeted practice based on review history.

## Core Features

- Local-first storage
- PMP domain and competency mapping
- Multimedia flashcards
- Reusable voice, image, and video media nodes
- Portable media bundles with integrity-checked saved files
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

Primary structured data should use IndexedDB through Dexie.js. Browser localStorage should only be used for lightweight preferences. Binary image/audio/video assets are local files/blobs referenced by reusable media nodes; they are never embedded directly inside prompt or response records.

## Domain Model

Model the app around a factored abstraction so actors, relationships, and components remain explicit as the study engine grows. Start with durable actors such as learners, sources, concepts, prompts, responses, sessions, attempts, and media; connect them through typed relationships; and attach content, scoring, scheduling, provenance, and UI details as components. See [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md) for the working model and [`src/domain/factored.ts`](src/domain/factored.ts) for the initial TypeScript contracts.

## Multimodal Media and Voice Nodes

Audio, images, and video are first-class reusable `media` actors. A flashcard attaches them through
`uses-media` relationships plus `media-usage` components, so the same voice explanation or
visual can be reused without duplicating the binary asset.

Spoken audio carries a transcript and language. Meaningful images carry alt text. Generated
voice nodes retain provenance and source-text integrity metadata without storing credentials.

Full media portability is part of the local-first floor: a bundle carries `study.json`,
`manifest.json`, and SHA-256-addressed binary assets. The repository includes a pack/validate
utility so this file contract can be proven before the browser UI exists.

See [`docs/MULTIMODAL_MEDIA.md`](docs/MULTIMODAL_MEDIA.md) and
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

## Arrays and Algorithms Mastery

Arrays have a dedicated evidence-oriented track beginning with **Two Sum front to back**:
correct brute force, complement reasoning, hash-map optimization, edge-case defense,
complexity explanation, blank-file no-AI reconstruction, and transfer. The track then advances
through membership/frequency maps, running state, prefix/suffix structure, two pointers,
windows, binary search, and an unfamiliar-problem capstone.

See [`docs/software/ARRAYS_MASTERY.md`](docs/software/ARRAYS_MASTERY.md) for the doctrine,
[`content/software/arrays-mastery.v1.json`](content/software/arrays-mastery.v1.json) for the
machine-readable roadmap and evidence contract, and [`practice/arrays/two_sum.py`](practice/arrays/two_sum.py)
for the known-good reference implementations.

Validate the contract and run the kata harness with:

```bash
python scripts/validate-arrays-mastery.py
python tests/test_two_sum.py
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
- Let media presentation be context-sensitive: audio-first, visual-first, multimodal, or text fallback.
- Design empty states as setup guides so the first study loop is clear.

## Repository Hygiene

This repository is intentionally light until the app is scaffolded. Before adding a framework, keep the default branch clean and avoid committing generated artifacts, dependency folders, local environment files, editor-specific state, or user media bundles.

## Repository Files

- `README.md` — project overview, stack, storage model, study content, and UI principles.
- `LICENSE` — MIT license for reuse and distribution terms.
- `.gitignore` — Node-friendly ignore rules for dependencies, build output, caches, environment files, and local media exports.
- `docs/DOMAIN_MODEL.md` — factored actor, relationship, component, and reusable media-node abstraction.
- `src/domain/factored.ts` — TypeScript contracts for actors, relationships, components, media assets, voice metadata, and media usage.
- `docs/MULTIMODAL_MEDIA.md` — canonical multimodal media, voice-node, accessibility, and portable bundle doctrine.
- `content/media/multimodal-media-contract.v1.json` — machine-readable media kinds, roles, usage modes, asset fields, bundle format, and acceptance contract.
- `scripts/media-bundle.py` — portable media bundle pack/validate utility.
- `scripts/test-media-bundle.py` — executable positive/negative bundle integrity tests.
- `scripts/validate-multimodal-media.py` — validator enforcing media doctrine, domain coupling, portability, and PMP alignment.
- `docs/PMP_STUDY_SYSTEM.md` — canonical PMP study system doctrine and MVP specification.
- `content/pmp/mvp-spec.v1.json` — machine-readable MVP contract for entities, exercises, grading, sources, competency mapping, weakness policy, session modes, build order, and Phase 1 media portability.
- `scripts/validate-pmp-doctrine.py` — validator enforcing the PMP doctrine, media portability contract, and MVP spec structural completeness.
- `docs/software/SQL_RUST_FOUNDATIONS.md` — canonical SQL/Rust resume-claim practice doctrine, mastery gates, and `taskq` integration project.
- `content/software/sql-rust-foundations.v1.json` — machine-readable SQL/Rust modules, exercises, cadence, maintenance roster, and acceptance contract.
- `scripts/validate-software-foundations.py` — validator enforcing the software-foundations doctrine and machine-readable practice pack.
- `docs/software/ARRAYS_MASTERY.md` — canonical arrays/algorithms mastery doctrine, Two Sum gate, 45-minute session loop, roadmap, and public-safe proof contract.
- `content/software/arrays-mastery.v1.json` — machine-readable arrays roadmap, Two Sum invariants, exercises, evidence ledger, and acceptance contract.
- `practice/arrays/two_sum.py` — known-good brute-force and hash-map Two Sum reference implementations.
- `tests/test_two_sum.py` — dependency-free Two Sum correctness and edge-case harness.
- `scripts/validate-arrays-mastery.py` — validator enforcing the arrays doctrine, roadmap, evidence contract, and executable-kata surface.
- `docs/mental-math/FRACTION_COMPARISON.md` — canonical fraction-comparison mental models and fallback ladder.
- `content/mental-math/fraction-comparison.v1.json` — reusable flashcards, exact practice problems, strategy paths, and answer explanations.
- `scripts/validate-mental-math-content.py` — exact-rational validator for the mental-math seed.
- `docs/SPRINT_HANDOFF.md` — handoff notes, known gaps, risks, targets, and next-agent plan.

## License

This project is licensed under the [MIT License](LICENSE).
