[CmdletBinding()]
param(
    [string]$StartPath = (Get-Location).Path,
    [string]$ProfileKey,
    [switch]$Json,
    [switch]$RunHarness
)

$ErrorActionPreference = 'Stop'
$repoRootFromScript = Split-Path -Parent $PSScriptRoot
$contractPath = Join-Path $repoRootFromScript 'harness/canonical-paths.v1.json'

if (-not (Test-Path -LiteralPath $contractPath -PathType Leaf)) {
    throw "Missing canonical path contract: $contractPath"
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$expectedRepository = [string]$contract.repository
$expectedRemotePattern = '(?i)github\.com[:/]' + [regex]::Escape($expectedRepository) + '(?:\.git)?$'

function Normalize-ExistingPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    try {
        return (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    }
    catch {
        return $null
    }
}

function Get-RepositoryRoot([string]$Candidate) {
    $resolved = Normalize-ExistingPath $Candidate
    if (-not $resolved) { return $null }

    $topRaw = (& git -C $resolved rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $topRaw) { return $null }
    $top = $topRaw.Trim()

    $originRaw = (& git -C $top remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $originRaw) { return $null }
    $origin = $originRaw.Trim()

    if ($origin -notmatch $expectedRemotePattern) { return $null }
    return $top
}

function Get-Profile([string]$RequestedKey) {
    $profiles = @($contract.profiles)
    if (-not [string]::IsNullOrWhiteSpace($RequestedKey)) {
        $matches = @($profiles | Where-Object { $_.key -eq $RequestedKey })
        if ($matches.Count -ne 1) {
            throw "Unknown or ambiguous StudySyndicate profile '$RequestedKey'."
        }
        return $matches[0]
    }

    if ($env:GITHUB_ACTIONS -eq 'true') {
        return @($profiles | Where-Object { $_.key -eq 'github-actions' })[0]
    }

    if ($IsWindows) {
        return @($profiles | Where-Object { $_.key -eq 'windows-desktop-dev' })[0]
    }

    throw 'No canonical StudySyndicate path profile matches this host. Specify a tracked profile key; do not invent a path.'
}

function Get-DesktopKnownFolder {
    if (-not $IsWindows) { return $null }
    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
    if ([string]::IsNullOrWhiteSpace($desktop)) {
        throw 'Windows Desktop Known Folder resolution returned an empty path.'
    }
    return [IO.Path]::GetFullPath($desktop)
}

function Join-RuleSegments([string]$Base, $Segments) {
    $result = $Base
    foreach ($segment in @($Segments)) {
        $result = Join-Path $result ([string]$segment)
    }
    return [IO.Path]::GetFullPath($result)
}

function Get-OneDriveState([string]$DesktopPath) {
    if (-not $IsWindows) { return 'NOT_APPLICABLE' }

    $rawRoots = @(
        $env:OneDrive,
        $env:OneDriveConsumer,
        $env:OneDriveCommercial
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    $roots = @($rawRoots | ForEach-Object {
        try { [IO.Path]::GetFullPath($_).TrimEnd([char[]]@('\','/')) } catch { $_.TrimEnd([char[]]@('\','/')) }
    } | Sort-Object -Unique)

    if ($roots.Count -eq 0) { return 'ABSENT' }
    if ($roots.Count -gt 1) { return 'MULTIPLE_ROOTS' }

    $root = $roots[0]
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        return 'ROOT_UNAVAILABLE'
    }

    $desktopFull = [IO.Path]::GetFullPath($DesktopPath).TrimEnd([char[]]@('\','/'))
    if ($desktopFull.Equals($root, [StringComparison]::OrdinalIgnoreCase) -or
        $desktopFull.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)) {
        return 'TARGET_FOLDER_REDIRECTED'
    }

    return 'ROOT_AVAILABLE'
}

function Resolve-ProfilePath($Rule, [string]$DesktopKnownFolder) {
    if ($null -eq $Rule) { return $null }
    switch ([string]$Rule.base) {
        'known-folder:Desktop' {
            if ([string]::IsNullOrWhiteSpace($DesktopKnownFolder)) {
                throw 'The selected profile requires the Windows Desktop Known Folder, but this host cannot resolve it.'
            }
            return Join-RuleSegments $DesktopKnownFolder $Rule.segments
        }
        'workflow-checkout' {
            return [IO.Path]::GetFullPath($repoRootFromScript)
        }
        default {
            throw "Unsupported canonical path base '$($Rule.base)'."
        }
    }
}

function Paths-Equal([string]$Left, [string]$Right) {
    if ([string]::IsNullOrWhiteSpace($Left) -or [string]::IsNullOrWhiteSpace($Right)) { return $false }
    try {
        $a = [IO.Path]::GetFullPath($Left).TrimEnd([char[]]@('\','/'))
        $b = [IO.Path]::GetFullPath($Right).TrimEnd([char[]]@('\','/'))
        if ($IsWindows) { return $a.Equals($b, [StringComparison]::OrdinalIgnoreCase) }
        return $a -ceq $b
    }
    catch {
        return $false
    }
}

$profile = Get-Profile $ProfileKey
$desktopKnownFolder = Get-DesktopKnownFolder
$canonicalDevelopmentPath = Resolve-ProfilePath $profile.development $desktopKnownFolder

if ($profile.use.relation -ne 'same-as-development') {
    throw "Unsupported path relation '$($profile.use.relation)'."
}
$canonicalUsePath = $canonicalDevelopmentPath
$canonicalWorktreeRoot = Resolve-ProfilePath $profile.worktree $desktopKnownFolder
$oneDriveState = Get-OneDriveState $desktopKnownFolder

$observedPath = Normalize-ExistingPath $StartPath
$observedRepoRoot = Get-RepositoryRoot $StartPath
$canonicalExists = Test-Path -LiteralPath $canonicalDevelopmentPath -PathType Container
$canonicalRepoRoot = if ($canonicalExists) { Get-RepositoryRoot $canonicalDevelopmentPath } else { $null }

$status = 'UNKNOWN'
$safeNextAction = ''
$evidenceSources = @(
    'harness/canonical-paths.v1.json',
    'native environment/profile selection',
    'Git origin identity check'
)

if ($profile.key -eq 'windows-desktop-dev') {
    $evidenceSources += 'Windows Environment.SpecialFolder Desktop Known Folder'
    $evidenceSources += 'OneDrive environment roots inspected without redirect fallback'
}

if (-not $canonicalExists) {
    $status = 'MISSING'
    if ($observedRepoRoot) {
        $status = 'NONCANONICAL + PRESERVE'
        $safeNextAction = "Preserve '$observedRepoRoot'; inspect git status and unpushed commits before creating or moving anything. Canonical development path is '$canonicalDevelopmentPath'."
    }
    else {
        $safeNextAction = "Canonical development checkout is missing at '$canonicalDevelopmentPath'. Inventory any existing StudySyndicate copies before cloning there."
    }
}
elseif (-not $canonicalRepoRoot) {
    $status = 'CONFLICT'
    $safeNextAction = "Path '$canonicalDevelopmentPath' exists but is not a verified EndeavorEverlasting/StudySyndicate checkout. Inspect it; do not overwrite it or create a fallback clone."
}
elseif (-not (Paths-Equal $canonicalRepoRoot $canonicalDevelopmentPath)) {
    $status = 'CONFLICT'
    $safeNextAction = "Canonical path resolves through a nested or redirected Git root '$canonicalRepoRoot'. Inspect junction/worktree state before mutation."
}
else {
    $status = 'CANONICAL + PROVED'
    $safeNextAction = "Use '$canonicalDevelopmentPath' for normal development and '$canonicalWorktreeRoot' for isolated parallel worktrees."
}

$head = $null
$branch = $null
$origin = $null
if ($canonicalRepoRoot) {
    $headRaw = (& git -C $canonicalRepoRoot rev-parse HEAD 2>$null)
    if ($LASTEXITCODE -eq 0 -and $headRaw) { $head = $headRaw.Trim() }
    $branchRaw = (& git -C $canonicalRepoRoot branch --show-current 2>$null)
    if ($LASTEXITCODE -eq 0 -and $branchRaw) { $branch = $branchRaw.Trim() }
    $originRaw = (& git -C $canonicalRepoRoot remote get-url origin 2>$null)
    if ($LASTEXITCODE -eq 0 -and $originRaw) { $origin = $originRaw.Trim() }
}

$observedClassification = if ($observedRepoRoot) {
    if (Paths-Equal $observedRepoRoot $canonicalDevelopmentPath) { 'CLONE' } else { 'CLONE_NONCANONICAL' }
}
elseif ($observedPath) {
    'NON_REPOSITORY_PATH'
}
else {
    'UNKNOWN'
}

$payload = [ordered]@{
    schema = 'studysyndicate.path-input-receipt.v1'
    repository = $expectedRepository
    platform = $(if ($IsWindows) { 'windows' } elseif ($IsLinux) { 'linux' } elseif ($IsMacOS) { 'macos' } else { 'unknown' })
    profileKey = [string]$profile.key
    desktopKnownFolder = $desktopKnownFolder
    oneDriveState = $oneDriveState
    canonicalDevelopmentPath = $canonicalDevelopmentPath
    canonicalUsePath = $canonicalUsePath
    canonicalWorktreeRoot = $canonicalWorktreeRoot
    pathRelation = [string]$profile.use.relation
    entrypoint = @($profile.use.entrypoint)
    productionDeployment = [string]$profile.use.productionDeployment
    observedPath = $observedPath
    observedRepoRoot = $observedRepoRoot
    observedClassification = $observedClassification
    status = $status
    branch = $(if ($branch) { $branch } else { $null })
    head = $head
    origin = $origin
    evidenceSources = $evidenceSources
    safeNextAction = $safeNextAction
}

if ($Json) {
    $payload | ConvertTo-Json -Depth 8
}
else {
    Write-Host "STATUS=$status"
    Write-Host "PROFILE=$($payload.profileKey)"
    Write-Host "DEV=$canonicalDevelopmentPath"
    Write-Host "USE=$canonicalUsePath"
    Write-Host "WORKTREES=$canonicalWorktreeRoot"
    Write-Host "ENTRYPOINT=$(@($payload.entrypoint) -join ' ')"
    Write-Host "OBSERVED=$observedPath"
    Write-Host "OBSERVED_REPO=$observedRepoRoot"
    Write-Host "ONEDRIVE_STATE=$oneDriveState"
    Write-Host "NEXT=$safeNextAction"
}

if ($status -ne 'CANONICAL + PROVED') {
    Write-Error "StudySyndicate path resolution failed closed: $status. Canonical='$canonicalDevelopmentPath'; observed='$observedRepoRoot'. $safeNextAction"
    exit 2
}

if ($RunHarness) {
    & python (Join-Path $canonicalRepoRoot 'scripts/harness.py') validate --level quick
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
