#!/usr/bin/env python3
"""
Schema parser for cfgpp-format schema files (.cfgpp-schema).

This module provides parsing capabilities for schema definitions that enable
validation, type checking, and enhanced developer experience for cfgpp configurations.

# REASONING: Schema parsing enables configuration validation and developer tooling for schema workflows.
# Schema workflows require schema parsing for configuration validation and developer tooling in schema workflows.
# Schema parsing supports configuration validation, developer tooling, and schema coordination while enabling
# comprehensive validation strategies and systematic schema-driven development workflows.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import re
from dataclasses import dataclass
from enum import Enum as PyEnum

from .lexer import lex
from .parser import ConfigParseError


class SchemaParseError(Exception):
    """Exception raised when schema parsing fails."""

    def __init__(self, message: str, line: int = 0, col: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col


class FieldRequirement(PyEnum):
    """Enumeration for field requirement levels."""

    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass
class SchemaField:
    """Represents a field definition in a schema."""

    name: str
    type_name: str
    requirement: FieldRequirement
    default_value: Optional[Any] = None
    is_array: bool = False
    line: int = 0
    col: int = 0


@dataclass
class ValidationRule:
    """Represents a validation rule in a schema."""

    expression: str
    line: int = 0
    col: int = 0


@dataclass
class EnumDefinition:
    """Represents an enum definition in a schema."""

    name: str
    values: List[str]
    default_value: Optional[str] = None
    line: int = 0
    col: int = 0


@dataclass
class SchemaDefinition:
    """Represents a complete schema definition."""

    name: str
    fields: Dict[str, SchemaField]
    validation_rules: List[ValidationRule]
    line: int = 0
    col: int = 0


@dataclass
class SchemaDocument:
    """Represents a complete schema document."""

    enums: Dict[str, EnumDefinition]
    schemas: Dict[str, SchemaDefinition]
    imports: List[str]


class SchemaParser:
    """
    Parser for cfgpp schema files (.cfgpp-schema).

    # REASONING: Schema parsing enables configuration validation and type checking for schema workflows.
    # Schema workflows require schema parsing for configuration validation and type checking in schema workflows.
    # Schema parsing supports configuration validation, type checking, and schema coordination while enabling
    # comprehensive parsing strategies and systematic schema validation workflows.
    """

    def __init__(self):
        """Initialize the schema parser."""
        self.tokens = []
        self.current_index = 0
        self.line = 1
        self.col = 1

    def parse(self, schema_text: str) -> SchemaDocument:
        """
        Parse a schema document from text.

        Args:
            schema_text: The schema file content to parse

        Returns:
            SchemaDocument: The parsed schema document

        Raises:
            SchemaParseError: If parsing fails
        """
        try:
            self.tokens = lex(schema_text)
            self.current_index = 0

            return self._parse_document()

        except Exception as e:
            if isinstance(e, SchemaParseError):
                raise
            raise SchemaParseError(
                f"Schema parsing failed: {str(e)}", self.line, self.col
            )

    def _current_token(self) -> Optional[Dict[str, Any]]:
        """Get the current token."""
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def _peek_token(self, offset: int = 1) -> Optional[Dict[str, Any]]:
        """Peek at a token ahead."""
        index = self.current_index + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def _consume(
        self, expected_type: Optional[str] = None, expected_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consume the current token and advance.

        Args:
            expected_type: Expected token type
            expected_value: Expected token value

        Returns:
            The consumed token

        Raises:
            SchemaParseError: If token doesn't match expectations
        """
        token = self._current_token()
        if not token:
            raise SchemaParseError("Unexpected end of input", self.line, self.col)

        if expected_type and token["type"] != expected_type:
            raise SchemaParseError(
                f"Expected {expected_type}, got {token['type']}",
                token.get("line", self.line),
                token.get("col", self.col),
            )

        if expected_value and token["value"] != expected_value:
            raise SchemaParseError(
                f"Expected '{expected_value}', got '{token['value']}'",
                token.get("line", self.line),
                token.get("col", self.col),
            )

        self.current_index += 1
        self.line = token.get("line", self.line)
        self.col = token.get("col", self.col)

        return token

    def _parse_document(self) -> SchemaDocument:
        """Parse the entire schema document."""
        document = SchemaDocument(enums={}, schemas={}, imports=[])

        while self._current_token():
            token = self._current_token()

            if token["type"] == "COMMENT":
                self._consume()
                continue

            if token["type"] == "IDENTIFIER":
                if token["value"] == "import":
                    import_path = self._parse_import()
                    document.imports.append(import_path)
                elif token["value"] == "schema":
                    schema_def = self._parse_schema_definition()
                    document.schemas[schema_def.name] = schema_def
                else:
                    raise SchemaParseError(
                        f"Unexpected identifier: {token['value']}",
                        token.get("line", self.line),
                        token.get("col", self.col),
                    )
            elif token["type"] == "ENUM":
                enum_def = self._parse_enum_definition()
                document.enums[enum_def.name] = enum_def
            else:
                raise SchemaParseError(
                    f"Unexpected token: {token['type']}",
                    token.get("line", self.line),
                    token.get("col", self.col),
                )

        return document

    def _parse_import(self) -> str:
        """Parse an import statement."""
        self._consume("IDENTIFIER", "import")
        path_token = self._consume("STRING")
        self._consume("PUNCTUATION", ";")
        return path_token["value"]

    def _parse_enum_definition(self) -> EnumDefinition:
        """Parse an enum definition."""
        line = self._current_token().get("line", self.line)
        col = self._current_token().get("col", self.col)

        self._consume("ENUM")
        name_token = self._consume("IDENTIFIER")
        enum_name = name_token["value"]

        self._consume("PUNCTUATION", "{")

        values = []
        default_value = None

        while self._current_token() and self._current_token()["value"] != "}":
            prop_token = self._consume("IDENTIFIER")
            prop_name = prop_token["value"]

            self._consume("PUNCTUATION", "=")

            if prop_name == "values":
                values = self._parse_string_array()
            elif prop_name == "default":
                default_token = self._consume("STRING")
                # Strip surrounding quotes from default value
                default_value = (
                    default_token["value"][1:-1]
                    if default_token["value"].startswith('"')
                    and default_token["value"].endswith('"')
                    else default_token["value"]
                )
            else:
                raise SchemaParseError(
                    f"Unknown enum property: {prop_name}",
                    prop_token.get("line", self.line),
                    prop_token.get("col", self.col),
                )

            # Optional comma
            if self._current_token() and self._current_token()["value"] == ",":
                self._consume("PUNCTUATION", ",")

        self._consume("PUNCTUATION", "}")

        return EnumDefinition(
            name=enum_name,
            values=values,
            default_value=default_value,
            line=line,
            col=col,
        )

    def _parse_string_array(self) -> List[str]:
        """Parse a string array."""
        self._consume("PUNCTUATION", "[")

        values = []
        while self._current_token() and self._current_token()["value"] != "]":
            string_token = self._consume("STRING")
            value = string_token["value"]
            # Strip surrounding quotes from string tokens
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            values.append(value)

            if self._current_token() and self._current_token()["value"] == ",":
                self._consume("PUNCTUATION", ",")

        self._consume("PUNCTUATION", "]")
        return values

    def _parse_schema_definition(self) -> SchemaDefinition:
        """Parse a schema definition."""
        line = self._current_token().get("line", self.line)
        col = self._current_token().get("col", self.col)

        self._consume("IDENTIFIER", "schema")
        name_token = self._consume("IDENTIFIER")
        schema_name = name_token["value"]

        self._consume("PUNCTUATION", "{")

        fields = {}
        validation_rules = []

        while self._current_token() and self._current_token()["value"] != "}":
            token = self._current_token()

            if token["value"] == "required" or token["value"] == "optional":
                field = self._parse_field_definition()
                fields[field.name] = field
            elif token["value"] == "validate":
                rules = self._parse_validation_block()
                validation_rules.extend(rules)
            else:
                raise SchemaParseError(
                    f"Unexpected token in schema: {token['value']}",
                    token.get("line", self.line),
                    token.get("col", self.col),
                )

        self._consume("PUNCTUATION", "}")

        return SchemaDefinition(
            name=schema_name,
            fields=fields,
            validation_rules=validation_rules,
            line=line,
            col=col,
        )

    def _parse_field_definition(self) -> SchemaField:
        """Parse a field definition."""
        line = self._current_token().get("line", self.line)
        col = self._current_token().get("col", self.col)

        # Parse requirement
        req_token = self._consume("IDENTIFIER")
        if req_token["value"] == "required":
            requirement = FieldRequirement.REQUIRED
        elif req_token["value"] == "optional":
            requirement = FieldRequirement.OPTIONAL
        else:
            raise SchemaParseError(
                f"Expected 'required' or 'optional', got '{req_token['value']}'",
                req_token.get("line", self.line),
                req_token.get("col", self.col),
            )

        # Parse type
        type_token = self._consume("IDENTIFIER")
        type_name = type_token["value"]
        is_array = False

        # Check for array notation
        if self._current_token() and self._current_token()["value"] == "[":
            self._consume("PUNCTUATION", "[")
            self._consume("PUNCTUATION", "]")
            is_array = True

        # Parse field name
        name_token = self._consume("IDENTIFIER")
        field_name = name_token["value"]

        # Parse optional default value
        default_value = None
        if self._current_token() and self._current_token()["value"] == "=":
            self._consume("PUNCTUATION", "=")
            default_value = self._parse_default_value()

        # Consume semicolon
        self._consume("PUNCTUATION", ";")

        return SchemaField(
            name=field_name,
            type_name=type_name,
            requirement=requirement,
            default_value=default_value,
            is_array=is_array,
            line=line,
            col=col,
        )

    def _parse_default_value(self) -> Any:
        """Parse a default value."""
        token = self._current_token()
        if not token:
            raise SchemaParseError("Expected default value", self.line, self.col)

        if token["type"] == "STRING":
            self._consume()
            value = token["value"]
            # Strip surrounding quotes from string tokens
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
        elif token["type"] == "NUMBER":
            self._consume()
            value = token["value"]
            return int(value) if "." not in str(value) else float(value)
        elif token["type"] == "BOOLEAN":
            self._consume()
            return token["value"] == "true"
        elif token["type"] == "IDENTIFIER":
            if token["value"] in ["true", "false"]:
                self._consume()
                return token["value"] == "true"
            else:
                # Enum value or identifier
                self._consume()
                return token["value"]
        elif token["type"] == "PUNCTUATION" and token["value"] == "[":
            # Array default value
            return self._parse_array_default()
        else:
            raise SchemaParseError(
                f"Invalid default value: {token['type']} '{token['value']}'",
                token.get("line", self.line),
                token.get("col", self.col),
            )

    def _parse_array_default(self) -> List[Any]:
        """Parse an array default value."""
        self._consume("PUNCTUATION", "[")

        values = []
        while self._current_token() and self._current_token()["value"] != "]":
            value = self._parse_default_value()
            values.append(value)

            if self._current_token() and self._current_token()["value"] == ",":
                self._consume("PUNCTUATION", ",")

        self._consume("PUNCTUATION", "]")
        return values

    def _parse_validation_block(self) -> List[ValidationRule]:
        """Parse a validation block."""
        self._consume("IDENTIFIER", "validate")
        self._consume("PUNCTUATION", "{")

        rules = []
        while self._current_token() and self._current_token()["value"] != "}":
            rule = self._parse_validation_rule()
            rules.append(rule)

        self._consume("PUNCTUATION", "}")
        return rules

    def _parse_validation_rule(self) -> ValidationRule:
        """Parse a single validation rule."""
        line = self._current_token().get("line", self.line)
        col = self._current_token().get("col", self.col)

        # For now, we'll parse validation rules as raw expressions
        # In a full implementation, we'd have a proper expression parser
        expression_parts = []
        brace_depth = 0

        while self._current_token():
            token = self._current_token()

            if token["value"] == "{":
                brace_depth += 1
            elif token["value"] == "}":
                if brace_depth == 0:
                    break
                brace_depth -= 1
            elif token["value"] == ";" and brace_depth == 0:
                self._consume()
                break

            expression_parts.append(token["value"])
            self._consume()

        # Join tokens with smart spacing - no spaces around dots
        expression = ""
        for i, part in enumerate(expression_parts):
            if i > 0:
                prev_part = expression_parts[i - 1]
                # No space before or after dots for property access
                if part == "." or prev_part == ".":
                    expression += part
                else:
                    expression += " " + part
            else:
                expression += part
        expression = expression.strip()

        return ValidationRule(expression=expression, line=line, col=col)


def loads_schema(schema_text: str) -> SchemaDocument:
    """
    Parse a schema document from text.

    Args:
        schema_text: The schema file content to parse

    Returns:
        SchemaDocument: The parsed schema document

    Raises:
        SchemaParseError: If parsing fails
    """
    parser = SchemaParser()
    return parser.parse(schema_text)


def load_schema(schema_file_path: str) -> SchemaDocument:
    """
    Load and parse a schema file.

    Args:
        schema_file_path: Path to the schema file

    Returns:
        SchemaDocument: The parsed schema document

    Raises:
        SchemaParseError: If parsing fails
        FileNotFoundError: If the file doesn't exist
    """
    with open(schema_file_path, "r", encoding="utf-8") as f:
        schema_text = f.read()

    return loads_schema(schema_text)
