# Operator State Report

Status refreshed for the reviewed bounded SQL runner proof floor on 2026-08-26.

## Working

- Canonical governance remains at `AGENTS.md`.
- PMP, software-foundations, arrays, mental-math, multimodal-media, repository-ledger, guided-problem,
  repository-location, Practice Workbench, source-ingestion, canonical-path, and promotion validation surfaces exist.
- `harness/canonical-paths.v1.json` owns machine/profile-aware development, use, and worktree roles. On the
  Windows operator profile, Desktop is resolved through the Windows Known Folder API and the canonical
  checkout is `<Desktop Known Folder>\Dev\StudySyndicate`; no alternate-root search list owns fallback authority.
- The Windows local-use path is currently the same canonical checkout and the operator entrypoint is
  `npm run dev`. Parallel writers use the sibling `<Desktop Known Folder>\Dev\StudySyndicate-worktrees` root.
- Repository-location recovery proves the tracked profile, canonical GitHub origin, branch, and HEAD before
  mutation and preserves a noncanonical verified checkout rather than silently adopting it.
- `harness/promotion-contract.v1.json` owns guarded squash integration into `main`; the provider workflow
  pins an exact PR head, runs the canonical full harness plus distinct application HTTP E2E, rechecks the
  candidate before mutation, proves post-merge containment, and emits a promotion receipt.
- The root Vite + React + TypeScript application shell exists with canonical `npm run lint`, `npm run build`,
  `npm run dev`, and Vite preview commands.
- The Practice Workbench renders a premise-first study surface with modal target/facet/language/mode selection.
- Premise, workspace, and feedback panels are reorderable through drag-and-drop.
- The text workspace remains usable as a plain textarea/Notepad-style fallback.
- Two Sum is rendered from its canonical problem packet rather than copied into UI prose.
- SQL and Rust foundation exercises are discoverable from their canonical study pack.
- Python, Rust, SQL, C, JavaScript, TypeScript, Java, and Lua have explicit runner kinds and statuses.
- Python Two Sum feedback is externally available through `scripts/study-problem.py`.
- SQL is externally available through `scripts/sql-runner.py`: every invocation uses a fresh in-memory SQLite
  database, emits strict normalized JSON `ExecutionOutcome`, enforces a finite execution/parsing deadline,
  reads at most 256 KiB of learner input, bounds individual values before serialization, caps serialized row
  payload at 64 KiB, and denies `ATTACH`, `DETACH`, `PRAGMA`, and the `load_extension` SQL function. The browser
  exposes the command but does not execute learner SQL directly.
- Reviewed SQL adapter proof on candidate `c3711d81c358a7e77bbc36afe58dda08974ac528` passed 11 boundary and
  regression cases in Practice Workbench workflow `33037590036`, including success, guest error, execution
  timeout, semicolon-heavy parsing, invalid UTF-8, load-extension denial, strict non-finite JSON, input budget,
  cell budget, result budget, and attachment denial. Repository ledger workflow `33037590037` passed on Ubuntu
  and Windows, and full registered harness workflow `33037590068` passed on that exact candidate.
- Guest-code failure is a host-boundary contract: exceptions, panics, compiler errors, database errors,
  process failures, and timeouts normalize to `ExecutionOutcome`; they do not become React-shell crashes.
- ParallaxPort public skill claims remain versioned study fodder rather than mastery proof.

## Deliberately capability-gated

- The browser does not directly execute learner code at this floor.
- Rust, C, JavaScript, TypeScript, Java, and Lua runner adapters are registered but remain `planned`
  until each adapter has runtime-specific timeout/failure proof.
- JavaScript/TypeScript are not implemented with `eval` or `new Function`; a dedicated sandbox contract is
  required before browser execution is marked available.
- The SQL adapter proves bounded SQLite execution and failure normalization, not semantic correctness against
  every exercise prompt and not learner mastery.
- No external production hosting/deployment contract exists yet. `main` promotion is repository integration,
  not hosted deployment, and a successful GitHub promotion does not prove the Windows local checkout/use path.
- Application E2E at this floor proves the built Vite preview HTTP path and referenced JavaScript asset; it
  does not claim interactive browser, IndexedDB, clipboard, or Windows `npm run dev` proof.
- ParallaxPort claim refresh remains explicit rather than live-scraped.
- Tracked Git hooks remain opt-in.

## Known traps

- Do not construct the Windows path as `C:\Users\<user>\Desktop`; resolve `Environment.SpecialFolder.Desktop`
  and append `Dev\StudySyndicate` from the tracked profile contract.
- An installed or running OneDrive client is not proof that Desktop is redirected. Use the actual Known Folder location.
- A detached or sibling worktree can be valid for a bounded sprint but is not the normal durable mutable clone.
- Do not issue repo-relative commands until canonical repository identity has been proven after a terminal restart.
- A green GitHub merge proves `REMOTE_INTEGRATED`, not `DEV_CHECKOUT_CURRENT`, `PROD_PATH_CURRENT`, or `ENTRYPOINT_PROVED`.
- A green harness does not substitute for the separate application E2E required by the promotion contract.
- A language in the Practice Workbench selector does **not** mean the runner is available; use its registered status.
- Do not let guest exceptions/panics/database errors escape into React event handlers.
- Do not weaken the SQL trust boundary by attaching filesystem databases, enabling unrestricted PRAGMA access,
  restoring optional load-extension APIs, removing input/result budgets, or emitting non-standard JSON numbers.
- Do not shorten a problem packet until the premise loses inputs, output, guarantees, or example context.
- Drag-and-drop changes panel presentation only; it must not alter mastery or runner semantics.
- Do not promote an exercise-catalog prompt to `mastery` until it is converted into a premise-first packet.
- Do not confuse the reference solution in `practice/arrays/two_sum.py` with learner mastery.
- Do not commit local study exports, media bundles, promotion scratch, `node_modules`, `dist`, secrets, logs, caches, or editor state.

## Next proof target

After the SQL runner change is integrated through the exact-candidate promotion contract, refresh the canonical
Windows checkout and observe the external SQL command there. The repository frontier remains authoritative for
the next feature sprint; do not replace that frontier with this state report.
