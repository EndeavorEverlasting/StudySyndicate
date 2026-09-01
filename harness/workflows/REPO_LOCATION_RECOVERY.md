# Repository Location Recovery

Use this workflow when a shell starts outside the repository, Git reports `fatal: not a git repository`, a temporary worktree is active, or there is uncertainty about which StudySyndicate copy is authoritative.

## Authority

`harness/canonical-paths.v1.json` is the single repository-owned path contract. `scripts/Resolve-StudySyndicateRepo.ps1` consumes that contract and emits a `studysyndicate.path-input-receipt.v1`.

Do not add another search list, fallback root, installer-specific clone path, or remembered user directory. A different existing checkout is evidence to preserve and inspect, not permission to redefine the canonical location.

## Windows operator profile

For `windows-desktop-dev`, resolve the Desktop through `Environment.SpecialFolder.Desktop`, then append:

`Dev\StudySyndicate`

This deliberately does **not** assume `%USERPROFILE%\Desktop`. If Windows redirects the Desktop Known Folder into OneDrive, the resolved Known Folder path wins because the operating system has proved that redirection. Merely having OneDrive installed does not move the path.

Roles:

- canonical development checkout: `<Desktop Known Folder>\Dev\StudySyndicate`
- canonical production/use path at this floor: the same checkout
- canonical operator entrypoint: `npm run dev`
- canonical parallel-worktree root: `<Desktop Known Folder>\Dev\StudySyndicate-worktrees`
- remote GitHub integration: separate from local checkout/use state

The sibling worktree root is intentionally outside the normal mutable checkout. A feature branch may be isolated under that worktree root when the same-path use checkout is active or its consumer state is unknown; this does not justify a second durable clone.

## EXECUTION CONTEXT receipt

Before path-sensitive or mutation-sensitive commands, the resolver records the actual PowerShell host/interpreter, platform/runtime boundary, execution target (`local` or `CI`), and material path/filesystem semantics. A terminal application name or prompt string is not treated as proof of the shell, kernel/runtime, or target.

If the selected profile cannot be resolved from the tracked contract and current execution context, resolution fails closed. Do not emit a guessed CMD/PowerShell/WSL/Linux write command for another target profile.

## Production/use state and same-path mutation

The Windows development and use roles currently resolve to the **same physical checkout**. That means an in-place development write is production/use-impacting whenever an operator process, watcher, server, scheduled task, updater, or similar consumer may observe the tree.

The resolver records `PROD_USE_STATE` as one of:

- `ACTIVE` — process evidence proves an npm/node/Vite/StudySyndicate consumer references the canonical use path.
- `QUIESCED` — explicitly asserted after the operator has stopped/paused consumers.
- `OFFLINE` — explicitly asserted when the use surface is not running/available; provider CI also reports this because it is not a workstation deployment.
- `UNKNOWN` — the default when inactivity has not been proved, including when consumer inspection is unavailable.

`UNKNOWN` is not idle. Same-path mutation is allowed only when the receipt reports `QUIESCED` or `OFFLINE`. Use `-RequireMutationSafe` before any helper or operator flow intends to write in the canonical checkout. If the state is `ACTIVE` or `UNKNOWN`, the resolver exits nonzero and the safe lane is to quiesce the consumer or create/use a branch worktree below the canonical worktree root.

The resolver also blocks `-RunHarness` from the same-path Windows checkout when production-use state is not mutation-safe, because even validation may create build/cache outputs.

## Bootstrap from any PowerShell prompt

The bootstrap only computes enough of the tracked rule to reach the resolver; the resolver remains authority:

```powershell
$Desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
if ([string]::IsNullOrWhiteSpace($Desktop)) { throw 'Windows Desktop Known Folder is unavailable.' }

$Repo = Join-Path $Desktop 'Dev\StudySyndicate'
$Resolver = Join-Path $Repo 'scripts\Resolve-StudySyndicateRepo.ps1'
if (-not (Test-Path -LiteralPath $Resolver -PathType Leaf)) {
    throw "Canonical StudySyndicate resolver is missing at $Resolver. Inventory existing copies before cloning or moving anything."
}

& $Resolver -StartPath (Get-Location).Path -Json
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

Before an in-place mutation, require a mutation-safe receipt. This example deliberately starts at `UNKNOWN`; only assert `QUIESCED` after actually stopping consumers:

```powershell
& $Resolver -StartPath (Get-Location).Path -RequireMutationSafe -Json
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

After the operator has intentionally quiesced the local-use surface:

```powershell
& $Resolver -StartPath (Get-Location).Path -ProdUseState QUIESCED -RequireMutationSafe -Json
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

For a human-readable proof plus the quick harness, use an approved isolated worktree or prove `QUIESCED`/`OFFLINE` first:

```powershell
& $Resolver -StartPath (Get-Location).Path -ProdUseState QUIESCED -RunHarness
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

## Drift behavior

The resolver fails closed and reports the canonical rule/path, observed location, evidence source, mutation safety, and safe next action.

- `CANONICAL + PROVED`: canonical checkout exists and its `origin` is `EndeavorEverlasting/StudySyndicate`.
- `NONCANONICAL + PRESERVE`: another verified StudySyndicate checkout is observed while the canonical path is missing. Preserve and inspect it before any move/clone.
- `MISSING`: canonical checkout is absent and no verified alternative was observed.
- `CONFLICT`: the canonical path exists but does not prove the expected repository identity, or resolves through an unexpected Git root.
- `UNKNOWN`: the host/profile cannot be resolved from tracked rules.

There is no silent fallback to `$HOME\dev`, `Desktop\StudySyndicate`, AppData, OneDrive, `%TEMP%`, or another convenient location.

## Copy/worktree classification

Before cleanup, classify observed locations:

- normal canonical repo -> `CLONE`
- checkout below the approved sibling worktree root -> `WORKTREE`
- other verified mutable repo -> `CLONE_NONCANONICAL` / preserve
- `dist/` -> `OUTPUT`
- `node_modules/` -> `CACHE`
- exported study data -> `OUTPUT`
- backups/mirrors -> not source authority

Do not `reset --hard`, `clean`, delete a worktree, or remove a noncanonical checkout merely to make the machine tidy. Dirty, unpushed, unique, or separately owned work must be preserved first.

## Local versus remote proof

Track these states separately:

1. `REMOTE_INTEGRATED`: intended merge SHA is contained in refreshed GitHub `main`.
2. `DEV_CHECKOUT_CURRENT`: canonical development checkout contains that integration and is safely reconciled.
3. `PROD_PATH_CURRENT`: canonical use path has consumed the intended version. At this floor it shares the development checkout, but this remains a separate observation.
4. `ENTRYPOINT_PROVED`: `npm run dev` actually starts from the canonical use path and the intended behavior is observed.

A GitHub merge proves only item 1. Provider CI is not proof that the Windows canonical checkout is current, quiesced, or observing the intended version.
