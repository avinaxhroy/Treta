# Treta Music Downloader - Remote Auto-Installer
# ===============================================
#
# 🎵 True One-Click Installer - Downloads and installs everything automatically! 🎵
#
# This script:
# ✅ Downloads the latest Treta repository
# ✅ Runs the enhanced auto-installer
# ✅ Sets up everything for you automatically
# ✅ Works from anywhere - no need to download repository first!
#
# Usage (run this from anywhere):
#   powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.ps1 | iex"
#

# Set error handling
$ErrorActionPreference = "Stop"

# Enable colors and UTF-8 encoding
try {
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $Env:PYTHONIOENCODING = "utf-8"
} catch {
    # Ignore encoding setup errors
}

# Color functions
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $originalColor = $Host.UI.RawUI.ForegroundColor
    try {
        $Host.UI.RawUI.ForegroundColor = $Color
        Write-Host $Message
    } finally {
        $Host.UI.RawUI.ForegroundColor = $originalColor
    }
}

function Write-Header {
    param([string]$Title, [string]$Subtitle = "")
    
    Write-Host ""
    Write-ColoredOutput "==================================================================" "Cyan"
    Write-ColoredOutput "🎵 $Title" "Cyan"
    if ($Subtitle) {
        Write-ColoredOutput "   $Subtitle" "Cyan"
    }
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

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "⚠️ $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "❌ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColoredOutput "ℹ️ $Message" "Cyan"
}

