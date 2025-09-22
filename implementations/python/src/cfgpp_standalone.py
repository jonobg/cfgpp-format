#!/usr/bin/env python3
"""
Standalone entry point for PyInstaller builds of CFGPP.
This avoids relative import issues when building with PyInstaller.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path so we can import cfgpp
src_dir = Path(__file__).parent / "cfgpp"
if src_dir.exists():
    sys.path.insert(0, str(src_dir.parent))

try:
    from cfgpp.tools.cli.cli import main
except ImportError:
    # Fallback for PyInstaller builds
    import cfgpp.cli

    main = cfgpp.cli.main

if __name__ == "__main__":
    sys.exit(main())
