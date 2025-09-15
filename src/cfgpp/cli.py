"""
Command-line interface for the cfgpp parser.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import re

from .parser import load, loads, ConfigParseError
from .lexer import LexerError
from .cli_schema import add_schema_commands


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
    elif format_type == "compact":
        return json.dumps(data, separators=(',', ':'))
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def validate_config(data: Dict[Any, Any]) -> Tuple[bool, List[str]]:
    """Validate configuration structure and return validation results."""
    errors = []
    warnings = []
    
    # Check basic structure
    if not isinstance(data, dict):
        errors.append("Configuration must be a dictionary")
        return False, errors
    
    if 'body' not in data:
        errors.append("Configuration missing required 'body' element")
        return False, errors
    
    # Check for common issues
    def check_nested_structure(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for empty objects
                if isinstance(value, dict) and not value:
                    warnings.append(f"Empty object at {current_path}")
                
                # Check for very deep nesting (potential issue)
                if path.count('.') > 10:
                    warnings.append(f"Very deep nesting at {current_path} (depth > 10)")
                
                # Recursively check nested structures
                check_nested_structure(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_nested_structure(item, f"{path}[{i}]")
    
    check_nested_structure(data['body'])
    
    # Print warnings
    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    
    return len(errors) == 0, errors


def format_cfgpp(data: Dict[Any, Any], indent: int = 2) -> str:
    """Format parsed configuration back to CFGPP syntax."""
    
    def format_value(value, current_indent=0):
        """Format a value according to its type."""
        if isinstance(value, dict):
            if 'type' in value and 'value' in value:
                # This is a typed value
                val = value['value']
                if value['type'] == 'string':
                    return f'"{val}"'
                elif value['type'] in ['integer', 'float']:
                    return str(val)
                elif value['type'] == 'boolean':
                    return 'true' if val else 'false'
                elif value['type'] == 'null':
                    return 'null'
                else:
                    return str(val)
            elif 'body' in value and 'name' in value:
                # This is an object
                return format_object(value, current_indent)
            else:
                # This is a plain dictionary
                return format_dict(value, current_indent)
        elif isinstance(value, list):
            return format_array(value, current_indent)
        else:
            return str(value)
    
    def format_array(arr, current_indent=0):
        """Format an array."""
        if not arr:
            return "[]"
        
        formatted_items = []
        for item in arr:
            formatted_items.append(format_value(item, current_indent))
        
        if len(formatted_items) <= 3 and all(len(item) < 20 for item in formatted_items):
            # Short array, format on one line
            return f"[{', '.join(formatted_items)}]"
        else:
            # Multi-line array
            indent_str = " " * (current_indent + indent)
            items_str = f",\n{indent_str}".join(formatted_items)
            return f"[\n{indent_str}{items_str}\n{' ' * current_indent}]"
    
    def format_dict(d, current_indent=0):
        """Format a plain dictionary."""
        if not d:
            return "{}"
        
        indent_str = " " * (current_indent + indent)
        items = []
        
        for key, value in d.items():
            formatted_value = format_value(value, current_indent + indent)
            items.append(f"{indent_str}{key} = {formatted_value}")
        
        return "{\n" + "\n".join(items) + f"\n{' ' * current_indent}}}"
    
    def format_object(obj, current_indent=0):
        """Format an object with name and body."""
        name = obj.get('name', 'UnknownObject')
        body = obj.get('body', {})
        
        if not body:
            return f"{name} {{}}"
        
        indent_str = " " * (current_indent + indent)
        items = []
        
        for key, prop in body.items():
            if isinstance(prop, dict) and 'value' in prop:
                formatted_value = format_value(prop['value'], current_indent + indent)
                type_prefix = ""
                if 'type' in prop and prop['type']:
                    type_prefix = f"{prop['type']} "
                items.append(f"{indent_str}{type_prefix}{key} = {formatted_value}")
        
        body_str = "\n".join(items)
        return f"{name} {{\n{body_str}\n{' ' * current_indent}}}"
    
    # Start formatting from the root
    if 'body' in data:
        items = []
        for obj_name, obj_data in data['body'].items():
            formatted_obj = format_object(obj_data, 0)
            items.append(formatted_obj)
        return "\n\n".join(items)
    else:
        return format_dict(data, 0)


def convert_to_json(data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Convert CFGPP parsed data to a simplified JSON structure."""
    
    def extract_value(obj):
        """Extract the actual value from CFGPP structure."""
        if isinstance(obj, dict):
            if 'type' in obj and 'value' in obj:
                # This is a typed value
                return obj['value']
            elif 'body' in obj:
                # This is an object, extract its properties
                result = {}
                for key, prop in obj['body'].items():
                    if isinstance(prop, dict) and 'value' in prop:
                        result[key] = extract_value(prop['value'])
                    else:
                        result[key] = extract_value(prop)
                return result
            elif 'value' in obj:
                # This has a value field
                return extract_value(obj['value'])
            else:
                # Plain dictionary
                return {k: extract_value(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [extract_value(item) for item in obj]
        else:
            return obj
    
    if 'body' in data:
        result = {}
        for obj_name, obj_data in data['body'].items():
            result[obj_name] = extract_value(obj_data)
        return result
    else:
        return extract_value(data)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Parse and process cfgpp configuration files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cfgpp config.cfgpp                    # Parse and output as JSON
  cfgpp config.cfgpp -f yaml            # Output as YAML
  cfgpp config.cfgpp --validate          # Validate configuration
  cfgpp config.cfgpp --format-cfgpp     # Format CFGPP syntax
  cfgpp config.cfgpp --convert-json     # Convert to simplified JSON
  cat config.cfgpp | cfgpp -            # Read from stdin
  
  # Schema commands:
  cfgpp validate config.cfgpp --schema schema.cfgpp-schema
  cfgpp schema-check schema.cfgpp-schema
  cfgpp schema-info schema.cfgpp-schema
        """
    )
    
    # Add schema subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    add_schema_commands(subparsers)
    
    # Input options
    parser.add_argument("file", nargs="?", help="Path to the cfgpp file to parse")
    parser.add_argument(
        "-", 
        dest="stdin", 
        action="store_true",
        help="Read from standard input"
    )
    
    # Output format options
    parser.add_argument(
        "-f", "--format", 
        choices=["json", "yaml", "compact"], 
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    
    # Operation modes
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration structure and report issues"
    )
    parser.add_argument(
        "--format-cfgpp",
        action="store_true",
        help="Format and pretty-print CFGPP syntax"
    )
    parser.add_argument(
        "--convert-json",
        action="store_true",
        help="Convert to simplified JSON structure (extract values only)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check syntax without producing output (exit code indicates success/failure)"
    )
    
    # Formatting options
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation spaces for formatted output (default: 2)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    # Verbose options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    args = parser.parse_args()

    # Handle schema subcommands
    if args.command:
        return args.func(args)

    try:
        # Read input
        if args.stdin:
            if args.verbose:
                print("Reading from standard input...", file=sys.stderr)
            config_text = sys.stdin.read()
            result = loads(config_text)
        elif args.file:
            if args.verbose:
                print(f"Reading from file: {args.file}", file=sys.stderr)
            result = load(args.file)
        else:
            parser.print_help()
            return 1

        # Validation mode
        if args.validate:
            if args.verbose:
                print("Validating configuration...", file=sys.stderr)
            is_valid, errors = validate_config(result)
            
            if is_valid:
                print("✓ Configuration is valid", file=sys.stderr if args.output else sys.stdout)
                return 0
            else:
                print("✗ Configuration validation failed:", file=sys.stderr)
                for error in errors:
                    print(f"  • {error}", file=sys.stderr)
                return 1

        # Check mode (syntax check only)
        if args.check:
            if args.verbose:
                print("✓ Syntax check passed", file=sys.stderr)
            return 0

        # Determine output content
        if args.format_cfgpp:
            if args.verbose:
                print("Formatting as CFGPP...", file=sys.stderr)
            output = format_cfgpp(result, args.indent)
        elif args.convert_json:
            if args.verbose:
                print("Converting to simplified JSON...", file=sys.stderr)
            simplified = convert_to_json(result)
            output = format_output(simplified, args.format)
        else:
            # Standard parsing output
            output = format_output(result, args.format)

        # Write output
        if args.output:
            if args.verbose:
                print(f"Writing to file: {args.output}", file=sys.stderr)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
                f.write('\n')  # Ensure file ends with newline
        else:
            print(output)

        return 0

    except (ConfigParseError, LexerError) as e:
        if hasattr(e, 'line') and hasattr(e, 'column'):
            print(f"Parse error at line {e.line}, column {e.column}: {e.message}", file=sys.stderr)
        else:
            print(f"Parse error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
