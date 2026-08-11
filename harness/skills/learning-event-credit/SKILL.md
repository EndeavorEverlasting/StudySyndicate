# Skill: Learning Event Credit

## Trigger

Use when a learner has produced any observable work that should receive evidence-based partial credit, including an
incorrect attempt, partial implementation, debugging trace, explanation, experiment, or useful discovery.

## Required inputs

- concept id
- learner-produced evidence
- assistance band
- facet-quality observations
- optional explicit cascade concept + relation weight

## Procedure

1. Read `docs/LEARNING_EVIDENCE_DOCTRINE.md`.
2. Read `content/learning/learning-evidence.v1.json`.
3. Do not score content generated solely by the agent as learner evidence.
4. Build one event JSON matching the contract.
5. Run `python scripts/learning-evidence.py score <event.json>`.
6. Report earned facets before missing facets.
7. Preserve assistance provenance and the mastery boundary.
8. Use cascade recognition only for acknowledgment or scheduling.
9. Select the smallest next rep that can produce new direct evidence.

## Expected outputs

- deterministic score JSON
- evidence-preserving acknowledgment
- weakest next facet
- explicit direct-vs-derived credit boundary
- no unsupported mastery claim