# Main installation function
function Install-Treta {
    Write-Header "Treta Music Downloader - Remote Auto-Installer v2.0" "Downloads and installs everything automatically!"
    
    Write-Info "🚀 This installer will:"
    Write-Info "  • Download the latest Treta repository"
    Write-Info "  • Install Python (if needed)"
    Write-Info "  • Set up all music downloaders (Spotify, Apple Music, YouTube)"
    Write-Info "  • Configure FFmpeg for audio processing"
    Write-Info "  • Create global 'treta' command"
    Write-Info "  • Set up everything for immediate use"
    Write-Host ""
    
    # Ask for confirmation
    $response = Read-Host "Ready to begin automatic installation? (Y/n)"
    if ($response -match '^[Nn]') {
        Write-Info "Installation cancelled by user."
        return
    }
    
    try {
        # Step 1: Check prerequisites
        Write-Step "Checking system prerequisites..."
        
        # Check if we have PowerShell 5.1+ or PowerShell Core
        $psVersion = $PSVersionTable.PSVersion
        if ($psVersion.Major -lt 5) {
            Write-Error "PowerShell 5.1+ required. Current version: $psVersion"
            Write-Info "Please update PowerShell and try again."
            return $false
        }
        Write-Success "PowerShell version: $psVersion ✓"
        
        # Check internet connectivity
        try {
            $null = Invoke-WebRequest -Uri "https://github.com" -UseBasicParsing -TimeoutSec 10
            Write-Success "Internet connectivity ✓"
        } catch {
            Write-Error "No internet connection available"
            Write-Info "Internet connection is required to download Treta."
            return $false
        }
        
        # Step 2: Choose installation directory
        Write-Step "Choosing installation directory..."
        
        # Default to user's Documents folder for safety
        $defaultInstallDir = Join-Path $env:USERPROFILE "Documents\Treta"
        $installDir = $defaultInstallDir
        
        Write-Info "Installation directory: $installDir"
        
        # Create directory if it doesn't exist
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
            Write-Success "Created installation directory"
        } else {
            Write-Info "Installation directory already exists"
        }
        
        # Step 3: Download repository
        Write-Step "Downloading latest Treta repository..."
        
        $repoUrl = "https://github.com/avinaxhroy/treta/archive/refs/heads/main.zip"
        $zipPath = Join-Path $env:TEMP "treta-main.zip"
        $extractPath = Join-Path $env:TEMP "treta-extract"
        
        try {
            # Download the repository
            Write-Info "Downloading from: $repoUrl"
            Invoke-WebRequest -Uri $repoUrl -OutFile $zipPath -UseBasicParsing
            Write-Success "Repository downloaded"
            
            # Extract the archive
            Write-Info "Extracting repository..."
            if (Test-Path $extractPath) {
                Remove-Item $extractPath -Recurse -Force
            }
            Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
            
            # Move contents to installation directory
            $sourceDir = Join-Path $extractPath "treta-main"
            if (Test-Path $sourceDir) {
                # Copy all contents from source to install directory
                Get-ChildItem -Path $sourceDir -Recurse | ForEach-Object {
                    $relativePath = $_.FullName.Substring($sourceDir.Length + 1)
                    $destPath = Join-Path $installDir $relativePath
                    
                    if ($_.PSIsContainer) {
                        # Create directory
                        if (-not (Test-Path $destPath)) {
                            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
                        }
                    } else {
                        # Copy file
                        $destDir = Split-Path $destPath -Parent
                        if (-not (Test-Path $destDir)) {
                            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                        }
                        Copy-Item $_.FullName $destPath -Force
                    }
                }
                Write-Success "Repository extracted to: $installDir"
            } else {
                throw "Repository structure not as expected"
            }
            
            # Clean up temporary files
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
            Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
            
        } catch {
            Write-Error "Failed to download repository: $_"
            return $false
        }
        
        # Step 4: Run the auto-installer
        Write-Step "Running Treta auto-installer..."
        
        $installerPath = Join-Path $installDir "install_auto.py"
        if (-not (Test-Path $installerPath)) {
            Write-Error "install_auto.py not found in downloaded repository"
            return $false
        }
        
        # Change to installation directory
        Push-Location $installDir
        
        try {
            # Check if Python is available
            try {
                $pythonVersion = python --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Python found: $pythonVersion"
                    $pythonCmd = "python"
                } else {
                    throw "Python not found"
                }
            } catch {
                # Try python3
                try {
                    $pythonVersion = python3 --version 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Python found: $pythonVersion"
                        $pythonCmd = "python3"
                    } else {
                        throw "Python3 not found"
                    }
                } catch {
                    Write-Warning "Python not found - the installer will attempt to install it"
                    $pythonCmd = "python"  # The installer will handle Python installation
                }
            }
            
            # Run the enhanced auto-installer with global install
            Write-Info "Starting Treta auto-installer with global install option..."
            Write-Info "This may take a few minutes..."
            Write-Host ""
            
            $installerArgs = @("install_auto.py", "--global-install", "--verbose")
            $process = Start-Process -FilePath $pythonCmd -ArgumentList $installerArgs -Wait -PassThru -NoNewWindow
            
            if ($process.ExitCode -eq 0) {
                Write-Success "Treta installation completed successfully!"
            } else {
                Write-Warning "Installation completed with some issues (exit code: $($process.ExitCode))"
                Write-Info "Basic functionality should still work."
            }
            
        } catch {
            Write-Error "Failed to run installer: $_"
            return $false
        } finally {
            Pop-Location
        }
        
        # Step 5: Final setup and instructions
        Write-Header "🎉 Installation Complete!" "Treta is ready to use!"
        
        Write-ColoredOutput "🎯 Quick Start:" "Green"
        Write-Info "1. Test your installation:"
        Write-Info "   cd `"$installDir`""
        Write-Info "   python test_installation.py"
        Write-Host ""
        
        Write-Info "2. IMPORTANT: Restart your PowerShell/Command Prompt!"
        Write-Info "   (The global 'treta' command needs a fresh terminal session)"
        Write-Host ""
        
        Write-Info "3. Authenticate with your music services:"
        Write-Info "   treta auth add --service spotify"
        Write-Info "   treta auth add --service apple"
        Write-Host ""
        
        Write-Info "4. Download your first song:"
        Write-Info "   treta download url `"https://open.spotify.com/track/...`""
        Write-Host ""
        
        Write-Warning "If 'treta' command doesn't work after restart:"
        Write-Info "• Navigate to: $installDir"
        Write-Info "• Use: python treta.py [command] instead"
        Write-Info "• Or use: .\\treta.bat [command]"
        Write-Host ""
        
        Write-ColoredOutput "📖 Installation Directory:" "Cyan"
        Write-Info $installDir
        Write-Host ""
        
        Write-ColoredOutput "🆘 Need Help?" "Blue"
        Write-Info "• Documentation: https://github.com/avinaxhroy/treta/wiki"
        Write-Info "• Issues: https://github.com/avinaxhroy/treta/issues"
        Write-Info "• Run diagnostics: python test_installation.py"
        Write-Host ""
        
        Write-ColoredOutput "🎵 Happy music downloading! 🎵" "Green"
        
    } catch {
        Write-Error "Installation failed: $_"
        Write-Info "Please report this issue on GitHub with the error details."
        return $false
    }
}

# Run the installation
Install-Treta

# Keep window open
Write-Host ""
Write-Info "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
