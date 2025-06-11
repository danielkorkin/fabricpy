#!/usr/bin/env python3
"""
Documentation generation script for FabricPy.

This script automates the process of generating Sphinx documentation with
Google-style docstrings for the FabricPy library.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    """Main documentation generation process."""
    # Change to docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)

    print("FabricPy Documentation Generator")
    print("=" * 40)

    # Step 1: Clean previous builds
    if not run_command("make clean", "Cleaning previous documentation builds"):
        return False

    # Step 2: Regenerate API documentation (optional)
    regenerate_api = (
        input("Regenerate API documentation files? (y/N): ").lower().strip()
    )
    if regenerate_api == "y":
        if not run_command("make apidoc", "Regenerating API documentation"):
            print("Warning: API regeneration failed, continuing with existing files...")

    # Step 3: Build HTML documentation
    if not run_command("make html", "Building HTML documentation"):
        return False

    # Step 4: Open documentation (optional)
    open_docs = input("Open documentation in browser? (y/N): ").lower().strip()
    if open_docs == "y":
        build_dir = docs_dir / "_build" / "html" / "index.html"
        if build_dir.exists():
            if sys.platform == "darwin":  # macOS
                run_command(f"open {build_dir}", "Opening documentation in browser")
            elif sys.platform == "linux":
                run_command(f"xdg-open {build_dir}", "Opening documentation in browser")
            elif sys.platform == "win32":
                run_command(f"start {build_dir}", "Opening documentation in browser")
        else:
            print("Documentation build directory not found!")

    print("\n" + "=" * 40)
    print("Documentation generation complete!")
    print(f"Documentation available at: {docs_dir / '_build' / 'html' / 'index.html'}")


if __name__ == "__main__":
    main()
