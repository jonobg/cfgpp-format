#!/usr/bin/env python3
"""
Code formatter for cfgpp-format configuration files.

This module provides comprehensive formatting capabilities for cfgpp files,
including style customization, consistent indentation, and intelligent layout.

# REASONING: Code formatting enables consistent code style and developer productivity for formatting workflows.
# Formatting workflows require code formatting for consistent code style and developer productivity in formatting workflows.
# Code formatting supports consistent code style, developer productivity, and formatting coordination while enabling
# comprehensive formatting strategies and systematic code style workflows.
"""

from typing import Dict, List, Any, Optional, Union, TextIO
import re
from dataclasses import dataclass
from enum import Enum as PyEnum
from io import StringIO

from .parser import loads, ConfigParseError
from .schema_parser import loads_schema, SchemaDocument, SchemaParseError


class BraceStyle(PyEnum):
    """Brace placement styles."""

    SAME_LINE = "same_line"  # { on same line
    NEW_LINE = "new_line"  # { on new line
    NEW_LINE_INDENT = "new_line_indent"  # { on new line, indented


class ArrayStyle(PyEnum):
    """Array formatting styles."""

    COMPACT = "compact"  # [1, 2, 3]
    ONE_PER_LINE = "one_per_line"  # [\n  1,\n  2,\n  3\n]
    AUTO = "auto"  # Compact if short, multi-line if long


class CommentStyle(PyEnum):
    """Comment formatting styles."""

    PRESERVE = "preserve"  # Keep original spacing
    ALIGN = "align"  # Align comments to column
    NORMALIZE = "normalize"  # Standard spacing


@dataclass
class FormatterConfig:
    """Configuration for the cfgpp formatter."""

    # Indentation
    indent_size: int = 4
    use_tabs: bool = False

    # Spacing
    space_before_colon: bool = False
    space_after_colon: bool = True
    space_before_equals: bool = True
    space_after_equals: bool = True
    space_before_semicolon: bool = False
    space_after_semicolon: bool = True
    space_before_comma: bool = False
    space_after_comma: bool = True

    # Layout
    brace_style: BraceStyle = BraceStyle.SAME_LINE
    array_style: ArrayStyle = ArrayStyle.AUTO
    max_line_length: int = 100
    blank_lines_before_object: int = 1
    blank_lines_after_object: int = 1

    # Comments
    comment_style: CommentStyle = CommentStyle.NORMALIZE
    comment_column: int = 40

    # Arrays and objects
    array_wrap_threshold: int = 80  # Line length to trigger array wrapping
    array_element_threshold: int = 5  # Number of elements to trigger wrapping

    # Sort options
    sort_object_keys: bool = False
    sort_enum_values: bool = False

    # Schema integration
    schema_aware_formatting: bool = True

    @classmethod
    def compact(cls) -> "FormatterConfig":
        """Create a compact formatting configuration."""
        return cls(
            indent_size=2,
            brace_style=BraceStyle.SAME_LINE,
            array_style=ArrayStyle.COMPACT,
            max_line_length=120,
            blank_lines_before_object=0,
            blank_lines_after_object=0,
        )

    @classmethod
    def expanded(cls) -> "FormatterConfig":
        """Create an expanded formatting configuration."""
        return cls(
            indent_size=4,
            brace_style=BraceStyle.NEW_LINE,
            array_style=ArrayStyle.ONE_PER_LINE,
            max_line_length=80,
            blank_lines_before_object=2,
            blank_lines_after_object=2,
        )


