# Factored Domain Model

StudySyndicate should model study work as explicit, factored records instead of one-off nested blobs. The goal is to make every actor, relationship, and component understandable before the app grows.

## Core Abstraction

Use three top-level domain shapes:

1. **Actors** — durable things that can own, create, perform, or be the subject of study activity.
2. **Relationships** — typed links between actors that explain why two records are connected.
3. **Components** — replaceable parts attached to an actor or relationship that carry content, scoring, media, scheduling, or metadata.

This keeps the system flexible: a flashcard, PMP concept, source note, rubric, review attempt, or media attachment can evolve without turning the database into a pile of special cases.

## Rules

- Prefer small, typed records over large records with many optional fields.
- Store relationships explicitly when the link has meaning, history, strength, order, provenance, or scoring impact.
- Store components separately when the part can be edited, versioned, reused, attached to multiple actors, or rendered independently.
- Avoid duplicating derived state; compute it from attempts, schedules, and relationships when practical.
- Keep every record locally addressable with a stable id so import/export and migrations stay predictable.

## Actor Types

| Actor | Purpose |
| --- | --- |
| `learner` | The local user profile, preferences, goals, and study constraints. |
| `source` | A book, article, video, course note, or user-created reference that produced study material. |
| `concept` | A PMP idea, process, term, formula, domain, task, or competency. |
| `prompt` | A study prompt such as a flashcard front, scenario, recall question, or exercise instruction. |
| `response` | An expected answer, rubric, explanation, or worked example. |
| `session` | A bounded study event containing attempts and review context. |
| `attempt` | A learner interaction with a prompt, including answer data and outcome. |
| `media` | Image, audio, video, or file metadata associated with study content. |

## Relationship Types

| Relationship | From → To | Meaning |
| --- | --- | --- |
| `derived-from` | study actor → `source` | Provenance for generated or user-created material. |
| `tests` | `prompt` → `concept` | The prompt evaluates understanding of a concept. |
| `explains` | `response` → `concept` | The response teaches or clarifies a concept. |
| `contains` | parent actor → child actor | Ordered composition such as source sections, card groups, or exercise sets. |
| `depends-on` | `concept` → `concept` | Prerequisite or enabling knowledge. |
| `conflicts-with` | actor → actor | Marks ambiguity, contradiction, duplicate material, or content needing review. |
| `attempted-in` | `attempt` → `session` | Places an attempt inside a study session. |
| `answered-by` | `attempt` → `response` | Links learner work to a selected or generated answer. |
| `uses-media` | actor/component → `media` | Attaches media without embedding binary payloads in core study records. |

## Component Types

| Component | Attaches To | Purpose |
| --- | --- | --- |
| `text-content` | actor or relationship | Markdown/plain text body, prompt text, explanation, or note. |
| `media-ref` | actor or relationship | Local file handle, blob key, mime type, duration, dimensions, and caption. |
| `pmp-map` | `concept` or `prompt` | PMP domain, task, process group, knowledge area, or competency tags. |
| `rubric` | `response` or `prompt` | Criteria for free recall or scenario scoring. |
| `schedule` | `prompt` or learner-prompt relationship | Spaced repetition state, due date, stability, difficulty, and lapse counts. |
| `attempt-result` | `attempt` | Grade, confidence, duration, mistakes, and weak-area signals. |
| `provenance` | any actor/component | Creation source, import id, author, timestamp, and revision metadata. |
| `ui-state` | learner-owned actor | Lightweight local preferences only; never primary study data. |

## Minimal TypeScript Sketch

```ts
export type ActorKind =
  | 'learner'
  | 'source'
  | 'concept'
  | 'prompt'
  | 'response'
  | 'session'
  | 'attempt'
  | 'media';

export type RelationshipKind =
  | 'derived-from'
  | 'tests'
  | 'explains'
  | 'contains'
  | 'depends-on'
  | 'conflicts-with'
  | 'attempted-in'
  | 'answered-by'
  | 'uses-media';

export type ComponentKind =
  | 'text-content'
  | 'media-ref'
  | 'pmp-map'
  | 'rubric'
  | 'schedule'
  | 'attempt-result'
  | 'provenance'
  | 'ui-state';

export interface Actor {
  id: string;
  kind: ActorKind;
  label: string;
  createdAt: string;
  updatedAt: string;
}

export interface Relationship {
  id: string;
  kind: RelationshipKind;
  fromActorId: string;
  toActorId: string;
  order?: number;
  weight?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Component<T = unknown> {
  id: string;
  kind: ComponentKind;
  ownerType: 'actor' | 'relationship';
  ownerId: string;
  data: T;
  createdAt: string;
  updatedAt: string;
}
```

## MVP Storage Tables

When Dexie is introduced, start with these tables before adding feature-specific tables:

- `actors`
- `relationships`
- `components`
- `reviewQueue` or component-backed schedule indexes if performance requires it
- `outbox` only if sync/export workflows later need operation logs

## Example Study Flow

1. Create a `source` actor for a PMP lesson.
2. Create `concept` actors for the lesson's key ideas.
3. Link concepts to the source with `derived-from` relationships.
4. Create `prompt` and `response` actors for flashcards or scenario drills.
5. Link each prompt to tested concepts with `tests` relationships.
6. Attach prompt text, answer text, PMP mapping, rubric, and media as components.
7. Create a `session` actor when studying begins.
8. Create `attempt` actors for each review and connect them with `attempted-in` relationships.
9. Attach `attempt-result` and `schedule` components after scoring.
10. Derive weak-area dashboards from prompt-concept relationships and attempt-result components.
