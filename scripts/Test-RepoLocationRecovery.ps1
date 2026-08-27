[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$resolver = Join-Path $PSScriptRoot 'Resolve-StudySyndicateRepo.ps1'

if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
    throw "Missing resolver: $resolver"
}

function Assert-Resolution([string]$StartPath) {
    $arguments = @('-StartPath', $StartPath, '-Json')
    if ($env:GITHUB_ACTIONS -ne 'true' -and -not $IsWindows) {
        $arguments += @('-ProfileKey', 'github-actions')
    }

    $json = & $resolver @arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $payload = $json | ConvertFrom-Json

    if ($payload.status -ne 'CANONICAL + PROVED') {
        throw "Resolver did not prove canonical path for '$StartPath': $($payload.status)"
    }
    if ($payload.repository -ne 'EndeavorEverlasting/StudySyndicate') {
        throw "Unexpected repository identity: $($payload.repository)"
    }
    if ([string]::IsNullOrWhiteSpace($payload.head)) {
        throw 'Resolver did not emit HEAD proof.'
    }
    if ($payload.origin -notmatch '(?i)github\.com[:/]EndeavorEverlasting/StudySyndicate(?:\.git)?$') {
        throw "Resolver accepted unexpected origin: $($payload.origin)"
    }
    if ($payload.canonicalUsePath -ne $payload.canonicalDevelopmentPath) {
        throw 'Use path must equal development path at this floor.'
    }

    if ($payload.profileKey -eq 'github-actions') {
        $expected = (Resolve-Path -LiteralPath $repoRoot).Path
        $actual = (Resolve-Path -LiteralPath $payload.canonicalDevelopmentPath).Path
        if ($actual -ne $expected) {
            throw "Provider profile returned wrong checkout: $actual != $expected"
        }
        if ($payload.oneDriveState -ne 'NOT_APPLICABLE') {
            throw "Provider profile must report OneDrive NOT_APPLICABLE, got $($payload.oneDriveState)"
        }
    }
}

Assert-Resolution $repoRoot
Assert-Resolution (Join-Path $repoRoot 'harness/skills')

Write-Host 'repo location recovery PASS: tracked profile contract resolves one canonical checkout and rejects fallback authority'
