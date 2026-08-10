# Skill: Guided Feedback Ladder

## Trigger

Use after an attempt exists and the learner needs feedback without immediately revealing the answer.

## Required inputs

- problem or exercise id
- current attempt
- expected behavior
- actual behavior or error
- study mode

## Feedback ladder

Stop at the first level that unlocks progress.

1. **L0 — Evidence only:** show the failing test, error, or counterexample without interpretation.
2. **L1 — Contract reminder:** restate the relevant input/output rule or invariant.
3. **L2 — Guiding question:** ask one question that points at the missing relationship.
4. **L3 — Structural hint:** name the data structure or algorithm shape without giving final code.
5. **L4 — Pseudocode comparison:** compare the attempt with language-neutral steps.
6. **L5 — Reference review:** inspect the known-good implementation only after an honest attempt.

For Two Sum, a useful L2 question is: "For the current number, what single value would complete the
target, and have you seen that value before?"

## Failure classification

Tag the failure as one of:

- syntax/import
- wrong output
- edge case
- self-use/index error
- data-structure choice
- complexity gap
- explanation gap
- environment/tooling

## Output

Record the highest hint level used, the smallest failing case, the repair, and the rerun result.

## Rule

Feedback should make the next learner action obvious without erasing the learner's opportunity to
perform that action.
