# Treta Music Downloader - Windows PowerShell Auto-Installer (REDIRECTOR)
# ========================================================================
#
# This script redirects to the new enhanced remote installer.
# The new installer downloads and sets up everything automatically!
#
# Usage:
#   powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install.ps1 | iex"
#   or
#   .\install.ps1
#

Write-Host ""
Write-Host "🎵 Treta Auto-Installer - Redirecting to Enhanced Version..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Loading the new enhanced remote installer..." -ForegroundColor Yellow
Write-Host ""

# Download and run the new remote installer
try {
    $remoteInstallerUrl = "https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.ps1"
    Invoke-Expression (Invoke-RestMethod $remoteInstallerUrl)
} catch {
    Write-Host "❌ Failed to load remote installer: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Fallback - Running legacy installer..." -ForegroundColor Yellow
    Write-Host ""
    
    # Continue with the original installer code below as fallback
}

# Enable colors in PowerShell
$Host.UI.RawUI.ForegroundColor = "White"

# Set UTF-8 encoding for better Unicode support
try {
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $Env:PYTHONIOENCODING = "utf-8"
} catch {
    # Ignore encoding setup errors
}

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
                # Zotify requires Python 3.11 or greater
                if ($minorVersion -ge 11) {
                    return $cmd
                } elseif ($minorVersion -ge 8) {
                    Write-Warning "Found Python 3.$minorVersion, but zotify requires Python 3.11+"
                    Write-Info "Some features may not work correctly with older Python versions"
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
    Write-Step "Python 3.11+ not found. Installing Python 3.11 for optimal compatibility..."
    
    # Try winget first
    try {
        Write-Info "Attempting installation via winget..."
        $wingetResult = winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python 3.11 installed via winget"
            # Refresh PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            Start-Sleep -Seconds 2  # Wait for PATH to refresh
            return Test-PythonInstallation
        }
    }
    catch {
        Write-Warning "winget installation failed, trying direct download..."
    }
    
    # Fallback: Direct download of Python 3.11
    Write-Info "Downloading Python 3.11 installer..."
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $tempFile = [System.IO.Path]::GetTempFileName() + ".exe"
    
    try {
        Write-Info "Downloading installer (this may take a moment)..."
        Invoke-WebRequest -Uri $pythonUrl -OutFile $tempFile -UseBasicParsing
        Write-Info "Installing Python 3.11 (this may take a few minutes)..."
        Start-Process -FilePath $tempFile -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0" -Wait
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        Start-Sleep -Seconds 3  # Wait for installation to complete
        
        return Test-PythonInstallation
    }
    catch {
        Write-Error "Failed to download or install Python: $($_.Exception.Message)"
        Write-Info "Please manually install Python 3.11+ from: https://www.python.org/downloads/"
        Write-Info "Important: Make sure to check 'Add Python to PATH' during installation"
        Write-Info "Note: Zotify requires Python 3.11 or greater for full functionality"
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
            # Remove existing directory if it exists
            if (Test-Path "Treta") {
                Write-Warning "Removing existing Treta directory..."
                Remove-Item "Treta" -Recurse -Force -ErrorAction SilentlyContinue
            }
            git clone https://github.com/avinaxhroy/Treta.git
            Set-Location Treta
        } else {
            Write-Info "Downloading repository as archive..."
            $zipUrl = "https://github.com/avinaxhroy/Treta/archive/main.zip"
            $zipFile = "treta.zip"
            
            # Remove existing directory if it exists
            if (Test-Path "Treta-main") {
                Write-Warning "Removing existing Treta-main directory..."
                Remove-Item "Treta-main" -Recurse -Force -ErrorAction SilentlyContinue
            }
            
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
            Write-Info "Test your installation with: python test_installation.py"
        } else {
            Write-Error "Installation failed. Please check the error messages above."
            Write-Host ""
            Write-Info "If you got an 'imp' module error, try this fix:"
            Write-Info "1. cd Treta"  
            Write-Info "2. .\.venv\Scripts\activate"
            Write-Info "3. python fix_zotify.py"
            Write-Host ""
            Write-Info "For more help, see: TROUBLESHOOTING.md"
            Write-Info "Or run: python test_installation.py to diagnose issues"
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
