#!/usr/bin/env python3
"""
Schema validation engine for cfgpp-format.

This module provides validation capabilities for cfgpp configurations against
schema definitions, enabling type checking, constraint validation, and enhanced
error reporting.

# REASONING: Schema validation enables configuration correctness and developer feedback for validation workflows.
# Validation workflows require schema validation for configuration correctness and developer feedback in validation workflows.
# Schema validation supports configuration correctness, developer feedback, and validation coordination while enabling
# comprehensive validation strategies and systematic schema-driven validation workflows.
"""

from typing import Dict, List, Any, Optional, Set, Union, Tuple
import re
from dataclasses import dataclass
from enum import Enum as PyEnum

from .schema_parser import (
    SchemaDocument,
    SchemaDefinition,
    SchemaField,
    EnumDefinition,
    ValidationRule,
    FieldRequirement,
    SchemaParseError,
)


class ValidationSeverity(PyEnum):
    """Severity levels for validation messages."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """Represents a validation message (error, warning, or info)."""

    severity: ValidationSeverity
    message: str
    path: str
    line: int = 0
    col: int = 0
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of schema validation."""

    is_valid: bool
    messages: List[ValidationMessage]

    def has_errors(self) -> bool:
        """Check if there are any error messages."""
        return any(msg.severity == ValidationSeverity.ERROR for msg in self.messages)

    def has_warnings(self) -> bool:
        """Check if there are any warning messages."""
        return any(msg.severity == ValidationSeverity.WARNING for msg in self.messages)

    def get_errors(self) -> List[ValidationMessage]:
        """Get only error messages."""
        return [
            msg for msg in self.messages if msg.severity == ValidationSeverity.ERROR
        ]

    def get_warnings(self) -> List[ValidationMessage]:
        """Get only warning messages."""
        return [
            msg for msg in self.messages if msg.severity == ValidationSeverity.WARNING
        ]


