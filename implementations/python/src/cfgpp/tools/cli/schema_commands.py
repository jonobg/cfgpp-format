#!/usr/bin/env python3
"""
CLI commands for cfgpp-format schema operations.

This module extends the main CLI with schema-specific commands for validation,
checking, and schema management.

# REASONING: CLI schema support enables developer-friendly schema operations for CLI workflows.
# CLI workflows require CLI schema support for developer-friendly schema operations in CLI workflows.
# CLI schema support supports developer-friendly schema operations, command-line integration, and CLI coordination while enabling
# comprehensive CLI strategies and systematic schema command-line workflows.
"""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from ...schema.integration import (
    load_with_auto_schema,
    loads_with_schema,
    auto_discover_schema,
    format_validation_messages,
    SchemaRegistry,
    register_global_schema,
)
from ...schema.parser import load_schema, loads_schema, SchemaParseError
from ...core.parser import loads as config_loads, ConfigParseError


def add_schema_commands(subparsers):
    """
    Add schema-related commands to the main CLI parser.

    Args:
        subparsers: The argparse subparsers object
    """

    # Schema validation command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a configuration file against a schema",
        description="Validate cfgpp configuration files using schema definitions",
    )
    validate_parser.add_argument(
        "config_file", help="Path to the configuration file to validate"
    )
    validate_parser.add_argument(
        "--schema",
        "-s",
        help="Path to the schema file (auto-discovered if not provided)",
    )
    validate_parser.add_argument(
        "--schema-name", help="Specific schema name within the schema document"
    )
    validate_parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    validate_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output errors, suppress info and warnings",
    )
    validate_parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format for validation results",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # Schema check command (parse and check schema itself)
    check_parser = subparsers.add_parser(
        "schema-check",
        help="Check a schema file for syntax errors",
        description="Parse and validate schema file syntax",
    )
    check_parser.add_argument("schema_file", help="Path to the schema file to check")
    check_parser.add_argument(
        "--format", choices=["human", "json"], default="human", help="Output format"
    )
    check_parser.set_defaults(func=cmd_schema_check)

    # Schema info command
    info_parser = subparsers.add_parser(
        "schema-info",
        help="Display information about a schema file",
        description="Show detailed information about schema definitions",
    )
    info_parser.add_argument("schema_file", help="Path to the schema file")
    info_parser.add_argument("--schema-name", help="Show info for specific schema only")
    info_parser.add_argument(
        "--format", choices=["human", "json"], default="human", help="Output format"
    )
    info_parser.set_defaults(func=cmd_schema_info)

    # Schema discovery command
    discover_parser = subparsers.add_parser(
        "schema-discover",
        help="Discover schema files for a configuration",
        description="Find and suggest schema files for configuration files",
    )
    discover_parser.add_argument("config_file", help="Path to the configuration file")
    discover_parser.set_defaults(func=cmd_schema_discover)


def cmd_validate(args) -> int:
    """
    Validate a configuration file against a schema.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success, 1 for validation failure, 2 for error)
    """
    try:
        config_path = Path(args.config_file)
        if not config_path.exists():
            print(f"❌ Configuration file not found: {config_path}", file=sys.stderr)
            return 2

        # Determine schema path
        schema_path = None
        if args.schema:
            schema_path = Path(args.schema)
            if not schema_path.exists():
                print(f"❌ Schema file not found: {schema_path}", file=sys.stderr)
                return 2
        else:
            # Auto-discover schema
            discovered_schema = auto_discover_schema(str(config_path))
            if discovered_schema:
                schema_path = Path(discovered_schema)
                if not args.quiet:
                    print(f"📋 Using auto-discovered schema: {schema_path}")
            else:
                print(
                    "⚠️  No schema file discovered. Use --schema to specify one.",
                    file=sys.stderr,
                )
                return 2

        # Load and validate
        config_data, validation_result = load_with_auto_schema(
            str(config_path), schema_name=args.schema_name, validate=True
        )

        if validation_result is None:
            print("❌ No validation performed (no schema available)", file=sys.stderr)
            return 2

        # Format output
        if args.format == "json":
            output_json_validation(validation_result)
        else:
            output_human_validation(validation_result, args.quiet, args.strict)

        # Determine exit code
        if validation_result.has_errors():
            return 1
        elif args.strict and validation_result.has_warnings():
            return 1
        else:
            return 0

    except (ConfigParseError, SchemaParseError) as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 2


