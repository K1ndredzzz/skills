[CmdletBinding()]
param(
    [string]$RepoPath = "E:\Code_new\bpc-fetch",
    [switch]$FixPipWarning,
    [switch]$SkipBrowserInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[bpc-fetch-news] $Message"
}

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath exited with code $LASTEXITCODE"
    }
}

function Remove-PipInvalidDistributionStubs {
    param([string]$PythonExe)

    $sitePaths = & $PythonExe -c "import site; [print(p) for p in site.getsitepackages()]"
    foreach ($sitePath in $sitePaths) {
        if ([string]::IsNullOrWhiteSpace($sitePath) -or -not (Test-Path -LiteralPath $sitePath)) {
            continue
        }

        $base = (Resolve-Path -LiteralPath $sitePath).Path
        $targets = Get-ChildItem -LiteralPath $base -Force | Where-Object { $_.Name -like "~ip*" }
        foreach ($target in $targets) {
            $full = $target.FullName
            if (-not $full.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Refusing to remove outside site-packages: $full"
            }
            Write-Step "Removing stale pip stub: $full"
            Remove-Item -LiteralPath $full -Recurse -Force
        }
    }
}

$pythonCommand = Get-Command python -ErrorAction Stop
$python = $pythonCommand.Source
$resolvedRepo = (Resolve-Path -LiteralPath $RepoPath).Path
$pyproject = Join-Path $resolvedRepo "pyproject.toml"

if (-not (Test-Path -LiteralPath $pyproject)) {
    throw "RepoPath does not contain pyproject.toml: $resolvedRepo"
}

if ($FixPipWarning) {
    Remove-PipInvalidDistributionStubs -PythonExe $python
}

Write-Step "Installing bpc-fetch from local source: $resolvedRepo"
Invoke-Checked -FilePath $python -Arguments @("-m", "pip", "install", "-e", $resolvedRepo)

if (-not $SkipBrowserInstall) {
    Write-Step "Ensuring Playwright Chromium is installed"
    Invoke-Checked -FilePath $python -Arguments @("-m", "playwright", "install", "chromium")
}

Write-Step "Running bpc-fetch doctor"
Invoke-Checked -FilePath $python -Arguments @("-m", "bpc_fetch", "doctor", "--compact")

$bpcFetch = Get-Command bpc-fetch -ErrorAction SilentlyContinue
if ($null -ne $bpcFetch) {
    Write-Step "Checking console script"
    & $bpcFetch.Source "sites" "--filter" "economist.com" "--limit" "1" "--compact"
    if ($LASTEXITCODE -ne 0) {
        throw "bpc-fetch console script exited with code $LASTEXITCODE"
    }
} else {
    Write-Warning "bpc-fetch console script is not on PATH; use: python -m bpc_fetch ..."
}
