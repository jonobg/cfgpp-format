#!/usr/bin/env python3
"""
Meta Workspace Bridge
Provides access to meta workspace tools from individual projects
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def load_meta_paths():
    """
    Load meta workspace paths from configuration
    """
    config_file = Path(__file__).parent / 'meta_paths.json'
    
    if not config_file.exists():
        return {
            'meta_root': 'd:/CascadeWorkspaces/meta',
            'tools_dir': 'd:/CascadeWorkspaces/meta/tools'
        }
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception:
        # Fallback to default paths
        return {
            'meta_root': 'd:/CascadeWorkspaces/meta', 
            'tools_dir': 'd:/CascadeWorkspaces/meta/tools'
        }

def run_meta_tool(tool_name, args=None):
    """
    Run a tool from the meta workspace
    
    Args:
        tool_name: Name of the tool to run
        args: Arguments to pass to the tool
        
    Returns:
        dict: Result with 'success', 'output', 'error' keys
    """
    if args is None:
        args = []
    
    paths = load_meta_paths()
    tool_path = Path(paths['tools_dir']) / f'{tool_name}.py'
    
    if not tool_path.exists():
        return {
            'success': False,
            'output': '',
            'error': f'Tool {tool_name} not found at {tool_path}'
        }
    
    try:
        result = subprocess.run(
            [sys.executable, str(tool_path)] + args,
            capture_output=True,
            text=True,
            cwd=paths['meta_root']
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else ''
        }
        
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e)
        }
