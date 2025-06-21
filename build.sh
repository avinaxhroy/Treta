#!/bin/bash
# Build script for Treta distribution

echo "🏗️  Building Treta distribution..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install build wheel

# Build the package
echo "🔨 Building package..."
python -m build

echo "✅ Build complete! Check the dist/ directory for distribution files."
echo ""
echo "📋 To install locally: pip install dist/treta-*.whl"
echo "📋 To upload to PyPI: twine upload dist/*"
