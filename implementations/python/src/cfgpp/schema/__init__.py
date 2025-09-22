"""
CFGPP Schema System

Schema parsing, validation, and integration functionality.
"""

from .schema_parser import load_schema, loads_schema, SchemaParseError
from .schema_validator import validate_config, SchemaValidator, ValidationResult
from .integration import SchemaAwareParser, SchemaRegistry

__all__ = [
    # Schema Parser
    "load_schema",
    "loads_schema",
    "SchemaParseError",
    # Schema Validator
    "validate_config",
    "SchemaValidator",
    "ValidationResult",
    # Schema Integration
    "SchemaAwareParser",
    "SchemaRegistry",
]