def cmd_schema_check(args) -> int:
    """
    Check a schema file for syntax errors.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success, 1 for errors)
    """
    try:
        schema_path = Path(args.schema_file)
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}", file=sys.stderr)
            return 1

        # Parse schema
        schema_doc = load_schema(str(schema_path))

        if args.format == "json":
            result = {
                "valid": True,
                "schemas": list(schema_doc.schemas.keys()),
                "enums": list(schema_doc.enums.keys()),
                "imports": schema_doc.imports,
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"✅ Schema file is valid: {schema_path}")
            print(
                f"📊 Found {len(schema_doc.schemas)} schema(s): {', '.join(schema_doc.schemas.keys())}"
            )
            print(
                f"🏷️  Found {len(schema_doc.enums)} enum(s): {', '.join(schema_doc.enums.keys())}"
            )
            if schema_doc.imports:
                print(f"📥 Imports: {', '.join(schema_doc.imports)}")

        return 0

    except SchemaParseError as e:
        if args.format == "json":
            result = {"valid": False, "error": str(e)}
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Schema syntax error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        if args.format == "json":
            result = {"valid": False, "error": f"Unexpected error: {e}"}
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


def cmd_schema_info(args) -> int:
    """
    Display information about a schema file.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success, 1 for errors)
    """
    try:
        schema_path = Path(args.schema_file)
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}", file=sys.stderr)
            return 1

        schema_doc = load_schema(str(schema_path))

        if args.format == "json":
            output_schema_info_json(schema_doc, args.schema_name)
        else:
            output_schema_info_human(schema_doc, args.schema_name)

        return 0

    except SchemaParseError as e:
        print(f"❌ Schema syntax error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


def cmd_schema_discover(args) -> int:
    """
    Discover schema files for a configuration.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success)
    """
    config_path = Path(args.config_file)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}", file=sys.stderr)
        return 1

    # Try auto-discovery
    discovered_schema = auto_discover_schema(str(config_path))

    if discovered_schema:
        print(f"✅ Found schema file: {discovered_schema}")

        # Try to load and show basic info
        try:
            schema_doc = load_schema(discovered_schema)
            print(f"📊 Schemas available: {', '.join(schema_doc.schemas.keys())}")
            print(f"🏷️  Enums available: {', '.join(schema_doc.enums.keys())}")
        except Exception as e:
            print(f"⚠️  Schema file found but has errors: {e}")
    else:
        print(f"❌ No schema file discovered for: {config_path}")
        print("💡 Suggestion: Create one of these files:")

        config_stem = config_path.stem
        config_dir = config_path.parent

        suggestions = [
            config_dir / f"{config_stem}.cfgpp-schema",
            config_dir / "schema" / f"{config_stem}.cfgpp-schema",
            config_dir / f"{config_stem}-schema.cfgpp-schema",
            config_dir / "schema.cfgpp-schema",
        ]

        for suggestion in suggestions:
            print(f"   • {suggestion}")

    return 0


def output_human_validation(
    validation_result, quiet: bool = False, strict: bool = False
):
    """Output validation results in human-readable format."""
    if validation_result.is_valid and not validation_result.messages:
        print("✅ Configuration is valid!")
        return

    # Filter messages based on quiet mode
    messages = validation_result.messages
    if quiet:
        messages = [msg for msg in messages if msg.severity.value == "error"]

    if messages:
        formatted = format_validation_messages(messages, show_suggestions=True)
        print(formatted)

    # Summary
    error_count = len(validation_result.get_errors())
    warning_count = len(validation_result.get_warnings())

    if error_count == 0 and warning_count == 0:
        print("\n✅ Configuration is valid!")
    elif error_count == 0:
        if strict:
            print(
                f"\n❌ Configuration failed strict validation ({warning_count} warnings treated as errors)"
            )
        else:
            print(
                f"\n⚠️  Configuration is valid with warnings ({warning_count} warnings)"
            )
    else:
        print(
            f"\n❌ Configuration is invalid ({error_count} errors, {warning_count} warnings)"
        )


