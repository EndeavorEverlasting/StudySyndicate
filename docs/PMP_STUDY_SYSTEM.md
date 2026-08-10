# PMP Study System Doctrine

Status: canonical product architecture for the StudySyndicate PMP study engine.

This document is the human-readable authority for what StudySyndicate is and what the
local-first MVP must deliver. Its machine-readable companion is
[`content/pmp/mvp-spec.v1.json`](../content/pmp/mvp-spec.v1.json), and both are enforced by
[`scripts/validate-pmp-doctrine.py`](../scripts/validate-pmp-doctrine.py). The factored data
abstraction that implements these entities lives in [`docs/DOMAIN_MODEL.md`](DOMAIN_MODEL.md).
Reusable image/audio/video nodes and portable media bundles are defined by
[`docs/MULTIMODAL_MEDIA.md`](MULTIMODAL_MEDIA.md).

## Product Vision

StudySyndicate is a study system, not merely a flashcard app. A flashcard is one exercise
variant among many. The product exists to turn raw source material into durable PMP judgment
by tracking what a learner actually gets wrong and steering practice toward it.

## Learning Model

The engine models a single directed pipeline:

`source-note` -> `atomic-concept` -> `exercise-variants` -> `review-attempts` ->
`mastery-weakness-map` -> `recommended-practice-queue`

Each stage is an explicit record so the system can explain every recommendation from its
evidence rather than from opaque scoring.

## Local-First Architecture

The MVP runs entirely in the browser with no backend or cloud dependency.

- Runtime: browser app.
- Structured data: IndexedDB through Dexie.js.
- Binary media: blobs/files for image, audio, and video.
- Preferences: `localStorage` only for tiny preferences, never primary study data.
- Structured portability: `study.json` round-trips the complete structured study dataset,
  including media records, metadata, provenance, and stable media references. JSON does not
  embed binary image/audio/video payloads.
- Full media portability: a Phase 1 media bundle carries `study.json`, `manifest.json`, and
  integrity-addressed binary assets. Directory and ZIP transports are both valid; import
  verifies SHA-256 and byte length before trusting saved audio/image/video files.
- Scheduling: FSRS-compatible spaced repetition.

Binary media portability is no longer deferred to rich media tooling. Rich authoring UX can
arrive later, but a saved voice node must already survive export/import in the local-first core.

## Provenance and Source Model

Every `concept`, `card`, and `exercise` must support source attribution. The PMP source
hierarchy is prioritized as:

1. `pmp-examination-content-outline` — PMP Examination Content Outline.
2. `pmi-standards-guides` — PMI standards and guides.
3. `user-course-video-notes` — user notes, course notes, and video notes.
4. `sanitized-real-work-scenarios` — sanitized real-work scenarios.
5. `mistake-log` — the learner's mistake log.

Copyright boundaries are preserved: cite and paraphrase, but never copy paid question banks
wholesale, and sanitize real-work scenarios to remove identifying detail.

## PMP Competency Mapping

Competency records carry six mapping dimensions: `examVersion`, `domain`, `taskOrEnabler`,
`deliveryApproach`, `source`, and `weight`. Delivery approaches are `predictive`,
`agile-adaptive`, `hybrid`, and `general`, so the same concept can be studied through the lens
the exam expects.

## Core Entities

The MVP data model is built from nine core entities:

| Entity | Key | Purpose |
| --- | --- | --- |
| `Source` | `source` | Attributable origin of study material with copyright boundary. |
| `Competency` | `competency` | Exam-version domain, task/enabler, delivery approach, and weight. |
| `Concept` | `concept` | Atomic PMP idea with plain-English meaning and PMI exam logic. |
| `Card` | `card` | A study prompt/answer unit that may carry multimedia. |
| `MediaAsset` | `mediaAsset` | Reusable local media node with integrity, provenance, accessibility, and portable bundle support. |
| `Exercise` | `exercise` | A typed exercise variant generated from a concept/card. |
| `Rubric` | `rubric` | Conceptual scoring for free-recall answers. |
| `ReviewAttempt` | `reviewAttempt` | A single graded interaction feeding scheduling and weakness. |
| `MasteryStat` | `masteryStat` | Derived mastery/weakness across scopes. |

These map onto the factored `actor`, `relationship`, and `component` shapes in the domain
model rather than becoming a pile of special-case tables.

## Multimedia Support

Cards and concepts may contain `text`, `image`, `audio`, and `video`. Text lives in the
structured store; image, audio, and video are reusable `media` actors backed by local files or
blobs and attached through `uses-media` relationships.

