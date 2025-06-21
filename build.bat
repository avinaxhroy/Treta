@echo off
REM Build script for Treta distribution (Windows)

echo 🏗️  Building Treta distribution...

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Install build dependencies
echo 📦 Installing build dependencies...
pip install build wheel

REM Build the package
echo 🔨 Building package...
python -m build

echo ✅ Build complete! Check the dist/ directory for distribution files.
echo.
echo 📋 To install locally: pip install dist/treta-*.whl
echo 📋 To upload to PyPI: twine upload dist/*
pause
