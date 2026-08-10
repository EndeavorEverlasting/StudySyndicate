# Repository Location Recovery

Use this workflow when a terminal says `fatal: not a git repository`, a shell was restarted, a worktree lived under `%TEMP%`, or the operator no longer knows which StudySyndicate checkout is active.

## Goal

Recover the canonical local repository root without assuming the current directory is correct and without resetting, cleaning, or deleting any checkout.

## Known Windows trap

A clone at:

`C:\Users\<user>\Desktop\Dev\StudySyndicate`

is **not** the same location as:

`C:\Users\<user>\dev\StudySyndicate`

or the home directory itself. Windows path case is normally insignificant, but the missing `Desktop` path segment is not.

A temporary detached worktree such as `%TEMP%\StudySyndicate-...` is also not the canonical clone and should not be treated as the durable repository location.

## Fast recovery from any PowerShell prompt

This snippet searches the known durable locations, proves the GitHub origin, and runs the ledger/frontier using `git -C`/absolute paths so the current directory does not have to be the repo:

```powershell
$repo = @(
  (Join-Path $HOME 'Desktop\Dev\StudySyndicate'),
  (Join-Path $HOME 'Desktop\dev\StudySyndicate'),
  (Join-Path $HOME 'dev\StudySyndicate')
) | Where-Object {
  (Test-Path -LiteralPath $_) -and
  ((git -C $_ remote get-url origin 2>$null) -match 'github\.com[:/]EndeavorEverlasting/StudySyndicate(?:\.git)?$')
} | Select-Object -First 1
if (-not $repo) { throw 'StudySyndicate durable clone not found in known locations.' }
Write-Host "REPO=$repo"
git -C $repo status --short
if ($LASTEXITCODE) { exit $LASTEXITCODE }
python (Join-Path $repo 'scripts/validate-repo-ledger.py')
if ($LASTEXITCODE) { exit $LASTEXITCODE }
python (Join-Path $repo 'scripts/get-repo-ledger-frontier.py') --prompt
if ($LASTEXITCODE) { exit $LASTEXITCODE }
```

## Tracked resolver

From any known path to this checkout, the tracked resolver performs the same identity checks:

```powershell
pwsh -NoLogo -NoProfile -File scripts/Resolve-StudySyndicateRepo.ps1 -RunHarness
```

For machine-readable proof:

```powershell
pwsh -NoLogo -NoProfile -File scripts/Resolve-StudySyndicateRepo.ps1 -Json
```

The resolver checks the current/nested path, the checkout containing the script itself, and common durable user roots. It rejects a Git repository whose `origin` is not `EndeavorEverlasting/StudySyndicate`.

## Safety boundary

- Do not `reset --hard`, `clean`, delete worktrees, or overwrite dirty work merely to recover location.
- Do not treat a detached `%TEMP%` worktree as the durable clone unless the task explicitly owns that worktree.
- Use `git -C <resolved-root> ...` when location uncertainty exists.
- After resolution, inspect `git status --short` before any mutation.
