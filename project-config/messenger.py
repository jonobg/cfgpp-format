#!/usr/bin/env python3
"""
CFGPP-Format Messaging Interface
Bridge to meta workspace messaging system
"""

import sys
import os

# Add meta path for bridge access
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from meta_bridge import run_meta_tool
except ImportError:
    print("Error: Meta bridge not available")
    print("Please ensure meta workspace is properly configured")
    sys.exit(1)

def main():
    """
    Main messaging interface
    Forwards all arguments to meta messaging system
    """
    try:
        # Forward all arguments to meta messaging system
        result = run_meta_tool('messaging', sys.argv[1:])
        
        if result['success']:
            if result['output']:
                print(result['output'], end='')
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Messaging system error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
