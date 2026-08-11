# Study Guidance Ingest Workflow

Use this workflow when a tracker, application iteration, interview result, learning event, or cascade produces guidance that should become StudySyndicate study material.

## Inputs

- one `study-syndicate/study-guidance/v1` packet
- durable origin identity (`system`, `recordType`, `recordId`)
- trigger reason and iteration number
- one or more concept targets
- zero or more source resources; books are first-class resources, not free-form notes

## Procedure

1. Preserve the origin record and iteration before deriving study material.
2. Validate the packet with `python scripts/study-guidance.py validate PATH_TO_PACKET.json`.
3. Derive normalized material with `python scripts/study-guidance.py derive PATH_TO_PACKET.json`.
4. Schedule direct concept targets by packet priority.
5. Preserve every resource with its kind, title, author/locator when supplied, relation, and concept bindings.
6. Treat `book` resources as `book-guidance` material so reading guidance can participate in future study-pack generation.
7. Treat cascade targets and all source resources as scheduling/guidance evidence only; they do not count toward mastery.
8. Feed completed direct practice back through `LEARNING_EVENT_CASCADE.md`; a later iteration may then supersede or refine the guidance packet.

## Tracker boundary

EscapeHatch or another tracker owns opportunity/application state and gap detection. StudySyndicate owns the study-guidance contract, resource semantics, derived study material, learning-event evidence, and mastery boundaries. Do not duplicate application state here.

## Failure handling

- Unknown resource kind: reject the packet rather than flattening it into a note.
- Book without author or locator: accept it when the title is present; preserve any metadata that exists.
- Resource references an unknown packet concept: reject the packet and repair the tracker export.
- Cascade-only guidance: schedule it as derived material and require direct learner work before mastery credit.
- New iteration conflicts with old guidance: preserve both records and mark the older packet `superseded` at its owner.

## Handoff evidence

Record the guidance id, origin record, iteration, direct concepts, cascade targets, preserved resources, derived material count, and next scheduled direct rep.
