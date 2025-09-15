#!/usr/bin/env python3
"""
CLI commands for cfgpp-format formatting operations.

This module extends the main CLI with formatting commands for code formatting,
style checking, and format configuration.

# REASONING: CLI formatting support enables developer-friendly formatting operations for CLI workflows.
# CLI workflows require CLI formatting support for developer-friendly formatting operations in CLI workflows.
# CLI formatting support supports developer-friendly formatting operations, command-line integration, and CLI coordination while enabling
# comprehensive CLI strategies and systematic formatting command-line workflows.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from .formatter import (
    CfgppFormatter, FormatterConfig, BraceStyle, ArrayStyle, CommentStyle,
    format_string, format_file
)
from .parser import loads, ConfigParseError
from .schema_integration import auto_discover_schema


def add_formatter_commands(subparsers):
    """
    Add formatter-related commands to the main CLI parser.
    
    Args:
        subparsers: The argparse subparsers object
    """
    
    # Format command
    format_parser = subparsers.add_parser(
        'format',
        help='Format cfgpp configuration files',
        description='Format cfgpp files with consistent style and layout'
    )
    format_parser.add_argument(
        'files',
        nargs='+',
        help='Configuration files to format'
    )
    format_parser.add_argument(
        '--in-place', '-i',
        action='store_true',
        help='Format files in-place (overwrite original files)'
    )
    format_parser.add_argument(
        '--output', '-o',
        help='Output directory (when not using --in-place)'
    )
    format_parser.add_argument(
        '--config', '-c',
        help='Path to formatting configuration file (.cfgpp-format)'
    )
    format_parser.add_argument(
        '--style',
        choices=['default', 'compact', 'expanded'],
        default='default',
        help='Predefined formatting style'
    )
    format_parser.add_argument(
        '--check',
        action='store_true',
        help='Check if files are formatted (exit code 1 if not)'
    )
    format_parser.add_argument(
        '--diff',
        action='store_true',
        help='Show diff of changes (implies --check)'
    )
    format_parser.add_argument(
        '--indent',
        type=int,
        help='Override indentation size'
    )
    format_parser.add_argument(
        '--tabs',
        action='store_true',
        help='Use tabs instead of spaces'
    )
    format_parser.add_argument(
        '--max-line-length',
        type=int,
        help='Maximum line length'
    )
    format_parser.add_argument(
        '--brace-style',
        choices=['same_line', 'new_line', 'new_line_indent'],
        help='Brace placement style'
    )
    format_parser.add_argument(
        '--array-style',
        choices=['compact', 'one_per_line', 'auto'],
        help='Array formatting style'
    )
    format_parser.add_argument(
        '--sort-keys',
        action='store_true',
        help='Sort object keys alphabetically'
    )
    format_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    format_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed formatting information'
    )
    format_parser.set_defaults(func=cmd_format)
    
    # Format check command (alias for format --check)
    check_parser = subparsers.add_parser(
        'format-check',
        help='Check if files are properly formatted',
        description='Check formatting without modifying files'
    )
    check_parser.add_argument(
        'files',
        nargs='+',
        help='Configuration files to check'
    )
    check_parser.add_argument(
        '--config', '-c',
        help='Path to formatting configuration file'
    )
    check_parser.add_argument(
        '--style',
        choices=['default', 'compact', 'expanded'],
        default='default',
        help='Predefined formatting style'
    )
    check_parser.add_argument(
        '--diff',
        action='store_true',
        help='Show diff of changes'
    )
    check_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    check_parser.set_defaults(func=cmd_format_check)
    
    # Format init command (create .cfgpp-format config)
    init_parser = subparsers.add_parser(
        'format-init',
        help='Initialize formatting configuration',
        description='Create a .cfgpp-format configuration file'
    )
    init_parser.add_argument(
        '--style',
        choices=['default', 'compact', 'expanded'],
        default='default',
        help='Base formatting style'
    )
    init_parser.add_argument(
        '--output', '-o',
        default='.cfgpp-format',
        help='Output configuration file (default: .cfgpp-format)'
    )
    init_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing configuration file'
    )
    init_parser.set_defaults(func=cmd_format_init)


def cmd_format(args) -> int:
    """
    Format configuration files.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for formatting issues, 2 for errors)
    """
    try:
        # Load formatting configuration
        config = _load_formatter_config(args)
        
        # Process files
        files_processed = 0
        files_changed = 0
        files_with_errors = 0
        
        for file_path in args.files:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {path}", file=sys.stderr)
                files_with_errors += 1
                continue
            
            if not path.is_file():
                print(f"❌ Not a file: {path}", file=sys.stderr)
                files_with_errors += 1
                continue
            
            try:
                # Read original content
                original_content = path.read_text(encoding='utf-8')
                
                # Format content
                formatted_content = format_string(original_content, config)
                
                # Check if content changed
                content_changed = original_content != formatted_content
                
                if args.check or args.diff:
                    # Check mode - don't modify files
                    if content_changed:
                        files_changed += 1
                        if not args.quiet:
                            print(f"❌ {path}: not formatted")
                        
                        if args.diff:
                            _show_diff(original_content, formatted_content, str(path))
                    else:
                        if not args.quiet and args.verbose:
                            print(f"✅ {path}: already formatted")
                else:
                    # Format mode - modify files
                    if args.in_place:
                        if content_changed:
                            path.write_text(formatted_content, encoding='utf-8')
                            files_changed += 1
                            if not args.quiet:
                                print(f"✅ Formatted: {path}")
                        else:
                            if not args.quiet and args.verbose:
                                print(f"✅ {path}: no changes needed")
                    else:
                        # Output to specified location or stdout
                        if args.output:
                            output_dir = Path(args.output)
                            output_dir.mkdir(parents=True, exist_ok=True)
                            output_path = output_dir / path.name
                            output_path.write_text(formatted_content, encoding='utf-8')
                            if not args.quiet:
                                print(f"✅ Formatted: {path} -> {output_path}")
                        else:
                            print(formatted_content, end='')
                
                files_processed += 1
                
            except ConfigParseError as e:
                print(f"❌ Parse error in {path}: {e}", file=sys.stderr)
                files_with_errors += 1
            except Exception as e:
                print(f"❌ Error processing {path}: {e}", file=sys.stderr)
                files_with_errors += 1
        
        # Summary
        if not args.quiet and files_processed > 1:
            if args.check:
                if files_changed > 0:
                    print(f"\n❌ {files_changed} of {files_processed} files are not formatted")
                else:
                    print(f"\n✅ All {files_processed} files are properly formatted")
            else:
                print(f"\n✅ Processed {files_processed} files ({files_changed} changed)")
        
        # Return appropriate exit code
        if files_with_errors > 0:
            return 2  # Errors occurred
        elif (args.check or args.diff) and files_changed > 0:
            return 1  # Files not formatted
        else:
            return 0  # Success
            
    except Exception as e:
        print(f"❌ Formatting failed: {e}", file=sys.stderr)
        return 2


def cmd_format_check(args) -> int:
    """
    Check if files are properly formatted.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 if formatted, 1 if not formatted, 2 for errors)
    """
    # Convert to format command with check enabled
    args.check = True
    args.in_place = False
    return cmd_format(args)


def cmd_format_init(args) -> int:
    """
    Initialize formatting configuration file.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for errors)
    """
    try:
        output_path = Path(args.output)
        
        # Check if file exists
        if output_path.exists() and not args.force:
            print(f"❌ Configuration file already exists: {output_path}", file=sys.stderr)
            print("Use --force to overwrite", file=sys.stderr)
            return 1
        
        # Create configuration based on style
        if args.style == 'compact':
            config = FormatterConfig.compact()
        elif args.style == 'expanded':
            config = FormatterConfig.expanded()
        else:
            config = FormatterConfig()
        
        # Convert to JSON
        config_dict = {
            'indent_size': config.indent_size,
            'use_tabs': config.use_tabs,
            'space_before_equals': config.space_before_equals,
            'space_after_equals': config.space_after_equals,
            'space_after_comma': config.space_after_comma,
            'brace_style': config.brace_style.value,
            'array_style': config.array_style.value,
            'max_line_length': config.max_line_length,
            'blank_lines_before_object': config.blank_lines_before_object,
            'blank_lines_after_object': config.blank_lines_after_object,
            'sort_object_keys': config.sort_object_keys,
            'sort_enum_values': config.sort_enum_values,
            'schema_aware_formatting': config.schema_aware_formatting,
        }
        
        # Write configuration file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"✅ Created formatting configuration: {output_path}")
        print(f"   Style: {args.style}")
        print(f"   Edit this file to customize formatting options")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}", file=sys.stderr)
        return 1


def _load_formatter_config(args) -> FormatterConfig:
    """Load formatting configuration from various sources."""
    # Start with base style
    if hasattr(args, 'style'):
        if args.style == 'compact':
            config = FormatterConfig.compact()
        elif args.style == 'expanded':
            config = FormatterConfig.expanded()
        else:
            config = FormatterConfig()
    else:
        config = FormatterConfig()
    
    # Load from config file if specified
    config_file = None
    if hasattr(args, 'config') and args.config:
        config_file = Path(args.config)
    else:
        # Look for .cfgpp-format in current directory
        default_config = Path('.cfgpp-format')
        if default_config.exists():
            config_file = default_config
    
    if config_file and config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update config with file values
            for key, value in config_data.items():
                if hasattr(config, key):
                    if key in ['brace_style']:
                        setattr(config, key, BraceStyle(value))
                    elif key in ['array_style']:
                        setattr(config, key, ArrayStyle(value))
                    elif key in ['comment_style']:
                        setattr(config, key, CommentStyle(value))
                    else:
                        setattr(config, key, value)
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file {config_file}: {e}", file=sys.stderr)
    
    # Apply command-line overrides
    if hasattr(args, 'indent') and args.indent is not None:
        config.indent_size = args.indent
    
    if hasattr(args, 'tabs') and args.tabs:
        config.use_tabs = True
    
    if hasattr(args, 'max_line_length') and args.max_line_length is not None:
        config.max_line_length = args.max_line_length
    
    if hasattr(args, 'brace_style') and args.brace_style:
        config.brace_style = BraceStyle(args.brace_style)
    
    if hasattr(args, 'array_style') and args.array_style:
        config.array_style = ArrayStyle(args.array_style)
    
    if hasattr(args, 'sort_keys') and args.sort_keys:
        config.sort_object_keys = True
    
    return config


def _show_diff(original: str, formatted: str, filename: str):
    """Show diff between original and formatted content."""
    import difflib
    
    original_lines = original.splitlines(keepends=True)
    formatted_lines = formatted.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        formatted_lines,
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (formatted)",
        lineterm=''
    )
    
    for line in diff:
        if line.startswith('+++') or line.startswith('---'):
            print(f"\033[1m{line}\033[0m")  # Bold
        elif line.startswith('@@'):
            print(f"\033[36m{line}\033[0m")  # Cyan
        elif line.startswith('+'):
            print(f"\033[32m{line}\033[0m")  # Green
        elif line.startswith('-'):
            print(f"\033[31m{line}\033[0m")  # Red
        else:
            print(line, end='')
    print()  # Ensure final newline
