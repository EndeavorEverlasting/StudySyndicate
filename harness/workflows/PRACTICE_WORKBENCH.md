# Practice Workbench Workflow

Use this workflow when a learner wants to practice a concept through the browser shell or when a
new language/runner is added.

## Session path

1. Select a study target from repository authority.
2. Open the session modal and choose **facet**, **language**, and **study mode**.
3. Read the premise/source context before editing.
4. Work in the text editor; richer editor services are optional enhancements, never prerequisites.
5. Use the feedback panel only at the capability level registered for the selected language.
6. If execution is unavailable, keep the attempt and surface the exact external adapter/tooling gap.
7. Record the result as guided, docs-assisted, or mastery evidence without upgrading the proof level.

## Runner boundary

`harness/practice-workbench.v1.json` owns the execution-capability contract. A language entry does
not imply a runnable environment. Every adapter must normalize guest failures into `ExecutionOutcome`
and must keep the host shell alive.

For embedded Lua specifically, a Lua error is expected to cross the guest boundary as an exception;
the embedding host catches it and returns a `runtime-error` outcome. Rust panics, Python exceptions,
SQL errors, compiler failures, rejected JavaScript promises, process exits, and timeouts follow the
same host-normalization principle.

## UI authority boundary

The browser is a renderer, not curriculum authority. For Two Sum it reads
`harness/problems/two-sum.v1.json`; it must not replace the premise with shorter UI copy that loses
inputs, output, guarantees, or the example.

## Drag-and-drop boundary

The learner may reorder premise/workspace/feedback panels. Panel order is presentation state only.
Dragging cannot change selected mode, source authority, grading semantics, or runner availability.

## Adding a language

Use `harness/skills/runner-adapter/SKILL.md`. The change is incomplete until the language has an
explicit runner kind, status, failure model, validator coverage, and UI capability label.
