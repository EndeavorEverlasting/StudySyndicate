# Learning Evidence State

Status: **contract + deterministic harness engine implemented in this sprint**

## Working

- Versioned learning-event evidence contract defines five observable facets.
- Partial credit survives incomplete/incorrect final answers when intermediate work is demonstrated.
- Assistance provenance caps event credit without deleting learner evidence.
- AI-answer credit is explicitly bounded and cannot emit a mastery signal.
- Explicit prerequisite/adjacent relationships receive bounded cascade recognition.
- Cascade recognition never counts toward mastery.
- Acknowledgment bands describe observed progress without inflating competence.
- The engine emits the weakest facet so the next practice rep can be targeted.
- Contract and behavior tests are registered in the repository validation floor.

## Not yet proven

- Longitudinal aggregation across persisted sessions.
- Browser persistence of learning-event records.
- Adaptive scheduling driven by cascade recognition.
- UI capture of facet observations.
- Runtime calibration of facet-quality judgments across different evaluators.

## Safety / integrity boundary

No single event can claim mastery. AI/source output is not learner evidence. Derived cascade credit is recognition-only.