A spoken voice node preserves transcript, language, origin, integrity metadata, and generated
voice provenance when applicable. A meaningful visual node preserves alt text. Media usage
declares whether the asset is acting as a prompt, answer, explanation, mnemonic, or context and
whether presentation is audio-first, visual-first, multimodal, or text-fallback.

The reusable contract is `study-syndicate/multimodal-media/v1`.

## Exercise Taxonomy

The engine supports thirteen exercise types generated from concepts and cards:

- `basic-flashcard`
- `cloze`
- `scenario-mcq`
- `multi-select`
- `ordering`
- `matching`
- `categorization`
- `image-prompt`
- `audio-recall`
- `video-critique`
- `free-recall`
- `case-drill`
- `trap-correction`

## Grading Doctrine

Recall grading must not require sacred exact wording. The engine supports:

- `exact` mode for formulas, acronyms, and named artifacts.
- Typo, case, and punctuation tolerance.
- Accepted synonyms.
- `rubric` mode for conceptual answers.
- Self-grade `Again` / `Hard` / `Good` / `Easy`.

Semantic / local-AI grading is a later extension, not an MVP dependency.

## Rubric Scoring

Conceptual answers define a rubric scored `0-3` with three fields: `requiredIdeas`,
`acceptedSynonyms`, and `commonWrongPatterns`. This lets free recall be graded on ideas
present rather than exact phrasing.

## Weakness and Mastery Model

Weakness is tracked at four levels: `card`, `concept`, `competency`, and `domain`. The
`MasteryStat` records at each scope are derived from `ReviewAttempt` evidence, never entered
by hand.

The recommendation queue favors an initial, configurable policy:

- ~70% weak areas.
- ~20% due reviews.
- ~10% new material.

This ratio is an initial configurable policy, not immutable mathematics.

## PMP Concept Record

PMP-specific `concept` records support six judgment fields so the learner internalizes not
just the definition but how PMI reasons:

- `plainEnglishMeaning` — plain-English meaning.
- `pmiExamLogic` — PMI exam logic.
- `commonTrap` — common trap.
- `realWorldInstinct` — real-world instinct.
- `pmiPreferredAnswer` — PMI-preferred answer.
- `whyPmiPrefersIt` — why PMI prefers it.

## MVP Session Modes

The MVP ships seven session modes:

- `due-review` — Due Review.
- `weakness-drill` — Weakness Drill.
- `exam-judgment` — Exam Judgment.
- `formula-pit` — Formula Pit.
- `mistake-replay` — Mistake Replay.
- `source-build` — Source Build Mode.
- `audio-walkthrough` — Audio Walkthrough.

## MVP Build Order

1. **Phase 1 — Local study core:** `Source` -> `Concept` -> `Card` -> `Media` ->
   `ReviewAttempt` -> basic weakness shell -> structured JSON import/export ->
   `media-bundle-import-export`.
2. **Phase 2 — Exercise engine:** the exercise taxonomy runtime.
3. **Phase 3 — Weakness recommender:** the recommendation queue policy.
4. **Phase 4 — Smarter grading:** natural-language grading.
5. **Phase 5 — Richer media tooling:** `media-authoring-tools` such as recording, synthesis,
   editing, waveform/thumbnail UX, and batch authoring. Portability is already Phase 1.

## MVP Acceptance Contract

The MVP is accepted only when all of the following hold:

- `ac-provenance`: every Concept, Card, and Exercise can carry Source attribution.
- `ac-competency`: Concepts map to exam version, domain, task/enabler, delivery approach,
  source, and weight.
- `ac-entities`: all nine core entities are represented in the local Dexie/IndexedDB model.
- `ac-multimedia`: Cards and concepts support text, image, audio, and video through reusable
  media nodes with explicit usage roles.
- `ac-exercises`: all thirteen exercise types are enumerated and gradable.
- `ac-grading`: recall grading supports exact, tolerant, synonym, rubric, and self-grade modes
  without requiring exact wording for concepts.
- `ac-weakness`: weakness is tracked at card, concept, competency, and domain levels and drives
  a configurable practice queue.
- `ac-portability`: JSON export/import round-trips the complete structured study dataset
  without embedding binary media payloads; a full media bundle carries `study.json`,
  `manifest.json`, and integrity-addressed binary media so saved audio, image, and video nodes
  survive export/import.
- `ac-scheduling`: scheduling is FSRS-compatible.

## Scope Boundaries

Do not prematurely implement cloud sync or AI grading. `cloud-sync`, `ai-grading`, and a rich
media authoring UI are explicitly deferred until the local-first core is proven.

The safety boundary is narrower than the old media deferral: **binary media portability is not
deferred**. The app may postpone recording/synthesis/editing UX, but it must not create voice
or visual nodes that cannot be backed up and restored.
