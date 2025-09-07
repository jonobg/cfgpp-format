"""
Command-line interface for the cfgpp parser.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .parser import load, loads


def format_output(data: dict, format_type: str = "json") -> str:
    """Format the output based on the specified format type."""
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "yaml":
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False)
        except ImportError:
            print("Warning: PyYAML not installed. Falling back to JSON format.", file=sys.stderr)
            return json.dumps(data, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Parse and process cfgpp configuration files.")
    parser.add_argument("file", nargs="?", help="Path to the cfgpp file to parse")
    parser.add_argument(
        "-", 
        dest="stdin", 
        action="store_true",
        help="Read from standard input"
    )
    parser.add_argument(
        "-f", "--format", 
        choices=["json", "yaml"], 
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    args = parser.parse_args()

    try:
        if args.stdin:
            # Read from stdin
            config_text = sys.stdin.read()
            result = loads(config_text)
        elif args.file:
            # Read from file
            result = load(args.file)
        else:
            parser.print_help()
            return 1

        # Format the output
        output = format_output(result, args.format)

        # Write to file or stdout
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