def output_json_validation(validation_result):
    """Output validation results in JSON format."""
    result = {
        "valid": validation_result.is_valid,
        "has_errors": validation_result.has_errors(),
        "has_warnings": validation_result.has_warnings(),
        "messages": [
            {
                "severity": msg.severity.value,
                "message": msg.message,
                "path": msg.path,
                "line": msg.line,
                "col": msg.col,
                "suggestion": msg.suggestion,
            }
            for msg in validation_result.messages
        ],
    }
    print(json.dumps(result, indent=2))


def output_schema_info_human(schema_doc, specific_schema: Optional[str] = None):
    """Output schema information in human-readable format."""
    print(f"📋 Schema Document Information")
    print(f"═══════════════════════════════")

    # Enums
    if schema_doc.enums:
        print(f"\n🏷️  Enums ({len(schema_doc.enums)}):")
        for enum_name, enum_def in schema_doc.enums.items():
            print(f"   • {enum_name}: {', '.join(enum_def.values)}")
            if enum_def.default_value:
                print(f"     Default: {enum_def.default_value}")

    # Schemas
    if schema_doc.schemas:
        schemas_to_show = schema_doc.schemas
        if specific_schema:
            if specific_schema in schemas_to_show:
                schemas_to_show = {specific_schema: schemas_to_show[specific_schema]}
            else:
                print(f"❌ Schema '{specific_schema}' not found")
                return

        print(f"\n📊 Schemas ({len(schemas_to_show)}):")
        for schema_name, schema_def in schemas_to_show.items():
            print(f"\n   🔧 {schema_name}:")

            # Required fields
            required_fields = [
                f
                for f in schema_def.fields.values()
                if f.requirement.value == "required"
            ]
            if required_fields:
                print(f"      Required fields ({len(required_fields)}):")
                for field in required_fields:
                    array_suffix = "[]" if field.is_array else ""
                    print(f"        • {field.type_name}{array_suffix} {field.name}")

            # Optional fields
            optional_fields = [
                f
                for f in schema_def.fields.values()
                if f.requirement.value == "optional"
            ]
            if optional_fields:
                print(f"      Optional fields ({len(optional_fields)}):")
                for field in optional_fields:
                    array_suffix = "[]" if field.is_array else ""
                    default_info = (
                        f" = {field.default_value}"
                        if field.default_value is not None
                        else ""
                    )
                    print(
                        f"        • {field.type_name}{array_suffix} {field.name}{default_info}"
                    )

            # Validation rules
            if schema_def.validation_rules:
                print(f"      Validation rules ({len(schema_def.validation_rules)}):")
                for rule in schema_def.validation_rules:
                    print(f"        • {rule.expression}")

    # Imports
    if schema_doc.imports:
        print(f"\n📥 Imports ({len(schema_doc.imports)}):")
        for import_path in schema_doc.imports:
            print(f"   • {import_path}")


def output_schema_info_json(schema_doc, specific_schema: Optional[str] = None):
    """Output schema information in JSON format."""
    result = {
        "enums": {
            name: {"values": enum_def.values, "default": enum_def.default_value}
            for name, enum_def in schema_doc.enums.items()
        },
        "schemas": {},
        "imports": schema_doc.imports,
    }

    schemas_to_include = schema_doc.schemas
    if specific_schema and specific_schema in schemas_to_include:
        schemas_to_include = {specific_schema: schemas_to_include[specific_schema]}

    for schema_name, schema_def in schemas_to_include.items():
        result["schemas"][schema_name] = {
            "fields": {
                field.name: {
                    "type": field.type_name,
                    "requirement": field.requirement.value,
                    "is_array": field.is_array,
                    "default_value": field.default_value,
                }
                for field in schema_def.fields.values()
            },
            "validation_rules": [
                rule.expression for rule in schema_def.validation_rules
            ],
        }

    print(json.dumps(result, indent=2))