class SchemaValidator:
    """
    Validates cfgpp configuration against schema definitions.

    # REASONING: Schema validation enables configuration validation and type safety for validation workflows.
    # Validation workflows require schema validation for configuration validation and type safety in validation workflows.
    # Schema validation supports configuration validation, type safety, and validation coordination while enabling
    # comprehensive validation strategies and systematic schema-based validation workflows.
    """

    def __init__(self, schema_doc: SchemaDocument):
        """
        Initialize the validator with a schema document.

        Args:
            schema_doc: The parsed schema document to validate against
        """
        self.schema_doc = schema_doc
        self.messages: List[ValidationMessage] = []
        self.current_path: List[str] = []

    def validate(
        self, config_data: Dict[str, Any], schema_name: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate configuration data against the schema.

        Args:
            config_data: The parsed configuration data to validate
            schema_name: Optional specific schema name to validate against

        Returns:
            ValidationResult: The validation result with messages
        """
        self.messages = []
        self.current_path = []

        try:
            # If no specific schema name provided, try to infer from config structure
            if schema_name is None:
                schema_name = self._infer_schema_name(config_data)

            if schema_name not in self.schema_doc.schemas:
                self._add_error(
                    f"Schema '{schema_name}' not found in schema document", ""
                )
                return ValidationResult(is_valid=False, messages=self.messages)

            schema = self.schema_doc.schemas[schema_name]

            # Validate the configuration body
            if "body" in config_data:
                body = config_data["body"]
                # Find the schema object in the body
                if schema_name in body:
                    self._validate_object(body[schema_name], schema, schema_name)
                else:
                    # Try to find any object that matches the schema
                    matching_objects = [
                        obj_name for obj_name in body.keys() if obj_name == schema_name
                    ]
                    if matching_objects:
                        self._validate_object(
                            body[matching_objects[0]], schema, matching_objects[0]
                        )
                    else:
                        self._add_error(
                            f"Configuration object '{schema_name}' not found in body",
                            "",
                        )
            else:
                self._add_error("Configuration missing 'body' section", "")

            # Check if validation passed
            is_valid = not any(
                msg.severity == ValidationSeverity.ERROR for msg in self.messages
            )

            return ValidationResult(is_valid=is_valid, messages=self.messages)

        except Exception as e:
            self._add_error(f"Validation failed with exception: {str(e)}", "")
            return ValidationResult(is_valid=False, messages=self.messages)

    def _infer_schema_name(self, config_data: Dict[str, Any]) -> str:
        """
        Try to infer schema name from configuration structure.

        Args:
            config_data: The configuration data

        Returns:
            str: The inferred schema name
        """
        # Look for the main configuration object name
        if "body" in config_data:
            body = config_data["body"]
            if len(body) == 1:
                main_key = list(body.keys())[0]
                # Try to find matching schema
                potential_schema = main_key + "Schema"
                if potential_schema in self.schema_doc.schemas:
                    return potential_schema

        # Default to first schema if available
        if self.schema_doc.schemas:
            return list(self.schema_doc.schemas.keys())[0]

        raise ValueError("Cannot infer schema name and no schemas available")

    def _validate_object(
        self, obj_data: Dict[str, Any], schema: SchemaDefinition, path: str
    ):
        """
        Validate an object against a schema definition.

        Args:
            obj_data: The object data to validate
            schema: The schema definition
            path: Current validation path for error reporting
        """
        # Determine where to look for fields - constructor calls store them under 'params'
        fields_data = obj_data
        if "params" in obj_data and isinstance(obj_data["params"], dict):
            fields_data = obj_data["params"]

        # Check for required fields
        for field_name, field_def in schema.fields.items():
            field_path = f"{path}.{field_name}" if path else field_name

            if field_def.requirement == FieldRequirement.REQUIRED:
                if field_name not in fields_data:
                    self._add_error(
                        f"Required field '{field_name}' is missing",
                        field_path,
                        suggestion=f"Add '{field_name}' field with type '{field_def.type_name}'",
                    )
                    continue

            # Validate field if present
            if field_name in fields_data:
                self._validate_field(fields_data[field_name], field_def, field_path)
            elif (
                field_def.requirement == FieldRequirement.OPTIONAL
                and field_def.default_value is not None
            ):
                # Field is optional with default - that's fine
                pass

        # Check for unknown fields in the appropriate location
        for field_name in fields_data:
            if field_name not in schema.fields:
                field_path = f"{path}.{field_name}" if path else field_name
                self._add_warning(
                    f"Unknown field '{field_name}' not defined in schema",
                    field_path,
                    suggestion="Remove this field or add it to the schema definition",
                )

        # Validate schema rules (simplified - in full implementation would have expression evaluator)
        self._validate_schema_rules(obj_data, schema, path)

    def _validate_field(self, field_data: Any, field_def: SchemaField, path: str):
        """
        Validate a single field against its definition.

        Args:
            field_data: The field data to validate
            field_def: The field definition from schema
            path: Current validation path
        """
        # Handle cfgpp parser structure - field data might be wrapped
        actual_value = field_data
        if isinstance(field_data, dict) and "value" in field_data:
            actual_value = field_data["value"]
            if isinstance(actual_value, dict) and "value" in actual_value:
                actual_value = actual_value["value"]

        # Check array types
        if field_def.is_array:
            if not isinstance(actual_value, list):
                self._add_error(
                    f"Field '{field_def.name}' should be an array but got {type(actual_value).__name__}",
                    path,
                )
                return

            # Validate each array element
            for i, element in enumerate(actual_value):
                element_path = f"{path}[{i}]"
                self._validate_type(element, field_def.type_name, element_path)
        else:
            # Validate single value
            self._validate_type(actual_value, field_def.type_name, path)

    def _validate_type(self, value: Any, type_name: str, path: str):
        """
        Validate a value against a type name.

        Args:
            value: The value to validate
            type_name: The expected type name
            path: Current validation path
        """
        # Handle wrapped values from cfgpp parser
        if isinstance(value, dict) and "value" in value:
            actual_value = value["value"]
        else:
            actual_value = value

        # Built-in type validation
        if type_name == "string":
            if not isinstance(actual_value, str):
                self._add_error(
                    f"Expected string but got {type(actual_value).__name__}", path
                )
        elif type_name == "int":
            if not isinstance(actual_value, int):
                self._add_error(
                    f"Expected int but got {type(actual_value).__name__}", path
                )
        elif type_name == "float":
            if not isinstance(actual_value, (int, float)):
                self._add_error(
                    f"Expected float but got {type(actual_value).__name__}", path
                )
        elif type_name == "bool":
            if not isinstance(actual_value, bool):
                self._add_error(
                    f"Expected bool but got {type(actual_value).__name__}", path
                )
        elif type_name in self.schema_doc.enums:
            # Enum validation
            enum_def = self.schema_doc.enums[type_name]
            if actual_value not in enum_def.values:
                self._add_error(
                    f"Value '{actual_value}' is not valid for enum '{type_name}'",
                    path,
                    suggestion=f"Valid values are: {', '.join(enum_def.values)}",
                )
        elif type_name in self.schema_doc.schemas:
            # Nested object validation
            if isinstance(value, dict) and "body" in value:
                nested_schema = self.schema_doc.schemas[type_name]
                self._validate_object(value["body"], nested_schema, path)
            else:
                self._add_error(
                    f"Expected object of type '{type_name}' but got {type(actual_value).__name__}",
                    path,
                )
        else:
            # Unknown type - might be a custom type not yet defined
            self._add_warning(f"Unknown type '{type_name}' - cannot validate", path)

    def _validate_schema_rules(
        self, obj_data: Dict[str, Any], schema: SchemaDefinition, path: str
    ):
        """
        Validate custom schema rules (simplified implementation).

        Args:
            obj_data: The object data
            schema: The schema definition with rules
            path: Current validation path
        """
        # This is a simplified implementation - a full version would need
        # a proper expression parser and evaluator
        for rule in schema.validation_rules:
            try:
                # For now, just validate some common patterns
                if self._validate_simple_rule(rule.expression, obj_data, path):
                    continue
                else:
                    self._add_info(f"Validation rule check: {rule.expression}", path)
            except Exception as e:
                self._add_warning(
                    f"Could not evaluate validation rule: {rule.expression}", path
                )

    def _validate_simple_rule(
        self, expression: str, obj_data: Dict[str, Any], path: str
    ) -> bool:
        """
        Validate simple common validation patterns.

        Args:
            expression: The validation expression
            obj_data: The object data
            path: Current validation path

        Returns:
            bool: True if validation passed or couldn't be evaluated
        """
        # Determine where to look for fields - constructor calls store them under 'params'
        fields_data = obj_data
        if "params" in obj_data and isinstance(obj_data["params"], dict):
            fields_data = obj_data["params"]

        # Simple pattern matching for common validations

        # Pattern: fieldName.length > N
        length_match = re.match(r"(\w+)\.length\s*>\s*(\d+)", expression.strip())
        if length_match:
            field_name, min_length = length_match.groups()
            if field_name in fields_data:
                field_value = self._extract_value(fields_data[field_name])
                if isinstance(field_value, str) and len(field_value) <= int(min_length):
                    self._add_error(
                        f"Field '{field_name}' length ({len(field_value)}) must be greater than {min_length}",
                        f"{path}.{field_name}",
                    )
                    return False
            return True

        # Pattern: fieldName > N && fieldName <= M
        range_match = re.match(
            r"(\w+)\s*>\s*(\d+)\s*&&\s*\1\s*<=\s*(\d+)", expression.strip()
        )
        if range_match:
            field_name, min_val, max_val = range_match.groups()
            if field_name in fields_data:
                field_value = self._extract_value(fields_data[field_name])
                if isinstance(field_value, (int, float)):
                    if not (int(min_val) < field_value <= int(max_val)):
                        self._add_error(
                            f"Field '{field_name}' value ({field_value}) must be between {min_val} and {max_val}",
                            f"{path}.{field_name}",
                        )
                        return False
            return True

        return True  # Unknown pattern - skip validation

    def _extract_value(self, field_data: Any) -> Any:
        """Extract the actual value from cfgpp parser field structure."""
        if isinstance(field_data, dict):
            if "value" in field_data:
                value = field_data["value"]
                if isinstance(value, dict) and "value" in value:
                    return value["value"]
                return value
        return field_data

    def _add_error(self, message: str, path: str, suggestion: Optional[str] = None):
        """Add a validation error message."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.ERROR,
                message=message,
                path=path,
                suggestion=suggestion,
            )
        )

    def _add_warning(self, message: str, path: str, suggestion: Optional[str] = None):
        """Add a validation warning message."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.WARNING,
                message=message,
                path=path,
                suggestion=suggestion,
            )
        )

    def _add_info(self, message: str, path: str, suggestion: Optional[str] = None):
        """Add a validation info message."""
        self.messages.append(
            ValidationMessage(
                severity=ValidationSeverity.INFO,
                message=message,
                path=path,
                suggestion=suggestion,
            )
        )


def validate_config(
    config_data: Dict[str, Any],
    schema_doc: SchemaDocument,
    schema_name: Optional[str] = None,
) -> ValidationResult:
    """
    Validate configuration data against a schema document.

    Args:
        config_data: The parsed configuration data
        schema_doc: The schema document to validate against
        schema_name: Optional specific schema name

    Returns:
        ValidationResult: The validation result
    """
    validator = SchemaValidator(schema_doc)
    return validator.validate(config_data, schema_name)