class CfgppFormatter:
    """
    Formatter for cfgpp configuration files.

    # REASONING: Code formatting enables developer productivity and team consistency for professional workflows.
    # Professional workflows require code formatting for developer productivity and team consistency in professional workflows.
    # Code formatting supports developer productivity, team consistency, and professional coordination while enabling
    # comprehensive formatting strategies and systematic code style workflows.

    # REASONING: AST-based formatting ensures semantic accuracy and preserves program correctness for formatting workflows.
    # Formatting workflows require AST-based formatting for semantic accuracy and program correctness in formatting workflows.
    # AST-based formatting supports semantic accuracy, program correctness, and formatting coordination while enabling
    # comprehensive accuracy strategies and systematic semantic formatting workflows.
    """

    def __init__(
        self,
        config: Optional[FormatterConfig] = None,
        schema_doc: Optional[SchemaDocument] = None,
    ):
        """
        Initialize the formatter.

        Args:
            config: Formatting configuration
            schema_doc: Optional schema document for schema-aware formatting
        """
        self.config = config or FormatterConfig()
        self.schema_doc = schema_doc
        self.output = StringIO()
        self.current_indent = 0
        self.line_buffer: List[str] = []

    def format(self, config_text: str) -> str:
        """
        Format cfgpp configuration text.

        Args:
            config_text: The configuration text to format

        Returns:
            str: The formatted configuration text

        Raises:
            ConfigParseError: If the configuration cannot be parsed
        """
        # Handle empty configuration
        if not config_text.strip():
            return ""

        # Parse the configuration
        try:
            parsed_config = loads(config_text)
        except ConfigParseError as e:
            raise ConfigParseError(
                f"Cannot format invalid configuration: {e}", e.line, e.col
            )

        # Reset formatter state
        self.output = StringIO()
        self.current_indent = 0
        self.line_buffer = []

        # Format the parsed structure
        self._format_document(parsed_config)

        # Get the formatted text
        result = self.output.getvalue()

        # Clean up trailing whitespace and ensure final newline
        lines = result.split("\n")
        lines = [line.rstrip() for line in lines]

        # Remove excessive blank lines
        cleaned_lines = []
        prev_blank = False

        for line in lines:
            is_blank = not line.strip()

            if is_blank:
                if not prev_blank:
                    cleaned_lines.append("")
                prev_blank = True
            else:
                cleaned_lines.append(line)
                prev_blank = False

        # Ensure file ends with exactly one newline
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()

        return "\n".join(cleaned_lines) + "\n" if cleaned_lines else ""

    def format_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Format a cfgpp file.

        Args:
            input_path: Path to input file
            output_path: Optional output path (defaults to overwriting input)

        Returns:
            str: The formatted content
        """
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        formatted = self.format(content)

        output_file = output_path or input_path
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted)

        return formatted

    def _format_document(self, doc: Dict[str, Any]):
        """Format the entire document."""
        if "body" not in doc:
            return

        body = doc["body"]
        if not body:
            return

        # Sort keys if requested
        keys = sorted(body.keys()) if self.config.sort_object_keys else body.keys()

        first_item = True
        for key in keys:
            if not first_item and self.config.blank_lines_before_object > 0:
                for _ in range(self.config.blank_lines_before_object):
                    self._write_line("")

            self._format_top_level_object(key, body[key])
            first_item = False

        # Add trailing blank lines if configured
        if self.config.blank_lines_after_object > 0:
            for _ in range(self.config.blank_lines_after_object):
                self._write_line("")

    def _format_top_level_object(self, name: str, obj: Dict[str, Any]):
        """Format a top-level configuration object."""
        if obj.get("type") == "enum_definition":
            self._format_enum_definition(name, obj)
        else:
            self._format_object(name, obj)

    def _format_enum_definition(self, name: str, enum_def: Dict[str, Any]):
        """Format an enum definition."""
        # Write enum header
        enum_line = f"enum::{name}"

        if self.config.brace_style == BraceStyle.SAME_LINE:
            enum_line += " {"

        self._write_line(enum_line)

        if self.config.brace_style != BraceStyle.SAME_LINE:
            self._write_line("{")

        # Format enum body
        self._indent()

        # Values array
        if "values" in enum_def and enum_def["values"]:
            values = enum_def["values"]
            if self.config.sort_enum_values:
                # Extract string values for sorting
                string_values = []
                for val in values:
                    if isinstance(val, dict) and "value" in val:
                        string_values.append(val["value"])
                    else:
                        string_values.append(str(val))
                string_values.sort()
                values = [f'"{v}"' for v in string_values]

            values_line = "values = "
            values_line += self._format_array(values, inline_context=True)

            if "default" in enum_def and enum_def["default"] is not None:
                values_line += ","

            self._write_line(values_line)

        # Default value
        if "default" in enum_def and enum_def["default"] is not None:
            default_val = enum_def["default"]
            if isinstance(default_val, dict) and "value" in default_val:
                default_val = default_val["value"]

            default_line = f'default = "{default_val}"'
            self._write_line(default_line)

        self._dedent()
        self._write_line("}")

    def _format_object(self, name: str, obj: Dict[str, Any]):
        """Format a regular configuration object."""
        # Extract parameters if present
        params = []
        if "params" in obj:
            params = self._format_parameters(obj["params"])

        # Write object header
        obj_line = name
        if params:
            if len("".join(params)) + len(name) + 2 < self.config.max_line_length:
                # Short parameter list - keep on same line
                obj_line += f"({', '.join(params)})"
            else:
                # Long parameter list - multi-line
                obj_line += "("
                self._write_line(obj_line)
                self._indent()

                for i, param in enumerate(params):
                    param_line = param
                    if i < len(params) - 1:
                        param_line += ","
                    self._write_line(param_line)

                self._dedent()
                obj_line = ")"

        # Check if object is empty
        is_empty = "body" not in obj or not obj["body"]

        if is_empty:
            # Format empty object on single line
            obj_line += " {}"
            self._write_line(obj_line)
        else:
            # Add opening brace
            if self.config.brace_style == BraceStyle.SAME_LINE:
                obj_line += " {"

            self._write_line(obj_line)

            if self.config.brace_style != BraceStyle.SAME_LINE:
                if self.config.brace_style == BraceStyle.NEW_LINE_INDENT:
                    self._indent()
                self._write_line("{")
                if self.config.brace_style == BraceStyle.NEW_LINE_INDENT:
                    self._dedent()

            # Format object body
            self._indent()
            self._format_object_body(obj)
            self._dedent()

            self._write_line("}")

    def _format_parameters(self, params: Dict[str, Any]) -> List[str]:
        """Format parameter list."""
        formatted_params = []

        for param_name, param_info in params.items():
            param_str = ""

            # Add type
            if "type" in param_info:
                param_type = param_info["type"]
                if param_info.get("is_array", False):
                    param_type += "[]"
                param_str += param_type

                if self.config.space_before_colon:
                    param_str += " "
                if self.config.space_after_colon:
                    param_str += " "

            # Add parameter name
            param_str += param_name

            # Add parameter value if present
            if "value" in param_info:
                if self.config.space_before_equals:
                    param_str += " "
                param_str += "="
                if self.config.space_after_equals:
                    param_str += " "

                # Format the parameter value
                param_str += self._format_value(param_info["value"])

            formatted_params.append(param_str)

        return formatted_params

    def _get_indent(self) -> str:
        """Get current indentation string."""
        if self.config.use_tabs:
            return "\t" * self._indent_level
        else:
            return " " * (self.config.indent_size * self._indent_level)

    def _format_value(self, value: Dict[str, Any]) -> str:
        """Format a value based on its type."""
        if value["type"] == "string":
            return f'"{value["value"]}"'
        elif value["type"] == "number":
            return str(value["value"])
        elif value["type"] == "boolean":
            return str(value["value"]).lower()
        elif value["type"] == "array":
            return self._format_array_value(value["value"])
        elif value["type"] == "identifier":
            return value["value"]
        else:
            return str(value["value"])

    def _format_array_value(self, array_items: List[Dict[str, Any]]) -> str:
        """Format an array value."""
        if not array_items:
            return "[]"

        formatted_items = [self._format_value(item) for item in array_items]

        if self.config.array_style == ArrayStyle.COMPACT:
            return f"[{', '.join(formatted_items)}]"
        elif self.config.array_style == ArrayStyle.ONE_PER_LINE:
            items_str = ",\n".join(
                f"{self._get_indent()}{item}" for item in formatted_items
            )
            return f"[\n{items_str}\n{self._get_indent()[:-4]}]"
        else:  # AUTO
            total_length = (
                sum(len(item) for item in formatted_items) + len(formatted_items) * 2
            )
            if total_length < self.config.max_line_length // 2:
                return f"[{', '.join(formatted_items)}]"
            else:
                items_str = ",\n".join(
                    f"{self._get_indent()}{item}" for item in formatted_items
                )
                return f"[\n{items_str}\n{self._get_indent()[:-4]}]"

    def _format_object_body(self, obj: Dict[str, Any]):
        """Format the body of an object."""
        if "body" not in obj:
            return

        body = obj["body"]
        if not body:
            return

        # Sort keys if requested
        keys = sorted(body.keys()) if self.config.sort_object_keys else body.keys()

        for key in keys:
            item = body[key]

            if isinstance(item, dict) and "value" in item:
                # Check if this is actually a nested object with constructor call parameters
                value = item["value"]
                if isinstance(value, dict) and ("params" in value or "body" in value):
                    # This is a constructor call/nested object, not a simple property
                    self._format_nested_constructor_object(key, item)
                else:
                    # This is a property assignment
                    self._format_property(key, item)
            else:
                # This is a nested object
                self._format_nested_object(key, item)

    def _format_property(self, name: str, prop: Dict[str, Any]):
        """Format a property assignment."""
        prop_line = ""

        # Add type if present and not inferred
        if "type" in prop and prop["type"] and not self._is_type_inferred(prop):
            prop_type = prop["type"]
            if prop.get("is_array", False):
                prop_type += "[]"
            prop_line += prop_type

            if self.config.space_after_colon:
                prop_line += " "

        # Add property name
        prop_line += name

        # Add equals with spacing
        if self.config.space_before_equals:
            prop_line += " "
        prop_line += "="
        if self.config.space_after_equals:
            prop_line += " "

        # Add value
        value = prop["value"]
        prop_line += self._format_value(value)

        # Add semicolon if configured
        if self.config.space_before_semicolon:
            prop_line += " "
        prop_line += ";"

        self._write_line(prop_line)

    def _format_nested_constructor_object(self, name: str, prop: Dict[str, Any]):
        """Format a nested object that has constructor call parameters."""
        value = prop["value"]

        # Extract constructor parameters from the property's params if available
        params = []
        if "params" in prop:
            params = self._format_parameters(prop["params"])
        elif "params" in value:
            params = self._format_parameters(value["params"])

        # Write object header with parameters
        obj_line = name
        if params:
            if len("".join(params)) + len(name) + 2 < self.config.max_line_length:
                # Short parameter list - keep on same line
                obj_line += f"({', '.join(params)})"
            else:
                # Long parameter list - multi-line
                obj_line += "("
                self._write_line(obj_line)
                self._indent()

                for i, param in enumerate(params):
                    param_line = param
                    if i < len(params) - 1:
                        param_line += ","
                    self._write_line(param_line)

                self._dedent()
                obj_line = ")"

        # Check if object is empty
        is_empty = "body" not in value or not value["body"]

        if is_empty:
            # Format empty object on single line
            obj_line += " {}"
            self._write_line(obj_line)
        else:
            # Add opening brace
            if self.config.brace_style == BraceStyle.SAME_LINE:
                obj_line += " {"

            self._write_line(obj_line)

            if self.config.brace_style != BraceStyle.SAME_LINE:
                if self.config.brace_style == BraceStyle.NEW_LINE_INDENT:
                    self._indent()
                self._write_line("{")
                if self.config.brace_style == BraceStyle.NEW_LINE_INDENT:
                    self._dedent()

            # Format object body
            self._indent()
            self._format_object_body(value)
            self._dedent()

            self._write_line("}")

    def _format_nested_object(self, name: str, obj: Dict[str, Any]):
        """Format a nested object."""
        # Add namespace if present
        obj_line = name
        if "::" in name:
            # Already has namespace
            pass
        elif "name" in obj and obj["name"] != name:
            # Add namespace
            obj_line = f"{obj['name']}::{name}"

        # Format like a regular object but without parameters
        self._format_object_without_params(obj_line, obj)

    def _format_object_without_params(self, name: str, obj: Dict[str, Any]):
        """Format an object without parameter list."""
        obj_line = name

        if self.config.brace_style == BraceStyle.SAME_LINE:
            obj_line += " {"

        self._write_line(obj_line)

        if self.config.brace_style != BraceStyle.SAME_LINE:
            self._write_line("{")

        self._indent()
        self._format_object_body(obj)
        self._dedent()

        self._write_line("}")

    def _format_value(self, value: Any) -> str:
        """Format a value based on its type."""
        if isinstance(value, dict):
            if "type" in value and "value" in value:
                # Typed value
                inner_value = value["value"]
                if value["type"] == "string":
                    return f'"{inner_value}"'
                elif value["type"] in ["integer", "float"]:
                    return str(inner_value)
                elif value["type"] == "boolean":
                    return "true" if inner_value else "false"
                elif value["type"] == "null":
                    return "null"
                else:
                    return str(inner_value)
            else:
                # Object or complex value
                return self._format_complex_value(value)
        elif isinstance(value, list):
            return self._format_array(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "null"
        else:
            return str(value)

    def _format_array(self, arr: List[Any], inline_context: bool = False) -> str:
        """Format an array based on configuration."""
        if not arr:
            return "[]"

        formatted_items = [self._format_value(item) for item in arr]

        # Decide on formatting style
        should_wrap = False

        if self.config.array_style == ArrayStyle.ONE_PER_LINE:
            should_wrap = True
        elif self.config.array_style == ArrayStyle.COMPACT:
            should_wrap = False
        else:  # AUTO
            # Check length and complexity
            total_length = (
                sum(len(item) for item in formatted_items) + len(formatted_items) * 2
            )  # commas and spaces
            should_wrap = (
                total_length > self.config.array_wrap_threshold
                or len(formatted_items) > self.config.array_element_threshold
                or any("\n" in item for item in formatted_items)
            )

        if should_wrap and not inline_context:
            # Multi-line array
            result = "[\n"
            self._indent()

            for i, item in enumerate(formatted_items):
                item_line = self._get_indent() + item
                if i < len(formatted_items) - 1:
                    item_line += ","
                result += item_line + "\n"

            self._dedent()
            result += self._get_indent() + "]"
            return result
        else:
            # Single line array
            separator = ", " if self.config.space_after_comma else ","
            return f"[{separator.join(formatted_items)}]"

    def _format_complex_value(self, value: Dict[str, Any]) -> str:
        """Format complex values like objects."""
        # For inline object formatting, we need to handle this differently
        # Objects as property values should be formatted inline or expanded
        if "body" in value and value["body"]:
            # Check if this is a simple object that can be formatted inline
            body = value["body"]
            if len(body) <= 2:  # Small objects can be inline
                formatted_parts = []
                for key, item in body.items():
                    if isinstance(item, dict) and "value" in item:
                        # Simple property
                        formatted_parts.append(
                            f"{key} = {self._format_value(item['value'])}"
                        )
                    else:
                        # Nested object - use placeholder for deeply nested
                        formatted_parts.append(f"{key} = {{...}}")
                return "{ " + "; ".join(formatted_parts) + " }"
            else:
                return "{...}"  # Complex objects get placeholder
        else:
            return "{}"

    def _is_type_inferred(self, prop: Dict[str, Any]) -> bool:
        """Check if type can be inferred from value."""
        if "value" not in prop or "type" not in prop:
            return True

        value = prop["value"]
        prop_type = prop["type"]

        # Simple type inference
        if isinstance(value, dict) and "type" in value:
            return value["type"] == prop_type
        elif isinstance(value, str) and prop_type == "string":
            return True
        elif isinstance(value, (int, float)) and prop_type in [
            "int",
            "float",
            "number",
        ]:
            return True
        elif isinstance(value, bool) and prop_type == "bool":
            return True

        return False

    def _write_line(self, line: str):
        """Write a line with proper indentation."""
        if line.strip():  # Don't indent empty lines
            indented_line = self._get_indent() + line
        else:
            indented_line = line

        self.output.write(indented_line + "\n")

    def _get_indent(self) -> str:
        """Get current indentation string."""
        if self.config.use_tabs:
            return "\t" * self.current_indent
        else:
            return " " * (self.current_indent * self.config.indent_size)

    def _indent(self):
        """Increase indentation level."""
        self.current_indent += 1

    def _dedent(self):
        """Decrease indentation level."""
        self.current_indent = max(0, self.current_indent - 1)


def format_string(
    config_text: str,
    config: Optional[FormatterConfig] = None,
    schema_text: Optional[str] = None,
) -> str:
    """
    Format cfgpp configuration text.

    Args:
        config_text: The configuration text to format
        config: Optional formatting configuration
        schema_text: Optional schema text for schema-aware formatting

    Returns:
        str: The formatted configuration text
    """
    schema_doc = None
    if schema_text:
        try:
            schema_doc = loads_schema(schema_text)
        except SchemaParseError:
            # Ignore schema errors for formatting
            pass

    formatter = CfgppFormatter(config, schema_doc)
    return formatter.format(config_text)


def format_file(
    input_path: str,
    output_path: Optional[str] = None,
    config: Optional[FormatterConfig] = None,
    schema_path: Optional[str] = None,
) -> str:
    """
    Format a cfgpp file.

    Args:
        input_path: Path to input file
        output_path: Optional output path (defaults to overwriting input)
        config: Optional formatting configuration
        schema_path: Optional schema file path

    Returns:
        str: The formatted content
    """
    schema_doc = None
    if schema_path:
        try:
            from .schema_parser import load_schema

            schema_doc = load_schema(schema_path)
        except (SchemaParseError, FileNotFoundError):
            # Ignore schema errors for formatting
            pass

    formatter = CfgppFormatter(config, schema_doc)
    return formatter.format_file(input_path, output_path)
