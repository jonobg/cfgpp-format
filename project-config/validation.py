#!/usr/bin/env python3
"""
Validation utilities for CFGPP-Format project
Validates integration with meta workspace
"""

from meta_bridge import run_meta_tool, load_meta_paths
from pathlib import Path

def validate_meta_integration():
    """
    Validate that meta workspace integration is working
    """
    paths = load_meta_paths()
    meta_root = Path(paths['meta_root'])
    
    if not meta_root.exists():
        return False, f"Meta workspace not found at {meta_root}"
    
    # Test messaging system
    result = run_meta_tool('messaging', ['--help'])
    if not result['success']:
        return False, "Messaging system not accessible"
    
    return True, "Meta workspace integration validated"
