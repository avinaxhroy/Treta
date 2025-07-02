# Treta Music Downloader - PowerShell Wrapper
# This script ensures proper Python environment activation

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists and activate it
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment (.venv)..." -ForegroundColor Blue
    & ".venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment (venv)..." -ForegroundColor Blue
    & "venv\Scripts\Activate.ps1"
}

# Check if Python is available
try {
    $null = & python --version 2>&1
} catch {
    Write-Host "Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run Treta with all passed arguments
& python "$ScriptDir\treta.py" @Arguments

# Preserve exit code
exit $LASTEXITCODE
