# Operator State Report

Status refreshed for the canonical-path and exact-candidate promotion floor on 2026-08-26.

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
- No external production hosting/deployment contract exists yet. `main` promotion is repository integration,
  not hosted deployment, and a successful GitHub promotion does not prove the Windows local checkout/use path.
- Application E2E at this floor proves the built Vite preview HTTP path and referenced JavaScript asset; it
  does not claim interactive browser, IndexedDB, or Windows `npm run dev` proof.
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
- A language in the Practice Workbench selector does **not** mean the runner is available.
- Do not let guest exceptions/panics escape into React event handlers.
- Do not shorten a problem packet until the premise loses inputs, output, guarantees, or example context.
- Drag-and-drop changes panel presentation only; it must not alter mastery or runner semantics.
- Do not promote an exercise-catalog prompt to `mastery` until it is converted into a premise-first packet.
- Do not confuse the reference solution in `practice/arrays/two_sum.py` with learner mastery.
- Do not commit local study exports, media bundles, promotion scratch, `node_modules`, `dist`, secrets, logs, caches, or editor state.

## Next proof target

After the promotion pipeline is provider-proven and the Windows path-input receipt is observed, the existing
repository frontier remains authoritative for the next feature sprint. Do not replace that frontier with this
state report.
