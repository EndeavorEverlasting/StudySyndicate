[CmdletBinding()]
param(
    [string]$RepositoryPath,
    [string]$TargetRef = 'origin/main',
    [string]$SqlIntegration = '62872f9f442582b076e79f94d046fe4d4792126d',
    [switch]$SkipFetch,
    [switch]$ProviderValidation
)

$ErrorActionPreference = 'Stop'
trap {
    $position = [string]$_.InvocationInfo.PositionMessage
    $stack = [string]$_.ScriptStackTrace
    [Console]::Error.WriteLine("StudySyndicate SQL field proof FAIL: $($_.Exception.Message)")
    if (-not [string]::IsNullOrWhiteSpace($position)) { [Console]::Error.WriteLine($position) }
    if (-not [string]::IsNullOrWhiteSpace($stack)) { [Console]::Error.WriteLine($stack) }
    exit 1
}

function Get-DefaultRepositoryPath {
    if ($env:GITHUB_ACTIONS -eq 'true' -and -not [string]::IsNullOrWhiteSpace($env:GITHUB_WORKSPACE)) {
        return [IO.Path]::GetFullPath($env:GITHUB_WORKSPACE)
    }

    if (-not $IsWindows) {
        throw 'The operator SQL field proof requires Windows. Provider validation must supply -RepositoryPath explicitly.'
    }

    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
    if ([string]::IsNullOrWhiteSpace($desktop)) {
        throw 'Windows Desktop Known Folder resolution returned an empty path.'
    }

    return Join-Path ([IO.Path]::GetFullPath($desktop)) 'Dev\StudySyndicate'
}

function Assert-NativeSuccess([string]$Action) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

if ([string]::IsNullOrWhiteSpace($RepositoryPath)) {
    $RepositoryPath = Get-DefaultRepositoryPath
}

if (-not (Test-Path -LiteralPath $RepositoryPath -PathType Container)) {
    throw "StudySyndicate checkout is missing: $RepositoryPath"
}
$RepositoryPath = (Resolve-Path -LiteralPath $RepositoryPath).Path

if ($ProviderValidation -and $env:GITHUB_ACTIONS -ne 'true') {
    throw '-ProviderValidation is reserved for GitHub Actions and cannot stand in for operator field proof.'
}
if (-not $ProviderValidation -and -not $IsWindows) {
    throw 'FIELD_PROOF requires the canonical Windows workstation runtime.'
}

$resolver = Join-Path $RepositoryPath 'scripts/Resolve-StudySyndicateRepo.ps1'
if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
    throw "Missing canonical repository resolver: $resolver"
}

$pathReceiptRaw = & $resolver -StartPath $RepositoryPath -Json
Assert-NativeSuccess 'Canonical path resolution'
$pathReceipt = $pathReceiptRaw | ConvertFrom-Json
if ($pathReceipt.status -ne 'CANONICAL + PROVED') {
    throw "Canonical path resolver did not prove the checkout: $($pathReceipt.status)"
}
if (-not $ProviderValidation -and $pathReceipt.profileKey -ne 'windows-desktop-dev') {
    throw "Operator proof requires windows-desktop-dev; resolver returned '$($pathReceipt.profileKey)'."
}

if (-not $SkipFetch) {
    & git -C $RepositoryPath fetch --all --prune --tags
    Assert-NativeSuccess 'git fetch --all --prune --tags'
}

$targetRaw = & git -C $RepositoryPath rev-parse $TargetRef
Assert-NativeSuccess "Resolve target ref '$TargetRef'"
$targetSha = ([string]$targetRaw).Trim()

& git -C $RepositoryPath merge-base --is-ancestor $SqlIntegration $targetSha
if ($LASTEXITCODE -ne 0) {
    throw "Required SQL integration $SqlIntegration is not contained in target $targetSha."
}

$dirty = @(& git -C $RepositoryPath status --porcelain=v1)
Assert-NativeSuccess 'Inspect canonical checkout status'
$branchRaw = & git -C $RepositoryPath branch --show-current
Assert-NativeSuccess 'Inspect canonical checkout branch'
$branch = ([string]$branchRaw).Trim()
$currentHeadRaw = & git -C $RepositoryPath rev-parse HEAD
Assert-NativeSuccess 'Inspect canonical checkout HEAD'
$currentHead = ([string]$currentHeadRaw).Trim()

$runRepo = $null
$proofMode = $null
$createdWorktree = $false

