# Skill: Add or Repair a Practice Runner Adapter

## Trigger

Use when a language, database, VM, embedded interpreter, compiler, or local process should provide
executable feedback to the Practice Workbench.

## Required inputs

- language/runtime id
- execution environment (`browser-sandbox`, `host-process`, `database-session`, `embedded-host`, or another reviewed kind)
- compile/start command or embedding API
- timeout/cancellation mechanism
- guest failure forms
- normalized output/error evidence

## Procedure

1. Add or update the language in `harness/practice-workbench.v1.json`; never infer availability.
2. Keep the adapter boundary outside React presentation code.
3. Catch/receive guest failures at the adapter boundary and map them to the registered
   `ExecutionOutcome` statuses.
4. Enforce finite timeout/cancellation for executable guest code.
5. Return actionable detail without leaking a reference solution.
6. Add targeted positive, failure, and timeout tests.
7. Run `python scripts/validate-practice-workbench.py`, the adapter tests, `npm run lint`, and
   `npm run build`.
8. Only change the runner status to available after intended-runtime proof exists.

## Lua rule

A Lua `error(...)`/raised failure is not a React failure. The embedding host catches it and returns a
`runtime-error` `ExecutionOutcome`. The host shell must remain usable for the next attempt.

## Forbidden shortcuts

- direct `eval` or `new Function` in the browser shell as a substitute for a sandbox
- marking a runner available because the language appears in a selector
- infinite/no-timeout guest execution
- allowing a panic/exception/process crash to terminate the UI host
- returning a full solution as error feedback

## Output

A capability-registry change, adapter implementation, targeted failure tests, and proof matching the
runner status claimed.
