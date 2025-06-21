#!/usr/bin/env python3
"""Simple test script to verify the environment."""

print("Testing basic imports...")

try:
    import typer
    print("✅ Typer imported successfully")
except ImportError as e:
    print(f"❌ Typer import failed: {e}")

try:
    import rich
    print("✅ Rich imported successfully")
except ImportError as e:
    print(f"❌ Rich import failed: {e}")

try:
    from pathlib import Path
    print("✅ Pathlib imported successfully")
except ImportError as e:
    print(f"❌ Pathlib import failed: {e}")

print("Testing complete!")