if ($ProviderValidation) {
    if ($dirty.Count -ne 0) {
        throw 'Provider validation checkout is dirty; refusing to certify a moved candidate.'
    }
    if ($currentHead -ne $targetSha) {
        throw "Provider validation must run the exact target HEAD: current=$currentHead target=$targetSha"
    }
    $runRepo = $RepositoryPath
    $proofMode = 'PROVIDER_EXACT_HEAD'
}
elseif (($dirty.Count -eq 0) -and ($branch -eq 'main') -and ($TargetRef -eq 'origin/main')) {
    & git -C $RepositoryPath pull --ff-only origin main
    Assert-NativeSuccess 'git pull --ff-only origin main'
    $runRepo = $RepositoryPath
    $proofMode = 'CANONICAL_MAIN'

    $targetRaw = & git -C $RepositoryPath rev-parse origin/main
    Assert-NativeSuccess 'Refresh target SHA after fast-forward'
    $targetSha = ([string]$targetRaw).Trim()
}
else {
    $worktreeRoot = [string]$pathReceipt.canonicalWorktreeRoot
    if ([string]::IsNullOrWhiteSpace($worktreeRoot)) {
        throw 'Canonical path receipt did not provide a worktree root.'
    }
    New-Item -ItemType Directory -Force -Path $worktreeRoot | Out-Null

    $runRepo = Join-Path $worktreeRoot ('ssq004-field-proof-' + $targetSha.Substring(0, 12))
    if (Test-Path -LiteralPath $runRepo -PathType Container) {
        $existingHeadRaw = & git -C $runRepo rev-parse HEAD 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $existingHeadRaw) {
            throw "Preservation worktree path exists but is not a usable Git worktree: $runRepo"
        }
        $existingHead = ([string]$existingHeadRaw).Trim()
        if ($existingHead -ne $targetSha) {
            throw "Preservation worktree exists at a different SHA: $runRepo ($existingHead != $targetSha)"
        }
        $existingDirty = @(& git -C $runRepo status --porcelain=v1)
        Assert-NativeSuccess 'Inspect existing preservation worktree'
        if ($existingDirty.Count -ne 0) {
            throw "Preservation worktree contains unique changes; refusing to overwrite or reuse it: $runRepo"
        }
    }
    else {
        & git -C $RepositoryPath worktree add --detach $runRepo $targetSha
        Assert-NativeSuccess 'Create preservation-first proof worktree'
        $createdWorktree = $true
    }
    $proofMode = 'ISOLATED_PRESERVE'
}

$runHeadRaw = & git -C $runRepo rev-parse HEAD
Assert-NativeSuccess 'Resolve proof checkout HEAD'
$runHead = ([string]$runHeadRaw).Trim()
if ($runHead -ne $targetSha) {
    throw "Proof checkout moved from exact target: $runHead != $targetSha"
}

& git -C $runRepo merge-base --is-ancestor $SqlIntegration HEAD
if ($LASTEXITCODE -ne 0) {
    throw "Proof checkout does not contain SQL integration $SqlIntegration."
}

& python (Join-Path $runRepo 'scripts/validate-practice-workbench.py')
Assert-NativeSuccess 'Practice Workbench validator'

& python (Join-Path $runRepo 'tests/test_sql_runner.py')
Assert-NativeSuccess 'SQL runner regression tests'

$spec = Get-Content -LiteralPath (Join-Path $runRepo 'harness/practice-workbench.v1.json') -Raw | ConvertFrom-Json
$sqlLanguages = @($spec.languages | Where-Object { $_.id -eq 'sql' })
if ($sqlLanguages.Count -ne 1) {
    throw "Expected exactly one SQL language registration; found $($sqlLanguages.Count)."
}
$sqlRunner = $sqlLanguages[0].runner
if ($sqlRunner.status -ne 'external-host-available' -or $sqlRunner.adapter -ne 'scripts/sql-runner.py') {
    throw 'Canonical SQL runner registration does not match the integrated contract.'
}

$attempt = Join-Path $env:TEMP 'studysyndicate-ssq004-field-proof.sql'
try {
    [IO.File]::WriteAllText(
        $attempt,
        'SELECT 1 AS field_proof;',
        [Text.UTF8Encoding]::new($false)
    )

    $adapterPath = Join-Path $runRepo ([string]$sqlRunner.adapter)
    $rawLines = @(& python $adapterPath $attempt)
    Assert-NativeSuccess 'Live SQL field proof'
    $rawOutcome = ($rawLines -join [Environment]::NewLine).Trim()
    $outcome = $rawOutcome | ConvertFrom-Json

    if ($outcome.status -ne 'passed') {
        throw "SQL field proof did not pass: $rawOutcome"
    }
    if ($null -eq $outcome.data -or $null -eq $outcome.data.rows -or $outcome.data.rows.Count -lt 1) {
        throw "SQL field proof returned no result row: $rawOutcome"
    }
    if ([int]$outcome.data.rows[0][0] -ne 1) {
        throw "SQL field proof returned the wrong first value: $rawOutcome"
    }
}
finally {
    Remove-Item -LiteralPath $attempt -Force -ErrorAction SilentlyContinue
}

$proof = [ordered]@{
    schema = 'studysyndicate.sql-field-proof.v1'
    status = 'passed'
    mode = $proofMode
    platform = $(if ($IsWindows) { 'windows' } else { 'non-windows-provider' })
    targetSha = $runHead
    sqlIntegration = $SqlIntegration
    pathProfile = [string]$pathReceipt.profileKey
    pathStatus = [string]$pathReceipt.status
    runnerAdapter = [string]$sqlRunner.adapter
    validator = 'passed'
    sqlRegressionTests = 'passed'
    selectOne = 1
}
$proof | ConvertTo-Json -Depth 6 -Compress

if ($ProviderValidation) {
    Write-Host "PROVIDER_FIELD_PROOF=PASS MODE=$proofMode SHA=$runHead"
}
else {
    Write-Host "FIELD_PROOF=PASS MODE=$proofMode SHA=$runHead"
}

if ($createdWorktree) {
    & git -C $RepositoryPath worktree remove $runRepo
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Field proof passed, but automatic worktree cleanup failed. Preserve and inspect: $runRepo"
    }
}
