[CmdletBinding()]
param(
    [string]$StartPath = (Get-Location).Path,
    [switch]$Json,
    [switch]$RunHarness
)

$ErrorActionPreference = 'Stop'
$ExpectedRepository = 'EndeavorEverlasting/StudySyndicate'
$ExpectedRemotePattern = '(?i)github\.com[:/]EndeavorEverlasting/StudySyndicate$'

function Normalize-Path([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    try {
        return (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    }
    catch {
        return $null
    }
}

function Resolve-CandidateRepo([string]$Candidate) {
    $resolved = Normalize-Path $Candidate
    if (-not $resolved) { return $null }

    $top = (& git -C $resolved rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $top) { return $null }
    $top = $top.Trim()

    $origin = (& git -C $top remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $origin) { return $null }
    $origin = $origin.Trim() -replace '\\.git$', ''
    if ($origin -notmatch $ExpectedRemotePattern) { return $null }

    return $top
}

$scriptRepoRoot = Split-Path -Parent $PSScriptRoot
$candidates = [System.Collections.Generic.List[string]]::new()
foreach ($candidate in @(
    $StartPath,
    $scriptRepoRoot,
    (Join-Path $HOME 'Desktop/Dev/StudySyndicate'),
    (Join-Path $HOME 'Desktop/dev/StudySyndicate'),
    (Join-Path $HOME 'dev/StudySyndicate'),
    (Join-Path $HOME 'Desktop/StudySyndicate')
)) {
    if (-not [string]::IsNullOrWhiteSpace($candidate) -and -not $candidates.Contains($candidate)) {
        $candidates.Add($candidate)
    }
}

$repoRoot = $null
foreach ($candidate in $candidates) {
    $repoRoot = Resolve-CandidateRepo $candidate
    if ($repoRoot) { break }
}

if (-not $repoRoot) {
    $searched = ($candidates -join "`n  - ")
    throw "StudySyndicate repository not found. Searched:`n  - $searched`nExpected origin: https://github.com/$ExpectedRepository.git"
}

$head = (& git -C $repoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$branch = (& git -C $repoRoot branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$origin = (& git -C $repoRoot remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$payload = [ordered]@{
    schema = 'studysyndicate.repo-location-proof.v1'
    repository = $ExpectedRepository
    root = $repoRoot
    branch = $(if ($branch) { $branch } else { '(detached)' })
    head = $head
    origin = $origin
}

if ($Json) {
    $payload | ConvertTo-Json -Depth 4
}
else {
    Write-Host "REPOSITORY=$($payload.repository)"
    Write-Host "ROOT=$($payload.root)"
    Write-Host "BRANCH=$($payload.branch)"
    Write-Host "HEAD=$($payload.head)"
    Write-Host "ORIGIN=$($payload.origin)"
}

if ($RunHarness) {
    & python (Join-Path $repoRoot 'scripts/validate-repo-ledger.py')
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & python (Join-Path $repoRoot 'scripts/get-repo-ledger-frontier.py') --prompt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
