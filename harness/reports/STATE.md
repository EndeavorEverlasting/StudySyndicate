# Operator State Report

Status captured after the Practice Workbench foundation sprint on 2026-08-10.

## Working

- Canonical governance remains at `AGENTS.md`.
- PMP, software-foundations, arrays, mental-math, multimodal-media, repository-ledger, guided-problem,
  repository-location, and Practice Workbench validation surfaces exist.
- Repository-location recovery distinguishes the durable clone from a wrong current directory or detached
  `%TEMP%` worktree and proves the canonical GitHub origin before mutation.
- The root Vite + React + TypeScript application shell exists with canonical `npm run lint` and
  `npm run build` commands.
- The Practice Workbench renders a premise-first study surface with modal target/facet/language/mode selection.
- Premise, workspace, and feedback panels are reorderable through drag-and-drop.
- The text workspace remains usable as a plain textarea/Notepad-style fallback.
- Two Sum is rendered from its canonical problem packet rather than copied into UI prose.
- SQL and Rust foundation exercises are discoverable from their canonical study pack.
- Python, Rust, SQL, C, JavaScript, TypeScript, Java, and Lua have explicit runner kinds and statuses.
- Guest-code failure is a host-boundary contract: exceptions, panics, compiler errors, database errors,
  process failures, and timeouts normalize to `ExecutionOutcome`; they do not become React-shell crashes.
- ParallaxPort public skill claims remain versioned study fodder rather than mastery proof.

## Deliberately capability-gated

- The browser does not directly execute learner code in this sprint.
- Python Two Sum executable feedback remains available through `scripts/study-problem.py` outside the browser.
- Rust, SQL, C, JavaScript, TypeScript, Java, and Lua runner adapters are registered but remain `planned`
  until each adapter has runtime-specific timeout/failure proof.
- JavaScript/TypeScript are not implemented with `eval` or `new Function`; a dedicated sandbox contract is
  required before browser execution is marked available.
- No production hosting/deployment contract exists yet. A successful Vite build is build proof, not deployment proof.
- ParallaxPort claim refresh remains explicit rather than live-scraped.
- Tracked Git hooks remain opt-in.

## Known traps

- `C:\Users\<user>\Desktop\Dev\StudySyndicate` and `C:\Users\<user>\dev\StudySyndicate` are different
  paths; missing `Desktop` matters even though `Dev`/`dev` case normally does not on Windows.
- A detached `%TEMP%\StudySyndicate-*` worktree can be valid for a bounded sprint but is not the durable clone.
- Do not issue repo-relative commands until repository identity has been proven after a terminal restart.
- A language in the Practice Workbench selector does **not** mean the runner is available.
- Do not let guest exceptions/panics escape into React event handlers.
- Do not shorten a problem packet until the premise loses inputs, output, guarantees, or example context.
- Drag-and-drop changes panel presentation only; it must not alter mastery or runner semantics.
- Do not promote an exercise-catalog prompt to `mastery` until it is converted into a premise-first packet.
- Do not confuse the reference solution in `practice/arrays/two_sum.py` with learner mastery.
- Do not commit local study exports, media bundles, `node_modules`, `dist`, secrets, logs, caches, or editor state.

## Next proof target

Implement and prove one real runner adapter behind the registered execution boundary. The adapter must show a
passing attempt, a guest failure converted to a normalized outcome, and timeout/cancellation while the host
shell remains usable. Repository identity must still be proven before that sprint starts.
