# Treta Music Downloader - Windows PowerShell Auto-Installer
# ===========================================================
#
# This script downloads and runs the Treta auto-installer.
# It handles everything automatically: Python, dependencies, FFmpeg, setup.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/Treta/main/install.ps1 | iex"
#   or
#   .\install.ps1
#

# Enable colors in PowerShell
$Host.UI.RawUI.ForegroundColor = "White"

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Header {
    param([string]$Title)
    
    Write-Host ""
    Write-ColoredOutput "==================================================================" "Cyan"
    Write-ColoredOutput "🎵 $Title" "Cyan"
    Write-ColoredOutput "==================================================================" "Cyan"
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-ColoredOutput "📋 $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "✅ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "❌ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "⚠️  $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColoredOutput "ℹ️  $Message" "Cyan"
}

function Test-PythonInstallation {
    $pythonCommands = @("python", "py", "python3")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -match "Python 3\.(\d+)\.") {
                $minorVersion = [int]$matches[1]
                if ($minorVersion -ge 8) {
                    return $cmd
                }
            }
        }
        catch {
            continue
        }
    }
    
    return $null
}

function Install-Python {
    Write-Step "Python 3.8+ not found. Attempting to install..."
    
    # Try winget first
    try {
        $wingetResult = winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python installed via winget"
            # Refresh PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            return Test-PythonInstallation
        }
    }
    catch {
        Write-Warning "winget installation failed, trying alternative method..."
    }
    
    # Fallback: Direct download
    Write-Info "Downloading Python installer..."
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $tempFile = [System.IO.Path]::GetTempFileName() + ".exe"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $tempFile -UseBasicParsing
        Write-Info "Installing Python (this may take a few minutes)..."
        Start-Process -FilePath $tempFile -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        Remove-Item $tempFile
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        return Test-PythonInstallation
    }
    catch {
        Write-Error "Failed to download or install Python: $($_.Exception.Message)"
        Write-Info "Please download and install Python manually from: https://python.org/downloads/"
        Write-Info "Make sure to check 'Add Python to PATH' during installation"
        return $null
    }
}

function Main {
    Write-Header "Treta Music Downloader - Auto-Installer"
    Write-Info "Setting up your music downloading environment..."
    Write-Host ""
    
    # Check if we're running from a cloned repository
    if ((Test-Path "install_auto.py") -and (Test-Path "treta.py")) {
        Write-Step "Running from local repository..."
        $pythonCmd = Test-PythonInstallation
        if (-not $pythonCmd) {
            $pythonCmd = Install-Python
        }
        
        if ($pythonCmd) {
            & $pythonCmd install_auto.py
            return $LASTEXITCODE
        } else {
            Write-Error "Python installation failed"
            return 1
        }
    }
    
    # We need to download the repository first
    Write-Step "Downloading Treta repository..."
    
    try {
        # Check if git is available
        $gitAvailable = $false
        try {
            git --version | Out-Null
            $gitAvailable = $true
        }
        catch {
            # Git not available
        }
        
        if ($gitAvailable) {
            Write-Info "Using git to clone repository..."
            git clone https://github.com/avinaxhroy/Treta.git
            Set-Location Treta
        } else {
            Write-Info "Downloading repository as archive..."
            $zipUrl = "https://github.com/avinaxhroy/Treta/archive/main.zip"
            $zipFile = "treta.zip"
            
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
            Expand-Archive -Path $zipFile -DestinationPath . -Force
            Remove-Item $zipFile
            Set-Location Treta-main
        }
        
        # Check Python installation
        Write-Step "Checking Python installation..."
        $pythonCmd = Test-PythonInstallation
        if (-not $pythonCmd) {
            $pythonCmd = Install-Python
        }
        
        if (-not $pythonCmd) {
            Write-Error "Python 3.8+ is required but not found"
            Write-Info "Please install Python from: https://python.org/downloads/"
            return 1
        }
        
        Write-Success "Found Python: $pythonCmd"
        
        # Run the auto-installer
        Write-Step "Running Treta auto-installer..."
        & $pythonCmd install_auto.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Treta installation completed successfully!"
            Write-Host ""
            Write-Info "You can now use Treta with: .\treta.bat"
            Write-Info "Or run 'treta.bat guide' for a complete walkthrough"
        } else {
            Write-Error "Installation failed. Please check the error messages above."
            return 1
        }
    }
    catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        return 1
    }
}

# Run main function
$exitCode = Main
exit $exitCode
