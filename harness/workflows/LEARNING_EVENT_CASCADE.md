# Learning Event Cascade Workflow

Use this workflow when a learner attempt, debugging session, explanation, experiment, or discovery should become
durable evidence instead of being reduced to pass/fail.

## Inputs

- one concept id
- the learner's actual attempt or observable behavior
- assistance used: `none`, `docs`, `hint`, `ai-scaffold`, or `ai-answer`
- facet observations for `construct`, `apply`, `debug`, `explain`, and/or `discover`
- optional explicitly related prerequisite/adjacent concepts

## Procedure

1. Preserve the learner's attempt before exposing a replacement answer.
2. Separate observed learner behavior from agent/source material.
3. Assign facet quality only for evidence actually observed.
4. Record the assistance band honestly.
5. If the event exercised a prerequisite/adjacent concept, add an explicit cascade relation weight; never infer a
   mastery relationship from topic proximity alone.
6. Run:
   `python scripts/learning-evidence.py score PATH_TO_EVENT.json`
7. Present event credit, earned facets, weakest facet, acknowledgment, and assistance provenance.
8. Treat `cascadeRecognition` as acknowledgment/scheduling evidence only.
9. If `eventMasterySignal` is true, record it as one direct rep. Do not claim mastery; aggregate proof is still required.
10. Choose the next rep from the weakest required facet or an explicit transfer target.

## Failure handling

- Invalid event shape: repair the event packet, not the scoring engine.
- Unknown facet/assistance band: use the versioned contract; do not invent a local label.
- AI produced the answer before the learner attempted: record `ai-answer` or `ai-scaffold`; do not backfill unassisted credit.
- Final answer wrong but reasoning contains valid work: preserve the valid facet observations and continue the rep.
- Cascade looks generous: reduce or remove the explicit relation weight. Never increase the global cascade cap ad hoc.

## Handoff evidence

Include the event id, concept id, assistance band, event credit, earned facets, cascade recognition, weakest facet,
mastery signal (if any), and the next direct practice target.
