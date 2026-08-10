[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$resolver = Join-Path $PSScriptRoot 'Resolve-StudySyndicateRepo.ps1'

if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
    throw "Missing resolver: $resolver"
}

function Assert-Resolution([string]$StartPath) {
    $json = & $resolver -StartPath $StartPath -Json
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $payload = $json | ConvertFrom-Json
    $expected = (Resolve-Path -LiteralPath $repoRoot).Path
    $actual = (Resolve-Path -LiteralPath $payload.root).Path
    if ($actual -ne $expected) {
        throw "Resolver returned wrong root for '$StartPath': $actual != $expected"
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
}

Assert-Resolution $repoRoot
Assert-Resolution (Join-Path $repoRoot 'harness/skills')

Write-Host 'repo location recovery PASS: root and nested-path resolution agree with canonical StudySyndicate origin'
